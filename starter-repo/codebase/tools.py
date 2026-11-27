"""Đối chiếu xét nghiệm với khoảng nghiên cứu theo tuổi thai hoặc khoảng trên phiếu."""

import re
import unicodedata
from decimal import Decimal

if __package__:
    from .tracing import tool
    from .catalog import ANALYTES, normalize_analyte
    from .references import GESTATIONAL_AGE, age_context, reference_mode, study_references, LAB_SOURCE
else:
    from tracing import tool
    from catalog import ANALYTES, normalize_analyte
    from references import GESTATIONAL_AGE, age_context, reference_mode, study_references, LAB_SOURCE

# Each exponent converts a value to the same dimension-specific base unit.
UNITS = {
    "HGB": {"g/l": ("g/L", -1), "g/dl": ("g/dL", 0)},
    "WBC": {
        "10^9/l": ("10⁹/L", 0),
        "10^3/μl": ("10³/µL", 0), "k/μl": ("K/µL", 0),
    },
}
UNITS["PLT"] = UNITS["WBC"]
UNITS["RBC"] = {"10^12/l": ("10¹²/L", 0), "10^6/μl": ("10⁶/µL", 0),
                "m/μl": ("M/µL", 0)}
UNITS["HCT"] = {"%": ("%", 0), "l/l": ("L/L", 2)}
UNITS["MCHC"] = UNITS["HGB"]
UNITS["FIB"] = {"g/l": ("g/L", 0), "mg/dl": ("mg/dL", -2)}
for _code in ("NEUT", "LYMPH", "MONO", "EOS", "BASO"):
    UNITS[_code + "_ABS"] = UNITS["WBC"]
    UNITS[_code + "_PCT"] = {"%": ("%", 0)}
for _code in ("MCV", "RDW_SD", "MPV"):
    UNITS[_code] = {"fl": ("fL", 0)}
UNITS["MCH"] = {"pg": ("pg", 0)}
UNITS["RDW"] = {"%": ("%", 0)}
for _code in ("PT", "APTT"):
    UNITS[_code] = {"s": ("s", 0), "sec": ("s", 0)}
NUMBER = re.compile(r"[0-9]{1,12}(?:[.,][0-9]{1,8})?")


def _decimal(raw):
    if isinstance(raw, bool) or not isinstance(raw, (str, int, float, Decimal)):
        raise ValueError
    text = str(raw).strip()
    if not NUMBER.fullmatch(text):
        raise ValueError
    return Decimal(text.replace(",", "."))


def _unit(analyte, raw):
    text = str(raw)
    for superscript, exponent in (("¹²", "^12"), ("⁹", "^9"), ("⁶", "^6"), ("³", "^3")):
        text = text.replace(superscript, exponent)
    key = unicodedata.normalize("NFKC", text).lower()
    key = "".join(key.split()).removeprefix("×").removeprefix("x")
    key = key.replace("ul", "μl")
    return UNITS[analyte].get(key)


def _format_decimal(value):
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


_TREND_BASE_UNITS = {
    "HGB": "g/dL", "RBC": "10¹²/L", "HCT": "%", "MCV": "fL",
    "MCH": "pg", "MCHC": "g/dL", "WBC": "10⁹/L", "PLT": "10⁹/L",
}


def confirmed_comparison(report):
    """Use a saved confirmation snapshot; safely reconstruct only known legacy reports."""
    snapshot = report.get("analysis_snapshot") if isinstance(report, dict) else None
    required = {"rows", "gestational_age", "trimester", "reference_mode", "reference_source"}
    if isinstance(snapshot, dict) and required <= snapshot.keys():
        return {"status": "ok", **snapshot}

    try:
        mode = reference_mode(report)
    except (TypeError, ValueError):
        return compare_cbc(report)
    if mode == "study" and not report.get("reference_version"):
        return {"status": "needs_input", "issues": [
            "Phiếu CBC cũ chưa lưu phiên bản khoảng nghiên cứu đã dùng; cần xác nhận lại trước khi so sánh."]}

    result = compare_cbc(report)
    if result["status"] == "ok":
        return result

    # Older accepted reports can contain a unit no longer recognized by the
    # current converter. Keep valid rows usable and explain only the affected one.
    successful_rows = []
    row_errors = {}
    metadata = None
    for raw in report.get("rows", []) if isinstance(report, dict) else []:
        if not isinstance(raw, dict):
            continue
        code = normalize_analyte(raw.get("analyte", ""))
        single = compare_cbc({**report, "rows": [raw]})
        if single["status"] == "ok":
            successful_rows.extend(single["rows"])
            metadata = metadata or single
        elif code in ANALYTES:
            row_errors[code] = {
                "reason": "Không thể đối chiếu đơn vị hoặc khoảng đã lưu của dòng này.",
                "value": str(raw.get("value") or ""),
                "unit": str(raw.get("unit") or ""),
            }
    if metadata is None:
        return result
    return {**metadata, "rows": successful_rows, "row_errors": row_errors}


