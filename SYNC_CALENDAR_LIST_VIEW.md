# Calendar and List View Synchronization

## Current Issue

The calendar view and list view are showing different flights because:

1. **List View** (`/api/v1/flights/cargo`):
   - Returns up to 100 flights
   - Now prioritizes future flights (scheduled_departure >= now)
   - Orders by scheduled_departure ascending
   - Shows flights from multiple months

2. **Calendar View** (`/api/v1/cargo/calendar`):
   - Returns flights for a specific month/year only
   - Filters by `scheduled_departure` within that month
   - Defaults to current month
   - Only shows flights in the selected month

## The Problem

- If the current month has no flights, calendar shows empty
- List view shows flights from next 3 months (from seed script)
- They don't match because they're querying different date ranges

## Solution Applied

1. **Updated `/api/v1/flights/cargo`** to prioritize future flights
2. **Calendar endpoint** already filters by month correctly
3. **Both endpoints** now use the same base query logic

## How They Should Work Together

### List View
- Shows upcoming flights (future dates first)
- Can show flights from multiple months
- Useful for seeing all upcoming flights

### Calendar View
- Shows flights for the selected month only
- Navigate months to see different time periods
- Click on a flight to see analytics

## To Ensure They Match

1. **Calendar defaults to current month** - should show flights if seeded
2. **List view shows future flights** - should include current month flights
3. **Both use same database** - same flights table
4. **Both filter by same criteria** - flight_type, passenger_count

## Verification Steps

1. Check current month has flights:
   ```bash
   # Check if December 2024 has flights
   curl http://localhost:8000/api/v1/cargo/calendar?year=2024&month=12
   ```

2. Check list view shows future flights:
   ```bash
   curl http://localhost:8000/api/v1/flights/cargo | jq '.[0:5] | .[] | {flight_number, scheduled_departure}'
   ```

3. Compare:
   - Calendar flights should appear in list view
   - List view flights for current month should appear in calendar
   - Flight IDs should match between views

## Expected Behavior

- **Current Month (Dec 2024)**: Both views show same flights
- **Next Month (Jan 2025)**: Calendar shows flights when navigated to that month
- **List View**: Shows all upcoming flights from current month onwards
