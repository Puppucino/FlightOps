"""In-memory flight repository"""
from typing import List, Optional
from uuid import UUID
from ...domain.entities.flight import Flight
from ...domain.interfaces.repositories import IFlightRepository


class InMemoryFlightRepository(IFlightRepository):
    """In-memory implementation of flight repository"""
    
    def __init__(self):
        self._flights: dict[UUID, Flight] = {}
        self._flights_by_number: dict[str, Flight] = {}
    
    def get_by_id(self, flight_id: UUID) -> Optional[Flight]:
        """Get flight by ID"""
        return self._flights.get(flight_id)
    
    def get_by_flight_number(self, flight_number: str) -> Optional[Flight]:
        """Get flight by flight number"""
        return self._flights_by_number.get(flight_number.upper())
    
    def get_departing_soon(self, minutes: int = 60) -> List[Flight]:
        """Get flights departing within specified minutes"""
        from datetime import datetime
        now = datetime.now()
        result = []
        
        for flight in self._flights.values():
            if flight.is_departing_soon(minutes):
                result.append(flight)
        
        return result
    
    def save(self, flight: Flight) -> None:
        """Save or update flight"""
        self._flights[flight.flight_id] = flight
        self._flights_by_number[flight.flight_number.upper()] = flight
    
    def get_all(self) -> List[Flight]:
        """Get all flights"""
        return list(self._flights.values())

