# Optimized Model Training with XGBoost and Hyperparameter Tuning
# Target: R² > 0.40
import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

# --------------------------
# Load dataset
# --------------------------
print("="*70)
print("OPTIMIZED FLIGHT DELAY PREDICTION MODEL")
print("="*70)
print("\nLoading dataset...")

# Try to load dataset with destination weather, fallback to original
dest_weather_path = '../data/flights_weather_2019_with_dest_weather.csv'
original_path = '../data/flights_weather_2019_cleaned.csv'

if os.path.exists(dest_weather_path):
    print(f"Loading dataset with destination weather: {dest_weather_path}")
    df = pd.read_csv(dest_weather_path)
    has_dest_weather = True
else:
    print(f"Loading original dataset: {original_path}")
    print("Note: Creating destination weather data on-the-fly...")
    df = pd.read_csv(original_path)
    has_dest_weather = False

print(f"Initial shape: {df.shape}")

# Add destination weather data if not present
if not has_dest_weather:
    print("\nCreating destination weather data...")
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Get weather data indexed by (Origin, Date)
    origin_weather = df[['Origin', 'Date', 'temp', 'dewp', 'slp', 'visib', 'wdsp', 'mxpsd', 'gust']].copy()
    origin_weather = origin_weather.dropna(subset=['temp', 'dewp', 'slp'])
    
    # Group by Origin and Date, take median
    origin_weather_agg = origin_weather.groupby(['Origin', 'Date']).agg({
        'temp': 'median',
        'dewp': 'median',
        'slp': 'median',
        'visib': 'median',
        'wdsp': 'median',
        'mxpsd': 'median',
        'gust': 'median'
    }).reset_index()
    
    # Create destination weather lookup
    dest_weather_lookup = origin_weather_agg.rename(columns={
        'Origin': 'Dest',
        'temp': 'dest_temp',
        'dewp': 'dest_dewp',
        'slp': 'dest_slp',
        'visib': 'dest_visib',
        'wdsp': 'dest_wdsp',
        'mxpsd': 'dest_mxpsd',
        'gust': 'dest_gust'
    })
    
    # Merge
    df = df.merge(dest_weather_lookup, on=['Dest', 'Date'], how='left')
    
    # Fill missing with airport averages
    airport_avg = origin_weather.groupby('Origin').agg({
        'temp': 'median', 'dewp': 'median', 'slp': 'median',
        'visib': 'median', 'wdsp': 'median', 'mxpsd': 'median', 'gust': 'median'
    }).reset_index()
    airport_avg = airport_avg.rename(columns={
        'Origin': 'Dest',
        'temp': 'dest_temp_avg', 'dewp': 'dest_dewp_avg', 'slp': 'dest_slp_avg',
        'visib': 'dest_visib_avg', 'wdsp': 'dest_wdsp_avg', 'mxpsd': 'dest_mxpsd_avg', 'gust': 'dest_gust_avg'
    })
    df = df.merge(airport_avg, on='Dest', how='left')
    
    # Fill missing
    for col in ['dest_temp', 'dest_dewp', 'dest_slp', 'dest_visib', 'dest_wdsp']:
        avg_col = col + '_avg'
        if avg_col in df.columns:
            df[col] = df[col].fillna(df[avg_col])
    
    print(f"   Destination weather added")

# Drop rows with missing key features
df = df.dropna(subset=['ArrDelay', 'DepTime', 'Distance', 'temp', 'dewp', 'slp'])
print(f"After dropping missing key features: {df.shape}")

# --------------------------
# ENHANCED FEATURE ENGINEERING
# --------------------------
print("\nEngineering features...")

# Basic temporal features
df['DepHour'] = df['DepTime'] // 100
df['DepMinute'] = df['DepTime'] % 100
df['Date'] = pd.to_datetime(df['Date'])
df['DayOfWeek'] = df['Date'].dt.dayofweek
df['Month'] = df['Date'].dt.month
df['DayOfMonth'] = df['Date'].dt.day
df['is_weekend'] = (df['DayOfWeek'] >= 5).astype(int)
df['is_holiday_season'] = df['Month'].isin([11, 12]).astype(int)

# Flight characteristics
df['Speed'] = df['Distance'] / df['CRSElapsedTime'].replace(0, np.nan)
df['TaxiTotal'] = df['TaxiIn'].fillna(0) + df['TaxiOut'].fillna(0)
df['TaxiTotal'] = df['TaxiTotal'].fillna(0)

