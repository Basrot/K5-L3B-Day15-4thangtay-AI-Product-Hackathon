import io
import json
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase import ai, vision


def pdf_bytes(pages=1):
    output = io.BytesIO()
    images = [Image.new("RGB", (300, 400), "white") for _ in range(pages)]
    images[0].save(output, format="PDF", save_all=True, append_images=images[1:])
    return output.getvalue()


class DocumentTest(unittest.TestCase):
    def test_failed_extraction_has_a_specific_safe_error_instead_of_provider_outage(self):
        from codebase.api import _upstream_error_detail
        with self.assertRaises(RuntimeError) as caught:
            vision._validate_result({"rows": [{"analyte": "secret-patient-name"}], "warnings": []})
        message = _upstream_error_detail("/v1/reports/extract", caught.exception)
        self.assertNotIn("chưa phản hồi", message)
        self.assertNotIn("secret-patient-name", message)
        self.assertIn("đọc", message.lower())

    def test_pdf_pages_are_rendered_and_sent_in_one_vision_call(self):
        with patch.object(ai, "MODEL_PROVIDER", "openai_compatible"), patch.dict(
                "os.environ", {"VISION_MODEL": "gpt-4.1-mini"}), patch.object(
                vision, "call_model", return_value={"text": json.dumps({"rows": [], "warnings": []}),
                                                    "model": "gpt-4.1-mini"}) as model:
            result = vision.extract_document(pdf_bytes(2), "application/pdf")
        self.assertEqual(model.call_count, 1)
        self.assertEqual(len(model.call_args.kwargs["images"]), 2)
        for page in model.call_args.kwargs["images"]:
            with Image.open(io.BytesIO(page)) as image:
                self.assertLessEqual(max(image.size), 2000)
        self.assertEqual(result["rows"], [])

    def test_pdf_limits_and_invalid_bytes_stop_before_model_call(self):
        for source in (b"not-pdf", b"%PDF-broken", pdf_bytes(4)):
            with self.subTest(length=len(source)), patch.object(vision, "call_model") as model:
                with self.assertRaises(ValueError):
                    vision.extract_document(source, "application/pdf")
                model.assert_not_called()

    def test_images_keep_the_existing_validation_and_extraction(self):
        with patch.object(vision, "extract_report", return_value={"rows": [], "warnings": []}) as extract:
            vision.extract_document(b"png", "image/png")
        extract.assert_called_once_with(b"png", "image/png")

    def test_openai_vision_uses_the_chat_model_if_no_separate_model_is_set(self):
        output = io.BytesIO()
        Image.new("RGB", (10, 10), "white").save(output, format="PNG")
        with patch.object(ai, "MODEL_PROVIDER", "openai_compatible"), patch.object(
                ai, "MODEL_NAME", "gpt-4.1-mini"), patch.dict("os.environ", {"VISION_MODEL": ""}), patch.object(
                vision, "call_model", return_value={"text": '{"rows":[],"warnings":[]}'}) as model:
            vision.extract_report(output.getvalue(), "image/png")
        self.assertEqual(model.call_args.kwargs["model_name"], "gpt-4.1-mini")
