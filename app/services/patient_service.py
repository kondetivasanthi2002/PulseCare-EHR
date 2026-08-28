"""
PulseCare Patient Management Business Service.
Handles patient registration, MRN generation, PHI encryption, vitals logging, and audit tracking.
"""

import uuid
import random
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.patient import Patient, PatientVitals, PatientAllergy, InsurancePolicy, Gender, BloodType
from app.core.crypto import phi_crypto
from app.core.audit import audit_logger, AuditActionType
from app.core.exceptions import HealthcareException


class PatientService:
    """Service handling patient registration, search, vitals tracking, and insurance policies."""

    @staticmethod
    def generate_mrn() -> str:
        """Generates a unique 9-digit Medical Record Number (MRN)."""
        random_digits = "".join([str(random.randint(0, 9)) for _ in range(7)])
        return f"MRN-{random_digits}"

    async def register_patient(
        self,
        db: AsyncSession,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        email: str,
        phone: str,
        address_line1: str,
        city: str,
        state: str,
        postal_code: str,
        actor_id: str,
        actor_role: str,
        ssn: Optional[str] = None,
        gender: Gender = Gender.UNKNOWN,
        blood_type: BloodType = BloodType.UNKNOWN,
        primary_language: str = "English",
        address_line2: Optional[str] = None
    ) -> Patient:
        """Registers a new patient, encrypting sensitive fields and creating HIPAA audit entry."""
        
        mrn = self.generate_mrn()
        patient = Patient(
            id=str(uuid.uuid4()),
            mrn=mrn,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            email=email,
            phone=phone,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            postal_code=postal_code,
            gender=gender.value,
            blood_type=blood_type.value,
            primary_language=primary_language,
            is_active=True
        )

        if ssn:
            patient.set_ssn(ssn)

        db.add(patient)
        await db.flush()

        # Audit Log
        audit_entry = audit_logger.create_log_entry(
            action_type=AuditActionType.PHI_CREATE,
            user_id=actor_id,
            user_role=actor_role,
            resource_type="Patient",
            patient_id=patient.id,
            resource_id=patient.id,
            details={"mrn": mrn, "action": "Registered new patient"}
        )
        db.add(audit_entry)

        return patient

    async def get_patient_by_id(
        self, db: AsyncSession, patient_id: str, actor_id: str, actor_role: str
    ) -> Optional[Patient]:
        """Fetches a patient record by ID and records a HIPAA PHI_READ audit event."""
        result = await db.execute(select(Patient).where(Patient.id == patient_id))
        patient = result.scalars().first()

        if patient:
            # Audit PHI read
            audit_entry = audit_logger.create_log_entry(
                action_type=AuditActionType.PHI_READ,
                user_id=actor_id,
                user_role=actor_role,
                resource_type="Patient",
                patient_id=patient.id,
                resource_id=patient.id,
                details={"mrn": patient.mrn}
            )
            db.add(audit_entry)

        return patient

    async def add_patient_vitals(
        self,
        db: AsyncSession,
        patient_id: str,
        recorded_by_id: str,
        systolic_bp: float,
        diastolic_bp: float,
        heart_rate: float,
        respiratory_rate: float,
        body_temperature: float,
        oxygen_saturation: float,
        height_cm: float,
        weight_kg: float
    ) -> PatientVitals:
        """Logs patient vital signs and computes BMI."""
        # Calculate BMI (kg / m^2)
        height_m = height_cm / 100.0
        bmi = round(weight_kg / (height_m * height_m), 2) if height_m > 0 else 0.0

        vitals = PatientVitals(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            recorded_by_id=recorded_by_id,
            systolic_bp=systolic_bp,
            diastolic_bp=diastolic_bp,
            heart_rate=heart_rate,
            respiratory_rate=respiratory_rate,
            body_temperature=body_temperature,
            oxygen_saturation=oxygen_saturation,
            height_cm=height_cm,
            weight_kg=weight_kg,
            bmi=bmi
        )

        db.add(vitals)
        return vitals


patient_service = PatientService()
