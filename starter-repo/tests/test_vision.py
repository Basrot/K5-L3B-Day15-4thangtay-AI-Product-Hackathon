import base64
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codebase"))

import ai
import vision


def image_bytes(fmt="PNG", size=(16, 12)):
    output = io.BytesIO()
    Image.new("RGB", size, "white").save(output, format=fmt)
    return output.getvalue()


def row(**changes):
    return {"analyte": "HGB", "value": "108", "unit": "g/L",
            "ref_low": None, "ref_high": None, "ref_unit": None, **changes}


class VisionTest(unittest.TestCase):
    def extract(self, payload):
        with patch.object(ai, "MODEL_PROVIDER", "ollama"), patch.object(
                vision, "call_model", return_value={"text": json.dumps(payload), "model": "gemma3:4b"}):
            return vision.extract_report(image_bytes(), "image/png")

    def test_preserves_printed_data_and_missing_reference_without_guessing(self):
        result = self.extract({"rows": [row()], "warnings": []})
        self.assertEqual(result["rows"], [{"analyte": "HGB", "value": "108", "unit": "g/L",
                                            "ref_low": None, "ref_high": None, "ref_unit": None}])
        self.assertIsInstance(result["warnings"], list)

    def test_only_the_supported_eight_codes_can_be_extracted(self):
        codes = "HGB RBC HCT MCV MCH MCHC WBC PLT".split()
        result = self.extract({"rows": [row(analyte=code) for code in codes], "warnings": []})
        self.assertEqual([item["analyte"] for item in result["rows"]], codes)

    def test_unsupported_code_is_omitted_with_warning(self):
        result = self.extract({"rows": [row(), row(analyte="RDW")], "warnings": []})
        self.assertEqual([item["analyte"] for item in result["rows"]], ["HGB"])
        self.assertTrue(result["warnings"])

    def test_identical_duplicate_rows_and_hb_alias_are_merged(self):
        result = self.extract({"rows": [row(analyte="Hb"), row(value="108.0")], "warnings": []})
        self.assertEqual(len(result["rows"]), 1)
        self.assertEqual(result["rows"][0]["analyte"], "HGB")
        self.assertEqual(result["rows"][0]["value"], "108")

    def test_conflicting_duplicate_rows_are_not_arbitrarily_selected(self):
        result = self.extract({"rows": [row(), row(value="120"), row(analyte="RBC")], "warnings": []})
        self.assertEqual([item["analyte"] for item in result["rows"]], ["RBC"])
        self.assertTrue(any("HGB" in warning and "để trống" in warning for warning in result["warnings"]))

    def test_image_bytes_and_vision_model_reach_central_model_boundary(self):
        source = image_bytes("JPEG")
        captured = {}

        def respond(system, user, **kwargs):
            captured.update(kwargs)
            return {"text": '{"rows":[],"warnings":["Không đọc rõ ảnh"]}', "model": "vision-local"}

        with patch.object(ai, "MODEL_PROVIDER", "ollama"), patch.dict("os.environ", {"VISION_MODEL": "vision-local"}), patch.object(vision, "call_model", side_effect=respond):
            result = vision.extract_report(source, "image/jpeg")
        self.assertEqual(captured["images"], [source])
        self.assertEqual(captured["model_name"], "vision-local")
        self.assertGreaterEqual(captured["max_tokens"], 3000)
        self.assertEqual(result["rows"], [])
        self.assertIn("Không đọc rõ ảnh", result["warnings"])

    def test_fake_mode_fails_explicitly(self):
        with patch.object(ai, "MODEL_PROVIDER", "fake"):
            with self.assertRaisesRegex(RuntimeError, "ollama"):
                vision.extract_report(image_bytes(), "image/png")

    def test_invalid_image_or_mime_is_rejected_before_model_call(self):
        for source, mime in [(b"not an image", "image/png"), (image_bytes(), "image/jpeg"),
                             (image_bytes(), "application/pdf"), (b"x" * (10 * 1024 * 1024 + 1), "image/png")]:
            with self.subTest(mime=mime, length=len(source)), patch.object(vision, "call_model", side_effect=AssertionError("model should not run")):
                with self.assertRaises(ValueError):
                    vision.extract_report(source, mime)

    def test_large_pixel_count_is_rejected(self):
        with patch.object(vision, "call_model", side_effect=AssertionError("model should not run")):
            with self.assertRaises(ValueError):
                vision.extract_report(image_bytes(size=(5000, 4001)), "image/png")

    def test_malformed_model_output_is_rejected(self):
        invalid = [None, {"rows": "bad", "warnings": []}, {"rows": [row(analyte={})], "warnings": []},
                   {"rows": [row(value=True)], "warnings": []},
                   {"rows": [row(value={"value": 1})], "warnings": []},
                   {"rows": [row(value=float("nan"))], "warnings": []},
                   {"rows": [row(unit=12)], "warnings": []}, {"rows": [row()], "warnings": "bad"},
                   {"rows": [row()] * 25, "warnings": []}]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(RuntimeError):
                self.extract(payload)

    def test_non_json_model_output_is_rejected(self):
        with patch.object(ai, "MODEL_PROVIDER", "ollama"), patch.object(vision, "call_model", return_value={"text": "unreadable"}):
            with self.assertRaises(RuntimeError):
                vision.extract_report(image_bytes(), "image/png")


class OllamaImagesTest(unittest.TestCase):
    def test_serializes_image_bytes_and_preserves_measured_usage(self):
        captured = {}

        def respond(request, timeout):
            captured.update(json.loads(request.data))
            return io.BytesIO(json.dumps({"model": "vision-local", "message": {"content": "{}"},
                                          "prompt_eval_count": 510, "eval_count": 250}).encode())

        with patch.object(ai, "MODEL_PROVIDER", "ollama"), patch.object(ai, "MODEL_NAME", "text-local"), patch.object(ai, "urlopen", side_effect=respond):
            result = ai.call_model("system", "read", images=[b"image-bytes"], model_name="vision-local", max_tokens=3500)
        self.assertEqual(captured["messages"][1]["images"], [base64.b64encode(b"image-bytes").decode("ascii")])
        self.assertEqual(captured["model"], "vision-local")
        self.assertEqual(captured["options"]["num_predict"], 3500)
        self.assertEqual((result["tokens_in"], result["tokens_out"]), (510, 250))

    def test_existing_fake_text_contract_is_preserved(self):
        with patch.object(ai, "MODEL_PROVIDER", "fake"):
            result = ai.call_model("system", "hello")
        self.assertEqual((result["model"], result["tokens_in"], result["tokens_out"]), ("fake", 0, 0))
        self.assertIn("hello", result["text"])


if __name__ == "__main__":
    unittest.main()