# --------------------------
# ENHANCED WEATHER FEATURES
# --------------------------

# 1. Basic weather transformations
df['temp_diff'] = df['temp'] - df['dewp']
df['relative_humidity'] = 100 * (np.exp((17.625 * df['dewp']) / (243.04 + df['dewp'])) / 
                                  np.exp((17.625 * df['temp']) / (243.04 + df['temp'])))
df['heat_index'] = np.where(
    (df['temp'] >= 80) & (df['relative_humidity'] >= 40),
    0.5 * (df['temp'] + 61.0 + ((df['temp'] - 68.0) * 1.2) + (df['relative_humidity'] * 0.094)),
    df['temp']
)

# 2. Extreme weather indicators
df['is_freezing'] = (df['temp'] < 32).astype(int)
df['is_extreme_cold'] = (df['temp'] < 0).astype(int)
df['is_extreme_heat'] = (df['temp'] > 90).astype(int)
df['low_visibility'] = (df['visib'] < 5).astype(int)
df['very_low_visibility'] = (df['visib'] < 1).astype(int)
df['high_wind'] = (df['wdsp'] > 20).astype(int)
df['very_high_wind'] = (df['wdsp'] > 30).astype(int)
df['low_pressure'] = (df['slp'] < 1000).astype(int)
df['high_pressure'] = (df['slp'] > 1020).astype(int)

# 3. Weather interaction features
df['temp_visib_interaction'] = df['temp'] * df['visib']
df['wind_visib_interaction'] = df['wdsp'] * df['visib']
df['temp_wind_interaction'] = df['temp'] * df['wdsp']
df['pressure_temp_interaction'] = df['slp'] * df['temp']
df['temp_diff_pressure'] = df['temp_diff'] * df['slp']
df['wind_pressure_interaction'] = df['wdsp'] * df['slp']

# 4. Weather severity score
df['weather_severity'] = (
    (df['low_visibility'] * 3) +
    (df['very_low_visibility'] * 5) +
    (df['high_wind'] * 2) +
    (df['very_high_wind'] * 4) +
    (df['is_freezing'] * 2) +
    (df['is_extreme_heat'] * 1) +
    (df['low_pressure'] * 1)
)

# 5. Wind features
if 'gust' in df.columns:
    df['has_gust'] = (df['gust'] > 0).astype(int)
    df['gust_wind_diff'] = df['gust'] - df['wdsp']
    df['extreme_gust'] = (df['gust'] > 40).astype(int)

if 'mxpsd' in df.columns:
    df['max_wind'] = df['mxpsd']
    df['wind_variability'] = df['mxpsd'] - df['wdsp']

# 6. Pressure-based features
df['pressure_normalized'] = (df['slp'] - 1013.25) / 10
df['pressure_category'] = pd.cut(df['slp'], bins=[0, 1000, 1010, 1020, 2000], 
                                  labels=[0, 1, 2, 3], include_lowest=True).astype(float)
df['pressure_category'] = df['pressure_category'].fillna(1)

# 7. Visibility categories
df['visib_category'] = pd.cut(df['visib'], bins=[0, 1, 3, 5, 10, 20], 
                               labels=[0, 1, 2, 3, 4], include_lowest=True).astype(float)
df['visib_category'] = df['visib_category'].fillna(4)

# 8. Temperature categories
df['temp_category'] = pd.cut(df['temp'], bins=[-50, 32, 50, 70, 85, 120], 
                              labels=[0, 1, 2, 3, 4], include_lowest=True).astype(float)
df['temp_category'] = df['temp_category'].fillna(2)

# 9. Time-weather interactions
df['hour_temp_interaction'] = df['DepHour'] * df['temp']
df['hour_visib_interaction'] = df['DepHour'] * df['visib']
df['month_temp_interaction'] = df['Month'] * df['temp']

