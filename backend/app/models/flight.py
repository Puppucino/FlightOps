"""
Flight model
"""
from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.core.types import GUID


class Flight(Base):
    """Scheduled and actual flight information"""
    __tablename__ = "flights"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    flight_number = Column(String(10), nullable=False)
    airline_id = Column(GUID(), ForeignKey("airlines.id"), nullable=False)
    aircraft_id = Column(GUID(), ForeignKey("aircraft.id"), nullable=False)
    origin_airport_id = Column(GUID(), ForeignKey("airports.id"), nullable=False, index=True)
    destination_airport_id = Column(GUID(), ForeignKey("airports.id"), nullable=False, index=True)
    scheduled_departure = Column(DateTime(timezone=True), nullable=False, index=True)
    scheduled_arrival = Column(DateTime(timezone=True), nullable=False)
    actual_departure = Column(DateTime(timezone=True))
    actual_arrival = Column(DateTime(timezone=True))
    departure_delay_minutes = Column(Integer)
    arrival_delay_minutes = Column(Integer)
    cancellation_status = Column(String(20))
    flight_type = Column(String(20), nullable=False)  # 'passenger' or 'cargo'
    passenger_count = Column(Integer)
    cargo_weight_tonnes = Column(DECIMAL(10, 2))
    flight_status = Column(String(20), index=True)  # e.g., 'scheduled', 'departed', 'arrived', 'cancelled'
    distance_km = Column(DECIMAL(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    airline = relationship("Airline", back_populates="flights")
    aircraft = relationship("Aircraft", back_populates="flights")
    origin_airport = relationship("Airport", foreign_keys=[origin_airport_id], back_populates="flights_origin")
    destination_airport = relationship("Airport", foreign_keys=[destination_airport_id], back_populates="flights_destination")
    delay_predictions = relationship("FlightDelayPrediction", back_populates="flight")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_flights_number_date', 'flight_number', 'scheduled_departure'),
        Index('idx_flights_origin_departure', 'origin_airport_id', 'scheduled_departure'),
        Index('idx_flights_destination_arrival', 'destination_airport_id', 'scheduled_arrival'),
        CheckConstraint("flight_type IN ('passenger', 'cargo', 'mixed')", name="check_flight_type"),
    )
    
    def __repr__(self):
        return f"<Flight {self.flight_number} {self.scheduled_departure}>"
