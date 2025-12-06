"""
Weather data model
"""
from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.core.types import GUID


class WeatherData(Base):
    """Historical and current weather conditions"""
    __tablename__ = "weather_data"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    airport_id = Column(GUID(), ForeignKey("airports.id"), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)
    temperature_celsius = Column(DECIMAL(5, 2))
    humidity_percent = Column(DECIMAL(5, 2))
    wind_speed_kmh = Column(DECIMAL(6, 2))
    wind_direction_degrees = Column(Integer)
    visibility_km = Column(DECIMAL(6, 2))
    pressure_hpa = Column(DECIMAL(7, 2))
    conditions = Column(String(100))  # e.g., "clear", "rain", "snow", "fog"
    precipitation_mm = Column(DECIMAL(6, 2))
    cloud_cover_percent = Column(DECIMAL(5, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    airport = relationship("Airport", back_populates="weather_data")
    
    # Indexes
    __table_args__ = (
        Index('idx_weather_airport_time', 'airport_id', 'recorded_at'),
    )
    
    def __repr__(self):
        return f"<WeatherData {self.airport_id} {self.recorded_at}>"
