"""Test the calendar endpoint to see what it returns"""
import sys
import json
from pathlib import Path
from datetime import datetime, date

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db_context
from app.models.flight import Flight
from app.api.v1.cargo_routes import get_cargo_calendar
from app.services.ml_service import MLService
from app.core.database import SessionLocal

# Test December 2025
year = 2025
month = 12

print(f"Testing calendar endpoint for {year}-{month}")
print("=" * 80)

# First check if flights exist
with get_db_context() as db:
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.min.time())
    
    flights = db.query(Flight).filter(
        Flight.scheduled_departure >= start_datetime,
        Flight.scheduled_departure < end_datetime,
        Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
        Flight.passenger_count.isnot(None)
    ).order_by(Flight.scheduled_departure.asc()).all()
    
    print(f"\nDirect query found {len(flights)} flights")
    if flights:
        print("Sample flights:")
        for f in flights[:5]:
            print(f"  {f.flight_number}: {f.scheduled_departure} (date: {f.scheduled_departure.date()})")
    else:
        # Check what flights exist
        all_flights = db.query(Flight).filter(
            Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
            Flight.passenger_count.isnot(None)
        ).order_by(Flight.scheduled_departure.asc()).limit(10).all()
        print(f"\nTotal flights in database: {len(all_flights)}")
        if all_flights:
            print("Sample flights (all dates):")
            for f in all_flights[:10]:
                print(f"  {f.flight_number}: {f.scheduled_departure} (date: {f.scheduled_departure.date()})")

# Now test the actual endpoint
print("\n" + "=" * 80)
print("Testing endpoint response...")
try:
    db = SessionLocal()
    ml_service = MLService()
    response = get_cargo_calendar(year=year, month=month, db=db, ml_service=ml_service)
    
    print(f"\nResponse structure:")
    print(f"  Year: {response['year']}")
    print(f"  Month: {response['month']}")
    print(f"  Peak seasons: {len(response['peak_seasons'])}")
    print(f"  Flights: {len(response['flights'])}")
    
    if response['flights']:
        print("\nSample flight data:")
        for f in response['flights'][:3]:
            print(f"  Flight {f['flight_number']}:")
            print(f"    date: {f['date']}")
            print(f"    scheduled_departure: {f['scheduled_departure']}")
            print(f"    origin: {f['origin']}")
            print(f"    destination: {f['destination']}")
    else:
        print("\n⚠️ No flights in response!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
