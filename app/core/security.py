"""
PulseCare Security & Authentication Framework.
Handles password hashing with bcrypt, JWT token generation & verification, role-based authorization (RBAC),
and session management for Healthcare System Users (Doctors, Nurses, Patients, Admins, Billing).
"""

import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.exceptions import HIPAAViolationError


class UserRole(str, Enum):
    """System Access Roles adhering to Principle of Least Privilege (PoLP)."""
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    PATIENT = "PATIENT"
    BILLING_CLERK = "BILLING_CLERK"
    LAB_TECHNICIAN = "LAB_TECHNICIAN"
    PHARMACIST = "PHARMACIST"


class TokenData(BaseModel):
    """JWT Payload Structure."""
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[str] = Field(default_factory=list)
    npi: Optional[str] = None
    exp: Optional[int] = None


class SecurityEngine:
    """Security engine for authentication and access token generation using direct bcrypt."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against the stored bcrypt hash."""
        try:
            pwd_bytes = plain_password[:72].encode('utf-8')
            hash_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(pwd_bytes, hash_bytes)
        except Exception:
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generates a secure bcrypt hash for a given user password."""
        pwd_bytes = password[:72].encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Creates a signed JWT access token for authentication."""
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "iss": settings.APP_NAME,
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Creates a long-lived refresh token for token renewal."""
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {
            "sub": user_id,
            "type": "refresh",
            "exp": int(expire.timestamp()),
        }
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> TokenData:
        """Decodes and validates a signed JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("user_id") or payload.get("sub")
            username: str = payload.get("username", "")
            email: str = payload.get("email", "")
            role_str: str = payload.get("role", UserRole.PATIENT.value)
            permissions: List[str] = payload.get("permissions", [])
            npi: Optional[str] = payload.get("npi")

            if not user_id:
                raise HIPAAViolationError("Invalid authentication token: missing user subject ID")

            return TokenData(
                user_id=user_id,
                username=username,
                email=email,
                role=UserRole(role_str),
                permissions=permissions,
                npi=npi,
                exp=payload.get("exp")
            )
        except JWTError as e:
            raise HIPAAViolationError(f"Authentication token verification failed: {str(e)}")

    @staticmethod
    def check_role_access(required_roles: List[UserRole], user_role: UserRole) -> bool:
        """Checks whether the user's role satisfies authorization requirements."""
        if user_role == UserRole.SYSTEM_ADMIN:
            return True
        return user_role in required_roles


security_engine = SecurityEngine()
