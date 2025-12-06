"""Repository interfaces"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..entities.flight import Flight
from ..entities.airport import Airport


class IFlightRepository(ABC):
    """Interface for flight repository"""
    
    @abstractmethod
    def get_by_id(self, flight_id: UUID) -> Optional[Flight]:
        """Get flight by ID"""
        pass
    
    @abstractmethod
    def get_by_flight_number(self, flight_number: str) -> Optional[Flight]:
        """Get flight by flight number"""
        pass
    
    @abstractmethod
    def get_departing_soon(self, minutes: int = 60) -> List[Flight]:
        """Get flights departing within specified minutes"""
        pass
    
    @abstractmethod
    def save(self, flight: Flight) -> None:
        """Save or update flight"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Flight]:
        """Get all flights"""
        pass


class IAirportRepository(ABC):
    """Interface for airport repository"""
    
    @abstractmethod
    def get_by_icao_code(self, icao_code: str) -> Optional[Airport]:
        """Get airport by ICAO code"""
        pass
    
    @abstractmethod
    def get_by_id(self, airport_id: UUID) -> Optional[Airport]:
        """Get airport by ID"""
        pass
    
    @abstractmethod
    def save(self, airport: Airport) -> None:
        """Save or update airport"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Airport]:
        """Get all airports"""
        pass


class IEventStore(ABC):
    """Interface for event store"""
    
    @abstractmethod
    def append(self, event) -> None:
        """Append event to store"""
        pass
    
    @abstractmethod
    def get_events_by_aggregate_id(self, aggregate_id: UUID) -> List:
        """Get all events for an aggregate"""
        pass
    
    @abstractmethod
    def get_events_by_type(self, event_type: str) -> List:
        """Get all events of a specific type"""
        pass
    
    @abstractmethod
    def get_all_events(self) -> List:
        """Get all events"""
        pass

