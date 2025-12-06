"""
Data loading script to import Google Sheets dataset
Can load from CSV export or directly via Google Sheets API
"""
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Optional
import uuid

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db_context
from app.models import Flight, Airport, Aircraft, AircraftType, Airline
from sqlalchemy import or_
from sqlalchemy.orm import Session


def parse_aircraft_type(aircraft_str: str) -> tuple[str, str]:
    """Parse aircraft type string into manufacturer and model"""
    aircraft_str = aircraft_str.strip()
    
    # Common patterns
    if 'Boeing' in aircraft_str:
        manufacturer = 'Boeing'
        model = aircraft_str.replace('Boeing ', '').strip()
    elif 'Airbus' in aircraft_str:
        manufacturer = 'Airbus'
        model = aircraft_str.replace('Airbus ', '').strip()
    else:
        # Try to infer
        parts = aircraft_str.split()
        if len(parts) > 1:
            manufacturer = parts[0]
            model = ' '.join(parts[1:])
        else:
            manufacturer = 'Unknown'
            model = aircraft_str
    
    return manufacturer, model


def get_or_create_airport(db: Session, iata_code: str, icao_code: Optional[str] = None) -> Airport:
    """Get or create airport by IATA code"""
    airport = db.query(Airport).filter(Airport.iata_code == iata_code).first()
    if not airport:
        airport = Airport(
            id=uuid.uuid4(),
            iata_code=iata_code,
            icao_code=icao_code or iata_code,
            name=f"{iata_code} Airport",
            city=iata_code,
            country="Unknown",
            is_active=True
        )
        db.add(airport)
        db.flush()
    return airport


def get_or_create_airline(db: Session, name: str = "Airline AB") -> Airline:
    """Get or create default airline"""
    airline = db.query(Airline).filter(Airline.name == name).first()
    if not airline:
        airline = Airline(
            id=uuid.uuid4(),
            name=name,
            iata_code="AB",
            icao_code="AB",
            is_active=True
        )
        db.add(airline)
        db.flush()
    return airline


def get_or_create_aircraft_type(db: Session, aircraft_str: str) -> AircraftType:
    """Get or create aircraft type"""
    manufacturer, model = parse_aircraft_type(aircraft_str)
    
    # First check if it already exists
    aircraft_type = db.query(AircraftType).filter(
        AircraftType.manufacturer == manufacturer,
        AircraftType.model == model
    ).first()
    
    if not aircraft_type:
        # Create unique ICAO code using standard ICAO format
        # e.g., "737-800" -> "B738", "A330-200" -> "A332", "A330-300" -> "A333"
        model_clean = model.replace('-', '').replace(' ', '').upper()
        
        # Special handling for common aircraft types to use standard ICAO codes
        icao_code_map = {
            '737-800': 'B738',
            '737-900ER': 'B739',
            'A330-200': 'A332',
            'A330-300': 'A333',
        }
        
        if model in icao_code_map:
            icao_code = icao_code_map[model]
        else:
            # Generate from model name
            if manufacturer.upper() == 'BOEING':
                prefix = 'B'
            elif manufacturer.upper() == 'AIRBUS':
                prefix = 'A'
            else:
                prefix = manufacturer[0].upper() if manufacturer else 'X'
            
            # Extract model numbers (digits and letters)
            model_num = ''.join(c for c in model_clean if c.isdigit())[:3]
            if not model_num:
                model_num = model_clean[:3]
            icao_code = (prefix + model_num).ljust(4, '0')[:4]
        
        # Check if ICAO code already exists, if so, try variations
        original_icao = icao_code
        counter = 1
        while db.query(AircraftType).filter(AircraftType.icao_code == icao_code).first():
            # Try variations: modify last character
            if counter < 10:
                icao_code = original_icao[:3] + str(counter)
            else:
                # Use hash-based fallback
                icao_code = original_icao[:3] + chr(65 + (counter % 26))  # A-Z
            counter += 1
            if counter > 50:  # Safety limit
                # Final fallback: use model hash
                icao_code = original_icao[:2] + str(abs(hash(model)) % 100)[:2]
                break
        # Estimate capacity based on aircraft type
        capacity_map = {
            '737-800': {'passenger': 162, 'cargo': 20.5},
            '737-900ER': {'passenger': 180, 'cargo': 24.0},
            'A330-200': {'passenger': 250, 'cargo': 19.7},
            'A330-300': {'passenger': 290, 'cargo': 19.7},
        }
        
        capacity = capacity_map.get(model, {'passenger': 200, 'cargo': 20.0})
        
        aircraft_type = AircraftType(
            id=uuid.uuid4(),
            icao_code=icao_code,
            manufacturer=manufacturer,
            model=model,
            passenger_capacity=capacity['passenger'],
            cargo_capacity_tonnes=capacity['cargo'],
            is_active=True
        )
        db.add(aircraft_type)
        db.flush()
    
    return aircraft_type


