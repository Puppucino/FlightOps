# Database Seeding Script

This script seeds the database with cargo flights for testing the calendar and list views.

## Usage

1. Make sure your virtual environment is activated:
   ```bash
   # Windows
   venv\Scripts\activate.bat
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. Run the seed script:
   ```bash
   python backend/scripts/seed_cargo_flights.py
   ```

## What it does

- Creates an airline (American Airlines)
- Creates 15 airports (JFK, LAX, ORD, ATL, LHR, HND, NRT, CDG, GRU, ICN, SYD, DFW, MIA, SEA, SFO)
- Creates 5 aircraft types (Boeing 777-300ER, 747-8F, 737-800, Airbus A330-200F, A350-900)
- Creates 8 aircraft with registrations
- Generates flights for the next 3 months:
  - 3 flights per weekday
  - 4 flights per weekend day
  - Flights are distributed across 8 different routes
  - Each flight has passenger count, cargo weight, and other required data

## Flight Data

Flights are created with:
- Consistent flight numbers (AA1000, AA1001, etc.)
- Deterministic UUIDs based on flight details (same flight = same ID)
- Passenger counts (180-280 range)
- Cargo weights (based on aircraft capacity)
- Proper relationships to airlines, aircraft, and airports

## After Seeding

After running the script, you can:
- View flights in the calendar: `/cargo-analytics` (Calendar View)
- View flights in the list: `/cargo-analytics` (List View)
- Click any flight to see detailed analytics: `/cargo-analytics/{flight_id}`

## Notes

- The script uses deterministic UUIDs so running it multiple times won't create duplicates
- Flights are created for future dates only (not in the past)
- Each flight has all required data for cargo analytics predictions
