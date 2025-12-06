"""
Airport model
"""
from sqlalchemy import Column, String, Integer, DECIMAL, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.core.types import GUID


class Airport(Base):
    """Airport information"""
    __tablename__ = "airports"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    icao_code = Column(String(4), unique=True, nullable=False, index=True)
    iata_code = Column(String(3), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    city = Column(String(100))
    country = Column(String(100))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    elevation_ft = Column(Integer)
    timezone = Column(String(50))
    passenger_capacity = Column(Integer)
    cargo_capacity_tonnes = Column(DECIMAL(10, 2))
    runways = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships (lazy loading to avoid circular imports)
    flights_origin = relationship("Flight", foreign_keys="Flight.origin_airport_id", back_populates="origin_airport")
    flights_destination = relationship("Flight", foreign_keys="Flight.destination_airport_id", back_populates="destination_airport")
    weather_data = relationship("WeatherData", back_populates="airport", cascade="all, delete-orphan")
    airport_traffic = relationship("AirportTraffic", back_populates="airport", cascade="all, delete-orphan")
    cargo_predictions = relationship("CargoPrediction", back_populates="airport", cascade="all, delete-orphan")
    passenger_traffic_predictions = relationship("PassengerTrafficPrediction", back_populates="airport", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_airports_location', 'latitude', 'longitude'),
    )
    
    def __repr__(self):
        return f"<Airport {self.icao_code} - {self.name}>"
