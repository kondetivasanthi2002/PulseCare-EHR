"""
PulseCare Patient Pydantic Validation Schemas.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from app.models.patient import Gender, BloodType


class PatientBaseSchema(BaseModel):
    first_name: str = Field(..., example="Eleanor")
    last_name: str = Field(..., example="Vance")
    date_of_birth: date = Field(..., example="1985-04-12")
    gender: Gender = Gender.FEMALE
    email: EmailStr = Field(..., example="eleanor.vance@example.com")
    phone: str = Field(..., example="+1-555-0192")
    address_line1: str = Field(..., example="742 Evergreen Terrace")
    address_line2: Optional[str] = None
    city: str = Field(..., example="Springfield")
    state: str = Field(..., example="OR")
    postal_code: str = Field(..., example="97477")
    blood_type: BloodType = BloodType.O_POSITIVE
    primary_language: str = "English"


class PatientCreateSchema(PatientBaseSchema):
    ssn: Optional[str] = Field(None, example="999-00-1234")


class PatientResponseSchema(PatientBaseSchema):
    id: str
    mrn: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientVitalsSchema(BaseModel):
    systolic_bp: float = Field(..., example=120.0)
    diastolic_bp: float = Field(..., example=80.0)
    heart_rate: float = Field(..., example=72.0)
    respiratory_rate: float = Field(..., example=16.0)
    body_temperature: float = Field(..., example=37.0)
    oxygen_saturation: float = Field(..., example=98.5)
    height_cm: float = Field(..., example=168.0)
    weight_kg: float = Field(..., example=65.0)


class PatientVitalsResponseSchema(PatientVitalsSchema):
    id: str
    patient_id: str
    bmi: float
    recorded_at: datetime

    class Config:
        from_attributes = True
