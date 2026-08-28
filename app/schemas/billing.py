"""
PulseCare Billing, Pharmacy, and Lab Pydantic Schemas.
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Billing Schemas
class InvoiceResponseSchema(BaseModel):
    id: str
    invoice_number: str
    patient_id: str
    encounter_id: Optional[str]
    issue_date: date
    due_date: date
    subtotal_amount: float
    insurance_covered_amount: float
    patient_copay_amount: float
    total_amount_due: float
    payment_status: str

    class Config:
        from_attributes = True


class ClaimResponseSchema(BaseModel):
    id: str
    claim_control_number: str
    invoice_id: str
    patient_id: str
    policy_number: str
    submitted_amount: float
    status: str
    submission_date: datetime

    class Config:
        from_attributes = True


# Pharmacy Schemas
class PrescriptionCreateSchema(BaseModel):
    patient_id: str
    prescribing_doctor_id: str
    prescribing_doctor_npi: str
    rxnorm_code: str = Field(..., example="313782")
    medication_name: str = Field(..., example="Warfarin 5mg")
    sig_instructions: str = Field(..., example="Take 1 tablet by mouth daily")
    quantity: float = 30.0
    days_supply: int = 30
    refills_allowed: int = 3
    force_override_warnings: bool = False


class PrescriptionResponseSchema(BaseModel):
    id: str
    prescription_number: str
    patient_id: str
    rxnorm_code: str
    medication_name: str
    status: str
    start_date: date
    end_date: Optional[date]

    class Config:
        from_attributes = True


# Laboratory Schemas
class LabOrderCreateSchema(BaseModel):
    patient_id: str
    ordering_doctor_id: str
    loinc_code: str = Field(..., example="2345-7")
    clinical_reason: str = Field(..., example="Evaluate fasting blood sugar levels")
    encounter_id: Optional[str] = None


class LabResultCreateSchema(BaseModel):
    order_id: str
    loinc_code: str
    parameter_name: str
    numerical_value: float
    performing_technician_id: str


class LabResultResponseSchema(BaseModel):
    id: str
    order_id: str
    loinc_code: str
    parameter_name: str
    numerical_value: float
    unit_of_measure: str
    is_abnormal: bool
    is_critical: bool

    class Config:
        from_attributes = True
