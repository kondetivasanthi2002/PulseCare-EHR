"""
PulseCare Billing, Pharmacy, Laboratory, and Analytics REST API Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.billing import InvoiceResponseSchema, ClaimResponseSchema, PrescriptionCreateSchema, PrescriptionResponseSchema, LabOrderCreateSchema, LabResultCreateSchema, LabResultResponseSchema
from app.services.billing_service import billing_service
from app.services.pharmacy_service import pharmacy_service
from app.services.lab_service import lab_service
from app.services.analytics_service import analytics_service
from app.core.exceptions import HealthcareException

billing_router = APIRouter(prefix="/billing", tags=["Billing & Claims"])
pharmacy_router = APIRouter(prefix="/pharmacy", tags=["Pharmacy & e-Prescribing"])
lab_router = APIRouter(prefix="/laboratory", tags=["Laboratory & Diagnostics"])
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics & KPIs"])


# Billing API
@billing_router.post("/invoices/generate/{encounter_id}", response_model=InvoiceResponseSchema, status_code=status.HTTP_201_CREATED)
async def generate_invoice(encounter_id: str, db: AsyncSession = Depends(get_db)):
    """Generates an itemized medical invoice from a clinical encounter."""
    try:
        return await billing_service.generate_invoice_from_encounter(db, encounter_id)
    except HealthcareException as e:
        raise HTTPException(status_code=400, detail=e.message)


@billing_router.post("/claims/submit/{invoice_id}", response_model=ClaimResponseSchema, status_code=status.HTTP_201_CREATED)
async def submit_claim(invoice_id: str, db: AsyncSession = Depends(get_db)):
    """Submits an EDI 837P electronic insurance claim."""
    try:
        return await billing_service.submit_insurance_claim(db, invoice_id, actor_id="usr_billing_1", actor_role="BILLING_CLERK")
    except HealthcareException as e:
        raise HTTPException(status_code=400, detail=e.message)


# Pharmacy API
@pharmacy_router.post("/prescriptions", response_model=PrescriptionResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_prescription(payload: PrescriptionCreateSchema, db: AsyncSession = Depends(get_db)):
    """Dispatches a new e-Prescription with drug safety collision validation."""
    try:
        return await pharmacy_service.create_prescription(
            db=db,
            patient_id=payload.patient_id,
            prescribing_doctor_id=payload.prescribing_doctor_id,
            prescribing_doctor_npi=payload.prescribing_doctor_npi,
            rxnorm_code=payload.rxnorm_code,
            medication_name=payload.medication_name,
            sig_instructions=payload.sig_instructions,
            quantity=payload.quantity,
            days_supply=payload.days_supply,
            refills_allowed=payload.refills_allowed,
            actor_id="usr_doc_1",
            actor_role="DOCTOR",
            force_override_warnings=payload.force_override_warnings
        )
    except HealthcareException as e:
        raise HTTPException(status_code=400, detail=e.message)


# Laboratory API
@lab_router.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_lab_order(payload: LabOrderCreateSchema, db: AsyncSession = Depends(get_db)):
    """Dispatches a new diagnostic laboratory order."""
    return await lab_service.create_lab_order(
        db=db,
        patient_id=payload.patient_id,
        ordering_doctor_id=payload.ordering_doctor_id,
        loinc_code=payload.loinc_code,
        clinical_reason=payload.clinical_reason,
        encounter_id=payload.encounter_id
    )


@lab_router.post("/results", response_model=LabResultResponseSchema, status_code=status.HTTP_201_CREATED)
async def record_lab_result(payload: LabResultCreateSchema, db: AsyncSession = Depends(get_db)):
    """Records lab observation values and checks LOINC reference ranges."""
    try:
        return await lab_service.record_lab_result(
            db=db,
            order_id=payload.order_id,
            loinc_code=payload.loinc_code,
            parameter_name=payload.parameter_name,
            numerical_value=payload.numerical_value,
            performing_technician_id=payload.performing_technician_id,
            actor_id="usr_tech_1",
            actor_role="LAB_TECHNICIAN"
        )
    except HealthcareException as e:
        raise HTTPException(status_code=400, detail=e.message)


# Analytics API
@analytics_router.get("/dashboard")
async def get_analytics_dashboard(db: AsyncSession = Depends(get_db)):
    """Provides operational metrics for healthcare executives."""
    return await analytics_service.get_dashboard_summary(db)
