"""
PulseCare Pharmacy & Drug Collision Detection Engine.
Validates RxNorm prescriptions, checks drug-drug interactions and patient allergies prior to dispatch.
"""

import uuid
import random
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.pharmacy import Prescription, Medication, PrescriptionStatus
from app.models.patient import PatientAllergy
from app.services.dictionaries import DRUG_INTERACTION_MATRIX
from app.core.exceptions import DrugInteractionCollisionError, HealthcareException
from app.core.audit import audit_logger, AuditActionType


class PharmacyService:
    """Service handling e-prescribing and drug safety verification."""

    @staticmethod
    def generate_prescription_number() -> str:
        return f"RX-{date.today().strftime('%Y%m')}-{random.randint(10000, 99999)}"

    async def check_drug_interactions(
        self,
        db: AsyncSession,
        patient_id: str,
        new_rxnorm_code: str,
        new_medication_name: str
    ) -> List[Dict[str, Any]]:
        """Checks new drug against patient's active prescriptions and known allergies."""
        collisions = []

        # Fetch active prescriptions
        res_rx = await db.execute(
            select(Prescription).where(
                Prescription.patient_id == patient_id,
                Prescription.status == PrescriptionStatus.ACTIVE.value
            )
        )
        active_rxs = res_rx.scalars().all()

        for rx in active_rxs:
            for rule in DRUG_INTERACTION_MATRIX:
                if (rule["drug1_rxnorm"] == new_rxnorm_code and rule["drug2_rxnorm"] == rx.rxnorm_code) or \
                   (rule["drug2_rxnorm"] == new_rxnorm_code and rule["drug1_rxnorm"] == rx.rxnorm_code):
                    collisions.append(rule)

        # Check known allergies
        res_alg = await db.execute(
            select(PatientAllergy).where(
                PatientAllergy.patient_id == patient_id,
                PatientAllergy.is_active == True
            )
        )
        allergies = res_alg.scalars().all()

        for alg in allergies:
            if alg.allergen_name.lower() in new_medication_name.lower() or new_medication_name.lower() in alg.allergen_name.lower():
                collisions.append({
                    "severity": "CRITICAL",
                    "warning": f"Patient has documented allergen match: '{alg.allergen_name}' ({alg.severity} severity)."
                })

        return collisions

    async def create_prescription(
        self,
        db: AsyncSession,
        patient_id: str,
        prescribing_doctor_id: str,
        prescribing_doctor_npi: str,
        rxnorm_code: str,
        medication_name: str,
        sig_instructions: str,
        quantity: float,
        days_supply: int,
        refills_allowed: int,
        actor_id: str,
        actor_role: str,
        force_override_warnings: bool = False
    ) -> Prescription:
        """Creates and dispatches an e-Prescription after passing safety collision checks."""
        
        collisions = await self.check_drug_interactions(db, patient_id, rxnorm_code, medication_name)

        if collisions and not force_override_warnings:
            warning_msg = " | ".join([c["warning"] for c in collisions])
            raise DrugInteractionCollisionError(f"Prescription safety alert: {warning_msg}", details={"collisions": collisions})

        rx_num = self.generate_prescription_number()
        prescription = Prescription(
            id=str(uuid.uuid4()),
            prescription_number=rx_num,
            patient_id=patient_id,
            prescribing_doctor_id=prescribing_doctor_id,
            prescribing_doctor_npi=prescribing_doctor_npi,
            rxnorm_code=rxnorm_code,
            medication_name=medication_name,
            sig_instructions=sig_instructions,
            quantity=quantity,
            days_supply=days_supply,
            refills_allowed=refills_allowed,
            refills_remaining=refills_allowed,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=days_supply),
            status=PrescriptionStatus.ACTIVE.value
        )
        db.add(prescription)

        # Audit prescription dispatch
        audit_entry = audit_logger.create_log_entry(
            action_type=AuditActionType.PRESCRIPTION_DISPATCH,
            user_id=actor_id,
            user_role=actor_role,
            resource_type="Prescription",
            patient_id=patient_id,
            resource_id=prescription.id,
            details={"prescription_number": rx_num, "rxnorm": rxnorm_code}
        )
        db.add(audit_entry)

        return prescription


pharmacy_service = PharmacyService()
