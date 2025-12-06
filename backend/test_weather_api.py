"""Test script for Aviation Weather API connection"""
import asyncio
import sys
from app.infrastructure.external.aviation_weather_client import AviationWeatherClient


async def test_airport(airport_code: str):
    """Test weather API for a specific airport"""
    print(f"\n{'='*80}")
    print(f"Testing Airport: {airport_code}")
    print(f"{'='*80}")
    
    client = AviationWeatherClient()
    
    try:
        print(f"Fetching METAR data for {airport_code}...")
        weather = await client.get_weather_observation(airport_code)
        
        print(f"\n✓ Successfully retrieved weather data!")
        print(f"\nWeather Observation Details:")
        print(f"  Airport Code: {weather.airport_code}")
        print(f"  Observation Time: {weather.observation_time}")
        print(f"  Visibility: {weather.visibility_miles} miles ({weather.visibility_meters} meters)")
        print(f"  Ceiling: {weather.ceiling_feet} feet")
        print(f"  Wind: {weather.wind_direction_degrees}° at {weather.wind_speed_knots} knots")
        if weather.wind_gust_knots:
            print(f"  Wind Gust: {weather.wind_gust_knots} knots")
        print(f"  Temperature: {weather.temperature_celsius}°C")
        if weather.dewpoint_celsius:
            print(f"  Dewpoint: {weather.dewpoint_celsius}°C")
        if weather.pressure_mb:
            print(f"  Pressure: {weather.pressure_mb} mb")
        if weather.weather_conditions:
            print(f"  Weather Conditions: {weather.weather_conditions}")
        if weather.raw_metar:
            print(f"  Raw METAR: {weather.raw_metar}")
        
        # Test weather analysis
        print(f"\nWeather Impact Analysis:")
        print(f"  Low Visibility (<3 miles): {weather.has_low_visibility()}")
        print(f"  Low Ceiling (<1000 ft): {weather.has_low_ceiling()}")
        print(f"  High Wind (>25 knots): {weather.has_high_wind()}")
        print(f"  Precipitation Present: {weather.has_precipitation()}")
        print(f"  IMC Conditions: {weather.is_imc()}")
        
        return True
        
    except ValueError as e:
        error_msg = str(e)
        if "204 No Content" in error_msg:
            print(f"\n⚠️  Warning: {error_msg}")
            print(f"   This is normal - the airport may not have recent observations.")
            print(f"   The API connection is working, but no data is available for this airport.")
            return None  # Return None to indicate "no data" vs "error"
        else:
            print(f"\n✗ Error: {error_msg}")
            return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_airports():
    """Test multiple airports"""
    airports = [
        "KJFK",  # New York
        "KLAX",  # Los Angeles
        "KORD",  # Chicago
        "KATL",  # Atlanta
        "KDEN",  # Denver
    ]
    
    print("="*80)
    print("Aviation Weather API Connection Test")
    print("="*80)
    print(f"\nTesting {len(airports)} airports...")
    
    results = []
    for airport in airports:
        success = await test_airport(airport)
        results.append((airport, success))
        # Small delay between requests to respect rate limits
        await asyncio.sleep(1)
    
    # Summary
    print(f"\n{'='*80}")
    print("Test Summary")
    print(f"{'='*80}")
    successful = sum(1 for _, success in results if success is True)
    no_data = sum(1 for _, success in results if success is None)
    failed = sum(1 for _, success in results if success is False)
    
    for airport, success in results:
        if success is True:
            status = "✓ PASS (Data Available)"
        elif success is None:
            status = "⚠️  NO DATA (204 Response)"
        else:
            status = "✗ FAIL (Error)"
        print(f"  {airport}: {status}")
    
    print(f"\nTotal: {len(results)} airports tested")
    print(f"  Successful (Data Available): {successful}")
    print(f"  No Data Available (204): {no_data}")
    print(f"  Failed (Errors): {failed}")
    
    if successful > 0:
        print(f"\n✓ API connection is working! {successful} airport(s) have data available.")
        if no_data > 0:
            print(f"⚠️  {no_data} airport(s) returned 204 No Content (no recent data).")
            print("   This is normal - not all airports have frequent observations.")
    elif no_data > 0:
        print(f"\n⚠️  API connection works, but no data available for tested airports.")
        print("   Try different airport codes or check if airports report frequently.")
    else:
        print("\n❌ All tests failed. Please check:")
        print("  1. Internet connection")
        print("  2. Aviation Weather API status")
        print("  3. Airport codes are valid ICAO codes")
        print("  4. Rate limiting (wait 1 minute and try again)")


async def test_single_airport(airport_code: str):
    """Test a single airport"""
    print("="*80)
    print("Aviation Weather API Connection Test - Single Airport")
    print("="*80)
    
    success = await test_airport(airport_code)
    
    if success:
        print("\n🎉 Test passed! API connection is working correctly.")
    else:
        print("\n❌ Test failed. Please check:")
        print("  1. Internet connection")
        print("  2. Airport code is valid (4-letter ICAO code)")
        print("  3. Aviation Weather API status")
    
    return success


async def main():
    """Main test function"""
    if len(sys.argv) > 1:
        # Test single airport from command line
        airport_code = sys.argv[1].upper()
        await test_single_airport(airport_code)
    else:
        # Test multiple airports
        await test_multiple_airports()


if __name__ == "__main__":
    print("\nStarting Aviation Weather API Test...")
    print("Usage: python test_weather_api.py [AIRPORT_CODE]")
    print("Example: python test_weather_api.py KJFK")
    print("Or run without arguments to test multiple airports\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nFatal error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

