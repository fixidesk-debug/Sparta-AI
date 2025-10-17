import shutil
from pathlib import Path
import numpy as np

from app.services.ml_models import MLModelsService


def test_train_and_predict_rf_classification(tmp_path):
    model_dir = tmp_path / "models"
    svc = MLModelsService(model_dir=str(model_dir))

    # Simple binary classification dataset
    X = [[0, 1], [1, 0], [0, 0], [1, 1]]
    y = [0, 1, 0, 1]

    res = svc.train('random_forest_classification', X, y, params={'n_estimators': 5, 'random_state': 42})
    assert 'model_id' in res

    model_id = res['model_id']

    preds = svc.predict(model_id, [[0, 1], [1, 0]])
    assert 'predictions' in preds
    assert len(preds['predictions']) == 2
