"""
Test Suite 2: Patient Demographics, Vitals Tracking, and SSN Decryption.
"""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.patient_service import patient_service
from app.models.patient import Gender, BloodType


@pytest.mark.asyncio
async def test_patient_registration_and_ssn_encryption(db_session: AsyncSession):
    """Test 2.1: Registers patient, verifies MRN generation and SSN encryption."""
    patient = await patient_service.register_patient(
        db=db_session,
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1990, 5, 15),
        email="jane.doe@example.com",
        phone="+1-555-0199",
        address_line1="123 Health Way",
        city="Boston",
        state="MA",
        postal_code="02108",
        actor_id="test_runner",
        actor_role="DOCTOR",
        ssn="888-00-1122",
        gender=Gender.FEMALE,
        blood_type=BloodType.A_POSITIVE
    )
    
    assert patient.id is not None
    assert patient.mrn.startswith("MRN-")
    assert patient.full_name == "Jane Doe"
    assert patient.get_ssn() == "888-00-1122"
    assert patient.ssn_encrypted != "888-00-1122"


@pytest.mark.asyncio
async def test_patient_vitals_logging_and_bmi_calculation(db_session: AsyncSession):
    """Test 2.2: Logs patient vitals and calculates Body Mass Index (BMI)."""
    patient = await patient_service.register_patient(
        db=db_session,
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1982, 11, 20),
        email="john.smith@example.com",
        phone="+1-555-0188",
        address_line1="456 Medical Ave",
        city="Boston",
        state="MA",
        postal_code="02108",
        actor_id="test_runner",
        actor_role="DOCTOR"
    )

    vitals = await patient_service.add_patient_vitals(
        db=db_session,
        patient_id=patient.id,
        recorded_by_id="nurse_1",
        systolic_bp=120.0,
        diastolic_bp=80.0,
        heart_rate=72.0,
        respiratory_rate=16.0,
        body_temperature=37.0,
        oxygen_saturation=99.0,
        height_cm=180.0,
        weight_kg=81.0
    )

    assert vitals.id is not None
    assert vitals.systolic_bp == 120.0
    assert vitals.bmi == 25.0  # 81 / (1.8 * 1.8) = 25.0
