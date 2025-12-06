import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.ensemble import RandomForestRegressor
from catboost import Pool
import pickle

# --------------------------------------------------
# Load LightGBM model
# --------------------------------------------------
lgb_model_path = "../trained_models/arr_delay_model_lgbm_ensemble.txt"
model_lgb = lgb.Booster(model_file=lgb_model_path)

# --------------------------------------------------
# Load RandomForest model
# --------------------------------------------------
rf_model_path = "../trained_models/arr_delay_model_rf.pkl"
with open(rf_model_path, "rb") as f:
    model_rf = pickle.load(f)

# --------------------------------------------------
# Feature lists (MATCHES training script!)
# --------------------------------------------------
numeric_features = [
    'Distance', 'temp', 'dewp', 'slp', 'DepHour', 'DayOfWeek',
    'Month', 'is_weekend', 'temp_diff', 'Speed', 'visib', 'wdsp'
]

categorical_features = ['UniqueCarrier', 'Origin', 'Dest']

all_features = numeric_features + categorical_features


# --------------------------------------------------
# Preprocess + feature engineering
# --------------------------------------------------
def preprocess(input_dict):
    df = pd.DataFrame([input_dict])

    # Required feature engineering
    df['DepHour'] = df['DepTime'] // 100
    df['DayOfWeek'] = pd.to_datetime(df['Date']).dt.dayofweek
    df['Month'] = pd.to_datetime(df['Date']).dt.month
    df['is_weekend'] = (df['DayOfWeek'] >= 5).astype(int)
    df['temp_diff'] = df['temp'] - df['dewp']
    df['Speed'] = df['Distance'] / df['CRSElapsedTime']

    # Ensure categorical dtype
    for col in categorical_features:
        df[col] = df[col].astype("category")

    # Return only model inputs
    return df[all_features]


# --------------------------------------------------
# Predict function
# --------------------------------------------------
def predict_delay(input_dict):
    df = preprocess(input_dict)

    # LGBM prediction (handling categoricals automatically)
    pred_lgb = model_lgb.predict(df)

    # Random forest only uses numeric features
    pred_rf = model_rf.predict(df[numeric_features])

    # Ensemble
    final_pred = (pred_lgb * 0.7) + (pred_rf * 0.3)

    return float(final_pred[0])


# --------------------------------------------------
# Optional test
# --------------------------------------------------
if __name__ == "__main__":
    sample = {
        "Date": "2019-01-05",
        "DepTime": 1430,
        "CRSElapsedTime": 150,
        "Distance": 1000,
        "temp": 10,
        "dewp": 5,
        "slp": 1015,
        "visib": 10,
        "wdsp": 12,
        "UniqueCarrier": "AA",
        "Origin": "JFK",
        "Dest": "LAX"
    }

    print("Predicted delay:", predict_delay(sample))
