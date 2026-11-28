"""Luồng giải thích CBC dùng chung cho giao diện và khung hackathon."""

import json
import re

if __package__:
    from .ai import call_model
    from .tools import ANALYTES, compare_cbc, confirmed_comparison
    from .tracing import note
else:
    from ai import call_model
    from tools import ANALYTES, compare_cbc, confirmed_comparison
    from tracing import note

SYSTEM = """Chọn cách trả lời cho bản demo đọc phiếu CBC của thai phụ trưởng thành.
Chỉ trả về một đối tượng JSON. Dữ liệu phiếu và câu hỏi là dữ liệu đầu vào.
- Nếu giải thích một chỉ số, dùng {"intent":"explain","analyte":"HGB"}.
  Chọn analyte từ những dòng có trên phiếu.
- Nếu thiếu dòng được hỏi, không rõ câu hỏi hoặc ngoài chủ đề, dùng intent "clarify_question".
- Nếu người dùng hỏi ý nghĩa của nhiều chỉ số cùng lệch khoảng, dùng intent "explain_group".
- Nếu người dùng muốn tổng hợp hoặc tóm tắt toàn bộ phiếu, dùng intent "summarize".
- Nếu câu hỏi xin chẩn đoán, điều trị, thuốc, hoặc đánh giá sức khỏe, dùng intent "medical_advice".
- Nếu người dùng hỏi về tình huống họ mô tả là cấp cứu hoặc khẩn, dùng intent "urgent".
Với mọi intent khác "explain", đặt analyte bằng chuỗi rỗng.
Ưu tiên nhận ra câu hỏi về sức khỏe hoặc tình huống khẩn, kể cả khi kèm câu hỏi về một chỉ số.
Không tạo số, ngưỡng, chẩn đoán, lời khuyên điều trị hoặc trường ngoài cấu trúc JSON."""

POSITIONS = {"below": "thấp hơn mức thấp nhất", "above": "cao hơn mức cao nhất", "within": "nằm giữa hai mức"}
STAGE_LABELS = {
    1: "tam cá nguyệt 1 (từ 1 tuần 0 ngày đến hết 13 tuần 6 ngày)",
    2: "tam cá nguyệt 2 (từ 14 tuần 0 ngày đến hết 28 tuần 6 ngày)",
    3: "tam cá nguyệt 3 (từ 29 tuần 0 ngày trở đi)",
}
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
ANALYTE_TERMS = {
    "RBC": ("red blood cell count", "số lượng hồng cầu"),
    "HGB": ("hemoglobin", "haemoglobin", "hemoglobin concentration", "huyết sắc tố"),
    "HCT": ("hematocrit", "haematocrit", "dung tích hồng cầu"),
    "MCV": ("mean corpuscular volume", "thể tích trung bình hồng cầu"),
    "MCH": ("mean corpuscular hemoglobin", "lượng huyết sắc tố trung bình hồng cầu"),
    "MCHC": ("mean corpuscular hemoglobin concentration", "nồng độ huyết sắc tố trung bình hồng cầu"),
    "WBC": ("white blood cell count", "white blood cells", "bạch cầu"),
    "PLT": ("platelet count", "platelets", "tiểu cầu"),
}
LAB_SOURCE = {
    "title": "MedlinePlus — How to Understand Your Lab Results",
    "url": "https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/",
}
CBC_SOURCE = {
    "title": "MedlinePlus — CBC blood test",
    "url": "https://medlineplus.gov/ency/article/003642.htm",
}
RBC_INDEX_SOURCE = {
    "title": "MedlinePlus — Red blood cell indices",
    "url": "https://medlineplus.gov/lab-tests/red-blood-cell-rbc-indices/",
}
CLARIFY = "Anh/chị muốn hỏi về chỉ số nào trên phiếu đã xác nhận ạ? Anh/chị cũng có thể nhờ em tóm tắt cả phiếu."
ROUTES = {
    "clarify_question": CLARIFY,
    "medical_advice": "Em chưa thể chẩn đoán hoặc hướng dẫn điều trị từ phiếu CBC. Anh/chị hãy trao đổi câu hỏi sức khỏe này với bác sĩ theo dõi thai kỳ ạ.",
    "urgent": "Nếu anh/chị đang gặp tình huống khẩn cấp, hãy liên hệ ngay với cơ sở y tế hoặc dịch vụ cấp cứu tại nơi anh/chị đang ở ạ.",
}
EXPLICIT_URGENCY = re.compile(r"\b(cấp cứu|khẩn cấp|gọi 115)\b", re.IGNORECASE)
DEMO_MEDICAL_REQUEST = re.compile(
    r"\b(chẩn đoán|bị bệnh gì|bị thiếu máu|uống gì|uống thuốc|nên uống|dùng thuốc|bổ sung sắt|bổ sung thuốc|liều thuốc|điều trị|kê đơn|có nguy hiểm)\b",
    re.IGNORECASE,
)
RANGE_STATUS_QUESTION = re.compile(
    r"\b(ổn|tốt|khỏe|bình thường|bất thường|trong khoảng|ngoài khoảng|nằm trong|cao hơn|thấp hơn|cao|thấp|vượt khoảng|ý nghĩa|là sao|có sao không)\b",
    re.IGNORECASE,
)
GROUP_QUESTION = re.compile(r"\b(nhóm|các chỉ số|nhiều chỉ số|cùng lệch|đồng thời|kết hợp)\b", re.IGNORECASE)
ANEMIA_QUESTION = re.compile(r"\b(thiếu máu|anemia)\b", re.IGNORECASE)
TREATMENT_QUESTION = re.compile(
    r"\b(thuốc|uống|bổ sung|điều trị|kê đơn|liều|chẩn đoán|bị bệnh gì)\b",
    re.IGNORECASE,
)


