"""
Load flights_weather_2019_cleaned.csv into the database
Maps CSV columns to Flight model and related tables
"""
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, time
from typing import Optional
import uuid

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db_context
from app.models.flight import Flight
from app.models.airport import Airport
from app.models.aircraft import Aircraft, AircraftType
from app.models.airline import Airline
from sqlalchemy.orm import Session


def parse_time(time_str):
    """Parse time string (HHMM format) to time object"""
    if pd.isna(time_str):
        return None
    time_str = str(int(time_str)).zfill(4)  # Ensure 4 digits
    if len(time_str) == 4:
        return time(int(time_str[:2]), int(time_str[2:]))
    return None


def get_or_create_airport(db: Session, iata_code: str, icao_code: Optional[str] = None, name: Optional[str] = None) -> Airport:
    """Get or create airport"""
    if not iata_code or pd.isna(iata_code):
        return None
    
    airport = db.query(Airport).filter(Airport.iata_code == iata_code.upper()).first()
    if not airport:
        airport = Airport(
            id=uuid.uuid4(),
            iata_code=iata_code.upper(),
            icao_code=icao_code.upper() if icao_code and not pd.isna(icao_code) else None,
            name=name or f"{iata_code} Airport",
            country="US",  # Default, can be updated
            city="Unknown"
        )
        db.add(airport)
        db.flush()
    return airport


def get_or_create_airline(db: Session, carrier_code: str, airline_name: Optional[str] = None) -> Airline:
    """Get or create airline"""
    if not carrier_code or pd.isna(carrier_code):
        carrier_code = "UNKNOWN"
    
    airline = db.query(Airline).filter(Airline.iata_code == carrier_code.upper()).first()
    if not airline:
        airline = Airline(
            id=uuid.uuid4(),
            iata_code=carrier_code.upper(),
            icao_code=carrier_code.upper(),
            name=airline_name or f"{carrier_code} Airlines",
            country="US"
        )
        db.add(airline)
        db.flush()
    return airline


def get_or_create_aircraft_type(db: Session, tail_num: str) -> AircraftType:
    """Get or create a default aircraft type based on tail number"""
    # Try to infer aircraft type from tail number or use default
    # This is a simplified approach - in production, you'd have a lookup table
    default_type = db.query(AircraftType).filter(
        AircraftType.manufacturer == "Boeing",
        AircraftType.model == "737-800"
    ).first()
    
    if not default_type:
        default_type = AircraftType(
            id=uuid.uuid4(),
            manufacturer="Boeing",
            model="737-800",
            iata_code="B738",
            icao_code="B738",
            passenger_capacity=175,
            cargo_capacity_tonnes=15.0,
            max_takeoff_weight_kg=79000,
            max_landing_weight_kg=66300
        )
        db.add(default_type)
        db.flush()
    
    return default_type


def get_or_create_aircraft(db: Session, tail_num: str, aircraft_type: AircraftType, airline: Airline) -> Aircraft:
    """Get or create aircraft"""
    if not tail_num or pd.isna(tail_num):
        tail_num = f"UNKNOWN-{uuid.uuid4().hex[:6]}"
    
    aircraft = db.query(Aircraft).filter(Aircraft.registration == tail_num.upper()).first()
    if not aircraft:
        aircraft = Aircraft(
            id=uuid.uuid4(),
            registration=tail_num.upper(),
            aircraft_type_id=aircraft_type.id,
            airline_id=airline.id
        )
        db.add(aircraft)
        db.flush()
    return aircraft


