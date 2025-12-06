"""Simple test script for Aviation Weather API"""
import asyncio
from app.infrastructure.external.aviation_weather_client import AviationWeatherClient


async def quick_test():
    """Quick test of the API connection"""
    print("Testing Aviation Weather API Connection...")
    print("-" * 60)
    
    client = AviationWeatherClient()
    airport_code = "KJFK"  # New York JFK
    
    try:
        print(f"Fetching weather for {airport_code}...")
        weather = await client.get_weather_observation(airport_code)
        
        print(f"\n✓ SUCCESS! API connection is working.")
        print(f"\nWeather Data:")
        print(f"  Airport: {weather.airport_code}")
        print(f"  Time: {weather.observation_time}")
        print(f"  Visibility: {weather.visibility_miles} miles")
        print(f"  Ceiling: {weather.ceiling_feet} feet")
        print(f"  Wind: {weather.wind_speed_knots} knots from {weather.wind_direction_degrees}°")
        print(f"  Temperature: {weather.temperature_celsius}°C")
        
        if weather.raw_metar:
            print(f"\n  Raw METAR: {weather.raw_metar}")
        
        return True
        
    except ValueError as e:
        error_msg = str(e)
        if "204 No Content" in error_msg:
            print(f"\n⚠️  NO DATA: {error_msg}")
            print(f"\nNote: 204 No Content means the API connection works,")
            print(f"      but this airport doesn't have recent weather observations.")
            print(f"      Try a different airport code (e.g., KATL, KMIA, KSEA)")
            return None
        else:
            print(f"\n✗ FAILED: {error_msg}")
            return False
    except Exception as e:
        print(f"\n✗ FAILED: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(quick_test())
    exit(0 if success else 1)

