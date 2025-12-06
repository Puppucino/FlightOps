@echo off
REM Setup script for Flight Delay Prediction Framework (Windows)
REM This script sets up both backend and frontend

echo Setting up Flight Delay Prediction Framework...

REM Backend setup
echo Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
echo Backend setup complete!
cd ..

REM Frontend setup
echo Setting up frontend...
cd frontend
call npm install
echo Frontend setup complete!
cd ..

echo Framework setup complete!
echo.
echo To start the backend:
echo   cd backend
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload
echo.
echo To start the frontend:
echo   cd frontend
echo   npm run dev

