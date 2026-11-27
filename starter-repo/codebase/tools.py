"""Quy tắc đối chiếu CBC với khoảng tham chiếu do người dùng xác nhận."""

import re
import unicodedata
from decimal import Decimal

if __package__:
    from .tracing import tool
    from .catalog import ANALYTES, normalize_analyte
else:
    from tracing import tool
    from catalog import ANALYTES, normalize_analyte

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
GESTATIONAL_AGE = re.compile(r"([0-9]{1,2})w([0-6])d", re.IGNORECASE)


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

    age = report.get("gestational_age")
    match = GESTATIONAL_AGE.fullmatch(age.strip()) if isinstance(age, str) else None
    if not match:
        return {"status": "needs_input", "issues": ["Bổ sung hoặc kiểm tra tuổi thai lúc xét nghiệm, ví dụ 21w3d."]}

    raw_rows = report.get("rows")
    if not isinstance(raw_rows, list) or not 1 <= len(raw_rows) <= len(ANALYTES):
        return {"status": "needs_input", "issues": ["Nhập từ 1 đến 24 chỉ số trong danh mục xét nghiệm."]}

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
        result_unit = _unit(analyte, raw.get("unit"))
        ref_unit = _unit(analyte, raw.get("ref_unit"))
        if result_unit is None or ref_unit is None:
            issues.append(f"{analyte}: kiểm tra đơn vị kết quả và đơn vị khoảng tham chiếu trên phiếu.")
            continue
        try:
            value, low, high = (_decimal(raw.get(key)) for key in ("value", "ref_low", "ref_high"))
        except ValueError:
            issues.append(f"{analyte}: kiểm tra giá trị và hai giới hạn của khoảng tham chiếu.")
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
    return {"status": "ok", "rows": rows, "gestational_age": match[0].lower()}
