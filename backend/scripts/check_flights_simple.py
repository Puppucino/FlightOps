"""Simple script to check flights"""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db_context
from app.models.flight import Flight

with get_db_context() as db:
    count = db.query(Flight).count()
    print(f"Total flights: {count}")
    
    if count > 0:
        flight = db.query(Flight).first()
        print(f"Sample flight: {flight.flight_number}")
        print(f"  Cargo weight: {flight.cargo_weight_tonnes}")
        print(f"  Passengers: {flight.passenger_count}")
        print(f"  Type: {flight.flight_type}")
