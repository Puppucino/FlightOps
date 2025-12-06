# Fix: Calendar Showing No Flights

## Problem
Backend logs show: `Calendar endpoint: Found 0 flights for 2025-12`
Frontend shows: `flightsCount: 0` for December 2025

## Root Cause
The database has no flights matching the query criteria:
- `scheduled_departure >= 2025-12-01` and `< 2026-01-01`
- `flight_type IN ('passenger', 'mixed', 'cargo')`
- `passenger_count IS NOT NULL`

## Solution Applied

### 1. Updated Auto-Navigation Logic
Changed from only working for default (current month) to working for **any month**:
```python
# Before: Only auto-navigate if no year/month specified
if len(flights) == 0 and not year and not month:

# After: Auto-navigate for any empty month
if len(flights) == 0:
```

### 2. Updated Seed Script
Ensures existing flights have required fields:
- If flight exists but missing `passenger_count` or wrong `flight_type`, update it
- This fixes flights that were created without proper criteria

### 3. Next Steps

**Option A: Re-run Seed Script**
```bash
cd backend
python scripts/seed_cargo_flights.py
```

**Option B: Check Database**
Verify flights exist and have correct fields:
```python
from app.core.database import SessionLocal
from app.models.flight import Flight
from datetime import datetime

db = SessionLocal()
flights = db.query(Flight).filter(
    Flight.scheduled_departure >= datetime(2025, 12, 1),
    Flight.scheduled_departure < datetime(2026, 1, 1),
    Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
    Flight.passenger_count.isnot(None)
).all()
print(f"Found {len(flights)} flights")
```

**Option C: Force Create Flights**
If seed script isn't working, manually verify and create flights for December 2025.

## Expected Behavior After Fix

1. **If December 2025 has flights**: Calendar shows them
2. **If December 2025 has no flights**: Auto-navigate to first month with flights
3. **Backend logs show**: Flight count > 0 for the displayed month
4. **Frontend shows**: Flights appear in calendar cells

## Verification

After restarting backend:
- Check backend logs for: `Calendar endpoint: Found X flights`
- Check browser console for: `flightsCount: X` where X > 0
- Calendar should display flights in day cells
