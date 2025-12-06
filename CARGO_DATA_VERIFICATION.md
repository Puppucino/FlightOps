# Cargo Data Verification Guide

## Database Structure

### Flights Table (Primary Cargo Data)
The `flights` table contains cargo data directly in these columns:
- `cargo_weight_tonnes` - Actual cargo weight in tonnes
- `cargo_volume_m3` - Actual cargo volume in cubic meters
- `baggage_weight_kg` - Passenger baggage weight
- `baggage_volume_m3` - Passenger baggage volume
- `passenger_count` - Number of passengers
- `flight_type` - 'passenger', 'cargo', or 'mixed'

**The seeded flights should already have cargo data in these fields.**

### Cargo Predictions Table (ML Predictions)
The `cargo_predictions` table stores ML model predictions:
- Linked to `airport_id` and `aircraft_id` (not directly to `flight_id`)
- Used for predictive analytics
- Generated on-demand when making predictions

## How to Verify

### Option 1: Use the Verification Script
```bash
cd backend/scripts
python verify_cargo_flights.py
```

This will show:
- Total flights count
- Flights with cargo data
- Sample flights with their cargo information
- Cargo predictions count

### Option 2: Check via API
Start your backend server and check:
```bash
# Get all cargo flights
curl http://localhost:8000/api/v1/flights/cargo

# Get calendar view (includes cargo predictions)
curl http://localhost:8000/api/v1/cargo/calendar?year=2024&month=12
```

### Option 3: Direct Database Query
If you have SQLite browser or command line:
```sql
-- Count flights with cargo data
SELECT COUNT(*) FROM flights WHERE cargo_weight_tonnes IS NOT NULL;

-- View sample flights
SELECT 
    flight_number,
    flight_type,
    passenger_count,
    cargo_weight_tonnes,
    cargo_volume_m3,
    scheduled_departure
FROM flights
ORDER BY scheduled_departure
LIMIT 10;
```

## Expected Results After Seeding

After running `seed_cargo_flights.py`, you should have:

1. **Flights Table:**
   - ~270 flights (3 months × ~30 days × 3-4 flights/day)
   - All flights should have:
     - `cargo_weight_tonnes` populated
     - `cargo_volume_m3` populated
     - `passenger_count` populated
     - `baggage_weight_kg` populated
     - `flight_type` = 'mixed'

2. **Related Tables:**
   - 1 airline (American Airlines)
   - 15 airports
   - 5 aircraft types
   - 8 aircraft

3. **Cargo Predictions:**
   - Initially 0 (generated on-demand via API)
   - Created when calling `/api/v1/cargo/calendar` or prediction endpoints

## Integration Points

### Calendar View
- Uses `/api/v1/cargo/calendar` endpoint
- Fetches flights from `flights` table
- Generates cargo predictions on-the-fly using ML service
- Returns flights with `cargo_prediction` data

### List View
- Uses `/api/v1/flights/cargo` endpoint
- Returns flights directly from `flights` table
- Shows actual cargo data from database

### Analytics View
- Uses flight ID to fetch specific flight
- Can generate predictions for that flight
- Shows both actual and predicted cargo data

## Troubleshooting

### If flights don't have cargo data:
1. Check the seed script ran successfully
2. Verify `cargo_weight_tonnes` is not NULL in database
3. Re-run seed script if needed

### If calendar view shows no flights:
1. Check backend is running
2. Verify flights exist in database
3. Check API endpoint: `GET /api/v1/cargo/calendar`
4. Ensure flights are in the requested month/year

### If predictions aren't working:
1. Check ML models are loaded (check backend logs)
2. Verify aircraft types exist
3. Check API endpoint returns predictions

## Quick Check Commands

```bash
# Check if flights exist
cd backend
python -c "from app.core.database import get_db_context; from app.models.flight import Flight; db = next(get_db_context()); print(f'Flights: {db.query(Flight).count()}')"

# Check flights with cargo
python -c "from app.core.database import get_db_context; from app.models.flight import Flight; db = next(get_db_context()); print(f'With cargo: {db.query(Flight).filter(Flight.cargo_weight_tonnes.isnot(None)).count()}')"
```
