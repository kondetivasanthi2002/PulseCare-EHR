"""
PulseCare Authentication & Token Management Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.security import security_engine, UserRole
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.DOCTOR


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    role: UserRole


@router.post("/login", response_model=TokenResponse)
async def login_access_token(req: LoginRequest):
    """Generates a signed JWT access token for authentication."""
    # Simplified authentication check for demonstration / API client access
    token_payload = {
        "user_id": f"usr_{req.username}",
        "username": req.username,
        "email": f"{req.username}@pulsecare.health",
        "role": req.role.value,
        "npi": "1234567890" if req.role == UserRole.DOCTOR else None
    }
    
    token = security_engine.create_access_token(token_payload)
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        role=req.role
    )
