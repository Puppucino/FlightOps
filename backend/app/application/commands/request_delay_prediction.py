"""Request delay prediction command"""
from dataclasses import dataclass
from uuid import UUID
from typing import Optional


@dataclass
class RequestDelayPredictionCommand:
    """Command to request a delay prediction"""
    
    flight_id: UUID
    prediction_horizon_minutes: int = 60
    
    def __post_init__(self):
        """Validate command"""
        if not 30 <= self.prediction_horizon_minutes <= 120:
            raise ValueError("Prediction horizon must be between 30 and 120 minutes")


@dataclass
class UpdateWeatherDataCommand:
    """Command to update weather data for an airport"""
    
    airport_code: str  # ICAO code
    
    def __post_init__(self):
        """Validate command"""
        if not self.airport_code or len(self.airport_code) != 4:
            raise ValueError("Valid ICAO code (4 characters) is required")