def load_flights_from_csv(csv_path: str, limit: Optional[int] = None, batch_size: int = 1000):
    """
    Load flight data from flights_weather_2019_cleaned.csv
    
    Args:
        csv_path: Path to CSV file
        limit: Maximum number of records to import (None for all)
        batch_size: Number of records to process before committing
    """
    print(f"Loading data from: {csv_path}")
    
    # Read CSV in chunks for memory efficiency
    chunk_size = 10000
    total_imported = 0
    total_skipped = 0
    total_errors = 0
    
    with get_db_context() as db:
        for chunk_df in pd.read_csv(csv_path, chunksize=chunk_size):
            if limit and total_imported >= limit:
                break
            
            imported = 0
            skipped = 0
            errors = 0
            
            for idx, row in chunk_df.iterrows():
                if limit and total_imported >= limit:
                    break
                
                try:
                    # Parse date
                    flight_date = pd.to_datetime(row['Date']).date()
                    
                    # Parse times
                    dep_time = parse_time(row.get('DepTime'))
                    arr_time = parse_time(row.get('ArrTime'))
                    crs_arr_time = parse_time(row.get('CRSArrTime'))
                    
                    # Create datetime objects
                    scheduled_departure = datetime.combine(flight_date, dep_time) if dep_time else None
                    scheduled_arrival = datetime.combine(flight_date, arr_time) if arr_time else None
                    
                    # If arrival time is next day (arrival time < departure time), add a day
                    if scheduled_departure and scheduled_arrival and scheduled_arrival < scheduled_departure:
                        from datetime import timedelta
                        scheduled_arrival += timedelta(days=1)
                    
                    # Use CRSArrTime if ArrTime is missing
                    if not scheduled_arrival and crs_arr_time:
                        scheduled_arrival = datetime.combine(flight_date, crs_arr_time)
                        if scheduled_departure and scheduled_arrival < scheduled_departure:
                            scheduled_arrival += timedelta(days=1)
                    
                    if not scheduled_departure:
                        skipped += 1
                        continue
                    
                    # Get or create airports
                    origin_airport = get_or_create_airport(
                        db, 
                        row.get('Origin'),
                        row.get('ICAO'),
                        row.get('Org_Airport')
                    )
                    dest_airport = get_or_create_airport(
                        db,
                        row.get('Dest'),
                        None,  # CSV doesn't have dest ICAO
                        row.get('Dest_Airport')
                    )
                    
                    if not origin_airport or not dest_airport:
                        skipped += 1
                        continue
                    
                    # Get or create airline
                    carrier_code = row.get('UniqueCarrier', 'UNKNOWN')
                    airline_name = row.get('Airline', None)
                    airline = get_or_create_airline(db, carrier_code, airline_name)
                    
                    # Get or create aircraft type and aircraft
                    tail_num = row.get('TailNum', None)
                    aircraft_type = get_or_create_aircraft_type(db, tail_num)
                    aircraft = get_or_create_aircraft(db, tail_num, aircraft_type, airline)
                    
                    # Check if flight already exists
                    flight_number = f"{carrier_code}{int(row.get('FlightNum', 0))}"
                    existing = db.query(Flight).filter(
                        Flight.flight_number == flight_number,
                        Flight.scheduled_departure == scheduled_departure
                    ).first()
                    
                    if existing:
                        # Update existing flight
                        existing.arrival_delay_minutes = int(row.get('ArrDelay', 0)) if not pd.isna(row.get('ArrDelay')) else None
                        existing.departure_delay_minutes = int(row.get('DepDelay', 0)) if not pd.isna(row.get('DepDelay')) else None
                        existing.distance_km = float(row.get('Distance', 0)) if not pd.isna(row.get('Distance')) else None
                        existing.cancellation_status = 'C' if row.get('Cancelled') == 1 else None
                        existing.flight_status = 'cancelled' if row.get('Cancelled') == 1 else 'arrived'
                        if scheduled_arrival:
                            existing.actual_arrival = scheduled_arrival
                        if scheduled_departure:
                            existing.actual_departure = scheduled_departure
                        imported += 1
                    else:
                        # Create new flight
                        flight = Flight(
                            id=uuid.uuid4(),
                            flight_number=flight_number,
                            airline_id=airline.id,
                            aircraft_id=aircraft.id,
                            origin_airport_id=origin_airport.id,
                            destination_airport_id=dest_airport.id,
                            scheduled_departure=scheduled_departure,
                            scheduled_arrival=scheduled_arrival or scheduled_departure,  # Fallback
                            actual_departure=scheduled_departure,
                            actual_arrival=scheduled_arrival,
                            departure_delay_minutes=int(row.get('DepDelay', 0)) if not pd.isna(row.get('DepDelay')) else None,
                            arrival_delay_minutes=int(row.get('ArrDelay', 0)) if not pd.isna(row.get('ArrDelay')) else None,
                            cancellation_status='C' if row.get('Cancelled') == 1 else None,
                            flight_type='passenger',  # Default, can be updated
                            flight_status='cancelled' if row.get('Cancelled') == 1 else 'arrived',
                            distance_km=float(row.get('Distance', 0)) if not pd.isna(row.get('Distance')) else None
                        )
                        db.add(flight)
                        imported += 1
                    
                    # Commit in batches
                    if (imported + skipped) % batch_size == 0:
                        db.commit()
                        print(f"Processed {total_imported + imported + total_skipped + skipped} records...")
                
                except Exception as e:
                    errors += 1
                    db.rollback()
                    if errors <= 5:  # Show first 5 errors
                        print(f"Error processing row {idx + 1}: {str(e)[:150]}")
                    continue
            
            # Commit remaining records
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"⚠️  Commit error: {e}")
            
            total_imported += imported
            total_skipped += skipped
            total_errors += errors
            
            print(f"Chunk complete: Imported {imported}, Skipped {skipped}, Errors {errors}")
            print(f"Total: Imported {total_imported}, Skipped {total_skipped}, Errors {total_errors}")
    
    print(f"\n✓ Import complete!")
    print(f"  - Imported/Updated: {total_imported}")
    print(f"  - Skipped: {total_skipped}")
    print(f"  - Errors: {total_errors}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load flights_weather_2019_cleaned.csv into database")
    parser.add_argument("csv_path", help="Path to flights_weather_2019_cleaned.csv")
    parser.add_argument("--limit", type=int, help="Limit number of records to import")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for commits")
    
    args = parser.parse_args()
    
    try:
        load_flights_from_csv(args.csv_path, args.limit, args.batch_size)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
