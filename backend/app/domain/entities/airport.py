"""Airport entity"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Airport:
    """Airport entity representing an airport"""
    
    airport_id: UUID
    icao_code: str  # 4-letter ICAO code
    name: str
    city: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    last_weather_update: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate airport data"""
        if not self.icao_code or len(self.icao_code) != 4:
            raise ValueError("Valid ICAO code (4 characters) is required")
        self.icao_code = self.icao_code.upper()

