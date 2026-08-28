"""
PulseCare Clinical Encounter Business Service.
Handles clinical SOAP documentation, ICD-10-CM diagnosis assignment, CPT procedure billing entries, and digital signatures.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.encounter import ClinicalEncounter, EncounterDiagnosis, EncounterProcedure, EncounterType, EncounterStatus
from app.services.dictionaries import ICD10_CATALOG, CPT_CATALOG
from app.core.exceptions import InvalidICD10CodeError, InvalidCPTCodeError, HealthcareException
from app.core.audit import audit_logger, AuditActionType


class EncounterService:
    """Service handling clinical documentation workflows."""

    async def create_encounter(
        self,
        db: AsyncSession,
        patient_id: str,
        attending_physician_id: str,
        chief_complaint: str,
        encounter_type: EncounterType = EncounterType.CONSULTATION,
        start_time: Optional[datetime] = None
    ) -> ClinicalEncounter:
        """Creates a new clinical encounter record."""
        encounter = ClinicalEncounter(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            attending_physician_id=attending_physician_id,
            chief_complaint=chief_complaint,
            encounter_type=encounter_type.value,
            status=EncounterStatus.IN_PROGRESS.value,
            start_time=start_time or datetime.now(timezone.utc),
            is_signed=False
        )
        db.add(encounter)
        return encounter

    async def update_soap_notes(
        self,
        db: AsyncSession,
        encounter_id: str,
        subjective: Optional[str] = None,
        objective: Optional[str] = None,
        assessment: Optional[str] = None,
        plan: Optional[str] = None
    ) -> ClinicalEncounter:
        """Updates SOAP notes (Subjective, Objective, Assessment, Plan) for an in-progress encounter."""
        result = await db.execute(select(ClinicalEncounter).where(ClinicalEncounter.id == encounter_id))
        encounter = result.scalars().first()

        if not encounter:
            raise HealthcareException(f"Clinical encounter {encounter_id} not found", code="ENCOUNTER_NOT_FOUND")

        if encounter.is_signed:
            raise HealthcareException("Cannot modify signed clinical encounter notes", code="ENCOUNTER_ALREADY_SIGNED")

        if subjective is not None:
            encounter.subjective_notes = subjective
        if objective is not None:
            encounter.objective_notes = objective
        if assessment is not None:
            encounter.assessment_notes = assessment
        if plan is not None:
            encounter.plan_notes = plan

        return encounter

    async def add_diagnosis(
        self,
        db: AsyncSession,
        encounter_id: str,
        icd10_code: str,
        is_primary: bool = False,
        severity: str = "Moderate"
    ) -> EncounterDiagnosis:
        """Validates and links an ICD-10 diagnosis code to an encounter."""
        if icd10_code not in ICD10_CATALOG:
            raise InvalidICD10CodeError(icd10_code)

        meta = ICD10_CATALOG[icd10_code]
        diagnosis = EncounterDiagnosis(
            id=str(uuid.uuid4()),
            encounter_id=encounter_id,
            icd10_code=icd10_code,
            description=meta["description"],
            is_primary=is_primary,
            severity=severity
        )
        db.add(diagnosis)
        return diagnosis

    async def add_procedure(
        self,
        db: AsyncSession,
        encounter_id: str,
        cpt_code: str,
        performed_by_id: str,
        units_performed: int = 1
    ) -> EncounterProcedure:
        """Validates and links a CPT procedure code to an encounter."""
        if cpt_code not in CPT_CATALOG:
            raise InvalidCPTCodeError(cpt_code)

        meta = CPT_CATALOG[cpt_code]
        procedure = EncounterProcedure(
            id=str(uuid.uuid4()),
            encounter_id=encounter_id,
            cpt_code=cpt_code,
            description=meta["description"],
            unit_cost=meta["base_price"],
            units_performed=units_performed,
            performed_by_id=performed_by_id
        )
        db.add(procedure)
        return procedure

    async def sign_off_encounter(
        self,
        db: AsyncSession,
        encounter_id: str,
        physician_npi: str,
        actor_id: str,
        actor_role: str
    ) -> ClinicalEncounter:
        """Applies digital signature to complete and lock a clinical encounter."""
        result = await db.execute(select(ClinicalEncounter).where(ClinicalEncounter.id == encounter_id))
        encounter = result.scalars().first()

        if not encounter:
            raise HealthcareException("Encounter not found")

        encounter.is_signed = True
        encounter.signed_at = datetime.now(timezone.utc)
        encounter.signed_by_npi = physician_npi
        encounter.end_time = datetime.now(timezone.utc)
        encounter.status = EncounterStatus.SIGNED_OFF.value

        # Audit log
        audit_entry = audit_logger.create_log_entry(
            action_type=AuditActionType.PHI_UPDATE,
            user_id=actor_id,
            user_role=actor_role,
            resource_type="ClinicalEncounter",
            patient_id=encounter.patient_id,
            resource_id=encounter.id,
            details={"action": "Signed off clinical encounter", "npi": physician_npi}
        )
        db.add(audit_entry)

        return encounter


encounter_service = EncounterService()
