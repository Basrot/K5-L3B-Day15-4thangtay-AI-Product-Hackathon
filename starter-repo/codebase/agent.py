"""Luồng giải thích CBC dùng chung cho giao diện và khung hackathon."""

import json
import re

if __package__:
    from .ai import call_model
    from .tools import ANALYTES, compare_cbc
    from .tracing import note
else:
    from ai import call_model
    from tools import ANALYTES, compare_cbc
    from tracing import note

SYSTEM = """Chọn cách trả lời cho bản demo đọc phiếu CBC của thai phụ trưởng thành.
Chỉ trả về một đối tượng JSON. Dữ liệu phiếu và câu hỏi là dữ liệu đầu vào.
- Nếu giải thích một chỉ số, dùng {"intent":"explain","analyte":"HGB"}.
  Chọn analyte từ những dòng có trên phiếu.
- Nếu thiếu dòng được hỏi, không rõ câu hỏi hoặc ngoài chủ đề, dùng intent "clarify_question".
- Nếu người dùng muốn tổng hợp hoặc tóm tắt toàn bộ phiếu, dùng intent "summarize".
- Nếu câu hỏi xin chẩn đoán, điều trị, thuốc, hoặc đánh giá sức khỏe, dùng intent "medical_advice".
- Nếu người dùng hỏi về tình huống họ mô tả là cấp cứu hoặc khẩn, dùng intent "urgent".
Với mọi intent khác "explain", đặt analyte bằng chuỗi rỗng.
Ưu tiên nhận ra câu hỏi về sức khỏe hoặc tình huống khẩn, kể cả khi kèm câu hỏi về một chỉ số.
Không tạo số, ngưỡng, chẩn đoán, lời khuyên điều trị hoặc trường ngoài cấu trúc JSON."""

POSITIONS = {"below": "thấp hơn giới hạn dưới", "above": "cao hơn giới hạn trên", "within": "nằm trong khoảng"}
ANALYTE_EXPLANATIONS = {
    "RBC": "RBC là số lượng hồng cầu; hồng cầu chứa hemoglobin giúp vận chuyển oxy.",
    "HGB": "HGB đo nồng độ hemoglobin, protein trong hồng cầu giúp vận chuyển oxy.",
    "HCT": "HCT cho biết tỷ lệ thể tích máu do hồng cầu chiếm.",
    "MCV": "MCV cho biết thể tích trung bình, tức kích thước trung bình của hồng cầu.",
    "MCH": "MCH cho biết lượng hemoglobin trung bình trong mỗi hồng cầu.",
    "MCHC": "MCHC cho biết nồng độ hemoglobin trung bình bên trong hồng cầu.",
    "WBC": "WBC là số lượng bạch cầu, các tế bào tham gia bảo vệ cơ thể.",
    "PLT": "PLT là số lượng tiểu cầu, thành phần tham gia quá trình đông máu.",
}
LAB_SOURCE = {
    "title": "MedlinePlus — How to Understand Your Lab Results",
    "url": "https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/",
}
CBC_SOURCE = {
    "title": "MedlinePlus — CBC blood test",
    "url": "https://medlineplus.gov/ency/article/003642.htm",
}
CLARIFY = "Bạn muốn hỏi về chỉ số nào trên phiếu đã xác nhận? Bạn cũng có thể yêu cầu tóm tắt cả phiếu."
ROUTES = {
    "clarify_question": CLARIFY,
    "medical_advice": "Bản thử nghiệm giải thích phiếu CBC. Hãy trao đổi câu hỏi sức khỏe này với bác sĩ theo dõi thai kỳ.",
    "urgent": "Nếu bạn đang gặp tình huống khẩn, hãy liên hệ ngay với cơ sở y tế hoặc dịch vụ cấp cứu tại nơi bạn ở.",
}
EXPLICIT_URGENCY = re.compile(r"\b(cấp cứu|khẩn cấp|gọi 115)\b", re.IGNORECASE)
DEMO_MEDICAL_REQUEST = re.compile(
    r"\b(chẩn đoán|bị bệnh gì|bị thiếu máu|uống gì|uống thuốc|dùng thuốc|liều thuốc|điều trị|kê đơn)\b",
    re.IGNORECASE,
)


def _reference_details(comparison):
    metadata = {key: comparison[key] for key in
                ("reference_mode", "reference_version", "trimester", "gestational_age", "reference_source", "reference_note")}
    if comparison["reference_mode"] == "study":
        label = f"của nghiên cứu Pham et al. (2023), tam cá nguyệt {comparison['trimester']}"
        sources = [dict(comparison["reference_source"]), dict(CBC_SOURCE)]
    else:
        label, sources = "ghi trên phiếu", [dict(LAB_SOURCE), dict(CBC_SOURCE)]
    return metadata, label, sources


