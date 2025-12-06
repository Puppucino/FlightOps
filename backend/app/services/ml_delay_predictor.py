"""
ML-based Flight Delay Predictor
Uses trained XGBoost + LightGBM ensemble model
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import pickle
from datetime import datetime

# Model directory path
backend_dir = Path(__file__).parent.parent.parent
models_dir = backend_dir.parent / "models"
MODEL_AVAILABLE = True  # Will be set to False if models can't be loaded


class MLDelayPredictor:
    """ML-based delay predictor using trained ensemble model"""
    
    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize ML delay predictor
        
        Args:
            model_dir: Optional path to model directory. If None, uses default location.
        """
        self.model_dir = model_dir or str(models_dir / "trained_models")
        self.model_loaded = False
        self.model_xgb = None
        self.model_lgb = None
        self.weights = {'xgb': 0.7, 'lgb': 0.3}
        
        if MODEL_AVAILABLE:
            self._load_models()
    
    def _load_models(self):
        """Load trained models"""
        try:
            # Load XGBoost model
            xgb_path = os.path.join(self.model_dir, "arr_delay_model_xgb.json")
            if os.path.exists(xgb_path):
                self.model_xgb = xgb.XGBRegressor()
                self.model_xgb.load_model(xgb_path)
                print(f"✅ Loaded XGBoost model from {xgb_path}")
            else:
                print(f"⚠️  XGBoost model not found at {xgb_path}")
            
            # Load LightGBM model
            lgb_path = os.path.join(self.model_dir, "arr_delay_model_lgb.txt")
            if os.path.exists(lgb_path):
                self.model_lgb = lgb.Booster(model_file=lgb_path)
                print(f"✅ Loaded LightGBM model from {lgb_path}")
            else:
                print(f"⚠️  LightGBM model not found at {lgb_path}")
            
            # Load ensemble info
            ensemble_path = os.path.join(self.model_dir, "ensemble_info.pkl")
            if os.path.exists(ensemble_path):
                with open(ensemble_path, 'rb') as f:
                    ensemble_info = pickle.load(f)
                self.weights = ensemble_info.get('weights', {'xgb': 0.7, 'lgb': 0.3})
                print(f"✅ Loaded ensemble weights: {self.weights}")
            
            self.model_loaded = (self.model_xgb is not None or self.model_lgb is not None)
            
        except Exception as e:
            print(f"⚠️  Error loading models: {e}")
            self.model_loaded = False
    
    def is_available(self) -> bool:
        """Check if ML models are available"""
        return self.model_loaded and MODEL_AVAILABLE
    
    def predict(
        self,
        flight_data: Dict[str, Any],
        departure_weather: Dict[str, Any],
        arrival_weather: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict flight delay using ML model
        
        Args:
            flight_data: Flight information (departure time, route, etc.)
            departure_weather: Weather at departure airport
            arrival_weather: Optional weather at arrival airport
            
        Returns:
            Dictionary with prediction results:
            - predicted_delay_minutes: Predicted delay in minutes
            - confidence_score: Confidence (0.0-1.0)
            - model_version: Model identifier
        """
        if not self.is_available():
            return self._fallback_prediction(departure_weather, arrival_weather)
        
        try:
            # Convert app data format to model format
            model_input = self._convert_to_model_format(
                flight_data,
                departure_weather,
                arrival_weather
            )
            
            # Make prediction using internal method
            predictions = self._predict_with_models(model_input)
            predicted_delay = float(predictions[0]) if len(predictions) > 0 else 0.0
            
            # Ensure non-negative
            predicted_delay = max(0.0, predicted_delay)
            
            # Calculate confidence based on prediction magnitude and data quality
            confidence = self._calculate_confidence(
                predicted_delay,
                departure_weather,
                arrival_weather
            )
            
            return {
                "predicted_delay_minutes": int(round(predicted_delay)),
                "confidence_score": confidence,
                "model_version": "xgb_lgb_ensemble_v1",
                "model_type": "ml_ensemble"
            }
            
        except Exception as e:
            print(f"⚠️  ML prediction error: {e}")
            return self._fallback_prediction(departure_weather, arrival_weather)
    
    def _convert_to_model_format(
        self,
        flight_data: Dict[str, Any],
        departure_weather: Dict[str, Any],
        arrival_weather: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Convert app data format to model input format
        
        Model expects:
        - Date, DepTime, Distance, CRSElapsedTime, TaxiIn, TaxiOut
        - UniqueCarrier, Origin, Dest
        - temp, dewp, slp, visib, wdsp (origin weather)
        - dest_temp, dest_dewp, dest_slp, dest_visib, dest_wdsp (destination weather)
        """
        # Extract flight info
        scheduled_departure = flight_data.get('scheduled_departure')
        if isinstance(scheduled_departure, datetime):
            date_str = scheduled_departure.strftime('%Y-%m-%d')
            dep_time = scheduled_departure.hour * 100 + scheduled_departure.minute
        else:
            date_str = flight_data.get('date', datetime.now().strftime('%Y-%m-%d'))
            dep_time = flight_data.get('dep_time', 1200)
        
        # Convert weather units
        # App uses: temperature_celsius, visibility_miles, wind_speed_knots, pressure_mb
        # Model expects: temp (F), visib (miles), wdsp (mph), slp (mb)
        
        def celsius_to_fahrenheit(c: Optional[float]) -> Optional[float]:
            if c is None:
                return None
            return (c * 9/5) + 32
        
        def knots_to_mph(k: Optional[int]) -> Optional[float]:
            if k is None:
                return None
            return k * 1.15078
        
        # Origin weather
        origin_temp = celsius_to_fahrenheit(departure_weather.get('temperature_celsius'))
        origin_dewp = celsius_to_fahrenheit(departure_weather.get('dewpoint_celsius'))
        origin_visib = departure_weather.get('visibility_miles')
        origin_wdsp = knots_to_mph(departure_weather.get('wind_speed_knots'))
        origin_slp = departure_weather.get('pressure_mb')
        
        # Destination weather
        dest_temp = None
        dest_dewp = None
        dest_visib = None
        dest_wdsp = None
        dest_slp = None
        
        if arrival_weather:
            dest_temp = celsius_to_fahrenheit(arrival_weather.get('temperature_celsius'))
            dest_dewp = celsius_to_fahrenheit(arrival_weather.get('dewpoint_celsius'))
            dest_visib = arrival_weather.get('visibility_miles')
            dest_wdsp = knots_to_mph(arrival_weather.get('wind_speed_knots'))
            dest_slp = arrival_weather.get('pressure_mb')
        
        # Build DataFrame
        data = {
            'Date': [date_str],
            'DepTime': [dep_time],
            'Distance': [flight_data.get('distance_km', 0) * 0.621371],  # km to miles
            'CRSElapsedTime': [flight_data.get('elapsed_time_minutes', 90)],
            'TaxiIn': [flight_data.get('taxi_in_minutes', 5)],
            'TaxiOut': [flight_data.get('taxi_out_minutes', 10)],
            'UniqueCarrier': [flight_data.get('airline_code', 'AA')],
            'Origin': [flight_data.get('origin_airport', 'KJFK')],
            'Dest': [flight_data.get('destination_airport', 'KLAX')],
            # Origin weather
            'temp': [origin_temp if origin_temp is not None else 70.0],
            'dewp': [origin_dewp if origin_dewp is not None else 60.0],
            'slp': [origin_slp if origin_slp is not None else 1013.25],
            'visib': [origin_visib if origin_visib is not None else 10.0],
            'wdsp': [origin_wdsp if origin_wdsp is not None else 10.0],
        }
        
        # Add destination weather if available
        if arrival_weather:
            data['dest_temp'] = [dest_temp if dest_temp is not None else origin_temp]
            data['dest_dewp'] = [dest_dewp if dest_dewp is not None else origin_dewp]
            data['dest_slp'] = [dest_slp if dest_slp is not None else origin_slp]
            data['dest_visib'] = [dest_visib if dest_visib is not None else origin_visib]
            data['dest_wdsp'] = [dest_wdsp if dest_wdsp is not None else origin_wdsp]
        
        return pd.DataFrame(data)
    
    def _calculate_confidence(
        self,
        predicted_delay: float,
        departure_weather: Dict[str, Any],
        arrival_weather: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate confidence score for ML prediction
        
        Higher confidence when:
        - Weather data is complete
        - Prediction is very low (no delay) or very high (definite delay)
        - Both origin and destination weather available
        """
        # Base confidence from prediction magnitude
        if predicted_delay < 5:
            base_confidence = 0.85  # High confidence for no delay
        elif predicted_delay < 15:
            base_confidence = 0.75
        elif predicted_delay < 30:
            base_confidence = 0.70
        elif predicted_delay < 60:
            base_confidence = 0.65
        else:
            base_confidence = 0.80  # High confidence for significant delays
        
        # Adjust for data completeness
        weather_completeness = 0.0
        required_fields = ['temperature_celsius', 'visibility_miles', 'wind_speed_knots', 'pressure_mb']
        
        dep_complete = sum(1 for f in required_fields if departure_weather.get(f) is not None) / len(required_fields)
        weather_completeness += dep_complete * 0.6
        
        if arrival_weather:
            arr_complete = sum(1 for f in required_fields if arrival_weather.get(f) is not None) / len(required_fields)
            weather_completeness += arr_complete * 0.4
        else:
            weather_completeness *= 0.8  # Reduce if no arrival weather
        
        # Final confidence
        confidence = base_confidence * (0.7 + weather_completeness * 0.3)
        
        return min(1.0, max(0.5, confidence))
    
    def _fallback_prediction(
        self,
        departure_weather: Dict[str, Any],
        arrival_weather: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fallback rule-based prediction if ML model unavailable"""
        delay = 0
        visibility = departure_weather.get('visibility_miles', 10)
        wind_speed = departure_weather.get('wind_speed_knots', 0)
        
        if visibility and visibility < 1.0:
            delay += 30
        elif visibility and visibility < 3.0:
            delay += 15
        
        if wind_speed and wind_speed > 25:
            delay += 20
        
        return {
            "predicted_delay_minutes": delay,
            "confidence_score": 0.6,
            "model_version": "fallback",
            "model_type": "rule_based"
        }
    
    def _predict_with_models(self, df: pd.DataFrame) -> np.ndarray:
        """
        Make prediction using loaded models
        Replicates logic from models/src/predict.py
        """
        # Prepare features
        df_processed = self._prepare_features(df)
        
        # Feature lists (must match training)
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
        
        # Add destination weather features if available
        dest_features = [
            'dest_temp', 'dest_dewp', 'dest_slp', 'dest_visib', 'dest_wdsp',
            'dest_temp_diff', 'dest_relative_humidity',
            'dest_is_freezing', 'dest_is_extreme_cold', 'dest_is_extreme_heat',
            'dest_low_visibility', 'dest_very_low_visibility',
            'dest_high_wind', 'dest_very_high_wind',
            'dest_low_pressure', 'dest_high_pressure',
            'dest_weather_severity',
            'temp_diff_origin_dest', 'visib_diff_origin_dest',
            'wind_diff_origin_dest', 'pressure_diff_origin_dest',
            'origin_dest_temp_interaction', 'origin_dest_visib_interaction',
            'origin_dest_wind_interaction',
        ]
        
        all_numeric = numeric_features + [f for f in dest_features if f in df_processed.columns]
        categorical_features = ['UniqueCarrier', 'Origin', 'Dest']
        
        # Filter to available features
        available_numeric = [f for f in all_numeric if f in df_processed.columns]
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
                median_val = X[col].median()
                X[col] = X[col].fillna(median_val if pd.notna(median_val) else 0)
        
        predictions = []
        
        # XGBoost prediction
        if self.model_xgb is not None:
            X_xgb = X.copy()
            for col in available_categorical:
                if col in X_xgb.columns:
                    X_xgb[col] = X_xgb[col].cat.codes
            pred_xgb = self.model_xgb.predict(X_xgb)
            predictions.append(('xgb', pred_xgb, self.weights.get('xgb', 0.7)))
        
        # LightGBM prediction
        if self.model_lgb is not None:
            pred_lgb = self.model_lgb.predict(X)
            predictions.append(('lgb', pred_lgb, self.weights.get('lgb', 0.3)))
        
        # Ensemble
        if len(predictions) == 2:
            final_pred = (predictions[0][1] * predictions[0][2] + 
                         predictions[1][1] * predictions[1][2])
        elif len(predictions) == 1:
            final_pred = predictions[0][1]
        else:
            raise ValueError("No models available for prediction")
        
        return final_pred
    
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features matching the training pipeline
        Replicates logic from models/src/predict.py
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
            if 'DepHour' in df.columns:
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
        
        # Destination weather features
        if 'dest_temp' in df.columns and 'dest_dewp' in df.columns:
            df['dest_temp_diff'] = df['dest_temp'] - df['dest_dewp']
            df['dest_relative_humidity'] = 100 * (
                np.exp((17.625 * df['dest_dewp']) / (243.04 + df['dest_dewp'])) / 
                np.exp((17.625 * df['dest_temp']) / (243.04 + df['dest_temp']))
            )
        
        if 'dest_temp' in df.columns:
            df['dest_is_freezing'] = (df['dest_temp'] < 32).astype(int)
            df['dest_is_extreme_cold'] = (df['dest_temp'] < 0).astype(int)
            df['dest_is_extreme_heat'] = (df['dest_temp'] > 90).astype(int)
        
        if 'dest_visib' in df.columns:
            df['dest_low_visibility'] = (df['dest_visib'] < 5).astype(int)
            df['dest_very_low_visibility'] = (df['dest_visib'] < 1).astype(int)
        
        if 'dest_wdsp' in df.columns:
            df['dest_high_wind'] = (df['dest_wdsp'] > 20).astype(int)
            df['dest_very_high_wind'] = (df['dest_wdsp'] > 30).astype(int)
        
        if 'dest_slp' in df.columns:
            df['dest_low_pressure'] = (df['dest_slp'] < 1000).astype(int)
            df['dest_high_pressure'] = (df['dest_slp'] > 1020).astype(int)
        
        # Destination weather severity
        dest_severity_cols = ['dest_low_visibility', 'dest_very_low_visibility', 'dest_high_wind',
                             'dest_very_high_wind', 'dest_is_freezing', 'dest_is_extreme_heat', 'dest_low_pressure']
        if all(col in df.columns for col in dest_severity_cols):
            df['dest_weather_severity'] = (
                (df['dest_low_visibility'] * 3) +
                (df['dest_very_low_visibility'] * 5) +
                (df['dest_high_wind'] * 2) +
                (df['dest_very_high_wind'] * 4) +
                (df['dest_is_freezing'] * 2) +
                (df['dest_is_extreme_heat'] * 1) +
                (df['dest_low_pressure'] * 1)
            )
        
        # Origin-destination differences
        if 'temp' in df.columns and 'dest_temp' in df.columns:
            df['temp_diff_origin_dest'] = df['temp'] - df['dest_temp']
        if 'visib' in df.columns and 'dest_visib' in df.columns:
            df['visib_diff_origin_dest'] = df['visib'] - df['dest_visib']
        if 'wdsp' in df.columns and 'dest_wdsp' in df.columns:
            df['wind_diff_origin_dest'] = df['wdsp'] - df['dest_wdsp']
        if 'slp' in df.columns and 'dest_slp' in df.columns:
            df['pressure_diff_origin_dest'] = df['slp'] - df['dest_slp']
        
        # Origin-destination interactions
        if 'temp' in df.columns and 'dest_temp' in df.columns:
            df['origin_dest_temp_interaction'] = df['temp'] * df['dest_temp']
        if 'visib' in df.columns and 'dest_visib' in df.columns:
            df['origin_dest_visib_interaction'] = df['visib'] * df['dest_visib']
        if 'wdsp' in df.columns and 'dest_wdsp' in df.columns:
            df['origin_dest_wind_interaction'] = df['wdsp'] * df['dest_wdsp']
        
        # Fill missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val if pd.notna(median_val) else 0)
        
        return df
