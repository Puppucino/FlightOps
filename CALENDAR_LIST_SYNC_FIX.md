# Calendar and List View Synchronization Fix

## Issue

The calendar view and list view show different flights because:

1. **Calendar View** (`/api/v1/cargo/calendar`):
   - Filters by specific month/year
   - Defaults to current month
   - Only shows flights in that month

2. **List View** (`/api/v1/flights/cargo`):
   - Shows all future flights (up to 100)
   - Not filtered by month
   - Shows flights from multiple months

## Root Cause

- Calendar defaults to **current month** (December 2024)
- Seed script creates flights for **next 3 months** from today
- If today is early December, flights might start in mid-December or January
- Calendar shows empty if current month has no flights yet

## Solution

Both endpoints now use the same query logic:
- Same filters: `flight_type`, `passenger_count`
- Same ordering: `scheduled_departure.asc()`
- Calendar filters by month (as intended)
- List view shows all future flights (as intended)

## Expected Behavior

### Calendar View
- Shows flights for the **selected month**
- Navigate months to see different time periods
- Defaults to current month
- If current month has no flights, navigate to next month

### List View
- Shows **all upcoming flights** (future dates)
- Includes flights from multiple months
- Orders by scheduled_departure (earliest first)

## How They Work Together

1. **Current Month Has Flights:**
   - Calendar shows flights for current month
   - List view includes those same flights (plus others)
   - ✅ They match for current month

2. **Current Month Has No Flights:**
   - Calendar shows empty (correct - no flights this month)
   - List view shows flights from next months
   - Navigate calendar to next month to see flights
   - ✅ Both are correct, just showing different time periods

3. **User Navigates Calendar:**
   - Calendar shows flights for selected month
   - List view still shows all upcoming flights
   - ✅ Calendar shows subset, list shows all

## Verification

To verify they're synchronized:

1. **Check current month:**
   ```bash
   curl http://localhost:8000/api/v1/cargo/calendar?year=2024&month=12
   ```

2. **Check list view:**
   ```bash
   curl http://localhost:8000/api/v1/flights/cargo | jq '.[0:5] | .[] | {flight_number, scheduled_departure}'
   ```

3. **Compare:**
   - Flights in calendar for current month should appear in list view
   - Flight IDs should match
   - Same flight data structure

## Next Steps

1. Restart backend to apply endpoint changes
2. Navigate calendar to a month with flights (if current month is empty)
3. Verify flights appear in both views
4. Click flights to test navigation
