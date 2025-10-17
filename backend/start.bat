@echo off
echo Starting SPARTA AI Backend...
echo.
echo Make sure you have:
echo 1. Activated virtual environment (venv\Scripts\activate)
echo 2. Installed dependencies (pip install -r requirements.txt)
echo 3. Initialized database (python init_db.py)
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
