"""Names and unit metadata only: no clinical reference ranges or patient data."""
import re
import unicodedata


ANALYTES = {
    "RBC": "hồng cầu", "HGB": "huyết sắc tố", "HCT": "dung tích hồng cầu",
    "MCV": "thể tích trung bình hồng cầu", "MCH": "lượng huyết sắc tố trung bình hồng cầu",
    "MCHC": "nồng độ huyết sắc tố trung bình hồng cầu", "RDW": "độ phân bố hồng cầu (CV)",
    "RDW_SD": "độ phân bố hồng cầu (SD)", "WBC": "bạch cầu",
    "NEUT_ABS": "bạch cầu trung tính (số lượng)", "NEUT_PCT": "bạch cầu trung tính (tỷ lệ)",
    "LYMPH_ABS": "bạch cầu lympho (số lượng)", "LYMPH_PCT": "bạch cầu lympho (tỷ lệ)",
    "MONO_ABS": "bạch cầu mono (số lượng)", "MONO_PCT": "bạch cầu mono (tỷ lệ)",
    "EOS_ABS": "bạch cầu ái toan (số lượng)", "EOS_PCT": "bạch cầu ái toan (tỷ lệ)",
    "BASO_ABS": "bạch cầu ái kiềm (số lượng)", "BASO_PCT": "bạch cầu ái kiềm (tỷ lệ)",
    "PLT": "tiểu cầu", "MPV": "thể tích trung bình tiểu cầu",
    "PT": "thời gian prothrombin", "APTT": "thời gian thromboplastin từng phần hoạt hóa",
    "FIB": "fibrinogen",
}

DEFAULT_UNITS = {
    "RBC": "10^12/L", "HGB": "g/dL", "HCT": "%", "MCV": "fL", "MCH": "pg",
    "MCHC": "g/dL", "RDW": "%", "RDW_SD": "fL", "WBC": "10^9/L",
    "NEUT_ABS": "10^9/L", "NEUT_PCT": "%", "LYMPH_ABS": "10^9/L", "LYMPH_PCT": "%",
    "MONO_ABS": "10^9/L", "MONO_PCT": "%", "EOS_ABS": "10^9/L", "EOS_PCT": "%",
    "BASO_ABS": "10^9/L", "BASO_PCT": "%", "PLT": "10^9/L", "MPV": "fL",
    "PT": "s", "APTT": "s", "FIB": "mg/dL",
}

GROUPS = {code: ("Hồng cầu" if code in tuple(ANALYTES)[:8] else
                 "Tiểu cầu" if code in ("PLT", "MPV") else
                 "Đông máu" if code in ("PT", "APTT", "FIB") else "Bạch cầu")
          for code in ANALYTES}

# Workbook measurement headers are aliases for analytes, never inferred units.
_HEADERS = dict(zip((
    "RBC_10e12_L", "HGB_g_dL", "HCT_pct", "MCV_fL", "MCH_pg", "MCHC_g_dL",
    "RDW_pct", "RDW_SD_fL", "WBC_10e9_L", "NEUT_abs_10e9_L", "NEUT_pct",
    "LYMPH_abs_10e9_L", "LYMPH_pct", "MONO_abs_10e9_L", "MONO_pct",
    "EOS_abs_10e9_L", "EOS_pct", "BASO_abs_10e9_L", "BASO_pct", "PLT_10e9_L",
    "MPV_fL", "PT_s", "APTT_s", "FIB_mg_dL",
), ANALYTES))


def _key(raw):
    return re.sub(r"[\s_-]+", "", unicodedata.normalize("NFKC", raw).upper())


_ALIASES = {_key(code): code for code in ANALYTES}
_ALIASES.update({_key(header): code for header, code in _HEADERS.items()})
_ALIASES.update({"RDWCV": "RDW", "HB": "HGB", "FIBRINOGEN": "FIB"})
for _code, _stems in {"NEUT": ("NEUT", "NEU"), "LYMPH": ("LYMPH", "LYM", "LY"),
                       "MONO": ("MONO", "MON"), "EOS": ("EOS", "EO"),
                       "BASO": ("BASO", "BAS", "BA")}.items():
    for _stem in _stems:
        for _suffix in ("#", "ABS"):
            _ALIASES[_stem + _suffix] = _code + "_ABS"
        for _suffix in ("%", "PCT"):
            _ALIASES[_stem + _suffix] = _code + "_PCT"


def normalize_analyte(raw: str) -> str:
    """Return a canonical code, or empty string for unknown/ambiguous names."""
    return _ALIASES.get(_key(raw), "") if isinstance(raw, str) else ""
