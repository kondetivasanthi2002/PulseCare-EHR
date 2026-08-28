# PulseCare EHR Architecture & Technical Specification

## System Overview

PulseCare is an enterprise-level Electronic Health Record (EHR) and Practice Management Platform designed for outpatient clinics, hospital departments, and integrated healthcare networks.

```
                  +-----------------------------------+
                  |   React Dashboard & Portal UI     |
                  +-----------------+-----------------+
                                    | REST / WebSockets
                                    v
                  +-----------------+-----------------+
                  |      FastAPI Gateway Layer        |
                  +-----------------+-----------------+
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
          v                         v                         v
+------------------+      +------------------+      +------------------+
| Security & Auth  |      | Clinical Engine  |      | Billing & Claims |
| (JWT / AES-256)  |      | (SOAP/ICD10/CPT) |      | (EDI 837P)       |
+--------+---------+      +--------+---------+      +--------+---------+
         |                         |                         |
         v                         v                         v
+------------------+      +------------------+      +------------------+
|  HIPAA Audit Log |      | Pharmacy Engine  |      |  LOINC Lab Engine|
| (SHA-256 HMAC)   |      | (RxNorm Safety)  |      | (HL7 / FHIR R4)  |
+--------+---------+      +--------+---------+      +--------+---------+
         |                         |                         |
         +-------------------------+-------------------------+
                                   |
                                   v
                  +-----------------------------------+
                  |  Async SQLAlchemy Database Engine |
                  +-----------------------------------+
```

## Security & Compliance Control Matrix

| HIPAA Security Rule Standard | Implementation Mechanism |
| :--- | :--- |
| **Access Control (45 CFR § 164.312(a))** | Passlib/bcrypt password hashing, Role-Based Access Control (RBAC), automatic token expiration (30 mins). |
| **Audit Controls (45 CFR § 164.312(b))** | Immutable `HIPAAAuditLog` tracking all PHI accesses, creations, modifications, and exports. Cryptographic SHA-256 HMAC integrity signatures. |
| **Integrity (45 CFR § 164.312(c))** | AES-256-GCM authenticated encryption for sensitive fields (SSN, insurance identifiers) at rest. |
| **Transmission Security (45 CFR § 164.312(e))** | TLS 1.3 enforced for REST endpoints and FHIR APIs. |

## Interoperability Standards

### 1. HL7 FHIR R4
Serializes `Patient`, `Observation`, `Encounter`, and `Condition` entities into FHIR R4 JSON resources compatible with USCDI (US Core Data for Interoperability).

### 2. HL7 v2.5 Messaging Protocol
Supports pipe-delimited message generation and parsing for:
- `ADT^A08`: Patient Demographics Update
- `ORM^O01`: Laboratory Test Request Dispatch
- `ORU^R01`: Laboratory Observation Result Unsolicited
