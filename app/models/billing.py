"""
PulseCare Billing, Invoicing & Insurance Claims Processing Models.
Handles medical coding billing, claim submissions, copay tracking, patient ledger, and payment processing.
"""

import uuid
from datetime import datetime, date
from typing import List, Optional
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Date, Float, Text, Boolean, ForeignKey, JSON

from app.core.database import TimeStampedBase


class ClaimStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    DENIED = "DENIED"
    APPEALED = "APPEALED"


class PaymentStatus(str, Enum):
    UNPAID = "UNPAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID_IN_FULL = "PAID_IN_FULL"
    REFUNDED = "REFUNDED"


class PatientInvoice(TimeStampedBase):
    """Patient Medical Invoice Entity."""
    __tablename__ = "patient_invoices"

    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("clinical_encounters.id"), nullable=True)
    
    issue_date: Mapped[date] = mapped_column(Date, default=date.today)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    subtotal_amount: Mapped[float] = mapped_column(Float, default=0.0)
    insurance_covered_amount: Mapped[float] = mapped_column(Float, default=0.0)
    patient_copay_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount_due: Mapped[float] = mapped_column(Float, default=0.0)
    amount_paid: Mapped[float] = mapped_column(Float, default=0.0)
    
    payment_status: Mapped[str] = mapped_column(String(30), default=PaymentStatus.UNPAID.value)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[List["InvoiceLineItem"]] = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    claims: Mapped[List["InsuranceClaim"]] = relationship("InsuranceClaim", back_populates="invoice")


class InvoiceLineItem(TimeStampedBase):
    """Individual Billable Line Item on a Patient Invoice."""
    __tablename__ = "invoice_line_items"

    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("patient_invoices.id"), nullable=False, index=True)
    cpt_code: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Float, default=1)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    invoice: Mapped["PatientInvoice"] = relationship("PatientInvoice", back_populates="items")


class InsuranceClaim(TimeStampedBase):
    """Insurance Claim Submission Record (EDI 837P / CMS-1500)."""
    __tablename__ = "insurance_claims"

    claim_control_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("patient_invoices.id"), nullable=False, index=True)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    policy_number: Mapped[str] = mapped_column(String(100), nullable=False)
    payer_id: Mapped[str] = mapped_column(String(50), nullable=False)
    
    submitted_amount: Mapped[float] = mapped_column(Float, nullable=False)
    allowed_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    paid_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    status: Mapped[str] = mapped_column(String(30), default=ClaimStatus.SUBMITTED.value, index=True)
    submission_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    adjudication_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    denial_reason_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    claim_payload_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    invoice: Mapped["PatientInvoice"] = relationship("PatientInvoice", back_populates="claims")
