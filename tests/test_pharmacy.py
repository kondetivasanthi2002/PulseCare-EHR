"""
Test Suite 5: e-Prescribing & Drug Safety Interaction Matrix.
"""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.patient_service import patient_service
from app.services.pharmacy_service import pharmacy_service
from app.models.patient import PatientAllergy
from app.core.exceptions import DrugInteractionCollisionError


@pytest.mark.asyncio
async def test_drug_drug_interaction_prevention(db_session: AsyncSession):
    """Test 5.1: Detects dangerous Warfarin + Aspirin drug collision and blocks prescription unless overridden."""
    patient = await patient_service.register_patient(
        db=db_session,
        first_name="Charles",
        last_name="Brown",
        date_of_birth=date(1965, 8, 14),
        email="charles.b@example.com",
        phone="+1-555-0155",
        address_line1="12 Walnut St",
        city="Chicago",
        state="IL",
        postal_code="60601",
        actor_id="test_runner",
        actor_role="DOCTOR"
    )

    # Prescribe Warfarin (RxNorm: 313782)
    rx1 = await pharmacy_service.create_prescription(
        db=db_session,
        patient_id=patient.id,
        prescribing_doctor_id="doc_303",
        prescribing_doctor_npi="1928374650",
        rxnorm_code="313782",
        medication_name="Warfarin Sodium 5mg",
        sig_instructions="Take 1 tablet daily",
        quantity=30.0,
        days_supply=30,
        refills_allowed=2,
        actor_id="doc_303",
        actor_role="DOCTOR"
    )
    assert rx1.prescription_number.startswith("RX-")

    # Attempt to prescribe Aspirin (RxNorm: 1191) -> Should raise DrugInteractionCollisionError!
    with pytest.raises(DrugInteractionCollisionError) as exc_info:
        await pharmacy_service.create_prescription(
            db=db_session,
            patient_id=patient.id,
            prescribing_doctor_id="doc_303",
            prescribing_doctor_npi="1928374650",
            rxnorm_code="1191",
            medication_name="Aspirin 325mg",
            sig_instructions="Take 1 tablet daily",
            quantity=30.0,
            days_supply=30,
            refills_allowed=0,
            actor_id="doc_303",
            actor_role="DOCTOR",
            force_override_warnings=False
        )

    assert "Warfarin" in str(exc_info.value)
    assert "Aspirin" in str(exc_info.value)


@pytest.mark.asyncio
async def test_drug_allergy_collision_detection(db_session: AsyncSession):
    """Test 5.2: Detects known patient drug allergen collision (Penicillin)."""
    patient = await patient_service.register_patient(
        db=db_session,
        first_name="David",
        last_name="Miller",
        date_of_birth=date(1992, 1, 30),
        email="david.m@example.com",
        phone="+1-555-0144",
        address_line1="55 Elm St",
        city="Chicago",
        state="IL",
        postal_code="60601",
        actor_id="test_runner",
        actor_role="DOCTOR"
    )

    # Document Penicillin Allergy
    allergy = PatientAllergy(
        patient_id=patient.id,
        allergen_name="Penicillin",
        allergy_type="Drug",
        severity="Anaphylactic",
        reaction_description="Hives and dyspnea",
        is_active=True
    )
    db_session.add(allergy)
    await db_session.flush()

    # Attempt to prescribe Penicillin V Potassium
    with pytest.raises(DrugInteractionCollisionError) as exc_info:
        await pharmacy_service.create_prescription(
            db=db_session,
            patient_id=patient.id,
            prescribing_doctor_id="doc_303",
            prescribing_doctor_npi="1928374650",
            rxnorm_code="834060",
            medication_name="Penicillin V Potassium 500mg",
            sig_instructions="Take 1 tablet every 6 hours",
            quantity=40.0,
            days_supply=10,
            refills_allowed=0,
            actor_id="doc_303",
            actor_role="DOCTOR"
        )

    assert "Penicillin" in str(exc_info.value)
