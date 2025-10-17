from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_validate_api_basic():
    payload = {
        "rows": [
            {"a": 1, "b": 10},
            {"a": None, "b": 20},
            {"a": 3, "b": 40}
        ],
        "rules": [
            {"name": "a_not_null", "column": "a", "rule_type": "not_null", "severity": 1.0},
            {"name": "b_max", "column": "b", "rule_type": "max", "value": 30, "severity": 0.5}
        ]
    }

    r = client.post("/api/v1/validation/validate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "score" in data
    assert any(res["rule"] == "a_not_null" for res in data["results"]) is True


def test_validate_api_bad_rows():
    # rows that can't be parsed into DataFrame
    payload = {"rows": "not-a-list", "rules": []}
    r = client.post("/api/v1/validation/validate", json=payload)
    assert r.status_code == 422 or r.status_code == 400
