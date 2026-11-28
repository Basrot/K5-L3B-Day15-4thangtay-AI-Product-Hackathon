import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase import ai


class CloudModelTest(unittest.TestCase):
    def test_vision_can_require_strict_structured_output(self):
        captured = {}
        def post(request, timeout):
            captured.update(json.loads(request.data))
            return io.BytesIO(json.dumps({"choices": [{"message": {"content": "{}"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 2}}).encode())
        with patch.object(ai, "MODEL_PROVIDER", "openai_compatible"), patch.dict("os.environ", {
            "API_KEY": "test-key", "LLM_API_BASE": "https://api.openai.com/v1",
        }), patch.object(ai, "urlopen", side_effect=post):
            ai.call_model("system", "read", model_name="gpt-4.1-mini", images=[b"image"],
                          output_schema={"type": "object"}, strict_schema=True)
        self.assertTrue(captured["response_format"]["json_schema"]["strict"])

    def test_image_calls_use_vision_endpoint_and_accounting_from_api(self):
        received = []

        def post(request, timeout):
            received.append((request, json.loads(request.data)))
            return io.BytesIO(json.dumps({
                "model": "vision-test",
                "choices": [{"message": {"content": '{"rows":[],"warnings":[]}'}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 5},
            }).encode())

        with patch.object(ai, "MODEL_PROVIDER", "openai_compatible"):
            with patch.dict("os.environ", {
                "API_KEY": "text-key", "LLM_API_BASE": "https://text.example/v1",
                "VISION_API_BASE": "https://vision.example/v1", "VISION_API_KEY": "vision-key",
            }):
                with patch.object(ai, "urlopen", side_effect=post):
                    reply = ai.call_model("system", "read", images=[b"image"], model_name="vision-test",
                                          output_schema={"type": "object"}, max_tokens=100)
        request, body = received[0]
        self.assertEqual(request.full_url, "https://vision.example/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer vision-key")
        self.assertEqual(body["messages"][1]["content"][1]["image_url"]["url"],
                         "data:image/jpeg;base64,aW1hZ2U=")
        self.assertNotIn("think", body)
        self.assertEqual((reply["tokens_in"], reply["tokens_out"]), (12, 5))

    def test_missing_api_key_fails_before_any_request(self):
        with patch.object(ai, "MODEL_PROVIDER", "openai_compatible"):
            with patch.dict("os.environ", {"API_KEY": ""}):
                with patch.object(ai, "urlopen", side_effect=AssertionError("unexpected HTTP")):
                    with self.assertRaisesRegex(RuntimeError, "API_KEY"):
                        ai.call_model("s", "u", model_name="test")

    def test_new_vision_provider_requires_its_own_key(self):
        with patch.object(ai, "MODEL_PROVIDER", "openai_compatible"):
            with patch.dict("os.environ", {"API_KEY": "text-key", "VISION_API_KEY": "",
                                          "LLM_API_BASE": "https://text.example/v1",
                                          "VISION_API_BASE": "https://other.example/v1"}):
                with patch.object(ai, "urlopen", side_effect=AssertionError("key leaked")):
                    with self.assertRaisesRegex(RuntimeError, "VISION_API_KEY"):
                        ai.call_model("s", "u", images=[b"image"], model_name="test")