def _explicit_analyte(question: str, available_codes) -> str | None:
    """Find one clearly named CBC indicator without asking the model to infer it."""
    matches = _explicit_analytes(question, available_codes)
    return matches[0] if len(matches) == 1 else None


def _explicit_analytes(question: str, available_codes) -> list[str]:
    """Find explicitly named CBC indicators in report order."""
    lowered = question.casefold()
    return [
        code for code in available_codes
        if (
            re.search(r"\b" + re.escape(code.casefold()) + r"\b", lowered)
            or ANALYTES[code].casefold() in lowered
            or any(term in lowered for term in ANALYTE_TERMS.get(code, ()))
        )
    ]


def _reference_details(comparison):
    metadata = {key: comparison[key] for key in
                ("reference_mode", "reference_version", "trimester", "gestational_age", "reference_source", "reference_note")}
    if comparison["reference_mode"] == "study":
        stage = STAGE_LABELS.get(comparison["trimester"], f"giai đoạn {comparison['trimester']}")
        label = f"của nghiên cứu Pham et al. (2023), {stage}"
        sources = [dict(comparison["reference_source"]), dict(CBC_SOURCE)]
    else:
        label, sources = "ghi trên phiếu", [dict(LAB_SOURCE), dict(CBC_SOURCE)]
    return metadata, label, sources


def analyze_report(report: dict, *, confirmed=False) -> dict:
    """Trả bảng đối chiếu toàn bộ chỉ số và tóm tắt sau khi người dùng xác nhận."""
    comparison = confirmed_comparison(report) if confirmed else compare_cbc(report)
    if comparison["status"] != "ok":
        return {"status": comparison["status"], "output": " ".join(comparison["issues"])}
    rows = comparison["rows"]
    metadata, reference_label, sources = _reference_details(comparison)
    counts = {status: sum(row["status"] == status for row in rows) for status in POSITIONS}
    lines = [
        f"Em đã so sánh {len(rows)} chỉ số với khoảng {reference_label}.",
        f"Trong đó, {counts['within']} chỉ số nằm trong khoảng; {counts['below']} thấp hơn mức thấp nhất "
        f"và {counts['above']} cao hơn mức cao nhất của khoảng đang chọn.",
    ]
    for status, label in (("below", "Thấp hơn khoảng"), ("above", "Cao hơn khoảng")):
        codes = [row["analyte"] for row in rows if row["status"] == status]
        if codes:
            lines.append(label + ": " + ", ".join(codes) + ".")
    row_errors = comparison.get("row_errors", {})
    if row_errors:
        lines.append("Chưa đối chiếu được: " + "; ".join(
            f"{code} ({issue['reason']})" for code, issue in row_errors.items()
        ) + ".")
    lines.append("Các trạng thái này chỉ cho biết vị trí của con số so với khoảng tham chiếu, "
                 "không tự kết luận có hay không có bệnh; kể cả nằm trong khoảng cũng không loại trừ bệnh.")
    lines.append("Anh/chị có thể dùng những dòng thấp hơn hoặc cao hơn khoảng để hỏi bác sĩ theo dõi thai kỳ; "
                 "bác sĩ sẽ xem thêm tuổi thai, triệu chứng và các thông tin sức khỏe ạ.")
    return {"status": "analyzed", "rows": rows, "counts": counts,
            "output": " ".join(lines), "sources": sources,
            "issues": [f"{code}: {issue['reason']}" for code, issue in row_errors.items()],
            "row_errors": row_errors, **metadata}


