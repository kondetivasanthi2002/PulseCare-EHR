# PulseCare EHR & Enterprise Healthcare Management System

PulseCare is an enterprise-grade Electronic Health Records (EHR), Practice Management, and Telehealth Platform compliant with HIPAA regulations, FHIR R4 interoperability standards, and HL7 messaging protocols.

## System Architecture

PulseCare is built using a modular domain-driven architecture:

- **Core & Security**: JWT Authentication, Role-Based Access Control (RBAC), AES-256 GCM encryption for PHI (Protected Health Information), and immutable HIPAA Audit Logging.
- **Patient Management**: Full demographics, vitals tracking, allergies, immunization records, emergency contacts, and medical history.
- **Clinical Encounters**: Subjective-Objective-Assessment-Plan (SOAP) clinical note workflow, ICD-10-CM diagnosis mapping, and CPT procedure coding.
- **Appointment Scheduling**: Doctor availability management, patient portal booking, double-booking prevention, and Telehealth integration.
- **Billing & Claims**: Automated CPT-based invoicing, ICD-10 cross-validation, insurance copay calculation, and electronic claim generation (CMS-1500 / 837P).
- **Pharmacy & e-Prescribing**: Drug interaction checks, dosage validation, electronic prescription dispatch (RxNorm mapping), and refill management.
- **Laboratory & Diagnostics**: LOINC laboratory test panel management, HL7 v2/FHIR observation parsing, reference range monitoring, and critical result alerts.
- **Interoperability (FHIR & HL7)**: FHIR R4 JSON resource serialization (`Patient`, `Encounter`, `Observation`, `Condition`, `DiagnosticReport`) and HL7 v2 message parsing (`ADT^A08`, `ORM^O01`, `ORU^R01`).
- **Analytics & Reporting**: Real-time operational metrics, bed occupancy, clinical outcome tracking, and billing revenue cycle performance graphs.

## Getting Started

### Prerequisites
- Python 3.9+
- Pip & Virtualenv

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/health-care-app.git
cd health-care-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
pytest tests/ -v --tb=short
```

### Starting Application

```bash
uvicorn app.main:app --reload --port 8000
```

## Compliance & Security

PulseCare adheres to HIPAA Security Rule guidelines:
1. **Access Control**: Unique user identification, emergency access procedures, automatic logoff.
2. **Audit Controls**: Immutable record of every PHI access, modification, or deletion.
3. **Data Integrity**: Cryptographic hashing of patient audit trails.
4. **Transmission Security**: TLS 1.3 enforced for network traffic, AES-256-GCM for storage encryption.

## License

Proprietary - All Rights Reserved. Confidential software. Not licensed under any open source license.
