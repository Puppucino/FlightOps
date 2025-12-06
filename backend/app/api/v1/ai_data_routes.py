"""
AI Data Access Routes
Endpoints that allow AI agent to query database and services
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.ai_context_provider import AIContextProvider
from app.services.ml_service import MLService
from app.services.flight_tracking_service import FlightTrackingService

router = APIRouter(prefix="/ai/data", tags=["AI Data Access"])


class FlightQueryRequest(BaseModel):
    """Flight query request"""
    filters: Dict[str, Any] = {}
    limit: int = 50


class RouteStatsRequest(BaseModel):
    """Route statistics request"""
    origin: str
    destination: str


@router.get("/context")
async def get_application_context(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive application context for AI agent
    
    Returns all information about the application, database, services, and capabilities
    """
    try:
        context_provider = AIContextProvider(db)
        context = context_provider.get_comprehensive_context()
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting context: {str(e)}")


@router.post("/query-flights")
async def query_flights(
    request: FlightQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Query flights with filters
    
    Allows AI agent to search flights by various criteria
    """
    try:
        context_provider = AIContextProvider(db)
        flights = await context_provider.query_flights(
            filters=request.filters,
            limit=request.limit
        )
        return {
            "count": len(flights),
            "flights": flights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying flights: {str(e)}")


@router.get("/flight/{flight_id}")
async def get_flight_details(
    flight_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed flight information
    
    Returns comprehensive flight data including relationships
    """
    try:
        context_provider = AIContextProvider(db)
        flight = await context_provider.get_flight_details(flight_id)
        
        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")
        
        return flight
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting flight details: {str(e)}")


@router.get("/route-stats/{origin}/{destination}")
async def get_route_statistics(
    origin: str,
    destination: str,
    db: Session = Depends(get_db)
):
    """
    Get route statistics
    
    Returns historical statistics for a route
    """
    try:
        context_provider = AIContextProvider(db)
        stats = await context_provider.get_route_statistics(origin, destination)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting route statistics: {str(e)}")


@router.get("/airport-stats/{airport_code}")
async def get_airport_statistics(
    airport_code: str,
    db: Session = Depends(get_db)
):
    """
    Get airport statistics
    
    Returns airport information and statistics
    """
    try:
        context_provider = AIContextProvider(db)
        stats = await context_provider.get_airport_statistics(airport_code)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting airport statistics: {str(e)}")


@router.get("/database-schema")
async def get_database_schema(
    db: Session = Depends(get_db)
):
    """
    Get database schema information
    
    Returns detailed schema for all tables
    """
    try:
        context_provider = AIContextProvider(db)
        schema = context_provider._get_database_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting schema: {str(e)}")


@router.get("/services")
async def get_available_services(
    db: Session = Depends(get_db)
):
    """
    Get available services information
    
    Returns all services and their capabilities
    """
    try:
        context_provider = AIContextProvider(db)
        services = context_provider._get_available_services()
        return services
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting services: {str(e)}")


@router.get("/statistics")
async def get_data_statistics(
    db: Session = Depends(get_db)
):
    """
    Get database statistics
    
    Returns counts and distributions of data
    """
    try:
        context_provider = AIContextProvider(db)
        stats = context_provider._get_data_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")
