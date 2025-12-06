"""Delay prediction engine service"""
from typing import Optional
from ..value_objects.weather_observation import WeatherObservation
from ..value_objects.delay_prediction import DelayPrediction
from ..value_objects.prediction_request import PredictionRequest
from .weather_impact_analyzer import WeatherImpactAnalyzer
from ...services.ml_delay_predictor import MLDelayPredictor


class DelayPredictionEngine:
    """Engine for predicting flight delays based on weather conditions"""
    
    def __init__(self, use_ml: bool = True):
        """
        Initialize delay prediction engine
        
        Args:
            use_ml: If True, use ML model when available; otherwise use rule-based
        """
        self.weather_analyzer = WeatherImpactAnalyzer()
        self.ml_predictor = MLDelayPredictor()
        self.use_ml = use_ml and self.ml_predictor.is_available()
    
    def predict_delay(
        self,
        request: PredictionRequest,
        departure_weather: WeatherObservation,
        arrival_weather: Optional[WeatherObservation] = None,
        flight_data: Optional[dict] = None
    ) -> DelayPrediction:
        """
        Predict delay based on weather conditions
        
        Uses ML model if available, otherwise falls back to rule-based prediction.
        
        Args:
            request: Prediction request with flight details
            departure_weather: Weather at departure airport
            arrival_weather: Optional weather at arrival airport
        
        Returns:
            Delay prediction with estimated delay minutes and confidence
        """
        # Try ML prediction first if available
        if self.use_ml:
            try:
                ml_result = self._predict_with_ml(request, departure_weather, arrival_weather, flight_data)
                if ml_result:
                    return ml_result
            except Exception as e:
                # Fall back to rule-based if ML fails
                print(f"ML prediction failed, using rule-based: {e}")
        
        # Fallback to rule-based prediction
        return self._predict_rule_based(request, departure_weather, arrival_weather)
    
    def _predict_with_ml(
        self,
        request: PredictionRequest,
        departure_weather: WeatherObservation,
        arrival_weather: Optional[WeatherObservation] = None,
        flight_data: Optional[dict] = None
    ) -> Optional[DelayPrediction]:
        """Predict delay using ML model"""
        # Convert WeatherObservation to dict format
        departure_weather_dict = self._weather_to_dict(departure_weather)
        arrival_weather_dict = self._weather_to_dict(arrival_weather) if arrival_weather else None
        
        # Prepare flight data (use provided or create default)
        if not flight_data:
            flight_data = {
                'scheduled_departure': request.scheduled_departure,
                'origin_airport': request.departure_airport,
                'destination_airport': request.arrival_airport,
                'airline_code': 'AA',
                'distance_km': 1000,
                'elapsed_time_minutes': 120,
                'taxi_in_minutes': 5,
                'taxi_out_minutes': 10,
            }
        else:
            # Ensure required fields are present
            flight_data.setdefault('scheduled_departure', request.scheduled_departure)
            flight_data.setdefault('origin_airport', request.departure_airport)
            flight_data.setdefault('destination_airport', request.arrival_airport)
        
        # Get ML prediction
        ml_result = self.ml_predictor.predict(
            flight_data,
            departure_weather_dict,
            arrival_weather_dict
        )
        
        # Convert to DelayPrediction
        # Calculate weather impact score from weather conditions
        departure_impact = self.weather_analyzer.analyze(departure_weather)
        weather_impact_score = departure_impact["overall_impact"]
        
        if arrival_weather:
            arrival_impact = self.weather_analyzer.analyze(arrival_weather)
            weather_impact_score = max(weather_impact_score, arrival_impact["overall_impact"])
        
        # Generate reason
        reason = self._generate_reason(departure_impact, arrival_impact if arrival_weather else None)
        
        return DelayPrediction(
            flight_id=request.flight_id,
            predicted_delay_minutes=ml_result["predicted_delay_minutes"],
            confidence_score=ml_result["confidence_score"],
            prediction_timestamp=request.request_timestamp,
            prediction_horizon_minutes=request.prediction_horizon_minutes,
            weather_impact_score=weather_impact_score,
            reason=reason
        )
    
    def _predict_rule_based(
        self,
        request: PredictionRequest,
        departure_weather: WeatherObservation,
        arrival_weather: Optional[WeatherObservation] = None
    ) -> DelayPrediction:
        """Fallback rule-based prediction"""
        # Analyze departure weather impact
        departure_impact = self.weather_analyzer.analyze(departure_weather)
        departure_score = departure_impact["overall_impact"]
        
        # Analyze arrival weather impact if provided
        arrival_score = 0.0
        arrival_impact = None
        if arrival_weather:
            arrival_impact = self.weather_analyzer.analyze(arrival_weather)
            arrival_score = arrival_impact["overall_impact"]
        
        # Use the higher impact (departure or arrival)
        weather_impact_score = max(departure_score, arrival_score)
        
        # Calculate predicted delay based on impact score
        predicted_delay_minutes = self._calculate_delay_minutes(weather_impact_score)
        
        # Calculate confidence based on how severe conditions are
        confidence = self._calculate_confidence(weather_impact_score, departure_weather)
        
        # Generate reason for prediction
        reason = self._generate_reason(departure_impact, arrival_impact)
        
        return DelayPrediction(
            flight_id=request.flight_id,
            predicted_delay_minutes=predicted_delay_minutes,
            confidence_score=confidence,
            prediction_timestamp=request.request_timestamp,
            prediction_horizon_minutes=request.prediction_horizon_minutes,
            weather_impact_score=weather_impact_score,
            reason=reason
        )
    
    def _weather_to_dict(self, weather: WeatherObservation) -> dict:
        """Convert WeatherObservation to dictionary format"""
        return {
            'temperature_celsius': weather.temperature_celsius,
            'dewpoint_celsius': weather.dewpoint_celsius,
            'visibility_miles': weather.visibility_miles,
            'wind_speed_knots': weather.wind_speed_knots,
            'wind_gust_knots': weather.wind_gust_knots,
            'pressure_mb': weather.pressure_mb,
            'ceiling_feet': weather.ceiling_feet,
            'weather_conditions': weather.weather_conditions,
        }
    
    def _calculate_delay_minutes(self, impact_score: float) -> int:
        """
        Calculate delay minutes based on impact score
        
        Impact score 0.0-1.0 maps to delay 0-120 minutes
        """
        if impact_score < 0.2:
            return 0
        elif impact_score < 0.4:
            return int(impact_score * 30)  # 0-12 minutes
        elif impact_score < 0.6:
            return int(15 + (impact_score - 0.4) * 75)  # 15-30 minutes
        elif impact_score < 0.8:
            return int(30 + (impact_score - 0.6) * 150)  # 30-60 minutes
        else:
            return int(60 + (impact_score - 0.8) * 300)  # 60-120 minutes
    
    def _calculate_confidence(
        self,
        impact_score: float,
        weather: WeatherObservation
    ) -> float:
        """
        Calculate confidence score for prediction
        
        Higher confidence when:
        - Impact is very low (no delay) or very high (definite delay)
        - Weather data is complete and recent
        """
        # Base confidence from impact score (extremes are more certain)
        if impact_score < 0.2 or impact_score > 0.8:
            base_confidence = 0.85
        elif impact_score < 0.4 or impact_score > 0.6:
            base_confidence = 0.70
        else:
            base_confidence = 0.60
        
        # Adjust based on data completeness
        data_completeness = self._assess_data_completeness(weather)
        confidence = base_confidence * data_completeness
        
        return min(1.0, max(0.5, confidence))
    
    def _assess_data_completeness(self, weather: WeatherObservation) -> float:
        """Assess how complete the weather data is"""
        factors = [
            weather.visibility_miles is not None,
            weather.ceiling_feet is not None,
            weather.wind_speed_knots is not None,
            weather.temperature_celsius is not None,
            weather.pressure_mb is not None
        ]
        completeness = sum(factors) / len(factors)
        return 0.7 + (completeness * 0.3)  # Minimum 0.7 if any data exists
    
    def _generate_reason(
        self,
        departure_impact: dict,
        arrival_impact: Optional[dict] = None
    ) -> str:
        """Generate human-readable reason for delay prediction"""
        reasons = []
        
        if departure_impact["visibility_impact"] > 0.5:
            reasons.append("low visibility at departure")
        if departure_impact["ceiling_impact"] > 0.5:
            reasons.append("low cloud ceiling at departure")
        if departure_impact["wind_impact"] > 0.5:
            reasons.append("high winds at departure")
        if departure_impact["precipitation_impact"] > 0.5:
            reasons.append("precipitation at departure")
        
        if arrival_impact:
            if arrival_impact["visibility_impact"] > 0.5:
                reasons.append("low visibility at arrival")
            if arrival_impact["ceiling_impact"] > 0.5:
                reasons.append("low cloud ceiling at arrival")
            if arrival_impact["wind_impact"] > 0.5:
                reasons.append("high winds at arrival")
            if arrival_impact["precipitation_impact"] > 0.5:
                reasons.append("precipitation at arrival")
        
        if not reasons:
            return "favorable weather conditions"
        
        return ", ".join(reasons)

