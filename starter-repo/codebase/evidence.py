"""Bounded, source-linked educational notes; no approved personal treatment rules.

These paraphrases were checked against the linked public pages on 2026-11-28.
This is source checking, not clinical validation by a clinician. A general page
does not establish that a recommendation applies to a particular patient.
"""

EDUCATIONAL_EVIDENCE = {
    "lab_results": {
        "title": "MedlinePlus — How to Understand Your Lab Results",
        "url": "https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/",
        "supports": "Ý nghĩa và giới hạn của khoảng tham chiếu; cần xem cùng bối cảnh lâm sàng.",
        "facts": "Kết quả xét nghiệm không cung cấp toàn bộ bức tranh sức khỏe. Trong khoảng tham chiếu không bảo đảm khỏe mạnh; ngoài khoảng không tự xác định bệnh. Cần xem thêm tiền sử, triệu chứng và đánh giá của bác sĩ.",
    },
    "cbc_basics": {
        "title": "MedlinePlus — CBC blood test",
        "url": "https://medlineplus.gov/ency/article/003642.htm",
        "supports": "CBC đo những gì và vai trò của các nhóm tế bào máu.",
        "facts": "CBC đo số lượng hồng cầu, bạch cầu, tiểu cầu, nồng độ hemoglobin và tỷ lệ thể tích hồng cầu. Một kết quả cao hoặc thấp có thể liên quan nhiều nguyên nhân, không chỉ ra nguyên nhân cá nhân.",
    },
    "rbc_indices": {
        "title": "MedlinePlus — Red Blood Cell Indices",
        "url": "https://medlineplus.gov/lab-tests/red-blood-cell-rbc-indices/",
        "supports": "Ý nghĩa MCV, MCH, MCHC và các khả năng chung khi chỉ số hồng cầu thay đổi.",
        "facts": "MCV mô tả kích thước trung bình hồng cầu; MCH là lượng hemoglobin trung bình mỗi hồng cầu; MCHC là nồng độ hemoglobin trong hồng cầu. MCV thấp có thể gặp trong thiếu sắt hoặc bệnh huyết sắc tố; đây chỉ là khả năng chung, không xác nhận nguyên nhân của chị.",
    },
    "hemoglobin_test": {
        "title": "MedlinePlus — Hemoglobin Test",
        "url": "https://medlineplus.gov/lab-tests/hemoglobin-test/",
        "supports": "HGB đo gì; kết quả bất thường chưa tự xác định nguyên nhân.",
        "facts": "HGB đo nồng độ hemoglobin, protein mang oxy trong hồng cầu. Xét nghiệm HGB một mình không cho biết nguyên nhân bất thường. Mất nước là một khả năng chung khi HGB cao, không phải nguyên nhân đã xác định cho người dùng. Không dùng HGB để tự suy ra cần kiêng sắt hay thay đổi thuốc.",
    },
    "pregnancy_nutrition": {
        "title": "NHS — Pregnancy vitamins and supplements",
        "url": "https://www.nhs.uk/pregnancy/keeping-well/pregnancy-vitamins-and-supplements/",
        "supports": "Thông tin dinh dưỡng thai kỳ nói chung; không chứng minh một chế độ ăn riêng cho HGB cao.",
        "facts": "Chế độ ăn đa dạng trong thai kỳ giúp cung cấp nhiều vitamin và khoáng chất. Việc bổ sung sắt cần được chuyên môn đánh giá. Nguồn này không đưa ra chế độ ăn hay hướng dẫn hạn chế sắt dành riêng cho người có HGB hoặc RBC cao.",
    },
    "iron_stores": {
        "title": "MedlinePlus — Ferritin Blood Test",
        "url": "https://medlineplus.gov/lab-tests/ferritin-blood-test/",
        "supports": "Ferritin liên quan dự trữ sắt; CBC và HGB không thay cho đánh giá dự trữ sắt.",
        "facts": "Ferritin là protein dự trữ sắt. Xét nghiệm ferritin giúp bác sĩ đánh giá lượng sắt dự trữ nhưng cũng cần diễn giải theo bối cảnh. Đây là thông tin chung, không phải chỉ định chị phải làm xét nghiệm hay thay đổi lượng sắt.",
    },
}


def approved_evidence(comparison, *, include_nutrition=False):
    keys = ["lab_results", "cbc_basics", "rbc_indices", "hemoglobin_test", "iron_stores"]
    if include_nutrition:
        keys.append("pregnancy_nutrition")
    evidence = {key: dict(EDUCATIONAL_EVIDENCE[key]) for key in keys}
    if comparison["reference_mode"] == "study":
        evidence["study_interval"] = {
            **comparison["reference_source"],
            "supports": "Khoảng đối chiếu nghiên cứu theo giai đoạn thai kỳ, không phải ngưỡng chẩn đoán.",
            "facts": "report_facts được đối chiếu với khoảng nghiên cứu Pham và cộng sự. Chỉ dùng nguồn này để giải thích vị trí so với khoảng; không suy ra không thiếu máu hoặc mẹ/bé an toàn.",
        }
    return evidence


def source_for_display(entry):
    return {key: entry[key] for key in ("title", "url", "supports") if key in entry}
