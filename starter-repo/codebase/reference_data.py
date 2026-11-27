"""Published trimester intervals; no patient-level workbook data.

Pham HN et al., BMC Pregnancy and Childbirth 23, 788 (2023), Tables 2/3.
https://doi.org/10.1186/s12884-023-06106-2
Transcribed from the 2.5th/97.5th point estimates, excluding the 90% CIs.
Names/units are normalized to the app catalog; decimal precision is preserved.
The article is CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
"""

from types import MappingProxyType

REFERENCE_VERSION = "pham2023-tables-v1"

STUDY_SOURCE = {
    "version": REFERENCE_VERSION,
    "title": "Reference intervals of complete blood count and coagulation tests in Vietnamese pregnant women",
    "url": "https://doi.org/10.1186/s12884-023-06106-2",
    "table_urls": (
        "https://bmcpregnancychildbirth.biomedcentral.com/articles/10.1186/s12884-023-06106-2/tables/2",
        "https://bmcpregnancychildbirth.biomedcentral.com/articles/10.1186/s12884-023-06106-2/tables/3",
    ),
    "year": 2023,
    "instruments": "DxH 900 (Beckman Coulter) cho CBC; ACL TOP 550 (Werfen) cho đông máu.",
    "population": (
        "Thai phụ đơn thai đủ tiêu chuẩn tại Bệnh viện Hùng Vương, TP.HCM, tháng 6–8/2023; "
        "879 người tuyển, 837 mẫu CBC và 836 mẫu đông máu đạt chất lượng trước loại ngoại lai."
    ),
}

SCOPE_NOTE = (
    "Khoảng tham chiếu nghiên cứu theo tam cá nguyệt, không phải ngưỡng chẩn đoán; "
    "chưa được xác nhận chuyển giao cho phòng xét nghiệm đang sử dụng. "
    "Nghiên cứu ở thai đơn tại Bệnh viện Hùng Vương, dùng DxH 900 và ACL TOP 550; "
    "loại trừ tăng huyết áp, đái tháo đường, tiền sản giật, bệnh huyết sắc tố, "
    "nhiễm trùng và sử dụng thuốc chống đông. "
    "Cần đối chiếu phương pháp, thiết bị, quần thể và khoảng trên phiếu; "
    "bác sĩ đánh giá cùng triệu chứng và bối cảnh lâm sàng. "
    "Trong khoảng không loại trừ bệnh; không dùng cận HGB này để kết luận có hay không thiếu máu."
)

SOURCE_NOTES = (
    "Giữ ước lượng điểm bách phân vị 2.5 và 97.5 của Bảng 2/3; không dùng cận khoảng tin cậy 90%.",
    "PT tam cá nguyệt 2: Bảng 3 ghi cận trên 11.60 s, abstract ghi 11.66 s; dữ liệu ứng dụng theo Bảng 3 (11.60 s).",
)

# Each row uses exactly the table's point estimates in catalog units.
# Nested mapping proxies and tuple bounds prevent accidental in-process edits.
REFERENCE_INTERVALS = MappingProxyType({
    code: MappingProxyType(entry) for code, entry in {
        "RBC": {"unit": "10^12/L", "1": ("3.73", "5.32"), "2": ("3.33", "4.98"), "3": ("3.54", "4.98")},
        "HGB": {"unit": "g/dL", "1": ("10.33", "13.95"), "2": ("9.71", "13.17"), "3": ("9.80", "13.97")},
        "HCT": {"unit": "%", "1": ("32.22", "42.29"), "2": ("30.26", "40.07"), "3": ("31.11", "42.70")},
        "MCV": {"unit": "fL", "1": ("66.13", "95.85"), "2": ("69.14", "97.79"), "3": ("69.43", "98.40")},
        "MCH": {"unit": "pg", "1": ("20.57", "31.78"), "2": ("21.51", "32.68"), "3": ("21.18", "32.47")},
        "MCHC": {"unit": "g/dL", "1": ("31.13", "33.85"), "2": ("30.99", "34.13"), "3": ("30.70", "33.94")},
        "RDW": {"unit": "%", "1": ("12.27", "17.78"), "2": ("12.69", "16.17"), "3": ("12.75", "17.29")},
        "RDW_SD": {"unit": "fL", "1": ("35.09", "50.49"), "2": ("37.97", "48.65"), "3": ("37.63", "52.52")},
        "WBC": {"unit": "10^9/L", "1": ("6.33", "15.24"), "2": ("6.99", "15.55"), "3": ("6.22", "14.14")},
        "NEUT_ABS": {"unit": "10^9/L", "1": ("3.43", "11.70"), "2": ("4.57", "12.25"), "3": ("3.99", "10.74")},
        "NEUT_PCT": {"unit": "%", "1": ("55.71", "80.31"), "2": ("59.72", "79.61"), "3": ("58.01", "80.30")},
        "LYMPH_ABS": {"unit": "10^9/L", "1": ("1.22", "3.23"), "2": ("1.24", "3.03"), "3": ("1.16", "3.06")},
        "LYMPH_PCT": {"unit": "%", "1": ("11.83", "34.29"), "2": ("11.94", "29.31"), "3": ("11.59", "31.07")},
        "MONO_ABS": {"unit": "10^9/L", "1": ("0.35", "1.12"), "2": ("0.38", "1.28"), "3": ("0.43", "1.21")},
        "MONO_PCT": {"unit": "%", "1": ("3.93", "10.59"), "2": ("4.17", "10.26"), "3": ("4.60", "11.94")},
        "EOS_ABS": {"unit": "10^9/L", "1": ("0.02", "0.50"), "2": ("0.04", "0.50"), "3": ("0.03", "0.39")},
        "EOS_PCT": {"unit": "%", "1": ("0.22", "4.79"), "2": ("0.34", "4.64"), "3": ("0.33", "3.74")},
        "BASO_ABS": {"unit": "10^9/L", "1": ("0.01", "0.09"), "2": ("0.01", "0.09"), "3": ("0.01", "0.09")},
        "BASO_PCT": {"unit": "%", "1": ("0.10", "0.92"), "2": ("0.10", "0.76"), "3": ("0.12", "0.93")},
        "PLT": {"unit": "10^9/L", "1": ("169.66", "413.88"), "2": ("172.34", "372.19"), "3": ("151.30", "417.14")},
        "MPV": {"unit": "fL", "1": ("6.65", "9.85"), "2": ("6.48", "9.70"), "3": ("6.69", "10.39")},
        "PT": {"unit": "s", "1": ("10.30", "12.88"), "2": ("9.80", "11.60"), "3": ("9.60", "11.40")},
        "APTT": {"unit": "s", "1": ("25.40", "35.46"), "2": ("24.05", "33.23"), "3": ("23.40", "31.80")},
        "FIB": {"unit": "mg/dL", "1": ("280.28", "559.00"), "2": ("347.75", "593.35"), "3": ("330.28", "628.56")},
    }.items()
})
