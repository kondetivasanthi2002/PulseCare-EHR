"""
PulseCare Synthetic Healthcare Data Generator & Database Seeder.
Populates the database with realistic patient records, clinical encounters, billing claims, prescriptions, and lab results.
"""

import asyncio
import random
from datetime import date, datetime, timedelta
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.patient import Patient, PatientVitals, PatientAllergy, InsurancePolicy, Gender, BloodType
from app.models.encounter import ClinicalEncounter, EncounterDiagnosis, EncounterProcedure, EncounterType, EncounterStatus
from app.models.appointment import Appointment, AppointmentStatus
from app.models.billing import PatientInvoice, InvoiceLineItem, InsuranceClaim, ClaimStatus, PaymentStatus
from app.models.pharmacy import Prescription, PrescriptionStatus
from app.models.laboratory import LabOrder, LabResult, LabOrderStatus
from app.core.crypto import phi_crypto

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
CHIEF_COMPLAINTS = [
    "Routine annual wellness examination",
    "Persistent dry cough and low-grade fever for 3 days",
    "Acute lower back pain after heavy lifting",
    "Fasting blood glucose monitoring and diabetes check",
    "Hypertension follow-up and medication review",
    "Severe throbbing headache with photophobia",
    "Shortness of breath during moderate exercise",
    "Abdominal pain in lower right quadrant",
    "Right knee joint stiffness and swelling",
    "Skin rash and localized itching on forearm"
]


async def seed_healthcare_database(num_patients: int = 50):
    """Generates synthetic patient records, clinical encounters, and financial ledgers."""
    print(f"Initializing database schema and seeding {num_patients} patient records...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        for i in range(num_patients):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            dob = date(random.randint(1950, 2005), random.randint(1, 12), random.randint(1, 28))
            mrn = f"MRN-{random.randint(1000000, 9999999)}"

            patient = Patient(
                mrn=mrn,
                first_name=fn,
                last_name=ln,
                date_of_birth=dob,
                gender=random.choice([Gender.MALE.value, Gender.FEMALE.value]),
                blood_type=random.choice([BloodType.A_POSITIVE.value, BloodType.O_POSITIVE.value, BloodType.B_POSITIVE.value]),
                email=f"{fn.lower()}.{ln.lower()}{i}@example.com",
                phone=f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                address_line1=f"{random.randint(100, 999)} Medical Center Blvd",
                city=random.choice(CITIES),
                state="NY",
                postal_code="10001",
                ssn_encrypted=phi_crypto.encrypt_str(f"999-{random.randint(10,99)}-{random.randint(1000,9999)}"),
                is_active=True
            )
            session.add(patient)
            await session.flush()

            # Vitals
            vitals = PatientVitals(
                patient_id=patient.id,
                recorded_by_id="nurse_seed",
                systolic_bp=float(random.randint(110, 145)),
                diastolic_bp=float(random.randint(70, 95)),
                heart_rate=float(random.randint(60, 90)),
                respiratory_rate=16.0,
                body_temperature=36.8,
                oxygen_saturation=98.5,
                height_cm=float(random.randint(155, 190)),
                weight_kg=float(random.randint(55, 95)),
                bmi=24.5
            )
            session.add(vitals)

            # Encounter
            encounter = ClinicalEncounter(
                patient_id=patient.id,
                attending_physician_id="doc_seed_1",
                encounter_type=EncounterType.CONSULTATION.value,
                status=EncounterStatus.SIGNED_OFF.value,
                chief_complaint=random.choice(CHIEF_COMPLAINTS),
                subjective_notes="Patient reports symptoms ongoing for several days.",
                objective_notes="Vitals within normal limits. Cardiopulmonary exam clear.",
                assessment_notes="Controlled hypertension and mild seasonal allergies.",
                plan_notes="Continue current regimen. Recheck in 6 months.",
                is_signed=True,
                signed_by_npi="1928374650",
                start_time=datetime.utcnow() - timedelta(days=random.randint(1, 60))
            )
            session.add(encounter)

        await session.commit()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_healthcare_database())
