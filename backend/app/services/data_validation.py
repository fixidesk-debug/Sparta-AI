from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from pathlib import Path
import json


@dataclass
class Rule:
    """Simple validation rule descriptor.

    Attributes:
        name: unique rule name
        column: column the rule applies to
        rule_type: one of 'not_null', 'min', 'max', 'in_set', 'regex'
        value: parameter for the rule (min/max value, allowed set, regex)
        severity: float in [0,1] where 1 is most severe
    """
    name: str
    column: str
    rule_type: str
    value: Optional[Any] = None
    severity: float = 0.5


@dataclass
class RuleResult:
    rule: Rule
    passed: bool
    failing_count: int
    total: int


@dataclass
class ValidationResult:
    results: List[RuleResult]
    score: float
    lineage: Dict[str, Any]


class DataValidator:
    """Lightweight data validator supporting basic rule types, scoring and lineage."""

    SUPPORTED = {"not_null", "min", "max", "in_set", "range"}

    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules = rules or []

    def add_rule(self, rule: Rule) -> None:
        if rule.rule_type not in self.SUPPORTED:
            raise ValueError(f"Unsupported rule type: {rule.rule_type}")
        self.rules.append(rule)

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        total_rows = len(df)
        rule_results: List[RuleResult] = []
        lineage: Dict[str, Any] = {"columns": list(df.columns), "rows": total_rows}

        if total_rows == 0:
            # Empty dataset: all not_null rules fail, others vacuously pass
            for r in self.rules:
                if r.rule_type == "not_null":
                    fr = RuleResult(rule=r, passed=False, failing_count=0, total=0)
                else:
                    fr = RuleResult(rule=r, passed=True, failing_count=0, total=0)
                rule_results.append(fr)
            score = 0.0 if any(r.rule_type == "not_null" for r in self.rules) else 1.0
            return ValidationResult(results=rule_results, score=score, lineage=lineage)

        weighted_total = 0.0
        weighted_fail = 0.0

        for r in self.rules:
            if r.column not in df.columns:
                # missing column -> count as failing for not_null, else skip
                if r.rule_type == "not_null":
                    failing = total_rows
                    passed = False
                else:
                    failing = 0
                    passed = True
                rr = RuleResult(rule=r, passed=passed, failing_count=failing, total=total_rows)
                rule_results.append(rr)
                weighted_total += r.severity
                weighted_fail += r.severity * (failing / max(1, total_rows))
                continue

            col = df[r.column]
            failing = 0

            if r.rule_type == "not_null":
                failing = int(col.isna().sum())
            elif r.rule_type == "min":
                fv = _to_float(r.value)
                if fv is None:
                    failing = int(col.isna().sum())
                else:
                    comp = col < fv
                    failing = int(comp.sum())
            elif r.rule_type == "max":
                fv = _to_float(r.value)
                if fv is None:
                    failing = int(col.isna().sum())
                else:
                    comp = col > fv
                    failing = int(comp.sum())
            elif r.rule_type == "in_set":
                allowed = _to_set(r.value)
                comp = ~col.isin(allowed)
                failing = int(comp.sum())
            elif r.rule_type == "range":
                bounds = _to_two_floats(r.value)
                if not bounds:
                    failing = int(col.isna().sum())
                else:
                    lo, hi = bounds
                    comp = (col < lo) | (col > hi)
                    failing = int(comp.sum())
            else:
                # unknown rule type (shouldn't happen due to add_rule guard)
                failing = 0

            passed = failing == 0
            rr = RuleResult(rule=r, passed=passed, failing_count=failing, total=total_rows)
            rule_results.append(rr)

            weighted_total += r.severity
            weighted_fail += r.severity * (failing / max(1, total_rows))

        score = 1.0 - (weighted_fail / weighted_total) if weighted_total > 0 else 1.0
        # clamp
        score = max(0.0, min(1.0, score))

        # Build lineage details: for each column, sample first non-null index/value
        col_lineage: Dict[str, Any] = {}
        for c in df.columns:
            sample_val = None
            nonnull = df[c].dropna()
            if len(nonnull) > 0:
                sample_val = _to_native(nonnull.iloc[0])
            col_lineage[c] = {"sample_value": sample_val, "dtype": str(df[c].dtype)}

        lineage["columns_detail"] = col_lineage

        return ValidationResult(results=rule_results, score=score, lineage=lineage)


def _to_float(v: Any) -> Optional[float]:
    """Safely coerce a value to float or return None if not possible."""
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        try:
            return float(np.asarray(v))
        except Exception:
            return None


def _to_two_floats(v: Any) -> Optional[Tuple[float, float]]:
    """Try to extract two numeric bounds (lo, hi) from value."""
    if v is None:
        return None
    try:
        a, b = v
        return float(a), float(b)
    except Exception:
        return None


def _to_set(v: Any) -> set:
    try:
        return set(v or [])
    except Exception:
        return set()


def _to_native(v: Any) -> Any:
    """Convert numpy/pandas scalar types into native Python types for JSON-safety."""
    if v is None:
        return None
    # numpy scalars
    if isinstance(v, (np.generic,)):
        try:
            return v.item()
        except Exception:
            try:
                return float(v)
            except Exception:
                return str(v)
    # pandas Timestamp
    try:
        import pandas as _pd

        if isinstance(v, _pd.Timestamp):
            return str(v)
    except Exception:
        pass
    return v


def save_report(result: ValidationResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({
            "score": result.score,
            "lineage": result.lineage,
            "results": [
                {"rule": asdict(r.rule), "passed": r.passed, "failing_count": r.failing_count, "total": r.total}
                for r in result.results
            ]
        }, fh, indent=2, default=str)
