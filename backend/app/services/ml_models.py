"""
Lightweight ML Models Service

Provides simple train/predict/list functionality for a few model types.

Supported model types:
- random_forest (classification/regression)
- linear_regression (regression)
- kmeans (clustering)

This is intentionally minimal: models are persisted to disk using joblib and
loaded on demand. Designed to integrate with the existing FastAPI endpoints.
"""
from __future__ import annotations

import os
import uuid
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import dump, load

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
try:
    # statsmodels is present in requirements; import lazily
    from statsmodels.tsa.arima.model import ARIMA
except Exception:  # pragma: no cover - fallback if not installed
    ARIMA = None
try:
    # prophet may not be installed in all environments
    from prophet import Prophet
except Exception:  # pragma: no cover - fallback
    Prophet = None


class MLModelError(Exception):
    pass


class MLModelsService:
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = Path(model_dir or Path("models/ml"))
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # simple registry of supported types -> factory function
        self._factories = {
            "random_forest_classification": lambda params: RandomForestClassifier(**(params or {})),
            "random_forest_regression": lambda params: RandomForestRegressor(**(params or {})),
            "linear_regression": lambda params: LinearRegression(**(params or {})),
            "kmeans": lambda params: KMeans(**(params or {})),
            # time series forecasting (ARIMA) - trained with a univariate series y and optional exog
            "arima": lambda params: ("ARIMA", params or {}),
            "prophet": lambda params: ("PROPHET", params or {}),
            # item-based collaborative filtering: expects user-item matrix (users x items)
            "item_cf": lambda params: ("ITEM_CF", params or {}),
        }
        # simple in-memory job registry for background training
        # job_id -> {status: pending/running/done/failed, result: {...}, error: str}
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def _model_path(self, model_id: str) -> Path:
        return self.model_dir / f"{model_id}.joblib"

    def list_models(self, owner: Optional[str] = None) -> List[Dict[str, Any]]:
        """List models, optionally filtered by owner (email).

        Args:
            owner: optional email to filter models by owner
        """
        models = []
        for f in sorted(self.model_dir.glob("*.joblib")):
            try:
                meta_path = f.with_suffix('.joblib.meta')
                meta = {}
                if meta_path.exists():
                    with open(meta_path, 'r', encoding='utf-8') as fh:
                        meta = json.load(fh)

                if owner and meta.get('owner') != owner:
                    continue

                models.append({
                    "model_id": f.stem,
                    "path": str(f),
                    "meta": meta
                })
            except Exception:
                continue
        return models

    def train(self, model_type: str, X: Any, y: Optional[Any] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Train a model and persist it.

        Args:
            model_type: one of supported model keys
            X: 2D array-like or pandas DataFrame
            y: target array-like for supervised models
            params: model hyperparameters

        Returns:
            dict with model_id and metadata
        """
        if model_type not in self._factories:
            raise MLModelError(f"Unsupported model_type: {model_type}")

        # Convert X/y to numpy arrays if pandas provided
        if X is None:
            X_np = None
        elif isinstance(X, (pd.DataFrame, pd.Series)):
            X_np = X.values
        else:
            X_np = np.array(X)

        y_np = None
        if y is not None:
            if isinstance(y, (pd.Series, pd.DataFrame)):
                y_np = np.ravel(np.asarray(y.values))
            else:
                y_np = np.array(y)

        model = self._factories[model_type](params)

        # Fit model (supervised stores require y)
        # specialized handling for ARIMA/time-series
        if model_type == 'arima':
            if ARIMA is None:
                raise MLModelError("ARIMA/forecasting support is not available (statsmodels not installed)")
            # ARIMA expects a univariate series (y). If X provided it will be used as exog.
            if y_np is None:
                raise MLModelError("ARIMA training requires a univariate 'y' series")
            # params may include order (p,d,q) and seasonal_order etc.
            order = None
            seasonal_order = None
            exog = None
            if isinstance(model, tuple) and model[0] == 'ARIMA':
                # factory returned a marker tuple; extract params
                arima_params = model[1]
                order = arima_params.get('order')
                seasonal_order = arima_params.get('seasonal_order')
            if X is not None:
                # use X as exogenous variables if provided (must align with y length)
                exog = X_np
            # Build and fit ARIMA model
            # statsmodels ARIMA requires pandas Series for endog
            endog = pd.Series(y_np)
            # If order is None, use (1,0,0) as a simple default
            if order is None:
                order = (1, 0, 0)
            model_obj = ARIMA(endog, exog=exog, order=order)
            fitted = model_obj.fit()
            model_to_store = fitted
        elif model_type == 'prophet':
            if Prophet is None:
                raise MLModelError("Prophet support is not available (prophet package not installed)")
            # Prophet expects a dataframe with columns ['ds','y']
            if y_np is None:
                raise MLModelError("Prophet training requires a univariate 'y' series")
            # build dataframe for Prophet; allow params to include 'freq' and 'start'
            freq = (params or {}).get('freq', 'D')
            start = (params or {}).get('start')
            if start:
                ds = pd.to_datetime(start) + pd.to_timedelta(np.arange(len(y_np)), unit=freq)
            else:
                ds = pd.date_range(end=pd.Timestamp.now(), periods=len(y_np), freq=freq)
            df = pd.DataFrame({'ds': ds, 'y': y_np})
            model_obj = Prophet(**(params or {}))
            # if exogenous vars provided (X_np), add as regressors
            if X_np is not None:
                # ensure X_np is 2D and has same length
                if getattr(X_np, 'ndim', 1) != 2 or X_np.shape[0] != len(y_np):
                    raise MLModelError('Exogenous variables X must be 2D and align with length of y')
                for i in range(X_np.shape[1]):
                    col = f'reg_{i}'
                    df[col] = X_np[:, i]
                    model_obj.add_regressor(col)
            model_obj.fit(df)
            model_to_store = model_obj
        elif model_type.startswith('random_forest') or model_type == 'linear_regression':
            if y_np is None:
                raise MLModelError("Supervised model training requires 'y' target values")
            model.fit(X_np, y_np)
            model_to_store = model
        else:
            # unsupervised
            model.fit(X_np)
            model_to_store = model

        # item-based CF training: compute item-item cosine similarity
        if model_type == 'item_cf':
            # X_np expected to be a 2D user-item matrix (users x items)
            if X_np is None:
                raise MLModelError("item_cf training requires a user-item matrix as X")
            # Normalize and compute cosine similarity between item columns
            # small safety: convert to float
            mat = np.asarray(X_np, dtype=float)
            # item vectors are columns
            item_vectors = mat.T  # shape: items x users
            # compute norms
            norms = np.linalg.norm(item_vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            normalized = item_vectors / norms
            # cosine similarity matrix (items x items)
            sim = normalized @ normalized.T
            # store sim matrix and item means
            model_to_store = {"sim": sim, "item_means": np.nanmean(mat, axis=0).tolist()}

        model_id = str(uuid.uuid4())
        model_path = self._model_path(model_id)
        # persist the trained object (for ARIMA we store the fitted results)
        dump(model_to_store, model_path)

        # Save metadata
        meta = {
            "model_type": model_type,
            "params": params or {},
            "n_features": (X_np.shape[1] if (X_np is not None and getattr(X_np, 'ndim', 0) == 2) else None),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "owner": None,
            "visibility": "private",
            "tenant_id": None
        }
        meta_path = model_path.with_suffix('.joblib.meta')
        with open(meta_path, 'w', encoding='utf-8') as fh:
            json.dump(meta, fh)

        return {"model_id": model_id, "meta": meta}

    def predict(self, model_id: str, X: Any) -> Dict[str, Any]:
        model_path = self._model_path(model_id)
        if not model_path.exists():
            raise MLModelError(f"Model not found: {model_id}")

        model = load(model_path)

        # try to read metadata to decide prediction behavior
        try:
            meta = self.load_metadata(model_id)
        except MLModelError:
            meta = {}

        model_type = meta.get('model_type')

        # ARIMA forecasting: expect X to be a dict with {'horizon': int, 'exog': optional}
        if model_type == 'arima':
            # Accept either dict or simple horizon int
            if isinstance(X, dict):
                horizon = X.get('horizon')
                exog = X.get('exog')
                if horizon is None:
                    raise MLModelError("ARIMA predict requires 'horizon' in request payload")
                exog_np = None
                if exog is not None:
                    exog_np = np.array(exog)
                # statsmodels results have get_forecast
                if hasattr(model, 'get_forecast'):
                    forecast = model.get_forecast(steps=int(horizon), exog=exog_np)
                    preds = forecast.predicted_mean
                elif hasattr(model, 'forecast'):
                    preds = model.forecast(steps=int(horizon), exog=exog_np)
                else:
                    raise MLModelError("Loaded ARIMA model cannot produce forecasts")
                return {"predictions": pd.Series(preds).tolist()}
            else:
                # if caller passed a simple list/array, attempt in-sample prediction
                if isinstance(X, (pd.DataFrame, pd.Series)):
                    X_np = X.values
                else:
                    X_np = np.array(X)
                if hasattr(model, 'predict'):
                    preds = model.predict(X_np)
                    return {"predictions": np.array(preds).tolist()}
                raise MLModelError("ARIMA model expects a forecasting request (dict with 'horizon')")
        # Default behavior for scikit-learn models
        # item_cf prediction: expect a dict {"user_index": int, "top_k": int}
        if model_type == 'item_cf':
            if not isinstance(X, dict):
                raise MLModelError("item_cf predict requires payload {'user_index': int, 'top_k': int}")
            user_index = X.get('user_index')
            top_k = X.get('top_k', 10)
            if user_index is None:
                raise MLModelError("item_cf predict requires 'user_index' in payload")
            # model is a stored dict with 'sim' and 'item_means'
            if not isinstance(model, dict) or 'sim' not in model:
                raise MLModelError('Invalid item_cf model data')
            sim = model['sim']
            # Load user-item matrix - we didn't persist original matrix; require passing user vector in payload
            user_vector = X.get('user_vector')
            if user_vector is None:
                raise MLModelError('item_cf predict requires user_vector in payload (user interactions)')
            user_vec = np.asarray(user_vector, dtype=float)
            # score items by sim @ user interactions
            scores = np.asarray(sim @ user_vec)
            # mask already interacted items (optional): user_vec > 0 treated as seen
            seen_mask = user_vec > 0
            scores[seen_mask] = -np.inf
            top_idx = np.argsort(-scores)[:int(top_k)]
            return {"recommendations": [{"item_index": int(i), "score": float(scores[i])} for i in top_idx]}

        if isinstance(X, (pd.DataFrame, pd.Series)):
            X_np = X.values
        else:
            X_np = np.array(X)

        preds = model.predict(X_np)

        # Convert numpy to python list for JSON serialization
        return {"predictions": preds.tolist()}

    def load_metadata(self, model_id: str) -> Dict[str, Any]:
        meta_path = self._model_path(model_id).with_suffix('.joblib.meta')
        if not meta_path.exists():
            raise MLModelError(f"Metadata not found for model: {model_id}")
        with open(meta_path, 'r', encoding='utf-8') as fh:
            return json.load(fh)

    def set_owner(self, model_id: str, owner: str) -> None:
        meta_path = self._model_path(model_id).with_suffix('.joblib.meta')
        if not meta_path.exists():
            raise MLModelError(f"Metadata not found for model: {model_id}")
        with open(meta_path, 'r', encoding='utf-8') as fh:
            meta = json.load(fh)
        meta['owner'] = owner
        # also assign tenant_id by default to owner email (can be changed later)
        if not meta.get('tenant_id'):
            meta['tenant_id'] = owner
        with open(meta_path, 'w', encoding='utf-8') as fh:
            json.dump(meta, fh)

    def delete_model(self, model_id: str) -> None:
        model_path = self._model_path(model_id)
        meta_path = model_path.with_suffix('.joblib.meta')
        if model_path.exists():
            try:
                model_path.unlink()
            except Exception as e:
                raise MLModelError(f"Failed to delete model file: {e}")
        if meta_path.exists():
            try:
                meta_path.unlink()
            except Exception as e:
                raise MLModelError(f"Failed to delete metadata file: {e}")

    # Background job helpers
    def create_job(self, job_id: str, payload: Dict[str, Any]) -> None:
        self._jobs[job_id] = {"status": "pending", "result": None, "error": None, "payload": payload}

    def update_job(self, job_id: str, status: str, result: Optional[Any] = None, error: Optional[str] = None) -> None:
        if job_id not in self._jobs:
            raise MLModelError(f"Job not found: {job_id}")
        self._jobs[job_id]["status"] = status
        self._jobs[job_id]["result"] = result
        self._jobs[job_id]["error"] = error

    def get_job(self, job_id: str) -> Dict[str, Any]:
        job = self._jobs.get(job_id)
        if not job:
            raise MLModelError(f"Job not found: {job_id}")
        return job

    def run_train_job(self, job_id: str, model_type: str, X: Any, y: Optional[Any], params: Optional[Dict[str, Any]], owner: Optional[str], visibility: str = "private", tenant_id: Optional[str] = None) -> None:
        try:
            self.update_job(job_id, "running")
            result = self.train(model_type, X, y, params)
            # set owner/visibility/tenant
            try:
                if owner:
                    self.set_owner(result['model_id'], owner)
                # update visibility & tenant in metadata
                meta = self.load_metadata(result['model_id'])
                meta['visibility'] = visibility
                if tenant_id:
                    meta['tenant_id'] = tenant_id
                # persist updated meta
                model_path = self._model_path(result['model_id'])
                meta_path = model_path.with_suffix('.joblib.meta')
                with open(meta_path, 'w', encoding='utf-8') as fh:
                    json.dump(meta, fh)
            except Exception:
                # best-effort
                pass

            self.update_job(job_id, "done", result=result)
        except Exception as e:
            self.update_job(job_id, "failed", error=str(e))


ml_service = MLModelsService()
