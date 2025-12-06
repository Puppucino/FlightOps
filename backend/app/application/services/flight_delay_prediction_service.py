"""Flight delay prediction application service"""
from typing import Optional
from uuid import UUID
from ...domain.aggregates.flight_aggregate import FlightAggregate
from ...domain.aggregates.airport_aggregate import AirportAggregate
from ...domain.value_objects.prediction_request import PredictionRequest
from ...domain.value_objects.delay_prediction import DelayPrediction
from ...domain.services.delay_prediction_engine import DelayPredictionEngine
from ...domain.interfaces.repositories import IFlightRepository, IAirportRepository
from ...domain.interfaces.services import IWeatherDataProvider
from ...infrastructure.events.in_memory_event_bus import InMemoryEventBus


class FlightDelayPredictionService:
    """Application service for flight delay prediction"""
    
    def __init__(
        self,
        flight_repository: IFlightRepository,
        airport_repository: IAirportRepository,
        weather_provider: IWeatherDataProvider,
        event_bus: InMemoryEventBus
    ):
        self.flight_repository = flight_repository
        self.airport_repository = airport_repository
        self.weather_provider = weather_provider
        self.event_bus = event_bus
        self.prediction_engine = DelayPredictionEngine()
    
    async def predict_delay(
        self,
        flight_id: UUID,
        prediction_horizon_minutes: int = 60
    ) -> DelayPrediction:
        """
        Predict delay for a flight
        
        Args:
            flight_id: Flight ID
            prediction_horizon_minutes: How many minutes before departure to predict
        
        Returns:
            Delay prediction
        """
        # Get flight
        flight = self.flight_repository.get_by_id(flight_id)
        if not flight:
            raise ValueError(f"Flight {flight_id} not found")
        
        # Create aggregate
        flight_aggregate = FlightAggregate(flight)
        
        # Request prediction (publishes event)
        request_event = flight_aggregate.request_prediction()
        self.event_bus.publish(request_event)
        
        # Create prediction request
        request = PredictionRequest(
            flight_id=flight.flight_id,
            departure_airport=flight.departure_airport,
            arrival_airport=flight.arrival_airport,
            scheduled_departure=flight.scheduled_departure,
            prediction_horizon_minutes=prediction_horizon_minutes
        )
        
        # Get weather data for departure airport
        try:
            departure_weather = await self.weather_provider.get_weather_observation(
                flight.departure_airport
            )
        except Exception as e:
            raise ValueError(
                f"Failed to get weather data for departure airport {flight.departure_airport}: {str(e)}"
            )
        
        # Get weather data for arrival airport (optional)
        arrival_weather = None
        try:
            arrival_weather = await self.weather_provider.get_weather_observation(
                flight.arrival_airport
            )
        except Exception as e:
            # If arrival weather unavailable, continue with departure only
            # Log but don't fail - departure weather is more critical
            pass
        
        # Update airport aggregates with weather
        departure_airport = self.airport_repository.get_by_icao_code(flight.departure_airport)
        if departure_airport:
            airport_aggregate = AirportAggregate(departure_airport)
            weather_event = airport_aggregate.update_weather(departure_weather)
            self.event_bus.publish(weather_event)
            self.airport_repository.save(departure_airport)
        
        if arrival_weather and flight.arrival_airport:
            arrival_airport = self.airport_repository.get_by_icao_code(flight.arrival_airport)
            if arrival_airport:
                airport_aggregate = AirportAggregate(arrival_airport)
                weather_event = airport_aggregate.update_weather(arrival_weather)
                self.event_bus.publish(weather_event)
                self.airport_repository.save(arrival_airport)
        
        # Generate prediction
        prediction = self.prediction_engine.predict_delay(
            request,
            departure_weather,
            arrival_weather
        )
        
        # Record prediction in aggregate (publishes events)
        events = flight_aggregate.record_prediction(prediction)
        self.event_bus.publish_all(events)
        
        # Save flight
        self.flight_repository.save(flight)
        
        return prediction
    
    async def get_prediction(self, flight_id: UUID) -> Optional[DelayPrediction]:
        """Get latest prediction for a flight"""
        flight = self.flight_repository.get_by_id(flight_id)
        if not flight:
            return None
        
        # In a real system, we'd query predictions from a store
        # For now, we'll need to track predictions separately or replay events
        # This is a simplified version
        return None

