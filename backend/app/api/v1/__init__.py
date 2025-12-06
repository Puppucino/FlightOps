"""API v1 routes"""
from fastapi import APIRouter
from .routes import router as flight_delay_router
from .cargo_routes import router as cargo_router
from .flight_routes import router as flight_router

# Combine all routers
router = APIRouter()
router.include_router(flight_delay_router)
router.include_router(cargo_router)
router.include_router(flight_router)

__all__ = ["router"]

