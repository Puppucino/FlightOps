"""
OpenSky Network API Client
Real-time flight tracking and historical flight data
No API key required for basic access!
"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger


class OpenSkyClient:
    """
    Client for OpenSky Network API
    
    Provides real-time flight tracking and historical data
    Documentation: https://openskynetwork.github.io/opensky-api/
    """
    
    BASE_URL = "https://opensky-network.org/api"
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize OpenSky client
        
        Args:
            username: Optional username for authenticated requests (higher rate limits)
            password: Optional password for authenticated requests
        """
        self.username = username
        self.password = password
        self.auth = (username, password) if username and password else None
    
    async def get_all_flights(
        self,
        begin: Optional[int] = None,
        end: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get all flights in a time range
        
        Args:
            begin: Start time as Unix timestamp
            end: End time as Unix timestamp
        
        Returns:
            Dictionary with flight states
        """
        url = f"{self.BASE_URL}/flights/all"
        params = {}
        
        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end
        
        headers = {
            "User-Agent": "CargoAnalytics/1.0 (Educational/Research Use)"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, auth=self.auth) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"OpenSky API returned {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching flights from OpenSky: {e}")
            return None
    
    async def get_flights_by_aircraft(
        self,
        icao24: str,
        begin: Optional[int] = None,
        end: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get flights for a specific aircraft by ICAO24 address
        
        Args:
            icao24: ICAO24 address (Mode S transponder code)
            begin: Start time as Unix timestamp
            end: End time as Unix timestamp
        
        Returns:
            List of flight data
        """
        url = f"{self.BASE_URL}/flights/aircraft"
        params = {"icao24": icao24.upper()}
        
        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end
        
        headers = {
            "User-Agent": "CargoAnalytics/1.0 (Educational/Research Use)"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, auth=self.auth) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data if isinstance(data, list) else []
                else:
                    logger.warning(f"OpenSky API returned {response.status_code} for aircraft {icao24}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching aircraft flights from OpenSky: {e}")
            return []
    
    async def get_flight_by_route(
        self,
        origin: str,
        destination: str,
        begin: Optional[int] = None,
        end: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get flights between two airports
        
        Args:
            origin: Origin airport ICAO code
            destination: Destination airport ICAO code
            begin: Start time as Unix timestamp
            end: End time as Unix timestamp
        
        Returns:
            List of flights on this route
        """
        url = f"{self.BASE_URL}/flights/route"
        params = {
            "airport1": origin.upper(),
            "airport2": destination.upper()
        }
        
        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end
        
        headers = {
            "User-Agent": "CargoAnalytics/1.0 (Educational/Research Use)"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, auth=self.auth) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data if isinstance(data, list) else []
                else:
                    logger.warning(f"OpenSky API returned {response.status_code} for route {origin}->{destination}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching route flights from OpenSky: {e}")
            return []
    
    async def get_current_flight_states(
        self,
        icao24: Optional[str] = None,
        bbox: Optional[tuple] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get current flight states (real-time tracking)
        
        Args:
            icao24: Optional ICAO24 address to filter
            bbox: Optional bounding box (min_lat, min_lon, max_lat, max_lon)
        
        Returns:
            List of current flight states
        """
        url = f"{self.BASE_URL}/states/all"
        params = {}
        
        if icao24:
            url = f"{self.BASE_URL}/states/aircraft"
            params["icao24"] = icao24.upper()
        
        if bbox:
            params["lamin"] = bbox[0]
            params["lomin"] = bbox[1]
            params["lamax"] = bbox[2]
            params["lomax"] = bbox[3]
        
        headers = {
            "User-Agent": "CargoAnalytics/1.0 (Educational/Research Use)"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0, auth=self.auth) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    # OpenSky returns {"time": timestamp, "states": [...]}
                    if isinstance(data, dict) and "states" in data:
                        return self._parse_flight_states(data["states"])
                    return []
                else:
                    logger.warning(f"OpenSky states API returned {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching flight states from OpenSky: {e}")
            return []
    
    def _parse_flight_states(self, states: List[List]) -> List[Dict[str, Any]]:
        """
        Parse OpenSky flight state array into dictionary
        
        OpenSky returns states as arrays with fixed positions:
        [icao24, callsign, origin_country, time_position, last_contact,
         longitude, latitude, baro_altitude, on_ground, velocity,
         true_track, vertical_rate, sensors, geo_altitude, squawk,
         spi, position_source]
        """
        parsed = []
        for state in states:
            if len(state) >= 17:
                parsed.append({
                    "icao24": state[0],
                    "callsign": state[1] if state[1] else None,
                    "origin_country": state[2],
                    "time_position": state[3],
                    "last_contact": state[4],
                    "longitude": state[5],
                    "latitude": state[6],
                    "baro_altitude": state[7],
                    "on_ground": state[8],
                    "velocity": state[9],
                    "true_track": state[10],
                    "vertical_rate": state[11],
                    "sensors": state[12],
                    "geo_altitude": state[13],
                    "squawk": state[14],
                    "spi": state[15],
                    "position_source": state[16]
                })
        return parsed
    
    async def get_airport_departures(
        self,
        airport: str,
        begin: Optional[int] = None,
        end: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get departures from an airport
        
        Args:
            airport: Airport ICAO code
            begin: Start time as Unix timestamp
            end: End time as Unix timestamp
        
        Returns:
            List of departure flights
        """
        url = f"{self.BASE_URL}/flights/departure"
        params = {"airport": airport.upper()}
        
        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end
        
        headers = {
            "User-Agent": "CargoAnalytics/1.0 (Educational/Research Use)"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, auth=self.auth) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data if isinstance(data, list) else []
                else:
                    logger.warning(f"OpenSky API returned {response.status_code} for departures from {airport}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching departures from OpenSky: {e}")
            return []
    
    async def get_airport_arrivals(
        self,
        airport: str,
        begin: Optional[int] = None,
        end: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get arrivals to an airport
        
        Args:
            airport: Airport ICAO code
            begin: Start time as Unix timestamp
            end: End time as Unix timestamp
        
        Returns:
            List of arrival flights
        """
        url = f"{self.BASE_URL}/flights/arrival"
        params = {"airport": airport.upper()}
        
        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end
        
        headers = {
            "User-Agent": "CargoAnalytics/1.0 (Educational/Research Use)"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, auth=self.auth) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data if isinstance(data, list) else []
                else:
                    logger.warning(f"OpenSky API returned {response.status_code} for arrivals to {airport}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching arrivals from OpenSky: {e}")
            return []
