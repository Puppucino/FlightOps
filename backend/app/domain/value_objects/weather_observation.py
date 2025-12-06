"""Weather observation value object"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class WeatherObservation:
    """Immutable weather observation value object"""
    
    airport_code: str
    observation_time: datetime
    visibility_miles: Optional[float] = None
    visibility_meters: Optional[float] = None
    ceiling_feet: Optional[int] = None
    wind_direction_degrees: Optional[int] = None
    wind_speed_knots: Optional[int] = None
    wind_gust_knots: Optional[int] = None
    temperature_celsius: Optional[float] = None
    dewpoint_celsius: Optional[float] = None
    pressure_mb: Optional[float] = None
    weather_conditions: Optional[str] = None  # e.g., "RA", "SN", "FG"
    raw_metar: Optional[str] = None
    
    def has_low_visibility(self, threshold_miles: float = 3.0) -> bool:
        """Check if visibility is below threshold"""
        if self.visibility_miles is None:
            return False
        return self.visibility_miles < threshold_miles
    
    def has_low_ceiling(self, threshold_feet: int = 1000) -> bool:
        """Check if ceiling is below threshold"""
        if self.ceiling_feet is None:
            return False
        return self.ceiling_feet < threshold_feet
    
    def has_high_wind(self, threshold_knots: int = 25) -> bool:
        """Check if wind speed exceeds threshold"""
        if self.wind_speed_knots is None:
            return False
        return self.wind_speed_knots > threshold_knots
    
    def has_precipitation(self) -> bool:
        """Check if precipitation is present"""
        if not self.weather_conditions:
            return False
        precip_codes = ["RA", "SN", "PL", "DZ", "GR", "GS", "UP"]
        return any(code in self.weather_conditions for code in precip_codes)
    
    def is_imc(self) -> bool:
        """Check if conditions are Instrument Meteorological Conditions (IMC)"""
        return self.has_low_visibility() or self.has_low_ceiling()

