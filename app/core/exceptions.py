"""
PulseCare Healthcare Specific Exceptions.
Provides standardized error classes for PHI violations, medical conflicts, and security errors.
"""

from typing import Any, Dict, Optional


class HealthcareException(Exception):
    """Base exception for all healthcare application domain errors."""
    
    def __init__(self, message: str, code: str = "HEALTHCARE_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class HIPAAViolationError(HealthcareException):
    """Raised when an illegal operation violates HIPAA privacy or security rules."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="HIPAA_VIOLATION_ERROR", details=details)


class PHICryptographyError(HealthcareException):
    """Raised when encryption or decryption of Protected Health Information fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="PHI_CRYPTO_ERROR", details=details)


class DrugInteractionCollisionError(HealthcareException):
    """Raised when a prescribed medication collides dangerously with patient's existing drugs or allergies."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="DRUG_INTERACTION_COLLISION", details=details)


class InvalidICD10CodeError(HealthcareException):
    """Raised when an invalid or retired ICD-10 diagnosis code is submitted."""
    def __init__(self, code_submitted: str):
        super().__init__(f"Invalid ICD-10 diagnosis code submitted: '{code_submitted}'", code="INVALID_ICD10_CODE", details={"submitted_code": code_submitted})


class InvalidCPTCodeError(HealthcareException):
    """Raised when an invalid CPT procedure code is submitted for billing."""
    def __init__(self, code_submitted: str):
        super().__init__(f"Invalid CPT procedure code submitted: '{code_submitted}'", code="INVALID_CPT_CODE", details={"submitted_code": code_submitted})


class DoubleBookingConflictError(HealthcareException):
    """Raised when an appointment scheduling request conflicts with an existing doctor/patient schedule."""
    def __init__(self, doctor_id: str, slot_time: str):
        super().__init__(
            f"Scheduling conflict: Doctor {doctor_id} already has an appointment scheduled at {slot_time}.",
            code="DOUBLE_BOOKING_CONFLICT",
            details={"doctor_id": doctor_id, "slot_time": slot_time}
        )


class InsufficientInsuranceCoverageError(HealthcareException):
    """Raised when an insurance claim fails verification or lacks active coverage."""
    def __init__(self, policy_number: str, reason: str):
        super().__init__(
            f"Insurance policy '{policy_number}' verification failed: {reason}",
            code="INSURANCE_CLAIM_REJECTED",
            details={"policy_number": policy_number, "reason": reason}
        )


class FHIRValidationError(HealthcareException):
    """Raised when a FHIR JSON resource fails specification schema validation."""
    def __init__(self, resource_type: str, validation_errors: list):
        super().__init__(
            f"FHIR resource '{resource_type}' failed validation with {len(validation_errors)} error(s).",
            code="FHIR_VALIDATION_ERROR",
            details={"resource_type": resource_type, "errors": validation_errors}
        )
