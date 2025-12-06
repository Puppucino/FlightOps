"""
Verify that seeded flights exist and have cargo data
"""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db_context
from app.models.flight import Flight
from app.models.aircraft import Aircraft, AircraftType
from app.models.airport import Airport
from app.models.airline import Airline
from app.models.prediction import CargoPrediction


def verify_cargo_flights():
    """Verify flights exist and have cargo data"""
    import sys
    sys.stdout.flush()
    print("Verifying cargo flights in database...")
    print("=" * 80)
    sys.stdout.flush()
    
    with get_db_context() as db:
        # Count total flights
        total_flights = db.query(Flight).count()
        print(f"✓ Total flights in database: {total_flights}")
        
        # Count flights with cargo data
        flights_with_cargo = db.query(Flight).filter(
            Flight.cargo_weight_tonnes.isnot(None)
        ).count()
        print(f"✓ Flights with cargo_weight_tonnes: {flights_with_cargo}")
        
        flights_with_passengers = db.query(Flight).filter(
            Flight.passenger_count.isnot(None)
        ).count()
        print(f"✓ Flights with passenger_count: {flights_with_passengers}")
        
        # Count by flight type
        flight_types = db.query(Flight.flight_type, db.func.count(Flight.id)).group_by(Flight.flight_type).all()
        print(f"\nFlight types breakdown:")
        for flight_type, count in flight_types:
            print(f"  - {flight_type}: {count}")
        
        # Get sample flights
        print(f"\nSample flights (first 10):")
        print("-" * 80)
        sample_flights = db.query(Flight).order_by(Flight.scheduled_departure).limit(10).all()
        
        for flight in sample_flights:
            # Get related data
            origin = db.query(Airport).filter(Airport.id == flight.origin_airport_id).first()
            dest = db.query(Airport).filter(Airport.id == flight.destination_airport_id).first()
            aircraft = db.query(Aircraft).filter(Aircraft.id == flight.aircraft_id).first()
            airline = db.query(Airline).filter(Airline.id == flight.airline_id).first()
            
            aircraft_type_str = "Unknown"
            if aircraft:
                aircraft_type = db.query(AircraftType).filter(AircraftType.id == aircraft.aircraft_type_id).first()
                if aircraft_type:
                    aircraft_type_str = f"{aircraft_type.manufacturer} {aircraft_type.model}"
            
            print(f"\n  Flight: {flight.flight_number}")
            print(f"    ID: {flight.id}")
            print(f"    Airline: {airline.name if airline else 'N/A'}")
            print(f"    Route: {origin.iata_code if origin else 'N/A'} → {dest.iata_code if dest else 'N/A'}")
            print(f"    Aircraft: {aircraft.registration if aircraft else 'N/A'} ({aircraft_type_str})")
            print(f"    Departure: {flight.scheduled_departure}")
            print(f"    Type: {flight.flight_type}")
            print(f"    Passengers: {flight.passenger_count or 'N/A'}")
            print(f"    Cargo Weight: {float(flight.cargo_weight_tonnes) if flight.cargo_weight_tonnes else 'N/A'} tonnes")
            print(f"    Cargo Volume: {float(flight.cargo_volume_m3) if flight.cargo_volume_m3 else 'N/A'} m³")
            print(f"    Baggage Weight: {float(flight.baggage_weight_kg) if flight.baggage_weight_kg else 'N/A'} kg")
            print(f"    Distance: {float(flight.distance_km) if flight.distance_km else 'N/A'} km")
            print(f"    Status: {flight.flight_status or 'N/A'}")
        
        # Check cargo predictions
        print(f"\n" + "=" * 80)
        cargo_predictions_count = db.query(CargoPrediction).count()
        print(f"Cargo Predictions in database: {cargo_predictions_count}")
        
        if cargo_predictions_count > 0:
            print(f"\nSample cargo predictions (first 5):")
            print("-" * 80)
            sample_predictions = db.query(CargoPrediction).limit(5).all()
            for pred in sample_predictions:
                airport = db.query(Airport).filter(Airport.id == pred.airport_id).first()
                aircraft = db.query(Aircraft).filter(Aircraft.id == pred.aircraft_id).first() if pred.aircraft_id else None
                print(f"  Prediction ID: {pred.id}")
                print(f"    Airport: {airport.iata_code if airport else 'N/A'}")
                print(f"    Aircraft: {aircraft.registration if aircraft else 'N/A'}")
                print(f"    Predicted Cargo: {float(pred.predicted_cargo_tonnes)} tonnes")
                print(f"    Confidence: {float(pred.confidence_score) if pred.confidence_score else 'N/A'}")
                print(f"    Timestamp: {pred.prediction_timestamp}")
        else:
            print("  ⚠ No cargo predictions found (this is normal - predictions are generated on-demand)")
        
        # Check flights for current month
        today = datetime.now()
        current_month_start = datetime(today.year, today.month, 1)
        if today.month == 12:
            next_month_start = datetime(today.year + 1, 1, 1)
        else:
            next_month_start = datetime(today.year, today.month + 1, 1)
        
        current_month_flights = db.query(Flight).filter(
            Flight.scheduled_departure >= current_month_start,
            Flight.scheduled_departure < next_month_start
        ).count()
        
        print(f"\n" + "=" * 80)
        print(f"Flights in current month ({today.strftime('%B %Y')}): {current_month_flights}")
        
        # Summary
        print(f"\n" + "=" * 80)
        print("SUMMARY:")
        print(f"  ✓ Total flights: {total_flights}")
        print(f"  ✓ Flights with cargo data: {flights_with_cargo}")
        print(f"  ✓ Flights with passenger data: {flights_with_passengers}")
        print(f"  ✓ Current month flights: {current_month_flights}")
        print(f"  ✓ Cargo predictions: {cargo_predictions_count}")
        
        if total_flights > 0 and flights_with_cargo > 0:
            print(f"\n✅ SUCCESS: Flights exist and have cargo data!")
        elif total_flights > 0:
            print(f"\n⚠ WARNING: Flights exist but some may be missing cargo data")
        else:
            print(f"\n❌ ERROR: No flights found in database")
        
        print("=" * 80)


if __name__ == "__main__":
    try:
        verify_cargo_flights()
    except Exception as e:
        print(f"✗ Error verifying database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
