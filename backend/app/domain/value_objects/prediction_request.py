"""Prediction request value object"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class PredictionRequest:
    """Immutable prediction request value object"""
    
    flight_id: UUID
    departure_airport: str  # ICAO code
    arrival_airport: str  # ICAO code
    scheduled_departure: datetime
    prediction_horizon_minutes: int = 60  # Predict 30-60 minutes before departure
    request_timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate request data"""
        if not self.departure_airport or len(self.departure_airport) != 4:
            raise ValueError("Valid departure airport ICAO code (4 characters) is required")
        if not self.arrival_airport or len(self.arrival_airport) != 4:
            raise ValueError("Valid arrival airport ICAO code (4 characters) is required")
        if not 30 <= self.prediction_horizon_minutes <= 120:
            raise ValueError("Prediction horizon must be between 30 and 120 minutes")
        if self.request_timestamp is None:
            object.__setattr__(self, 'request_timestamp', datetime.now())
    
    def is_within_prediction_window(self) -> bool:
        """Check if current time is within prediction window"""
        now = datetime.now()
        window_start = self.scheduled_departure.replace(
            minute=self.scheduled_departure.minute - self.prediction_horizon_minutes
        )
        window_end = self.scheduled_departure
        return window_start <= now <= window_end

