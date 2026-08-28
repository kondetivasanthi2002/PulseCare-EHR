"""
PulseCare Doctor Scheduling & Appointment Models.
Manages physician availability, patient booking slots, conflict checking, and Telehealth virtual room links.
"""

from datetime import datetime, time
from typing import Optional
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Time, Text, Boolean, ForeignKey

from app.core.database import TimeStampedBase


class AppointmentStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"
    CANCELLED = "CANCELLED"


class DoctorScheduleSlot(TimeStampedBase):
    """Doctor Master Availability Slot."""
    __tablename__ = "doctor_schedule_slots"

    doctor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    doctor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), default="General Practice")
    day_of_week: Mapped[int] = mapped_column(String(20), nullable=False) # 0=Monday ... 6=Sunday
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_duration_minutes: Mapped[int] = mapped_column(String(10), default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Appointment(TimeStampedBase):
    """Patient Scheduled Appointment Record."""
    __tablename__ = "appointments"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    doctor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    status: Mapped[str] = mapped_column(String(30), default=AppointmentStatus.CONFIRMED.value, index=True)
    appointment_reason: Mapped[str] = mapped_column(Text, nullable=False)
    is_telehealth: Mapped[bool] = mapped_column(Boolean, default=False)
    telehealth_room_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
