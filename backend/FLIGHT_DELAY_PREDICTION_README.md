# Flight Delay Prediction System - Implementation Summary

## Overview
A highly scalable, event-driven Flight Delay Prediction system implemented using Domain Driven Design (DDD) principles. The system predicts flight delays 30-60 minutes early using real-time weather data from the Aviation Weather API.

## Architecture

### Domain Layer (`backend/app/domain/`)
- **Entities**: `Flight`, `Airport`
- **Value Objects**: `WeatherObservation`, `DelayPrediction`, `PredictionRequest`
- **Aggregates**: `FlightAggregate`, `AirportAggregate`
- **Domain Events**: `FlightDelayPredicted`, `WeatherDataReceived`, `PredictionRequested`, `DelayThresholdExceeded`
- **Domain Services**: `DelayPredictionEngine`, `WeatherImpactAnalyzer`
- **Interfaces**: Repository and service contracts

### Application Layer (`backend/app/application/`)
- **Services**: `FlightDelayPredictionService` - orchestrates prediction workflow
- **Commands**: `RequestDelayPredictionCommand`, `UpdateWeatherDataCommand`

### Infrastructure Layer (`backend/app/infrastructure/`)
- **Repositories**: In-memory implementations for flights, airports, and events
- **External Services**: `AviationWeatherClient` - integrates with Aviation Weather API
- **Events**: `InMemoryEventBus` - event publishing and subscription

### API Layer (`backend/app/api/v1/`)
- RESTful endpoints for:
  - Creating flights
  - Requesting delay predictions
  - Retrieving flight information

## Key Features

1. **Weather-Based Delay Prediction**
   - Analyzes visibility, ceiling, wind, and precipitation
   - Calculates weather impact scores
   - Predicts delay duration (0-120 minutes)
   - Provides confidence scores

2. **Event-Driven Architecture**
   - Domain events for all significant actions
   - Event store for audit trail
   - Event bus for decoupled communication

3. **Real-Time Weather Integration**
   - Fetches METAR data from Aviation Weather API
   - Respects API rate limits (100 requests/minute)
   - Parses and maps weather data to domain objects

4. **In-Memory Storage**
   - All repositories use in-memory storage
   - Event store tracks all domain events
   - Suitable for demos and testing

## Usage

### Running the Demo Script

```bash
cd backend
python demo_flight_delay_prediction.py
```

The demo script will:
1. Initialize repositories and services
2. Create sample airports (KJFK, KLAX, KORD)
3. Create sample flights
4. Fetch real weather data from Aviation Weather API
5. Generate delay predictions
6. Display event history

### Using the API

Start the FastAPI server:
```bash
cd backend
uvicorn app.main:app --reload
```

API endpoints:
- `POST /api/v1/flight-delay/flights` - Create a flight
- `POST /api/v1/flight-delay/predict/{flight_id}` - Get delay prediction
- `GET /api/v1/flight-delay/flights/{flight_id}` - Get flight details

Example API request:
```bash
# Create a flight
curl -X POST "http://localhost:8000/api/v1/flight-delay/flights" \
  -H "Content-Type: application/json" \
  -d '{
    "flight_number": "AA100",
    "departure_airport": "KJFK",
    "arrival_airport": "KLAX",
    "scheduled_departure": "2025-01-15T14:00:00",
    "scheduled_arrival": "2025-01-15T20:00:00"
  }'

# Get prediction
curl "http://localhost:8000/api/v1/flight-delay/predict/{flight_id}?prediction_horizon_minutes=60"
```

## Prediction Algorithm

The system uses a weighted scoring approach:

1. **Weather Impact Analysis**
   - Visibility impact (0.0 - 1.0)
   - Ceiling impact (0.0 - 1.0)
   - Wind impact (0.0 - 1.0)
   - Precipitation impact (0.0 - 1.0)
   - Overall impact = max of all impacts

2. **Delay Calculation**
   - Impact < 0.2: No delay (0 minutes)
   - Impact 0.2-0.4: Minor delay (0-12 minutes)
   - Impact 0.4-0.6: Moderate delay (15-30 minutes)
   - Impact 0.6-0.8: Significant delay (30-60 minutes)
   - Impact > 0.8: Major delay (60-120 minutes)

3. **Confidence Scoring**
   - Higher confidence for extreme conditions (very good or very bad)
   - Adjusted based on data completeness
   - Minimum confidence: 50%

## File Structure

```
backend/app/
├── domain/
│   ├── entities/
│   │   ├── flight.py
│   │   └── airport.py
│   ├── value_objects/
│   │   ├── weather_observation.py
│   │   ├── delay_prediction.py
│   │   └── prediction_request.py
│   ├── aggregates/
│   │   ├── flight_aggregate.py
│   │   └── airport_aggregate.py
│   ├── events/
│   │   ├── base_event.py
│   │   ├── flight_delay_predicted.py
│   │   ├── weather_data_received.py
│   │   ├── prediction_requested.py
│   │   └── delay_threshold_exceeded.py
│   ├── services/
│   │   ├── delay_prediction_engine.py
│   │   └── weather_impact_analyzer.py
│   └── interfaces/
│       ├── repositories.py
│       └── services.py
├── application/
│   ├── services/
│   │   └── flight_delay_prediction_service.py
│   └── commands/
│       └── request_delay_prediction.py
├── infrastructure/
│   ├── repositories/
│   │   ├── in_memory_flight_repository.py
│   │   ├── in_memory_airport_repository.py
│   │   └── in_memory_event_store.py
│   ├── external/
│   │   └── aviation_weather_client.py
│   └── events/
│       └── in_memory_event_bus.py
└── api/
    └── v1/
        └── routes.py
```

## Dependencies

All required dependencies are already in `requirements.txt`:
- `httpx` - HTTP client for API calls
- `pydantic` - Data validation
- `python-dateutil` - Date/time utilities
- `fastapi` - Web framework
- `uvicorn` - ASGI server

## Notes

- The system uses in-memory storage as specified
- All repositories and event stores are in-memory implementations
- The Aviation Weather API is rate-limited to 100 requests/minute
- Weather data is fetched in real-time from the API
- Predictions are based on current weather conditions at departure and arrival airports

## Future Enhancements

- Persistent storage (database integration)
- Machine learning model integration
- Historical data analysis
- Real-time monitoring and alerts
- Integration with flight scheduling systems

