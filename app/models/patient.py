"""
PulseCare Patient Demographics & Health Profile Database Models.
Stores PHI patient records, contact details, emergency contacts, insurance policies, and baseline health indicators.
"""

import uuid
from datetime import date, datetime
from typing import List, Optional
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, DateTime, Text, Float, Boolean, ForeignKey, JSON

from app.core.database import TimeStampedBase
from app.core.crypto import phi_crypto


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "UNKNOWN"


class Patient(TimeStampedBase):
    """Patient Master Record Entity."""
    __tablename__ = "patients"

    mrn: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)  # Medical Record Number
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), default=Gender.UNKNOWN.value)
    ssn_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Encrypted SSN
    blood_type: Mapped[str] = mapped_column(String(10), default=BloodType.UNKNOWN.value)
    
    # Contact & Location Info
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Insurance & Primary Care Provider
    primary_language: Mapped[str] = mapped_column(String(50), default="English")
    primary_physician_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    vitals_history: Mapped[List["PatientVitals"]] = relationship("PatientVitals", back_populates="patient", cascade="all, delete-orphan")
    allergies: Mapped[List["PatientAllergy"]] = relationship("PatientAllergy", back_populates="patient", cascade="all, delete-orphan")
    insurance_policies: Mapped[List["InsurancePolicy"]] = relationship("InsurancePolicy", back_populates="patient", cascade="all, delete-orphan")

    def get_ssn(self) -> Optional[str]:
        """Decrypts and returns patient SSN if present."""
        if not self.ssn_encrypted:
            return None
        return phi_crypto.decrypt_str(self.ssn_encrypted)

    def set_ssn(self, ssn_plain: str) -> None:
        """Encrypts and sets patient SSN."""
        self.ssn_encrypted = phi_crypto.encrypt_str(ssn_plain)

    @property
    def full_name(self) -> str:
        """Returns patient's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self) -> int:
        """Calculates current patient age in years."""
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class PatientVitals(TimeStampedBase):
    """Patient Vital Signs Record."""
    __tablename__ = "patient_vitals"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    recorded_by_id: Mapped[str] = mapped_column(String(36), nullable=False)
    
    systolic_bp: Mapped[int] = mapped_column(Float, nullable=False)  # mmHg
    diastolic_bp: Mapped[int] = mapped_column(Float, nullable=False) # mmHg
    heart_rate: Mapped[int] = mapped_column(Float, nullable=False)   # bpm
    respiratory_rate: Mapped[int] = mapped_column(Float, nullable=False) # breaths/min
    body_temperature: Mapped[float] = mapped_column(Float, nullable=False) # °C
    oxygen_saturation: Mapped[float] = mapped_column(Float, nullable=False) # SpO2 %
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    bmi: Mapped[float] = mapped_column(Float, nullable=False)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="vitals_history")


class PatientAllergy(TimeStampedBase):
    """Patient Known Allergies Entity."""
    __tablename__ = "patient_allergies"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    allergen_name: Mapped[str] = mapped_column(String(255), nullable=False) # e.g. Penicillin, Peanuts
    allergy_type: Mapped[str] = mapped_column(String(50), default="Drug") # Drug, Food, Environmental
    severity: Mapped[str] = mapped_column(String(30), default="Moderate") # Mild, Moderate, Severe, Anaphylactic
    reaction_description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="allergies")


class InsurancePolicy(TimeStampedBase):
    """Patient Insurance Policy Record."""
    __tablename__ = "insurance_policies"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    payer_name: Mapped[str] = mapped_column(String(255), nullable=False) # e.g. Blue Cross Blue Shield
    payer_id: Mapped[str] = mapped_column(String(50), nullable=False)
    policy_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    group_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subscriber_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship_to_subscriber: Mapped[str] = mapped_column(String(50), default="Self")
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    copay_amount: Mapped[float] = mapped_column(Float, default=20.00)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="insurance_policies")
