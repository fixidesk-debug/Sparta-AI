from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main as app_main
from app.main import app as fastapi_app
from app.api.v1.endpoints.exec import get_current_user as get_current_user_exec
from app.api.v1.endpoints import files as files_module
from app.db.session import get_db
from app.db.base import Base


class DummyUser:
    def __init__(self, id: int = 1):
        self.id = id


def override_get_current_user():
    return DummyUser()


# Provide an in-memory SQLite database for tests to avoid requiring Postgres during unit tests
TEST_SQLITE_URL = "sqlite:///:memory:"
# Use StaticPool so the in-memory SQLite DB is accessible across threads used by TestClient
engine = create_engine(
    TEST_SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Patch the application's DB engine references so the startup uses our in-memory DB
import app.db.session as db_session_module
db_session_module.engine = engine
app_main.engine = engine


# Ensure all models are imported and tables created in the in-memory DB
import app.db.models  # register models on Base
Base.metadata.create_all(bind=engine)


# Apply dependency overrides and auth override
fastapi_app.dependency_overrides[get_current_user_exec] = override_get_current_user
fastapi_app.dependency_overrides[files_module.get_current_user] = override_get_current_user
fastapi_app.dependency_overrides[get_db] = override_get_db


# Now create the TestClient (after DB and overrides are set)
client = TestClient(fastapi_app)


def test_create_dataset_from_nonexistent_file_returns_404():
    rv = client.post("/api/v1/files/9999/create_dataset", json={"dataset_name": "FromFile", "description": "desc", "tags": "alpha,beta"})
    assert rv.status_code == 404
