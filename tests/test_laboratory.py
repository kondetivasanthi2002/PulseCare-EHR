"""
Test Suite 6 & 7: Laboratory LOINC Orders, Critical Value Alerts, and HL7/FHIR Interoperability.
"""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.patient_service import patient_service
from app.services.lab_service import lab_service
from app.services.fhir import fhir_mapper
from app.services.hl7 import hl7_engine


@pytest.mark.asyncio
async def test_lab_order_and_critical_value_alert(db_session: AsyncSession):
    """Test 6.1: Dispatches LOINC lab order, enters observation result, and detects critical glucose alert."""
    patient = await patient_service.register_patient(
        db=db_session,
        first_name="Emma",
        last_name="Davis",
        date_of_birth=date(1995, 12, 5),
        email="emma.d@example.com",
        phone="+1-555-0133",
        address_line1="88 Oak St",
        city="Denver",
        state="CO",
        postal_code="80202",
        actor_id="test_runner",
        actor_role="DOCTOR"
    )

    # Dispatch Glucose lab order (LOINC: 2345-7)
    order = await lab_service.create_lab_order(
        db=db_session,
        patient_id=patient.id,
        ordering_doctor_id="doc_404",
        loinc_code="2345-7",
        clinical_reason="Suspected severe hypoglycemia episode"
    )
    assert order.order_number.startswith("LAB-")

    # Enter Critical Low Glucose result (35.0 mg/dL - Reference Low: 70.0, Critical Low: 40.0)
    result = await lab_service.record_lab_result(
        db=db_session,
        order_id=order.id,
        loinc_code="2345-7",
        parameter_name="Fasting Blood Glucose",
        numerical_value=35.0,
        performing_technician_id="tech_707",
        actor_id="tech_707",
        actor_role="LAB_TECHNICIAN"
    )

    assert result.is_abnormal is True
    assert result.is_critical is True
    assert result.unit_of_measure == "mg/dL"


@pytest.mark.asyncio
async def test_hl7_message_generation_and_parsing(db_session: AsyncSession):
    """Test 7.1: Generates ADT^A08 HL7 message and parses incoming ORU^R01 lab results."""
    patient = await patient_service.register_patient(
        db=db_session,
        first_name="George",
        last_name="Wilson",
        date_of_birth=date(1980, 4, 18),
        email="george.w@example.com",
        phone="+1-555-0122",
        address_line1="99 Pine Ave",
        city="Denver",
        state="CO",
        postal_code="80202",
        actor_id="test_runner",
        actor_role="DOCTOR"
    )

    # 1. Generate ADT^A08 HL7 string
    adt_msg = hl7_engine.generate_adt_a08(patient)
    assert "MSH|^~\\&|PULSECARE" in adt_msg
    assert "ADT^A08" in adt_msg
    assert "Wilson^George" in adt_msg

    # 2. Parse sample incoming ORU^R01 HL7 message
    sample_hl7_oru = (
        "MSH|^~\\&|CENTRAL_LAB|LAB1|PULSECARE|MAIN|20260828110000||ORU^R01|MSG99001|P|2.5\r"
        f"PID|1||{patient.mrn}^^^PULSECARE^MR||Wilson^George||19800418|M\r"
        "OBR|1|ORD10099||2345-7^Glucose^LN|||20260828110000\r"
        "OBX|1|NM|2345-7^Fasting Blood Glucose^LN||85|mg/dL|70-99|N|||F"
    )
    parsed = hl7_engine.parse_oru_r01(sample_hl7_oru)
    assert parsed["message_type"] == "ORU_R01"
    assert parsed["patient_mrn"] == patient.mrn
    assert len(parsed["observations"]) == 1
    assert parsed["observations"][0]["value"] == "85"


@pytest.mark.asyncio
async def test_fhir_r4_patient_json_export(db_session: AsyncSession):
    """Test 7.2: Serializes patient record to valid HL7 FHIR R4 JSON schema."""
    patient = await patient_service.register_patient(
        db=db_session,
        first_name="Hannah",
        last_name="Taylor",
        date_of_birth=date(1998, 9, 9),
        email="hannah.t@example.com",
        phone="+1-555-0111",
        address_line1="123 Birch Rd",
        city="Denver",
        state="CO",
        postal_code="80202",
        actor_id="test_runner",
        actor_role="DOCTOR"
    )

    fhir_json = fhir_mapper.patient_to_fhir(patient)
    assert fhir_json["resourceType"] == "Patient"
    assert fhir_json["id"] == patient.id
    assert fhir_json["name"][0]["family"] == "Taylor"
    assert fhir_json["name"][0]["given"] == ["Hannah"]
    assert fhir_json["identifier"][0]["value"] == patient.mrn
