"""
Airport traffic model
"""
from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.core.types import GUID


class AirportTraffic(Base):
    """Historical airport traffic data (passengers and aircraft movements)"""
    __tablename__ = "airport_traffic"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    airport_id = Column(GUID(), ForeignKey("airports.id"), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)
    hour_of_day = Column(Integer, index=True)  # 0-23
    day_of_week = Column(Integer, index=True)  # 0-6 (Monday=0)
    passenger_count = Column(Integer)
    aircraft_movements = Column(Integer)
    cargo_tonnes = Column(DECIMAL(10, 2))
    arrival_count = Column(Integer)
    departure_count = Column(Integer)
    runway_utilization_percent = Column(DECIMAL(5, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    airport = relationship("Airport", back_populates="airport_traffic")
    
    # Indexes
    __table_args__ = (
        Index('idx_traffic_airport_time', 'airport_id', 'recorded_at'),
    )
    
    def __repr__(self):
        return f"<AirportTraffic {self.airport_id} {self.recorded_at}>"