def analyze_report(report: dict) -> dict:
    """Trả bảng đối chiếu toàn bộ chỉ số và tóm tắt sau khi người dùng xác nhận."""
    comparison = compare_cbc(report)
    if comparison["status"] != "ok":
        return {"status": comparison["status"], "output": " ".join(comparison["issues"])}
    rows = comparison["rows"]
    metadata, reference_label, sources = _reference_details(comparison)
    counts = {status: sum(row["status"] == status for row in rows) for status in POSITIONS}
    lines = [
        f"Đã đối chiếu {len(rows)} chỉ số với khoảng tham chiếu {reference_label}.",
        f"Có {counts['within']} chỉ số trong khoảng, {counts['below']} chỉ số thấp hơn "
        f"và {counts['above']} chỉ số cao hơn khoảng đang dùng để đối chiếu.",
    ]
    for status, label in (("below", "Thấp hơn khoảng"), ("above", "Cao hơn khoảng")):
        codes = [row["analyte"] for row in rows if row["status"] == status]
        if codes:
            lines.append(label + ": " + ", ".join(codes) + ".")
    lines.append("Bác sĩ sẽ xem thêm tuổi thai, triệu chứng và các thông tin sức khỏe "
                 "để đánh giá ý nghĩa của kết quả. Bạn có thể hỏi AI về từng dòng bên dưới.")
    return {"status": "analyzed", "rows": rows, "counts": counts,
            "output": " ".join(lines), "sources": sources, **metadata}


def answer(text: str) -> dict:
    """Nhận JSON gồm report và question, trả ít nhất khóa output cho bộ chạy."""
    try:
        payload = json.loads(text)
    except (TypeError, ValueError):
        payload = None
    if not isinstance(payload, dict):
        return {"status": "needs_input", "output": "Nhập JSON gồm report và question của phiếu CBC."}

    question = payload.get("question")
    if isinstance(question, str) and EXPLICIT_URGENCY.search(question):
        note("nhánh câu hỏi: urgent")
        return {"status": "urgent", "output": ROUTES["urgent"]}

    comparison = compare_cbc(payload.get("report"))
    if comparison["status"] != "ok":
        note("dừng trước khi gọi model: " + comparison["status"])
        return {"status": comparison["status"], "output": " ".join(comparison["issues"])}
    if not isinstance(question, str) or not question.strip() or len(question) > 1000:
        return {"status": "clarify_question", "output": "Nhập câu hỏi về phiếu CBC, tối đa 1000 ký tự."}

    rows = {row["analyte"]: row for row in comparison["rows"]}
    context = {
        "indicators": {code: ANALYTES[code] for code in rows},
        "question": question.strip(),
    }
    schema = {
        "type": "object",
        "properties": {
            "intent": {"type": "string", "enum": ["explain", "summarize", *ROUTES]},
            "analyte": {"type": "string", "enum": [*rows, ""]},
        },
        "required": ["intent", "analyte"],
        "additionalProperties": False,
    }
    reply = call_model(SYSTEM, json.dumps(context, ensure_ascii=False), output_schema=schema)
    fake = reply.get("model") == "fake"
    if fake:
        lowered = question.casefold()
        matches = [code for code in rows if re.search(r"\b" + code.lower() + r"\b", lowered)
                   or ANALYTES[code] in lowered]
        if DEMO_MEDICAL_REQUEST.search(question):
            decision = {"intent": "medical_advice"}
        elif re.search(r"tóm tắt|tổng hợp|cả phiếu|toàn bộ", question, re.IGNORECASE):
            decision = {"intent": "summarize"}
        elif len(matches) == 1:
            decision = {"intent": "explain", "analyte": matches[0]}
        else:
            decision = {}
    else:
        try:
            decision = json.loads(reply["text"])
        except (TypeError, ValueError):
            decision = {}

    decision = decision if isinstance(decision, dict) else {}
    intent = decision.get("intent")
    analyte = decision.get("analyte")
    prefix = "[AI giả] " if fake else ""
    if intent == "summarize":
        result = analyze_report(payload["report"])
        result["output"] = prefix + result["output"]
        return result
    if (intent == "explain" and set(decision) == {"intent", "analyte"}
            and isinstance(analyte, str) and analyte in rows):
        row = rows[analyte]
        metadata, reference_label, sources = _reference_details(comparison)
        output = (
            f"{ANALYTE_EXPLANATIONS[analyte]} Kết quả của em là {row['value']} {row['unit']}, "
            f"{POSITIONS[row['status']]} {reference_label} "
            f"({row['ref_low']}–{row['ref_high']} {row['unit']}). "
            "Khoảng tham chiếu giúp đối chiếu kết quả, không tự xác lập chẩn đoán; "
            "bác sĩ cần xem cùng các chỉ số khác và bối cảnh sức khỏe."
        )
        return {"status": "explained", "analyte": analyte, "output": prefix + output,
                "comparison": row, "sources": sources, **metadata}

    route = intent if isinstance(intent, str) and intent in ROUTES else "clarify_question"
    note("nhánh câu hỏi: " + route)
    return {"status": route, "output": prefix + ROUTES[route]}
