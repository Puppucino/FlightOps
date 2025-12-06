"""Weather data received event"""
from datetime import datetime
from typing import Optional
from .base_event import DomainEvent
from ..value_objects.weather_observation import WeatherObservation


class WeatherDataReceived(DomainEvent):
    """Event raised when weather data is received for an airport"""
    
    def __init__(
        self,
        airport_code: str,
        weather_observation: WeatherObservation,
        occurred_at: Optional[datetime] = None
    ):
        super().__init__("WeatherDataReceived", occurred_at)
        self.airport_code = airport_code
        self.weather_observation = weather_observation

