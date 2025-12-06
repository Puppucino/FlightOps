"""
Prediction script for flight delay model
Uses the optimized XGBoost + LightGBM ensemble
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import pickle
import os

# --------------------------
# Load Models
# --------------------------
MODEL_DIR = "../trained_models"

# Load XGBoost model (primary)
xgb_model_path = os.path.join(MODEL_DIR, "arr_delay_model_xgb.json")
if os.path.exists(xgb_model_path):
    model_xgb = xgb.XGBRegressor()
    model_xgb.load_model(xgb_model_path)
    print(f"✅ Loaded XGBoost model from {xgb_model_path}")
else:
    model_xgb = None
    print(f"⚠️  XGBoost model not found at {xgb_model_path}")

# Load LightGBM model (for ensemble)
lgb_model_path = os.path.join(MODEL_DIR, "arr_delay_model_lgb.txt")
if os.path.exists(lgb_model_path):
    model_lgb = lgb.Booster(model_file=lgb_model_path)
    print(f"✅ Loaded LightGBM model from {lgb_model_path}")
else:
    model_lgb = None
    print(f"⚠️  LightGBM model not found at {lgb_model_path}")

# Load ensemble info
ensemble_info_path = os.path.join(MODEL_DIR, "ensemble_info.pkl")
if os.path.exists(ensemble_info_path):
    with open(ensemble_info_path, 'rb') as f:
        ensemble_info = pickle.load(f)
    weights = ensemble_info.get('weights', {'xgb': 0.7, 'lgb': 0.3})
    print(f"✅ Loaded ensemble weights: XGBoost={weights.get('xgb', 0.7)}, LightGBM={weights.get('lgb', 0.3)}")
else:
    weights = {'xgb': 0.7, 'lgb': 0.3}
    print(f"⚠️  Ensemble info not found, using default weights")

# --------------------------
# Feature Lists (MUST MATCH training script!)
# --------------------------
numeric_features = [
    'Distance', 'Speed', 'TaxiTotal',
    'DepHour', 'DepMinute', 'DayOfWeek', 'Month', 'DayOfMonth', 
    'is_weekend', 'is_holiday_season',
    'temp', 'dewp', 'slp', 'visib', 'wdsp',
    'temp_diff', 'relative_humidity', 'heat_index',
    'pressure_normalized', 'pressure_category',
    'visib_category', 'temp_category',
    'is_freezing', 'is_extreme_cold', 'is_extreme_heat',
    'low_visibility', 'very_low_visibility',
    'high_wind', 'very_high_wind',
    'low_pressure', 'high_pressure',
    'temp_visib_interaction', 'wind_visib_interaction', 'temp_wind_interaction',
    'pressure_temp_interaction', 'temp_diff_pressure', 'wind_pressure_interaction',
    'weather_severity',
    'hour_temp_interaction', 'hour_visib_interaction', 'month_temp_interaction',
]

categorical_features = ['UniqueCarrier', 'Origin', 'Dest']

# Optional features (if available in data)
optional_features = {
    'gust': ['has_gust', 'gust_wind_diff', 'extreme_gust'],
    'mxpsd': ['max_wind', 'wind_variability']
}


def prepare_features(df):
    """
    Prepare features matching the training pipeline
    """
    df = df.copy()
    
    # Ensure Date is datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    
    # Temporal features
    if 'DepTime' in df.columns:
        df['DepHour'] = df['DepTime'] // 100
        df['DepMinute'] = df['DepTime'] % 100
    
    if 'Date' in df.columns:
        df['DayOfWeek'] = df['Date'].dt.dayofweek
        df['Month'] = df['Date'].dt.month
        df['DayOfMonth'] = df['Date'].dt.day
        df['is_weekend'] = (df['DayOfWeek'] >= 5).astype(int)
        df['is_holiday_season'] = df['Month'].isin([11, 12]).astype(int)
    
    # Flight characteristics
    if 'Distance' in df.columns and 'CRSElapsedTime' in df.columns:
        df['Speed'] = df['Distance'] / df['CRSElapsedTime'].replace(0, np.nan)
    
    if 'TaxiIn' in df.columns and 'TaxiOut' in df.columns:
        df['TaxiTotal'] = df['TaxiIn'].fillna(0) + df['TaxiOut'].fillna(0)
    
    # Weather features
    if 'temp' in df.columns and 'dewp' in df.columns:
        df['temp_diff'] = df['temp'] - df['dewp']
        df['relative_humidity'] = 100 * (
            np.exp((17.625 * df['dewp']) / (243.04 + df['dewp'])) / 
            np.exp((17.625 * df['temp']) / (243.04 + df['temp']))
        )
        df['heat_index'] = np.where(
            (df['temp'] >= 80) & (df['relative_humidity'] >= 40),
            0.5 * (df['temp'] + 61.0 + ((df['temp'] - 68.0) * 1.2) + (df['relative_humidity'] * 0.094)),
            df['temp']
        )
    
    # Extreme weather indicators
    if 'temp' in df.columns:
        df['is_freezing'] = (df['temp'] < 32).astype(int)
        df['is_extreme_cold'] = (df['temp'] < 0).astype(int)
        df['is_extreme_heat'] = (df['temp'] > 90).astype(int)
    
    if 'visib' in df.columns:
        df['low_visibility'] = (df['visib'] < 5).astype(int)
        df['very_low_visibility'] = (df['visib'] < 1).astype(int)
    
    if 'wdsp' in df.columns:
        df['high_wind'] = (df['wdsp'] > 20).astype(int)
        df['very_high_wind'] = (df['wdsp'] > 30).astype(int)
    
    if 'slp' in df.columns:
        df['low_pressure'] = (df['slp'] < 1000).astype(int)
        df['high_pressure'] = (df['slp'] > 1020).astype(int)
        df['pressure_normalized'] = (df['slp'] - 1013.25) / 10
        df['pressure_category'] = pd.cut(df['slp'], bins=[0, 1000, 1010, 1020, 2000], 
                                          labels=[0, 1, 2, 3], include_lowest=True).astype(float)
        df['pressure_category'] = df['pressure_category'].fillna(1)
    
    if 'visib' in df.columns:
        df['visib_category'] = pd.cut(df['visib'], bins=[0, 1, 3, 5, 10, 20], 
                                       labels=[0, 1, 2, 3, 4], include_lowest=True).astype(float)
        df['visib_category'] = df['visib_category'].fillna(4)
    
    if 'temp' in df.columns:
        df['temp_category'] = pd.cut(df['temp'], bins=[-50, 32, 50, 70, 85, 120], 
                                     labels=[0, 1, 2, 3, 4], include_lowest=True).astype(float)
        df['temp_category'] = df['temp_category'].fillna(2)
    
    # Weather interactions
    if 'temp' in df.columns and 'visib' in df.columns:
        df['temp_visib_interaction'] = df['temp'] * df['visib']
        df['hour_visib_interaction'] = df['DepHour'] * df['visib']
    
    if 'wdsp' in df.columns and 'visib' in df.columns:
        df['wind_visib_interaction'] = df['wdsp'] * df['visib']
    
    if 'temp' in df.columns and 'wdsp' in df.columns:
        df['temp_wind_interaction'] = df['temp'] * df['wdsp']
    
    if 'slp' in df.columns and 'temp' in df.columns:
        df['pressure_temp_interaction'] = df['slp'] * df['temp']
    
    if 'temp_diff' in df.columns and 'slp' in df.columns:
        df['temp_diff_pressure'] = df['temp_diff'] * df['slp']
    
    if 'wdsp' in df.columns and 'slp' in df.columns:
        df['wind_pressure_interaction'] = df['wdsp'] * df['slp']
    
    if 'DepHour' in df.columns and 'temp' in df.columns:
        df['hour_temp_interaction'] = df['DepHour'] * df['temp']
    
    if 'Month' in df.columns and 'temp' in df.columns:
        df['month_temp_interaction'] = df['Month'] * df['temp']
    
    # Weather severity
    severity_cols = ['low_visibility', 'very_low_visibility', 'high_wind', 
                     'very_high_wind', 'is_freezing', 'is_extreme_heat', 'low_pressure']
    if all(col in df.columns for col in severity_cols):
        df['weather_severity'] = (
            (df['low_visibility'] * 3) +
            (df['very_low_visibility'] * 5) +
            (df['high_wind'] * 2) +
            (df['very_high_wind'] * 4) +
            (df['is_freezing'] * 2) +
            (df['is_extreme_heat'] * 1) +
            (df['low_pressure'] * 1)
        )
    
    # Optional features
    if 'gust' in df.columns and 'wdsp' in df.columns:
        df['has_gust'] = (df['gust'] > 0).astype(int)
        df['gust_wind_diff'] = df['gust'] - df['wdsp']
        df['extreme_gust'] = (df['gust'] > 40).astype(int)
    
    if 'mxpsd' in df.columns and 'wdsp' in df.columns:
        df['max_wind'] = df['mxpsd']
        df['wind_variability'] = df['mxpsd'] - df['wdsp']
    
    # Fill missing values
    all_numeric = numeric_features.copy()
    for opt_key, opt_features in optional_features.items():
        if opt_key in df.columns:
            all_numeric.extend(opt_features)
    
    for col in all_numeric:
        if col in df.columns:
            if df[col].isnull().sum() > 0:
                df[col] = df[col].fillna(df[col].median() if df[col].dtype in [np.float64, np.int64] else 0)
    
    return df


def predict_delay(df):
    """
    Predict arrival delay for given flight data
    
    Args:
        df: DataFrame with flight and weather data
        
    Returns:
        Array of predicted delays (minutes)
    """
    # Prepare features
    df_processed = prepare_features(df)
    
    # Get all available features
    all_features = numeric_features.copy()
    for opt_key, opt_features in optional_features.items():
        if opt_key in df_processed.columns:
            all_features.extend(opt_features)
    
    # Filter to available features
    available_numeric = [f for f in all_features if f in df_processed.columns]
    available_categorical = [f for f in categorical_features if f in df_processed.columns]
    
    # Prepare data
    X = df_processed[available_numeric + available_categorical].copy()
    
    # Handle categoricals
    for col in available_categorical:
        if col in X.columns:
            X[col] = X[col].astype('category')
    
    # Fill any remaining NaN
    for col in available_numeric:
        if col in X.columns and X[col].isnull().sum() > 0:
            X[col] = X[col].fillna(X[col].median())
    
    predictions = []
    
    # XGBoost prediction
    if model_xgb is not None:
        X_xgb = X.copy()
        for col in available_categorical:
            if col in X_xgb.columns:
                X_xgb[col] = X_xgb[col].cat.codes
        pred_xgb = model_xgb.predict(X_xgb)
        predictions.append(('xgb', pred_xgb, weights.get('xgb', 0.7)))
    
    # LightGBM prediction
    if model_lgb is not None:
        pred_lgb = model_lgb.predict(X)
        predictions.append(('lgb', pred_lgb, weights.get('lgb', 0.3)))
    
    # Ensemble
    if len(predictions) == 2:
        final_pred = (predictions[0][1] * predictions[0][2] + 
                     predictions[1][1] * predictions[1][2])
    elif len(predictions) == 1:
        final_pred = predictions[0][1]
    else:
        raise ValueError("No models available for prediction")
    
    return final_pred


if __name__ == "__main__":
    # Example usage
    print("\n" + "="*70)
    print("Flight Delay Prediction")
    print("="*70)
    
    # Sample data
    sample_data = pd.DataFrame({
        'Date': ['2019-06-15'],
        'DepTime': [1400],
        'Distance': [500],
        'CRSElapsedTime': [90],
        'TaxiIn': [5],
        'TaxiOut': [10],
        'UniqueCarrier': ['WN'],
        'Origin': ['LAX'],
        'Dest': ['SFO'],
        'temp': [75],
        'dewp': [60],
        'slp': [1015],
        'visib': [10],
        'wdsp': [8]
    })
    
    try:
        predictions = predict_delay(sample_data)
        print(f"\nPredicted delay: {predictions[0]:.2f} minutes")
    except Exception as e:
        print(f"\nError: {e}")
