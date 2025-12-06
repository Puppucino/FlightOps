"""
AI Agent API Routes
Endpoints for conversational AI, natural language queries, and intelligent features
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.services.ai_agent_service import AIAgentService
from app.services.ai_context_provider import AIContextProvider
from app.services.alert_service import AlertService
from app.services.cargo_optimization_service import CargoOptimizationService
from app.services.ml_service import MLService
from app.services.flight_tracking_service import FlightTrackingService
from app.models.flight import Flight
from app.models.airport import Airport

router = APIRouter(prefix="/ai", tags=["AI Agent"])

# Global service instances
_ai_service = None
_ml_service = None
_alert_service = None
_optimization_service = None


def get_ai_service() -> AIAgentService:
    """Get AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIAgentService()
    return _ai_service


def get_ml_service() -> MLService:
    """Get ML service instance"""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService()
    return _ml_service


def get_alert_service() -> AlertService:
    """Get alert service instance"""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service


def get_optimization_service() -> CargoOptimizationService:
    """Get optimization service instance"""
    global _optimization_service
    if _optimization_service is None:
        _optimization_service = CargoOptimizationService()
    return _optimization_service


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User's message")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Previous messages")
    context: Optional[Dict[str, Any]] = Field(None, description="Current context (flight, etc.)")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    conversation_id: Optional[str] = None


class NaturalLanguageQueryRequest(BaseModel):
    """Natural language query request"""
    query: str = Field(..., description="User's natural language query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class QueryResponse(BaseModel):
    """Query response model"""
    query_type: str
    filters: Dict[str, Any]
    intent: str
    results: Optional[List[Dict[str, Any]]] = None


class InsightRequest(BaseModel):
    """Request for generating insights"""
    flight_id: str
    days_before_flight: int = 0


class InsightResponse(BaseModel):
    """Insight response model"""
    insights: str
    prediction_data: Dict[str, Any]
    flight_data: Dict[str, Any]


class OptimizationRequest(BaseModel):
    """Cargo optimization request"""
    flight_id: Optional[str] = None
    available_weight_kg: float
    available_volume_m3: float
    constraining_factor: str
    route_info: Optional[Dict[str, Any]] = None


class FeedbackRequest(BaseModel):
    """User feedback request"""
    feedback: str
    prediction_id: Optional[str] = None
    correction_data: Optional[Dict[str, Any]] = None
    flight_id: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    ai_service: AIAgentService = Depends(get_ai_service)
):
    """
    Conversational chat with AI agent
    
    Supports natural language queries about flights, cargo capacity, and recommendations.
    The AI has full access to all database data and services.
    """
    try:
        # Convert conversation history
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        # Get comprehensive application context
        context_provider = AIContextProvider(db)
        app_context = context_provider.get_comprehensive_context()
        
        response = await ai_service.chat_conversation(
            user_message=request.message,
            conversation_history=history,
            context=request.context,
            app_context=app_context
        )
        
        return ChatResponse(response=response)
        
    except ValueError as e:
        # API key validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_detail = str(e) if str(e) else f"Unknown error: {type(e).__name__}"
        logger.error(f"Chat endpoint error: {error_detail}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat error: {error_detail}")


