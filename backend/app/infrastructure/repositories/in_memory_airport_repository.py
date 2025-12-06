"""In-memory airport repository"""
from typing import List, Optional
from uuid import UUID
from ...domain.entities.airport import Airport
from ...domain.interfaces.repositories import IAirportRepository


class InMemoryAirportRepository(IAirportRepository):
    """In-memory implementation of airport repository"""
    
    def __init__(self):
        self._airports: dict[UUID, Airport] = {}
        self._airports_by_icao: dict[str, Airport] = {}
    
    def get_by_icao_code(self, icao_code: str) -> Optional[Airport]:
        """Get airport by ICAO code"""
        return self._airports_by_icao.get(icao_code.upper())
    
    def get_by_id(self, airport_id: UUID) -> Optional[Airport]:
        """Get airport by ID"""
        return self._airports.get(airport_id)
    
    def save(self, airport: Airport) -> None:
        """Save or update airport"""
        self._airports[airport.airport_id] = airport
        self._airports_by_icao[airport.icao_code.upper()] = airport
    
    def get_all(self) -> List[Airport]:
        """Get all airports"""
        return list(self._airports.values())

