import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure the repository root (backend folder) is on sys.path so `import app` works
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Ensure test DATABASE_URL/REDIS_URL are set before importing the application so
# the SQLAlchemy engine and other clients are configured for the test DB.
TEST_DB = os.environ.get('TEST_DATABASE_URL', 'postgresql://sparta:sparta_pass@localhost:5433/sparta_test')
os.environ.setdefault('DATABASE_URL', TEST_DB)
os.environ.setdefault('REDIS_URL', os.environ.get('TEST_REDIS_URL', 'redis://localhost:6379/0'))

from app.main import app

# Initialize (drop/create) the test database schema to match models
from app.db.session import engine
from app.db.models import Base


@pytest.fixture(scope='session', autouse=True)
def init_test_db():
    # ensure a clean schema matching current models if the test DB is available
    from sqlalchemy.exc import OperationalError
    try:
        try:
            Base.metadata.drop_all(bind=engine)
        except Exception:
            # ignore if drop fails on first run
            pass
        Base.metadata.create_all(bind=engine)
        created = True
    except OperationalError as e:
        # Database not reachable or DB does not exist in container; skip schema setup.
        # Tests that require DB should either start the DB or override get_db.
        created = False
        print(f"[tests/conftest.py] Warning: test database not available: {e}")

    yield

    if created:
        try:
            Base.metadata.drop_all(bind=engine)
        except Exception:
            pass

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
