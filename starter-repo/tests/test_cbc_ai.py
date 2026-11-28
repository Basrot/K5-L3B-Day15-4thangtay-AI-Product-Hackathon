import io
import json
import sys
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codebase"))

import agent
import tools


def report(**changes):
    return {
        "pregnancy_status": "pregnant",
        "adult_confirmed": True,
        "gestational_age": "21w3d",
        "rows": [
            {"analyte": "HGB", "value": "108", "unit": "g/L",
             "ref_low": "11,0", "ref_high": "14", "ref_unit": "g/dL"},
            {"analyte": "WBC", "value": "6", "unit": "10⁹/L",
             "ref_low": "6", "ref_high": "15", "ref_unit": "10^9/L"},
        ],
        **changes,
    }


def question(text, **changes):
    return json.dumps({"report": report(**changes), "question": text}, ensure_ascii=False)


class CBCWorkflowTest(unittest.TestCase):
    def test_uses_lab_range_and_includes_its_boundaries(self):
        comparison = tools.compare_cbc(report())
        self.assertEqual(comparison["status"], "ok")
        first, second = comparison["rows"]
        self.assertEqual((first["value"], first["status"]), ("10.8", "below"))
        self.assertEqual(second["status"], "within")

    def test_missing_unit_prevents_a_model_call(self):
        rows = report()["rows"]
        rows[0]["unit"] = None
        with patch.object(agent, "call_model", side_effect=AssertionError("unexpected model call")):
            result = agent.answer(question("HGB thế nào?", rows=rows))
        self.assertEqual(result["status"], "needs_input")
        self.assertIn("đơn vị", result["output"])

    def test_out_of_scope_and_missing_age_have_distinct_statuses(self):
        with patch.object(agent, "call_model", side_effect=AssertionError("unexpected model call")):
            outside = agent.answer(question("HGB thế nào?", pregnancy_status="not_pregnant"))
            missing = agent.answer(question("HGB thế nào?", gestational_age=None))
        self.assertEqual(outside["status"], "out_of_scope")
        self.assertEqual(missing["status"], "needs_input")

    def test_invalid_numbers_and_incompatible_units_are_rejected(self):
        for changes in ({"value": "NaN"}, {"value": "1,2.3"}, {"unit": "%"},
                        {"ref_low": "15"}, {"value": True}):
            with self.subTest(changes=changes):
                row = {**report()["rows"][0], **changes}
                self.assertEqual(tools.compare_cbc(report(rows=[row]))["status"], "needs_input")

    def test_ambiguous_cell_count_unit_requires_confirmation(self):
        wbc = {**report()["rows"][1], "unit": "10e9/L"}
        self.assertEqual(tools.compare_cbc(report(rows=[wbc]))["status"], "needs_input")

    def test_model_selects_row_and_explanation_uses_comparison_data(self):
        model_reply = {"text": json.dumps({
            "answer": "HGB là huyết sắc tố giúp vận chuyển oxy; bác sĩ xem kết quả trong bối cảnh thai kỳ.",
            "analytes": ["HGB"], "needs_clarification": False, "evidence_ids": ["lab_results"],
        }, ensure_ascii=False)}
        with patch.object(agent, "call_model", return_value=model_reply):
            result = agent.answer(question("Tại sao huyết sắc tố có dấu L?"))
        self.assertEqual((result["status"], result["analyte"]), ("explained", "HGB"))
        self.assertIn("vận chuyển oxy", result["output"])
        self.assertEqual(result["verified_facts"][0]["value"], "10.8")
        self.assertEqual((result["verified_facts"][0]["ref_low"], result["verified_facts"][0]["ref_high"]),
                         ("11", "14"))

    def test_unknown_model_analyte_or_free_text_is_not_rendered(self):
        for decision in ('{"intent":"explain","analyte":"RBC"}',
                         '{"intent":"explain","analyte":"HGB","extra":"take medicine"}',
                         'Hãy uống thuốc.'):
            with self.subTest(decision=decision):
                with patch.object(agent, "call_model", return_value={"text": decision}):
                    result = agent.answer(question("Tôi muốn hỏi về chỉ số."))
                self.assertEqual(result["status"], "clarify_question")
                self.assertNotIn("uống thuốc", result["output"])

    def test_model_can_route_a_diagnosis_request_to_medical_staff(self):
        with patch.object(agent, "call_model", return_value={"text": '{"intent":"medical_advice"}'}):
            result = agent.answer(question("Tôi bị bệnh gì và nên uống gì?"))
        self.assertEqual(result["status"], "medical_advice")
        self.assertIn("bác sĩ", result["output"])

    def test_fake_mode_labels_its_output(self):
        with patch.object(agent, "call_model", return_value={"text": "", "model": "fake"}):
            result = agent.answer(question("Vì sao HGB có dấu L?"))
        self.assertEqual(result["status"], "explained")
        self.assertIn("[AI giả]", result["output"])

    def test_explanation_returns_comparison_and_source_for_ui(self):
        with patch.object(agent, "call_model", return_value={"text": "", "model": "fake"}):
            result = agent.answer(question("WBC của em như thế nào?"))
        self.assertEqual(result["comparison"]["status"], "within")
        self.assertTrue(result["sources"][0]["url"].startswith("https://medlineplus.gov/"))
        self.assertIn("bác sĩ", result["output"])

    def test_supported_report_with_missing_optional_reference_unit_is_incomplete(self):
        row = report()["rows"][0].copy()
        row.pop("ref_unit")
        self.assertEqual(tools.compare_cbc(report(rows=[row]))["status"], "needs_input")

    def test_urgent_question_takes_priority_over_missing_report(self):
        with patch.object(agent, "call_model", side_effect=AssertionError("unexpected model call")):
            result = agent.answer(json.dumps({"question": "Tôi đang cần cấp cứu."}))
        self.assertEqual(result["status"], "urgent")

    def test_fake_mode_routes_medication_question_away_from_explanation(self):
        with patch.object(agent, "call_model", return_value={"text": "", "model": "fake"}):
            result = agent.answer(question("HGB thấp thì uống thuốc gì?"))
        self.assertEqual(result["status"], "medical_advice")

    def test_model_can_select_only_rows_on_the_confirmed_report(self):
        def respond(_system, user, *, output_schema, **_kwargs):
            self.assertEqual(output_schema["properties"]["analytes"]["items"]["enum"], ["HGB", "WBC"])
            self.assertNotIn("ref_low", user)
            return {"text": json.dumps({
                "answer": "HGB là dòng được hỏi và cần được hiểu theo khoảng đã xác nhận.",
                "analytes": ["HGB"], "needs_clarification": False, "evidence_ids": ["lab_results"],
            }, ensure_ascii=False)}

        with patch.object(agent, "call_model", side_effect=respond):
            result = agent.answer(question("Vì sao dấu L đứng cạnh huyết sắc tố?"))
        self.assertEqual(result["analyte"], "HGB")
        self.assertEqual(result["status"], "explained")


