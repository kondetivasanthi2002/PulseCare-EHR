"""
PulseCare Clinical Dictionaries & Medical Coding Catalogs.
Contains authoritative clinical lookup data for ICD-10-CM diagnoses, CPT procedure codes,
RxNorm drug interaction matrices, and LOINC laboratory reference ranges.
"""

from typing import Dict, Any, List, Optional


# ICD-10-CM Diagnosis Code Dictionary
ICD10_CATALOG: Dict[str, Dict[str, Any]] = {
    "E11.9": {"description": "Type 2 diabetes mellitus without complications", "category": "Endocrine", "risk_score": 1.2},
    "E11.65": {"description": "Type 2 diabetes mellitus with hyperglycemia", "category": "Endocrine", "risk_score": 1.8},
    "I10": {"description": "Essential (primary) hypertension", "category": "Cardiovascular", "risk_score": 1.1},
    "I25.10": {"description": "Atherosclerotic heart disease of native coronary artery", "category": "Cardiovascular", "risk_score": 2.5},
    "J45.909": {"description": "Unspecified asthma, uncomplicated", "category": "Respiratory", "risk_score": 1.3},
    "J44.9": {"description": "Chronic obstructive pulmonary disease, unspecified", "category": "Respiratory", "risk_score": 2.2},
    "F41.1": {"description": "Generalized anxiety disorder", "category": "Mental Health", "risk_score": 1.0},
    "F32.9": {"description": "Major depressive disorder, single episode, unspecified", "category": "Mental Health", "risk_score": 1.2},
    "M54.50": {"description": "Low back pain, unspecified", "category": "Musculoskeletal", "risk_score": 1.0},
    "K21.9": {"description": "Gastro-esophageal reflux disease without esophagitis", "category": "Gastrointestinal", "risk_score": 1.0},
    "N39.0": {"description": "Urinary tract infection, site not specified", "category": "Genitourinary", "risk_score": 1.1},
    "U07.1": {"description": "COVID-19", "category": "Infectious Disease", "risk_score": 2.0},
    "Z00.00": {"description": "Encounter for general adult medical examination without abnormal findings", "category": "Preventive", "risk_score": 0.0},
}


# CPT Procedure Code Catalog
CPT_CATALOG: Dict[str, Dict[str, Any]] = {
    "99211": {"description": "Office or other outpatient visit, minimal severity, 5-10 minutes", "base_price": 45.00, "category": "Evaluation & Management"},
    "99212": {"description": "Office or other outpatient visit, straightforward, 10-19 minutes", "base_price": 85.00, "category": "Evaluation & Management"},
    "99213": {"description": "Office or other outpatient visit, low complexity, 20-29 minutes", "base_price": 130.00, "category": "Evaluation & Management"},
    "99214": {"description": "Office or other outpatient visit, moderate complexity, 30-39 minutes", "base_price": 195.00, "category": "Evaluation & Management"},
    "99215": {"description": "Office or other outpatient visit, high complexity, 40-54 minutes", "base_price": 275.00, "category": "Evaluation & Management"},
    "93000": {"description": "Electrocardiogram, routine ECG with at least 12 leads", "base_price": 110.00, "category": "Cardiology"},
    "36415": {"description": "Routine venipuncture (blood draw)", "base_price": 25.00, "category": "Laboratory"},
    "71045": {"description": "Chest X-ray, single view", "base_price": 140.00, "category": "Radiology"},
    "71046": {"description": "Chest X-ray, 2 views", "base_price": 185.00, "category": "Radiology"},
    "90658": {"description": "Influenza virus vaccine, trivalent", "base_price": 40.00, "category": "Immunization"},
}


# RxNorm Drug Collision & Dangerous Interaction Matrix
DRUG_INTERACTION_MATRIX: List[Dict[str, Any]] = [
    {
        "drug1_rxnorm": "313782",  # Warfarin
        "drug1_name": "Warfarin",
        "drug2_rxnorm": "1191",    # Aspirin
        "drug2_name": "Aspirin",
        "severity": "CRITICAL",
        "warning": "Increased risk of major hemorrhage/bleeding when Warfarin is combined with Aspirin."
    },
    {
        "drug1_rxnorm": "313782",  # Warfarin
        "drug1_name": "Warfarin",
        "drug2_rxnorm": "5640",    # Ibuprofen
        "drug2_name": "Ibuprofen",
        "severity": "CRITICAL",
        "warning": "Severe GI ulceration and bleeding risk when Warfarin is taken with NSAIDs."
    },
    {
        "drug1_rxnorm": "197361",  # Lisinopril
        "drug1_name": "Lisinopril",
        "drug2_rxnorm": "855332",  # Potassium Chloride
        "drug2_name": "Potassium Chloride",
        "severity": "HIGH",
        "warning": "Risk of severe hyperkalemia (high serum potassium) causing cardiac arrest."
    },
    {
        "drug1_rxnorm": "860975",  # Sildenafil
        "drug1_name": "Sildenafil",
        "drug2_rxnorm": "7531",    # Nitroglycerin
        "drug2_name": "Nitroglycerin",
        "severity": "CRITICAL",
        "warning": "Potentially fatal profound hypotension (life-threatening drop in blood pressure)."
    },
]


# LOINC Laboratory Reference Ranges
LOINC_CATALOG: Dict[str, Dict[str, Any]] = {
    "2345-7": {"name": "Glucose [Mass/volume] in Serum or Plasma", "unit": "mg/dL", "ref_low": 70.0, "ref_high": 99.0, "critical_low": 40.0, "critical_high": 400.0},
    "4544-3": {"name": "Hematocrit [Volume Fraction] of Blood", "unit": "%", "ref_low": 38.3, "ref_high": 48.6, "critical_low": 20.0, "critical_high": 60.0},
    "718-7": {"name": "Hemoglobin [Mass/volume] in Blood", "unit": "g/dL", "ref_low": 13.8, "ref_high": 17.2, "critical_low": 7.0, "critical_high": 20.0},
    "2823-3": {"name": "Potassium [Moles/volume] in Serum or Plasma", "unit": "mmol/L", "ref_low": 3.5, "ref_high": 5.1, "critical_low": 2.8, "critical_high": 6.2},
    "2951-2": {"name": "Sodium [Moles/volume] in Serum or Plasma", "unit": "mmol/L", "ref_low": 135.0, "ref_high": 145.0, "critical_low": 120.0, "critical_high": 160.0},
    "2160-0": {"name": "Creatinine [Mass/volume] in Serum or Plasma", "unit": "mg/dL", "ref_low": 0.74, "ref_high": 1.35, "critical_low": 0.3, "critical_high": 5.0},
}
