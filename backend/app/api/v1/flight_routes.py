"""API v1 routes for flight management"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import math
import asyncio

from app.core.database import get_db
from app.models.flight import Flight
from app.models.aircraft import Aircraft, AircraftType
from app.models.airport import Airport
from app.models.airline import Airline
from app.services.ml_delay_predictor import MLDelayPredictor
from app.infrastructure.external.aviation_weather_client import AviationWeatherClient

router = APIRouter(prefix="/flights", tags=["Flights"])

# Global ML delay predictor instance
_global_delay_predictor = None
_global_weather_client = None

def get_delay_predictor() -> MLDelayPredictor:
    """Get ML delay predictor instance (singleton pattern)"""
    global _global_delay_predictor
    if _global_delay_predictor is None:
        _global_delay_predictor = MLDelayPredictor()
    return _global_delay_predictor

def get_weather_client() -> AviationWeatherClient:
    """Get weather client instance (singleton pattern)"""
    global _global_weather_client
    if _global_weather_client is None:
        _global_weather_client = AviationWeatherClient()
    return _global_weather_client


@router.get("/cargo")
async def get_cargo_flights(db: Session = Depends(get_db)):
    """
    Get all flights with cargo data
    
    Returns list of flights suitable for cargo analytics
    Prioritizes future flights over past flights
    """
    try:
        # Get current datetime for filtering
        now = datetime.now()
        
        # First try to get future flights (upcoming flights)
        flights = db.query(Flight).filter(
            Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
            Flight.passenger_count.isnot(None),
            Flight.scheduled_departure >= now
        ).order_by(Flight.scheduled_departure.asc()).limit(100).all()
        
        # If we don't have enough future flights, also include recent past flights
        if len(flights) < 50:
            past_flights = db.query(Flight).filter(
                Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
                Flight.passenger_count.isnot(None),
                Flight.scheduled_departure < now
            ).order_by(Flight.scheduled_departure.desc()).limit(100 - len(flights)).all()
            flights.extend(past_flights)
        
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
            
            # Get airline name
            airline_name = "American Airlines"  # Default
            if flight.airline_id:
                airline = db.query(Airline).filter(Airline.id == flight.airline_id).first()
                if airline:
                    airline_name = airline.name
            
            result.append({
                "id": str(flight.id),
                "flight_number": flight.flight_number,
                "airline_name": airline_name,
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


@router.get("/dashboard")
async def get_dashboard_flights(
    limit: Optional[int] = 100,
    include_historical: bool = True,
    days_back: Optional[int] = None,
    days_forward: Optional[int] = None,
    db: Session = Depends(get_db),
    delay_predictor: MLDelayPredictor = Depends(get_delay_predictor),
    weather_client: AviationWeatherClient = Depends(get_weather_client)
):
    """
    Get flights for the main Dashboard with delay predictions
    
    Returns flights with delay predictions, weather data, and airport traffic
    
    Args:
        limit: Maximum number of flights to return
        include_historical: If True, include historical flights (default: True)
        days_back: Number of days back to look (default: 30 if include_historical, else 1)
        days_forward: Number of days forward to look (default: 7)
    """
    try:
        now = datetime.now()
        
        # Determine date range
        if days_back is None:
            days_back = 30 if include_historical else 1
        if days_forward is None:
            days_forward = 7
        
        # Get flights in date range
        start_date = now - timedelta(days=days_back)
        end_date = now + timedelta(days=days_forward)
        
        flights = db.query(Flight).filter(
            Flight.scheduled_departure >= start_date,
            Flight.scheduled_departure <= end_date
        ).order_by(Flight.scheduled_departure.desc()).limit(limit).all()
        
        result = []
        for flight in flights:
            # Get related data
            origin = db.query(Airport).filter(Airport.id == flight.origin_airport_id).first()
            dest = db.query(Airport).filter(Airport.id == flight.destination_airport_id).first()
            aircraft = db.query(Aircraft).filter(Aircraft.id == flight.aircraft_id).first()
            airline = db.query(Airline).filter(Airline.id == flight.airline_id).first() if flight.airline_id else None
            
            if not origin or not dest:
                continue
            
            # Get aircraft type
            aircraft_type_str = "Unknown"
            if aircraft:
                aircraft_type = db.query(AircraftType).filter(AircraftType.id == aircraft.aircraft_type_id).first()
                if aircraft_type:
                    aircraft_type_str = f"{aircraft_type.manufacturer} {aircraft_type.model}"
            
            # Format times
            scheduled_departure_str = flight.scheduled_departure.strftime("%H:%M") if flight.scheduled_departure else None
            scheduled_arrival_str = flight.scheduled_arrival.strftime("%H:%M") if flight.scheduled_arrival else None
            
            # Calculate delay prediction
            # Use historical delay if available, otherwise predict
            delay_probability = 0.3
            estimated_delay_minutes = 0
            confidence = 0.7
            
            if flight.arrival_delay_minutes is not None:
                # Use actual delay if available
                estimated_delay_minutes = max(0, flight.arrival_delay_minutes)
                delay_probability = min(1.0, estimated_delay_minutes / 60.0)  # Normalize to 0-1
                confidence = 1.0
            elif delay_predictor.is_available() and flight.scheduled_departure:
                # Try ML prediction
                try:
                    flight_data = {
                        'departure_time': flight.scheduled_departure,
                        'origin': origin.iata_code,
                        'destination': dest.iata_code,
                        'distance_km': float(flight.distance_km) if flight.distance_km else 0
                    }
                    
                    # Get real weather for delay prediction
                    departure_weather = {
                        'temperature': 20.0,
                        'wind_speed': 10.0,
                        'visibility': 10.0,
                        'precipitation': 0.0
                    }
                    
                    # Try to get real weather for prediction
                    if origin and origin.icao_code:
                        try:
                            weather_obs = await asyncio.wait_for(
                                weather_client.get_weather_observation(origin.icao_code),
                                timeout=2.0
                            )
                            departure_weather = {
                                'temperature': weather_obs.temperature_celsius or 20.0,
                                'wind_speed': (weather_obs.wind_speed_knots or 0) * 1.852,  # knots to km/h
                                'visibility': (weather_obs.visibility_miles or 10.0) * 1.60934,  # miles to km
                                'precipitation': 0.0  # Not directly available in METAR
                            }
                        except:
                            pass  # Use defaults if weather API fails
                    
                    prediction = delay_predictor.predict(flight_data, departure_weather)
                    estimated_delay_minutes = max(0, prediction.get('predicted_delay_minutes', 0))
                    delay_probability = min(1.0, estimated_delay_minutes / 60.0)
                    confidence = prediction.get('confidence_score', 0.7)
                except Exception as e:
                    # Fallback to heuristic
                    estimated_delay_minutes = 15  # Default estimate
                    delay_probability = 0.3
                    confidence = 0.5
            
            # Get inbound aircraft (simplified - would need to query related flights)
            inbound_aircraft = None
            # Try to find inbound flight
            inbound_flight = db.query(Flight).filter(
                Flight.destination_airport_id == flight.origin_airport_id,
                Flight.scheduled_arrival <= flight.scheduled_departure,
                Flight.scheduled_arrival >= flight.scheduled_departure - timedelta(hours=2)
            ).order_by(Flight.scheduled_arrival.desc()).first()
            
            if inbound_flight:
                inbound_delay = inbound_flight.arrival_delay_minutes or 0
                inbound_aircraft = {
                    "flightNumber": inbound_flight.flight_number,
                    "status": "delayed" if inbound_delay > 15 else "on-time",
                    "delayMinutes": inbound_delay
                }
            
            # Calculate airport traffic (count flights in time window)
            origin_traffic_count = db.query(Flight).filter(
                Flight.origin_airport_id == flight.origin_airport_id,
                Flight.scheduled_departure >= flight.scheduled_departure - timedelta(hours=1),
                Flight.scheduled_departure <= flight.scheduled_departure + timedelta(hours=1)
            ).count()
            
            # Get airport capacity from database or use default
            airport_capacity = 60  # Default capacity
            if origin and origin.passenger_capacity:
                # Estimate based on passenger capacity (rough heuristic)
                airport_capacity = max(30, min(100, origin.passenger_capacity // 1000))
            current_traffic = min(origin_traffic_count, airport_capacity)
            
            # Get real weather data from API
            weather = {
                "temperature": 20.0,
                "humidity": 65.0,
                "wind_speed": 10.0,
                "visibility": 10.0,
                "conditions": "Clear"
            }
            
            # Try to get real weather if we have ICAO code
            if origin and origin.icao_code:
                try:
                    # Use asyncio to call async weather client
                    weather_obs = await asyncio.wait_for(
                        weather_client.get_weather_observation(origin.icao_code),
                        timeout=3.0  # 3 second timeout
                    )
                    
                    # Convert weather observation to dashboard format
                    weather = {
                        "temperature": weather_obs.temperature_celsius or 20.0,
                        "humidity": 65.0,  # Not in METAR, use default
                        "wind_speed": (weather_obs.wind_speed_knots or 0) * 1.852,  # Convert knots to km/h
                        "visibility": (weather_obs.visibility_miles or 10.0) * 1.60934,  # Convert miles to km
                        "conditions": weather_obs.weather_conditions or "Clear"
                    }
                    
                    # Determine conditions from weather string
                    wx_string = (weather_obs.weather_conditions or "").upper()
                    if "RA" in wx_string or "DZ" in wx_string:
                        weather["conditions"] = "Rain"
                    elif "SN" in wx_string:
                        weather["conditions"] = "Snow"
                    elif "FG" in wx_string or "BR" in wx_string:
                        weather["conditions"] = "Fog"
                    elif "TS" in wx_string:
                        weather["conditions"] = "Thunderstorm"
                    elif weather_obs.ceiling_feet and weather_obs.ceiling_feet < 1000:
                        weather["conditions"] = "Low Clouds"
                    else:
                        weather["conditions"] = "Clear"
                    
                except asyncio.TimeoutError:
                    # Weather API timeout - use default
                    pass
                except Exception as e:
                    # Weather API error - use default, log for debugging
                    import logging
                    logging.warning(f"Weather API error for {origin.icao_code}: {e}")
                    pass
            
            result.append({
                "id": str(flight.id),
                "flightNumber": flight.flight_number,
                "origin": origin.iata_code,
                "destination": dest.iata_code,
                "scheduledDeparture": scheduled_departure_str,
                "scheduledArrival": scheduled_arrival_str,
                "delayPrediction": {
                    "delay_probability": delay_probability,
                    "estimated_delay_minutes": int(estimated_delay_minutes),
                    "confidence": confidence
                },
                "weather": weather,
                "inboundAircraft": inbound_aircraft,
                "airportTraffic": {
                    "airport_code": origin.iata_code,
                    "current_traffic": current_traffic,
                    "capacity": airport_capacity
                }
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard flights: {str(e)}"
        )


@router.get("/operations")
async def get_flight_operations(
    limit: Optional[int] = 50,
    db: Session = Depends(get_db)
):
    """
    Get flight operations data for FlightOpsDashboard
    
    Returns flights with status, delays, gates, and operational metrics
    """
    try:
        now = datetime.now()
        
        # Get recent and upcoming flights
        flights = db.query(Flight).filter(
            Flight.scheduled_departure >= now - timedelta(hours=6),
            Flight.scheduled_departure <= now + timedelta(hours=12)
        ).order_by(Flight.scheduled_departure.asc()).limit(limit).all()
        
        result = []
        for flight in flights:
            origin = db.query(Airport).filter(Airport.id == flight.origin_airport_id).first()
            dest = db.query(Airport).filter(Airport.id == flight.destination_airport_id).first()
            
            if not origin or not dest:
                continue
            
            # Calculate delay
            delay_minutes = flight.arrival_delay_minutes or flight.departure_delay_minutes or 0
            
            # Determine status
            if flight.cancellation_status == 'C':
                status = 'Cancelled'
            elif delay_minutes >= 30:
                status = 'At Risk'
            elif delay_minutes >= 15:
                status = 'Warning'
            else:
                status = 'On Time'
            
            # Calculate risk percentage (0-100)
            risk = min(100, max(0, delay_minutes * 2))  # Simple heuristic
            
            # ETA
            if flight.actual_arrival:
                eta = flight.actual_arrival.strftime("%H:%M")
            elif flight.scheduled_arrival:
                # Adjust for delay
                eta_time = flight.scheduled_arrival + timedelta(minutes=delay_minutes)
                eta = eta_time.strftime("%H:%M")
            else:
                eta = "N/A"
            
            # Gate (simplified - would need gate assignment data)
            gate = f"{origin.iata_code[0]}{hash(flight.id) % 20 + 1}"
            
            # Weather condition (simplified)
            weather_conditions = ["Clear", "Moderate", "Heavy Rain", "Snow"]
            weather = weather_conditions[hash(str(flight.id)) % len(weather_conditions)]
            
            # Traffic level
            traffic_levels = ["Low", "Normal", "High"]
            traffic = traffic_levels[min(2, (delay_minutes // 20))]
            
            result.append({
                "id": flight.flight_number,
                "status": status,
                "delay": delay_minutes,
                "gate": gate,
                "eta": eta,
                "risk": risk,
                "weather": weather,
                "traffic": traffic,
                "origin": origin.iata_code,
                "destination": dest.iata_code,
                "flight_number": flight.flight_number,
                "scheduled_departure": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get flight operations: {str(e)}"
        )


@router.get("/weather")
async def get_weather_data(
    airport_code: Optional[str] = None,
    limit: Optional[int] = 20,
    db: Session = Depends(get_db),
    weather_client: AviationWeatherClient = Depends(get_weather_client)
):
    """
    Get weather data for airports
    
    Returns weather information for airports with active flights
    If airport_code is provided, returns weather for that specific airport
    """
    try:
        now = datetime.now()
        
        # Get airports with recent/upcoming flights
        if airport_code:
            # Get specific airport
            airport = db.query(Airport).filter(
                (Airport.iata_code == airport_code.upper()) | 
                (Airport.icao_code == airport_code.upper())
            ).first()
            
            if not airport:
                raise HTTPException(status_code=404, detail=f"Airport {airport_code} not found")
            
            airports = [airport]
        else:
            # Get airports with flights in next 24 hours
            flights = db.query(Flight).filter(
                Flight.scheduled_departure >= now,
                Flight.scheduled_departure <= now + timedelta(hours=24)
            ).limit(100).all()
            
            # Get unique airports
            airport_ids = set()
            for flight in flights:
                if flight.origin_airport_id:
                    airport_ids.add(flight.origin_airport_id)
                if flight.destination_airport_id:
                    airport_ids.add(flight.destination_airport_id)
            
            airports = db.query(Airport).filter(Airport.id.in_(list(airport_ids))).limit(limit).all()
        
        result = []
        for airport in airports:
            weather_data = {
                "airport_code": airport.iata_code,
                "airport_name": airport.name,
                "icao_code": airport.icao_code,
                "temperature": None,
                "humidity": None,
                "wind_speed": None,
                "wind_direction": None,
                "visibility": None,
                "conditions": "Unknown",
                "pressure": None,
                "last_updated": None,
                "error": None
            }
            
            # Try to get real weather if we have ICAO code
            if airport.icao_code:
                try:
                    weather_obs = await asyncio.wait_for(
                        weather_client.get_weather_observation(airport.icao_code),
                        timeout=3.0
                    )
                    
                    weather_data.update({
                        "temperature": weather_obs.temperature_celsius,
                        "wind_speed": (weather_obs.wind_speed_knots or 0) * 1.852,  # knots to km/h
                        "wind_direction": weather_obs.wind_direction_degrees,
                        "visibility": (weather_obs.visibility_miles or 0) * 1.60934,  # miles to km
                        "pressure": weather_obs.pressure_mb,
                        "last_updated": weather_obs.observation_time.isoformat() if weather_obs.observation_time else None,
                        "conditions": weather_obs.weather_conditions or "Clear"
                    })
                    
                    # Determine conditions from weather string
                    wx_string = (weather_obs.weather_conditions or "").upper()
                    if "RA" in wx_string or "DZ" in wx_string:
                        weather_data["conditions"] = "Rain"
                    elif "SN" in wx_string:
                        weather_data["conditions"] = "Snow"
                    elif "FG" in wx_string or "BR" in wx_string:
                        weather_data["conditions"] = "Fog"
                    elif "TS" in wx_string:
                        weather_data["conditions"] = "Thunderstorm"
                    elif weather_obs.ceiling_feet and weather_obs.ceiling_feet < 1000:
                        weather_data["conditions"] = "Low Clouds"
                    else:
                        weather_data["conditions"] = "Clear"
                    
                except asyncio.TimeoutError:
                    weather_data["error"] = "Weather API timeout"
                except Exception as e:
                    weather_data["error"] = f"Weather API error: {str(e)[:100]}"
            
            result.append(weather_data)
        
        return {
            "count": len(result),
            "weather_data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get weather data: {str(e)}"
        )


@router.get("/traffic")
async def get_traffic_data(
    airport_code: Optional[str] = None,
    hours_ahead: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get airport traffic data
    
    Returns traffic statistics for airports with active flights
    If airport_code is provided, returns traffic for that specific airport
    """
    try:
        now = datetime.now()
        end_time = now + timedelta(hours=hours_ahead)
        
        if airport_code:
            # Get specific airport
            airport = db.query(Airport).filter(
                (Airport.iata_code == airport_code.upper()) | 
                (Airport.icao_code == airport_code.upper())
            ).first()
            
            if not airport:
                raise HTTPException(status_code=404, detail=f"Airport {airport_code} not found")
            
            airports = [airport]
        else:
            # Get airports with flights in the time window
            flights = db.query(Flight).filter(
                Flight.scheduled_departure >= now,
                Flight.scheduled_departure <= end_time
            ).limit(200).all()
            
            # Get unique airports
            airport_ids = set()
            for flight in flights:
                if flight.origin_airport_id:
                    airport_ids.add(flight.origin_airport_id)
                if flight.destination_airport_id:
                    airport_ids.add(flight.destination_airport_id)
            
            airports = db.query(Airport).filter(Airport.id.in_(list(airport_ids))).all()
        
        result = []
        for airport in airports:
            # Count departures in next hour
            next_hour = now + timedelta(hours=1)
            departures_next_hour = db.query(Flight).filter(
                Flight.origin_airport_id == airport.id,
                Flight.scheduled_departure >= now,
                Flight.scheduled_departure <= next_hour
            ).count()
            
            # Count arrivals in next hour
            arrivals_next_hour = db.query(Flight).filter(
                Flight.destination_airport_id == airport.id,
                Flight.scheduled_arrival >= now,
                Flight.scheduled_arrival <= next_hour
            ).count()
            
            # Count total flights in time window
            total_departures = db.query(Flight).filter(
                Flight.origin_airport_id == airport.id,
                Flight.scheduled_departure >= now,
                Flight.scheduled_departure <= end_time
            ).count()
            
            total_arrivals = db.query(Flight).filter(
                Flight.destination_airport_id == airport.id,
                Flight.scheduled_arrival >= now,
                Flight.scheduled_arrival <= end_time
            ).count()
            
            # Estimate capacity
            airport_capacity = 60  # Default
            if airport.passenger_capacity:
                airport_capacity = max(30, min(100, airport.passenger_capacity // 1000))
            
            # Calculate utilization
            total_movements = departures_next_hour + arrivals_next_hour
            utilization = min(100, (total_movements / airport_capacity) * 100) if airport_capacity > 0 else 0
            
            # Determine traffic level
            if utilization >= 80:
                traffic_level = "High"
            elif utilization >= 50:
                traffic_level = "Moderate"
            else:
                traffic_level = "Low"
            
            result.append({
                "airport_code": airport.iata_code,
                "airport_name": airport.name,
                "icao_code": airport.icao_code,
                "departures_next_hour": departures_next_hour,
                "arrivals_next_hour": arrivals_next_hour,
                "total_departures": total_departures,
                "total_arrivals": total_arrivals,
                "total_movements": total_movements,
                "capacity": airport_capacity,
                "utilization_percent": round(utilization, 1),
                "traffic_level": traffic_level,
                "time_window_hours": hours_ahead
            })
        
        # Sort by utilization (busiest first)
        result.sort(key=lambda x: x["utilization_percent"], reverse=True)
        
        return {
            "count": len(result),
            "traffic_data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get traffic data: {str(e)}"
        )
