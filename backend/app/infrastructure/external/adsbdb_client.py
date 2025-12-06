"""
ADSBDB.com API Client
Public API for aircraft, airline, and flight route data
No API key required!
"""
import asyncio
import httpx
from typing import Optional, Dict, Any
from loguru import logger


class ADSBDBClient:
    """
    Client for ADSBDB.com API
    
    This is a public API - no authentication required!
    Documentation: https://github.com/mrjackwills/adsbdb
    """
    
    BASE_URL = "https://api.adsbdb.com/v1"
    
    def __init__(self, rate_limit_delay: float = 0.6):
        """
        Initialize ADSBDB client
        
        Args:
            rate_limit_delay: Delay between requests in seconds (default 0.6s)
        """
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time: Optional[float] = None
    
    async def _respect_rate_limit(self) -> None:
        """Ensure we respect API rate limits"""
        import asyncio
        from time import time
        
        if self._last_request_time:
            elapsed = time() - self._last_request_time
            if elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
        
        self._last_request_time = time()
    
    async def get_aircraft(
        self,
        identifier: str,
        use_mode_s: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get aircraft information by registration or Mode S code
        
        Args:
            identifier: Aircraft registration (e.g., "9M-XXX") or Mode S code
            use_mode_s: If True, treats identifier as Mode S code
        
        Returns:
            Aircraft data dictionary or None if not found
        """
        await self._respect_rate_limit()
        
        url = f"{self.BASE_URL}/aircraft/{identifier}"
        headers = {
            "User-Agent": "CargoAnalytics/1.0 (Educational/Research Use)",
            "Accept": "application/json"
        }
        
        try:
            # Use shorter timeout and asyncio timeout wrapper for extra safety
            timeout_seconds = 5.0  # Reduced from 10 to 5 seconds
            
            async def fetch_with_timeout():
                async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        # ADSBDB returns data in "response.aircraft" structure
                        if "response" in data and "aircraft" in data["response"]:
                            return data["response"]["aircraft"]
                        return data
                    elif response.status_code == 404:
                        logger.debug(f"Aircraft {identifier} not found in ADSBDB")
                        return None
                    else:
                        logger.warning(f"ADSBDB API returned {response.status_code} for {identifier}")
                        return None
            
            # Double timeout protection: httpx timeout + asyncio timeout
            return await asyncio.wait_for(fetch_with_timeout(), timeout=timeout_seconds + 1.0)
                    
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching aircraft {identifier} from ADSBDB (asyncio timeout)")
            return None
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching aircraft {identifier} from ADSBDB (httpx timeout)")
            return None
        except httpx.RequestError as e:
            logger.warning(f"Request error fetching aircraft {identifier} from ADSBDB: {e}")
            return None
        except asyncio.CancelledError:
            logger.warning(f"Request cancelled for aircraft {identifier} from ADSBDB")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error fetching aircraft {identifier} from ADSBDB: {e}")
            return None
    
    async def get_aircraft_by_registration(self, registration: str) -> Optional[Dict[str, Any]]:
        """
        Get aircraft by registration (convenience method)
        
        Args:
            registration: Aircraft registration (e.g., "9M-XXX", "N123AB")
        
        Returns:
            Aircraft data or None
        """
        return await self.get_aircraft(registration, use_mode_s=False)
    
    async def get_aircraft_by_mode_s(self, mode_s: str) -> Optional[Dict[str, Any]]:
        """
        Get aircraft by Mode S code (convenience method)
        
        Args:
            mode_s: Mode S transponder code
        
        Returns:
            Aircraft data or None
        """
        return await self.get_aircraft(mode_s, use_mode_s=True)
    
    async def get_random_aircraft(self) -> Optional[Dict[str, Any]]:
        """
        Get a random aircraft (useful for testing)
        
        Returns:
            Random aircraft data or None
        """
        await self._respect_rate_limit()
        
        url = f"{self.BASE_URL}/aircraft/random"
        headers = {
            "User-Agent": "CargoAnalytics/1.0 (Educational/Research Use)",
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "response" in data and "aircraft" in data["response"]:
                        return data["response"]["aircraft"]
                    return data
                return None
                
        except Exception as e:
            logger.error(f"Error fetching random aircraft: {e}")
            return None
    
    def extract_aircraft_type(self, aircraft_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract aircraft type from ADSBDB response
        
        Args:
            aircraft_data: Aircraft data from ADSBDB API
        
        Returns:
            Aircraft type string (e.g., "Boeing 737-800") or None
        """
        # ADSBDB provides both "type" and "icao_type"
        # Prefer full type name, fallback to ICAO code
        return aircraft_data.get("type") or aircraft_data.get("icao_type")
    
    def extract_aircraft_info(self, aircraft_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant aircraft information for cargo analytics
        
        Args:
            aircraft_data: Aircraft data from ADSBDB API
        
        Returns:
            Dictionary with extracted aircraft info
        """
        return {
            "registration": aircraft_data.get("registration"),
            "aircraft_type": self.extract_aircraft_type(aircraft_data),
            "icao_type": aircraft_data.get("icao_type"),
            "manufacturer": aircraft_data.get("manufacturer"),
            "mode_s": aircraft_data.get("mode_s"),
            "owner": aircraft_data.get("registered_owner"),
            "owner_country": aircraft_data.get("registered_owner_country_name"),
            "operator_flag": aircraft_data.get("registered_owner_operator_flag_code"),
            "photo_url": aircraft_data.get("url_photo"),
            "photo_thumbnail_url": aircraft_data.get("url_photo_thumbnail")
        }
    
    async def get_aircraft_for_capacity_calculation(
        self,
        registration: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get aircraft data formatted for capacity calculations
        
        This method fetches aircraft data and extracts information
        useful for cargo capacity predictions.
        
        Args:
            registration: Aircraft registration
        
        Returns:
            Dictionary with aircraft info for capacity calculations
        """
        aircraft_data = await self.get_aircraft_by_registration(registration)
        
        if not aircraft_data:
            return None
        
        info = self.extract_aircraft_info(aircraft_data)
        
        # Note: ADSBDB doesn't provide cargo capacity specs directly
        # You'll still need to use your existing AIRCRAFT_CAPACITIES lookup
        # But this enriches the data with accurate aircraft type
        
        return info
    
    async def get_flight_routes(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        airline: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get flight routes data
        
        Note: ADSBDB route endpoints may vary - this is a generic implementation
        Check their GitHub for exact endpoint structure
        
        Args:
            origin: Origin airport code (ICAO or IATA)
            destination: Destination airport code
            airline: Airline code (optional)
        
        Returns:
            Route data or None
        """
        # ADSBDB route endpoints may be different - adjust based on actual API
        # This is a placeholder implementation
        url = f"{self.BASE_URL}/routes"
        params = {}
        
        if origin:
            params["origin"] = origin.upper()
        if destination:
            params["destination"] = destination.upper()
        if airline:
            params["airline"] = airline.upper()
        
        await self._respect_rate_limit()
        
        headers = {
            "User-Agent": "CargoAnalytics/1.0 (Educational/Research Use)",
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data
                elif response.status_code == 404:
                    logger.debug(f"Route not found: {origin} -> {destination}")
                    return None
                else:
                    logger.warning(f"ADSBDB routes API returned {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching routes from ADSBDB: {e}")
            return None
    
    async def search_aircraft_by_type(
        self,
        aircraft_type: str,
        limit: int = 10
    ) -> list:
        """
        Search for aircraft by type
        
        Args:
            aircraft_type: Aircraft type (e.g., "Boeing 737-800", "B738")
            limit: Maximum results to return
        
        Returns:
            List of aircraft matching the type
        """
        # Note: This endpoint may not exist in ADSBDB
        # This is a placeholder - check ADSBDB docs for actual search endpoints
        logger.warning("Search by type may not be available in ADSBDB API")
        return []
