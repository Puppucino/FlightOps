"""
Seed database with cargo flights for calendar and list views
Creates flights that match the mock data structure
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import hashlib

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db_context, init_db
from app.models.flight import Flight
from app.models.airline import Airline
from app.models.aircraft import Aircraft, AircraftType
from app.models.airport import Airport


def get_or_create_airline(db, name: str, iata_code: str = None):
    """Get or create an airline"""
    airline = db.query(Airline).filter(Airline.name == name).first()
    if not airline:
        airline = Airline(
            id=uuid.uuid4(),
            name=name,
            iata_code=iata_code or name[:2].upper(),
            icao_code=name[:3].upper() if len(name) >= 3 else name.upper(),
            country="USA"
        )
        db.add(airline)
        db.flush()
    return airline


def get_or_create_airport(db, iata_code: str, name: str, city: str = None, country: str = "USA"):
    """Get or create an airport"""
    airport = db.query(Airport).filter(Airport.iata_code == iata_code).first()
    if not airport:
        airport = Airport(
            id=uuid.uuid4(),
            iata_code=iata_code,
            icao_code=f"K{iata_code}",
            name=name,
            city=city or name.split()[0],
            country=country
        )
        db.add(airport)
        db.flush()
    return airport


def get_or_create_aircraft_type(db, manufacturer: str, model: str):
    """Get or create an aircraft type"""
    full_name = f"{manufacturer} {model}"
    aircraft_type = db.query(AircraftType).filter(
        AircraftType.manufacturer == manufacturer,
        AircraftType.model == model
    ).first()
    
    if not aircraft_type:
        # Estimate cargo capacity based on aircraft type
        cargo_capacity_map = {
            "Boeing 777-300ER": Decimal("102.5"),
            "Boeing 747-8F": Decimal("120.0"),
            "Airbus A330-200F": Decimal("70.0"),
            "Boeing 737-800": Decimal("20.5"),
            "Airbus A350-900": Decimal("80.0"),
        }
        
        # Generate ICAO code based on aircraft type
        icao_code_map = {
            "Boeing 777-300ER": "B77W",
            "Boeing 747-8F": "B748",
            "Airbus A330-200F": "A33F",
            "Boeing 737-800": "B738",
            "Airbus A350-900": "A359",
        }
        
        cargo_capacity = cargo_capacity_map.get(full_name, Decimal("50.0"))
        icao_code = icao_code_map.get(full_name, "UNKN")
        
        aircraft_type = AircraftType(
            id=uuid.uuid4(),
            icao_code=icao_code,
            manufacturer=manufacturer,
            model=model,
            passenger_capacity=300,
            cargo_capacity_tonnes=cargo_capacity,
            max_range_km=10000
        )
        db.add(aircraft_type)
        db.flush()
    return aircraft_type


def get_or_create_aircraft(db, registration: str, aircraft_type: AircraftType, airline: Airline):
    """Get or create an aircraft"""
    aircraft = db.query(Aircraft).filter(Aircraft.registration == registration).first()
    if not aircraft:
        aircraft = Aircraft(
            id=uuid.uuid4(),
            registration=registration,
            aircraft_type_id=aircraft_type.id,
            airline_id=airline.id,
            is_active=True,
            maintenance_status="operational"
        )
        db.add(aircraft)
        db.flush()
    return aircraft


def seed_cargo_flights():
    """Seed database with cargo flights for the next 3 months"""
    print("Seeding cargo flights database...")
    print("=" * 80)
    
    with get_db_context() as db:
        # Create airline
        airline = get_or_create_airline(db, "American Airlines", "AA")
        print(f"✓ Airline: {airline.name}")
        
        # Create airports
        airports_data = [
            ("JFK", "John F. Kennedy International Airport", "New York"),
            ("LAX", "Los Angeles International Airport", "Los Angeles"),
            ("ORD", "Chicago O'Hare International Airport", "Chicago"),
            ("ATL", "Hartsfield-Jackson Atlanta International Airport", "Atlanta"),
            ("LHR", "London Heathrow Airport", "London"),
            ("HND", "Tokyo Haneda Airport", "Tokyo"),
            ("NRT", "Tokyo Narita Airport", "Tokyo"),
            ("CDG", "Charles de Gaulle Airport", "Paris"),
            ("GRU", "São Paulo-Guarulhos International Airport", "São Paulo"),
            ("ICN", "Incheon International Airport", "Seoul"),
            ("SYD", "Sydney Kingsford Smith Airport", "Sydney"),
            ("DFW", "Dallas/Fort Worth International Airport", "Dallas"),
            ("MIA", "Miami International Airport", "Miami"),
            ("SEA", "Seattle-Tacoma International Airport", "Seattle"),
            ("SFO", "San Francisco International Airport", "San Francisco"),
        ]
        
        airports = {}
        for iata, name, city in airports_data:
            airports[iata] = get_or_create_airport(db, iata, name, city)
            print(f"✓ Airport: {iata} - {name}")
        
        # Create aircraft types
        aircraft_types_data = [
            ("Boeing", "777-300ER"),
            ("Boeing", "747-8F"),
            ("Airbus", "A330-200F"),
            ("Boeing", "737-800"),
            ("Airbus", "A350-900"),
        ]
        
        aircraft_types = {}
        for manufacturer, model in aircraft_types_data:
            full_name = f"{manufacturer} {model}"
            aircraft_types[full_name] = get_or_create_aircraft_type(db, manufacturer, model)
            print(f"✓ Aircraft Type: {full_name}")
        
        # Create aircraft
        aircraft_registrations = [
            ("N123AB", "Boeing 777-300ER"),
            ("N456CD", "Boeing 747-8F"),
            ("N789EF", "Airbus A330-200F"),
            ("N012GH", "Boeing 737-800"),
            ("N345IJ", "Airbus A350-900"),
            ("N678KL", "Boeing 777-300ER"),
            ("N901MN", "Boeing 747-8F"),
            ("N234OP", "Airbus A330-200F"),
        ]
        
        aircraft_list = {}
        for reg, aircraft_type_name in aircraft_registrations:
            aircraft_list[reg] = get_or_create_aircraft(
                db, reg, aircraft_types[aircraft_type_name], airline
            )
            print(f"✓ Aircraft: {reg} ({aircraft_type_name})")
        
        print()
        print("Creating flights...")
        print("-" * 80)
        
        # Flight routes matching mock data
        routes = [
            ("JFK", "LAX", 3984),
            ("ORD", "HND", 10350),
            ("ATL", "LHR", 6780),
            ("LAX", "NRT", 8800),
            ("DFW", "CDG", 8100),
            ("MIA", "GRU", 6800),
            ("SEA", "ICN", 8500),
            ("SFO", "SYD", 12000),
        ]
        
        # Generate flights for the next 3 months
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        flights_created = 0
        
        for month_offset in range(3):
            target_date = today + timedelta(days=30 * month_offset)
            year = target_date.year
            month = target_date.month
            # Calculate days in month properly
            if month == 12:
                days_in_month = 31
            else:
                next_month = target_date.replace(month=month + 1, day=1)
                days_in_month = (next_month - timedelta(days=1)).day
            
            for day in range(1, days_in_month + 1):
                flight_date = datetime(year, month, day, 8, 0)
                # Skip past dates only for the current month
                # For future months, include all days
                if flight_date < today:
                    # Only skip if it's the current month
                    if month == today.month and year == today.year:
                        continue
                    # For past months, skip entirely (don't create flights in the past)
                    elif flight_date < today:
                        continue
                
                date_obj = datetime(year, month, day)
                is_weekend = date_obj.weekday() >= 5
                
                # Determine number of flights per day
                flights_per_day = 4 if is_weekend else 3
                
                for i in range(flights_per_day):
                    route = routes[i % len(routes)]
                    origin_code, dest_code, distance = route
                    
                    # Get aircraft (rotate through available aircraft)
                    aircraft_reg = list(aircraft_list.keys())[i % len(aircraft_list)]
                    aircraft = aircraft_list[aircraft_reg]
                    aircraft_type = aircraft_types[aircraft.aircraft_type.manufacturer + " " + aircraft.aircraft_type.model]
                    
                    # Generate flight number (consistent format)
                    flight_number = f"AA{1000 + flights_created}"
                    
                    # Generate deterministic UUID based on flight details for consistency
                    # This ensures the same flight always gets the same ID when re-running the script
                    hash_input = f"{flight_number}-{flight_date.isoformat()}-{origin_code}-{dest_code}-{i}"
                    hash_bytes = hashlib.md5(hash_input.encode()).digest()
                    # Create UUID from hash (16 bytes from MD5)
                    flight_uuid = uuid.UUID(bytes=hash_bytes[:16])
                    
                    # Check if flight already exists (by flight number and date)
                    existing = db.query(Flight).filter(
                        Flight.flight_number == flight_number,
                        Flight.scheduled_departure == flight_date
                    ).first()
                    
                    if existing:
                        # Ensure existing flight has required fields for calendar query
                        if existing.passenger_count is None or existing.flight_type not in ['passenger', 'mixed', 'cargo']:
                            existing.passenger_count = passenger_count
                            existing.flight_type = "mixed"
                            db.commit()
                        flights_created += 1
                        continue
                    
                    # Calculate passenger count (base + variation)
                    base_passengers = 180 + (i * 20)
                    passenger_count = base_passengers + (10 if is_weekend else 0)
                    
                    # Calculate cargo weight (some percentage of capacity)
                    cargo_capacity = float(aircraft_type.cargo_capacity_tonnes)
                    cargo_weight = Decimal(str(cargo_capacity * (0.4 + (i * 0.1))))
                    
                    # Calculate flight duration (estimate based on distance)
                    hours = distance / 800  # Average speed ~800 km/h
                    scheduled_arrival = flight_date + timedelta(hours=hours)
                    
                    # Create flight with consistent ID
                    flight = Flight(
                        id=flight_uuid,
                        flight_number=flight_number,
                        airline_id=airline.id,
                        aircraft_id=aircraft.id,
                        origin_airport_id=airports[origin_code].id,
                        destination_airport_id=airports[dest_code].id,
                        scheduled_departure=flight_date,
                        scheduled_arrival=scheduled_arrival,
                        flight_type="mixed",
                        passenger_count=passenger_count,
                        cargo_weight_tonnes=cargo_weight,
                        cargo_volume_m3=Decimal(str(float(cargo_weight) * 1.5)),
                        baggage_weight_kg=Decimal(str(passenger_count * 20)),  # ~20kg per passenger
                        baggage_volume_m3=Decimal(str(passenger_count * 0.1)),
                        fuel_weight_kg=Decimal(str((aircraft_type.passenger_capacity or 300) * 50)),
                        distance_km=Decimal(str(distance)),
                        flight_status="scheduled"
                    )
                    
                    db.add(flight)
                    flights_created += 1
                    
                    if flights_created % 50 == 0:
                        print(f"  Created {flights_created} flights...")
        
        db.commit()
        print()
        print(f"✓ Successfully created {flights_created} flights")
        print("=" * 80)
        print("Database seeding complete!")
        print()
        print("Flights are now available in:")
        print("  - Calendar view: /cargo-analytics")
        print("  - List view: /cargo-analytics (switch to list view)")
        print("  - Individual flight analytics: /cargo-analytics/{flight_id}")


if __name__ == "__main__":
    try:
        # Initialize database if needed
        init_db()
        seed_cargo_flights()
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
