@echo off
echo ========================================
echo Cargo Capacity Prediction - Quick Start
echo ========================================
echo.

cd /d "%~dp0.."

echo Step 1: Initializing database...
python scripts\init_db.py
echo.

echo Step 2: Loading data from Google Sheets...
echo Please provide the CSV file path or Google Sheets URL:
echo (You can export from: https://docs.google.com/spreadsheets/d/1Y9zVyc2UKIVgPSwrawVkj9o-pImfb0xOOHkParpUJ6A/edit)
echo.
set /p DATA_SOURCE="Enter CSV file path or URL (or press Enter to skip): "

if not "%DATA_SOURCE%"=="" (
    python scripts\load_google_sheets_data.py "%DATA_SOURCE%"
    echo.
)

echo Step 3: Training ML model...
python scripts\train_baggage_model.py
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start the backend: uvicorn app.main:app --reload
echo 2. Start the frontend: cd ..\frontend ^&^& npm run dev
echo 3. Visit: http://localhost:5173/cargo-analytics
echo.
pause
