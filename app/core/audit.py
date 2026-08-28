"""
PulseCare HIPAA Audit Control Module.
Provides immutable access logging for Protected Health Information (PHI) access, modifications, and exports.
Required by HIPAA Security Rule (45 CFR § 164.312(b)).
"""

import uuid
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, JSON

from app.core.database import Base
from app.core.config import settings


class AuditActionType(str, Enum):
    """Types of Auditable Actions on PHI and System Resources."""
    PHI_READ = "PHI_READ"
    PHI_CREATE = "PHI_CREATE"
    PHI_UPDATE = "PHI_UPDATE"
    PHI_DELETE = "PHI_DELETE"
    PHI_EXPORT = "PHI_EXPORT"
    USER_LOGIN_SUCCESS = "USER_LOGIN_SUCCESS"
    USER_LOGIN_FAILED = "USER_LOGIN_FAILED"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    PRESCRIPTION_DISPATCH = "PRESCRIPTION_DISPATCH"
    LAB_RESULT_VERIFICATION = "LAB_RESULT_VERIFICATION"
    CLAIM_SUBMISSION = "CLAIM_SUBMISSION"


class HIPAAAuditLog(Base):
    """Database Model for Immutable Audit Trail Entries."""
    __tablename__ = "hipaa_audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    user_role: Mapped[str] = mapped_column(String(30), nullable=False)
    patient_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), default="127.0.0.1")
    user_agent: Mapped[str] = mapped_column(String(255), default="System Engine")
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    integrity_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    def compute_integrity_hash(self) -> str:
        """Calculates SHA-256 HMAC integrity hash to make the audit log immutable and tamper-evident."""
        ts_str = self.timestamp.isoformat() if self.timestamp else ""
        raw_data = f"{self.id}|{ts_str}|{self.action_type}|{self.user_id}|{self.patient_id}|{self.resource_type}|{self.resource_id}|{settings.SECRET_KEY}"
        return hashlib.sha256(raw_data.encode('utf-8')).hexdigest()


class AuditLogger:
    """Service to create audit log records across the application."""

    @staticmethod
    def create_log_entry(
        action_type: AuditActionType,
        user_id: str,
        user_role: str,
        resource_type: str,
        patient_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: str = "127.0.0.1",
        user_agent: str = "PulseCare Core Engine",
        details: Optional[Dict[str, Any]] = None
    ) -> HIPAAAuditLog:
        """Instantiates an audited record with computed cryptographic integrity hash."""
        now = datetime.now(timezone.utc)
        entry = HIPAAAuditLog(
            id=str(uuid.uuid4()),
            timestamp=now,
            action_type=action_type.value,
            user_id=user_id,
            user_role=user_role,
            patient_id=patient_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
        entry.integrity_hash = entry.compute_integrity_hash()
        return entry


audit_logger = AuditLogger()
