# Next Steps - After Model Training

Congratulations! Your ML models have been trained. Here's how to use them:

## Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Step 2: Start the Frontend

Open a **new terminal** and run:

```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:5173

## Step 3: Test Predictions

### Option A: Test via Frontend (Recommended)

1. Navigate to: http://localhost:5173/cargo-analytics
2. Select a flight from the dropdown
3. Use the "Days Before Flight" selector to see predictions for different time horizons
4. View:
   - Available cargo capacity (weight & volume)
   - Confidence intervals
   - Baggage predictions
   - Constraining factor (weight vs volume)
   - Overbooking risk assessment

### Option B: Test via API

#### Get Cargo Analytics for a Flight

```bash
# Replace {flight_id} with an actual flight ID from your database
curl http://localhost:8000/api/v1/cargo/analytics/{flight_id}?days_before_flight=7
```

#### Predict Capacity for a New Flight

```bash
curl -X POST "http://localhost:8000/api/v1/cargo/predict-capacity" \
  -H "Content-Type: application/json" \
  -d '{
    "aircraft_type": "Boeing 737-800",
    "passenger_count": 162,
    "origin": "KUL",
    "destination": "SIN",
    "flight_date": "2024-02-15T10:00:00",
    "days_before_flight": 7
  }'
```

### Option C: Use the Interactive API Docs

1. Visit: http://localhost:8000/api/docs
2. Find the `/api/v1/cargo/predict-capacity` endpoint
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"

## Step 4: Verify Model Performance

Check the model files created:

```bash
cd backend
dir models
```

You should see:
- `baggage_weight_model.joblib` - Weight prediction model
- `baggage_volume_model.joblib` - Volume prediction model
- `route_encoder.joblib` - Route encoding
- `aircraft_encoder.joblib` - Aircraft encoding

## Understanding the Predictions

### What You'll See:

1. **Available Weight/Volume**: How much cargo space is predicted to be available
2. **Confidence Intervals**: Range of possible values (95% confidence)
3. **Constraining Factor**: Whether weight or volume is the limiting factor
4. **Overbooking Risk**: Low/Medium/High - risk of overselling cargo space
5. **Baggage Prediction**: Predicted passenger baggage weight and volume

### Days Before Flight Impact:

- **0 days** (Day of Flight): Most accurate, but too late for planning
- **7 days**: Good balance of accuracy and advance planning
- **14-30 days**: Lower accuracy but enables early cargo sales

## Common Use Cases

### 1. Daily Capacity Planning
```bash
# Get predictions for all flights tomorrow
# (You'd query your database for tomorrow's flights)
# Then call the API for each flight
```

### 2. Cargo Sales Optimization
- Use predictions 7-14 days before flight
- Adjust pricing based on predicted availability
- Prioritize high-value cargo when capacity is limited

### 3. Route Analysis
- Compare predicted vs actual capacity over time
- Identify routes with consistent capacity constraints
- Adjust flight scheduling based on patterns

## Troubleshooting

### "Model not found" errors
- Make sure models are in `backend/models/` directory
- Models load automatically when MLService initializes

### Poor prediction accuracy
- Check training metrics from model training output
- Ensure you have enough training data (100+ flights recommended)
- Retrain with more data as you accumulate it

### API returns errors
- Check backend logs for detailed error messages
- Verify database has flight data loaded
- Ensure flight records have passenger_count data

## Monitoring & Improvement

1. **Compare Predictions vs Actuals**:
   - After flights complete, compare predicted vs actual baggage
   - Track prediction accuracy over time

2. **Retrain Periodically**:
   - Retrain models monthly or quarterly with new data
   - Use: `python scripts/train_baggage_model.py`

3. **Model Performance Metrics**:
   - Monitor R² scores (should be > 0.7)
   - Track Mean Absolute Error (MAE)
   - Adjust if accuracy degrades

## What's Next?

1. ✅ Models trained - Done!
2. ✅ API endpoints ready - Done!
3. ✅ Frontend integrated - Done!
4. 🔄 **Start using predictions in your workflow**
5. 🔄 **Monitor and improve model performance**
6. 🔄 **Retrain periodically with new data**

## Need Help?

- Check API docs: http://localhost:8000/api/docs
- Review training metrics from model training output
- Check backend logs for detailed error messages

Happy predicting! 🚀

