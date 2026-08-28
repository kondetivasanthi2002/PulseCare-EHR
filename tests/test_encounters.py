"""
Test Suite 3: Clinical Documentation, SOAP Notes, and Medical Coding.
"""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.patient_service import patient_service
from app.services.encounter_service import encounter_service
from app.models.encounter import EncounterType
from app.core.exceptions import InvalidICD10CodeError, InvalidCPTCodeError


@pytest.mark.asyncio
async def test_encounter_workflow_and_coding(db_session: AsyncSession):
    """Test 3.1: Clinical encounter workflow, SOAP notes, ICD-10/CPT attachment, and digital sign-off."""
    # Create patient
    patient = await patient_service.register_patient(
        db=db_session,
        first_name="Robert",
        last_name="Johnson",
        date_of_birth=date(1975, 3, 10),
        email="robert.j@example.com",
        phone="+1-555-0177",
        address_line1="789 Care Rd",
        city="Austin",
        state="TX",
        postal_code="73301",
        actor_id="test_runner",
        actor_role="DOCTOR"
    )

    # 1. Create encounter
    encounter = await encounter_service.create_encounter(
        db=db_session,
        patient_id=patient.id,
        attending_physician_id="doc_101",
        chief_complaint="Chest tightness and shortness of breath",
        encounter_type=EncounterType.URGENT_CARE
    )
    assert encounter.status == "IN_PROGRESS"
    assert encounter.is_signed is False

    # 2. Update SOAP Notes
    encounter = await encounter_service.update_soap_notes(
        db=db_session,
        encounter_id=encounter.id,
        subjective="Patient reports mild exertional dyspnea.",
        objective="Vitals stable. ECG normal sinus rhythm.",
        assessment="Hypertension and mild asthma exacerbation.",
        plan="Start Lisinopril 10mg daily and Albuterol inhaler."
    )
    assert encounter.assessment_notes == "Hypertension and mild asthma exacerbation."

    # 3. Add Valid ICD-10 Diagnosis (Essential Hypertension)
    diagnosis = await encounter_service.add_diagnosis(
        db=db_session,
        encounter_id=encounter.id,
        icd10_code="I10",
        is_primary=True
    )
    assert diagnosis.icd10_code == "I10"

    # 4. Add Valid CPT Procedure (Office visit 99214)
    procedure = await encounter_service.add_procedure(
        db=db_session,
        encounter_id=encounter.id,
        cpt_code="99214",
        performed_by_id="doc_101"
    )
    assert procedure.cpt_code == "99214"
    assert procedure.unit_cost == 195.00

    # 5. Sign off encounter
    signed_encounter = await encounter_service.sign_off_encounter(
        db=db_session,
        encounter_id=encounter.id,
        physician_npi="1928374650",
        actor_id="doc_101",
        actor_role="DOCTOR"
    )
    assert signed_encounter.is_signed is True
    assert signed_encounter.status == "SIGNED_OFF"


@pytest.mark.asyncio
async def test_invalid_icd10_code_rejection(db_session: AsyncSession):
    """Test 3.2: Rejects invalid or nonexistent ICD-10 code."""
    with pytest.raises(InvalidICD10CodeError):
        await encounter_service.add_diagnosis(
            db=db_session,
            encounter_id="fake_enc",
            icd10_code="INVALID_CODE_99"
        )
