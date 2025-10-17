from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

router = APIRouter()


class RowsPayload(BaseModel):
    rows: List[Dict[str, Any]] = Field(..., description="List of row dicts")


class SummaryRequest(RowsPayload):
    columns: Optional[List[str]] = None
    unique_limit: int = 20


class FilterSpec(BaseModel):
    op: str
    min: Optional[float] = None
    max: Optional[float] = None
    values: Optional[List[Any]] = None
    pattern: Optional[str] = None


class FilterRequest(RowsPayload):
    filters: Dict[str, FilterSpec]



class AggregateRequest(RowsPayload):
    group_by: List[str]
    aggs: Dict[str, List[str]] = Field(..., description="Aggregations per column, e.g. { 'sales': ['sum','mean'] }")


def _native(val: Any) -> Any:
    # Convert numpy scalar types to native Python
    if isinstance(val, np.generic):
        try:
            return val.item()
        except Exception:
            return str(val)
    return val


@router.post("/summary")
def summary(payload: SummaryRequest):
    try:
        df = pd.DataFrame(payload.rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid rows payload: {e}")

    cols = payload.columns or list(df.columns)
    result: Dict[str, Dict[str, Any]] = {}
    for c in cols:
        if c not in df.columns:
            result[c] = {"present": False}
            continue
        series = df[c]
        nonnull = series.dropna()
        dtype = str(series.dtype)
        meta: Dict[str, Any] = {"present": True, "dtype": dtype}
        if pd.api.types.is_numeric_dtype(series):
            if len(nonnull) > 0:
                meta.update({"min": _native(nonnull.min()), "max": _native(nonnull.max()), "mean": _native(nonnull.mean())})
            else:
                meta.update({"min": None, "max": None, "mean": None})
        # unique values (limited)
        uniques = list(pd.unique(nonnull))[: payload.unique_limit]
        meta["unique_sample"] = [_native(v) for v in uniques]
        result[c] = meta

    return {"columns": result}


@router.post("/filter")
def apply_filter(payload: FilterRequest):
    try:
        df = pd.DataFrame(payload.rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid rows payload: {e}")

    filtered = df
    for col, spec in payload.filters.items():
        if col not in filtered.columns:
            # missing column => no rows pass
            filtered = filtered.iloc[0:0]
            break
        if spec.op == "range":
            lo = spec.min
            hi = spec.max
            if lo is None and hi is None:
                continue
            if lo is None:
                filtered = filtered[filtered[col] <= hi]
            elif hi is None:
                filtered = filtered[filtered[col] >= lo]
            else:
                filtered = filtered[(filtered[col] >= lo) & (filtered[col] <= hi)]
        elif spec.op == "in":
            vals = spec.values or []
            filtered = filtered[filtered[col].isin(vals)]
        elif spec.op == "contains":
            # substring containment (string columns)
            pat = spec.values[0] if spec.values else None
            if pat is None:
                continue
            filtered = filtered[filtered[col].astype(str).str.contains(pat, na=False)]
        elif spec.op == "regex":
            pat = spec.pattern
            if not pat:
                raise HTTPException(status_code=400, detail="Missing regex pattern for op=regex")
            filtered = filtered[filtered[col].astype(str).str.match(pat, na=False)]
        elif spec.op == "not_null":
            filtered = filtered[filtered[col].notna()]
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported filter op: {spec.op}")

    # Convert rows to native types to avoid numpy scalars in response
    rows = []
    for rec in filtered.to_dict(orient="records"):
        clean = {k: _native(v) for k, v in rec.items()}
        rows.append(clean)

    return {"count": len(rows), "rows": rows}


@router.post("/aggregate")
def aggregate(payload: AggregateRequest):
    try:
        df = pd.DataFrame(payload.rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid rows payload: {e}")

    # validate group_by
    for g in payload.group_by:
        if g not in df.columns:
            raise HTTPException(status_code=400, detail=f"Group-by column missing: {g}")

    agg_map = {}
    allowed = {"count", "sum", "mean", "min", "max", "median", "std"}
    for col, ops in payload.aggs.items():
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Agg column missing: {col}")
        funcs = []
        for op in ops:
            if op not in allowed:
                raise HTTPException(status_code=400, detail=f"Unsupported agg op: {op}")
            funcs.append(op)
        agg_map[col] = funcs

    grouped = df.groupby(payload.group_by).agg(agg_map)
    # flatten multiindex columns if present
    if isinstance(grouped.columns, pd.MultiIndex):
        grouped.columns = ["__".join(map(str, c)).strip() for c in grouped.columns.values]

    records = []
    for rec in grouped.reset_index().to_dict(orient="records"):
        clean = {k: _native(v) for k, v in rec.items()}
        records.append(clean)

    return {"count": len(records), "rows": records}