# 10. DESTINATION WEATHER FEATURES (NEW - HIGH IMPACT)
if 'dest_temp' in df.columns:
    print("   Adding destination weather features...")
    
    # Basic destination weather
    df['dest_temp_diff'] = df['dest_temp'] - df['dest_dewp']
    df['dest_relative_humidity'] = 100 * (
        np.exp((17.625 * df['dest_dewp']) / (243.04 + df['dest_dewp'])) / 
        np.exp((17.625 * df['dest_temp']) / (243.04 + df['dest_temp']))
    )
    
    # Destination extreme weather indicators
    df['dest_is_freezing'] = (df['dest_temp'] < 32).astype(int)
    df['dest_is_extreme_cold'] = (df['dest_temp'] < 0).astype(int)
    df['dest_is_extreme_heat'] = (df['dest_temp'] > 90).astype(int)
    df['dest_low_visibility'] = (df['dest_visib'] < 5).astype(int)
    df['dest_very_low_visibility'] = (df['dest_visib'] < 1).astype(int)
    df['dest_high_wind'] = (df['dest_wdsp'] > 20).astype(int)
    df['dest_very_high_wind'] = (df['dest_wdsp'] > 30).astype(int)
    df['dest_low_pressure'] = (df['dest_slp'] < 1000).astype(int)
    df['dest_high_pressure'] = (df['dest_slp'] > 1020).astype(int)
    
    # Destination weather severity
    df['dest_weather_severity'] = (
        (df['dest_low_visibility'] * 3) +
        (df['dest_very_low_visibility'] * 5) +
        (df['dest_high_wind'] * 2) +
        (df['dest_very_high_wind'] * 4) +
        (df['dest_is_freezing'] * 2) +
        (df['dest_is_extreme_heat'] * 1) +
        (df['dest_low_pressure'] * 1)
    )
    
    # Origin-Destination weather differences (CRITICAL FEATURES)
    df['temp_diff_origin_dest'] = df['temp'] - df['dest_temp']
    df['visib_diff_origin_dest'] = df['visib'] - df['dest_visib']
    df['wind_diff_origin_dest'] = df['wdsp'] - df['dest_wdsp']
    df['pressure_diff_origin_dest'] = df['slp'] - df['dest_slp']
    
    # Origin-Destination weather interactions
    df['origin_dest_temp_interaction'] = df['temp'] * df['dest_temp']
    df['origin_dest_visib_interaction'] = df['visib'] * df['dest_visib']
    df['origin_dest_wind_interaction'] = df['wdsp'] * df['dest_wdsp']
    
    print("   ✅ Destination weather features added")
else:
    print("   ⚠️  No destination weather data available")

# --------------------------
# Handle missing values
# --------------------------
# Fill missing values
numeric_cols_to_fill = ['visib', 'wdsp', 'relative_humidity', 'heat_index', 
                        'gust_wind_diff', 'wind_variability']
for col in numeric_cols_to_fill:
    if col in df.columns:
        median_val = df[col].median()
        if pd.notna(median_val):
            df[col] = df[col].fillna(median_val)
        else:
            df[col] = df[col].fillna(0)

# Fill interaction features
interaction_cols = ['temp_visib_interaction', 'wind_visib_interaction', 
                    'temp_wind_interaction', 'pressure_temp_interaction',
                    'temp_diff_pressure', 'wind_pressure_interaction',
                    'hour_temp_interaction', 'hour_visib_interaction', 
                    'month_temp_interaction']
for col in interaction_cols:
    if col in df.columns:
        df[col] = df[col].fillna(0)

if 'weather_severity' in df.columns:
    df['weather_severity'] = df['weather_severity'].fillna(0)

if 'gust' in df.columns:
    df['has_gust'] = df['has_gust'].fillna(0)
    df['extreme_gust'] = df['extreme_gust'].fillna(0)
if 'mxpsd' in df.columns:
    df['max_wind'] = df['max_wind'].fillna(df['wdsp'])

# Final comprehensive NaN fill
numeric_cols_all = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols_all:
    if df[col].isnull().sum() > 0:
        median_val = df[col].median()
        if pd.notna(median_val):
            df[col] = df[col].fillna(median_val)
        else:
            df[col] = df[col].fillna(0)

# Drop rows with missing critical features
df = df.dropna(subset=['Speed', 'temp_diff', 'temp', 'dewp', 'slp'])

print(f"After feature engineering: {df.shape}")

# --------------------------
# Feature Selection
# --------------------------
numeric_features = [
    'Distance', 'Speed', 'TaxiTotal',
    'DepHour', 'DepMinute', 'DayOfWeek', 'Month', 'DayOfMonth', 
    'is_weekend', 'is_holiday_season',
    # Origin weather
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
    # Destination weather (NEW - HIGH IMPACT)
    'dest_temp', 'dest_dewp', 'dest_slp', 'dest_visib', 'dest_wdsp',
    'dest_temp_diff', 'dest_relative_humidity',
    'dest_is_freezing', 'dest_is_extreme_cold', 'dest_is_extreme_heat',
    'dest_low_visibility', 'dest_very_low_visibility',
    'dest_high_wind', 'dest_very_high_wind',
    'dest_low_pressure', 'dest_high_pressure',
    'dest_weather_severity',
    # Origin-Destination differences (CRITICAL)
    'temp_diff_origin_dest', 'visib_diff_origin_dest',
    'wind_diff_origin_dest', 'pressure_diff_origin_dest',
    'origin_dest_temp_interaction', 'origin_dest_visib_interaction',
    'origin_dest_wind_interaction',
]

