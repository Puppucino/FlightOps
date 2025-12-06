"""API v1 routes for cargo capacity prediction"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.ml_service import MLService
from app.services.traffic_estimator import TrafficEstimator
from app.models.flight import Flight
from app.models.aircraft import Aircraft, AircraftType
from app.models.airport import Airport

router = APIRouter(prefix="/cargo", tags=["Cargo Capacity Prediction"])

# Global ML service instance
_global_ml_service = None


def get_ml_service() -> MLService:
    """Get ML service instance (singleton pattern)"""
    global _global_ml_service
    if _global_ml_service is None:
        _global_ml_service = MLService()
    return _global_ml_service


class CargoCapacityPredictionRequest(BaseModel):
    """Request for cargo capacity prediction"""
    flight_number: Optional[str] = None
    flight_id: Optional[str] = None
    aircraft_type: str
    passenger_count: int = Field(..., ge=0, description="Number of passengers")
    origin: str = Field(..., min_length=3, max_length=3, description="Origin airport IATA code")
    destination: str = Field(..., min_length=3, max_length=3, description="Destination airport IATA code")
    flight_date: datetime = Field(..., description="Flight departure datetime")
    fuel_weight_kg: Optional[float] = Field(None, ge=0, description="Fuel weight in kg (optional)")
    days_before_flight: int = Field(0, ge=0, le=365, description="Days before flight (0 = day of flight)")


class CargoCapacityPredictionResponse(BaseModel):
    """Response for cargo capacity prediction"""
    available_weight_kg: float
    available_volume_m3: float
    confidence_interval_95_lower_weight: float
    confidence_interval_95_upper_weight: float
    confidence_interval_95_lower_volume: float
    confidence_interval_95_upper_volume: float
    utilization_percentage: float
    weight_utilization_pct: float
    volume_utilization_pct: float
    constraining_factor: str
    predicted_cargo_demand_kg: float
    overbooking_risk: str
    baggage_prediction: dict
    aircraft_max_cargo_weight_kg: float
    aircraft_max_cargo_volume_m3: float
    predicted_baggage_weight_kg: float
    predicted_baggage_volume_m3: float
    fuel_weight_kg: float
    days_before_flight: int


@router.post("/predict-capacity", response_model=CargoCapacityPredictionResponse)
async def predict_cargo_capacity(
    request: CargoCapacityPredictionRequest,
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Predict available cargo capacity X days before flight
    
    This endpoint predicts how much cargo space (weight and volume) will be available
    for sale on a flight, given the predicted passenger baggage requirements.
    
    The prediction accounts for:
    - Predicted passenger baggage weight/volume
    - Fuel requirements
    - Aircraft capacity constraints
    - Temporal and route-specific patterns
    - Uncertainty based on days before flight
    """
    try:
        prediction = await ml_service.predict_available_cargo_capacity(
            aircraft_type=request.aircraft_type,
            passenger_count=request.passenger_count,
            origin=request.origin.upper(),
            destination=request.destination.upper(),
            flight_date=request.flight_date,
            fuel_weight_kg=request.fuel_weight_kg,
            days_before_flight=request.days_before_flight,
            aircraft_registration=None  # Can be added to request model if needed
        )
        
        return CargoCapacityPredictionResponse(**prediction)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict-capacity-by-flight/{flight_id}", response_model=CargoCapacityPredictionResponse)
