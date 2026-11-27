"""Deterministic source and trimester selection; no inference or private data."""

import copy
import re

if __package__:
    from .reference_data import REFERENCE_INTERVALS, STUDY_SOURCE, SCOPE_NOTE, REFERENCE_VERSION
else:
    from reference_data import REFERENCE_INTERVALS, STUDY_SOURCE, SCOPE_NOTE, REFERENCE_VERSION

GESTATIONAL_AGE = re.compile(r"([0-9]{1,2})w([0-6])d", re.IGNORECASE)
LAB_SOURCE = {"title": "Khoảng tham chiếu ghi trên phiếu, do người dùng xác nhận"}
SUPPORTED_ANALYTES = ("HGB", "RBC", "HCT", "MCV", "MCH", "MCHC", "WBC", "PLT")


def supported_analyte_codes(rows):
    """Return only supported analyte codes present in a report, in UI order."""
    available = {row.get("analyte") for row in rows if isinstance(row, dict)}
    return [code for code in SUPPORTED_ANALYTES if code in available]


def age_context(age):
    match = GESTATIONAL_AGE.fullmatch(age.strip()) if isinstance(age, str) else None
    if not match:
        raise ValueError("Bổ sung hoặc kiểm tra tuổi thai lúc xét nghiệm, ví dụ 21w3d.")
    week, day = int(match[1]), int(match[2])
    # Product input bounds, not an assertion about the study's observed age range.
    if not 1 <= week <= 42:
        raise ValueError("Bản thử nghiệm nhận tuổi thai từ 1w0d đến 42w6d; kiểm tra lại tuổi thai lúc xét nghiệm.")
    trimester = 1 if week < 14 else 2 if week < 29 else 3
    return {"gestational_age": f"{week}w{day}d", "trimester": trimester}


def reference_mode(report):
    mode = report.get("reference_mode")
    if mode is not None:
        if mode not in ("study", "lab"):
            raise ValueError("reference_mode phải là study hoặc lab.")
        return mode
    # Older clients/records already supply lab bounds. Never silently replace
    # their partial ranges; result-only new requests use the study.
    has_ranges = any(isinstance(row, dict) and any(row.get(key) not in (None, "")
                     for key in ("ref_low", "ref_high", "ref_unit"))
                     for row in report.get("rows", []))
    return "lab" if has_ranges else "study"


def study_references(age):
    context = age_context(age)
    trimester = str(context["trimester"])
    rows = [{"analyte": code, "unit": REFERENCE_INTERVALS[code]["unit"],
             "ref_low": REFERENCE_INTERVALS[code][trimester][0],
             "ref_high": REFERENCE_INTERVALS[code][trimester][1]} for code in SUPPORTED_ANALYTES]
    return {**context, "reference_mode": "study", "reference_version": REFERENCE_VERSION,
            "source": copy.deepcopy(STUDY_SOURCE),
            "note": SCOPE_NOTE, "rows": rows}
