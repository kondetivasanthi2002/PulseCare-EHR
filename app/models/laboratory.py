"""
PulseCare Laboratory & Diagnostic Test Models.
Supports LOINC laboratory code catalog, lab order dispatch, observation results, reference ranges, and abnormal value flags.
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Float, Text, Boolean, ForeignKey

from app.core.database import TimeStampedBase


class LabOrderStatus(str, Enum):
    ORDERED = "ORDERED"
    SPECIMEN_COLLECTED = "SPECIMEN_COLLECTED"
    IN_ANALYSIS = "IN_ANALYSIS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class LabOrder(TimeStampedBase):
    """Laboratory Test Order Entity."""
    __tablename__ = "lab_orders"

    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    ordering_doctor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    encounter_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("clinical_encounters.id"), nullable=True)
    
    loinc_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # e.g. '2345-7' (Glucose)
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    clinical_reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default=LabOrderStatus.ORDERED.value, index=True)
    
    ordered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    specimen_collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    results: Mapped[List["LabResult"]] = relationship("LabResult", back_populates="order", cascade="all, delete-orphan")


class LabResult(TimeStampedBase):
    """Laboratory Result Observation Entity."""
    __tablename__ = "lab_results"

    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("lab_orders.id"), nullable=False, index=True)
    loinc_code: Mapped[str] = mapped_column(String(50), nullable=False)
    parameter_name: Mapped[str] = mapped_column(String(255), nullable=False) # e.g. Fasting Blood Sugar
    
    numerical_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    text_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    unit_of_measure: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. mg/dL, mmol/L
    
    reference_range_low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reference_range_high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    is_abnormal: Mapped[bool] = mapped_column(Boolean, default=False)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False) # Triggers urgent notification
    performing_technician_id: Mapped[str] = mapped_column(String(36), nullable=False)
    technician_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    order: Mapped["LabOrder"] = relationship("LabOrder", back_populates="results")
