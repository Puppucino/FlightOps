"""
Aircraft models
"""
from sqlalchemy import Column, String, Integer, DECIMAL, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.core.types import GUID


class AircraftType(Base):
    """Aircraft type specifications"""
    __tablename__ = "aircraft_types"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    icao_code = Column(String(4), unique=True, nullable=False, index=True)
    manufacturer = Column(String(100))
    model = Column(String(100), nullable=False)
    passenger_capacity = Column(Integer)
    cargo_capacity_tonnes = Column(DECIMAL(10, 2))
    max_range_km = Column(Integer)
    cruising_speed_kmh = Column(Integer)
    fuel_capacity_liters = Column(DECIMAL(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    aircraft = relationship("Aircraft", back_populates="aircraft_type")
    
    def __repr__(self):
        return f"<AircraftType {self.icao_code} - {self.manufacturer} {self.model}>"


class Aircraft(Base):
    """Individual aircraft records"""
    __tablename__ = "aircraft"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    registration = Column(String(20), unique=True, nullable=False, index=True)
    aircraft_type_id = Column(GUID(), ForeignKey("aircraft_types.id"), nullable=False, index=True)
    airline_id = Column(GUID(), ForeignKey("airlines.id"), nullable=False, index=True)
    year_manufactured = Column(Integer)
    maintenance_status = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    aircraft_type = relationship("AircraftType", back_populates="aircraft")
    airline = relationship("Airline", back_populates="aircraft")
    flights = relationship("Flight", back_populates="aircraft")
    cargo_predictions = relationship("CargoPrediction", back_populates="aircraft")
    
    def __repr__(self):
        return f"<Aircraft {self.registration}>"
