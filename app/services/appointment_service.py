"""
PulseCare Appointment & Telehealth Scheduling Engine.
Prevents double-booking conflicts, allocates doctor time slots, and generates secure virtual room links.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.appointment import Appointment, AppointmentStatus
from app.core.exceptions import DoubleBookingConflictError, HealthcareException


class AppointmentService:
    """Service managing physician appointment bookings and telehealth sessions."""

    async def schedule_appointment(
        self,
        db: AsyncSession,
        patient_id: str,
        doctor_id: str,
        doctor_name: str,
        start_time: datetime,
        duration_minutes: int,
        appointment_reason: str,
        is_telehealth: bool = False
    ) -> Appointment:
        """Schedules a patient appointment, enforcing strict double-booking prevention."""
        end_time = start_time + timedelta(minutes=duration_minutes)

        # Check for scheduling collisions (overlapping doctor times)
        query = select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.status.in_([AppointmentStatus.CONFIRMED.value, AppointmentStatus.CHECKED_IN.value, AppointmentStatus.IN_PROGRESS.value]),
                or_(
                    and_(Appointment.start_time <= start_time, Appointment.end_time > start_time),
                    and_(Appointment.start_time < end_time, Appointment.end_time >= end_time),
                    and_(Appointment.start_time >= start_time, Appointment.end_time <= end_time)
                )
            )
        )
        result = await db.execute(query)
        conflicts = result.scalars().all()

        if conflicts:
            raise DoubleBookingConflictError(doctor_id=doctor_id, slot_time=start_time.isoformat())

        telehealth_url = None
        if is_telehealth:
            room_id = str(uuid.uuid4())[:12]
            telehealth_url = f"https://telehealth.pulsecare.health/room/{room_id}"

        appointment = Appointment(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            start_time=start_time,
            end_time=end_time,
            appointment_reason=appointment_reason,
            is_telehealth=is_telehealth,
            telehealth_room_url=telehealth_url,
            status=AppointmentStatus.CONFIRMED.value
        )
        db.add(appointment)
        return appointment

    async def check_in_patient(self, db: AsyncSession, appointment_id: str) -> Appointment:
        """Updates appointment status to CHECKED_IN when patient arrives."""
        result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
        appointment = result.scalars().first()
        if not appointment:
            raise HealthcareException("Appointment not found", code="APPOINTMENT_NOT_FOUND")

        appointment.status = AppointmentStatus.CHECKED_IN.value
        return appointment


appointment_service = AppointmentService()
