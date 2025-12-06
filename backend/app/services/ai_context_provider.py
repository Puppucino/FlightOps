"""
AI Context Provider
Provides comprehensive context about the application, database, and services to the AI agent
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.flight import Flight
from app.models.aircraft import Aircraft, AircraftType
from app.models.airport import Airport
from app.models.airline import Airline
from app.models.weather import WeatherData
from app.models.traffic import AirportTraffic
from app.models.prediction import (
    FlightDelayPrediction,
    CargoPrediction,
    PassengerTrafficPrediction,
    MLModel
)
from loguru import logger


class AIContextProvider:
    """Provides comprehensive context to AI agent about the application"""
    
    def __init__(self, db: Session):
        """
        Initialize context provider
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_application_context(self) -> Dict[str, Any]:
        """
        Get comprehensive application context
        
        Returns:
            Dictionary with all application information
        """
        return {
            "application_name": "Cargo Analytics System",
            "version": "1.0.0",
            "description": "Intelligent cargo capacity prediction and flight analytics system",
            "database_tables": self._get_database_schema(),
            "available_services": self._get_available_services(),
            "api_endpoints": self._get_api_endpoints(),
            "data_statistics": self._get_data_statistics(),
            "current_time": datetime.now().isoformat()
        }
    
    def _get_database_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        return {
            "flights": {
                "description": "Scheduled and actual flight information",
                "key_fields": [
                    "id", "flight_number", "airline_id", "aircraft_id",
                    "origin_airport_id", "destination_airport_id",
                    "scheduled_departure", "scheduled_arrival",
                    "actual_departure", "actual_arrival",
                    "departure_delay_minutes", "arrival_delay_minutes",
                    "passenger_count", "cargo_weight_tonnes", "cargo_volume_m3",
                    "baggage_weight_kg", "baggage_volume_m3",
                    "flight_status", "distance_km", "flight_type"
                ],
                "relationships": [
                    "airline", "aircraft", "origin_airport", "destination_airport",
                    "delay_predictions"
                ]
            },
            "aircraft": {
                "description": "Individual aircraft records",
                "key_fields": [
                    "id", "registration", "aircraft_type_id", "airline_id",
                    "year_manufactured", "maintenance_status", "is_active"
                ],
                "relationships": ["aircraft_type", "airline", "flights"]
            },
            "aircraft_types": {
                "description": "Aircraft specifications and capacity",
                "key_fields": [
                    "id", "manufacturer", "model", "icao_code",
                    "max_cargo_weight_kg", "max_cargo_volume_m3",
                    "max_takeoff_weight_kg", "range_km", "cruise_speed_kmh"
                ]
            },
            "airports": {
                "description": "Airport information",
                "key_fields": [
                    "id", "icao_code", "iata_code", "name", "city", "country",
                    "latitude", "longitude", "passenger_capacity",
                    "cargo_capacity_tonnes", "runways"
                ],
                "relationships": [
                    "flights_origin", "flights_destination",
                    "weather_data", "airport_traffic"
                ]
            },
            "airlines": {
                "description": "Airline information",
                "key_fields": [
                    "id", "icao_code", "iata_code", "name", "country"
                ],
                "relationships": ["aircraft", "flights"]
            },
            "weather_data": {
                "description": "Historical weather conditions at airports",
                "key_fields": [
                    "id", "airport_id", "observation_time",
                    "temperature_celsius", "wind_speed_kmh", "wind_direction_degrees",
                    "visibility_km", "precipitation_mm", "pressure_mb"
                ]
            },
            "airport_traffic": {
                "description": "Passenger and aircraft traffic patterns",
                "key_fields": [
                    "id", "airport_id", "date", "passenger_count",
                    "aircraft_movements", "traffic_level"
                ]
            },
            "flight_delay_predictions": {
                "description": "ML delay predictions",
                "key_fields": [
                    "id", "flight_id", "prediction_time",
                    "delay_probability", "estimated_delay_minutes", "confidence"
                ]
            },
            "cargo_predictions": {
                "description": "ML cargo demand predictions",
                "key_fields": [
                    "id", "aircraft_id", "airport_id", "prediction_date",
                    "predicted_weight_kg", "predicted_volume_m3", "confidence"
                ]
            },
            "passenger_traffic_predictions": {
                "description": "ML passenger traffic predictions",
                "key_fields": [
                    "id", "airport_id", "prediction_date",
                    "predicted_passengers", "confidence"
                ]
            },
            "ml_models": {
                "description": "ML model metadata and versions",
                "key_fields": [
                    "id", "model_name", "model_type", "version",
                    "training_date", "accuracy", "features_used"
                ]
            }
        }
    
    def _get_available_services(self) -> Dict[str, Any]:
        """Get information about available services"""
        return {
            "ml_service": {
                "description": "Machine learning predictions",
                "capabilities": [
                    "predict_available_cargo_capacity",
                    "predict_flight_delay",
                    "predict_cargo_demand",
                    "predict_passenger_traffic",
                    "train_baggage_model"
                ]
            },
            "flight_tracking_service": {
                "description": "Real-time flight tracking and aircraft data",
                "capabilities": [
                    "get_aircraft_info",
                    "get_flight_route_info",
                    "get_real_time_flight_status",
                    "get_airport_flights"
                ]
            },
            "cargo_optimization_service": {
                "description": "Cargo mix optimization",
                "capabilities": [
                    "optimize_cargo_mix",
                    "calculate_revenue_estimate"
                ]
            },
            "alert_service": {
                "description": "Proactive alerts and monitoring",
                "capabilities": [
                    "check_flight_alerts",
                    "check_upcoming_flights"
                ]
            },
            "baggage_predictor": {
                "description": "Baggage weight/volume prediction",
                "capabilities": [
                    "predict",
                    "train"
                ]
            },
            "cargo_capacity_predictor": {
                "description": "Available cargo capacity prediction",
                "capabilities": [
                    "predict_available_capacity",
                    "get_capacity_summary"
                ]
            }
        }
    
    def _get_api_endpoints(self) -> List[Dict[str, Any]]:
        """Get available API endpoints"""
        return [
            {
                "path": "/api/v1/cargo/predict-capacity",
                "method": "POST",
                "description": "Predict cargo capacity for a flight",
                "parameters": [
                    "aircraft_type", "passenger_count", "origin", "destination",
                    "flight_date", "days_before_flight"
                ]
            },
            {
                "path": "/api/v1/cargo/analytics/{flight_id}",
                "method": "GET",
                "description": "Get comprehensive cargo analytics",
                "parameters": ["flight_id", "days_before_flight"]
            },
            {
                "path": "/api/v1/tracking/aircraft/{registration}",
                "method": "GET",
                "description": "Get aircraft information"
            },
            {
                "path": "/api/v1/tracking/routes/{origin}/{destination}",
                "method": "GET",
                "description": "Get route information"
            },
            {
                "path": "/api/v1/tracking/realtime/{registration}",
                "method": "GET",
                "description": "Get real-time flight status"
            },
            {
                "path": "/api/v1/ai/chat",
                "method": "POST",
                "description": "Conversational AI chat"
            },
            {
                "path": "/api/v1/ai/query",
                "method": "POST",
                "description": "Process natural language query"
            },
            {
                "path": "/api/v1/ai/insights",
                "method": "POST",
                "description": "Generate insights for a flight"
            },
            {
                "path": "/api/v1/ai/optimize-cargo",
                "method": "POST",
                "description": "Get cargo mix recommendations"
            },
            {
                "path": "/api/v1/ai/alerts",
                "method": "GET",
                "description": "Get proactive alerts"
            }
        ]
    
    def _get_data_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            total_flights = self.db.query(func.count(Flight.id)).scalar() or 0
            total_aircraft = self.db.query(func.count(Aircraft.id)).scalar() or 0
            total_airports = self.db.query(func.count(Airport.id)).scalar() or 0
            total_airlines = self.db.query(func.count(Airline.id)).scalar() or 0
            
            # Get date range
            earliest_flight = self.db.query(func.min(Flight.scheduled_departure)).scalar()
            latest_flight = self.db.query(func.max(Flight.scheduled_departure)).scalar()
            
            # Get flight status distribution
            status_counts = {}
            if total_flights > 0:
                statuses = self.db.query(
                    Flight.flight_status,
                    func.count(Flight.id)
                ).group_by(Flight.flight_status).all()
                status_counts = {status: count for status, count in statuses}
            
            return {
                "total_flights": total_flights,
                "total_aircraft": total_aircraft,
                "total_airports": total_airports,
                "total_airlines": total_airlines,
                "date_range": {
                    "earliest": earliest_flight.isoformat() if earliest_flight else None,
                    "latest": latest_flight.isoformat() if latest_flight else None
                },
                "flight_status_distribution": status_counts
            }
        except Exception as e:
            logger.error(f"Error getting data statistics: {e}")
            return {
                "total_flights": 0,
                "total_aircraft": 0,
                "total_airports": 0,
                "total_airlines": 0
            }
    
    async def query_flights(
        self,
        filters: Dict[str, Any],
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Query flights with filters
        
        Args:
            filters: Dictionary with filter criteria
            limit: Maximum results to return
        
        Returns:
            List of flight dictionaries
        """
        try:
            query = self.db.query(Flight)
            
            # Apply filters
            if "flight_number" in filters:
                query = query.filter(Flight.flight_number.ilike(f"%{filters['flight_number']}%"))
            
            if "origin" in filters:
                origin_airport = self.db.query(Airport).filter(
                    or_(
                        Airport.iata_code == filters["origin"].upper(),
                        Airport.icao_code == filters["origin"].upper()
                    )
                ).first()
                if origin_airport:
                    query = query.filter(Flight.origin_airport_id == origin_airport.id)
            
            if "destination" in filters:
                dest_airport = self.db.query(Airport).filter(
                    or_(
                        Airport.iata_code == filters["destination"].upper(),
                        Airport.icao_code == filters["destination"].upper()
                    )
                ).first()
                if dest_airport:
                    query = query.filter(Flight.destination_airport_id == dest_airport.id)
            
            if "date_range" in filters:
                date_range = filters["date_range"]
                if "start" in date_range:
                    start_date = datetime.fromisoformat(date_range["start"].replace("Z", "+00:00"))
                    query = query.filter(Flight.scheduled_departure >= start_date)
                if "end" in date_range:
                    end_date = datetime.fromisoformat(date_range["end"].replace("Z", "+00:00"))
                    query = query.filter(Flight.scheduled_departure <= end_date)
            
            if "flight_status" in filters:
                query = query.filter(Flight.flight_status == filters["flight_status"])
            
            if "flight_type" in filters:
                query = query.filter(Flight.flight_type == filters["flight_type"])
            
            flights = query.limit(limit).all()
            
            # Convert to dictionaries
            result = []
            for flight in flights:
                origin = self.db.query(Airport).filter(Airport.id == flight.origin_airport_id).first()
                dest = self.db.query(Airport).filter(Airport.id == flight.destination_airport_id).first()
                aircraft = self.db.query(Aircraft).filter(Aircraft.id == flight.aircraft_id).first()
                
                result.append({
                    "flight_id": str(flight.id),
                    "flight_number": flight.flight_number,
                    "origin": origin.iata_code if origin else None,
                    "destination": dest.iata_code if dest else None,
                    "scheduled_departure": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None,
                    "scheduled_arrival": flight.scheduled_arrival.isoformat() if flight.scheduled_arrival else None,
                    "flight_status": flight.flight_status,
                    "passenger_count": flight.passenger_count,
                    "cargo_weight_tonnes": float(flight.cargo_weight_tonnes) if flight.cargo_weight_tonnes else None,
                    "aircraft_registration": aircraft.registration if aircraft else None,
                    "distance_km": float(flight.distance_km) if flight.distance_km else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error querying flights: {e}")
            return []
    
    async def get_flight_details(self, flight_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed flight information"""
        try:
            flight = self.db.query(Flight).filter(Flight.id == flight_id).first()
            if not flight:
                return None
            
            origin = self.db.query(Airport).filter(Airport.id == flight.origin_airport_id).first()
            dest = self.db.query(Airport).filter(Airport.id == flight.destination_airport_id).first()
            aircraft = self.db.query(Aircraft).filter(Aircraft.id == flight.aircraft_id).first()
            airline = self.db.query(Airline).filter(Airline.id == flight.airline_id).first()
            
            aircraft_type = None
            if aircraft:
                aircraft_type = self.db.query(AircraftType).filter(
                    AircraftType.id == aircraft.aircraft_type_id
                ).first()
            
            # Get predictions
            delay_prediction = self.db.query(FlightDelayPrediction).filter(
                FlightDelayPrediction.flight_id == flight.id
            ).order_by(FlightDelayPrediction.prediction_time.desc()).first()
            
            return {
                "flight_id": str(flight.id),
                "flight_number": flight.flight_number,
                "airline": {
                    "name": airline.name if airline else None,
                    "icao_code": airline.icao_code if airline else None
                },
                "aircraft": {
                    "registration": aircraft.registration if aircraft else None,
                    "type": f"{aircraft_type.manufacturer} {aircraft_type.model}" if aircraft_type else None,
                    "max_cargo_weight_kg": float(aircraft_type.max_cargo_weight_kg) if aircraft_type and aircraft_type.max_cargo_weight_kg else None
                },
                "route": {
                    "origin": {
                        "code": origin.iata_code if origin else None,
                        "name": origin.name if origin else None,
                        "city": origin.city if origin else None
                    },
                    "destination": {
                        "code": dest.iata_code if dest else None,
                        "name": dest.name if dest else None,
                        "city": dest.city if dest else None
                    },
                    "distance_km": float(flight.distance_km) if flight.distance_km else None
                },
                "schedule": {
                    "scheduled_departure": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None,
                    "scheduled_arrival": flight.scheduled_arrival.isoformat() if flight.scheduled_arrival else None,
                    "actual_departure": flight.actual_departure.isoformat() if flight.actual_departure else None,
                    "actual_arrival": flight.actual_arrival.isoformat() if flight.actual_arrival else None
                },
                "delays": {
                    "departure_delay_minutes": flight.departure_delay_minutes,
                    "arrival_delay_minutes": flight.arrival_delay_minutes
                },
                "cargo": {
                    "cargo_weight_tonnes": float(flight.cargo_weight_tonnes) if flight.cargo_weight_tonnes else None,
                    "cargo_volume_m3": float(flight.cargo_volume_m3) if flight.cargo_volume_m3 else None,
                    "baggage_weight_kg": float(flight.baggage_weight_kg) if flight.baggage_weight_kg else None,
                    "baggage_volume_m3": float(flight.baggage_volume_m3) if flight.baggage_volume_m3 else None
                },
                "passengers": {
                    "count": flight.passenger_count
                },
                "status": flight.flight_status,
                "delay_prediction": {
                    "delay_probability": float(delay_prediction.delay_probability) if delay_prediction else None,
                    "estimated_delay_minutes": delay_prediction.estimated_delay_minutes if delay_prediction else None,
                    "confidence": float(delay_prediction.confidence) if delay_prediction else None
                } if delay_prediction else None
            }
            
        except Exception as e:
            logger.error(f"Error getting flight details: {e}")
            return None
    
    async def get_route_statistics(
        self,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """Get route statistics"""
        try:
            origin_airport = self.db.query(Airport).filter(
                or_(
                    Airport.iata_code == origin.upper(),
                    Airport.icao_code == origin.upper()
                )
            ).first()
            
            dest_airport = self.db.query(Airport).filter(
                or_(
                    Airport.iata_code == destination.upper(),
                    Airport.icao_code == destination.upper()
                )
            ).first()
            
            if not origin_airport or not dest_airport:
                return {"error": "Airports not found"}
            
            # Get flights on this route
            flights = self.db.query(Flight).filter(
                and_(
                    Flight.origin_airport_id == origin_airport.id,
                    Flight.destination_airport_id == dest_airport.id
                )
            ).all()
            
            if not flights:
                return {
                    "route": f"{origin} -> {destination}",
                    "total_flights": 0,
                    "message": "No flights found on this route"
                }
            
            # Calculate statistics
            total_flights = len(flights)
            flights_with_passengers = [f for f in flights if f.passenger_count]
            avg_passengers = sum(f.passenger_count for f in flights_with_passengers) / len(flights_with_passengers) if flights_with_passengers else 0
            
            flights_with_cargo = [f for f in flights if f.cargo_weight_tonnes]
            avg_cargo_weight = sum(float(f.cargo_weight_tonnes) for f in flights_with_cargo) / len(flights_with_cargo) if flights_with_cargo else 0
            
            flights_with_delays = [f for f in flights if f.departure_delay_minutes and f.departure_delay_minutes > 0]
            avg_delay = sum(f.departure_delay_minutes for f in flights_with_delays) / len(flights_with_delays) if flights_with_delays else 0
            delay_rate = len(flights_with_delays) / total_flights if total_flights > 0 else 0
            
            # Get aircraft types used
            aircraft_types = {}
            for flight in flights:
                if flight.aircraft_id:
                    aircraft = self.db.query(Aircraft).filter(Aircraft.id == flight.aircraft_id).first()
                    if aircraft:
                        aircraft_type = self.db.query(AircraftType).filter(
                            AircraftType.id == aircraft.aircraft_type_id
                        ).first()
                        if aircraft_type:
                            type_name = f"{aircraft_type.manufacturer} {aircraft_type.model}"
                            aircraft_types[type_name] = aircraft_types.get(type_name, 0) + 1
            
            return {
                "route": f"{origin} -> {destination}",
                "total_flights": total_flights,
                "statistics": {
                    "average_passengers": round(avg_passengers, 2),
                    "average_cargo_weight_tonnes": round(avg_cargo_weight, 2),
                    "average_delay_minutes": round(avg_delay, 2),
                    "delay_rate": round(delay_rate * 100, 2)
                },
                "aircraft_types": aircraft_types,
                "date_range": {
                    "earliest": min(f.scheduled_departure for f in flights if f.scheduled_departure).isoformat(),
                    "latest": max(f.scheduled_departure for f in flights if f.scheduled_departure).isoformat()
                } if flights else None
            }
            
        except Exception as e:
            logger.error(f"Error getting route statistics: {e}")
            return {"error": str(e)}
    
    async def get_airport_statistics(self, airport_code: str) -> Dict[str, Any]:
        """Get airport statistics"""
        try:
            airport = self.db.query(Airport).filter(
                or_(
                    Airport.iata_code == airport_code.upper(),
                    Airport.icao_code == airport_code.upper()
                )
            ).first()
            
            if not airport:
                return {"error": "Airport not found"}
            
            # Get flights
            departures = self.db.query(Flight).filter(
                Flight.origin_airport_id == airport.id
            ).count()
            
            arrivals = self.db.query(Flight).filter(
                Flight.destination_airport_id == airport.id
            ).count()
            
            # Get recent weather
            recent_weather = self.db.query(WeatherData).filter(
                WeatherData.airport_id == airport.id
            ).order_by(WeatherData.observation_time.desc()).first()
            
            return {
                "airport": {
                    "code": airport.iata_code,
                    "name": airport.name,
                    "city": airport.city,
                    "country": airport.country
                },
                "statistics": {
                    "total_departures": departures,
                    "total_arrivals": arrivals,
                    "total_flights": departures + arrivals
                },
                "capacity": {
                    "passenger_capacity": airport.passenger_capacity,
                    "cargo_capacity_tonnes": float(airport.cargo_capacity_tonnes) if airport.cargo_capacity_tonnes else None
                },
                "recent_weather": {
                    "temperature_celsius": float(recent_weather.temperature_celsius) if recent_weather and recent_weather.temperature_celsius else None,
                    "wind_speed_kmh": float(recent_weather.wind_speed_kmh) if recent_weather and recent_weather.wind_speed_kmh else None,
                    "visibility_km": float(recent_weather.visibility_km) if recent_weather and recent_weather.visibility_km else None,
                    "observation_time": recent_weather.observation_time.isoformat() if recent_weather and recent_weather.observation_time else None
                } if recent_weather else None
            }
            
        except Exception as e:
            logger.error(f"Error getting airport statistics: {e}")
            return {"error": str(e)}
    
    def get_comprehensive_context(self) -> Dict[str, Any]:
        """
        Get comprehensive context for AI agent
        
        This includes everything the AI needs to know about the application
        """
        return {
            "application": self.get_application_context(),
            "database_schema": self._get_database_schema(),
            "services": self._get_available_services(),
            "api_endpoints": self._get_api_endpoints(),
            "data_statistics": self._get_data_statistics(),
            "capabilities": {
                "can_query_flights": True,
                "can_get_flight_details": True,
                "can_get_route_statistics": True,
                "can_get_airport_statistics": True,
                "can_predict_cargo_capacity": True,
                "can_track_flights_realtime": True,
                "can_optimize_cargo_mix": True,
                "can_generate_alerts": True
            }
        }
