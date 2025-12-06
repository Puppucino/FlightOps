"""Airport aggregate root"""
from typing import List, Optional
from datetime import datetime
from ..entities.airport import Airport
from ..value_objects.weather_observation import WeatherObservation
from ..events.weather_data_received import WeatherDataReceived


class AirportAggregate:
    """Airport aggregate root managing airport state and weather"""
    
    def __init__(self, airport: Airport):
        self.airport = airport
        self._uncommitted_events: List = []
        self._current_weather: Optional[WeatherObservation] = None
    
    def update_weather(self, weather: WeatherObservation) -> WeatherDataReceived:
        """Update weather observation and publish event"""
        self._current_weather = weather
        
        # Update airport last weather update time
        self.airport.last_weather_update = datetime.now()
        
        # Publish event
        event = WeatherDataReceived(
            airport_code=self.airport.icao_code,
            weather_observation=weather
        )
        self._uncommitted_events.append(event)
        return event
    
    def get_current_weather(self) -> Optional[WeatherObservation]:
        """Get current weather observation"""
        return self._current_weather
    
    def get_uncommitted_events(self) -> List:
        """Get all uncommitted events"""
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self) -> None:
        """Mark all events as committed"""
        self._uncommitted_events.clear()