@router.post("/query", response_model=QueryResponse)
async def process_natural_language_query(
    request: NaturalLanguageQueryRequest,
    db: Session = Depends(get_db),
    ai_service: AIAgentService = Depends(get_ai_service)
):
    """
    Process natural language query and return structured results
    
    Examples:
    - "Show me flights with high overbooking risk next week"
    - "What's the cargo capacity for flight MH123?"
    - "Find all flights from KUL to SIN with low capacity"
    - "What are the statistics for KUL to SIN route?"
    - "Tell me about airport KUL"
    """
    try:
        # Get application context
        context_provider = AIContextProvider(db)
        app_context = context_provider.get_comprehensive_context()
        
        # Parse query
        parsed = await ai_service.process_natural_language_query(
            query=request.query,
            context=request.context,
            app_context=app_context
        )
        
        query_type = parsed.get("query_type", "other")
        filters = parsed.get("filters", {})
        needs_data = parsed.get("needs_data", True)
        
        # Execute query based on type
        results = []
        
        # Handle route statistics query
        if query_type == "get_route_stats":
            if "origin" in filters and "destination" in filters:
                route_stats = await context_provider.get_route_statistics(
                    origin=filters["origin"],
                    destination=filters["destination"]
                )
                return QueryResponse(
                    query_type=query_type,
                    filters=filters,
                    intent=parsed.get("intent", request.query),
                    results=[route_stats]
                )
        
        # Handle airport statistics query
        if query_type == "get_airport_stats":
            airport_code = filters.get("airport") or filters.get("origin") or filters.get("destination")
            if airport_code:
                airport_stats = await context_provider.get_airport_statistics(airport_code)
                return QueryResponse(
                    query_type=query_type,
                    filters=filters,
                    intent=parsed.get("intent", request.query),
                    results=[airport_stats]
                )
        
        # Handle flight details query
        if query_type == "get_flight_details":
            flight_id = filters.get("flight_id")
            flight_number = filters.get("flight_number")
            if flight_id:
                flight_details = await context_provider.get_flight_details(flight_id)
                if flight_details:
                    return QueryResponse(
                        query_type=query_type,
                        filters=filters,
                        intent=parsed.get("intent", request.query),
                        results=[flight_details]
                    )
            elif flight_number:
                # Find flight by number
                flight = db.query(Flight).filter(Flight.flight_number == flight_number).first()
                if flight:
                    flight_details = await context_provider.get_flight_details(str(flight.id))
                    if flight_details:
                        return QueryResponse(
                            query_type=query_type,
                            filters=filters,
                            intent=parsed.get("intent", request.query),
                            results=[flight_details]
                        )
        
        if query_type == "search_flights":
            # Use context provider for consistent querying
            flights_data = await context_provider.query_flights(
                filters=filters,
                limit=50
            )
            flights = flights_data
            
            # Get predictions for flights if risk filter is specified
            if "risk_level" in filters:
                ml_service = get_ml_service()
                filtered_flights = []
                
                for flight_data in flights:
                    flight_id = flight_data.get("flight_id")
                    if not flight_id:
                        continue
                    
                    # Get full flight object for prediction
                    flight = db.query(Flight).filter(Flight.id == flight_id).first()
                    if not flight or not flight.aircraft or not flight.origin_airport or not flight.destination_airport:
                        continue
                    
                    try:
                        aircraft_registration = flight.aircraft.registration if flight.aircraft else None
                        aircraft_type = None
                        if flight.aircraft:
                            from app.models.aircraft import AircraftType
                            aircraft_type_obj = db.query(AircraftType).filter(
                                AircraftType.id == flight.aircraft.aircraft_type_id
                            ).first()
                            if aircraft_type_obj:
                                aircraft_type = f"{aircraft_type_obj.manufacturer} {aircraft_type_obj.model}"
                        
                        if not aircraft_type:
                            continue
                        
                        prediction = await ml_service.predict_available_cargo_capacity(
                            aircraft_type=aircraft_type,
                            passenger_count=flight.passenger_count or 0,
                            origin=flight.origin_airport.iata_code,
                            destination=flight.destination_airport.iata_code,
                            flight_date=flight.scheduled_departure,
                            days_before_flight=parsed.get("days_before_flight", 0),
                            aircraft_registration=aircraft_registration
                        )
                        
                        if prediction.get("overbooking_risk") == filters["risk_level"]:
                            flight_data["overbooking_risk"] = prediction.get("overbooking_risk")
                            flight_data["available_weight_kg"] = prediction.get("available_weight_kg")
                            filtered_flights.append(flight_data)
                    except Exception as e:
                        logger.debug(f"Error predicting for flight {flight_id}: {e}")
                        continue
                
                results = filtered_flights
            else:
                results = flights
        
        return QueryResponse(
            query_type=query_type,
            filters=filters,
            intent=parsed.get("intent", request.query),
            results=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")


@router.post("/insights", response_model=InsightResponse)
async def generate_insights(
    request: InsightRequest,
    db: Session = Depends(get_db),
    ai_service: AIAgentService = Depends(get_ai_service),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Generate natural language insights for a flight's cargo capacity prediction
    """
    try:
        flight = db.query(Flight).filter(Flight.id == request.flight_id).first()
        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")
        
        if not flight.aircraft or not flight.origin_airport or not flight.destination_airport:
            raise HTTPException(status_code=400, detail="Flight missing required data")
        
        # Get prediction
        aircraft_registration = flight.aircraft.registration if flight.aircraft else None
        prediction = await ml_service.predict_available_cargo_capacity(
            aircraft_type=flight.aircraft.aircraft_type.name if flight.aircraft.aircraft_type else "Boeing 737-800",
            passenger_count=flight.passenger_count or 0,
            origin=flight.origin_airport.iata_code,
            destination=flight.destination_airport.iata_code,
            flight_date=flight.scheduled_departure,
            days_before_flight=request.days_before_flight,
            aircraft_registration=aircraft_registration
        )
        
        flight_data = {
            "flight_id": str(flight.id),
            "flight_number": flight.flight_number,
            "origin": flight.origin_airport.iata_code,
            "destination": flight.destination_airport.iata_code,
            "scheduled_departure": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None
        }
        
        # Generate insights
        insights = await ai_service.generate_insights(prediction, flight_data)
        
        return InsightResponse(
            insights=insights,
            prediction_data=prediction,
            flight_data=flight_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation error: {str(e)}")


@router.post("/optimize-cargo", response_model=Dict[str, Any])
async def optimize_cargo_mix(
    request: OptimizationRequest,
    db: Session = Depends(get_db),
    optimization_service: CargoOptimizationService = Depends(get_optimization_service)
):
    """
    Generate optimal cargo mix recommendations
    
    Can be called with flight_id or direct capacity parameters
    """
    try:
        route_info = request.route_info
        
        # If flight_id provided, get flight data
        if request.flight_id:
            flight = db.query(Flight).filter(Flight.id == request.flight_id).first()
            if flight and flight.origin_airport and flight.destination_airport:
                route_info = {
                    "origin": flight.origin_airport.iata_code,
                    "destination": flight.destination_airport.iata_code
                }
        
        # Generate optimization
        recommendations = await optimization_service.optimize_cargo_mix(
            available_weight_kg=request.available_weight_kg,
            available_volume_m3=request.available_volume_m3,
            constraining_factor=request.constraining_factor,
            route_info=route_info
        )
        
        # Calculate revenue estimate
        revenue = optimization_service.calculate_revenue_estimate(
            recommendations.get("recommended_cargo_mix", []),
            route_info
        )
        
        recommendations["revenue_estimate"] = revenue
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")


@router.get("/alerts")
async def get_alerts(
    days_ahead: int = 7,
    days_before_flight: int = 0,
    db: Session = Depends(get_db),
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Get proactive alerts for upcoming flights
    """
    try:
        alerts = await alert_service.check_upcoming_flights(
            db=db,
            days_ahead=days_ahead,
            days_before_flight=days_before_flight
        )
        
        return {
            "alerts": alerts,
            "count": len(alerts),
            "high_priority": len([a for a in alerts if a.get("severity") == "high"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert generation error: {str(e)}")


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    ai_service: AIAgentService = Depends(get_ai_service)
):
    """
    Submit user feedback to improve predictions
    
    The system learns from feedback to improve future recommendations
    """
    try:
        feedback_insights = await ai_service.process_feedback(
            feedback=request.feedback,
            prediction_id=request.prediction_id,
            correction_data=request.correction_data
        )
        
        # TODO: Store feedback in database for learning
        # This would be used to fine-tune predictions over time
        
        return {
            "status": "success",
            "feedback_processed": True,
            "insights": feedback_insights,
            "message": "Thank you for your feedback! This will help improve our predictions."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback processing error: {str(e)}")
