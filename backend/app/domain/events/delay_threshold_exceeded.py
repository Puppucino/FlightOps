"""Delay threshold exceeded event"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from .base_event import DomainEvent


class DelayThresholdExceeded(DomainEvent):
    """Event raised when predicted delay exceeds a threshold"""
    
    def __init__(
        self,
        flight_id: UUID,
        predicted_delay_minutes: int,
        threshold_minutes: int,
        occurred_at: Optional[datetime] = None
    ):
        super().__init__("DelayThresholdExceeded", occurred_at)
        self.flight_id = flight_id
        self.predicted_delay_minutes = predicted_delay_minutes
        self.threshold_minutes = threshold_minutes

