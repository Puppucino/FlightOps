"""
Database models
Import all models here to ensure they are registered with SQLAlchemy Base
"""
from app.models.airport import Airport
from app.models.airline import Airline
from app.models.aircraft import Aircraft, AircraftType
from app.models.flight import Flight
from app.models.weather import WeatherData
from app.models.traffic import AirportTraffic
from app.models.prediction import (
    FlightDelayPrediction,
    CargoPrediction,
    PassengerTrafficPrediction,
    MLModel
)

__all__ = [
    "Airport",
    "Airline",
    "Aircraft",
    "AircraftType",
    "Flight",
    "WeatherData",
    "AirportTraffic",
    "FlightDelayPrediction",
    "CargoPrediction",
    "PassengerTrafficPrediction",
    "MLModel",
]