def answer(text: str, *, confirmed=False) -> dict:
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

    comparison = confirmed_comparison(payload.get("report")) if confirmed else compare_cbc(payload.get("report"))
    if comparison["status"] != "ok":
        note("dừng trước khi gọi model: " + comparison["status"])
        return {"status": comparison["status"], "output": " ".join(comparison["issues"])}
    if not isinstance(question, str) or not question.strip() or len(question) > 1000:
        return {"status": "clarify_question", "output": "Nhập câu hỏi về phiếu CBC, tối đa 1000 ký tự."}

    rows = {row["analyte"]: row for row in comparison["rows"]}
    flagged_count = sum(row["status"] != "within" for row in rows.values())
    explicit_analyte = _explicit_analyte(question, rows)
    safe_status_question = (
        explicit_analyte and RANGE_STATUS_QUESTION.search(question)
        and not DEMO_MEDICAL_REQUEST.search(question)
    )
    safe_hgb_anemia_question = (
        explicit_analyte == "HGB" and ANEMIA_QUESTION.search(question)
        and not TREATMENT_QUESTION.search(question)
    )
    if safe_status_question or safe_hgb_anemia_question:
        # A direct question about one analyte's saved range status is answered
        # from the deterministic comparison, not left to the LLM's medical-advice classifier.
        note("trả lời trạng thái khoảng theo dữ liệu đã đối chiếu: " + explicit_analyte)
        return _explain_analyte(explicit_analyte, rows[explicit_analyte], comparison)

    context = {
        "indicators": {code: ANALYTES[code] for code in rows},
        "question": question.strip(),
    }
    schema = {
        "type": "object",
        "properties": {
            "intent": {"type": "string", "enum": ["explain", "explain_group", "summarize", *ROUTES]},
            "analyte": {"type": "string", "enum": [*rows, ""]},
        },
        "required": ["intent", "analyte"],
        "additionalProperties": False,
    }
    reply = call_model(SYSTEM, json.dumps(context, ensure_ascii=False), output_schema=schema)
    fake = reply.get("model") == "fake"
    if fake:
        if DEMO_MEDICAL_REQUEST.search(question):
            decision = {"intent": "medical_advice"}
        elif re.search(r"tóm tắt|tổng hợp|cả phiếu|toàn bộ", question, re.IGNORECASE):
            decision = {"intent": "summarize"}
        elif (GROUP_QUESTION.search(question) or RANGE_STATUS_QUESTION.search(question)) and (
                len(_explicit_analytes(question, rows)) >= 2 or flagged_count >= 2):
            decision = {"intent": "explain_group"}
        elif (analyte := _explicit_analyte(question, rows)):
            decision = {"intent": "explain", "analyte": analyte}
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
    named_analytes = _explicit_analytes(question, rows)
    if ((len(named_analytes) >= 2 or flagged_count >= 2)
            and (GROUP_QUESTION.search(question) or RANGE_STATUS_QUESTION.search(question))
            and not DEMO_MEDICAL_REQUEST.search(question)):
        intent = "explain_group"
    explicit_analyte = _explicit_analyte(question, rows)
    if explicit_analyte and intent not in ("explain_group", "summarize", "medical_advice", "urgent"):
        if intent != "explain" or analyte != explicit_analyte:
            note("dùng chỉ số được nêu rõ trong câu hỏi: " + explicit_analyte)
        intent, analyte = "explain", explicit_analyte
    prefix = "[AI giả] " if fake else ""
    if intent == "summarize":
        result = analyze_report(payload["report"], confirmed=confirmed)
        result["output"] = prefix + result["output"]
        return result
    if intent == "explain_group":
        selected = [rows[code] for code in named_analytes if rows[code]["status"] != "within"]
        if len(selected) < 2:
            selected = [row for row in rows.values() if row["status"] != "within"]
        if selected:
            return _explain_group(selected, comparison, prefix=prefix)
        result = analyze_report(payload["report"], confirmed=confirmed)
        result["output"] = prefix + result["output"]
        return result
    if (intent == "explain" and set(decision) == {"intent", "analyte"}
            and isinstance(analyte, str) and analyte in rows):
        return _explain_analyte(analyte, rows[analyte], comparison, prefix=prefix)

    route = intent if isinstance(intent, str) and intent in ROUTES else "clarify_question"
    note("nhánh câu hỏi: " + route)
    missing_analyte = _explicit_analyte(question, ANALYTES)
    if route == "clarify_question" and missing_analyte:
        return {
            "status": route,
            "output": f"Em chưa thấy dòng {missing_analyte} trong phiếu đã xác nhận. Anh/chị kiểm tra phiếu hoặc bổ sung chỉ số này rồi xác nhận lại nhé ạ.",
        }
    return {"status": route, "output": prefix + ROUTES[route]}