def compare_cbc_reports(prior_report, current_report, prior_date, current_date):
    """Compare saved reports as values only; do not interpret rise/fall clinically."""
    prior_result = confirmed_comparison(prior_report)
    current_result = confirmed_comparison(current_report)
    for label, result in (("Phiếu trước", prior_result), ("Phiếu hiện tại", current_result)):
        if result["status"] != "ok":
            raise ValueError(f"{label}: " + " ".join(result.get("issues", [])))

    prior_rows = {row["analyte"]: row for row in prior_result["rows"]}
    current_rows = {row["analyte"]: row for row in current_result["rows"]}
    prior_errors = prior_result.get("row_errors", {})
    current_errors = current_result.get("row_errors", {})
    present_codes = set(prior_rows) | set(current_rows) | set(prior_errors) | set(current_errors)
    all_codes = [code for code in ANALYTES if code in present_codes]
    paired = []
    for code in all_codes:
        before, now = prior_rows.get(code), current_rows.get(code)
        item = {"analyte": code, "prior": before, "current": now,
                "delta": None, "delta_unit": None, "comparable": False, "reason": None,
                "prior_normalized_value": None, "current_normalized_value": None,
                "normalized_unit": None, "reference_context_differs": False,
                "prior_unavailable": prior_errors.get(code),
                "current_unavailable": current_errors.get(code)}
        if before is None or now is None:
            if code in prior_errors or code in current_errors:
                item["reason"] = "Không thể chuẩn hóa đơn vị hoặc khoảng tham chiếu của một lần đo."
            else:
                item["reason"] = "Chỉ số này không có trên cả hai phiếu."
        else:
            before_unit = _unit(code, before["unit"])
            now_unit = _unit(code, now["unit"])
            if before_unit is None or now_unit is None:
                item["reason"] = "Không thể chuẩn hóa đơn vị của hai phiếu."
            else:
                range_differs = any(
                    Decimal(before[key]).scaleb(before_unit[1])
                    != Decimal(now[key]).scaleb(now_unit[1])
                    for key in ("ref_low", "ref_high")
                )
                item["reference_context_differs"] = range_differs
                before_value = Decimal(before["value"]).scaleb(before_unit[1])
                now_value = Decimal(now["value"]).scaleb(now_unit[1])
                unit_name = _TREND_BASE_UNITS.get(code) or next(
                    (label for label, exponent in UNITS[code].values() if exponent == 0), None)
                if unit_name is None:
                    item["reason"] = "Không có đơn vị chung an toàn cho hai lần đo."
                else:
                    item.update({
                        "delta": _format_decimal(now_value - before_value),
                        "delta_unit": unit_name,
                        "comparable": True,
                        "prior_normalized_value": _format_decimal(before_value),
                        "current_normalized_value": _format_decimal(now_value),
                        "normalized_unit": unit_name,
                    })
        paired.append(item)

    return {
        "status": "compared",
        "prior": {"specimen_date": prior_date, "gestational_age": prior_result["gestational_age"],
                  "trimester": prior_result["trimester"], "reference_mode": prior_result["reference_mode"],
                  "reference_source": prior_result["reference_source"]},
        "current": {"specimen_date": current_date, "gestational_age": current_result["gestational_age"],
                    "trimester": current_result["trimester"], "reference_mode": current_result["reference_mode"],
                    "reference_source": current_result["reference_source"]},
        "reference_context_differs": (
            any(prior_result[key] != current_result[key]
                for key in ("trimester", "reference_mode", "reference_version"))
            or any(row["reference_context_differs"] for row in paired)
        ),
        "rows": paired,
    }


