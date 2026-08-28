"""
PulseCare Core Configuration Module.
Handles system configuration, security settings, HIPAA compliance policies, and database connection settings.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application Settings Configuration."""
    
    APP_NAME: str = "PulseCare EHR Platform"
    APP_VERSION: str = "2.4.0-enterprise"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./pulsecare_healthcare.db",
        description="SQLAlchemy Database URL"
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Security & Encryption Settings
    SECRET_KEY: str = Field(
        default="pulsecare_super_secret_jwt_signing_key_change_in_production_9847120394871029384710928374019283",
        description="JWT Secret Key"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PHI_ENCRYPTION_KEY: str = Field(
        default="A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0U1v=",
        description="Base64 encoded 256-bit AES encryption key for PHI storage"
    )
    
    # HIPAA Compliance Enforcement
    HIPAA_AUDIT_LOG_ENABLED: bool = True
    HIPAA_MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    HIPAA_SESSION_TIMEOUT_MINUTES: int = 15
    REQUIRE_MFA_FOR_DOCTORS: bool = True
    ENFORCE_PHI_ENCRYPTION_AT_REST: bool = True
    
    # Organization Metadata
    CLINIC_NAME: str = "Metropolitan Healthcare Alliance"
    CLINIC_NPI: str = "1928374650"
    CLINIC_TAX_ID: str = "12-3456789"
    CLINIC_ADDRESS: str = "100 Healthcare Boulevard, Suite 500, Medical District, NY 10001"
    CLINIC_PHONE: str = "+1 (800) 555-PULSE"
    CLINIC_EMAIL: str = "contact@pulsecare.health"
    
    # FHIR & HL7 Messaging Settings
    FHIR_SERVER_URL: str = "https://fhir.pulsecare.health/r4"
    HL7_LISTENER_PORT: int = 2575
    HL7_DEFAULT_FACILITY: str = "PULSECARE_MAIN"
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://app.pulsecare.health"
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
