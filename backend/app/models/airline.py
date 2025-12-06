"""
Airline model
"""
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.core.types import GUID


class Airline(Base):
    """Airline information"""
    __tablename__ = "airlines"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    icao_code = Column(String(3), unique=True, index=True)
    iata_code = Column(String(2), unique=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    aircraft = relationship("Aircraft", back_populates="airline", cascade="all, delete-orphan")
    flights = relationship("Flight", back_populates="airline", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Airline {self.icao_code} - {self.name}>"
