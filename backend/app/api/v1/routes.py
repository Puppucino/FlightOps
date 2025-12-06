"""API v1 routes for flight delay prediction"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
import httpx

from app.application.services.flight_delay_prediction_service import FlightDelayPredictionService
from app.infrastructure.repositories.in_memory_flight_repository import InMemoryFlightRepository
from app.infrastructure.repositories.in_memory_airport_repository import InMemoryAirportRepository
from app.infrastructure.external.aviation_weather_client import AviationWeatherClient
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.domain.entities.flight import Flight
from app.domain.entities.airport import Airport

router = APIRouter(prefix="/flight-delay", tags=["Flight Delay Prediction"])

# Global service instances - in production, use proper DI container
_global_flight_repo = None
_global_airport_repo = None
_global_weather_client = None
_global_event_bus = None
_global_prediction_service = None


def get_prediction_service() -> FlightDelayPredictionService:
    """Get prediction service instance (singleton pattern)"""
    global _global_prediction_service, _global_flight_repo, _global_airport_repo
    global _global_weather_client, _global_event_bus
    
    if _global_prediction_service is None:
        _global_flight_repo = InMemoryFlightRepository()
        _global_airport_repo = InMemoryAirportRepository()
        _global_weather_client = AviationWeatherClient()
        _global_event_bus = InMemoryEventBus()
        
        _global_prediction_service = FlightDelayPredictionService(
            flight_repository=_global_flight_repo,
            airport_repository=_global_airport_repo,
            weather_provider=_global_weather_client,
            event_bus=_global_event_bus
        )
        
        # Initialize with some sample airports
        _initialize_sample_airports(_global_airport_repo)
    
    return _global_prediction_service


def _initialize_sample_airports(airport_repo: InMemoryAirportRepository):
    """Initialize with common airports if not already present"""
    from uuid import uuid4
    
    sample_airports = [
        ("KJFK", "John F. Kennedy International Airport", "New York", "USA"),
        ("KLAX", "Los Angeles International Airport", "Los Angeles", "USA"),
        ("KORD", "Chicago O'Hare International Airport", "Chicago", "USA"),
        ("KATL", "Hartsfield-Jackson Atlanta International Airport", "Atlanta", "USA"),
        ("KDEN", "Denver International Airport", "Denver", "USA"),
        ("KSFO", "San Francisco International Airport", "San Francisco", "USA"),
        ("KMIA", "Miami International Airport", "Miami", "USA"),
        ("KSEA", "Seattle-Tacoma International Airport", "Seattle", "USA"),
    ]
    
    for icao, name, city, country in sample_airports:
        if not airport_repo.get_by_icao_code(icao):
            airport = Airport(
                airport_id=uuid4(),
                icao_code=icao,
                name=name,
                city=city,
                country=country
            )
            airport_repo.save(airport)


class FlightCreateRequest(BaseModel):
    """Request to create a flight"""
    flight_number: str
    departure_airport: str
    arrival_airport: str
    scheduled_departure: datetime
    scheduled_arrival: datetime


class PredictionResponse(BaseModel):
    """Delay prediction response"""
    flight_id: str
    predicted_delay_minutes: int
    confidence_score: float
    weather_impact_score: float
    reason: Optional[str] = None
    prediction_timestamp: datetime


@router.post("/flights", response_model=dict)
async def create_flight(
    request: FlightCreateRequest,
    service: FlightDelayPredictionService = Depends(get_prediction_service)
):
    """Create a new flight"""
    from uuid import uuid4
    
    flight = Flight(
        flight_id=uuid4(),
        flight_number=request.flight_number,
        departure_airport=request.departure_airport.upper(),
        arrival_airport=request.arrival_airport.upper(),
        scheduled_departure=request.scheduled_departure,
        scheduled_arrival=request.scheduled_arrival
    )
    
    service.flight_repository.save(flight)
    
    return {
        "flight_id": str(flight.flight_id),
        "flight_number": flight.flight_number,
        "status": "created"
    }


@router.post("/predict/{flight_id}", response_model=PredictionResponse)
async def predict_delay(
    flight_id: UUID,
    prediction_horizon_minutes: int = 60,
    service: FlightDelayPredictionService = Depends(get_prediction_service)
):
    """Predict delay for a flight
    
    Note: You must create a flight first using POST /api/v1/flight-delay/flights
    or use POST /api/v1/flight-delay/flights/sample to create a sample flight.
    """
    try:
        # Check if flight exists first
        flight = service.flight_repository.get_by_id(flight_id)
        if not flight:
            available_flights = service.flight_repository.get_all()
            if len(available_flights) == 0:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Flight {flight_id} not found. No flights exist. "
                        f"Please create a flight first using POST /api/v1/flight-delay/flights "
                        f"or POST /api/v1/flight-delay/flights/sample"
                    )
                )
            else:
                flight_ids = [str(f.flight_id) for f in available_flights]
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Flight {flight_id} not found. "
                        f"Available flight IDs: {', '.join(flight_ids[:5])}"
                        f"{'...' if len(flight_ids) > 5 else ''}"
                    )
                )
        
        prediction = await service.predict_delay(flight_id, prediction_horizon_minutes)
        
        return PredictionResponse(
            flight_id=str(prediction.flight_id),
            predicted_delay_minutes=prediction.predicted_delay_minutes,
            confidence_score=prediction.confidence_score,
            weather_impact_score=prediction.weather_impact_score,
            reason=prediction.reason,
            prediction_timestamp=prediction.prediction_timestamp
        )
    except ValueError as e:
        error_msg = str(e)
        # Check if it's a flight not found error
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        # Weather API errors
        elif "no metar" in error_msg.lower() or "no data" in error_msg.lower() or "empty response" in error_msg.lower():
            raise HTTPException(status_code=503, detail=f"Weather data unavailable: {error_msg}")
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Aviation Weather API error: {str(e)}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to Aviation Weather API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/flights/{flight_id}", response_model=dict)
async def get_flight(
    flight_id: UUID,
    service: FlightDelayPredictionService = Depends(get_prediction_service)
):
    """Get flight details"""
    flight = service.flight_repository.get_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    return {
        "flight_id": str(flight.flight_id),
        "flight_number": flight.flight_number,
        "departure_airport": flight.departure_airport,
        "arrival_airport": flight.arrival_airport,
        "scheduled_departure": flight.scheduled_departure.isoformat(),
        "scheduled_arrival": flight.scheduled_arrival.isoformat(),
        "status": flight.status
    }


@router.get("/flights", response_model=dict)
async def list_flights(
    service: FlightDelayPredictionService = Depends(get_prediction_service)
):
    """List all flights"""
    flights = service.flight_repository.get_all()
    return {
        "count": len(flights),
        "flights": [
            {
                "flight_id": str(flight.flight_id),
                "flight_number": flight.flight_number,
                "departure_airport": flight.departure_airport,
                "arrival_airport": flight.arrival_airport,
                "scheduled_departure": flight.scheduled_departure.isoformat(),
                "scheduled_arrival": flight.scheduled_arrival.isoformat(),
                "status": flight.status
            }
            for flight in flights
        ]
    }


@router.post("/flights/sample", response_model=dict)
async def create_sample_flight(
    service: FlightDelayPredictionService = Depends(get_prediction_service)
):
    """Create a sample flight for testing"""
    from uuid import uuid4
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    flight = Flight(
        flight_id=uuid4(),
        flight_number="AA100",
        departure_airport="KJFK",
        arrival_airport="KLAX",
        scheduled_departure=now + timedelta(minutes=60),
        scheduled_arrival=now + timedelta(hours=6)
    )
    
    service.flight_repository.save(flight)
    
    return {
        "flight_id": str(flight.flight_id),
        "flight_number": flight.flight_number,
        "departure_airport": flight.departure_airport,
        "arrival_airport": flight.arrival_airport,
        "scheduled_departure": flight.scheduled_departure.isoformat(),
        "scheduled_arrival": flight.scheduled_arrival.isoformat(),
        "status": "created",
        "message": "Sample flight created. Use this flight_id to test predictions."
    }


@router.get("/test-weather/{airport_code}", response_model=dict)
async def test_weather_api(
    airport_code: str,
    service: FlightDelayPredictionService = Depends(get_prediction_service)
):
    """Test weather API connection for a specific airport"""
    try:
        weather = await service.weather_provider.get_weather_observation(airport_code.upper())
        return {
            "airport_code": airport_code.upper(),
            "status": "success",
            "weather": {
                "observation_time": weather.observation_time.isoformat(),
                "visibility_miles": weather.visibility_miles,
                "ceiling_feet": weather.ceiling_feet,
                "wind_speed_knots": weather.wind_speed_knots,
                "wind_direction_degrees": weather.wind_direction_degrees,
                "temperature_celsius": weather.temperature_celsius,
                "weather_conditions": weather.weather_conditions
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Weather API test failed for {airport_code}: {str(e)}"
        )

