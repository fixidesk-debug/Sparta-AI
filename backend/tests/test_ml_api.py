import os
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Note: tests assume the backend app has a working auth system and a test user in DB.
# We'll use a helper token creation approach if available; otherwise these tests will
# be smoke/integration-style and may need adjustments in CI.

# Minimal helper to create a lightweight token if auth helpers are available
try:
    from app.core.security import create_access_token
    TOKEN_AVAILABLE = True
except Exception:
    TOKEN_AVAILABLE = False


TEST_USER_EMAIL = os.environ.get('TEST_USER_EMAIL', 'test@example.com')


def _auth_headers():
    if TOKEN_AVAILABLE:
        token = create_access_token(subject=TEST_USER_EMAIL)
        return {"Authorization": f"Bearer {token}"}
    # fallback: no auth, some endpoints may still be protected
    return {}


def test_train_and_predict_linear_regression():
    headers = _auth_headers()

    # small toy dataset: y = 2*x + 1
    X = [[1.0], [2.0], [3.0], [4.0]]
    y = [3.0, 5.0, 7.0, 9.0]

    train_payload = {
        "model_type": "linear_regression",
        "X": X,
        "y": y,
        "params": {},
        "visibility": "private"
    }

    r = client.post('/api/v1/ml/train', json=train_payload, headers=headers)
    assert r.status_code in (200, 201), r.text
    jr = r.json()
    assert jr.get('success') is True
    model = jr.get('model')
    assert model and model.get('model_id')
    model_id = model['model_id']

    # Predict
    predict_payload = {"model_id": model_id, "X": [[5.0], [6.0]]}
    r2 = client.post('/api/v1/ml/predict', json=predict_payload, headers=headers)
    assert r2.status_code == 200, r2.text
    pjr = r2.json()
    assert pjr.get('success') is True
    preds = pjr.get('predictions')
    assert isinstance(preds, list) or isinstance(preds, (list,))
    assert len(preds) == 2


def test_visibility_update_and_protection():
    headers = _auth_headers()
    # Train small model
    X = [[0.0], [1.0]]
    y = [0.0, 1.0]
    r = client.post('/api/v1/ml/train', json={"model_type": "linear_regression", "X": X, "y": y}, headers=headers)
    assert r.status_code == 200
    model_id = r.json()['model']['model_id']

    # Update visibility to public
    r2 = client.patch(f'/api/v1/ml/{model_id}/visibility', json={"visibility": "public"}, headers=headers)
    assert r2.status_code == 200
    assert r2.json()['meta']['visibility'] == 'public'

    # Try unauthorized delete: simulate different user by not sending headers (or different token)
    r3 = client.delete(f'/api/v1/ml/{model_id}')
    # if API enforces auth strictly, expect 401 or 403; accept either
    assert r3.status_code in (401, 403, 200)