def _explain_group(rows, comparison, *, prefix=""):
    """Explain only confirmed out-of-range CBC groups with controlled language."""
    metadata, reference_label, sources = _reference_details(comparison)
    selected = [row for row in rows if row["status"] != "within"]
    items = "; ".join(
        f"{row['analyte']} {row['value']} {row['unit']} ({POSITIONS[row['status']]})"
        for row in selected
    )
    codes = {row["analyte"] for row in selected}
    notes = []
    red_cell = codes & {"HGB", "RBC", "HCT", "MCV", "MCH", "MCHC"}
    if red_cell:
        notes.append(
            ("Nhiều dòng thuộc nhóm hồng cầu/huyết sắc tố cùng lệch khoảng. " if len(red_cell) >= 2 else
             "Dòng lệch khoảng này thuộc nhóm hồng cầu/huyết sắc tố. ")
            + "Bác sĩ có thể xem chúng cùng tuổi thai và bối cảnh sức khỏe; riêng CBC không xác định được nguyên nhân."
        )
        if any(row["analyte"] == "HGB" and row["status"] == "below" for row in selected):
            notes.append(
                "HGB thấp có thể khiến bác sĩ đánh giá thêm về thiếu máu. Nếu MCV hoặc MCH cũng thấp, kiểu kết quả này có thể gặp trong nhiều nguyên nhân, chẳng hạn thiếu sắt hoặc bệnh huyết sắc tố; cần đánh giá của bác sĩ để phân biệt."
            )
        elif any(row["analyte"] in {"MCV", "MCH", "MCHC"} and row["status"] == "below" for row in selected):
            notes.append(
                "MCV/MCH/MCHC thấp mô tả đặc điểm hồng cầu; có thể gặp trong nhiều tình trạng, nhưng không chỉ ra nguyên nhân duy nhất nếu chưa xem các chỉ số khác và xét nghiệm liên quan."
            )
        sources.extend([dict(LAB_SOURCE), dict(CBC_SOURCE), dict(RBC_INDEX_SOURCE)])
    if "WBC" in codes:
        notes.append(
            "WBC là số lượng bạch cầu. Mức cao hoặc thấp không tự chứng minh có nhiễm trùng; thai kỳ, triệu chứng và các thành phần bạch cầu khác cũng cần được xem xét."
        )
    if "PLT" in codes:
        notes.append(
            "PLT là số lượng tiểu cầu, có vai trò trong đông máu. CBC một mình không cho biết nguyên nhân của mức cao hoặc thấp."
        )
    if not notes:
        notes.append(
            "Các dòng này cùng nằm ngoài khoảng đang dùng nhưng không tạo thành một kết luận chẩn đoán từ CBC. Bác sĩ cần diễn giải chúng cùng phiếu gốc, tuổi thai, triệu chứng và xét nghiệm liên quan."
        )
    notes.append(
        f"Khoảng này là {reference_label}, không phải ngưỡng chẩn đoán. Anh/chị có thể hỏi bác sĩ: các chỉ số này có cần đánh giá thêm trong bối cảnh thai kỳ của tôi không, và cần xét nghiệm nào để tìm nguyên nhân?"
    )
    unique_sources = {source["url"]: source for source in sources if source.get("url")}
    return {
        "status": "explained_group",
        "analytes": [row["analyte"] for row in selected],
        "output": prefix + "Em đã xem các dòng đã xác nhận: " + items + ". " + " ".join(notes),
        "sources": list(unique_sources.values()),
        **metadata,
    }


