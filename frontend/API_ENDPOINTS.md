# Required Backend API Endpoints

This document lists the API endpoints that need to be implemented in the backend for the Cargo Analytics page to work with real data.

## Base URL
All endpoints should be prefixed with `/api/v1`

## Endpoints

### 1. Get Cargo Analytics
**GET** `/api/v1/cargo/analytics/{flight_id}`

Returns comprehensive cargo analytics data for a specific flight.

**Response:**
```json
{
  "flight": {
    "id": "string (UUID)",
    "flight_number": "string",
    "airline_name": "string",
    "aircraft_registration": "string",
    "aircraft_type": "string",
    "origin_airport": "string",
    "origin_airport_code": "string",
    "destination_airport": "string",
    "destination_airport_code": "string",
    "scheduled_departure": "ISO 8601 datetime",
    "scheduled_arrival": "ISO 8601 datetime",
    "actual_departure": "ISO 8601 datetime (optional)",
    "actual_arrival": "ISO 8601 datetime (optional)",
    "flight_status": "scheduled | departed | arrived | cancelled | delayed",
    "distance_km": "number",
    "flight_type": "passenger | cargo | mixed"
  },
  "storage_availability": {
    "aircraft_id": "string (UUID)",
    "aircraft_registration": "string",
    "total_capacity_tonnes": "number",
    "current_cargo_tonnes": "number",
    "available_capacity_tonnes": "number",
    "utilization_percentage": "number (0-100)",
    "predicted_demand_tonnes": "number",
    "confidence_score": "number (0-1)"
  },
  "loading_progress": {
    "flight_id": "string (UUID)",
    "flight_number": "string",
    "total_cargo_tonnes": "number",
    "loaded_cargo_tonnes": "number",
    "loading_percentage": "number (0-100)",
    "estimated_completion_time": "ISO 8601 datetime (optional)",
    "status": "not_started | in_progress | completed | delayed"
  },
  "prediction": {
    "predicted_cargo_volume": "number",
    "confidence": "number (0-1)"
  }
}
```

### 2. Get Cargo Analytics by Flight Number
**GET** `/api/v1/cargo/analytics/flight/{flight_number}`

Same response structure as endpoint #1, but uses flight number instead of flight ID.

### 3. Get Storage Availability
**GET** `/api/v1/cargo/storage/{aircraft_id}`

Returns storage availability data for a specific aircraft.

**Response:**
```json
{
  "aircraft_id": "string (UUID)",
  "aircraft_registration": "string",
  "total_capacity_tonnes": "number",
  "current_cargo_tonnes": "number",
  "available_capacity_tonnes": "number",
  "utilization_percentage": "number (0-100)",
  "predicted_demand_tonnes": "number",
  "confidence_score": "number (0-1)"
}
```

### 4. Get Cargo Loading Progress
**GET** `/api/v1/cargo/loading/{flight_id}`

Returns cargo loading progress for a specific flight.

**Response:**
```json
{
  "flight_id": "string (UUID)",
  "flight_number": "string",
  "total_cargo_tonnes": "number",
  "loaded_cargo_tonnes": "number",
  "loading_percentage": "number (0-100)",
  "estimated_completion_time": "ISO 8601 datetime (optional)",
  "status": "not_started | in_progress | completed | delayed"
}
```

### 5. Get Flight Details
**GET** `/api/v1/flights/{flight_id}`

Returns detailed flight information.

**Response:**
```json
{
  "id": "string (UUID)",
  "flight_number": "string",
  "airline_name": "string",
  "aircraft_registration": "string",
  "aircraft_type": "string",
  "origin_airport": "string",
  "origin_airport_code": "string",
  "destination_airport": "string",
  "destination_airport_code": "string",
  "scheduled_departure": "ISO 8601 datetime",
  "scheduled_arrival": "ISO 8601 datetime",
  "actual_departure": "ISO 8601 datetime (optional)",
  "actual_arrival": "ISO 8601 datetime (optional)",
  "flight_status": "scheduled | departed | arrived | cancelled | delayed",
  "distance_km": "number",
  "flight_type": "passenger | cargo | mixed"
}
```

### 6. Get All Cargo Flights
**GET** `/api/v1/flights/cargo`

Returns a list of all flights that carry cargo.

**Response:**
```json
[
  {
    "id": "string (UUID)",
    "flight_number": "string",
    "airline_name": "string",
    "aircraft_registration": "string",
    "aircraft_type": "string",
    "origin_airport": "string",
    "origin_airport_code": "string",
    "destination_airport": "string",
    "destination_airport_code": "string",
    "scheduled_departure": "ISO 8601 datetime",
    "scheduled_arrival": "ISO 8601 datetime",
    "actual_departure": "ISO 8601 datetime (optional)",
    "actual_arrival": "ISO 8601 datetime (optional)",
    "flight_status": "scheduled | departed | arrived | cancelled | delayed",
    "distance_km": "number",
    "flight_type": "passenger | cargo | mixed"
  }
]
```

## Notes

- All datetime fields should be in ISO 8601 format with timezone information
- The frontend will automatically fall back to mock data if API calls fail
- To force mock data usage, set `VITE_USE_MOCK_DATA=true` in your `.env` file
- All endpoints should return appropriate HTTP status codes (200 for success, 404 for not found, etc.)