class SpeechTest(unittest.TestCase):
    def test_passes_normalized_wav_samples_into_the_recognizer(self):
        import speech

        class Recognizer:
            def create_stream(self):
                return SimpleNamespace(accept_waveform=self.accept_waveform)

            def accept_waveform(self, sample_rate, samples):
                self.input = (sample_rate, samples)

            def decode_stream(self, stream):
                stream.result = SimpleNamespace(text=" huyết sắc tố ")

        recognizer = Recognizer()
        out = io.BytesIO()
        with wave.open(out, "wb") as recording:
            recording.setparams((1, 2, 16000, 0, "NONE", ""))
            recording.writeframes(bytes.fromhex("0080 0000 0040"))
        with patch.dict("os.environ", {"ZIPFORMER_MODEL_DIR": "unused-model", "ZIPFORMER_BACKEND": "sherpa"}):
            with patch.object(speech, "_recognizer", return_value=recognizer):
                self.assertEqual(speech.transcribe_wav(out.getvalue()), "huyết sắc tố")
        self.assertEqual(recognizer.input, (16000, [-1.0, 0.0, 0.5]))

    def test_non_wav_is_rejected_before_loading_a_model(self):
        from speech import transcribe_wav

        with self.assertRaisesRegex(ValueError, "WAV"):
            transcribe_wav(b"not a WAV")

    def test_silent_wav_returns_empty_transcript(self):
        from speech import transcribe_wav

        out = io.BytesIO()
        with wave.open(out, "wb") as recording:
            recording.setparams((1, 2, 16000, 0, "NONE", ""))
            recording.writeframes(b"\0\0" * 1600)
        self.assertEqual(transcribe_wav(out.getvalue()), "")


if __name__ == "__main__":
    unittest.main()
