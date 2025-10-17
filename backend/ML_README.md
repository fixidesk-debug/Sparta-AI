ML Models Service (Lightweight)
================================

This service provides a minimal in-repo ML models manager for training and
prediction. It's intended as a scaffold to be extended into production-ready
model infra.

Endpoints:
- POST /api/v1/ml/train -> train a model (JSON body with model_type, X, y)
- POST /api/v1/ml/predict -> predict with a trained model (model_id, X)
- GET  /api/v1/ml/list -> list persisted models

Supported model types:
- random_forest_classification
- random_forest_regression
- linear_regression
- kmeans

Notes:
- Models are stored under `models/ml/*.joblib` relative to the backend working directory.
- This is intentionally simple; add authentication, validation, and async handling for production.
