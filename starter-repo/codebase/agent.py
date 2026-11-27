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
- Nếu giải thích một chỉ số, dùng {"intent":"explain","analyte":"HGB","follow_up":"context"}.
  Chọn analyte từ những dòng có trên phiếu. follow_up là "context" hoặc "compare".
- Nếu thiếu dòng được hỏi, không rõ câu hỏi hoặc ngoài chủ đề, dùng intent "clarify_question".
- Nếu câu hỏi xin chẩn đoán, điều trị, thuốc, hoặc đánh giá sức khỏe, dùng intent "medical_advice".
- Nếu người dùng hỏi về tình huống họ mô tả là cấp cứu hoặc khẩn, dùng intent "urgent".
Với mọi intent khác "explain", đặt analyte và follow_up bằng chuỗi rỗng.
Ưu tiên nhận ra câu hỏi về sức khỏe hoặc tình huống khẩn, kể cả khi kèm câu hỏi về một chỉ số.
Không tạo số, ngưỡng, chẩn đoán, lời khuyên điều trị hoặc trường ngoài cấu trúc JSON."""

FOLLOW_UPS = {
    "context": "Với tuổi thai của em, bác sĩ cần xem thêm thông tin nào để hiểu kết quả này?",
    "compare": "Khi so sánh với lần xét nghiệm trước, em nên dùng thông tin nào trên hai phiếu?",
}
POSITIONS = {"below": "thấp hơn giới hạn dưới", "above": "cao hơn giới hạn trên", "within": "nằm trong khoảng"}
CLARIFY = "Bạn muốn hỏi về dòng nào trên phiếu đã xác nhận, HGB, WBC hay PLT?"
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
            "intent": {"type": "string", "enum": ["explain", *ROUTES]},
            "analyte": {"type": "string", "enum": [*rows, ""]},
            "follow_up": {"type": "string", "enum": [*FOLLOW_UPS, ""]},
        },
        "required": ["intent", "analyte", "follow_up"],
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
        elif len(matches) == 1:
            decision = {"intent": "explain", "analyte": matches[0], "follow_up": "context"}
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
    follow_up = decision.get("follow_up")
    prefix = "[AI giả] " if fake else ""
    if intent == "explain" and isinstance(analyte, str) and analyte in rows and (
        isinstance(follow_up, str) and follow_up in FOLLOW_UPS
    ):
        row = rows[analyte]
        output = (
            f"{analyte} ({ANALYTES[analyte]}) là {row['value']} {row['unit']} sau khi đưa về đơn vị đối chiếu, "
            f"{POSITIONS[row['status']]} ghi trên phiếu ({row['ref_low']}–{row['ref_high']} {row['unit']}). "
            f"Bạn có thể hỏi bác sĩ: {FOLLOW_UPS[follow_up]}"
        )
        return {"status": "explained", "analyte": analyte, "output": prefix + output}

    route = intent if isinstance(intent, str) and intent in ROUTES else "clarify_question"
    note("nhánh câu hỏi: " + route)
    return {"status": route, "output": prefix + ROUTES[route]}
