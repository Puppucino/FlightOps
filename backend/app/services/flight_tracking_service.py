"""
Flight Tracking Service
Combines ADSBDB (aircraft data) and OpenSky (real-time tracking) for comprehensive flight information
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from app.infrastructure.external.adsbdb_client import ADSBDBClient
from app.infrastructure.external.opensky_client import OpenSkyClient


class FlightTrackingService:
    """Service for tracking flights using multiple data sources"""
    
    def __init__(
        self,
        adsbdb_client: Optional[ADSBDBClient] = None,
        opensky_client: Optional[OpenSkyClient] = None
    ):
        self.adsbdb = adsbdb_client or ADSBDBClient()
        self.opensky = opensky_client or OpenSkyClient()
    
    async def get_aircraft_info(
        self,
        registration: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive aircraft information
        
        Combines ADSBDB aircraft data with any additional sources
        
        Args:
            registration: Aircraft registration
        
        Returns:
            Comprehensive aircraft information
        """
        try:
            # Get from ADSBDB
            aircraft_data = await self.adsbdb.get_aircraft_by_registration(registration)
            
            if not aircraft_data:
                logger.warning(f"Aircraft {registration} not found in ADSBDB")
                return None
            
            # Extract and format
            info = self.adsbdb.extract_aircraft_info(aircraft_data)
            
            # Get Mode S code for real-time tracking
            mode_s = aircraft_data.get("mode_s")
            if mode_s:
                info["mode_s"] = mode_s
                # Get current flight state if available
                current_state = await self.opensky.get_current_flight_states(icao24=mode_s)
                if current_state and len(current_state) > 0:
                    info["current_flight_state"] = current_state[0]
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting aircraft info for {registration}: {e}")
            return None
    
    async def get_flight_route_info(
        self,
        origin: str,
        destination: str,
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get flight route information
        
        Combines route data from multiple sources
        
        Args:
            origin: Origin airport code (ICAO)
            destination: Destination airport code (ICAO)
            date: Optional date for historical data
        
        Returns:
            Route information dictionary
        """
        route_info = {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "flights": [],
            "aircraft_types": [],
            "average_distance_km": None
        }
        
        try:
            # Get flights from OpenSky
            begin = None
            end = None
            if date:
                begin = int((date - timedelta(hours=1)).timestamp())
                end = int((date + timedelta(hours=1)).timestamp())
            
            flights = await self.opensky.get_flight_by_route(
                origin=origin,
                destination=destination,
                begin=begin,
                end=end
            )
            
            if flights:
                route_info["flights"] = flights
                
                # Extract unique aircraft types
                aircraft_types = set()
                for flight in flights:
                    if "icao24" in flight:
                        # Try to get aircraft info from ADSBDB
                        # Note: Would need Mode S to ICAO24 mapping
                        pass
                
                route_info["aircraft_types"] = list(aircraft_types)
            
            # Try ADSBDB routes (if available)
            adsbdb_routes = await self.adsbdb.get_flight_routes(
                origin=origin,
                destination=destination
            )
            
            if adsbdb_routes:
                route_info["adsbdb_data"] = adsbdb_routes
            
        except Exception as e:
            logger.error(f"Error getting route info {origin}->{destination}: {e}")
        
        return route_info
    
    async def get_real_time_flight_status(
        self,
        registration: Optional[str] = None,
        mode_s: Optional[str] = None,
        flight_number: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get real-time flight status
        
        Args:
            registration: Aircraft registration
            mode_s: Mode S code (ICAO24)
            flight_number: Flight number (for lookup)
        
        Returns:
            Real-time flight status
        """
        try:
            # Get Mode S code if we have registration
            icao24 = mode_s
            if not icao24 and registration:
                aircraft_info = await self.get_aircraft_info(registration)
                if aircraft_info and "mode_s" in aircraft_info:
                    icao24 = aircraft_info["mode_s"]
            
            if not icao24:
                logger.warning("Cannot track flight without Mode S code")
                return None
            
            # Get current flight state
            states = await self.opensky.get_current_flight_states(icao24=icao24)
            
            if not states or len(states) == 0:
                return {
                    "status": "not_tracked",
                    "message": "Aircraft not currently being tracked"
                }
            
            state = states[0]
            
            # Get aircraft info
            aircraft_info = None
            if registration:
                aircraft_info = await self.get_aircraft_info(registration)
            
            return {
                "status": "tracked",
                "aircraft": aircraft_info,
                "position": {
                    "latitude": state.get("latitude"),
                    "longitude": state.get("longitude"),
                    "altitude": state.get("baro_altitude") or state.get("geo_altitude"),
                    "heading": state.get("true_track"),
                    "velocity": state.get("velocity"),  # m/s
                    "vertical_rate": state.get("vertical_rate")  # m/s
                },
                "flight_info": {
                    "callsign": state.get("callsign"),
                    "squawk": state.get("squawk"),
                    "origin_country": state.get("origin_country"),
                    "on_ground": state.get("on_ground"),
                    "last_contact": datetime.fromtimestamp(state.get("last_contact", 0)) if state.get("last_contact") else None
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time flight status: {e}")
            return None
    
    async def get_airport_flights(
        self,
        airport: str,
        flight_type: str = "departures",  # "departures" or "arrivals"
        begin: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get flights from/to an airport
        
        Args:
            airport: Airport ICAO code
            flight_type: "departures" or "arrivals"
            begin: Start time
            end: End time
        
        Returns:
            List of flights
        """
        try:
            begin_ts = int(begin.timestamp()) if begin else None
            end_ts = int(end.timestamp()) if end else None
            
            if flight_type == "departures":
                flights = await self.opensky.get_airport_departures(
                    airport=airport,
                    begin=begin_ts,
                    end=end_ts
                )
            else:
                flights = await self.opensky.get_airport_arrivals(
                    airport=airport,
                    begin=begin_ts,
                    end=end_ts
                )
            
            # Enrich with aircraft data
            enriched_flights = []
            for flight in flights:
                enriched = flight.copy()
                
                # Try to get aircraft info if we have icao24
                if "icao24" in flight:
                    # Note: Would need to map icao24 to registration for ADSBDB lookup
                    pass
                
                enriched_flights.append(enriched)
            
            return enriched_flights
            
        except Exception as e:
            logger.error(f"Error getting airport flights: {e}")
            return []
