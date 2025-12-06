"""Flight delay predicted event"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from .base_event import DomainEvent


class FlightDelayPredicted(DomainEvent):
    """Event raised when a flight delay is predicted"""
    
    def __init__(
        self,
        flight_id: UUID,
        predicted_delay_minutes: int,
        confidence_score: float,
        weather_impact_score: float = 0.0,
        reason: Optional[str] = None,
        occurred_at: Optional[datetime] = None
    ):
        super().__init__("FlightDelayPredicted", occurred_at)
        self.flight_id = flight_id
        self.predicted_delay_minutes = predicted_delay_minutes
        self.confidence_score = confidence_score
        self.weather_impact_score = weather_impact_score
        self.reason = reason

