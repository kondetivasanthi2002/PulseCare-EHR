"""
PulseCare Clinical Encounter & Medical Record Models.
Supports Subjective-Objective-Assessment-Plan (SOAP) clinical documentation,
ICD-10-CM diagnosis coding, and CPT procedure code tracking.
"""

from datetime import datetime, timezone
from typing import List, Optional
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Text, Float, Boolean, ForeignKey, JSON

from app.core.database import TimeStampedBase


class EncounterType(str, Enum):
    WELLNESS_EXAM = "WELLNESS_EXAM"
    URGENT_CARE = "URGENT_CARE"
    EMERGENCY = "EMERGENCY"
    FOLLOW_UP = "FOLLOW_UP"
    TELEHEALTH = "TELEHEALTH"
    CONSULTATION = "CONSULTATION"


class EncounterStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SIGNED_OFF = "SIGNED_OFF"
    CANCELLED = "CANCELLED"


class ClinicalEncounter(TimeStampedBase):
    """Clinical Encounter Record (Patient Doctor Visit Document)."""
    __tablename__ = "clinical_encounters"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    attending_physician_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    encounter_type: Mapped[str] = mapped_column(String(50), default=EncounterType.CONSULTATION.value)
    status: Mapped[str] = mapped_column(String(30), default=EncounterStatus.SCHEDULED.value)
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    chief_complaint: Mapped[str] = mapped_column(Text, nullable=False)
    
    # SOAP Note Sections
    subjective_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Patient symptoms & history
    objective_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # Physical exam & vitals findings
    assessment_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Physician diagnosis evaluation
    plan_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)        # Treatment plan & prescriptions
    
    is_signed: Mapped[bool] = mapped_column(Boolean, default=False)
    signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    signed_by_npi: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relationships
    diagnoses: Mapped[List["EncounterDiagnosis"]] = relationship("EncounterDiagnosis", back_populates="encounter", cascade="all, delete-orphan")
    procedures: Mapped[List["EncounterProcedure"]] = relationship("EncounterProcedure", back_populates="encounter", cascade="all, delete-orphan")


class EncounterDiagnosis(TimeStampedBase):
    """ICD-10-CM Diagnosis Code associated with a Clinical Encounter."""
    __tablename__ = "encounter_diagnoses"

    encounter_id: Mapped[str] = mapped_column(String(36), ForeignKey("clinical_encounters.id"), nullable=False, index=True)
    icd10_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True) # e.g., 'E11.9' (Type 2 Diabetes)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    severity: Mapped[str] = mapped_column(String(30), default="Moderate")

    encounter: Mapped["ClinicalEncounter"] = relationship("ClinicalEncounter", back_populates="diagnoses")


class EncounterProcedure(TimeStampedBase):
    """CPT Procedure Code associated with a Clinical Encounter."""
    __tablename__ = "encounter_procedures"

    encounter_id: Mapped[str] = mapped_column(String(36), ForeignKey("clinical_encounters.id"), nullable=False, index=True)
    cpt_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True) # e.g., '99214' (Office visit level 4)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    units_performed: Mapped[int] = mapped_column(Float, default=1)
    performed_by_id: Mapped[str] = mapped_column(String(36), nullable=False)

    encounter: Mapped["ClinicalEncounter"] = relationship("ClinicalEncounter", back_populates="procedures")
