from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_summary_basic():
    payload = {"rows": [{"a": 1, "b": 10}, {"a": 2, "b": 20}, {"a": None, "b": 5}]}
    r = client.post("/api/v1/widgets/summary", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "columns" in data
    assert "a" in data["columns"]
    assert "b" in data["columns"]


def test_filter_range_and_in():
    payload = {"rows": [{"a": 1, "b": "x"}, {"a": 5, "b": "y"}, {"a": 10, "b": "x"}], "filters": {"a": {"op": "range", "min": 2, "max": 10}, "b": {"op": "in", "values": ["x"]}}}
    r = client.post("/api/v1/widgets/filter", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["rows"][0]["a"] == 10 or data["rows"][0]["a"] == 5


def test_aggregate_group_by():
    payload = {"rows": [{"category": "x", "value": 10}, {"category": "x", "value": 20}, {"category": "y", "value": 5}], "group_by": ["category"], "aggs": {"value": ["sum", "mean"]}}
    r = client.post("/api/v1/widgets/aggregate", json=payload)
    assert r.status_code == 200
    d = r.json()
    assert d["count"] == 2
    # find category x
    rows = {row["category"]: row for row in d["rows"]}
    assert rows["x"]["value__sum"] == 30
    assert abs(rows["x"]["value__mean"] - 15.0) < 1e-6


def test_filter_contains_and_regex():
    payload = {"rows": [{"name": "alice"}, {"name": "bob"}, {"name": "alicorn"}], "filters": {"name": {"op": "contains", "values": ["alic"]}}}
    r = client.post("/api/v1/widgets/filter", json=payload)
    assert r.status_code == 200
    d = r.json()
    assert d["count"] == 2

    payload2 = {"rows": [{"tag": "A-123"}, {"tag": "B-456"}, {"tag": "A-789"}], "filters": {"tag": {"op": "regex", "pattern": r"^A-\d+"}}}
    r2 = client.post("/api/v1/widgets/filter", json=payload2)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["count"] == 2


def test_aggregate_median_std():
    payload = {"rows": [{"group": "g", "v": 1}, {"group": "g", "v": 3}, {"group": "g", "v": 5}], "group_by": ["group"], "aggs": {"v": ["median", "std"]}}
    r = client.post("/api/v1/widgets/aggregate", json=payload)
    assert r.status_code == 200
    d = r.json()
    assert d["count"] == 1
    row = d["rows"][0]
    assert row["v__median"] == 3
    # std may be floating
    assert row["v__std"] is not None
