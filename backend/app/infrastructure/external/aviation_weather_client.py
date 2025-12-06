"""Aviation Weather API client"""
import httpx
from typing import Optional
from datetime import datetime
from ...domain.value_objects.weather_observation import WeatherObservation
from ...domain.interfaces.services import IWeatherDataProvider


class AviationWeatherClient(IWeatherDataProvider):
    """Client for Aviation Weather API"""
    
    BASE_URL = "https://aviationweather.gov/api/data"
    
    def __init__(self, rate_limit_delay: float = 0.6):
        """
        Initialize client
        
        Args:
            rate_limit_delay: Delay between requests in seconds (default 0.6s = 100 req/min)
        """
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time: Optional[datetime] = None
    
    async def get_weather_observation(self, airport_code: str) -> WeatherObservation:
        """
        Get current weather observation (METAR) for airport
        
        Args:
            airport_code: ICAO airport code (4 letters)
        
        Returns:
            WeatherObservation value object
        """
        await self._respect_rate_limit()
        
        url = f"{self.BASE_URL}/metar"
        # Try without hours parameter first (get most recent available)
        # If that fails, we'll try with hours parameter
        params = {
            "ids": airport_code.upper(),
            "format": "json"
        }
        
        # Set custom user agent as required by API to prevent automated filtering
        headers = {
            "User-Agent": "FlightDelayPrediction/1.0 (Educational/Research Use)"
        }
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
            except httpx.TimeoutException:
                raise ValueError(f"Timeout connecting to Aviation Weather API for {airport_code}")
            except httpx.ConnectError as e:
                raise ValueError(f"Connection error to Aviation Weather API for {airport_code}: {str(e)}")
            except httpx.RequestError as e:
                raise ValueError(f"Request error to Aviation Weather API for {airport_code}: {str(e)}")
            
            # Handle specific status codes
            if response.status_code == 204:
                # 204 No Content means valid request but no data available
                # This is normal for some airports that don't report frequently
                raise ValueError(
                    f"No METAR data available for {airport_code} (204 No Content). "
                    f"This airport may not have recent weather observations in the database. "
                    f"Try a different airport or check if the airport code is correct."
                )
            elif response.status_code == 429:
                raise ValueError(f"Rate limit exceeded for Aviation Weather API. Please wait before retrying.")
            elif response.status_code == 400:
                raise ValueError(f"Invalid request to Aviation Weather API for {airport_code}: Bad request")
            elif response.status_code >= 500:
                raise ValueError(
                    f"Aviation Weather API server error ({response.status_code}) for {airport_code}. "
                    f"Response: {response.text[:200] if response.text else 'No response body'}"
                )
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            # Check if response has content
            if not response.text or response.text.strip() == "":
                raise ValueError(f"Empty response from Aviation Weather API for {airport_code}")
            
            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if "application/json" not in content_type and "text/json" not in content_type:
                # Might be HTML error page or other format
                raise ValueError(
                    f"Unexpected content type from Aviation Weather API for {airport_code}: "
                    f"{content_type}. Response: {response.text[:200]}"
                )
            
            try:
                data = response.json()
            except Exception as e:
                raise ValueError(
                    f"Invalid JSON response from Aviation Weather API for {airport_code}: {str(e)}. "
                    f"Response text: {response.text[:200]}"
                )
            
            # Handle empty data
            if not data:
                raise ValueError(f"No METAR data available for {airport_code}")
            
            # Handle empty array
            if isinstance(data, list) and len(data) == 0:
                raise ValueError(f"No METAR data available for {airport_code} (empty array)")
            
            # Get the most recent observation
            metar = data[0] if isinstance(data, list) else data
            
            # Validate metar has required fields
            if not isinstance(metar, dict):
                raise ValueError(
                    f"Unexpected METAR data format for {airport_code}. "
                    f"Expected dict, got {type(metar)}"
                )
            
            return self._parse_metar(metar, airport_code)
    
    async def get_taf(self, airport_code: str) -> dict:
        """
        Get Terminal Aerodrome Forecast (TAF) for airport
        
        Args:
            airport_code: ICAO airport code
        
        Returns:
            TAF data dictionary
        """
        await self._respect_rate_limit()
        
        url = f"{self.BASE_URL}/taf"
        params = {
            "ids": airport_code.upper(),
            "format": "json"
        }
        
        # Set custom user agent as required by API
        headers = {
            "User-Agent": "FlightDelayPrediction/1.0 (Educational/Research Use)"
        }
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
            except httpx.TimeoutException:
                raise ValueError(f"Timeout connecting to Aviation Weather API for {airport_code}")
            except httpx.ConnectError as e:
                raise ValueError(f"Connection error to Aviation Weather API for {airport_code}: {str(e)}")
            except httpx.RequestError as e:
                raise ValueError(f"Request error to Aviation Weather API for {airport_code}: {str(e)}")
            
            # Handle specific status codes
            if response.status_code == 204:
                raise ValueError(f"No TAF data available for {airport_code} (204 No Content)")
            elif response.status_code == 429:
                raise ValueError(f"Rate limit exceeded for Aviation Weather API. Please wait before retrying.")
            elif response.status_code == 400:
                raise ValueError(f"Invalid request to Aviation Weather API for {airport_code}: Bad request")
            elif response.status_code >= 500:
                raise ValueError(
                    f"Aviation Weather API server error ({response.status_code}) for {airport_code}. "
                    f"Response: {response.text[:200] if response.text else 'No response body'}"
                )
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            # Check if response has content
            if not response.text or response.text.strip() == "":
                raise ValueError(f"Empty response from Aviation Weather API for {airport_code}")
            
            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if "application/json" not in content_type and "text/json" not in content_type:
                raise ValueError(
                    f"Unexpected content type from Aviation Weather API for {airport_code}: "
                    f"{content_type}. Response: {response.text[:200]}"
                )
            
            try:
                data = response.json()
            except Exception as e:
                raise ValueError(
                    f"Invalid JSON response from Aviation Weather API for {airport_code}: {str(e)}. "
                    f"Response text: {response.text[:200]}"
                )
            
            return data[0] if isinstance(data, list) else data
    
    def _parse_metar(self, metar_data: dict, airport_code: str) -> WeatherObservation:
        """Parse METAR JSON response into WeatherObservation"""
        
        # Parse observation time
        obs_time_str = metar_data.get("obsTime", "")
        try:
            # METAR times are typically in format: 2025-01-15T12:00:00Z
            if obs_time_str.endswith('Z'):
                obs_time_str = obs_time_str[:-1] + '+00:00'
            obs_time = datetime.fromisoformat(obs_time_str.replace('Z', '+00:00'))
        except:
            obs_time = datetime.now()
        
        # Parse visibility
        vis_miles = None
        vis_meters = None
        if "visib" in metar_data:
            vis_value = metar_data["visib"]
            if isinstance(vis_value, (int, float)):
                vis_miles = float(vis_value)
                vis_meters = vis_miles * 1609.34
            elif isinstance(vis_value, str):
                # Try to parse string like "10SM" or "1600"
                try:
                    if "SM" in vis_value:
                        vis_miles = float(vis_value.replace("SM", "").strip())
                        vis_meters = vis_miles * 1609.34
                    else:
                        vis_meters = float(vis_value)
                        vis_miles = vis_meters / 1609.34
                except:
                    pass
        
        # Parse ceiling
        ceiling_feet = None
        if "clouds" in metar_data and metar_data["clouds"]:
            # Find lowest ceiling
            for cloud in metar_data["clouds"]:
                if isinstance(cloud, dict) and "base" in cloud:
                    base = cloud["base"]
                    if isinstance(base, (int, float)):
                        if ceiling_feet is None or base < ceiling_feet:
                            ceiling_feet = int(base)
        
        # Parse wind
        wind_dir = None
        wind_speed = None
        wind_gust = None
        if "wdir" in metar_data and metar_data["wdir"] is not None:
            wind_dir = int(metar_data["wdir"])
        if "wspd" in metar_data and metar_data["wspd"] is not None:
            wind_speed = int(metar_data["wspd"])
        if "wgst" in metar_data and metar_data["wgst"] is not None:
            wind_gust = int(metar_data["wgst"])
        
        # Parse temperature
        temp_c = None
        if "temp" in metar_data and metar_data["temp"] is not None:
            temp_c = float(metar_data["temp"])
        
        # Parse dewpoint
        dewp_c = None
        if "dewp" in metar_data and metar_data["dewp"] is not None:
            dewp_c = float(metar_data["dewp"])
        
        # Parse pressure
        pressure_mb = None
        if "altim" in metar_data and metar_data["altim"] is not None:
            # Altimeter setting in inches of mercury, convert to mb
            altim_inhg = float(metar_data["altim"])
            pressure_mb = altim_inhg * 33.8639
        
        # Parse weather conditions
        wx_string = metar_data.get("wxString", "")
        
        # Get raw METAR
        raw_metar = metar_data.get("rawOb", "")
        
        return WeatherObservation(
            airport_code=airport_code.upper(),
            observation_time=obs_time,
            visibility_miles=vis_miles,
            visibility_meters=vis_meters,
            ceiling_feet=ceiling_feet,
            wind_direction_degrees=wind_dir,
            wind_speed_knots=wind_speed,
            wind_gust_knots=wind_gust,
            temperature_celsius=temp_c,
            dewpoint_celsius=dewp_c,
            pressure_mb=pressure_mb,
            weather_conditions=wx_string if wx_string else None,
            raw_metar=raw_metar
        )
    
    async def _respect_rate_limit(self) -> None:
        """Ensure we respect API rate limits"""
        import asyncio
        if self._last_request_time:
            elapsed = (datetime.now() - self._last_request_time).total_seconds()
            if elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = datetime.now()

