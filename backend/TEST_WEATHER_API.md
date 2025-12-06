# Testing Aviation Weather API Connection

Two test scripts are available to verify the Aviation Weather API connection.

## Quick Test (Simple)

Run a quick test with a single airport:

```bash
cd backend
python test_weather_api_simple.py
```

This will test the connection with KJFK (New York JFK) and display basic weather information.

## Comprehensive Test

Test multiple airports with detailed output:

```bash
cd backend
python test_weather_api.py
```

This tests 5 airports (KJFK, KLAX, KORD, KATL, KDEN) and provides a summary.

### Test a Specific Airport

You can also test a specific airport:

```bash
python test_weather_api.py KJFK
python test_weather_api.py KLAX
python test_weather_api.py KORD
```

## Expected Output

### Successful Connection:
```
✓ SUCCESS! API connection is working.

Weather Data:
  Airport: KJFK
  Time: 2025-01-15 12:00:00
  Visibility: 10.0 miles
  Ceiling: 5000 feet
  Wind: 15 knots from 270°
  Temperature: 5.0°C
```

### Failed Connection:
```
✗ FAILED: [Error message]
```

## Understanding Test Results

### ✓ Success (Data Available)
The API connection works and weather data was retrieved successfully.

### ⚠️ No Data (204 No Content)
This is **normal** and means:
- The API connection is working correctly
- The airport code is valid
- But the airport doesn't have recent weather observations in the database

Some airports report less frequently than others. This is not an error.

### ✗ Failed (Error)
An actual error occurred. Check troubleshooting section below.

## Troubleshooting

If tests fail:

1. **204 No Content is Normal**: If you see "204 No Content", the API is working but that airport has no recent data. Try different airports.

2. **Check Internet Connection**: Ensure you have internet access

3. **Check API Status**: Visit https://aviationweather.gov/data/api/status

4. **Rate Limiting**: Wait 1 minute between test runs (API limit: 100 requests/minute)

5. **Airport Code**: Ensure you're using valid 4-letter ICAO codes (e.g., KJFK, KLAX)

6. **User-Agent**: The script includes a proper User-Agent header (required by API)

## Airports That Typically Have Data

Based on testing, these airports usually have data available:
- **KATL** - Atlanta (usually has data)
- **KMIA** - Miami
- **KSEA** - Seattle
- **KSFO** - San Francisco

Some airports like KJFK, KLAX may return 204 if they haven't reported recently.

## Common Airport Codes

- **KJFK** - New York JFK
- **KLAX** - Los Angeles
- **KORD** - Chicago O'Hare
- **KATL** - Atlanta
- **KDEN** - Denver
- **KSFO** - San Francisco
- **KMIA** - Miami
- **KSEA** - Seattle

## Notes

- The API has a rate limit of 100 requests per minute
- Some airports may not have recent METAR data (returns 204 No Content)
- The test scripts include proper error handling and rate limiting

