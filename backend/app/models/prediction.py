"""
ML Prediction models
"""
from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
import uuid

from app.core.database import Base
from app.core.types import GUID


class FlightDelayPrediction(Base):
    """ML model predictions for flight delays"""
    __tablename__ = "flight_delay_predictions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    flight_id = Column(GUID(), ForeignKey("flights.id"), nullable=False, index=True)
    prediction_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    delay_probability = Column(DECIMAL(5, 4), nullable=False)  # 0-1
    predicted_delay_minutes = Column(Integer)
    confidence_score = Column(DECIMAL(5, 4))  # 0-1
    model_version = Column(String(50), index=True)
    predicted_by = Column(String(50))  # Model identifier
    actual_delay_minutes = Column(Integer)  # For validation after flight
    prediction_accuracy = Column(DECIMAL(5, 4))  # Calculated after actual data available
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    flight = relationship("Flight", back_populates="delay_predictions")
    
    def __repr__(self):
        return f"<FlightDelayPrediction {self.flight_id} delay_prob={self.delay_probability}>"


class CargoPrediction(Base):
    """ML model predictions for cargo demand"""
    __tablename__ = "cargo_predictions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    airport_id = Column(GUID(), ForeignKey("airports.id"), nullable=False, index=True)
    aircraft_id = Column(GUID(), ForeignKey("aircraft.id"), nullable=True, index=True)
    prediction_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    predicted_cargo_tonnes = Column(DECIMAL(10, 2), nullable=False)
    predicted_period_start = Column(DateTime(timezone=True))
    predicted_period_end = Column(DateTime(timezone=True))
    confidence_score = Column(DECIMAL(5, 4))  # 0-1
    model_version = Column(String(50))
    actual_cargo_tonnes = Column(DECIMAL(10, 2))  # For validation
    prediction_accuracy = Column(DECIMAL(5, 4))  # Calculated after actual data available
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    airport = relationship("Airport", back_populates="cargo_predictions")
    aircraft = relationship("Aircraft", back_populates="cargo_predictions")
    
    # Indexes
    __table_args__ = (
        Index('idx_cargo_predictions_period', 'predicted_period_start', 'predicted_period_end'),
    )
    
    def __repr__(self):
        return f"<CargoPrediction {self.airport_id} cargo={self.predicted_cargo_tonnes} tonnes>"


class PassengerTrafficPrediction(Base):
    """ML model predictions for passenger traffic"""
    __tablename__ = "passenger_traffic_predictions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    airport_id = Column(GUID(), ForeignKey("airports.id"), nullable=False, index=True)
    prediction_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    predicted_passengers = Column(Integer, nullable=False)
    predicted_period_start = Column(DateTime(timezone=True))
    predicted_period_end = Column(DateTime(timezone=True))
    confidence_score = Column(DECIMAL(5, 4))  # 0-1
    model_version = Column(String(50))
    actual_passengers = Column(Integer)  # For validation
    prediction_accuracy = Column(DECIMAL(5, 4))  # Calculated after actual data available
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    airport = relationship("Airport", back_populates="passenger_traffic_predictions")
    
    # Indexes
    __table_args__ = (
        Index('idx_passenger_predictions_period', 'predicted_period_start', 'predicted_period_end'),
    )
    
    def __repr__(self):
        return f"<PassengerTrafficPrediction {self.airport_id} passengers={self.predicted_passengers}>"


class MLModel(Base):
    """Metadata about trained ML models"""
    __tablename__ = "ml_models"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), unique=True, nullable=False)
    model_type = Column(String(50), nullable=False)  # 'delay', 'cargo', 'passenger_traffic'
    version = Column(String(50), nullable=False)
    file_path = Column(String(500))
    training_accuracy = Column(DECIMAL(5, 4))
    validation_accuracy = Column(DECIMAL(5, 4))
    test_accuracy = Column(DECIMAL(5, 4))
    training_data_range_start = Column(DateTime(timezone=True))
    training_data_range_end = Column(DateTime(timezone=True))
    feature_list = Column(JSON)  # List of features used
    hyperparameters = Column(JSON)  # Model hyperparameters
    is_active = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_models_name_version', 'model_name', 'version'),
        Index('idx_models_type_active', 'model_type', 'is_active'),
    )
    
    def __repr__(self):
        return f"<MLModel {self.model_name} v{self.version} ({self.model_type})>"
