# Cargo Calendar View Setup Guide

## Overview

The cargo analytics page now features a comprehensive calendar view that displays upcoming flights with cargo utilization predictions based on estimated traffic and peak seasons.

## Features

### Calendar View
- **Monthly calendar grid** showing all flights for the selected month
- **Peak season highlighting**:
  - 🎉 Holidays (red border)
  - 🎓 School holidays (orange border)
  - 📈 Peak season days (blue border)
- **Flight cards** on each day showing:
  - Flight number
  - Route (origin → destination)
  - Utilization percentage (color-coded)
  - Risk badges for high overbooking risk
- **Clickable flights** - Click any flight to view detailed analytics

### Sidebars
- **Left Sidebar**: Insights, Quick Filters, Peak Season List
- **Right Sidebar**: Statistics, Top Routes, Risk Alerts

### List View
- Traditional list view (toggle available)
- Same flights as calendar view
- Clickable to view analytics

## Setup Instructions

### Option 1: Use Mock Data (Quick Start)

The calendar view works with mock data by default. No setup required!

1. Navigate to `/cargo-analytics`
2. The calendar will automatically populate with mock flights
3. Click any flight to view analytics

### Option 2: Use Database (Recommended for Production)

1. **Initialize the database** (if not already done):
   ```bash
   python backend/scripts/init_db.py
   ```

2. **Seed the database with flights**:
   ```bash
   python backend/scripts/seed_cargo_flights.py
   ```

3. **Start the backend server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. **Start the frontend** (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

5. **Disable mock data** (optional):
   - Create/update `.env` file in `frontend/` directory
   - Set `VITE_USE_MOCK_DATA=false` (or remove the variable)

## Data Synchronization

### Calendar View ↔ List View
- Both views use the same data source
- Flight IDs are consistent between views
- Clicking a flight in either view navigates to the same analytics page

### Mock Data
- Mock data generates flights for the current month and next 2 months
- Flight IDs follow format: `flight-YYYYMMDD-index`
- Same flights appear in both calendar and list views

### Database Data
- Database flights use UUIDs
- Calendar and list views both query `/api/v1/flights/cargo`
- Calendar view uses `/api/v1/cargo/calendar` for month-specific data

## Flight Navigation

### From Calendar View
1. Click any flight card on a calendar day
2. Navigates to `/cargo-analytics/{flight_id}`
3. Shows detailed cargo analytics for that flight

### From List View
1. Click any flight in the list
2. Navigates to `/cargo-analytics/{flight_id}`
3. Shows detailed cargo analytics for that flight

## Peak Season Detection

The system automatically detects:
- **Holidays**: New Year's Day, Christmas, New Year's Eve
- **School Holidays**:
  - Winter Break: December 15 - January 5
  - Summer Break: June - August
  - Spring Break: March 15-31
  - Fall Break: October 1-15

## Traffic Estimation

Traffic multipliers are applied based on:
- **Weekends**: 1.15x multiplier
- **Holidays**: 1.5x multiplier
- **School Holidays**: 1.3x multiplier
- **Summer Months** (Jun-Aug): 1.2x multiplier
- **Winter Season** (Dec-Jan): 1.25x multiplier

## Cargo Utilization Predictions

Each flight shows:
- **Utilization Percentage**: Based on predicted baggage + cargo demand
- **Available Weight**: In kg (converted to tonnes in UI)
- **Available Volume**: In m³
- **Overbooking Risk**: Low, Medium, or High
- **Constraining Factor**: Weight or Volume

## Troubleshooting

### Calendar shows no flights
1. Check if mock data is enabled: `VITE_USE_MOCK_DATA=true` in `.env`
2. If using database, run the seed script: `python backend/scripts/seed_cargo_flights.py`
3. Check browser console for errors

### Flight clicks don't work
1. Ensure flight IDs are consistent (check browser console)
2. Verify the route `/cargo-analytics/:flightId` exists
3. Check that flight IDs match between calendar and list views

### Data not syncing
1. Both views use the same API endpoints
2. Mock data uses the same generator function
3. Database flights use the same query

## API Endpoints

- `GET /api/v1/cargo/calendar?year=2024&month=12` - Calendar data with predictions
- `GET /api/v1/flights/cargo` - List of all cargo flights
- `GET /api/v1/cargo/analytics/{flight_id}` - Detailed analytics for a flight

## Mock Data Structure

Mock flights are generated with:
- Consistent IDs: `flight-YYYYMMDD-index`
- Realistic routes and aircraft types
- Traffic-based utilization predictions
- Peak season adjustments

## Next Steps

1. Run the seed script to populate the database
2. Test the calendar view navigation
3. Verify list view shows the same flights
4. Click flights to test analytics page navigation
