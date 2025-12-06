# Cargo Capacity Prediction - Setup & Training Guide

This guide will help you load your Google Sheets data and train the ML models for cargo capacity prediction.

## Prerequisites

1. **Python Environment**: Make sure you have Python 3.8+ installed
2. **Dependencies**: Install backend dependencies
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Database**: SQLite database will be created automatically

## Quick Start

### Option 1: Automated Setup (Recommended)

Run the complete setup script that guides you through all steps:

```bash
cd backend
python scripts/setup_and_train.py
```

This script will:
1. Initialize the database
2. Help you load data from Google Sheets
3. Train the ML model

### Option 2: Manual Setup

#### Step 1: Initialize Database

```bash
cd backend
python scripts/init_db.py
```

#### Step 2: Load Data from Google Sheets

You have two options:

**Option A: Export CSV and Load**
1. Open your Google Sheets: https://docs.google.com/spreadsheets/d/1Y9zVyc2UKIVgPSwrawVkj9o-pImfb0xOOHkParpUJ6A/edit?gid=1925197823#gid=1925197823
2. Go to File → Download → Comma-separated values (.csv)
3. Save the file (e.g., as `flight_data.csv`)
4. Run the loading script:
   ```bash
   python scripts/load_google_sheets_data.py flight_data.csv
   ```

**Option B: Load Directly from Google Sheets URL**
```bash
python scripts/load_google_sheets_data.py "https://docs.google.com/spreadsheets/d/1Y9zVyc2UKIVgPSwrawVkj9o-pImfb0xOOHkParpUJ6A/edit?gid=1925197823#gid=1925197823"
```

**Note**: The URL method requires the sheet to be publicly accessible or exported. For private sheets, use Option A.

#### Step 3: Train the Model

```bash
python scripts/train_baggage_model.py
```

This will:
- Load all flight data from the database
- Train baggage weight/volume prediction models
- Save models to `backend/models/` directory
- Display training metrics (R², MAE, etc.)

## Expected Output

### Data Loading
```
Loading data from: flight_data.csv
Found 100 records to import
Processed 100/100 records...

✓ Import complete!
  - Imported/Updated: 100
  - Skipped: 0
```

### Model Training
```
Training baggage prediction models...
Training complete!
  Weight Model - R²: 0.850, MAE: 245.32 kg
  Volume Model - R²: 0.845, MAE: 3.67 m³

✅ Models saved to backend/models/
```

## Verify Setup

### Test the API

Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Test a prediction:
```bash
curl -X POST "http://localhost:8000/api/v1/cargo/predict-capacity" \
  -H "Content-Type: application/json" \
  -d '{
    "aircraft_type": "Boeing 737-800",
    "passenger_count": 162,
    "origin": "KUL",
    "destination": "SIN",
    "flight_date": "2024-01-15T10:00:00",
    "days_before_flight": 7
  }'
```

### View in Frontend

1. Start the frontend (if not already running):
   ```bash
   cd frontend
   npm run dev
   ```

2. Navigate to: http://localhost:5173/cargo-analytics

3. Select a flight and adjust the "Days Before Flight" dropdown to see predictions

## Troubleshooting

### "No training data found in database"
- Make sure you've run the data loading script first
- Check that the CSV file has the correct columns:
  - `flight_number`, `flight_date`, `origin`, `destination`
  - `tail_number`, `aircraft_type`
  - `passenger_count`, `baggage_weight_kg`
  - `gross_weight_cargo_kg`, `gross_volume_cargo_m3`

### "Error: No module named 'app'"
- Make sure you're running scripts from the `backend` directory
- Or use: `python -m scripts.train_baggage_model`

### Model Performance is Poor
- Ensure you have enough training data (recommended: 100+ flights)
- Check data quality: missing values, outliers
- Try retraining with more data

### Database Errors
- If you need to start fresh, delete the database file:
  ```bash
  rm flight_delays.db  # Linux/Mac
  del flight_delays.db  # Windows
  ```
- Then re-run `init_db.py`

## Files Created

After training, you'll have:
- `backend/models/baggage_weight_model.joblib` - Trained weight prediction model
- `backend/models/baggage_volume_model.joblib` - Trained volume prediction model
- `backend/models/route_encoder.joblib` - Route encoding for ML features
- `backend/models/aircraft_encoder.joblib` - Aircraft type encoding

## Next Steps

1. **Use Predictions**: The models are now ready to use in the API and frontend
2. **Monitor Performance**: Compare predictions vs actuals over time
3. **Retrain Periodically**: As you get more data, retrain to improve accuracy
4. **Customize Aircraft Types**: Add more aircraft to `cargo_capacity_predictor.py` if needed

## API Endpoints

Once models are trained, you can use:

- `POST /api/v1/cargo/predict-capacity` - Predict capacity for any flight
- `GET /api/v1/cargo/analytics/{flight_id}?days_before_flight=7` - Get analytics with predictions
- `POST /api/v1/cargo/predict-capacity-by-flight/{flight_id}` - Predict for existing flight

See API docs at: http://localhost:8000/api/docs
