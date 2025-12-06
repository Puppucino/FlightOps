"""API v1 routes"""
from fastapi import APIRouter
from .routes import router as flight_delay_router
from .cargo_routes import router as cargo_router
from .flight_routes import router as flight_router
from .ai_agent_routes import router as ai_agent_router
from .flight_tracking_routes import router as flight_tracking_router
from .ai_data_routes import router as ai_data_router

# Combine all routers
router = APIRouter()
router.include_router(flight_delay_router)
router.include_router(cargo_router)
router.include_router(flight_router)
router.include_router(ai_agent_router)
router.include_router(flight_tracking_router)
router.include_router(ai_data_router)

__all__ = ["router"]