@tool
def compare_cbc(report: dict) -> dict:
    """Đối chiếu CBC. Input: phiếu đã xác nhận. Output: trạng thái và các dòng/lỗi. Chỉ đọc."""
    if not isinstance(report, dict):
        return {"status": "needs_input", "issues": ["Bổ sung thông tin phiếu CBC."]}

    pregnant = report.get("pregnancy_status")
    adult = report.get("adult_confirmed")
    if pregnant == "not_pregnant" or adult is False:
        return {"status": "out_of_scope", "issues": ["Bản thử nghiệm hỗ trợ thai phụ trưởng thành."]}
    if pregnant != "pregnant" or adult is not True:
        return {"status": "needs_input", "issues": ["Xác nhận tình trạng thai kỳ và người làm xét nghiệm đã trưởng thành."]}

    try:
        context = age_context(report.get("gestational_age"))
    except ValueError as exc:
        return {"status": "needs_input", "issues": [str(exc)]}

    raw_rows = report.get("rows")
    if not isinstance(raw_rows, list) or not 1 <= len(raw_rows) <= len(ANALYTES):
        return {"status": "needs_input", "issues": ["Nhập từ 1 đến 24 chỉ số trong danh mục xét nghiệm."]}

    try:
        mode = reference_mode(report)
    except ValueError as exc:
        return {"status": "needs_input", "issues": [str(exc)]}
    study = study_references(context["gestational_age"]) if mode == "study" else None
    if study and report.get("reference_version") not in (None, study["reference_version"]):
        return {"status": "needs_input", "issues": [
            "Phiên bản bảng tham chiếu đã thay đổi hoặc không được hỗ trợ. "
            "Kiểm tra phiếu và xác nhận lại với bảng tham chiếu hiện tại."]}
    ranges = {row["analyte"]: row for row in study["rows"]} if study else {}

    rows, issues, seen = [], [], set()
    for index, raw in enumerate(raw_rows, start=1):
        analyte = normalize_analyte(raw.get("analyte", "")) if isinstance(raw, dict) else ""
        if analyte not in ANALYTES:
            issues.append(f"Dòng {index}: chọn chỉ số trong danh mục; bạch cầu thành phần cần ghi rõ số lượng (#/ABS) hoặc tỷ lệ (%/PCT).")
            continue
        if analyte in seen:
            issues.append(f"{analyte}: chỉ giữ một dòng từ phiếu hiện tại.")
            continue
        seen.add(analyte)
        reference = ({"ref_low": ranges[analyte]["ref_low"], "ref_high": ranges[analyte]["ref_high"],
                      "ref_unit": ranges[analyte]["unit"]} if study else raw)
        result_unit = _unit(analyte, raw.get("unit"))
        ref_unit = _unit(analyte, reference.get("ref_unit"))
        if result_unit is None or ref_unit is None:
            issues.append(f"{analyte}: kiểm tra đơn vị kết quả." if study else
                          f"{analyte}: kiểm tra đơn vị kết quả và đơn vị khoảng tham chiếu trên phiếu.")
            continue
        try:
            value = _decimal(raw.get("value"))
            low, high = (_decimal(reference.get(key)) for key in ("ref_low", "ref_high"))
        except ValueError:
            issues.append(f"{analyte}: kiểm tra giá trị kết quả." if study else
                          f"{analyte}: kiểm tra giá trị và hai giới hạn của khoảng tham chiếu.")
            continue
        if low >= high:
            issues.append(f"{analyte}: giới hạn dưới phải nhỏ hơn giới hạn trên.")
            continue
        value = value.scaleb(result_unit[1] - ref_unit[1])
        status = "below" if value < low else "above" if value > high else "within"
        rows.append({"analyte": analyte, "value": _format_decimal(value), "unit": ref_unit[0],
                     "ref_low": _format_decimal(low), "ref_high": _format_decimal(high), "status": status})
    if issues:
        return {"status": "needs_input", "issues": issues}
    return {"status": "ok", "rows": rows, **context, "reference_mode": mode,
            "reference_version": study["reference_version"] if study else None,
            "reference_source": study["source"] if study else dict(LAB_SOURCE),
            "reference_note": study["note"] if study else ""}
