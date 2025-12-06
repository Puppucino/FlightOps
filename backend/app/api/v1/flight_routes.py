"""API v1 routes for flight management"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.flight import Flight
from app.models.aircraft import Aircraft, AircraftType
from app.models.airport import Airport

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.get("/cargo")
async def get_cargo_flights(db: Session = Depends(get_db)):
    """
    Get all flights with cargo data
    
    Returns list of flights suitable for cargo analytics
    """
    try:
        flights = db.query(Flight).filter(
            Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
            Flight.passenger_count.isnot(None)
        ).limit(100).all()
        
        result = []
        for flight in flights:
            # Get related data
            origin = db.query(Airport).filter(Airport.id == flight.origin_airport_id).first()
            dest = db.query(Airport).filter(Airport.id == flight.destination_airport_id).first()
            aircraft = db.query(Aircraft).filter(Aircraft.id == flight.aircraft_id).first()
            
            # Get aircraft type
            aircraft_type_str = "Unknown"
            if aircraft:
                aircraft_type = db.query(AircraftType).filter(AircraftType.id == aircraft.aircraft_type_id).first()
                if aircraft_type:
                    aircraft_type_str = f"{aircraft_type.manufacturer} {aircraft_type.model}"
            
            result.append({
                "id": str(flight.id),
                "flight_number": flight.flight_number,
                "airline_name": "Airline AB",  # TODO: Get from airline relation
                "aircraft_registration": aircraft.registration if aircraft else "N/A",
                "aircraft_type": aircraft_type_str,
                "origin_airport": origin.name if origin else "Unknown",
                "origin_airport_code": origin.iata_code if origin else "N/A",
                "destination_airport": dest.name if dest else "Unknown",
                "destination_airport_code": dest.iata_code if dest else "N/A",
                "scheduled_departure": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None,
                "scheduled_arrival": flight.scheduled_arrival.isoformat() if flight.scheduled_arrival else None,
                "flight_status": flight.flight_status or "scheduled",
                "distance_km": float(flight.distance_km) if flight.distance_km else 0,
                "flight_type": flight.flight_type
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get flights: {str(e)}"
        )
