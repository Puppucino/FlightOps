"""
Proactive Alert Service
Monitors flights and generates alerts for capacity issues, risks, and opportunities
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.flight import Flight
from app.services.ml_service import MLService
from app.services.ai_agent_service import AIAgentService
from loguru import logger


class AlertService:
    """Service for generating proactive alerts"""
    
    def __init__(self, ml_service: Optional[MLService] = None, ai_service: Optional[AIAgentService] = None):
        self.ml_service = ml_service or MLService()
        self.ai_service = ai_service or AIAgentService()
    
    async def check_flight_alerts(
        self,
        flight: Flight,
        days_before_flight: int = 0,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """
        Check a single flight for alerts
        
        Args:
            flight: Flight object
            days_before_flight: Days before flight for prediction
            db: Database session
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        try:
            # Get prediction
            if not flight.aircraft or not flight.origin_airport or not flight.destination_airport:
                return alerts
            
            aircraft_registration = flight.aircraft.registration if flight.aircraft else None
            prediction = await self.ml_service.predict_available_cargo_capacity(
                aircraft_type=flight.aircraft.aircraft_type.name if flight.aircraft.aircraft_type else "Boeing 737-800",
                passenger_count=flight.passenger_count or 0,
                origin=flight.origin_airport.iata_code,
                destination=flight.destination_airport.iata_code,
                flight_date=flight.scheduled_departure,
                days_before_flight=days_before_flight,
                aircraft_registration=aircraft_registration
            )
            
            # Check for high overbooking risk
            if prediction.get('overbooking_risk') == 'high':
                alert = await self._create_risk_alert(flight, prediction)
                alerts.append(alert)
            
            # Check for low capacity
            available_weight_tonnes = prediction.get('available_weight_kg', 0) / 1000
            if available_weight_tonnes < 2.0:  # Less than 2 tonnes
                alert = await self._create_low_capacity_alert(flight, prediction)
                alerts.append(alert)
            
            # Check for opportunity (high available capacity)
            if available_weight_tonnes > 10.0:  # More than 10 tonnes
                alert = await self._create_opportunity_alert(flight, prediction)
                alerts.append(alert)
            
            # Check for weight/volume constraint issues
            if prediction.get('constraining_factor') == 'weight' and available_weight_tonnes < 3.0:
                alert = await self._create_constraint_alert(flight, prediction, 'weight')
                alerts.append(alert)
            elif prediction.get('constraining_factor') == 'volume' and prediction.get('available_volume_m3', 0) < 5.0:
                alert = await self._create_constraint_alert(flight, prediction, 'volume')
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Error checking alerts for flight {flight.flight_number}: {e}")
        
        return alerts
    
    async def _create_risk_alert(
        self,
        flight: Flight,
        prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create high risk alert"""
        flight_data = {
            'flight_number': flight.flight_number,
            'origin': flight.origin_airport.iata_code if flight.origin_airport else '',
            'destination': flight.destination_airport.iata_code if flight.destination_airport else '',
            'scheduled_departure': flight.scheduled_departure.isoformat() if flight.scheduled_departure else ''
        }
        
        metrics = {
            'overbooking_risk': prediction.get('overbooking_risk'),
            'available_weight_kg': prediction.get('available_weight_kg'),
            'predicted_demand_kg': prediction.get('predicted_cargo_demand_kg')
        }
        
        explanation = await self.ai_service.generate_alert_explanation(
            'high_risk',
            flight_data,
            metrics
        )
        
        return {
            'type': 'high_risk',
            'severity': 'high',
            'flight_id': str(flight.id),
            'flight_number': flight.flight_number,
            'title': f'High Overbooking Risk: {flight.flight_number}',
            'message': explanation,
            'metrics': metrics,
            'flight_data': flight_data,
            'timestamp': datetime.now().isoformat(),
            'action_required': True
        }
    
    async def _create_low_capacity_alert(
        self,
        flight: Flight,
        prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create low capacity alert"""
        flight_data = {
            'flight_number': flight.flight_number,
            'origin': flight.origin_airport.iata_code if flight.origin_airport else '',
            'destination': flight.destination_airport.iata_code if flight.destination_airport else '',
        }
        
        metrics = {
            'available_weight_kg': prediction.get('available_weight_kg'),
            'available_volume_m3': prediction.get('available_volume_m3')
        }
        
        explanation = await self.ai_service.generate_alert_explanation(
            'low_capacity',
            flight_data,
            metrics
        )
        
        return {
            'type': 'low_capacity',
            'severity': 'medium',
            'flight_id': str(flight.id),
            'flight_number': flight.flight_number,
            'title': f'Low Capacity Available: {flight.flight_number}',
            'message': explanation,
            'metrics': metrics,
            'flight_data': flight_data,
            'timestamp': datetime.now().isoformat(),
            'action_required': True
        }
    
    async def _create_opportunity_alert(
        self,
        flight: Flight,
        prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create opportunity alert"""
        flight_data = {
            'flight_number': flight.flight_number,
            'origin': flight.origin_airport.iata_code if flight.origin_airport else '',
            'destination': flight.destination_airport.iata_code if flight.destination_airport else '',
        }
        
        metrics = {
            'available_weight_kg': prediction.get('available_weight_kg'),
            'available_volume_m3': prediction.get('available_volume_m3')
        }
        
        explanation = await self.ai_service.generate_alert_explanation(
            'opportunity',
            flight_data,
            metrics
        )
        
        return {
            'type': 'opportunity',
            'severity': 'low',
            'flight_id': str(flight.id),
            'flight_number': flight.flight_number,
            'title': f'High Capacity Opportunity: {flight.flight_number}',
            'message': explanation,
            'metrics': metrics,
            'flight_data': flight_data,
            'timestamp': datetime.now().isoformat(),
            'action_required': False
        }
    
    async def _create_constraint_alert(
        self,
        flight: Flight,
        prediction: Dict[str, Any],
        constraint_type: str
    ) -> Dict[str, Any]:
        """Create constraint alert"""
        flight_data = {
            'flight_number': flight.flight_number,
            'origin': flight.origin_airport.iata_code if flight.origin_airport else '',
            'destination': flight.destination_airport.iata_code if flight.destination_airport else '',
        }
        
        metrics = {
            'constraining_factor': constraint_type,
            'available_weight_kg': prediction.get('available_weight_kg'),
            'available_volume_m3': prediction.get('available_volume_m3')
        }
        
        explanation = await self.ai_service.generate_alert_explanation(
            'constraint',
            flight_data,
            metrics
        )
        
        return {
            'type': 'constraint',
            'severity': 'medium',
            'flight_id': str(flight.id),
            'flight_number': flight.flight_number,
            'title': f'{constraint_type.title()} Constraint: {flight.flight_number}',
            'message': explanation,
            'metrics': metrics,
            'flight_data': flight_data,
            'timestamp': datetime.now().isoformat(),
            'action_required': True
        }
    
    async def check_upcoming_flights(
        self,
        db: Session,
        days_ahead: int = 7,
        days_before_flight: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Check all upcoming flights for alerts
        
        Args:
            db: Database session
            days_ahead: How many days ahead to check
            days_before_flight: Days before flight for prediction
            
        Returns:
            List of all alerts
        """
        all_alerts = []
        
        try:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)
            
            flights = db.query(Flight).filter(
                and_(
                    Flight.scheduled_departure >= start_date,
                    Flight.scheduled_departure <= end_date,
                    Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
                    Flight.passenger_count.isnot(None)
                )
            ).all()
            
            for flight in flights:
                alerts = await self.check_flight_alerts(flight, days_before_flight, db)
                all_alerts.extend(alerts)
            
            # Sort by severity and timestamp
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            all_alerts.sort(key=lambda x: (
                severity_order.get(x.get('severity', 'low'), 2),
                x.get('timestamp', '')
            ))
            
        except Exception as e:
            logger.error(f"Error checking upcoming flights: {e}")
        
        return all_alerts
