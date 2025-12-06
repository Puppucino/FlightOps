"""Service interfaces"""
from abc import ABC, abstractmethod
from typing import Optional
from ..value_objects.weather_observation import WeatherObservation
from ..value_objects.delay_prediction import DelayPrediction
from ..value_objects.prediction_request import PredictionRequest


class IWeatherDataProvider(ABC):
    """Interface for weather data provider"""
    
    @abstractmethod
    async def get_weather_observation(self, airport_code: str) -> WeatherObservation:
        """Get current weather observation for airport"""
        pass


class IDelayPredictionEngine(ABC):
    """Interface for delay prediction engine"""
    
    @abstractmethod
    def predict_delay(
        self,
        request: PredictionRequest,
        departure_weather: WeatherObservation,
        arrival_weather: Optional[WeatherObservation] = None
    ) -> DelayPrediction:
        """Predict delay based on weather conditions"""
        pass

