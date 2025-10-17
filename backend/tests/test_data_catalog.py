import os
import shutil
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


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "catalog")


def setup_module(module):
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)


def teardown_module(module):
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)


def test_catalog_crud_and_search():
    # create dataset
    rv = client.post("/api/v1/catalog/", json={"name": "Test Dataset", "description": "A dataset", "tags": ["alpha", "beta"]})
    assert rv.status_code == 201
    ds = rv.json()
    ds_id = ds["id"]

    # list
    rv = client.get("/api/v1/catalog/")
    assert rv.status_code == 200
    listings = rv.json()["datasets"]
    assert any(d["id"] == ds_id for d in listings)

    # get
    rv = client.get(f"/api/v1/catalog/{ds_id}")
    assert rv.status_code == 200
    loaded = rv.json()
    assert loaded["name"] == "Test Dataset"

    # add version
    rv = client.post(f"/api/v1/catalog/{ds_id}/versions", json={"file_path": "/tmp/data.csv", "metadata": {"rows": 10}})
    assert rv.status_code == 201
    ver = rv.json()
    assert "id" in ver

    # search by tag
    rv = client.get("/api/v1/catalog/search", params={"q": "test", "tags": "alpha"})
    assert rv.status_code == 200
    found = rv.json()["datasets"]
    assert any(d["id"] == ds_id for d in found)

    # delete
    rv = client.delete(f"/api/v1/catalog/{ds_id}")
    assert rv.status_code == 204
