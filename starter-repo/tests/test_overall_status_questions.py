import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codebase"))

import agent


def report(hgb="12", hgb_low="11", hgb_high="14", wbc="8"):
    return {
        "pregnancy_status": "pregnant",
        "adult_confirmed": True,
        "gestational_age": "24w2d",
        "rows": [
            {"analyte": "HGB", "value": hgb, "unit": "g/dL",
             "ref_low": hgb_low, "ref_high": hgb_high, "ref_unit": "g/dL"},
            {"analyte": "WBC", "value": wbc, "unit": "10^9/L",
             "ref_low": "4", "ref_high": "10", "ref_unit": "10^9/L"},
        ],
    }


def ask(text, report_data=None, history=None):
    return agent.answer(json.dumps({
        "report": report_data or report(), "question": text,
    }, ensure_ascii=False), history=history)


class ConversationalStatusQuestionTest(unittest.TestCase):
    def test_reference_concept_answer_with_negated_diagnosis_passes(self):
        text = "Trong khoảng tham chiếu nghĩa là kết quả nằm giữa giới hạn dưới và trên đang dùng để đối chiếu. Đây không phải là chẩn đoán và không khẳng định chị hoàn toàn khỏe mạnh."
        with patch.object(agent, "call_model", return_value={"text": json.dumps({
            "answer": text, "analytes": [], "needs_clarification": False,
        })}):
            result = ask("Thế nào là trong khoảng tham chiếu?")
        self.assertEqual(result["status"], "explained")
        self.assertEqual(result["output"], text)

    def test_rejected_numeric_explanation_gets_one_checked_rephrase(self):
        replies = [{"text": json.dumps({"answer": text, "analytes": [], "needs_clarification": False})}
                   for text in ("Khoảng tham chiếu chứa 95% kết quả của quần thể.",
                                "Đó là khoảng dùng để so sánh kết quả với các giới hạn tham chiếu, không tự khẳng định sức khỏe.")]
        with patch.object(agent, "call_model", side_effect=replies) as model:
            result = ask("Thế nào là trong khoảng tham chiếu?")
        self.assertEqual(model.call_count, 2)
        self.assertEqual(result["status"], "explained")
        self.assertIn("Đó là khoảng", result["output"])

    def test_safe_diagnostic_disclaimer_is_not_treated_as_a_diagnosis(self):
        for text in (
            "RBC phản ánh số lượng hồng cầu. Kết quả nằm trong khoảng tham chiếu, nhưng không thể chẩn đoán sức khỏe chỉ từ riêng chỉ số này.",
            "RBC nằm trong khoảng đang dùng. Điều này không thay thế chẩn đoán của bác sĩ.",
            "Khoảng tham chiếu không phải là ngưỡng chẩn đoán bệnh.",
            "Kết quả này chỉ dùng để đối chiếu, không có giá trị chẩn đoán bệnh riêng lẻ.",
            "RBC nằm trong khoảng nghiên cứu; bác sĩ cần thêm thông tin để chẩn đoán.",
        ):
            with self.subTest(text=text), patch.object(agent, "call_model", return_value={
                "text": json.dumps({"answer": text, "analytes": ["HGB"], "needs_clarification": False})
            }):
                result = ask("Giải thích kết quả nhé")
            self.assertEqual(result["status"], "explained")
            self.assertEqual(result["output"], text)

    def test_disclaimer_does_not_hide_a_following_diagnosis_or_drug_advice(self):
        for text in (
            "Em không thể chẩn đoán. Chị bị thiếu máu.",
            "Điều này không thay thế chẩn đoán của bác sĩ. Chị nên uống thuốc sắt.",
            "Chị bị thiếu máu.",
            "Em chẩn đoán thiếu máu.",
            "Chẩn đoán: thiếu máu.",
            "WBC nằm trong khoảng nên không có dấu hiệu viêm hoặc nhiễm trùng rõ ràng.",
            "Kết quả HGB là 99.",
        ):
            with self.subTest(text=text), patch.object(agent, "call_model", return_value={
                "text": json.dumps({"answer": text, "analytes": ["HGB"], "needs_clarification": False})
            }):
                self.assertEqual(ask("Giải thích kết quả nhé")["status"], "clarify_question")

    def test_chat_context_omits_long_reference_notice_and_limits_history(self):
        history = [{"question": "HGB?", "output": "Giải thích ngắn."} for _ in range(8)]

        def respond(system, user, **kwargs):
            context = json.loads(user)
            self.assertNotIn("reference_note", context["reference_context"])
            self.assertEqual(len(context["recent_conversation"]), 4)
            self.assertLess(len(system), 3000)
            self.assertLessEqual(kwargs["max_tokens"], 800)
            return {"text": json.dumps({"answer": "Em sẽ giải thích tiếp về HGB.",
                                       "analytes": ["HGB"], "needs_clarification": False})}

        with patch.object(agent, "call_model", side_effect=respond):
            self.assertEqual(ask("Giải thích thêm nhé", history=history)["status"], "explained")

    def test_named_analyte_status_is_generated_and_facts_remain_server_verified(self):
        def respond(_system, user, *, output_schema, **_kwargs):
            context = json.loads(user)
            hgb = next(row for row in context["report_facts"] if row["analyte"] == "HGB")
            self.assertEqual(hgb["status"], "below")
            self.assertEqual(hgb["value"], "9.5")
            self.assertEqual(output_schema["properties"]["answer"]["maxLength"], 4000)
            return {"text": json.dumps({
                "answer": "Phiếu cho thấy HGB đang thấp hơn khoảng đã chọn. Điều này là một dấu hiệu để bác sĩ cân nhắc thêm, nhưng riêng kết quả này chưa cho biết nguyên nhân.",
                "analytes": ["HGB"], "needs_clarification": False,
            }, ensure_ascii=False)}

        with patch.object(agent, "call_model", side_effect=respond) as model:
            result = ask("HGB của tôi có ổn không", report(hgb="9.5"))

        self.assertEqual(model.call_count, 1)
        self.assertEqual(result["status"], "explained")
        self.assertIn("Điều này là một dấu hiệu", result["output"])
        self.assertEqual(result["verified_facts"][0]["value"], "9.5")
        self.assertEqual(result["verified_facts"][0]["status"], "below")

    def test_brief_whole_report_question_uses_generated_answer_not_a_fixed_template(self):
        def respond(_system, user, **_kwargs):
            context = json.loads(user)
            self.assertEqual(context["question"], "ổn k")
            return {"text": json.dumps({
                "answer": "Em đã xem các dòng trên phiếu: hiện chúng nằm trong khoảng đang đối chiếu. Đây chỉ là so sánh với khoảng tham chiếu, không thể khẳng định sức khỏe hoàn toàn bình thường; nếu chị đang có triệu chứng thì nên trao đổi với bác sĩ.",
                "analytes": ["HGB", "WBC"], "needs_clarification": False,
            }, ensure_ascii=False)}

        with patch.object(agent, "call_model", side_effect=respond) as model:
            result = ask("ổn k")

        self.assertEqual(model.call_count, 1)
        self.assertEqual(result["status"], "explained")
        self.assertIn("Em đã xem các dòng", result["output"])
        self.assertEqual([fact["analyte"] for fact in result["verified_facts"]], ["HGB", "WBC"])

    def test_follow_up_uses_recent_turn_to_resolve_implicit_hgb_reference(self):
        history = [{
            "question": "HGB của tôi có ổn không?",
            "output": "HGB đang thấp hơn khoảng tham chiếu đã xác nhận.",
        }]

        def respond(_system, user, **_kwargs):
            context = json.loads(user)
            self.assertEqual(context["recent_conversation"], [{
                "question": history[0]["question"], "answer": history[0]["output"],
            }])
            return {"text": json.dumps({
                "answer": "Có nhiều khả năng bác sĩ sẽ cân nhắc khi HGB thấp, chẳng hạn tình trạng thiếu sắt hoặc các nguyên nhân khác. Riêng CBC chưa phân biệt được lý do; bác sĩ sẽ xem thêm triệu chứng và xét nghiệm liên quan.",
                "analytes": ["HGB"], "needs_clarification": False,
            }, ensure_ascii=False)}

        with patch.object(agent, "call_model", side_effect=respond) as model:
            result = ask("vậy thấp thì có thể do đâu?", report(hgb="9.5"), history)

        self.assertEqual(model.call_count, 1)
        self.assertEqual(result["status"], "explained")
        self.assertIn("thiếu sắt", result["output"])
        self.assertEqual(result["analyte"], "HGB")


if __name__ == "__main__":
    unittest.main()
