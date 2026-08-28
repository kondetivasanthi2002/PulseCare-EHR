"""
PulseCare Billing, Invoicing & Electronic Insurance Claims Engine.
Automates claim payload generation (EDI 837P / CMS-1500), copay allocation, line item pricing, and claim adjudication.
"""

import uuid
import random
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.billing import PatientInvoice, InvoiceLineItem, InsuranceClaim, ClaimStatus, PaymentStatus
from app.models.patient import InsurancePolicy
from app.models.encounter import ClinicalEncounter, EncounterProcedure
from app.core.exceptions import HealthcareException, InsufficientInsuranceCoverageError
from app.core.audit import audit_logger, AuditActionType


class BillingService:
    """Service handling medical invoicing and electronic insurance claims engine."""

    @staticmethod
    def generate_invoice_number() -> str:
        return f"INV-{date.today().strftime('%Y%m')}-{random.randint(1000, 9999)}"

    @staticmethod
    def generate_claim_control_number() -> str:
        return f"CLM-837P-{random.randint(100000, 999999)}"

    async def generate_invoice_from_encounter(
        self,
        db: AsyncSession,
        encounter_id: str,
        due_days: int = 30
    ) -> PatientInvoice:
        """Generates an itemized patient invoice from an encounter's CPT procedures."""
        res_enc = await db.execute(select(ClinicalEncounter).where(ClinicalEncounter.id == encounter_id))
        encounter = res_enc.scalars().first()
        if not encounter:
            raise HealthcareException(f"Encounter {encounter_id} not found")

        # Fetch associated CPT procedures
        res_proc = await db.execute(select(EncounterProcedure).where(EncounterProcedure.encounter_id == encounter_id))
        procedures = res_proc.scalars().all()

        invoice_num = self.generate_invoice_number()
        issue_dt = date.today()
        due_dt = issue_dt + timedelta(days=due_days)

        invoice = PatientInvoice(
            id=str(uuid.uuid4()),
            invoice_number=invoice_num,
            patient_id=encounter.patient_id,
            encounter_id=encounter.id,
            issue_date=issue_dt,
            due_date=due_dt,
            subtotal_amount=0.0,
            insurance_covered_amount=0.0,
            patient_copay_amount=0.0,
            total_amount_due=0.0,
            amount_paid=0.0,
            payment_status=PaymentStatus.UNPAID.value
        )
        db.add(invoice)
        await db.flush()

        subtotal = 0.0
        for proc in procedures:
            line_total = proc.unit_cost * proc.units_performed
            subtotal += line_total
            line_item = InvoiceLineItem(
                id=str(uuid.uuid4()),
                invoice_id=invoice.id,
                cpt_code=proc.cpt_code,
                description=proc.description,
                quantity=proc.units_performed,
                unit_price=proc.unit_cost,
                total_price=line_total
            )
            db.add(line_item)

        # Check for active insurance policy to calculate copay
        res_ins = await db.execute(select(InsurancePolicy).where(InsurancePolicy.patient_id == encounter.patient_id, InsurancePolicy.is_primary == True))
        policy = res_ins.scalars().first()

        copay = policy.copay_amount if policy else 20.0
        insurance_covered = max(0.0, subtotal - copay)

        invoice.subtotal_amount = round(subtotal, 2)
        invoice.patient_copay_amount = round(copay, 2)
        invoice.insurance_covered_amount = round(insurance_covered, 2)
        invoice.total_amount_due = round(copay, 2) # Patient owes copay

        return invoice

    async def submit_insurance_claim(
        self,
        db: AsyncSession,
        invoice_id: str,
        actor_id: str,
        actor_role: str
    ) -> InsuranceClaim:
        """Constructs an electronic EDI 837P claim payload and submits to insurance payer."""
        res_inv = await db.execute(select(PatientInvoice).where(PatientInvoice.id == invoice_id))
        invoice = res_inv.scalars().first()
        if not invoice:
            raise HealthcareException("Invoice not found")

        res_ins = await db.execute(select(InsurancePolicy).where(InsurancePolicy.patient_id == invoice.patient_id, InsurancePolicy.is_primary == True))
        policy = res_ins.scalars().first()
        if not policy:
            raise InsufficientInsuranceCoverageError("N/A", "Patient has no primary insurance policy on file.")

        claim_num = self.generate_claim_control_number()
        
        # Build EDI 837P JSON Payload
        payload = {
            "transaction_set": "837P",
            "control_number": claim_num,
            "payer_name": policy.payer_name,
            "payer_id": policy.payer_id,
            "subscriber_name": policy.subscriber_name,
            "policy_number": policy.policy_number,
            "total_submitted_amount": invoice.insurance_covered_amount,
            "service_date": invoice.issue_date.isoformat(),
        }

        claim = InsuranceClaim(
            id=str(uuid.uuid4()),
            claim_control_number=claim_num,
            invoice_id=invoice.id,
            patient_id=invoice.patient_id,
            policy_number=policy.policy_number,
            payer_id=policy.payer_id,
            submitted_amount=invoice.insurance_covered_amount,
            status=ClaimStatus.SUBMITTED.value,
            submission_date=datetime.now(timezone.utc),
            claim_payload_json=payload
        )
        db.add(claim)

        # Audit submission
        audit_entry = audit_logger.create_log_entry(
            action_type=AuditActionType.CLAIM_SUBMISSION,
            user_id=actor_id,
            user_role=actor_role,
            resource_type="InsuranceClaim",
            patient_id=invoice.patient_id,
            resource_id=claim.id,
            details={"claim_control_number": claim_num, "amount": invoice.insurance_covered_amount}
        )
        db.add(audit_entry)

        return claim


billing_service = BillingService()