def _explain_analyte(analyte, row, comparison, *, prefix=""):
    metadata, reference_label, sources = _reference_details(comparison)
    explanation = ANALYTE_EXPLANATIONS.get(
        analyte, f"{ANALYTES[analyte].capitalize()} là một chỉ số trong công thức máu CBC."
    )
    status = {
        "below": "thấp hơn khoảng tham chiếu",
        "within": "nằm trong khoảng tham chiếu",
        "above": "cao hơn khoảng tham chiếu",
    }[row["status"]]
    context = ""
    if analyte == "HGB" and row["status"] == "below":
        context = (
            " HGB thấp hơn khoảng có thể khiến bác sĩ đánh giá thêm về thiếu máu, nhưng trạng thái này không tự xác nhận thiếu máu "
            "và riêng CBC không xác định nguyên nhân; cách đánh giá còn phụ thuộc tuổi thai, triệu chứng và xét nghiệm liên quan."
        )
        sources.append(dict(RBC_INDEX_SOURCE))
    elif analyte == "HGB" and row["status"] == "within":
        context = " HGB nằm trong khoảng đang dùng không tự loại trừ thiếu máu hoặc vấn đề sức khỏe khác; bác sĩ xem kết quả cùng tuổi thai và bối cảnh cụ thể."
    elif analyte in {"MCV", "MCH", "MCHC"} and row["status"] == "below":
        context = (
            " Chỉ số thấp mô tả kích thước hoặc lượng hemoglobin của hồng cầu; kiểu kết quả này có thể gặp trong nhiều nguyên nhân, "
            "chẳng hạn thiếu sắt hoặc bệnh huyết sắc tố, nhưng không phân biệt được nguyên nhân nếu chỉ nhìn CBC."
        )
        sources.append(dict(RBC_INDEX_SOURCE))
    elif analyte in {"RBC", "HCT"}:
        context = (
            " Chỉ số này mô tả số lượng hoặc tỷ lệ hồng cầu; bác sĩ thường xem cùng HGB và các chỉ số hồng cầu khác, "
            "vì một kết quả riêng lẻ không xác định nguyên nhân."
        )
    elif analyte == "WBC":
        context = (
            " WBC cao hoặc thấp không tự xác nhận có nhiễm trùng hay bệnh khác; bác sĩ có thể xem thêm triệu chứng, "
            "các dòng bạch cầu và bối cảnh thai kỳ."
        )
    elif analyte == "PLT":
        context = (
            " Tiểu cầu tham gia đông máu; CBC một mình không giải thích nguyên nhân của kết quả cao hoặc thấp."
        )
    if row["status"] == "within" and "không tự loại trừ" not in context:
        context += " Nằm trong khoảng này không tự loại trừ bệnh và không thay thế đánh giá của bác sĩ."
    output = (
        f"{explanation} Em ghi nhận kết quả {analyte} của anh/chị là {row['value']} {row['unit']}, {status} "
        f"{reference_label} ({row['ref_low']}–{row['ref_high']} {row['unit']}). "
        f"{context} "
        "Trạng thái này chỉ mô tả vị trí của con số so với khoảng đang dùng; không tự kết luận có hay không có bệnh. "
        "Bác sĩ sẽ xem thêm tuổi thai, triệu chứng và thông tin sức khỏe để đánh giá trong bối cảnh cụ thể ạ."
    )
    return {"status": "explained", "analyte": analyte, "output": prefix + output,
            "comparison": row, "sources": sources, **metadata}
