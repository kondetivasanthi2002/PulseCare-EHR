"""
PulseCare FHIR R4 Interoperability Mapper.
Converts PulseCare internal database entities to HL7 FHIR R4 compliant JSON resources.
Compliant with US Core Implementation Guide (USCDI).
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, date

from app.models.patient import Patient, PatientVitals
from app.models.encounter import ClinicalEncounter, EncounterDiagnosis
from app.models.laboratory import LabOrder, LabResult


class FHIRResourceMapper:
    """Serializes domain models into standard FHIR R4 JSON schemas."""

    @staticmethod
    def patient_to_fhir(patient: Patient) -> Dict[str, Any]:
        """Converts Patient entity to FHIR R4 Patient resource."""
        return {
            "resourceType": "Patient",
            "id": str(patient.id),
            "meta": {
                "versionId": "1",
                "lastUpdated": patient.updated_at.isoformat() if patient.updated_at else datetime.utcnow().isoformat()
            },
            "identifier": [
                {
                    "use": "official",
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "MR",
                                "display": "Medical Record Number"
                            }
                        ]
                    },
                    "system": "urn:oid:2.16.840.1.113883.4.1",
                    "value": patient.mrn
                }
            ],
            "active": patient.is_active,
            "name": [
                {
                    "use": "official",
                    "family": patient.last_name,
                    "given": [patient.first_name]
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": patient.phone,
                    "use": "home"
                },
                {
                    "system": "email",
                    "value": patient.email,
                    "use": "home"
                }
            ],
            "gender": patient.gender.lower() if patient.gender else "unknown",
            "birthDate": patient.date_of_birth.isoformat() if isinstance(patient.date_of_birth, date) else patient.date_of_birth,
            "address": [
                {
                    "use": "home",
                    "line": [patient.address_line1] + ([patient.address_line2] if patient.address_line2 else []),
                    "city": patient.city,
                    "state": patient.state,
                    "postalCode": patient.postal_code,
                    "country": "USA"
                }
            ],
            "communication": [
                {
                    "language": {
                        "coding": [
                            {
                                "system": "urn:ietf:bcp:47",
                                "code": "en",
                                "display": patient.primary_language
                            }
                        ]
                    },
                    "preferred": True
                }
            ]
        }

    @staticmethod
    def vitals_to_fhir_observation(vitals: PatientVitals) -> Dict[str, Any]:
        """Converts Vitals entity to FHIR R4 Observation resource (Vital Signs)."""
        return {
            "resourceType": "Observation",
            "id": str(vitals.id),
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "85354-9",
                        "display": "Blood pressure panel with device"
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{vitals.patient_id}"
            },
            "effectiveDateTime": vitals.recorded_at.isoformat() if vitals.recorded_at else datetime.utcnow().isoformat(),
            "component": [
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": vitals.systolic_bp,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                },
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": vitals.diastolic_bp,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                },
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8867-4",
                                "display": "Heart rate"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": vitals.heart_rate,
                        "unit": "beats/min",
                        "system": "http://unitsofmeasure.org",
                        "code": "/min"
                    }
                }
            ]
        }

    @staticmethod
    def encounter_to_fhir(encounter: ClinicalEncounter) -> Dict[str, Any]:
        """Converts ClinicalEncounter entity to FHIR R4 Encounter resource."""
        return {
            "resourceType": "Encounter",
            "id": str(encounter.id),
            "status": encounter.status.lower(),
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory"
            },
            "type": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "408443003",
                            "display": encounter.encounter_type
                        }
                    ]
                }
            ],
            "subject": {
                "reference": f"Patient/{encounter.patient_id}"
            },
            "participant": [
                {
                    "individual": {
                        "reference": f"Practitioner/{encounter.attending_physician_id}"
                    }
                }
            ],
            "period": {
                "start": encounter.start_time.isoformat() if encounter.start_time else None,
                "end": encounter.end_time.isoformat() if encounter.end_time else None
            },
            "reasonCode": [
                {
                    "text": encounter.chief_complaint
                }
            ]
        }


fhir_mapper = FHIRResourceMapper()
