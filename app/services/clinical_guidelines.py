"""
PulseCare Clinical Decision Support System (CDSS) & Evidence-Based Clinical Guidelines.
Implements evidence-based clinical protocols for chronic condition management, sepsis screening, and preventive care alerts.
"""

from typing import Dict, Any, List, Optional
from datetime import date


class ClinicalDecisionSupportEngine:
    """Evaluates patient vitals, lab results, and active diagnoses against clinical practice guidelines."""

    @staticmethod
    def evaluate_hypertension_stage(systolic: float, diastolic: float) -> Dict[str, Any]:
        """AHA/ACC 2017 Hypertension Clinical Practice Guidelines Evaluation."""
        if systolic < 120 and diastolic < 80:
            stage = "NORMAL"
            recommendation = "Encourage healthy lifestyle habits and annual re-evaluation."
            risk_level = "LOW"
        elif 120 <= systolic <= 129 and diastolic < 80:
            stage = "ELEVATED"
            recommendation = "Non-pharmacological therapy (diet, exercise) and re-evaluate in 3-6 months."
            risk_level = "MODERATE"
        elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
            stage = "STAGE_1_HYPERTENSION"
            recommendation = "Assess 10-year ASCVD risk. Consider first-line antihypertensive medication (Thiazide, CCB, ACEi)."
            risk_level = "HIGH"
        elif (140 <= systolic <= 179) or (90 <= diastolic <= 119):
            stage = "STAGE_2_HYPERTENSION"
            recommendation = "Initiate prompt antihypertensive medication with 2 agents of different classes."
            risk_level = "VERY_HIGH"
        else:
            stage = "HYPERTENSIVE_CRISIS"
            recommendation = "EMERGENCY: Immediate medical evaluation required. Check for target organ damage."
            risk_level = "CRITICAL"

        return {
            "stage": stage,
            "systolic_bp": systolic,
            "diastolic_bp": diastolic,
            "recommendation": recommendation,
            "risk_level": risk_level
        }

    @staticmethod
    def evaluate_diabetes_control(hba1c: float, fasting_glucose: float) -> Dict[str, Any]:
        """ADA 2024 Standards of Medical Care in Diabetes Evaluation."""
        if hba1c < 5.7:
            status = "NORMAL"
            action = "Routine screening every 3 years."
        elif 5.7 <= hba1c <= 6.4:
            status = "PREDIABETES"
            action = "Lifestyle modification, weight management, consider Metformin."
        else:
            status = "DIABETES_MELLITUS"
            if hba1c < 7.0:
                action = "Well controlled diabetes. Maintain current therapeutic regimen."
            elif 7.0 <= hba1c <= 9.0:
                action = "Suboptimally controlled diabetes. Consider medication titration or dual therapy."
            else:
                action = "Uncontrolled diabetes (A1C > 9%). Consider immediate Insulin therapy or combination agents."

        return {
            "status": status,
            "hba1c_percent": hba1c,
            "fasting_glucose_mg_dl": fasting_glucose,
            "clinical_action": action
        }

    @staticmethod
    def evaluate_qsofa_sepsis_score(respiratory_rate: float, systolic_bp: float, altered_mental_state: bool) -> Dict[str, Any]:
        """Quick Sequential Organ Failure Assessment (qSOFA) Sepsis Screening Score."""
        score = 0
        factors = []

        if respiratory_rate >= 22.0:
            score += 1
            factors.append("Tachypnea (Respiratory rate >= 22 breaths/min)")
        if systolic_bp <= 100.0:
            score += 1
            factors.append("Hypotension (Systolic BP <= 100 mmHg)")
        if altered_mental_state:
            score += 1
            factors.append("Altered Mental Status (GCS < 15)")

        high_risk = score >= 2

        return {
            "qsofa_score": score,
            "high_risk_sepsis": high_risk,
            "contributing_factors": factors,
            "recommendation": "URGENT: Initiate Sepsis-3 bundle (Blood cultures, Lactate, IV Antibiotics, IV Fluids)" if high_risk else "Monitor vital signs."
        }


cdss_engine = ClinicalDecisionSupportEngine()
