import json
import os
from fastapi.testclient import TestClient
import pytest

from app.main import app


client = TestClient(app)


class DummyUser:
    id = 1
    email = "test@example.com"


@pytest.fixture(autouse=True)
def patch_auth(monkeypatch, tmp_path):
    # Monkeypatch get_current_user to return a dummy user
    from app.api.v1.endpoints.exec import get_current_user as real_dep

    # Set FastAPI dependency override so all routes using get_current_user are satisfied
    app.dependency_overrides[real_dep] = lambda: DummyUser()

    # ensure notebooks data dir is under tmp_path and run tests from there
    os.chdir(tmp_path)
    try:
        yield
    finally:
        app.dependency_overrides.pop(real_dep, None)


def test_create_list_get_delete_notebook():
    # Create
    res = client.post("/api/v1/notebooks/", json={"title": "My NB", "cells": [{"source": "print(1)", "type": "code"}]})
    assert res.status_code == 201
    nb = res.json()
    assert nb["title"] == "My NB"
    nb_id = nb["id"]

    # List
    res = client.get("/api/v1/notebooks/")
    assert res.status_code == 200
    lst = res.json()["notebooks"]
    assert any(n["id"] == nb_id for n in lst)

    # Get
    res = client.get(f"/api/v1/notebooks/{nb_id}")
    assert res.status_code == 200
    got = res.json()
    assert got["id"] == nb_id

    # Delete
    res = client.delete(f"/api/v1/notebooks/{nb_id}")
    assert res.status_code == 204

    # Not found afterwards
    res = client.get(f"/api/v1/notebooks/{nb_id}")
    assert res.status_code == 404


def test_run_cell(monkeypatch):
    # create a notebook
    res = client.post("/api/v1/notebooks/", json={"title": "Run NB", "cells": [{"source": "print('hi')", "type": "code"}]})
    assert res.status_code == 201
    nb = res.json()
    nb_id = nb["id"]
    cell_id = nb["cells"][0]["id"]

    # monkeypatch CodeExecutor.execute to return deterministic result
    class StubExec:
        def __init__(self, *args, **kwargs):
            pass

        def execute(self, code, context=None):
            # ensure db helper is provided
            assert context is not None and "db" in context
            # return a deterministic result
            return {"success": True, "output": "hi\n", "error": None, "execution_time": 0.01, "images": [], "plotly_figures": [], "variables": {}, "timestamp": "now"}

    monkeypatch.setattr("app.api.v1.endpoints.notebooks.CodeExecutor", StubExec)

    res = client.post(f"/api/v1/notebooks/{nb_id}/cells/{cell_id}/run")
    assert res.status_code == 200
    out = res.json()
    assert out["success"] is True
