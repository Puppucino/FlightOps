"""Flight aggregate root"""
from typing import List, Optional
from uuid import UUID
from ..entities.flight import Flight
from ..value_objects.delay_prediction import DelayPrediction
from ..events.flight_delay_predicted import FlightDelayPredicted
from ..events.prediction_requested import PredictionRequested
from ..events.delay_threshold_exceeded import DelayThresholdExceeded


class FlightAggregate:
    """Flight aggregate root managing flight state and events"""
    
    def __init__(self, flight: Flight):
        self.flight = flight
        self._uncommitted_events: List = []
        self._predictions: List[DelayPrediction] = []
    
    def request_prediction(self) -> PredictionRequested:
        """Request a delay prediction for this flight"""
        event = PredictionRequested(
            flight_id=self.flight.flight_id,
            departure_airport=self.flight.departure_airport,
            arrival_airport=self.flight.arrival_airport,
            scheduled_departure=self.flight.scheduled_departure
        )
        self._uncommitted_events.append(event)
        return event
    
    def record_prediction(
        self,
        prediction: DelayPrediction,
        threshold_minutes: int = 15
    ) -> List:
        """Record a delay prediction and publish events"""
        events = []
        
        # Store prediction
        self._predictions.append(prediction)
        
        # Publish delay predicted event
        delay_event = FlightDelayPredicted(
            flight_id=prediction.flight_id,
            predicted_delay_minutes=prediction.predicted_delay_minutes,
            confidence_score=prediction.confidence_score,
            weather_impact_score=prediction.weather_impact_score,
            reason=prediction.reason
        )
        events.append(delay_event)
        self._uncommitted_events.append(delay_event)
        
        # Check if threshold exceeded
        if prediction.is_significant_delay(threshold_minutes):
            threshold_event = DelayThresholdExceeded(
                flight_id=prediction.flight_id,
                predicted_delay_minutes=prediction.predicted_delay_minutes,
                threshold_minutes=threshold_minutes
            )
            events.append(threshold_event)
            self._uncommitted_events.append(threshold_event)
            
            # Update flight status if significant delay
            if self.flight.status == "scheduled":
                self.flight.status = "delayed"
        
        return events
    
    def get_latest_prediction(self) -> Optional[DelayPrediction]:
        """Get the most recent prediction"""
        if not self._predictions:
            return None
        return max(self._predictions, key=lambda p: p.prediction_timestamp)
    
    def get_uncommitted_events(self) -> List:
        """Get all uncommitted events"""
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self) -> None:
        """Mark all events as committed"""
        self._uncommitted_events.clear()

