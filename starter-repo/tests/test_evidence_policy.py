import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codebase"))
import agent


def ask(question):
    return agent.answer(json.dumps({"report": {
        "pregnancy_status": "pregnant", "adult_confirmed": True,
        "gestational_age": "24w2d", "reference_mode": "study",
        "rows": [{"analyte": "HGB", "value": "17.2", "unit": "g/dL"}],
    }, "question": question}, ensure_ascii=False))


class EvidencePolicyTest(unittest.TestCase):
    def test_a_valid_source_id_does_not_authorize_personal_treatment_advice(self):
        for text in ("Chị nên uống nhiều nước để hạ HGB.", "Uống đủ nước mỗi ngày để hạ HGB.",
                     "Hạn chế các thực phẩm nhiều muối để sửa kết quả HGB."):
            with self.subTest(text=text), patch.object(agent, "call_model", return_value={"text": json.dumps({
                "answer": text, "analytes": ["HGB"],
                "needs_clarification": False, "evidence_ids": ["hemoglobin_test"],
            })}):
                result = ask("HGB cao có ý nghĩa gì?")
            self.assertEqual(result["status"], "clarify_question")
            self.assertIn("chưa có đủ bằng chứng", result["output"])
            self.assertNotEqual(result["output"], text)

    def test_personal_diet_recommendation_is_withheld_warmly_without_generation(self):
        for question in ("HGB của tôi cao thì tôi nên ăn gì và uống bao nhiêu nước?",
                         "Em có nên uống thêm nước không?", "Chế độ ăn nào phù hợp với phiếu này?"):
            with self.subTest(question=question), patch.object(agent, "call_model", side_effect=AssertionError("no audited personal advice rule")):
                result = ask(question)
            self.assertEqual(result["status"], "medical_advice")
            self.assertIn("chưa có đủ bằng chứng", result["output"])
            self.assertIn("Em hiểu", result["output"])
            self.assertIn("bác sĩ trực tiếp", result["output"])
            self.assertEqual(result["evidence_status"], "insufficient_for_personal_advice")

    def test_missing_evidence_or_invented_source_cannot_support_generated_explanation(self):
        for extra in ({}, {"evidence_ids": ["imaginary_clinical_guideline"]}, {"evidence_ids": []}):
            with self.subTest(extra=extra), patch.object(agent, "call_model", return_value={"text": json.dumps({
                "answer": "Giải thích không có nguồn được kiểm tra.", "analytes": ["HGB"],
                "needs_clarification": False, **extra,
            })}):
                result = ask("HGB là gì?")
            self.assertEqual(result["status"], "clarify_question")
            self.assertNotIn("Giải thích không có nguồn", result["output"])

    def test_known_education_source_is_attached_with_its_scope(self):
        with patch.object(agent, "call_model", return_value={"text": json.dumps({
            "answer": "HGB đo nồng độ huyết sắc tố trong máu; xét nghiệm này một mình chưa xác định nguyên nhân thay đổi.",
            "analytes": ["HGB"], "needs_clarification": False, "evidence_ids": ["hemoglobin_test"],
        })}):
            result = ask("HGB là gì?")
        self.assertEqual(result["status"], "explained")
        self.assertTrue(any(source["url"].endswith("/hemoglobin-test/") and source.get("supports")
                            for source in result["sources"]))
