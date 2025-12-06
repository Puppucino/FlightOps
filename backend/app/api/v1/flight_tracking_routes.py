"""
Flight Tracking API Routes
Endpoints for aircraft data, flight routes, and real-time tracking
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.flight_tracking_service import FlightTrackingService
from app.infrastructure.external.adsbdb_client import ADSBDBClient
from app.infrastructure.external.opensky_client import OpenSkyClient
from app.models.flight import Flight
from app.models.aircraft import Aircraft

router = APIRouter(prefix="/tracking", tags=["Flight Tracking"])

# Global service instances
_tracking_service = None


def get_tracking_service() -> FlightTrackingService:
    """Get flight tracking service instance"""
    global _tracking_service
    if _tracking_service is None:
        _tracking_service = FlightTrackingService()
    return _tracking_service


class AircraftInfoResponse(BaseModel):
    """Aircraft information response"""
    registration: Optional[str]
    aircraft_type: Optional[str]
    icao_type: Optional[str]
    manufacturer: Optional[str]
    owner: Optional[str]
    owner_country: Optional[str]
    photo_url: Optional[str]
    current_flight_state: Optional[dict]


class RouteInfoResponse(BaseModel):
    """Route information response"""
    origin: str
    destination: str
    flights: List[dict]
    aircraft_types: List[str]


class RealTimeFlightStatusResponse(BaseModel):
    """Real-time flight status response"""
    status: str
    aircraft: Optional[dict]
    position: Optional[dict]
    flight_info: Optional[dict]
    timestamp: str


@router.get("/aircraft/{registration}", response_model=AircraftInfoResponse)
async def get_aircraft_info(
    registration: str,
    tracking_service: FlightTrackingService = Depends(get_tracking_service)
):
    """
    Get comprehensive aircraft information from ADSBDB
    
    Includes aircraft type, manufacturer, owner, and current flight state if available
    """
    try:
        info = await tracking_service.get_aircraft_info(registration)
        
        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"Aircraft {registration} not found"
            )
        
        return AircraftInfoResponse(**info)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching aircraft info: {str(e)}"
        )


@router.get("/routes/{origin}/{destination}", response_model=RouteInfoResponse)
async def get_route_info(
    origin: str,
    destination: str,
    date: Optional[datetime] = Query(None, description="Optional date for historical data"),
    tracking_service: FlightTrackingService = Depends(get_tracking_service)
):
    """
    Get flight route information between two airports
    
    Combines data from ADSBDB and OpenSky Network
    """
    try:
        route_info = await tracking_service.get_flight_route_info(
            origin=origin.upper(),
            destination=destination.upper(),
            date=date
        )
        
        return RouteInfoResponse(**route_info)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching route info: {str(e)}"
        )


@router.get("/realtime/{registration}", response_model=RealTimeFlightStatusResponse)
async def get_real_time_status(
    registration: str,
    mode_s: Optional[str] = Query(None, description="Mode S code (ICAO24) if known"),
    flight_number: Optional[str] = Query(None, description="Flight number for lookup"),
    tracking_service: FlightTrackingService = Depends(get_tracking_service)
):
    """
    Get real-time flight status and position
    
    Uses OpenSky Network for real-time tracking
    """
    try:
        status = await tracking_service.get_real_time_flight_status(
            registration=registration,
            mode_s=mode_s,
            flight_number=flight_number
        )
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Real-time status not available for {registration}"
            )
        
        return RealTimeFlightStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching real-time status: {str(e)}"
        )


@router.get("/airport/{airport}/flights")
async def get_airport_flights(
    airport: str,
    flight_type: str = Query("departures", regex="^(departures|arrivals)$"),
    begin: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    tracking_service: FlightTrackingService = Depends(get_tracking_service)
):
    """
    Get flights from/to an airport
    
    Returns departures or arrivals based on flight_type parameter
    """
    try:
        flights = await tracking_service.get_airport_flights(
            airport=airport.upper(),
            flight_type=flight_type,
            begin=begin,
            end=end
        )
        
        return {
            "airport": airport.upper(),
            "flight_type": flight_type,
            "count": len(flights),
            "flights": flights
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching airport flights: {str(e)}"
        )


@router.get("/flight/{flight_id}/enrich")
async def enrich_flight_with_tracking(
    flight_id: str,
    db: Session = Depends(get_db),
    tracking_service: FlightTrackingService = Depends(get_tracking_service)
):
    """
    Enrich a flight record with real-time tracking data
    
    Combines database flight data with ADSBDB aircraft info and OpenSky real-time status
    """
    try:
        flight = db.query(Flight).filter(Flight.id == flight_id).first()
        
        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")
        
        result = {
            "flight_id": str(flight.id),
            "flight_number": flight.flight_number,
            "scheduled_departure": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None,
            "scheduled_arrival": flight.scheduled_arrival.isoformat() if flight.scheduled_arrival else None,
            "aircraft_info": None,
            "real_time_status": None,
            "route_info": None
        }
        
        # Get aircraft info if registration available
        if flight.aircraft and flight.aircraft.registration:
            aircraft_info = await tracking_service.get_aircraft_info(flight.aircraft.registration)
            result["aircraft_info"] = aircraft_info
            
            # Get real-time status
            if aircraft_info and "mode_s" in aircraft_info:
                real_time = await tracking_service.get_real_time_flight_status(
                    registration=flight.aircraft.registration,
                    mode_s=aircraft_info["mode_s"]
                )
                result["real_time_status"] = real_time
        
        # Get route info
        if flight.origin_airport and flight.destination_airport:
            route_info = await tracking_service.get_flight_route_info(
                origin=flight.origin_airport.icao_code,
                destination=flight.destination_airport.icao_code,
                date=flight.scheduled_departure
            )
            result["route_info"] = route_info
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error enriching flight: {str(e)}"
        )
