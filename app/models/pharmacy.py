"""
PulseCare Pharmacy & e-Prescribing Data Models.
Manages pharmaceutical formulary, RxNorm codes, active patient prescriptions, dosage instructions, and refill tracking.
"""

from datetime import datetime, date
from typing import Optional
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Date, Float, Text, Boolean, ForeignKey

from app.core.database import TimeStampedBase


class PrescriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    DISCONTINUED = "DISCONTINUED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class Medication(TimeStampedBase):
    """Pharmaceutical Drug Formulary Entry."""
    __tablename__ = "medications"

    rxnorm_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # RxNorm CUI
    brand_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    generic_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    dosage_form: Mapped[str] = mapped_column(String(100), nullable=False) # Tablet, Capsule, Solution, Injection
    strength: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. 500mg, 10mg/mL
    controlled_substance_class: Mapped[Optional[str]] = mapped_column(String(10), nullable=True) # Schedule II, III, IV, V
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Prescription(TimeStampedBase):
    """Patient e-Prescription Entity."""
    __tablename__ = "prescriptions"

    prescription_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    prescribing_doctor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    prescribing_doctor_npi: Mapped[str] = mapped_column(String(20), nullable=False)
    encounter_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("clinical_encounters.id"), nullable=True)
    
    rxnorm_code: Mapped[str] = mapped_column(String(50), nullable=False)
    medication_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sig_instructions: Mapped[str] = mapped_column(Text, nullable=False) # e.g., "Take 1 tablet by mouth twice daily with meals"
    quantity: Mapped[int] = mapped_column(Float, nullable=False)
    days_supply: Mapped[int] = mapped_column(Float, nullable=False)
    refills_allowed: Mapped[int] = mapped_column(Float, default=0)
    refills_remaining: Mapped[int] = mapped_column(Float, default=0)
    
    start_date: Mapped[date] = mapped_column(Date, default=date.today)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default=PrescriptionStatus.ACTIVE.value, index=True)
    pharmacy_npi: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
