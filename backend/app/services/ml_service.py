"""
Machine Learning Service
ML model training and prediction services
"""
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd

from app.services.cargo_capacity_predictor import CargoCapacityPredictor
from app.services.baggage_predictor import BaggagePredictor


class MLService:
    """Service for machine learning operations"""
    
    def __init__(self):
        """Initialize ML service"""
        # Initialize cargo capacity predictor
        self.baggage_predictor = BaggagePredictor()
        self.cargo_capacity_predictor = CargoCapacityPredictor(self.baggage_predictor)
        
        # Initialize ML delay predictor
        from app.services.ml_delay_predictor import MLDelayPredictor
        self.ml_delay_predictor = MLDelayPredictor()
        
        # Other models (to be implemented)
        self.cargo_model = None
        self.passenger_traffic_model = None
    
    def predict_flight_delay(
        self,
        weather_data: Dict[str, Any],
        flight_route: Dict[str, Any],
        airport_traffic: Dict[str, Any],
        aircraft_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict flight delay based on various factors
        
        Uses ML model if available, otherwise falls back to rule-based.
        
        Args:
            weather_data: Weather conditions data
            flight_route: Flight route information
            airport_traffic: Airport traffic data
            aircraft_data: Aircraft information
            
        Returns:
            Prediction results with delay probability and estimated delay time
        """
        # Try ML prediction first
        if self.ml_delay_predictor.is_available():
            try:
                # Convert weather data format
                departure_weather = {
                    'temperature_celsius': weather_data.get('temperature_celsius'),
                    'dewpoint_celsius': weather_data.get('dewpoint_celsius'),
                    'visibility_miles': weather_data.get('visibility_km', 0) * 0.621371 if weather_data.get('visibility_km') else weather_data.get('visibility_miles'),
                    'wind_speed_knots': weather_data.get('wind_speed_kmh', 0) * 0.539957 if weather_data.get('wind_speed_kmh') else weather_data.get('wind_speed_knots'),
                    'pressure_mb': weather_data.get('pressure_hpa'),
                }
                
                flight_data = {
                    'scheduled_departure': flight_route.get('scheduled_departure'),
                    'origin_airport': flight_route.get('origin', 'KJFK'),
                    'destination_airport': flight_route.get('destination', 'KLAX'),
                    'airline_code': flight_route.get('airline_code', 'AA'),
                    'distance_km': flight_route.get('distance_km', 1000),
                    'elapsed_time_minutes': flight_route.get('elapsed_time_minutes', 120),
                    'taxi_in_minutes': 5,
                    'taxi_out_minutes': 10,
                }
                
                ml_result = self.ml_delay_predictor.predict(flight_data, departure_weather)
                
                # Convert to expected format
                estimated_delay = ml_result.get('predicted_delay_minutes', 0)
                confidence = ml_result.get('confidence_score', 0.7)
                delay_probability = min(0.95, estimated_delay / 120.0) if estimated_delay > 0 else 0.0
                
                return {
                    "delay_probability": round(delay_probability, 2),
                    "estimated_delay_minutes": int(estimated_delay),
                    "confidence": round(confidence, 2),
                    "factors": {
                        "weather_impact": True,
                        "traffic_impact": airport_traffic is not None,
                        "route_impact": flight_route.get('distance_km', 0) > 0,
                        "model_type": "ml_ensemble"
                    }
                }
            except Exception as e:
                print(f"ML prediction failed, using fallback: {e}")
        
        # Fallback to rule-based prediction
        delay_probability = 0.0
        estimated_delay = 0
        confidence = 0.5
        
        # Weather impact
        if weather_data:
            visibility = weather_data.get('visibility_km', 10)
            wind_speed = weather_data.get('wind_speed_kmh', 0)
            precipitation = weather_data.get('precipitation_mm', 0)
            
            if visibility < 1.0:
                delay_probability += 0.4
                estimated_delay += 30
            elif visibility < 3.0:
                delay_probability += 0.2
                estimated_delay += 15
            
            if wind_speed > 50:
                delay_probability += 0.3
                estimated_delay += 20
            
            if precipitation > 5.0:
                delay_probability += 0.25
                estimated_delay += 15
        
        # Airport traffic impact
        if airport_traffic:
            traffic_level = airport_traffic.get('traffic_level', 'normal')
            if traffic_level == 'high':
                delay_probability += 0.2
                estimated_delay += 10
            elif traffic_level == 'very_high':
                delay_probability += 0.35
                estimated_delay += 25
        
        # Route distance impact (longer routes more susceptible)
        distance_km = flight_route.get('distance_km', 0)
        if distance_km > 5000:
            delay_probability += 0.1
        
        # Cap probability at 0.95
        delay_probability = min(delay_probability, 0.95)
        
        # Adjust confidence based on data availability
        if weather_data and airport_traffic:
            confidence = 0.75
        elif weather_data or airport_traffic:
            confidence = 0.6
        else:
            confidence = 0.4
        
        return {
            "delay_probability": round(delay_probability, 2),
            "estimated_delay_minutes": int(estimated_delay),
            "confidence": round(confidence, 2),
            "factors": {
                "weather_impact": weather_data is not None,
                "traffic_impact": airport_traffic is not None,
                "route_impact": distance_km > 0
            }
        }
    
    def predict_cargo_demand(
        self,
        aircraft_data: Dict[str, Any],
        airport_traffic: Dict[str, Any],
        route_info: Optional[Dict[str, Any]] = None,
        historical_avg: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Predict cargo demand based on aircraft and traffic data
        
        Args:
            aircraft_data: Aircraft information (capacity, type)
            airport_traffic: Airport traffic data
            route_info: Optional route information (origin, destination)
            historical_avg: Optional historical average cargo demand
            
        Returns:
            Cargo demand prediction
        """
        # Base prediction from aircraft capacity
        max_cargo_weight = aircraft_data.get('max_cargo_weight_kg', 20000)
        max_cargo_volume = aircraft_data.get('max_cargo_volume_m3', 40.0)
        
        # Start with historical average if available
        if historical_avg:
            predicted_weight = historical_avg
            confidence = 0.7
        else:
            # Estimate based on aircraft capacity (typical utilization 60-80%)
            utilization_rate = 0.7
            predicted_weight = max_cargo_weight * utilization_rate
            confidence = 0.5
        
        # Adjust based on airport traffic
        if airport_traffic:
            traffic_level = airport_traffic.get('traffic_level', 'normal')
            if traffic_level == 'high':
                predicted_weight *= 1.15
                confidence += 0.1
            elif traffic_level == 'very_high':
                predicted_weight *= 1.25
                confidence += 0.15
            elif traffic_level == 'low':
                predicted_weight *= 0.85
                confidence += 0.05
        
        # Route-specific adjustments (can be enhanced with route data)
        if route_info:
            # Some routes have higher cargo demand
            origin = route_info.get('origin', '')
            destination = route_info.get('destination', '')
            # Example: Major cargo routes
            major_cargo_routes = ['KUL', 'SIN', 'HKG', 'PVG', 'NRT']
            if origin in major_cargo_routes or destination in major_cargo_routes:
                predicted_weight *= 1.1
                confidence += 0.05
        
        # Calculate volume (assuming average density)
        avg_density_kg_per_m3 = 500  # Typical cargo density
        predicted_volume = predicted_weight / avg_density_kg_per_m3
        
        # Cap at max capacity
        predicted_weight = min(predicted_weight, max_cargo_weight * 0.95)
        predicted_volume = min(predicted_volume, max_cargo_volume * 0.95)
        
        confidence = min(confidence, 0.9)
        
        return {
            "predicted_cargo_weight_kg": round(predicted_weight, 2),
            "predicted_cargo_volume_m3": round(predicted_volume, 2),
            "confidence": round(confidence, 2),
            "utilization_percentage": round((predicted_weight / max_cargo_weight) * 100, 2)
        }
    
    def predict_passenger_traffic(
        self,
        airport_data: Dict[str, Any],
        historical_data: Dict[str, Any],
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Predict passenger traffic at airports
        
        Args:
            airport_data: Current airport information (capacity, current load)
            historical_data: Historical traffic patterns (avg, std, seasonal factors)
            date: Optional date for prediction
            
        Returns:
            Passenger traffic prediction
        """
        # Base prediction from historical average
        historical_avg = historical_data.get('average_passengers', 0)
        historical_std = historical_data.get('std_passengers', 0)
        
        predicted_passengers = historical_avg
        confidence = 0.6
        
        # Seasonal adjustments
        if date:
            month = date.month
            # Peak months (holiday seasons)
            if month in [12, 1, 7, 8]:  # December, January, July, August
                seasonal_factor = 1.2
                predicted_passengers = int(historical_avg * seasonal_factor)
                confidence += 0.1
            elif month in [2, 3, 9, 10]:  # Shoulder months
                seasonal_factor = 0.9
                predicted_passengers = int(historical_avg * seasonal_factor)
            else:
                seasonal_factor = 0.85
                predicted_passengers = int(historical_avg * seasonal_factor)
        
        # Day of week adjustments
        if date:
            day_of_week = date.weekday()  # 0 = Monday
            if day_of_week in [4, 5, 6]:  # Friday, Saturday, Sunday
                predicted_passengers = int(predicted_passengers * 1.15)
            elif day_of_week in [0, 1]:  # Monday, Tuesday
                predicted_passengers = int(predicted_passengers * 0.9)
        
        # Airport capacity constraints
        max_capacity = airport_data.get('passenger_capacity', 0)
        if max_capacity > 0:
            predicted_passengers = min(predicted_passengers, int(max_capacity * 0.95))
        
        # Confidence based on data quality
        if historical_avg > 0 and historical_std > 0:
            # Lower std = higher confidence
            cv = historical_std / historical_avg if historical_avg > 0 else 1.0
            confidence = max(0.5, min(0.9, 0.8 - (cv * 0.3)))
        
        # Add uncertainty range
        uncertainty_range = int(historical_std * 1.96) if historical_std > 0 else int(predicted_passengers * 0.1)
        
        return {
            "predicted_passengers": int(predicted_passengers),
            "confidence": round(confidence, 2),
            "uncertainty_range": uncertainty_range,
            "lower_bound": max(0, int(predicted_passengers - uncertainty_range)),
            "upper_bound": int(predicted_passengers + uncertainty_range),
            "utilization_percentage": round((predicted_passengers / max_capacity * 100), 2) if max_capacity > 0 else 0
        }
    
    async def predict_available_cargo_capacity(
        self,
        aircraft_type: str,
        passenger_count: int,
        origin: str,
        destination: str,
        flight_date: datetime,
        fuel_weight_kg: Optional[float] = None,
        days_before_flight: int = 0,
        aircraft_registration: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict available cargo capacity X days before flight
        
        Args:
            aircraft_type: Aircraft type string (e.g., "Boeing 737-800")
            passenger_count: Number of passengers (from bookings)
            origin: Origin airport IATA code
            destination: Destination airport IATA code
            flight_date: Flight departure datetime
            fuel_weight_kg: Fuel weight in kg (optional, will be estimated if not provided)
            days_before_flight: Days before flight (0 = day of flight)
            
        Returns:
            Dictionary with available capacity predictions including:
            - available_weight_kg: Predicted available cargo weight capacity
            - available_volume_m3: Predicted available cargo volume capacity
            - confidence intervals for both
            - utilization_percentage: Current utilization
            - constraining_factor: "weight" or "volume"
            - overbooking_risk: "low", "medium", or "high"
        """
        return await self.cargo_capacity_predictor.predict_available_capacity(
            aircraft_type=aircraft_type,
            passenger_count=passenger_count,
            origin=origin,
            destination=destination,
            flight_date=flight_date,
            fuel_weight_kg=fuel_weight_kg,
            days_before_flight=days_before_flight,
            aircraft_registration=aircraft_registration
        )
    
    def train_baggage_model(self, flights_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Train baggage prediction models from flight data
        
        Args:
            flights_df: DataFrame with flight data including:
                - flight_date, origin, destination, aircraft_type
                - passenger_count, baggage_weight_kg, baggage_volume_m3
                
        Returns:
            Training metrics dictionary
        """
        return self.baggage_predictor.train(flights_df)

