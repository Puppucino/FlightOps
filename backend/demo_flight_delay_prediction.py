"""Demo script for Flight Delay Prediction system"""
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from app.domain.entities.flight import Flight
from app.domain.entities.airport import Airport
from app.infrastructure.repositories.in_memory_flight_repository import InMemoryFlightRepository
from app.infrastructure.repositories.in_memory_airport_repository import InMemoryAirportRepository
from app.infrastructure.repositories.in_memory_event_store import InMemoryEventStore
from app.infrastructure.external.aviation_weather_client import AviationWeatherClient
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.application.services.flight_delay_prediction_service import FlightDelayPredictionService


async def demo():
    """Run demo of flight delay prediction system"""
    print("=" * 80)
    print("Flight Delay Prediction System - Demo")
    print("=" * 80)
    print()
    
    # Initialize repositories and services
    print("Initializing repositories and services...")
    flight_repo = InMemoryFlightRepository()
    airport_repo = InMemoryAirportRepository()
    event_store = InMemoryEventStore()
    weather_client = AviationWeatherClient()
    event_bus = InMemoryEventBus()
    
    # Subscribe to events
    def handle_delay_predicted(event):
        print(f"  📊 Event: Delay predicted for flight {event.flight_id}")
        print(f"     Predicted delay: {event.predicted_delay_minutes} minutes")
        print(f"     Confidence: {event.confidence_score:.2%}")
        print(f"     Reason: {event.reason}")
        event_store.append(event)
    
    def handle_weather_received(event):
        print(f"  🌤️  Event: Weather data received for {event.airport_code}")
        event_store.append(event)
    
    def handle_threshold_exceeded(event):
        print(f"  ⚠️  Event: Delay threshold exceeded for flight {event.flight_id}")
        print(f"     Predicted delay: {event.predicted_delay_minutes} minutes")
        print(f"     Threshold: {event.threshold_minutes} minutes")
        event_store.append(event)
    
    event_bus.subscribe("FlightDelayPredicted", handle_delay_predicted)
    event_bus.subscribe("WeatherDataReceived", handle_weather_received)
    event_bus.subscribe("DelayThresholdExceeded", handle_threshold_exceeded)
    
    prediction_service = FlightDelayPredictionService(
        flight_repository=flight_repo,
        airport_repository=airport_repo,
        weather_provider=weather_client,
        event_bus=event_bus
    )
    
    print("✓ Initialization complete")
    print()
    
    # Create sample airports
    print("Creating sample airports...")
    airports = [
        Airport(
            airport_id=uuid4(),
            icao_code="KJFK",
            name="John F. Kennedy International Airport",
            city="New York",
            country="USA"
        ),
        Airport(
            airport_id=uuid4(),
            icao_code="KLAX",
            name="Los Angeles International Airport",
            city="Los Angeles",
            country="USA"
        ),
        Airport(
            airport_id=uuid4(),
            icao_code="KORD",
            name="Chicago O'Hare International Airport",
            city="Chicago",
            country="USA"
        )
    ]
    
    for airport in airports:
        airport_repo.save(airport)
        print(f"  ✓ Created airport: {airport.icao_code} - {airport.name}")
    print()
    
    # Create sample flights
    print("Creating sample flights...")
    now = datetime.now()
    
    flights = [
        Flight(
            flight_id=uuid4(),
            flight_number="AA100",
            departure_airport="KJFK",
            arrival_airport="KLAX",
            scheduled_departure=now + timedelta(minutes=45),  # Departing in 45 minutes
            scheduled_arrival=now + timedelta(hours=6)
        ),
        Flight(
            flight_id=uuid4(),
            flight_number="UA200",
            departure_airport="KORD",
            arrival_airport="KJFK",
            scheduled_departure=now + timedelta(minutes=60),  # Departing in 60 minutes
            scheduled_arrival=now + timedelta(hours=2, minutes=30)
        ),
        Flight(
            flight_id=uuid4(),
            flight_number="DL300",
            departure_airport="KLAX",
            arrival_airport="KORD",
            scheduled_departure=now + timedelta(minutes=90),  # Departing in 90 minutes
            scheduled_arrival=now + timedelta(hours=4)
        )
    ]
    
    for flight in flights:
        flight_repo.save(flight)
        print(f"  ✓ Created flight: {flight.flight_number}")
        print(f"     Route: {flight.departure_airport} → {flight.arrival_airport}")
        print(f"     Scheduled departure: {flight.scheduled_departure.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Request predictions
    print("Requesting delay predictions...")
    print("-" * 80)
    
    for flight in flights:
        print(f"\nFlight {flight.flight_number} ({flight.departure_airport} → {flight.arrival_airport}):")
        print(f"Scheduled departure: {flight.scheduled_departure.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            prediction = await prediction_service.predict_delay(
                flight.flight_id,
                prediction_horizon_minutes=60
            )
            
            print(f"\n📈 Prediction Results:")
            print(f"   Predicted delay: {prediction.predicted_delay_minutes} minutes")
            print(f"   Confidence: {prediction.confidence_score:.2%}")
            print(f"   Weather impact: {prediction.weather_impact_score:.2%}")
            if prediction.reason:
                print(f"   Reason: {prediction.reason}")
            
            if prediction.is_significant_delay(15):
                print(f"   ⚠️  Significant delay predicted (>15 minutes)")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print("-" * 80)
        await asyncio.sleep(1)  # Rate limiting
    
    print()
    
    # Show event history
    print("Event History:")
    print("-" * 80)
    all_events = event_store.get_all_events()
    print(f"Total events recorded: {len(all_events)}")
    
    event_types = {}
    for event in all_events:
        event_type = getattr(event, 'event_type', type(event).__name__)
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")
    
    print()
    print("=" * 80)
    print("Demo complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demo())

