"""Check flight dates in database"""
import sys
from pathlib import Path
from datetime import datetime

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db_context
from app.models.flight import Flight

now = datetime.now()
print(f"Current date/time: {now}")
print("=" * 80)

with get_db_context() as db:
    total = db.query(Flight).count()
    print(f"Total flights: {total}")
    
    future = db.query(Flight).filter(Flight.scheduled_departure >= now).count()
    past = db.query(Flight).filter(Flight.scheduled_departure < now).count()
    
    print(f"Future flights (>= now): {future}")
    print(f"Past flights (< now): {past}")
    
    if future > 0:
        next_flight = db.query(Flight).filter(
            Flight.scheduled_departure >= now
        ).order_by(Flight.scheduled_departure.asc()).first()
        if next_flight:
            print(f"\nNext future flight:")
            print(f"  Number: {next_flight.flight_number}")
            print(f"  Departure: {next_flight.scheduled_departure}")
            print(f"  Type: {next_flight.flight_type}")
            print(f"  Passengers: {next_flight.passenger_count}")
            print(f"  Cargo: {next_flight.cargo_weight_tonnes} tonnes")
    
    if past > 0:
        recent_past = db.query(Flight).filter(
            Flight.scheduled_departure < now
        ).order_by(Flight.scheduled_departure.desc()).first()
        if recent_past:
            print(f"\nMost recent past flight:")
            print(f"  Number: {recent_past.flight_number}")
            print(f"  Departure: {recent_past.scheduled_departure}")
            print(f"  Type: {recent_past.flight_type}")