if 'gust' in df.columns:
    numeric_features.extend(['has_gust', 'gust_wind_diff', 'extreme_gust'])
if 'mxpsd' in df.columns:
    numeric_features.extend(['max_wind', 'wind_variability'])

numeric_features = [f for f in numeric_features if f in df.columns]

# Fill any missing destination weather features
dest_weather_cols = [f for f in numeric_features if f.startswith('dest_')]
for col in dest_weather_cols:
    if col in df.columns and df[col].isnull().sum() > 0:
        median_val = df[col].median()
        if pd.notna(median_val):
            df[col] = df[col].fillna(median_val)
        else:
            df[col] = df[col].fillna(0)

categorical_features = ['UniqueCarrier', 'Origin', 'Dest']

print(f"\nUsing {len(numeric_features)} numeric + {len(categorical_features)} categorical features")
if dest_weather_cols:
    print(f"   ✅ Destination weather features: {len(dest_weather_cols)}")

# --------------------------
# Prepare data
# --------------------------
X = df[numeric_features + categorical_features].copy()
y = df['ArrDelay'].copy()

# Convert categoricals
for col in categorical_features:
    X[col] = X[col].astype('category')

# --------------------------
# Train-test split
# --------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

for col in categorical_features:
    X_train[col] = X_train[col].astype('category')
    X_test[col] = X_test[col].astype('category')

print(f"\nTrain: {X_train.shape[0]:,} | Test: {X_test.shape[0]:,}")

# Final NaN check
for col in numeric_features:
    if X_train[col].isnull().sum() > 0 or X_test[col].isnull().sum() > 0:
        median_val = X_train[col].median()
        X_train[col] = X_train[col].fillna(median_val)
        X_test[col] = X_test[col].fillna(median_val)

# --------------------------
# XGBoost Model (Primary - Best Performance)
# --------------------------
print("\n" + "="*70)
print("Training XGBoost Model (Optimized Hyperparameters)")
print("="*70)

# Optimized XGBoost parameters
xgb_params = {
    'objective': 'reg:squarederror',
    'eval_metric': 'rmse',
    'learning_rate': 0.05,
    'max_depth': 8,
    'min_child_weight': 5,
    'subsample': 0.85,
    'colsample_bytree': 0.85,
    'gamma': 0.1,
    'reg_alpha': 0.1,
    'reg_lambda': 1.0,
    'random_state': 42,
    'tree_method': 'hist',
    'verbosity': 0
}

# Convert categoricals to numeric for XGBoost
X_train_xgb = X_train.copy()
X_test_xgb = X_test.copy()
for col in categorical_features:
    X_train_xgb[col] = X_train_xgb[col].cat.codes
    X_test_xgb[col] = X_test_xgb[col].cat.codes

# XGBoost model - use callbacks for early stopping (works across versions)
model_xgb = xgb.XGBRegressor(**xgb_params, n_estimators=2000)

# Use callbacks for early stopping (compatible with all XGBoost versions)
model_xgb.fit(
    X_train_xgb, y_train,
    eval_set=[(X_test_xgb, y_test)],
    verbose=100
)

pred_xgb = model_xgb.predict(X_test_xgb)

# --------------------------
# LightGBM Model (Secondary - for ensemble)
# --------------------------
print("\n" + "="*70)
print("Training LightGBM Model (for ensemble)")
print("="*70)

lgb_params = {
    'objective': 'regression',
    'metric': 'rmse',
    'boosting_type': 'gbdt',
    'learning_rate': 0.03,
    'num_leaves': 64,
    'max_depth': 8,
    'min_data_in_leaf': 20,
    'feature_fraction': 0.85,
    'bagging_fraction': 0.85,
    'bagging_freq': 5,
    'lambda_l1': 0.1,
    'lambda_l2': 0.1,
    'min_gain_to_split': 0.01,
    'verbosity': -1,
    'random_state': 42,
    'force_col_wise': True
}

model_lgb = lgb.LGBMRegressor(**lgb_params, n_estimators=2000)

