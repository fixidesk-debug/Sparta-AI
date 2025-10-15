import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest import mock
from sqlalchemy.exc import OperationalError

client = TestClient(app)

def test_health_endpoint_basic():
    r = client.get('/health')
    assert r.status_code == 200
    data = r.json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data


def test_liveness_and_readiness():
    r = client.get('/health/live')
    assert r.status_code == 200
    assert r.json() == {'status': 'alive'}

    r2 = client.get('/health/ready')
    assert r2.status_code == 200
    assert r2.json()['status'] in ('ready', 'not ready')


def test_detailed_health_with_unhealthy_db():
    # mock DB to raise on execute
    class DummyDB:
        def execute(self, *args, **kwargs):
            raise OperationalError('test', None, None)

    mock_redis = mock.MagicMock()
    mock_redis.ping.side_effect = Exception('redis down')

    # Override dependencies used by FastAPI
    from app.api.v1.endpoints import health
    app.dependency_overrides[health.get_db] = lambda: DummyDB()
    app.dependency_overrides[health.get_redis] = lambda: mock_redis

    try:
        r = client.get('/health/detailed')
        assert r.status_code == 200
        data = r.json()
        assert data['status'] in ('degraded', 'healthy')
        assert data['dependencies']['database'] == 'unhealthy'
        assert data['dependencies']['redis'] == 'unhealthy'
    finally:
        app.dependency_overrides.clear()


def test_detailed_health_all_healthy():
    class DummyDB:
        def execute(self, *args, **kwargs):
            return None

    mock_redis = mock.MagicMock()
    mock_redis.ping.return_value = True

    from app.api.v1.endpoints import health
    app.dependency_overrides[health.get_db] = lambda: DummyDB()
    app.dependency_overrides[health.get_redis] = lambda: mock_redis

    try:
        r = client.get('/health/detailed')
        assert r.status_code == 200
        data = r.json()
        assert data['status'] == 'healthy'
        assert data['dependencies']['database'] == 'healthy'
        assert data['dependencies']['redis'] == 'healthy'
    finally:
        app.dependency_overrides.clear()
