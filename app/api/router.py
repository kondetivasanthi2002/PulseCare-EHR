"""
PulseCare Main API Router Aggregator.
"""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.patients import router as patients_router
from app.api.v1.encounters import router as encounters_router
from app.api.v1.endpoints import billing_router, pharmacy_router, lab_router, analytics_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(patients_router)
api_router.include_router(encounters_router)
api_router.include_router(billing_router)
api_router.include_router(pharmacy_router)
api_router.include_router(lab_router)
api_router.include_router(analytics_router)
