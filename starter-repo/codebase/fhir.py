"""Build a patient-scoped FHIR R4 collection bundle for a confirmed CBC report."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import uuid4


FHIR_R4 = "http://hl7.org/fhir"
LOINC = "http://loinc.org"
UCUM = "http://unitsofmeasure.org"
OBSERVATION_CATEGORY = "http://terminology.hl7.org/CodeSystem/observation-category"
OBSERVATION_INTERPRETATION = "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"

LOINC_CODES = {
    "HGB": ("718-7", "Hemoglobin [Mass/volume] in Blood"),
    "RBC": ("789-8", "Erythrocytes [#/volume] in Blood by Automated count"),
    "HCT": ("4544-3", "Hematocrit [Volume Fraction] of Blood by Automated count"),
    "MCV": ("787-2", "MCV [Entitic mean volume] in Red Blood Cells by Automated count"),
    "MCH": ("785-6", "MCH [Entitic mass] by Automated count"),
    "MCHC": ("786-4", "MCHC [Mass/volume] in Red Blood Cells by Automated count"),
    "WBC": ("6690-2", "Leukocytes [#/volume] in Blood by Automated count"),
    "PLT": ("777-3", "Platelets [#/volume] in Blood by Automated count"),
}

UCUM_CODES = {
    "g/dL": "g/dL", "10^12/L": "10*12/L", "10^9/L": "10*9/L",
    "%": "%", "fL": "fL", "pg": "pg",
}


def build_cbc_bundle(report: dict, *, session_id: str) -> dict:
    """Create a FHIR R4 Bundle from stored, confirmed values and their comparison snapshot."""
    snapshot = report.get("analysis_snapshot") or {}
    rows = snapshot.get("rows") or []
    source = snapshot.get("reference_source") or {}
    source_title = source.get("title") or (
        "Khoảng nghiên cứu CBC thai kỳ theo tam cá nguyệt" if snapshot.get("reference_mode") == "study"
        else "Khoảng tham chiếu do người dùng xác nhận từ phiếu xét nghiệm"
    )
    range_context = "Khoảng nghiên cứu theo tam cá nguyệt; không phải ngưỡng chẩn đoán." \
        if snapshot.get("reference_mode") == "study" else "Khoảng ghi trên phiếu xét nghiệm."
    by_analyte = {row.get("analyte"): row for row in rows if isinstance(row, dict)}
    patient_id = str(uuid4())
    diagnostic_report_id = str(uuid4())
    patient_ref = f"urn:uuid:{patient_id}"
    report_ref = f"urn:uuid:{diagnostic_report_id}"
    entries = [{"fullUrl": patient_ref, "resource": {"resourceType": "Patient", "id": patient_id}}]
    observation_refs = []
    exported_analytes = set()

    for raw in report.get("rows", []):
        analyte = raw.get("analyte")
        code_info = LOINC_CODES.get(analyte)
        if not code_info:
            continue
        analyzed = by_analyte.get(analyte)
        if not analyzed:
            continue
        try:
            value = Decimal(str(analyzed["value"]))
            low = Decimal(str(analyzed["ref_low"]))
            high = Decimal(str(analyzed["ref_high"]))
        except (KeyError, InvalidOperation, TypeError):
            continue
        unit = analyzed.get("unit") or raw.get("unit") or ""
        if not unit or unit not in UCUM_CODES:
            continue
        observation_id = str(uuid4())
        observation_ref = f"urn:uuid:{observation_id}"
        observation = {
            "resourceType": "Observation", "id": observation_id, "status": "final",
            "category": [{"coding": [{"system": OBSERVATION_CATEGORY, "code": "laboratory", "display": "Laboratory"}]}],
            "code": {"coding": [{"system": LOINC, "code": code_info[0], "display": code_info[1]}], "text": analyte},
            "subject": {"reference": patient_ref},
            "valueQuantity": {"value": float(value), "unit": unit, "system": UCUM, "code": UCUM_CODES[unit]},
            "referenceRange": [{
                "low": {"value": float(low), "unit": unit, "system": UCUM, "code": UCUM_CODES[unit]},
                "high": {"value": float(high), "unit": unit, "system": UCUM, "code": UCUM_CODES[unit]},
                "text": range_context,
            }],
        }
        if report.get("specimen_date"):
            observation["effectiveDateTime"] = report["specimen_date"]
        status = analyzed.get("status")
        interpretation = {"below": ("L", "Low"), "above": ("H", "High")}.get(status)
        if interpretation:
            observation["interpretation"] = [{"coding": [{
                "system": OBSERVATION_INTERPRETATION, "code": interpretation[0], "display": interpretation[1],
            }]}]
        observation_refs.append({"reference": observation_ref})
        entries.append({"fullUrl": observation_ref, "resource": observation})
        exported_analytes.add(analyte)

    if not observation_refs:
        raise ValueError("Không có chỉ số CBC đã xác nhận và có mã LOINC để xuất FHIR.")

    diagnostic_report = {
        "resourceType": "DiagnosticReport", "id": diagnostic_report_id, "status": "final",
        "issued": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "category": [{"coding": [{"system": OBSERVATION_CATEGORY, "code": "laboratory", "display": "Laboratory"}]}],
        "code": {"coding": [{"system": LOINC, "code": "58410-2", "display": "CBC panel - Blood by Automated count"}],
                 "text": "Complete blood count"},
        "subject": {"reference": patient_ref}, "result": observation_refs,
        "conclusion": ("Kết quả đã được xác nhận bởi người dùng. Trạng thái khoảng tham chiếu không phải chẩn đoán. "
                       + f"Nguồn khoảng: {source_title}. "
                       + ("Đã xuất: " + ", ".join(sorted(exported_analytes)) + ". "
                          + ("Chưa xuất được: " + ", ".join(sorted({row.get('analyte', '') for row in report.get('rows', [])} - exported_analytes)) + "."
                             if len(exported_analytes) < len(report.get("rows", [])) else ""))),
    }
    if report.get("specimen_date"):
        diagnostic_report["effectiveDateTime"] = report["specimen_date"]
    if report.get("gestational_age"):
        diagnostic_report["note"] = [{"text": f"Tuổi thai lúc lấy mẫu theo dữ liệu người dùng: {report['gestational_age']}."}]
    entries.append({"fullUrl": report_ref, "resource": diagnostic_report})
    return {
        "resourceType": "Bundle", "id": str(uuid4()), "meta": {"profile": [f"{FHIR_R4}/StructureDefinition/Bundle"]},
        "type": "collection", "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "identifier": {"system": "urn:cbc-ai:session", "value": session_id}, "entry": entries,
    }
