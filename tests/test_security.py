"""
Test Suite 1: Core Security, Cryptography, and HIPAA Audit Controls.
"""

import pytest
from app.core.security import security_engine, UserRole
from app.core.crypto import phi_crypto
from app.core.audit import audit_logger, AuditActionType


def test_password_hashing_and_verification():
    """Test 1.1: Password bcrypt hashing and verification."""
    raw_password = "SecureDoctorPassword#2026"
    hashed = security_engine.get_password_hash(raw_password)
    
    assert hashed != raw_password
    assert security_engine.verify_password(raw_password, hashed) is True
    assert security_engine.verify_password("WrongPassword", hashed) is False


def test_jwt_token_generation_and_decoding():
    """Test 1.2: Signed JWT token encoding and role claims decoding."""
    user_data = {
        "user_id": "usr_doc_99",
        "username": "dr_smith",
        "email": "smith@pulsecare.health",
        "role": UserRole.DOCTOR.value,
        "npi": "1928374650"
    }
    
    token = security_engine.create_access_token(user_data)
    decoded = security_engine.decode_token(token)
    
    assert decoded.user_id == "usr_doc_99"
    assert decoded.role == UserRole.DOCTOR
    assert decoded.npi == "1928374650"


def test_phi_aes_gcm_encryption_and_decryption():
    """Test 1.3: AES-256-GCM PHI encryption and decryption engine."""
    phi_ssn = "999-12-3456"
    encrypted_b64 = phi_crypto.encrypt_str(phi_ssn)
    
    assert encrypted_b64 != phi_ssn
    decrypted = phi_crypto.decrypt_str(encrypted_b64)
    assert decrypted == phi_ssn


def test_hipaa_audit_log_integrity_hash():
    """Test 1.4: Immutable HIPAA audit log SHA-256 HMAC integrity calculation."""
    entry = audit_logger.create_log_entry(
        action_type=AuditActionType.PHI_READ,
        user_id="usr_doc_1",
        user_role="DOCTOR",
        resource_type="Patient",
        patient_id="pat_100",
        resource_id="pat_100"
    )
    
    assert entry.integrity_hash is not None
    assert len(entry.integrity_hash) == 64  # SHA-256 hex length
    assert entry.compute_integrity_hash() == entry.integrity_hash
