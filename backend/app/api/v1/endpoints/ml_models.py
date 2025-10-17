from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field, validator, root_validator
from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timezone
import json

from app.services.ml_models import ml_service, MLModelError
from app.db.models import User
from app.db.session import get_db
from app.core.security import get_current_user

router = APIRouter()


def _matrix_size_ok(matrix: Any, max_cells: int) -> bool:
    """Check if matrix size is within acceptable limits"""
    if not isinstance(matrix, list):
        return True
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 and isinstance(matrix[0], list) else 1
    return rows * cols <= max_cells


SUPPORTED_MODELS = {
    'random_forest_regression',
    'linear_regression',
    'kmeans',
    'arima',
    'prophet',
}


class TrainRequest(BaseModel):
    model_type: str = Field(..., description="Type of ML model to train")
    X: Optional[List[List[float]]] = Field(None, description="2D numeric matrix or exogenous variables for time series")
    y: Optional[List[float]] = Field(None, description="Target vector for supervised models or time series for forecasting")
    params: Optional[Dict[str, Any]] = None
    background: Optional[bool] = False
    visibility: Optional[str] = Field("private", description="Model visibility")
    tenant_id: Optional[str] = None

    @validator('model_type')
    def model_must_be_supported(cls, v):
        if v not in SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model_type '{v}'. Supported: {', '.join(sorted(SUPPORTED_MODELS))}")
        return v

    @validator('X')
    def check_X_size(cls, v):
        if v is not None and not _matrix_size_ok(v, max_cells=20000):
            raise ValueError("Input matrix too large: exceeds 20,000 cells")
        return v

    @validator('visibility')
    def check_visibility(cls, v):
        if v not in {'private', 'public'}:
            raise ValueError('visibility must be "private" or "public"')
        return v

    @root_validator(skip_on_failure=True)
    def check_shapes_for_model(cls, values):
        model_type = values.get('model_type')
        X = values.get('X')
        y = values.get('y')

        if model_type in {'random_forest_classification', 'random_forest_regression', 'linear_regression'}:
            if X is None or y is None:
                raise ValueError('Supervised models require both X (2D matrix) and y (target vector)')
            if len(X) != len(y):
                raise ValueError('Length of y must match number of rows in X')

        elif model_type == 'kmeans':
            if X is None:
                raise ValueError('Clustering models require X (2D matrix)')

        elif model_type in {'arima', 'prophet'}:
            if y is None:
                raise ValueError('Forecasting models require y (a univariate time series)')

        elif model_type == 'item_cf':
            if X is None:
                raise ValueError('Item-CF requires a user-item matrix X (users x items)')

        return values


class PredictRequest(BaseModel):
    model_id: str
    X: Any

    @validator('X')
    def check_X_size(cls, v):
        if isinstance(v, dict):
            horizon = v.get('horizon')
            if horizon is not None:
                if not isinstance(horizon, int) or horizon <= 0:
                    raise ValueError('Forecasting requests must include a positive integer "horizon"')
            exog = v.get('exog')
            if exog is not None and not _matrix_size_ok(exog, max_cells=5000):
                raise ValueError('Exogenous matrix too large: exceeds 5,000 cells')
            return v

        if not _matrix_size_ok(v, max_cells=5000):
            raise ValueError('Input matrix too large: exceeds 5,000 cells')
        return v


class VisibilityUpdateRequest(BaseModel):
    visibility: Optional[str] = None
    tenant_id: Optional[str] = None

    @validator('visibility')
    def check_visibility(cls, v):
        if v is not None and v not in {'private', 'public'}:
            raise ValueError('visibility must be "private" or "public"')
        return v


@router.get('/list')
def list_models(mine: bool = False, current_user: User = Depends(get_current_user)):
    """List available ML models"""
    try:
        owner = current_user.email if mine else None  # type: ignore[reportArgumentType]
        models = ml_service.list_models(owner=owner)  # type: ignore[reportArgumentType]
        return {"success": True, "models": models}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/train')
