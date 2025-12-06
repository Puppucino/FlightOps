"""Flight entity"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Flight:
    """Flight entity representing a scheduled flight"""
    
    flight_id: UUID
    flight_number: str
    departure_airport: str  # ICAO code
    arrival_airport: str  # ICAO code
    scheduled_departure: datetime
    scheduled_arrival: datetime
    status: str = "scheduled"  # scheduled, delayed, cancelled, departed, arrived
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate flight data"""
        if not self.flight_number:
            raise ValueError("Flight number is required")
        if not self.departure_airport or len(self.departure_airport) != 4:
            raise ValueError("Valid departure airport ICAO code (4 characters) is required")
        if not self.arrival_airport or len(self.arrival_airport) != 4:
            raise ValueError("Valid arrival airport ICAO code (4 characters) is required")
    
    def is_departing_soon(self, minutes: int = 60) -> bool:
        """Check if flight is departing within specified minutes"""
        if self.actual_departure:
            return False
        time_until_departure = (self.scheduled_departure - datetime.now()).total_seconds() / 60
        return 0 <= time_until_departure <= minutes
    
    def get_minutes_until_departure(self) -> float:
        """Get minutes until scheduled departure"""
        if self.actual_departure:
            return 0.0
        delta = (self.scheduled_departure - datetime.now()).total_seconds() / 60
        return max(0.0, delta)

