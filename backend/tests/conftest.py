import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure the repository root (backend folder) is on sys.path so `import app` works
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app

# Use TestClient for API tests
@pytest.fixture(scope='session')
def client():
    with TestClient(app) as c:
        yield c

# Example: database fixture using env vars (for integration tests)
@pytest.fixture(scope='session')
def db_url():
    return os.environ.get('TEST_DATABASE_URL', 'postgresql://sparta:sparta_pass@localhost:5433/sparta_test')

@pytest.fixture
def sample_user():
    return {"username": "testuser", "password": "password123"}
