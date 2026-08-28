"""
PulseCare Clinical Encounter REST API Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.encounter import EncounterCreateSchema, SOAPNotesUpdateSchema, EncounterDiagnosisCreateSchema, EncounterProcedureCreateSchema, EncounterResponseSchema
from app.services.encounter_service import encounter_service
from app.core.exceptions import HealthcareException

router = APIRouter(prefix="/encounters", tags=["Clinical Encounters"])


@router.post("", response_model=EncounterResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_encounter(payload: EncounterCreateSchema, db: AsyncSession = Depends(get_db)):
    """Creates a new clinical encounter note."""
    return await encounter_service.create_encounter(
        db=db,
        patient_id=payload.patient_id,
        attending_physician_id=payload.attending_physician_id,
        chief_complaint=payload.chief_complaint,
        encounter_type=payload.encounter_type
    )


@router.put("/{encounter_id}/soap", response_model=EncounterResponseSchema)
async def update_soap_notes(encounter_id: str, payload: SOAPNotesUpdateSchema, db: AsyncSession = Depends(get_db)):
    """Updates SOAP notes on an in-progress encounter."""
    try:
        return await encounter_service.update_soap_notes(
            db=db,
            encounter_id=encounter_id,
            subjective=payload.subjective,
            objective=payload.objective,
            assessment=payload.assessment,
            plan=payload.plan
        )
    except HealthcareException as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.post("/{encounter_id}/diagnoses", status_code=status.HTTP_201_CREATED)
async def add_encounter_diagnosis(encounter_id: str, payload: EncounterDiagnosisCreateSchema, db: AsyncSession = Depends(get_db)):
    """Attaches an ICD-10 diagnosis code to the encounter."""
    try:
        return await encounter_service.add_diagnosis(
            db=db,
            encounter_id=encounter_id,
            icd10_code=payload.icd10_code,
            is_primary=payload.is_primary,
            severity=payload.severity
        )
    except HealthcareException as e:
        raise HTTPException(status_code=400, detail=e.message)


@router.post("/{encounter_id}/sign", response_model=EncounterResponseSchema)
async def sign_encounter(encounter_id: str, physician_npi: str = "1928374650", db: AsyncSession = Depends(get_db)):
    """Applies digital signature to complete clinical encounter."""
    try:
        return await encounter_service.sign_off_encounter(
            db=db,
            encounter_id=encounter_id,
            physician_npi=physician_npi,
            actor_id="usr_doc_1",
            actor_role="DOCTOR"
        )
    except HealthcareException as e:
        raise HTTPException(status_code=400, detail=e.message)
