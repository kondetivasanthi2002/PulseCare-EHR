"""
PulseCare PHI Cryptography Module.
Provides field-level AES-256-GCM encryption for Sensitive Protected Health Information (PHI).
Compliant with HIPAA Security Rule Technical Safeguards (45 CFR § 164.312(e)(2)(ii)).
"""

import os
import base64
import json
from typing import Any, Union
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings
from app.core.exceptions import PHICryptographyError


class PHICryptoEngine:
    """AES-256-GCM Cryptographic Engine for PHI encryption at rest and in transit."""
    
    def __init__(self, key_b64: Optional[str] = None):
        key_str = key_b64 or settings.PHI_ENCRYPTION_KEY
        try:
            # Ensure key is 32 bytes (256 bits)
            raw_key = base64.b64decode(key_str)
            if len(raw_key) < 32:
                # Pad to 32 bytes if short
                raw_key = raw_key.ljust(32, b'\0')[:32]
            elif len(raw_key) > 32:
                raw_key = raw_key[:32]
            self.key = raw_key
            self.cipher = AESGCM(self.key)
        except Exception as e:
            raise PHICryptographyError(f"Failed to initialize AESGCM cipher engine: {str(e)}")

    def encrypt_str(self, plaintext: str) -> str:
        """Encrypts a plaintext string into a base64 encoded ciphertext string containing nonces."""
        if not plaintext:
            return ""
        try:
            nonce = os.urandom(12)  # 96-bit recommended nonce for AES-GCM
            ciphertext = self.cipher.encrypt(nonce, plaintext.encode('utf-8'), None)
            combined = nonce + ciphertext
            return base64.b64encode(combined).decode('utf-8')
        except Exception as e:
            raise PHICryptographyError(f"Encryption failed for PHI field: {str(e)}")

    def decrypt_str(self, ciphertext_b64: str) -> str:
        """Decrypts a base64 encoded ciphertext string back into original plaintext."""
        if not ciphertext_b64:
            return ""
        try:
            combined = base64.b64decode(ciphertext_b64.encode('utf-8'))
            if len(combined) < 13:
                raise ValueError("Invalid ciphertext length")
            nonce = combined[:12]
            ciphertext = combined[12:]
            plaintext_bytes = self.cipher.decrypt(nonce, ciphertext, None)
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise PHICryptographyError(f"Decryption failed for PHI field: {str(e)}")

    def encrypt_json(self, data: Any) -> str:
        """Encrypts any Python dictionary or list structure into encrypted JSON format."""
        json_bytes = json.dumps(data).encode('utf-8')
        return self.encrypt_str(json_bytes.decode('utf-8'))

    def decrypt_json(self, ciphertext_b64: str) -> Any:
        """Decrypts ciphertext back into original Python dictionary or list structure."""
        plaintext = self.decrypt_str(ciphertext_b64)
        return json.loads(plaintext) if plaintext else None


phi_crypto = PHICryptoEngine()
