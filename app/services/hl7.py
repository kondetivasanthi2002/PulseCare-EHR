"""
PulseCare HL7 v2 Messaging Protocol Service.
Generates and parses standard HL7 v2.5 messages (ADT Patient Registration, ORM Lab Orders, ORU Lab Results).
"""

from datetime import datetime
from typing import Dict, Any, Optional
from app.models.patient import Patient
from app.models.laboratory import LabOrder, LabResult


class HL7MessageEngine:
    """HL7 v2.5 Pipe-Delimited Message Construction Engine."""

    @staticmethod
    def generate_adt_a08(patient: Patient) -> str:
        """Generates an ADT^A08 (Patient Demographics Update) HL7 Message."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        dob = patient.date_of_birth.strftime("%Y%m%d") if patient.date_of_birth else ""
        gender = patient.gender[0] if patient.gender else "U"

        msh = f"MSH|^~\\&|PULSECARE|MAIN_CLINIC|LAB_SYS|CENTRAL_LAB|{timestamp}||ADT^A08|MSG{patient.id[:8]}|P|2.5"
        pid = f"PID|1||{patient.mrn}^^^PULSECARE^MR||{patient.last_name}^{patient.first_name}||{dob}|{gender}|||{patient.address_line1}^^{patient.city}^{patient.state}^{patient.postal_code}^USA||{patient.phone}"
        pv1 = f"PV1|1|O|CLINIC1^^^PULSECARE||||{patient.primary_physician_id or 'UNKNOWN'}^DOCTOR^PRIMARY|||||||||||||||||||||||||||||||||||||{timestamp}"

        return "\r".join([msh, pid, pv1])

    @staticmethod
    def generate_orm_o01(lab_order: LabOrder, patient: Patient) -> str:
        """Generates an ORM^O01 (General Order Message - Lab Request) HL7 Message."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        dob = patient.date_of_birth.strftime("%Y%m%d") if patient.date_of_birth else ""

        msh = f"MSH|^~\\&|PULSECARE|MAIN_CLINIC|LAB_SYS|CENTRAL_LAB|{timestamp}||ORM^O01|ORD{lab_order.order_number}|P|2.5"
        pid = f"PID|1||{patient.mrn}^^^PULSECARE^MR||{patient.last_name}^{patient.first_name}||{dob}|{patient.gender[0] if patient.gender else 'U'}"
        orc = f"ORC|NW|{lab_order.order_number}|||||^30^MINUTES||{timestamp}|||{lab_order.ordering_doctor_id}^DOCTOR"
        obr = f"OBR|1|{lab_order.order_number}||{lab_order.loinc_code}^{lab_order.test_name}^LN|||{timestamp}|||||||||{lab_order.ordering_doctor_id}^DOCTOR"

        return "\r".join([msh, pid, orc, obr])

    @staticmethod
    def parse_oru_r01(hl7_str: str) -> Dict[str, Any]:
        """Parses an incoming ORU^R01 (Observation Result Unsolicited) HL7 message into structured data."""
        segments = hl7_str.split("\r")
        parsed_data = {
            "message_type": "ORU_R01",
            "patient_mrn": None,
            "order_number": None,
            "observations": []
        }

        for segment in segments:
            fields = segment.split("|")
            seg_type = fields[0]

            if seg_type == "PID":
                if len(fields) > 3:
                    parsed_data["patient_mrn"] = fields[3].split("^")[0]
            elif seg_type == "OBR":
                if len(fields) > 2:
                    parsed_data["order_number"] = fields[2]
            elif seg_type == "OBX":
                if len(fields) > 5:
                    loinc_part = fields[3].split("^")
                    parsed_data["observations"].append({
                        "loinc_code": loinc_part[0] if len(loinc_part) > 0 else "",
                        "parameter_name": loinc_part[1] if len(loinc_part) > 1 else "",
                        "value": fields[5],
                        "units": fields[6] if len(fields) > 6 else "",
                        "abnormal_flag": fields[8] if len(fields) > 8 else "N"
                    })

        return parsed_data


hl7_engine = HL7MessageEngine()
