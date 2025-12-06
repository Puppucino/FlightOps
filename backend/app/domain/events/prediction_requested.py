"""Prediction requested event"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from .base_event import DomainEvent


class PredictionRequested(DomainEvent):
    """Event raised when a delay prediction is requested"""
    
    def __init__(
        self,
        flight_id: UUID,
        departure_airport: str,
        arrival_airport: str,
        scheduled_departure: datetime,
        occurred_at: Optional[datetime] = None
    ):
        super().__init__("PredictionRequested", occurred_at)
        self.flight_id = flight_id
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.scheduled_departure = scheduled_departure

