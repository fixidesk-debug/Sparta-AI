from app.services.ml_models import MLModelsService, MLModelError


def test_metadata_and_ownership(tmp_path):
    svc = MLModelsService(model_dir=str(tmp_path / "models"))

    X = [[0, 1], [1, 0], [0, 0], [1, 1]]
    y = [0, 1, 0, 1]

    res = svc.train('random_forest_classification', X, y, params={'n_estimators': 3, 'random_state': 42})
    model_id = res['model_id']

    meta = svc.load_metadata(model_id)
    assert meta['model_type'] == 'random_forest_classification'

    # Set owner and verify listing filtering
    svc.set_owner(model_id, 'alice@example.com')
    meta2 = svc.load_metadata(model_id)
    assert meta2['owner'] == 'alice@example.com'

    # List filtering
    all_models = svc.list_models()
    assert any(m['model_id'] == model_id for m in all_models)

    alice_models = svc.list_models(owner='alice@example.com')
    assert any(m['model_id'] == model_id for m in alice_models)

    bob_models = svc.list_models(owner='bob@example.com')
    assert not any(m['model_id'] == model_id for m in bob_models)

    # Delete and ensure it's gone
    svc.delete_model(model_id)
    try:
        svc.load_metadata(model_id)
        assert False, "Expected metadata load to fail after deletion"
    except MLModelError:
        pass
