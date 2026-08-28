"""
PulseCare Clinical Encounter Pydantic Validation Schemas.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.encounter import EncounterType, EncounterStatus


class EncounterCreateSchema(BaseModel):
    patient_id: str
    attending_physician_id: str
    chief_complaint: str
    encounter_type: EncounterType = EncounterType.CONSULTATION


class SOAPNotesUpdateSchema(BaseModel):
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None


class EncounterDiagnosisCreateSchema(BaseModel):
    icd10_code: str = Field(..., example="E11.9")
    is_primary: bool = False
    severity: str = "Moderate"


class EncounterProcedureCreateSchema(BaseModel):
    cpt_code: str = Field(..., example="99214")
    performed_by_id: str
    units_performed: int = 1


class EncounterResponseSchema(BaseModel):
    id: str
    patient_id: str
    attending_physician_id: str
    encounter_type: str
    status: str
    chief_complaint: str
    subjective_notes: Optional[str] = None
    objective_notes: Optional[str] = None
    assessment_notes: Optional[str] = None
    plan_notes: Optional[str] = None
    is_signed: bool
    signed_at: Optional[datetime] = None
    signed_by_npi: Optional[str] = None

    class Config:
        from_attributes = True
