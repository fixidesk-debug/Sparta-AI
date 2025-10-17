@echo off
echo ========================================
echo SPARTA AI - Setup Script
echo ========================================
echo.

echo [1/4] Setting up Backend...
cd backend

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo Initializing database...
python init_db.py

cd ..

echo.
echo [2/4] Setting up Frontend...
cd frontend

echo Installing Node dependencies...
call npm install

cd ..

echo.
echo [3/4] Creating uploads directory...
mkdir backend\uploads 2>nul

echo.
echo [4/4] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Start Backend:  START_BACKEND.bat
echo 2. Start Frontend: START_FRONTEND.bat
echo 3. Open browser:   http://localhost:3000
echo.
echo Backend API:       http://localhost:8000
echo API Docs:          http://localhost:8000/docs
echo ========================================
pause