def train_model(req: TrainRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """Train a new ML model"""
    try:
        if req.background:
            job_id = str(uuid4())
            payload = {
                "model_type": req.model_type, 
                "params": req.params, 
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            ml_service.create_job(job_id, payload)
            
            background_tasks.add_task(
                ml_service.run_train_job,
                job_id,
                req.model_type,
                req.X,
                req.y,
                req.params,
                current_user.email,  # type: ignore[reportArgumentType]
                req.visibility or "private",
                req.tenant_id
            )
            return {"success": True, "job_id": job_id, "status": "pending"}

        # Synchronous training
        result = ml_service.train(req.model_type, req.X, req.y, req.params)
        
        # Set owner and visibility metadata
        try:
            ml_service.set_owner(result['model_id'], current_user.email)  # type: ignore[reportArgumentType]
            meta = ml_service.load_metadata(result['model_id'])
            meta['visibility'] = req.visibility or 'private'
            if req.tenant_id:
                meta['tenant_id'] = req.tenant_id
                
            model_path = ml_service._model_path(result['model_id'])
            meta_path = model_path.with_suffix('.joblib.meta')
            with open(meta_path, 'w', encoding='utf-8') as fh:
                json.dump(meta, fh)
        except Exception:
            # Best-effort metadata persistence; ignore failures
            pass

        return {"success": True, "model": result}
        
    except MLModelError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/predict')
def predict(req: PredictRequest, current_user: User = Depends(get_current_user)):
    """Make predictions using a trained model"""
    try:
        meta = ml_service.load_metadata(req.model_id)
        owner = meta.get('owner')
        visibility = meta.get('visibility', 'private')
        tenant_id = meta.get('tenant_id')

        # Check authorization
        if owner and owner != current_user.email:
            if visibility != 'public' and tenant_id != current_user.email:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail='Not authorized to use this model'
                )

        result = ml_service.predict(req.model_id, req.X)
        # ml_service.predict may return a dict with keys like 'predictions' or 'recommendations'
        if isinstance(result, dict):
            if 'predictions' in result:
                return {"success": True, "predictions": result['predictions']}
            if 'recommendations' in result:
                return {"success": True, "recommendations": result['recommendations']}
        # fallback: return result directly
        return {"success": True, **(result if isinstance(result, dict) else {'result': result})}
        
    except MLModelError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/info/{model_id}')
def model_info(model_id: str, current_user: User = Depends(get_current_user)):
    """Get information about a specific model"""
    try:
        meta = ml_service.load_metadata(model_id)
        owner = meta.get('owner')
        
        # Check authorization for private models
        if owner and owner != current_user.email and meta.get('visibility') != 'public':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail='Not authorized to view this model'
            )
            
        return {"success": True, "model_id": model_id, "meta": meta}
        
    except MLModelError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch('/{model_id}/visibility')
def update_visibility(model_id: str, payload: VisibilityUpdateRequest, current_user: User = Depends(get_current_user)):
    """Update visibility and/or tenant_id for a model. Owner-only action."""
    try:
        meta = ml_service.load_metadata(model_id)
        owner = meta.get('owner')
        
        # Only owner can modify visibility
        if owner and owner != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail='Not authorized to modify this model'
            )

        # Update metadata
        if payload.visibility is not None:
            meta['visibility'] = payload.visibility
        if payload.tenant_id is not None:
            meta['tenant_id'] = payload.tenant_id

        # Persist changes
        model_path = ml_service._model_path(model_id)
        meta_path = model_path.with_suffix('.joblib.meta')
        with open(meta_path, 'w', encoding='utf-8') as fh:
            json.dump(meta, fh)

        return {"success": True, "model_id": model_id, "meta": meta}
        
    except MLModelError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete('/{model_id}')
def delete_model(model_id: str, current_user: User = Depends(get_current_user)):
    """Delete a model. Owner-only action."""
    try:
        meta = ml_service.load_metadata(model_id)
        owner = meta.get('owner')
        
        # Only owner can delete
        if owner and owner != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail='Not authorized to delete this model'
            )
            
        ml_service.delete_model(model_id)
        return {"success": True, "deleted": model_id}
        
    except MLModelError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/jobs/{job_id}')
def job_status(job_id: str, current_user: User = Depends(get_current_user)):
    """Get status of a background training job"""
    try:
        job = ml_service.get_job(job_id)
        return {"success": True, "job": job}
        
    except MLModelError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
