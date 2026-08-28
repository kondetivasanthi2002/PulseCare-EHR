"""
Test Suite 4: Billing Invoices, Copay Calculations, and EDI 837P Insurance Claims.
"""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.patient_service import patient_service
from app.services.encounter_service import encounter_service
from app.services.billing_service import billing_service
from app.models.patient import InsurancePolicy


@pytest.mark.asyncio
async def test_billing_invoice_and_claim_generation(db_session: AsyncSession):
    """Test 4.1: Generates invoice from CPT codes, calculates copay, and generates EDI 837P claim."""
    # 1. Setup Patient with Insurance Policy
    patient = await patient_service.register_patient(
        db=db_session,
        first_name="Alice",
        last_name="Williams",
        date_of_birth=date(1988, 7, 24),
        email="alice.w@example.com",
        phone="+1-555-0166",
        address_line1="101 Pine St",
        city="Seattle",
        state="WA",
        postal_code="98101",
        actor_id="test_runner",
        actor_role="DOCTOR"
    )

    policy = InsurancePolicy(
        patient_id=patient.id,
        payer_name="Blue Cross Blue Shield",
        payer_id="BCBS-WA-99",
        policy_number="POL-98471203",
        subscriber_name="Alice Williams",
        effective_date=date(2023, 1, 1),
        copay_amount=25.00,
        is_primary=True
    )
    db_session.add(policy)
    await db_session.flush()

    # 2. Setup Encounter with 2 CPT procedures
    encounter = await encounter_service.create_encounter(
        db=db_session,
        patient_id=patient.id,
        attending_physician_id="doc_202",
        chief_complaint="Annual Physical Examination"
    )
    await encounter_service.add_procedure(db_session, encounter.id, "99214", "doc_202")  # $195.00
    await encounter_service.add_procedure(db_session, encounter.id, "93000", "doc_202")  # $110.00
    # Total = $305.00

    # 3. Generate Invoice
    invoice = await billing_service.generate_invoice_from_encounter(db_session, encounter.id)
    
    assert invoice.subtotal_amount == 305.00
    assert invoice.patient_copay_amount == 25.00
    assert invoice.insurance_covered_amount == 280.00 # 305 - 25

    # 4. Submit Insurance Claim (EDI 837P)
    claim = await billing_service.submit_insurance_claim(
        db_session, invoice.id, actor_id="billing_clerk_1", actor_role="BILLING_CLERK"
    )
    assert claim.claim_control_number.startswith("CLM-837P-")
    assert claim.submitted_amount == 280.00
    assert claim.status == "SUBMITTED"
    assert claim.claim_payload_json["transaction_set"] == "837P"
