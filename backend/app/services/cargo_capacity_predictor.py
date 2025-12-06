"""
Cargo Capacity Prediction Service
Predicts available cargo capacity (weight and volume) for flights
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger
from app.services.baggage_predictor import BaggagePredictor
from app.infrastructure.external.adsbdb_client import ADSBDBClient


class CargoCapacityPredictor:
    """Predicts available cargo capacity for flights"""
    
    # Aircraft capacity lookup (in kg and m³)
    # These are approximate - should be loaded from database or config
    # Can be enriched with ADSBDB data
    AIRCRAFT_CAPACITIES = {
        'Boeing 737-800': {
            'cargo_weight_kg': 20500,
            'cargo_volume_m3': 38.0,
            'max_takeoff_weight_kg': 79010
        },
        'Boeing 737-900ER': {
            'cargo_weight_kg': 24000,
            'cargo_volume_m3': 45.0,
            'max_takeoff_weight_kg': 85250
        },
        'Airbus A330-200': {
            'cargo_weight_kg': 19700,
            'cargo_volume_m3': 136.0,
            'max_takeoff_weight_kg': 242000
        },
        'Airbus A330-300': {
            'cargo_weight_kg': 19700,
            'cargo_volume_m3': 162.0,
            'max_takeoff_weight_kg': 242000
        }
    }
    
    def __init__(
        self,
        baggage_predictor: Optional[BaggagePredictor] = None,
        adsbdb_client: Optional[ADSBDBClient] = None
    ):
        self.baggage_predictor = baggage_predictor or BaggagePredictor()
        self.adsbdb_client = adsbdb_client or ADSBDBClient()
        
    async def _get_aircraft_capacity(
        self,
        aircraft_type: str,
        registration: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Get aircraft cargo capacity specifications
        
        Tries to enrich with ADSBDB data if registration is provided
        
        Args:
            aircraft_type: Aircraft type string
            registration: Optional aircraft registration for ADSBDB lookup
        
        Returns:
            Dictionary with capacity specifications
        """
        # Try to get accurate aircraft type from ADSBDB if registration provided
        # Make this non-blocking and fail gracefully
        if registration:
            try:
                # Add timeout wrapper for extra safety
                aircraft_info = await asyncio.wait_for(
                    self.adsbdb_client.get_aircraft_for_capacity_calculation(registration),
                    timeout=6.0  # Slightly longer than the client timeout
                )
                if aircraft_info and aircraft_info.get("aircraft_type"):
                    # Use the more accurate type from ADSBDB
                    aircraft_type = aircraft_info["aircraft_type"]
                    logger.debug(f"Enriched aircraft type from ADSBDB: {aircraft_type}")
            except asyncio.TimeoutError:
                logger.debug(f"ADSBDB lookup timed out for {registration}, using provided type: {aircraft_type}")
            except asyncio.CancelledError:
                logger.debug(f"ADSBDB lookup cancelled for {registration}, using provided type: {aircraft_type}")
            except Exception as e:
                # Fallback to provided type if ADSBDB fails
                logger.debug(f"ADSBDB lookup failed for {registration}: {e}, using provided type: {aircraft_type}")
                pass
        
        # Try exact match
        if aircraft_type in self.AIRCRAFT_CAPACITIES:
            return self.AIRCRAFT_CAPACITIES[aircraft_type]
        
        # Try partial match
        for key, capacity in self.AIRCRAFT_CAPACITIES.items():
            if aircraft_type in key or key in aircraft_type:
                return capacity
        
        # Default capacity (Boeing 737-800 like)
        return {
            'cargo_weight_kg': 20000,
            'cargo_volume_m3': 40.0,
            'max_takeoff_weight_kg': 80000
        }
    
    async def predict_available_capacity(
        self,
        aircraft_type: str,
        passenger_count: int,
        origin: str,
        destination: str,
        flight_date: datetime,
        fuel_weight_kg: Optional[float] = None,
        days_before_flight: int = 0,
        safety_margin_pct: float = 0.05,  # 5% safety margin
        aircraft_registration: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict available cargo capacity
        
        Args:
            aircraft_type: Aircraft type string
            passenger_count: Number of passengers
            origin: Origin airport code
            destination: Destination airport code
            flight_date: Flight departure date
            fuel_weight_kg: Fuel weight (if known, otherwise estimated)
            days_before_flight: Days before flight for prediction
            safety_margin_pct: Safety margin percentage (default 5%)
        
        Returns:
            Dictionary with available capacity predictions
        """
        # Get aircraft capacity (with ADSBDB enrichment if registration provided)
        aircraft_cap = await self._get_aircraft_capacity(aircraft_type, aircraft_registration)
        max_cargo_weight_kg = aircraft_cap['cargo_weight_kg']
        max_cargo_volume_m3 = aircraft_cap['cargo_volume_m3']
        
        # Predict baggage
        baggage_pred = self.baggage_predictor.predict(
            passenger_count=passenger_count,
            origin=origin,
            destination=destination,
            aircraft_type=aircraft_type,
            flight_date=flight_date,
            days_before_flight=days_before_flight
        )
        
        predicted_baggage_weight = baggage_pred['predicted_baggage_weight_kg']
        predicted_baggage_volume = baggage_pred['predicted_baggage_volume_m3']
        
        # Estimate fuel if not provided (rough estimate: 10-15% of max takeoff weight)
        if fuel_weight_kg is None:
            # Estimate based on route distance (would need actual distance calculation)
            # For now, use a default percentage of max takeoff weight
            estimated_fuel_pct = 0.12  # 12% of MTOW
            fuel_weight_kg = aircraft_cap['max_takeoff_weight_kg'] * estimated_fuel_pct
        
        # Calculate available capacity (accounting for baggage and fuel)
        # Note: Baggage and fuel share cargo hold space, but fuel is in tanks
        # Simplified assumption: baggage and cargo compete for cargo hold space
        available_weight_kg = max_cargo_weight_kg - predicted_baggage_weight
        available_volume_m3 = max_cargo_volume_m3 - predicted_baggage_volume
        
        # Apply safety margin
        available_weight_kg = available_weight_kg * (1 - safety_margin_pct)
        available_volume_m3 = available_volume_m3 * (1 - safety_margin_pct)
        
        # Determine constraining factor
        weight_utilization = (predicted_baggage_weight / max_cargo_weight_kg) * 100
        volume_utilization = (predicted_baggage_volume / max_cargo_volume_m3) * 100
        
        constraining_factor = "weight" if weight_utilization > volume_utilization else "volume"
        
        # Calculate confidence intervals for available capacity
        # Use inverse of baggage confidence intervals (wider uncertainty)
        baggage_weight_lower = baggage_pred['confidence_interval_95_lower_weight']
        baggage_weight_upper = baggage_pred['confidence_interval_95_upper_weight']
        baggage_volume_lower = baggage_pred['confidence_interval_95_lower_volume']
        baggage_volume_upper = baggage_pred['confidence_interval_95_upper_volume']
        
        # Available capacity is inversely related to baggage
        available_weight_upper = max(0, max_cargo_weight_kg - baggage_weight_lower) * (1 - safety_margin_pct)
        available_weight_lower = max(0, max_cargo_weight_kg - baggage_weight_upper) * (1 - safety_margin_pct)
        
        available_volume_upper = max(0, max_cargo_volume_m3 - baggage_volume_lower) * (1 - safety_margin_pct)
        available_volume_lower = max(0, max_cargo_volume_m3 - baggage_volume_upper) * (1 - safety_margin_pct)
        
        # Estimate cargo demand from historical patterns (placeholder)
        # Would need historical data analysis
        predicted_cargo_demand_kg = max(0, available_weight_kg * 0.8)  # Assume 80% utilization
        
        # Overbooking risk assessment
        if available_weight_kg < predicted_cargo_demand_kg * 0.9:
            overbooking_risk = "high"
        elif available_weight_kg < predicted_cargo_demand_kg:
            overbooking_risk = "medium"
        else:
            overbooking_risk = "low"
        
        return {
            'available_weight_kg': float(available_weight_kg),
            'available_volume_m3': float(available_volume_m3),
            'available_weight_confidence_lower': float(available_weight_lower),
            'available_weight_confidence_upper': float(available_weight_upper),
            'available_volume_confidence_lower': float(available_volume_lower),
            'available_volume_confidence_upper': float(available_volume_upper),
            'utilization_percentage': float(max(weight_utilization, volume_utilization)),
            'weight_utilization_pct': float(weight_utilization),
            'volume_utilization_pct': float(volume_utilization),
            'constraining_factor': constraining_factor,
            'predicted_cargo_demand_kg': float(predicted_cargo_demand_kg),
            'overbooking_risk': overbooking_risk,
            'baggage_prediction': baggage_pred,
            'aircraft_max_cargo_weight_kg': float(max_cargo_weight_kg),
            'aircraft_max_cargo_volume_m3': float(max_cargo_volume_m3),
            'predicted_baggage_weight_kg': float(predicted_baggage_weight),
            'predicted_baggage_volume_m3': float(predicted_baggage_volume),
            'fuel_weight_kg': float(fuel_weight_kg),
            'days_before_flight': days_before_flight
        }
    
    async def get_capacity_summary(
        self,
        aircraft_type: str,
        passenger_count: int,
        origin: str,
        destination: str,
        flight_date: datetime,
        fuel_weight_kg: Optional[float] = None,
        days_before_flight: int = 0,
        aircraft_registration: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get simplified capacity summary for API responses
        
        Returns a simplified version suitable for API responses
        """
        prediction = await self.predict_available_capacity(
            aircraft_type=aircraft_type,
            passenger_count=passenger_count,
            origin=origin,
            destination=destination,
            flight_date=flight_date,
            fuel_weight_kg=fuel_weight_kg,
            days_before_flight=days_before_flight,
            aircraft_registration=aircraft_registration
        )
        
        return {
            'available_weight_kg': prediction['available_weight_kg'],
            'available_volume_m3': prediction['available_volume_m3'],
            'confidence_interval_95_lower_weight': prediction['available_weight_confidence_lower'],
            'confidence_interval_95_upper_weight': prediction['available_weight_confidence_upper'],
            'confidence_interval_95_lower_volume': prediction['available_volume_confidence_lower'],
            'confidence_interval_95_upper_volume': prediction['available_volume_confidence_upper'],
            'utilization_percentage': prediction['utilization_percentage'],
            'constraining_factor': prediction['constraining_factor'],
            'predicted_cargo_demand_kg': prediction['predicted_cargo_demand_kg'],
            'overbooking_risk': prediction['overbooking_risk'],
            'days_before_flight': days_before_flight
        }
