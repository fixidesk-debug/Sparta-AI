import pandas as pd
import numpy as np
from app.services.data_validation import DataValidator, Rule, save_report
from pathlib import Path


def test_basic_not_null_and_range(tmp_path: Path):
    df = pd.DataFrame({
        "a": [1, 2, None, 4],
        "b": [10, 20, 30, 40]
    })

    rules = [
        Rule(name="a_not_null", column="a", rule_type="not_null", severity=1.0),
        Rule(name="b_range", column="b", rule_type="range", value=(5, 35), severity=0.5),
    ]

    v = DataValidator(rules=rules)
    res = v.validate(df)

    # a_not_null should fail because one None
    a_res = next(r for r in res.results if r.rule.name == "a_not_null")
    assert a_res.failing_count == 1

    # b_range should have one failing (40)
    b_res = next(r for r in res.results if r.rule.name == "b_range")
    assert b_res.failing_count == 1

    # score should be between 0 and 1
    assert 0.0 <= res.score <= 1.0

    # test save_report writes file
    out = tmp_path / "report.json"
    save_report(res, out)
    assert out.exists()


def test_empty_dataframe():
    df = pd.DataFrame(columns=["x", "y"])  # zero rows
    rules = [Rule(name="x_not_null", column="x", rule_type="not_null", severity=1.0)]
    v = DataValidator(rules=rules)
    res = v.validate(df)
    # empty dataset -> not_null considered failing (score 0)
    assert res.score == 0.0


def test_missing_column_behavior():
    df = pd.DataFrame({"a": [1, 2, 3]})
    rules = [Rule(name="z_not_null", column="z", rule_type="not_null", severity=1.0),
             Rule(name="a_min", column="a", rule_type="min", value=0, severity=0.5)]
    v = DataValidator(rules=rules)
    res = v.validate(df)
    # missing column z counts as failing all rows
    z_res = next(r for r in res.results if r.rule.name == "z_not_null")
    assert z_res.failing_count == 3
    # a_min should pass
    a_res = next(r for r in res.results if r.rule.name == "a_min")
    assert a_res.failing_count == 0