def get_or_create_aircraft(db: Session, tail_number: str, aircraft_type: AircraftType, airline: Airline) -> Aircraft:
    """Get or create aircraft by tail number"""
    aircraft = db.query(Aircraft).filter(Aircraft.registration == tail_number).first()
    if not aircraft:
        aircraft = Aircraft(
            id=uuid.uuid4(),
            registration=tail_number,
            aircraft_type_id=aircraft_type.id,
            airline_id=airline.id,
            is_active=True
        )
        db.add(aircraft)
        db.flush()
    return aircraft


def load_data_from_csv(file_path: str, limit: Optional[int] = None) -> None:
    """
    Load flight data from CSV file exported from Google Sheets
    
    Expected columns:
    - flight_number, flight_date, origin, destination, tail_number, aircraft_type
    - gross_weight_cargo_kg, gross_volume_cargo_m3
    - passenger_count, baggage_weight_kg
    - fuel_weight_kg, fuel_price_per_kg, cargo_price_per_kg
    """
    print(f"Loading data from: {file_path}")
    
    # Read CSV
    df = pd.read_csv(file_path)
    
    if limit:
        df = df.head(limit)
    
    print(f"Found {len(df)} records to import")
    
    with get_db_context() as db:
        # Get or create default airline
        airline = get_or_create_airline(db)
        
        imported = 0
        skipped = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                # Parse flight date
                flight_date = pd.to_datetime(row['flight_date']).to_pydatetime()
                
                # Get or create airports
                origin_airport = get_or_create_airport(db, row['origin'])
                dest_airport = get_or_create_airport(db, row['destination'])
                
                # Get or create aircraft type
                aircraft_type = get_or_create_aircraft_type(db, row['aircraft_type'])
                
                # Get or create aircraft
                aircraft = get_or_create_aircraft(db, row['tail_number'], aircraft_type, airline)
                
                # Check if flight already exists
                existing = db.query(Flight).filter(
                    Flight.flight_number == row['flight_number'],
                    Flight.scheduled_departure == flight_date
                ).first()
                
                if existing:
                    # Update existing flight with baggage and cargo data
                    existing.passenger_count = int(row['passenger_count']) if pd.notna(row['passenger_count']) else None
                    existing.cargo_weight_tonnes = float(row['gross_weight_cargo_kg']) / 1000.0 if pd.notna(row['gross_weight_cargo_kg']) else None
                    existing.cargo_volume_m3 = float(row['gross_volume_cargo_m3']) if pd.notna(row['gross_volume_cargo_m3']) else None
                    existing.baggage_weight_kg = float(row['baggage_weight_kg']) if pd.notna(row['baggage_weight_kg']) else None
                    existing.fuel_weight_kg = float(row['fuel_weight_kg']) if pd.notna(row['fuel_weight_kg']) else None
                    existing.fuel_price_per_kg = float(row['fuel_price_per_kg']) if pd.notna(row['fuel_price_per_kg']) else None
                    existing.cargo_price_per_kg = float(row['cargo_price_per_kg']) if pd.notna(row['cargo_price_per_kg']) else None
                    
                    # Estimate baggage volume if not provided (approximate: 1 kg = 0.015 m³)
                    if pd.notna(row['baggage_weight_kg']) and not existing.baggage_volume_m3:
                        existing.baggage_volume_m3 = float(row['baggage_weight_kg']) * 0.015
                    
                    imported += 1
                else:
                    # Calculate distance (rough estimate - would need actual coordinates)
                    distance = 1000.0  # Default, should be calculated from airport coordinates
                    
                    # Create new flight
                    flight = Flight(
                        id=uuid.uuid4(),
                        flight_number=row['flight_number'],
                        airline_id=airline.id,
                        aircraft_id=aircraft.id,
                        origin_airport_id=origin_airport.id,
                        destination_airport_id=dest_airport.id,
                        scheduled_departure=flight_date,
                        scheduled_arrival=flight_date,  # Should be calculated based on route
                        flight_type='mixed',
                        passenger_count=int(row['passenger_count']) if pd.notna(row['passenger_count']) else None,
                        cargo_weight_tonnes=float(row['gross_weight_cargo_kg']) / 1000.0 if pd.notna(row['gross_weight_cargo_kg']) else None,
                        cargo_volume_m3=float(row['gross_volume_cargo_m3']) if pd.notna(row['gross_volume_cargo_m3']) else None,
                        baggage_weight_kg=float(row['baggage_weight_kg']) if pd.notna(row['baggage_weight_kg']) else None,
                        fuel_weight_kg=float(row['fuel_weight_kg']) if pd.notna(row['fuel_weight_kg']) else None,
                        fuel_price_per_kg=float(row['fuel_price_per_kg']) if pd.notna(row['fuel_price_per_kg']) else None,
                        cargo_price_per_kg=float(row['cargo_price_per_kg']) if pd.notna(row['cargo_price_per_kg']) else None,
                        distance_km=distance,
                        flight_status='arrived'
                    )
                    
                    # Estimate baggage volume if not provided
                    if pd.notna(row['baggage_weight_kg']) and not flight.baggage_volume_m3:
                        flight.baggage_volume_m3 = float(row['baggage_weight_kg']) * 0.015
                    
                    db.add(flight)
                    imported += 1
                
                if (idx + 1) % 100 == 0:
                    print(f"Processed {idx + 1}/{len(df)} records...")
                    # Commit periodically to avoid large transactions
                    db.commit()
                    
            except Exception as e:
                error_count += 1
                db.rollback()
                error_msg = str(e)
                print(f"Error processing row {idx + 1}: {error_msg[:150]}")
                if error_count <= 3:  # Show first 3 errors in detail
                    import traceback
                    tb_lines = traceback.format_exc().split('\n')[:5]  # First 5 lines
                    print(f"  Traceback: {' | '.join(tb_lines)}")
                skipped += 1
                continue
        
        # Final commit
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"⚠️  Final commit error: {e}")
        
        print(f"\n✓ Import complete!")
        print(f"  - Imported/Updated: {imported}")
        print(f"  - Skipped: {skipped}")


def load_data_from_url(url: str, limit: Optional[int] = None) -> None:
    """
    Load data from Google Sheets URL (CSV export format)
    
    Example URL format:
    https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}
    """
    # Convert Google Sheets URL to CSV export URL
    if '/edit' in url:
        # Extract sheet ID
        sheet_id = url.split('/d/')[1].split('/')[0]
        gid = '0'  # Default to first sheet
        if '#gid=' in url:
            gid = url.split('#gid=')[1]
        
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        print(f"Exporting from Google Sheets: {csv_url}")
        load_data_from_csv(csv_url, limit)
    else:
        # Assume it's already a CSV URL
        load_data_from_csv(url, limit)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load flight data from Google Sheets or CSV")
    parser.add_argument("source", help="CSV file path or Google Sheets URL")
    parser.add_argument("--limit", type=int, help="Limit number of records to import")
    
    args = parser.parse_args()
    
    try:
        if args.source.startswith("http"):
            load_data_from_url(args.source, args.limit)
        else:
            load_data_from_csv(args.source, args.limit)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
