"""
PulseCare Patient Management REST API Endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.patient import PatientCreateSchema, PatientResponseSchema, PatientVitalsSchema, PatientVitalsResponseSchema
from app.services.patient_service import patient_service
from app.services.fhir import fhir_mapper
from app.core.exceptions import HealthcareException

router = APIRouter(prefix="/patients", tags=["Patients & EHR"])


@router.post("", response_model=PatientResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_patient(payload: PatientCreateSchema, db: AsyncSession = Depends(get_db)):
    """Registers a new patient record in the EHR system."""
    patient = await patient_service.register_patient(
        db=db,
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=payload.date_of_birth,
        email=payload.email,
        phone=payload.phone,
        address_line1=payload.address_line1,
        address_line2=payload.address_line2,
        city=payload.city,
        state=payload.state,
        postal_code=payload.postal_code,
        actor_id="system_api",
        actor_role="DOCTOR",
        ssn=payload.ssn,
        gender=payload.gender,
        blood_type=payload.blood_type,
        primary_language=payload.primary_language
    )
    return patient


@router.get("/{patient_id}", response_model=PatientResponseSchema)
async def get_patient(patient_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves patient demographics record."""
    patient = await patient_service.get_patient_by_id(db, patient_id, actor_id="system_api", actor_role="DOCTOR")
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/{patient_id}/fhir", response_model=dict)
async def export_patient_fhir(patient_id: str, db: AsyncSession = Depends(get_db)):
    """Exports patient record as an HL7 FHIR R4 JSON resource."""
    patient = await patient_service.get_patient_by_id(db, patient_id, actor_id="system_api", actor_role="DOCTOR")
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return fhir_mapper.patient_to_fhir(patient)


@router.post("/{patient_id}/vitals", response_model=PatientVitalsResponseSchema, status_code=status.HTTP_201_CREATED)
async def log_patient_vitals(patient_id: str, payload: PatientVitalsSchema, db: AsyncSession = Depends(get_db)):
    """Logs vital signs observation for a patient."""
    vitals = await patient_service.add_patient_vitals(
        db=db,
        patient_id=patient_id,
        recorded_by_id="usr_nurse_1",
        systolic_bp=payload.systolic_bp,
        diastolic_bp=payload.diastolic_bp,
        heart_rate=payload.heart_rate,
        respiratory_rate=payload.respiratory_rate,
        body_temperature=payload.body_temperature,
        oxygen_saturation=payload.oxygen_saturation,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg
    )
    return vitals
