import os
import shutil
import json
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.endpoints.exec import get_current_user


class DummyUser:
    def __init__(self, id: str = "test-user"):
        self.id = id


def override_get_current_user():
    return DummyUser()


app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "notebooks")


def setup_module(module):
    # ensure clean test data dir
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)


def teardown_module(module):
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)


def test_cell_crud_and_move():
    # create notebook
    rv = client.post("/api/v1/notebooks/", json={"title": "Cells NB", "cells": []})
    assert rv.status_code == 201
    nb = rv.json()
    nb_id = nb["id"]

    # add a cell
    payload = {"type": "code", "language": "python", "source": "print(1)", "metadata": {}}
    rv = client.post(f"/api/v1/notebooks/{nb_id}/cells", json=payload)
    assert rv.status_code == 201
    cell = rv.json()
    cell_id = cell["id"]
    assert cell["source"] == "print(1)"

    # update the cell
    rv = client.patch(f"/api/v1/notebooks/{nb_id}/cells/{cell_id}", json={"source": "print(2)"})
    assert rv.status_code == 200
    updated = rv.json()
    assert updated["source"] == "print(2)"

    # add another cell
    payload2 = {"type": "code", "language": "python", "source": "print(3)", "metadata": {}}
    rv = client.post(f"/api/v1/notebooks/{nb_id}/cells", json=payload2)
    assert rv.status_code == 201
    c2 = rv.json()

    # move first cell to index 1 (end)
    rv = client.post(f"/api/v1/notebooks/{nb_id}/cells/{cell_id}/move", json={"position": 1})
    assert rv.status_code == 200
    data = rv.json()
    cells = data["cells"]
    assert len(cells) == 2
    assert cells[1]["id"] == cell_id

    # delete the first cell (which is c2 now)
    rv = client.delete(f"/api/v1/notebooks/{nb_id}/cells/{c2['id']}")
    assert rv.status_code == 204

    # final notebook should have one cell
    rv = client.get(f"/api/v1/notebooks/{nb_id}")
    assert rv.status_code == 200
    final = rv.json()
    assert len(final.get("cells", [])) == 1