async def predict_cargo_capacity_by_flight(
    flight_id: str,
    passenger_count: Optional[int] = None,
    days_before_flight: int = 0,
    db: Session = Depends(get_db),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Predict cargo capacity for an existing flight in the database
    
    Uses flight data from database, but can override passenger_count and days_before_flight
    """
    try:
        # Get flight from database
        flight = db.query(Flight).filter(Flight.id == flight_id).first()
        if not flight:
            raise HTTPException(status_code=404, detail=f"Flight {flight_id} not found")
        
        # Get aircraft type
        aircraft = db.query(Aircraft).filter(Aircraft.id == flight.aircraft_id).first()
        if not aircraft:
            raise HTTPException(status_code=404, detail=f"Aircraft not found for flight {flight_id}")
        
        aircraft_type = db.query(AircraftType).filter(AircraftType.id == aircraft.aircraft_type_id).first()
        if not aircraft_type:
            raise HTTPException(status_code=404, detail=f"Aircraft type not found for flight {flight_id}")
        
        aircraft_type_str = f"{aircraft_type.manufacturer} {aircraft_type.model}"
        
        # Get origin and destination
        origin_airport = db.query(Airport).filter(Airport.id == flight.origin_airport_id).first()
        dest_airport = db.query(Airport).filter(Airport.id == flight.destination_airport_id).first()
        
        if not origin_airport or not dest_airport:
            raise HTTPException(status_code=404, detail="Origin or destination airport not found")
        
        # Use provided passenger_count or flight's passenger_count
        pax_count = passenger_count if passenger_count is not None else (flight.passenger_count or 0)
        if pax_count == 0:
            raise HTTPException(
                status_code=400,
                detail="passenger_count is required (not provided and not in flight record)"
            )
        
        # Predict (with aircraft registration for ADSBDB enrichment)
        aircraft_registration = aircraft.registration if aircraft else None
        prediction = await ml_service.predict_available_cargo_capacity(
            aircraft_type=aircraft_type_str,
            passenger_count=pax_count,
            origin=origin_airport.iata_code,
            destination=dest_airport.iata_code,
            flight_date=flight.scheduled_departure,
            fuel_weight_kg=float(flight.fuel_weight_kg) if flight.fuel_weight_kg else None,
            days_before_flight=days_before_flight,
            aircraft_registration=aircraft_registration
        )
        
        return CargoCapacityPredictionResponse(**prediction)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/analytics/{flight_id}")
async def get_cargo_analytics(
    flight_id: str,
    days_before_flight: int = 0,
    db: Session = Depends(get_db),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Get comprehensive cargo analytics for a flight including predictions
    
    This endpoint accepts either:
    - UUID flight ID
    - Flight number (e.g., "AB101")
    
    Returns both actual data (if available) and predictions
    """
    try:
        # Try to get flight - first try as UUID, then as flight_number
        flight = None
        try:
            # Try UUID format
            import uuid as uuid_lib
            uuid_lib.UUID(flight_id)  # Validate UUID format
            flight = db.query(Flight).filter(Flight.id == flight_id).first()
        except (ValueError, TypeError):
            # Not a valid UUID, try flight_number instead
            flight = db.query(Flight).filter(Flight.flight_number == flight_id).first()
        
        # If still not found (including mock IDs), try to get first available flight
        if not flight:
            # For mock IDs or any ID not found, return first flight with passenger data
            flight = db.query(Flight).filter(
                Flight.passenger_count.isnot(None),
                Flight.passenger_count > 0
            ).first()
            
            if not flight:
                # Last resort: get any flight
                flight = db.query(Flight).first()
        
        if not flight:
            raise HTTPException(status_code=404, detail=f"No flights found in database")
        
        # Get aircraft and type
        aircraft = db.query(Aircraft).filter(Aircraft.id == flight.aircraft_id).first()
        if not aircraft:
            raise HTTPException(status_code=404, detail=f"Aircraft not found")
        
        aircraft_type = db.query(AircraftType).filter(AircraftType.id == aircraft.aircraft_type_id).first()
        if not aircraft_type:
            raise HTTPException(status_code=404, detail=f"Aircraft type not found")
        
        aircraft_type_str = f"{aircraft_type.manufacturer} {aircraft_type.model}"
        
        # Get airports (Airport is already imported at the top)
        origin_airport = db.query(Airport).filter(Airport.id == flight.origin_airport_id).first()
        dest_airport = db.query(Airport).filter(Airport.id == flight.destination_airport_id).first()
        
        if not origin_airport or not dest_airport:
            raise HTTPException(status_code=404, detail="Airports not found")
        
        # Get predictions
        pax_count = flight.passenger_count or 0
        if pax_count > 0:
            aircraft_registration = aircraft.registration if aircraft else None
            prediction = await ml_service.predict_available_cargo_capacity(
                aircraft_type=aircraft_type_str,
                passenger_count=pax_count,
                origin=origin_airport.iata_code,
                destination=dest_airport.iata_code,
                flight_date=flight.scheduled_departure,
                fuel_weight_kg=float(flight.fuel_weight_kg) if flight.fuel_weight_kg else None,
                days_before_flight=days_before_flight,
                aircraft_registration=aircraft_registration
            )
        else:
            # Return default/empty prediction if no passenger data
            max_cargo_weight = float(aircraft_type.cargo_capacity_tonnes * 1000) if aircraft_type and aircraft_type.cargo_capacity_tonnes else 0.0
            prediction = {
                'available_weight_kg': max_cargo_weight,
                'available_volume_m3': 0.0,
                'confidence_interval_95_lower_weight': max_cargo_weight * 0.9,
                'confidence_interval_95_upper_weight': max_cargo_weight * 1.1,
                'confidence_interval_95_lower_volume': 0.0,
                'confidence_interval_95_upper_volume': 0.0,
                'utilization_percentage': 0.0,
                'weight_utilization_pct': 0.0,
                'volume_utilization_pct': 0.0,
                'constraining_factor': 'weight',
                'predicted_cargo_demand_kg': 0.0,
                'overbooking_risk': 'low',
                'baggage_prediction': {},
                'aircraft_max_cargo_weight_kg': max_cargo_weight,
                'aircraft_max_cargo_volume_m3': 0.0,
                'predicted_baggage_weight_kg': 0.0,
                'predicted_baggage_volume_m3': 0.0,
                'fuel_weight_kg': float(flight.fuel_weight_kg) if flight.fuel_weight_kg else 0.0,
                'days_before_flight': days_before_flight
            }
        
        # Build response with actual and predicted data
        return {
            "flight": {
                "id": str(flight.id),
                "flight_number": flight.flight_number,
                "airline_name": "Airline AB",  # TODO: Get from airline relation
                "aircraft_registration": aircraft.registration if aircraft else "N/A",
                "aircraft_type": aircraft_type_str,
                "origin_airport": origin_airport.name if origin_airport else "Unknown",
                "origin_airport_code": origin_airport.iata_code if origin_airport else "N/A",
                "destination_airport": dest_airport.name if dest_airport else "Unknown",
                "destination_airport_code": dest_airport.iata_code if dest_airport else "N/A",
                "scheduled_departure": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None,
                "scheduled_arrival": flight.scheduled_arrival.isoformat() if flight.scheduled_arrival else None,
                "flight_status": flight.flight_status or "scheduled",
                "distance_km": float(flight.distance_km) if flight.distance_km else 0,
                "flight_type": flight.flight_type,
                "passenger_count": flight.passenger_count,
                "status": flight.flight_status
            },
            "actual_data": {
                "cargo_weight_kg": float(flight.cargo_weight_tonnes * 1000) if flight.cargo_weight_tonnes else None,
                "cargo_volume_m3": float(flight.cargo_volume_m3) if flight.cargo_volume_m3 else None,
                "baggage_weight_kg": float(flight.baggage_weight_kg) if flight.baggage_weight_kg else None,
                "baggage_volume_m3": float(flight.baggage_volume_m3) if flight.baggage_volume_m3 else None,
                "fuel_weight_kg": float(flight.fuel_weight_kg) if flight.fuel_weight_kg else None
            },
            "prediction": {
                "predicted_cargo_volume": prediction.get('predicted_cargo_demand_kg', 0) / 1000.0,
                "confidence": max(0, min(1, 1.0 - (
                    (prediction.get('available_weight_confidence_upper', prediction.get('available_weight_kg', 0)) - 
                     prediction.get('available_weight_confidence_lower', 0)) / 
                    max(prediction.get('available_weight_kg', 1), 1)
                ))),
                # Include full ML prediction details for frontend
                "available_weight_kg": prediction.get('available_weight_kg', 0),
                "available_volume_m3": prediction.get('available_volume_m3', 0),
                "confidence_interval_95_lower_weight": prediction.get('available_weight_confidence_lower', 0),
                "confidence_interval_95_upper_weight": prediction.get('available_weight_confidence_upper', 0),
                "confidence_interval_95_lower_volume": prediction.get('available_volume_confidence_lower', 0),
                "confidence_interval_95_upper_volume": prediction.get('available_volume_confidence_upper', 0),
                "constraining_factor": prediction.get('constraining_factor', 'weight'),
                "overbooking_risk": prediction.get('overbooking_risk', 'low'),
                "baggage_prediction": prediction.get('baggage_prediction', {}),
                "aircraft_max_cargo_weight_kg": prediction.get('aircraft_max_cargo_weight_kg', 0),
                "aircraft_max_cargo_volume_m3": prediction.get('aircraft_max_cargo_volume_m3', 0),
                "predicted_baggage_weight_kg": prediction.get('predicted_baggage_weight_kg', 0),
                "predicted_baggage_volume_m3": prediction.get('predicted_baggage_volume_m3', 0)
            },
            "storage_availability": {
                "aircraft_id": str(aircraft.id),
                "aircraft_registration": aircraft.registration,
                "total_capacity_tonnes": prediction.get('aircraft_max_cargo_weight_kg', 0) / 1000.0,
                "current_cargo_tonnes": (flight.cargo_weight_tonnes or 0),
                "available_capacity_tonnes": prediction.get('available_weight_kg', 0) / 1000.0,
                "utilization_percentage": prediction.get('utilization_percentage', 0),
                "predicted_demand_tonnes": prediction.get('predicted_cargo_demand_kg', 0) / 1000.0,
                "confidence_score": 1.0 - (prediction.get('available_weight_confidence_upper', prediction.get('available_weight_kg', 0)) - prediction.get('available_weight_confidence_lower', 0)) / (prediction.get('available_weight_kg', 1) + 1)
            },
            "loading_progress": {
                "flight_id": str(flight.id),
                "flight_number": flight.flight_number,
                "total_cargo_tonnes": prediction.get('aircraft_max_cargo_weight_kg', 0) / 1000.0,
                "loaded_cargo_tonnes": float(flight.cargo_weight_tonnes or 0),
                "loading_percentage": min(100, max(0, (float(flight.cargo_weight_tonnes or 0) / max(prediction.get('aircraft_max_cargo_weight_kg', 1) / 1000.0, 0.01)) * 100)) if prediction.get('aircraft_max_cargo_weight_kg', 0) > 0 else 0,
                "status": "in_progress" if (flight.cargo_weight_tonnes or 0) > 0 and (flight.cargo_weight_tonnes or 0) < (prediction.get('aircraft_max_cargo_weight_kg', 0) / 1000.0 * 0.9) else ("completed" if (flight.cargo_weight_tonnes or 0) >= (prediction.get('aircraft_max_cargo_weight_kg', 0) / 1000.0 * 0.9) else "not_started")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cargo analytics: {str(e)}"
        )


@router.get("/calendar")
async def get_cargo_calendar(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Get calendar view of upcoming flights with cargo utilization predictions
    
    Returns flights for the specified month/year (or current month if not specified)
    with traffic estimates and cargo predictions based on peak seasons
    """
    try:
        # Use current date if not specified
        today = date.today()
        target_year = year or today.year
        target_month = month or today.month
        
        # Calculate date range for the month
        start_date = date(target_year, target_month, 1)
        if target_month == 12:
            end_date = date(target_year + 1, 1, 1)
        else:
            end_date = date(target_year, target_month + 1, 1)
        
        # Get flights in the date range
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.min.time())
        
        # Get all flights in the requested month/year range
        # This ensures calendar view shows flights for the selected month
        # Use the same filtering logic as the list view endpoint
        flights_query = db.query(Flight).filter(
            Flight.scheduled_departure >= start_datetime,
            Flight.scheduled_departure < end_datetime,
            Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
            Flight.passenger_count.isnot(None)
        )
        
        flights = flights_query.order_by(Flight.scheduled_departure.asc()).all()
        
        # Debug: Log flight count
        print(f"Calendar endpoint: Found {len(flights)} flights for {target_year}-{target_month}")
        if len(flights) > 0:
            print(f"  First flight: {flights[0].flight_number} on {flights[0].scheduled_departure}")
        
        # If no flights in requested month, try to find the first month with flights
        # Only auto-navigate if year/month not explicitly provided (default/current month)
        # This prevents infinite loops when user explicitly requests a month with no flights
        if len(flights) == 0 and not year and not month:
            # Find first month with flights
            first_flight = db.query(Flight).filter(
                Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
                Flight.passenger_count.isnot(None),
                Flight.scheduled_departure >= datetime.now()
            ).order_by(Flight.scheduled_departure.asc()).first()
            
            if first_flight:
                first_date = first_flight.scheduled_departure.date()
                # Update target to first month with flights
                target_year = first_date.year
                target_month = first_date.month
                start_date = date(target_year, target_month, 1)
                if target_month == 12:
                    end_date = date(target_year + 1, 1, 1)
                else:
                    end_date = date(target_year, target_month + 1, 1)
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.min.time())
                
                flights = db.query(Flight).filter(
                    Flight.scheduled_departure >= start_datetime,
                    Flight.scheduled_departure < end_datetime,
                    Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
                    Flight.passenger_count.isnot(None)
                ).order_by(Flight.scheduled_departure.asc()).all()
                
                print(f"Calendar endpoint: Auto-navigated to {first_date.year}-{first_date.month}, found {len(flights)} flights")
                
                # Update return values to reflect the month we're actually showing
                target_year = first_date.year
                target_month = first_date.month
        
        # Initialize traffic estimator
        traffic_estimator = TrafficEstimator()
        
        # Get peak seasons for the month
        peak_seasons = traffic_estimator.get_peak_seasons_for_month(target_year, target_month)
        
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
            
            # Get flight date
            flight_date = flight.scheduled_departure.date() if flight.scheduled_departure else today
            pax_count = flight.passenger_count or 0
            
            # Estimate traffic
            route = f"{origin.iata_code}-{dest.iata_code}" if origin and dest else None
            traffic_est = traffic_estimator.estimate_passenger_traffic(
                base_passenger_count=pax_count,
                flight_date=flight_date,
                route=route
            )
            
            # Get cargo prediction if we have passenger data
            cargo_prediction = None
            if pax_count > 0 and origin and dest:
                try:
                    days_before = (flight_date - today).days
                    days_before = max(0, days_before)  # Don't use negative days
                    
                    aircraft_registration = aircraft.registration if aircraft else None
                    cargo_prediction = await ml_service.predict_available_cargo_capacity(
                        aircraft_type=aircraft_type_str,
                        passenger_count=traffic_est["estimated_passenger_count"],
                        origin=origin.iata_code,
                        destination=dest.iata_code,
                        flight_date=flight.scheduled_departure,
                        fuel_weight_kg=float(flight.fuel_weight_kg) if flight.fuel_weight_kg else None,
                        days_before_flight=days_before,
                        aircraft_registration=aircraft_registration
                    )
                except Exception as e:
                    # If prediction fails, continue without it
                    print(f"Warning: Failed to predict cargo for flight {flight.id}: {e}")
            
            result.append({
                "flight_id": str(flight.id),
                "flight_number": flight.flight_number,
                "date": flight_date.isoformat(),
                "scheduled_departure": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None,
                "origin": origin.iata_code if origin else "N/A",
                "destination": dest.iata_code if dest else "N/A",
                "route": route,
                "aircraft_type": aircraft_type_str,
                "passenger_count": pax_count,
                "traffic_estimation": traffic_est,
                "cargo_prediction": cargo_prediction,
                "utilization_percentage": cargo_prediction.get("utilization_percentage", 0) if cargo_prediction else 0,
                "available_weight_kg": cargo_prediction.get("available_weight_kg", 0) if cargo_prediction else 0,
                "available_volume_m3": cargo_prediction.get("available_volume_m3", 0) if cargo_prediction else 0,
                "overbooking_risk": cargo_prediction.get("overbooking_risk", "low") if cargo_prediction else "low",
            })
        
        # Debug: Log final response
        print(f"Calendar endpoint: Returning {len(result)} flights for {target_year}-{target_month}")
        
        return {
            "year": target_year,
            "month": target_month,
            "peak_seasons": [
                {
                    "date": p["date"].isoformat(),
                    "day": p["day"],
                    "multiplier": p["multiplier"],
                    "type": p["type"],
                    "is_holiday": p["is_holiday"],
                    "is_school_holiday": p["is_school_holiday"],
                }
                for p in peak_seasons
            ],
            "flights": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cargo calendar: {str(e)}"
        )
