from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import pandas as pd

from app.services.data_validation import DataValidator, Rule, ValidationResult, save_report
import numpy as np

router = APIRouter()


class RulePayload(BaseModel):
    name: str
    column: str
    rule_type: str
    value: Optional[Any] = None
    severity: float = 0.5


class ValidatePayload(BaseModel):
    rows: List[Dict[str, Any]] = Field(..., description="List of row dicts to validate")
    rules: List[RulePayload] = Field(..., description="Validation rules")


@router.post("/validate")
def validate(payload: ValidatePayload):
    try:
        df = pd.DataFrame(payload.rows)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid rows payload: {e}")

    rules = [Rule(name=r.name, column=r.column, rule_type=r.rule_type, value=r.value, severity=r.severity) for r in payload.rules]
    dv = DataValidator(rules=rules)
    result = dv.validate(df)
    # build response and coerce numpy types to native Python types for JSON encoding
    # score
    score = float(result.score)

    # lineage: copy and coerce sample values
    lineage = dict(result.lineage) if result.lineage is not None else {}
    cols = lineage.get("columns_detail", {})
    safe_cols = {}
    for col, meta in cols.items():
        sample = meta.get("sample_value")
        if isinstance(sample, np.generic):
            try:
                sample = sample.item()
            except Exception:
                sample = str(sample)
        safe_cols[col] = {"sample_value": sample, "dtype": meta.get("dtype")}
    if safe_cols:
        lineage["columns_detail"] = safe_cols

    # results: ensure native types
    results = []
    for r in result.results:
        results.append({
            "rule": r.rule.name,
            "passed": bool(r.passed),
            "failing_count": int(r.failing_count),
            "total": int(r.total),
        })

    resp = {"score": score, "lineage": lineage, "results": results}
    return resp
