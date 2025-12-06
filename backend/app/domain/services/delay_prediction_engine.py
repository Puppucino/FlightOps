"""Delay prediction engine service"""
from typing import Optional
from ..value_objects.weather_observation import WeatherObservation
from ..value_objects.delay_prediction import DelayPrediction
from ..value_objects.prediction_request import PredictionRequest
from .weather_impact_analyzer import WeatherImpactAnalyzer


class DelayPredictionEngine:
    """Engine for predicting flight delays based on weather conditions"""
    
    def __init__(self):
        self.weather_analyzer = WeatherImpactAnalyzer()
    
    def predict_delay(
        self,
        request: PredictionRequest,
        departure_weather: WeatherObservation,
        arrival_weather: Optional[WeatherObservation] = None
    ) -> DelayPrediction:
        """
        Predict delay based on weather conditions
        
        Args:
            request: Prediction request with flight details
            departure_weather: Weather at departure airport
            arrival_weather: Optional weather at arrival airport
        
        Returns:
            Delay prediction with estimated delay minutes and confidence
        """
        # Analyze departure weather impact
        departure_impact = self.weather_analyzer.analyze(departure_weather)
        departure_score = departure_impact["overall_impact"]
        
        # Analyze arrival weather impact if provided
        arrival_score = 0.0
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
        reason = self._generate_reason(departure_impact, arrival_impact if arrival_weather else None)
        
        return DelayPrediction(
            flight_id=request.flight_id,
            predicted_delay_minutes=predicted_delay_minutes,
            confidence_score=confidence,
            prediction_timestamp=request.request_timestamp,
            prediction_horizon_minutes=request.prediction_horizon_minutes,
            weather_impact_score=weather_impact_score,
            reason=reason
        )
    
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

