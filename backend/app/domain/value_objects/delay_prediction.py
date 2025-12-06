"""Delay prediction value object"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class DelayPrediction:
    """Immutable delay prediction value object"""
    
    flight_id: UUID
    predicted_delay_minutes: int
    confidence_score: float  # 0.0 to 1.0
    prediction_timestamp: datetime
    prediction_horizon_minutes: int  # How many minutes before departure
    weather_impact_score: float = 0.0  # 0.0 to 1.0
    reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate prediction data"""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        if self.predicted_delay_minutes < 0:
            raise ValueError("Predicted delay cannot be negative")
        if not 0.0 <= self.weather_impact_score <= 1.0:
            raise ValueError("Weather impact score must be between 0.0 and 1.0")
    
    def is_significant_delay(self, threshold_minutes: int = 15) -> bool:
        """Check if predicted delay exceeds threshold"""
        return self.predicted_delay_minutes >= threshold_minutes
    
    def is_high_confidence(self, threshold: float = 0.7) -> bool:
        """Check if prediction has high confidence"""
        return self.confidence_score >= threshold