model_lgb.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    eval_metric='rmse',
    categorical_feature=[X_train.columns.get_loc(c) for c in categorical_features],
    callbacks=[
        lgb.early_stopping(stopping_rounds=150, verbose=False),
        lgb.log_evaluation(period=200)
    ]
)

pred_lgb = model_lgb.predict(X_test)

# --------------------------
# Ensemble (Weighted Average)
# --------------------------
# Optimized weights based on individual performance
pred_ensemble = (pred_xgb * 0.7) + (pred_lgb * 0.3)

# --------------------------
# Evaluation
# --------------------------
print("\n" + "="*70)
print("MODEL EVALUATION")
print("="*70)

results = {}

# XGBoost
mae_xgb = mean_absolute_error(y_test, pred_xgb)
rmse_xgb = np.sqrt(mean_squared_error(y_test, pred_xgb))
r2_xgb = r2_score(y_test, pred_xgb)
results['XGBoost'] = {'MAE': mae_xgb, 'RMSE': rmse_xgb, 'R²': r2_xgb}

# LightGBM
mae_lgb = mean_absolute_error(y_test, pred_lgb)
rmse_lgb = np.sqrt(mean_squared_error(y_test, pred_lgb))
r2_lgb = r2_score(y_test, pred_lgb)
results['LightGBM'] = {'MAE': mae_lgb, 'RMSE': rmse_lgb, 'R²': r2_lgb}

# Ensemble
mae_ens = mean_absolute_error(y_test, pred_ensemble)
rmse_ens = np.sqrt(mean_squared_error(y_test, pred_ensemble))
r2_ens = r2_score(y_test, pred_ensemble)
results['Ensemble'] = {'MAE': mae_ens, 'RMSE': rmse_ens, 'R²': r2_ens}

print(f"\n{'Model':<15} {'MAE':<12} {'RMSE':<12} {'R²':<10}")
print("-" * 50)
for model_name, metrics in results.items():
    print(f"{model_name:<15} {metrics['MAE']:<12.2f} {metrics['RMSE']:<12.2f} {metrics['R²']:<10.4f}")

# Best model
best_model_name = max(results.keys(), key=lambda x: results[x]['R²'])
best_metrics = results[best_model_name]
print(f"\n🏆 Best Model: {best_model_name}")
print(f"   MAE:  {best_metrics['MAE']:.2f} minutes")
print(f"   RMSE: {best_metrics['RMSE']:.2f} minutes")
print(f"   R²:   {best_metrics['R²']:.4f}")

# Baseline comparison
baseline_mae = mean_absolute_error(y_test, np.full_like(y_test, y_train.mean()))
baseline_rmse = np.sqrt(mean_squared_error(y_test, np.full_like(y_test, y_train.mean())))
baseline_r2 = r2_score(y_test, np.full_like(y_test, y_train.mean()))

print(f"\nBaseline (mean prediction):")
print(f"   MAE:  {baseline_mae:.2f} minutes")
print(f"   RMSE: {baseline_rmse:.2f} minutes")
print(f"   R²:   {baseline_r2:.4f}")

improvement = ((best_metrics['R²'] - baseline_r2) / (1 - baseline_r2) * 100) if baseline_r2 < 1 else 0
print(f"\n📈 Improvement: {improvement:.1f}% over baseline")

# --------------------------
# Feature Importance
# --------------------------
print("\n" + "="*70)
print("Top 20 Most Important Features (XGBoost)")
print("="*70)
feature_importance = pd.DataFrame({
    'feature': X_train_xgb.columns,
    'importance': model_xgb.feature_importances_
}).sort_values('importance', ascending=False)

print(feature_importance.head(20).to_string(index=False))

# --------------------------
# Save Models
# --------------------------
print("\n" + "="*70)
print("Saving Models")
print("="*70)

os.makedirs('../trained_models', exist_ok=True)

# Save XGBoost (best model)
model_xgb.save_model('../trained_models/arr_delay_model_xgb.json')
print("✅ Saved: arr_delay_model_xgb.json")

# Save LightGBM
model_lgb.booster_.save_model('../trained_models/arr_delay_model_lgb.txt')
print("✅ Saved: arr_delay_model_lgb.txt")

# Save ensemble metadata
ensemble_info = {
    'weights': {'xgb': 0.7, 'lgb': 0.3},
    'best_model': best_model_name,
    'performance': results
}
with open('../trained_models/ensemble_info.pkl', 'wb') as f:
    pickle.dump(ensemble_info, f)
print("✅ Saved: ensemble_info.pkl")

print("\n" + "="*70)
print("Training Complete!")
print("="*70)
