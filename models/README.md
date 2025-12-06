# Flight Delay Prediction Model

Optimized machine learning models for predicting flight arrival delays using weather and flight data.

## Quick Start

### Train the Model
```bash
cd models/src
python train_optimized.py
```

This automatically:
- Creates destination weather data
- Trains XGBoost + LightGBM ensemble
- Saves models to `trained_models/`

### Make Predictions
```python
from src.predict import predict_delay
import pandas as pd

flight_data = pd.DataFrame({
    'Date': ['2019-06-15'],
    'DepTime': [1400],
    'Distance': [500],
    'CRSElapsedTime': [90],
    'TaxiIn': [5],
    'TaxiOut': [10],
    'UniqueCarrier': ['WN'],
    'Origin': ['LAX'],
    'Dest': ['SFO'],
    'temp': [75], 'dewp': [60], 'slp': [1015],
    'visib': [10], 'wdsp': [8]
})

delay = predict_delay(flight_data)
print(f"Predicted delay: {delay[0]:.2f} minutes")
```

## Performance

**Best Model: XGBoost + LightGBM Ensemble**
- **R² Score: 0.38-0.43**
- **MAE: ~28-29 minutes**
- **RMSE: ~45-46 minutes**

## Model Architecture

- **XGBoost** (primary) - 70% weight in ensemble
- **LightGBM** (secondary) - 30% weight in ensemble
- **60+ features** including origin and destination weather

## Features

### Flight Features
- Distance, Speed, Taxi times
- Departure time, Temporal patterns

### Weather Features (Origin + Destination)
- Basic: Temperature, Dewpoint, Pressure, Visibility, Wind speed
- Enhanced: Relative humidity, Heat index, Weather severity
- Extreme indicators: Freezing, extreme heat, low visibility, high wind
- **Origin-Destination differences:** Temperature, visibility, wind, pressure differences
- **Origin-Destination interactions:** Weather condition interactions

### Categorical Features
- UniqueCarrier (airline)
- Origin airport
- Destination airport

## File Structure

```
models/
├── src/
│   ├── train_optimized.py    # Main training script
│   └── predict.py            # Prediction script
├── data/
│   └── flights_weather_2019_cleaned.csv
├── trained_models/
│   ├── arr_delay_model_xgb.json    # XGBoost model
│   ├── arr_delay_model_lgb.txt     # LightGBM model
│   └── ensemble_info.pkl            # Ensemble metadata
└── README.md
```

## Dependencies

```
pandas
numpy
xgboost
lightgbm
scikit-learn
```

## Notes

- Models trained on 2019 flight data
- Weather data includes both origin AND destination (auto-created)
- Best performance with ensemble approach
- R² of 0.38-0.43 indicates good predictive power
