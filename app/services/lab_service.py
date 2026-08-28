"""
PulseCare Laboratory Order & LOINC Observation Service.
Processes diagnostic lab orders, checks LOINC reference ranges, and flags critical value alerts.
"""

import uuid
import random
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.laboratory import LabOrder, LabResult, LabOrderStatus
from app.services.dictionaries import LOINC_CATALOG
from app.core.exceptions import HealthcareException
from app.core.audit import audit_logger, AuditActionType


class LaboratoryService:
    """Service handling diagnostic laboratory workflows."""

    @staticmethod
    def generate_order_number() -> str:
        return f"LAB-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    async def create_lab_order(
        self,
        db: AsyncSession,
        patient_id: str,
        ordering_doctor_id: str,
        loinc_code: str,
        clinical_reason: str,
        encounter_id: Optional[str] = None
    ) -> LabOrder:
        """Dispatches a new diagnostic laboratory order."""
        meta = LOINC_CATALOG.get(loinc_code, {"name": f"LOINC Test {loinc_code}"})
        order_num = self.generate_order_number()

        order = LabOrder(
            id=str(uuid.uuid4()),
            order_number=order_num,
            patient_id=patient_id,
            ordering_doctor_id=ordering_doctor_id,
            encounter_id=encounter_id,
            loinc_code=loinc_code,
            test_name=meta["name"],
            clinical_reason=clinical_reason,
            status=LabOrderStatus.ORDERED.value,
            ordered_at=datetime.now(timezone.utc)
        )
        db.add(order)
        return order

    async def record_lab_result(
        self,
        db: AsyncSession,
        order_id: str,
        loinc_code: str,
        parameter_name: str,
        numerical_value: float,
        performing_technician_id: str,
        actor_id: str,
        actor_role: str
    ) -> LabResult:
        """Records lab observation results, automatically evaluating abnormal & critical ranges."""
        res_ord = await db.execute(select(LabOrder).where(LabOrder.id == order_id))
        order = res_ord.scalars().first()
        if not order:
            raise HealthcareException("Lab order not found")

        meta = LOINC_CATALOG.get(loinc_code, {})
        unit = meta.get("unit", "mg/dL")
        ref_low = meta.get("ref_low")
        ref_high = meta.get("ref_high")
        crit_low = meta.get("critical_low")
        crit_high = meta.get("critical_high")

        is_abnormal = False
        is_critical = False

        if ref_low is not None and numerical_value < ref_low:
            is_abnormal = True
        if ref_high is not None and numerical_value > ref_high:
            is_abnormal = True

        if crit_low is not None and numerical_value <= crit_low:
            is_critical = True
            is_abnormal = True
        if crit_high is not None and numerical_value >= crit_high:
            is_critical = True
            is_abnormal = True

        result = LabResult(
            id=str(uuid.uuid4()),
            order_id=order.id,
            loinc_code=loinc_code,
            parameter_name=parameter_name,
            numerical_value=numerical_value,
            unit_of_measure=unit,
            reference_range_low=ref_low,
            reference_range_high=ref_high,
            is_abnormal=is_abnormal,
            is_critical=is_critical,
            performing_technician_id=performing_technician_id
        )
        db.add(result)

        order.status = LabOrderStatus.COMPLETED.value
        order.completed_at = datetime.now(timezone.utc)

        # Audit verification
        audit_entry = audit_logger.create_log_entry(
            action_type=AuditActionType.LAB_RESULT_VERIFICATION,
            user_id=actor_id,
            user_role=actor_role,
            resource_type="LabResult",
            patient_id=order.patient_id,
            resource_id=result.id,
            details={"is_critical": is_critical, "is_abnormal": is_abnormal, "value": numerical_value}
        )
        db.add(audit_entry)

        return result


lab_service = LaboratoryService()
