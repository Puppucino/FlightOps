"""
Baggage Weight/Volume Prediction Service
Predicts passenger baggage weight and volume based on flight context
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import LabelEncoder
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class BaggagePredictor:
    """Predicts baggage weight and volume for flights"""
    
    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = model_dir or Path(__file__).parent.parent.parent / "models"
        self.model_dir.mkdir(exist_ok=True)
        
        self.weight_model: Optional[RandomForestRegressor] = None
        self.volume_model: Optional[RandomForestRegressor] = None
        self.route_encoder = LabelEncoder()
        self.aircraft_encoder = LabelEncoder()
        self.is_trained = False
        
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for baggage prediction"""
        features_df = df.copy()
        
        # Ensure flight_date is datetime
        if 'flight_date' in features_df.columns:
            if not pd.api.types.is_datetime64_any_dtype(features_df['flight_date']):
                features_df['flight_date'] = pd.to_datetime(features_df['flight_date'])
        
        # Temporal features
        if 'flight_date' in features_df.columns:
            features_df['month'] = features_df['flight_date'].dt.month
            features_df['day_of_week'] = features_df['flight_date'].dt.dayofweek
            features_df['day_of_year'] = features_df['flight_date'].dt.dayofyear
            features_df['is_weekend'] = (features_df['day_of_week'] >= 5).astype(int)
            
            # Holiday indicators (simplified - would need proper holiday calendar)
            features_df['is_holiday_season'] = (
                (features_df['month'] == 12) |  # December
                (features_df['month'] == 1) |   # January
                (features_df['month'] == 7)     # July
            ).astype(int)
        
        # Route features
        if 'origin' in features_df.columns and 'destination' in features_df.columns:
            features_df['route'] = features_df['origin'] + '-' + features_df['destination']
        
        # Passenger features
        if 'passenger_count' in features_df.columns:
            features_df['passenger_count'] = pd.to_numeric(features_df['passenger_count'], errors='coerce')
        
        # Aircraft type normalization
        if 'aircraft_type' in features_df.columns:
            # Extract manufacturer and model
            features_df['aircraft_manufacturer'] = features_df['aircraft_type'].str.split().str[0]
            features_df['aircraft_model'] = features_df['aircraft_type'].str.replace('Boeing ', '').str.replace('Airbus ', '')
        
        # Calculate baggage per passenger if we have both
        if 'baggage_weight_kg' in features_df.columns and 'passenger_count' in features_df.columns:
            mask = (features_df['passenger_count'] > 0) & (features_df['baggage_weight_kg'].notna())
            features_df.loc[mask, 'baggage_per_passenger'] = (
                features_df.loc[mask, 'baggage_weight_kg'] / features_df.loc[mask, 'passenger_count']
            )
        
        # Route-level statistics (if training data available)
        if 'route' in features_df.columns:
            if 'baggage_per_passenger' in features_df.columns and features_df['baggage_per_passenger'].notna().any():
                # Calculate from available data
                route_stats = features_df.groupby('route')['baggage_per_passenger'].agg(['mean', 'std']).reset_index()
                route_stats.columns = ['route', 'route_avg_baggage_per_pax', 'route_std_baggage_per_pax']
                features_df = features_df.merge(route_stats, on='route', how='left')
                features_df['route_avg_baggage_per_pax'] = features_df['route_avg_baggage_per_pax'].fillna(15.0)  # Default 15 kg/pax
                features_df['route_std_baggage_per_pax'] = features_df['route_std_baggage_per_pax'].fillna(3.0)
            else:
                # No historical data available, use defaults
                features_df['route_avg_baggage_per_pax'] = 15.0  # Default 15 kg/pax
                features_df['route_std_baggage_per_pax'] = 3.0  # Default 3 kg std
        
        return features_df
    
    def _prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """Prepare features and targets for training"""
        features_df = self._engineer_features(df)
        
        # Select features for model
        feature_cols = [
            'passenger_count',
            'month', 'day_of_week', 'day_of_year', 'is_weekend', 'is_holiday_season',
            'route_avg_baggage_per_pax', 'route_std_baggage_per_pax'
        ]
        
        # Encode categorical features
        if 'route' in features_df.columns:
            features_df['route_encoded'] = self.route_encoder.fit_transform(features_df['route'].fillna('UNKNOWN'))
            feature_cols.append('route_encoded')
        
        if 'aircraft_type' in features_df.columns:
            features_df['aircraft_encoded'] = self.aircraft_encoder.fit_transform(
                features_df['aircraft_type'].fillna('UNKNOWN')
            )
            feature_cols.append('aircraft_encoded')
        
        # Filter to available features
        available_cols = [col for col in feature_cols if col in features_df.columns]
        X = features_df[available_cols].fillna(0)
        
        # Targets
        y_weight = features_df['baggage_weight_kg'] if 'baggage_weight_kg' in features_df.columns else None
        y_volume = features_df['baggage_volume_m3'] if 'baggage_volume_m3' in features_df.columns else None
        
        # If volume not available, estimate from weight (1 kg ≈ 0.015 m³)
        if y_volume is None and y_weight is not None:
            y_volume = y_weight * 0.015
        
        return X, y_weight, y_volume
    
    def train(self, flights_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Train baggage prediction models
        
        Args:
            flights_df: DataFrame with columns: flight_date, origin, destination, 
                       aircraft_type, passenger_count, baggage_weight_kg, baggage_volume_m3
        
        Returns:
            Dictionary with training metrics
        """
        print("Training baggage prediction models...")
        
        # Prepare data
        X, y_weight, y_volume = self._prepare_training_data(flights_df)
        
        # Remove rows with missing targets
        valid_mask = y_weight.notna() & (y_weight > 0)
        X = X[valid_mask]
        y_weight = y_weight[valid_mask]
        y_volume = y_volume[valid_mask] if y_volume is not None else y_weight[valid_mask] * 0.015
        
        if len(X) == 0:
            raise ValueError("No valid training data available")
        
        # Split data (time-series aware)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_weight_train, y_weight_test = y_weight.iloc[:split_idx], y_weight.iloc[split_idx:]
        y_volume_train, y_volume_test = y_volume.iloc[:split_idx], y_volume.iloc[split_idx:]
        
        # Train weight model
        self.weight_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.weight_model.fit(X_train, y_weight_train)
        
        # Train volume model
        self.volume_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.volume_model.fit(X_train, y_volume_train)
        
        # Evaluate
        weight_pred = self.weight_model.predict(X_test)
        volume_pred = self.volume_model.predict(X_test)
        
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        
        weight_mae = mean_absolute_error(y_weight_test, weight_pred)
        weight_rmse = np.sqrt(mean_squared_error(y_weight_test, weight_pred))
        weight_r2 = r2_score(y_weight_test, weight_pred)
        
        volume_mae = mean_absolute_error(y_volume_test, volume_pred)
        volume_rmse = np.sqrt(mean_squared_error(y_volume_test, volume_pred))
        volume_r2 = r2_score(y_volume_test, volume_pred)
        
        self.is_trained = True
        
        # Save models
        self.save_models()
        
        metrics = {
            'weight_model': {
                'mae': float(weight_mae),
                'rmse': float(weight_rmse),
                'r2': float(weight_r2)
            },
            'volume_model': {
                'mae': float(volume_mae),
                'rmse': float(volume_rmse),
                'r2': float(volume_r2)
            },
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        print(f"Training complete!")
        print(f"  Weight Model - R²: {weight_r2:.3f}, MAE: {weight_mae:.2f} kg")
        print(f"  Volume Model - R²: {volume_r2:.3f}, MAE: {volume_mae:.3f} m³")
        
        return metrics
    
    def _get_route_statistics(self, route: str, db_session=None) -> Tuple[float, float]:
        """
        Get route statistics from database if available
        Returns (avg_baggage_per_pax, std_baggage_per_pax)
        """
        if db_session is None:
            # Try to compute from database
            try:
                from app.core.database import SessionLocal
                from app.models.flight import Flight
                from app.models.airport import Airport
                from sqlalchemy import func
                
                db = SessionLocal()
                try:
                    # Get origin and destination IDs
                    origin_code, dest_code = route.split('-')
                    origin_airport = db.query(Airport).filter(Airport.iata_code == origin_code).first()
                    dest_airport = db.query(Airport).filter(Airport.iata_code == dest_code).first()
                    
                    if origin_airport and dest_airport:
                        # Get historical flights on this route
                        flights = db.query(Flight).filter(
                            Flight.origin_airport_id == origin_airport.id,
                            Flight.destination_airport_id == dest_airport.id,
                            Flight.baggage_weight_kg.isnot(None),
                            Flight.passenger_count.isnot(None),
                            Flight.passenger_count > 0
                        ).limit(100).all()
                        
                        if flights:
                            # Calculate statistics
                            baggage_per_pax_values = []
                            for flight in flights:
                                if flight.baggage_weight_kg and flight.passenger_count:
                                    baggage_per_pax_values.append(float(flight.baggage_weight_kg) / float(flight.passenger_count))
                            
                            if baggage_per_pax_values:
                                avg = np.mean(baggage_per_pax_values)
                                std = np.std(baggage_per_pax_values) if len(baggage_per_pax_values) > 1 else 3.0
                                return float(avg), float(std)
                finally:
                    db.close()
            except Exception:
                pass
        
        # Default values
        return 15.0, 3.0
    
    def predict(
        self,
        passenger_count: int,
        origin: str,
        destination: str,
        aircraft_type: str,
        flight_date: datetime,
        days_before_flight: int = 0,
        db_session=None
    ) -> Dict[str, Any]:
        """
        Predict baggage weight and volume
        
        Args:
            passenger_count: Number of passengers
            origin: Origin airport code
            destination: Destination airport code
            aircraft_type: Aircraft type string
            flight_date: Flight departure date
            days_before_flight: Days before flight (for uncertainty adjustment)
        
        Returns:
            Dictionary with predictions and confidence intervals
        """
        if not self.is_trained and self.weight_model is None:
            # Try to load models
            self.load_models()
        
        if not self.is_trained or self.weight_model is None:
            # Return default prediction if no model available
            avg_baggage_per_pax = 15.0  # Default 15 kg per passenger
            return {
                'predicted_baggage_weight_kg': passenger_count * avg_baggage_per_pax,
                'predicted_baggage_volume_m3': passenger_count * avg_baggage_per_pax * 0.015,
                'confidence_interval_95_lower_weight': passenger_count * (avg_baggage_per_pax - 3.0),
                'confidence_interval_95_upper_weight': passenger_count * (avg_baggage_per_pax + 3.0),
                'confidence_interval_95_lower_volume': passenger_count * (avg_baggage_per_pax - 3.0) * 0.015,
                'confidence_interval_95_upper_volume': passenger_count * (avg_baggage_per_pax + 3.0) * 0.015,
                'days_before_flight': days_before_flight,
                'model_used': 'default'
            }
        
        # Prepare features
        route = f"{origin}-{destination}"
        
        # Get route statistics from database
        route_avg, route_std = self._get_route_statistics(route, db_session)
        
        features_df = pd.DataFrame([{
            'passenger_count': passenger_count,
            'origin': origin,
            'destination': destination,
            'route': route,
            'aircraft_type': aircraft_type,
            'flight_date': flight_date
        }])
        
        features_df = self._engineer_features(features_df)
        
        # Ensure route statistics are present (use computed or defaults)
        features_df['route_avg_baggage_per_pax'] = route_avg
        features_df['route_std_baggage_per_pax'] = route_std
        
        # Define base feature columns
        feature_cols = [
            'passenger_count',
            'month', 'day_of_week', 'day_of_year', 'is_weekend', 'is_holiday_season',
            'route_avg_baggage_per_pax', 'route_std_baggage_per_pax'
        ]
        
        if 'route' in features_df.columns and hasattr(self.route_encoder, 'classes_'):
            try:
                if route in self.route_encoder.classes_:
                    features_df['route_encoded'] = self.route_encoder.transform([route])[0]
                else:
                    features_df['route_encoded'] = 0
            except:
                features_df['route_encoded'] = 0
            feature_cols.append('route_encoded')
        
        if 'aircraft_type' in features_df.columns and hasattr(self.aircraft_encoder, 'classes_'):
            try:
                if aircraft_type in self.aircraft_encoder.classes_:
                    features_df['aircraft_encoded'] = self.aircraft_encoder.transform([aircraft_type])[0]
                else:
                    features_df['aircraft_encoded'] = 0
            except:
                features_df['aircraft_encoded'] = 0
            feature_cols.append('aircraft_encoded')
        
        # Ensure all required feature columns are present with proper defaults
        for col in feature_cols:
            if col not in features_df.columns:
                # Add missing columns with default values
                if 'avg' in col or 'mean' in col:
                    features_df[col] = route_avg
                elif 'std' in col:
                    features_df[col] = route_std
                elif col == 'month':
                    features_df[col] = flight_date.month if isinstance(flight_date, datetime) else pd.to_datetime(flight_date).month
                elif col == 'day_of_week':
                    features_df[col] = flight_date.weekday() if isinstance(flight_date, datetime) else pd.to_datetime(flight_date).weekday()
                elif col == 'day_of_year':
                    features_df[col] = flight_date.timetuple().tm_yday if isinstance(flight_date, datetime) else pd.to_datetime(flight_date).timetuple().tm_yday
                elif col == 'is_weekend':
                    dow = flight_date.weekday() if isinstance(flight_date, datetime) else pd.to_datetime(flight_date).weekday()
                    features_df[col] = 1 if dow >= 5 else 0
                elif col == 'is_holiday_season':
                    month = flight_date.month if isinstance(flight_date, datetime) else pd.to_datetime(flight_date).month
                    features_df[col] = 1 if month in [12, 1, 7] else 0
                else:
                    features_df[col] = 0
        
        # Ensure feature order matches training (important for sklearn)
        # Get feature names from the model if available
        if hasattr(self.weight_model, 'feature_names_in_'):
            # Use model's expected feature order
            model_features = list(self.weight_model.feature_names_in_)
            # Create DataFrame with all model features
            X = pd.DataFrame(0, index=features_df.index, columns=model_features)
            # Fill in available values
            for col in model_features:
                if col in features_df.columns:
                    X[col] = features_df[col].values
                elif 'avg' in col:
                    X[col] = route_avg
                elif 'std' in col:
                    X[col] = route_std
        else:
            # Fallback: use feature_cols in order
            available_cols = [col for col in feature_cols if col in features_df.columns]
            X = features_df[available_cols].fillna(0)
        
        # Predict
        weight_pred = self.weight_model.predict(X)[0]
        volume_pred = self.volume_model.predict(X)[0]
        
        # Estimate confidence intervals (simplified - would use proper prediction intervals)
        # Increase uncertainty based on days before flight
        uncertainty_factor = 1.0 + (days_before_flight / 30.0) * 0.3  # Up to 30% more uncertainty
        
        weight_std = max(weight_pred * 0.1, 200) * uncertainty_factor  # At least 200 kg std
        volume_std = weight_std * 0.015
        
        return {
            'predicted_baggage_weight_kg': float(weight_pred),
            'predicted_baggage_volume_m3': float(volume_pred),
            'confidence_interval_95_lower_weight': max(0, float(weight_pred - 1.96 * weight_std)),
            'confidence_interval_95_upper_weight': float(weight_pred + 1.96 * weight_std),
            'confidence_interval_95_lower_volume': max(0, float(volume_pred - 1.96 * volume_std)),
            'confidence_interval_95_upper_volume': float(volume_pred + 1.96 * volume_std),
            'days_before_flight': days_before_flight,
            'model_used': 'ml_model'
        }
    
    def save_models(self):
        """Save trained models to disk"""
        if self.weight_model:
            joblib.dump(self.weight_model, self.model_dir / "baggage_weight_model.joblib")
        if self.volume_model:
            joblib.dump(self.volume_model, self.model_dir / "baggage_volume_model.joblib")
        if hasattr(self.route_encoder, 'classes_'):
            joblib.dump(self.route_encoder, self.model_dir / "route_encoder.joblib")
        if hasattr(self.aircraft_encoder, 'classes_'):
            joblib.dump(self.aircraft_encoder, self.model_dir / "aircraft_encoder.joblib")
    
    def load_models(self):
        """Load trained models from disk"""
        weight_path = self.model_dir / "baggage_weight_model.joblib"
        volume_path = self.model_dir / "baggage_volume_model.joblib"
        
        if weight_path.exists() and volume_path.exists():
            self.weight_model = joblib.load(weight_path)
            self.volume_model = joblib.load(volume_path)
            
            route_enc_path = self.model_dir / "route_encoder.joblib"
            aircraft_enc_path = self.model_dir / "aircraft_encoder.joblib"
            
            if route_enc_path.exists():
                self.route_encoder = joblib.load(route_enc_path)
            if aircraft_enc_path.exists():
                self.aircraft_encoder = joblib.load(aircraft_enc_path)
            
            self.is_trained = True
            return True
        return False
