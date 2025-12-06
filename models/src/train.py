# Model evaluation:
# MAE:  30.09
# RMSE: 46.96
# R²:   0.309
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

# --------------------------
# Load dataset
# --------------------------
df = pd.read_csv('../data/flights_weather_2019_cleaned.csv')

# Drop rows with missing key features
df = df.dropna(subset=['ArrDelay', 'DepTime', 'Distance', 'temp', 'dewp', 'slp'])

# --------------------------
# Feature engineering (simple + high-signal only)
# --------------------------
df['DepHour'] = df['DepTime'] // 100
df['DayOfWeek'] = pd.to_datetime(df['Date']).dt.dayofweek
df['Month'] = pd.to_datetime(df['Date']).dt.month
df['is_weekend'] = (df['DayOfWeek'] >= 5).astype(int)
df['temp_diff'] = df['temp'] - df['dewp']
df['Speed'] = df['Distance'] / df['CRSElapsedTime'].replace(0, np.nan)
df = df.dropna(subset=['Speed'])

# --------------------------
# Features and target
# --------------------------
numeric_features = [
    'Distance', 'temp', 'dewp', 'slp', 'DepHour', 'DayOfWeek',
    'Month', 'is_weekend', 'temp_diff', 'Speed', 'visib', 'wdsp'
]

categorical_features = ['UniqueCarrier', 'Origin', 'Dest']

X = df[numeric_features + categorical_features]
y = df['ArrDelay']

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

# --------------------------
# LightGBM Model
# --------------------------
lgb_params = {
    'objective': 'regression',
    'metric': 'rmse',
    'boosting_type': 'gbdt',
    'learning_rate': 0.05,
    'num_leaves': 128,
    'max_depth': -1,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbosity': -1,
    'random_state': 42
}

model_lgb = lgb.LGBMRegressor(**lgb_params, n_estimators=1200)

model_lgb.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    eval_metric='rmse',
    categorical_feature=[X_train.columns.get_loc(c) for c in categorical_features],
    callbacks=[lgb.early_stopping(100), lgb.log_evaluation(200)]
)

# --------------------------
# Random Forest (2nd model for ensemble)
# --------------------------
model_rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=20,
    min_samples_split=5,
    n_jobs=-1,
    random_state=42
)

model_rf.fit(X_train[numeric_features], y_train)

import pickle
with open('../trained_models/arr_delay_model_rf.pkl', 'wb') as f:
    pickle.dump(model_rf, f)

# --------------------------
# Predictions
# --------------------------
pred_lgb = model_lgb.predict(X_test)
pred_rf = model_rf.predict(X_test[numeric_features])

# Ensemble average
y_pred = (pred_lgb * 0.7) + (pred_rf * 0.3)

# --------------------------
# Evaluation
# --------------------------
print("Model evaluation:")
print("MAE: ", round(mean_absolute_error(y_test, y_pred), 2))
print("RMSE:", round(np.sqrt(mean_squared_error(y_test, y_pred)), 2))
print("R²:  ", round(r2_score(y_test, y_pred), 3))

# --------------------------
# Save LGBM model
# --------------------------
model_lgb.booster_.save_model('../trained_models/arr_delay_model_lgbm_ensemble.txt')
