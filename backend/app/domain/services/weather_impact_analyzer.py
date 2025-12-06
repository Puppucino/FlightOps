"""Weather impact analyzer service"""
from typing import Dict
from ..value_objects.weather_observation import WeatherObservation


class WeatherImpactAnalyzer:
    """Analyzes weather conditions and calculates impact scores"""
    
    # Thresholds for weather conditions
    VISIBILITY_THRESHOLDS = {
        "excellent": 10.0,  # miles
        "good": 5.0,
        "moderate": 3.0,
        "poor": 1.0,
        "very_poor": 0.5
    }
    
    CEILING_THRESHOLDS = {
        "excellent": 5000,  # feet
        "good": 3000,
        "moderate": 1500,
        "poor": 1000,
        "very_poor": 500
    }
    
    WIND_THRESHOLDS = {
        "calm": 10,  # knots
        "light": 15,
        "moderate": 25,
        "strong": 35,
        "very_strong": 50
    }
    
    def analyze(self, weather: WeatherObservation) -> Dict[str, float]:
        """
        Analyze weather conditions and return impact scores
        
        Returns:
            Dictionary with impact scores for visibility, ceiling, wind, precipitation
            Each score is 0.0 (no impact) to 1.0 (severe impact)
        """
        visibility_score = self._analyze_visibility(weather)
        ceiling_score = self._analyze_ceiling(weather)
        wind_score = self._analyze_wind(weather)
        precipitation_score = self._analyze_precipitation(weather)
        
        return {
            "visibility_impact": visibility_score,
            "ceiling_impact": ceiling_score,
            "wind_impact": wind_score,
            "precipitation_impact": precipitation_score,
            "overall_impact": max(visibility_score, ceiling_score, wind_score, precipitation_score)
        }
    
    def _analyze_visibility(self, weather: WeatherObservation) -> float:
        """Calculate visibility impact score"""
        if weather.visibility_miles is None:
            return 0.0
        
        vis = weather.visibility_miles
        
        if vis >= self.VISIBILITY_THRESHOLDS["excellent"]:
            return 0.0
        elif vis >= self.VISIBILITY_THRESHOLDS["good"]:
            return 0.2
        elif vis >= self.VISIBILITY_THRESHOLDS["moderate"]:
            return 0.4
        elif vis >= self.VISIBILITY_THRESHOLDS["poor"]:
            return 0.7
        elif vis >= self.VISIBILITY_THRESHOLDS["very_poor"]:
            return 0.9
        else:
            return 1.0
    
    def _analyze_ceiling(self, weather: WeatherObservation) -> float:
        """Calculate ceiling impact score"""
        if weather.ceiling_feet is None:
            return 0.0
        
        ceiling = weather.ceiling_feet
        
        if ceiling >= self.CEILING_THRESHOLDS["excellent"]:
            return 0.0
        elif ceiling >= self.CEILING_THRESHOLDS["good"]:
            return 0.2
        elif ceiling >= self.CEILING_THRESHOLDS["moderate"]:
            return 0.4
        elif ceiling >= self.CEILING_THRESHOLDS["poor"]:
            return 0.7
        elif ceiling >= self.CEILING_THRESHOLDS["very_poor"]:
            return 0.9
        else:
            return 1.0
    
    def _analyze_wind(self, weather: WeatherObservation) -> float:
        """Calculate wind impact score"""
        if weather.wind_speed_knots is None:
            return 0.0
        
        wind = weather.wind_speed_knots
        gust = weather.wind_gust_knots or wind
        
        # Use gust speed if available, otherwise use sustained wind
        effective_wind = max(wind, gust * 0.8)  # Gusts are temporary
        
        if effective_wind < self.WIND_THRESHOLDS["calm"]:
            return 0.0
        elif effective_wind < self.WIND_THRESHOLDS["light"]:
            return 0.1
        elif effective_wind < self.WIND_THRESHOLDS["moderate"]:
            return 0.3
        elif effective_wind < self.WIND_THRESHOLDS["strong"]:
            return 0.6
        elif effective_wind < self.WIND_THRESHOLDS["very_strong"]:
            return 0.9
        else:
            return 1.0
    
    def _analyze_precipitation(self, weather: WeatherObservation) -> float:
        """Calculate precipitation impact score"""
        if not weather.has_precipitation():
            return 0.0
        
        # Different precipitation types have different impacts
        conditions = weather.weather_conditions or ""
        
        if "GR" in conditions or "GS" in conditions:  # Hail
            return 1.0
        elif "SN" in conditions:  # Snow
            return 0.8
        elif "RA" in conditions and "TS" in conditions:  # Thunderstorm with rain
            return 0.9
        elif "RA" in conditions:  # Rain
            return 0.5
        elif "DZ" in conditions:  # Drizzle
            return 0.3
        else:
            return 0.4
    
    def categorize_severity(self, overall_impact: float) -> str:
        """Categorize weather severity based on impact score"""
        if overall_impact < 0.3:
            return "low"
        elif overall_impact < 0.6:
            return "medium"
        else:
            return "high"

