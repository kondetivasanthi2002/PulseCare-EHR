"""
PulseCare Healthcare Management Application Entrypoint.
FastAPI Web Server, Database Initialization, CORS Security, and OpenAPI Specs.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import api_router
from app.core.exceptions import HealthcareException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context: initializes database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise EHR, Patient Portal, Telehealth, and Practice Management API System.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HealthcareException)
async def healthcare_exception_handler(request, exc: HealthcareException):
    """Global exception handler for healthcare domain errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error_code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.get("/", tags=["Health Check"])
async def root():
    """System status health check endpoint."""
    return {
        "system": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "HEALTHY",
        "compliance": "HIPAA COMPLIANT",
        "fhir_r4_endpoint": f"{settings.API_V1_STR}/patients/{{id}}/fhir"
    }


app.include_router(api_router, prefix=settings.API_V1_STR)
