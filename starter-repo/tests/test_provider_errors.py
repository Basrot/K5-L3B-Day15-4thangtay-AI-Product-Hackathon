import io
import json
import sys
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase import ai, speech, tts


class ProviderErrorTest(unittest.TestCase):
    def test_ai_invalid_configuration_is_runtime_error(self):
        for base in ("http://unsafe.example/v1", "https://example.com:bad/v1"):
            with self.subTest(base=base), patch.object(ai, "MODEL_PROVIDER", "openai_compatible"), patch.object(ai, "MODEL_NAME", "test"), patch.dict("os.environ", {"LLM_API_BASE": base, "API_KEY": "secret"}):
                with self.assertRaises(RuntimeError):
                    ai.call_model("system", "hello")

    def test_ai_malformed_json_and_transport_are_runtime_errors_without_secrets(self):
        for result in (io.BytesIO(b"invalid secret-json"), OSError("secret-network")):
            with self.subTest(result=type(result).__name__), patch.object(ai, "MODEL_PROVIDER", "ollama"), patch.object(ai, "MODEL_NAME", "test"):
                kwargs = {"side_effect": result} if isinstance(result, Exception) else {"return_value": result}
                with patch.object(ai, "urlopen", **kwargs), self.assertRaises(RuntimeError) as caught:
                    ai.call_model("system", "hello")
                self.assertNotIn("secret", str(caught.exception))

    def test_ai_invalid_upstream_usage_is_runtime_error(self):
        payload = {"message": {"content": "{}"}, "prompt_eval_count": True, "eval_count": -1}
        with patch.object(ai, "MODEL_PROVIDER", "ollama"), patch.object(ai, "MODEL_NAME", "test"), patch.object(ai, "urlopen", return_value=io.BytesIO(json.dumps(payload).encode())):
            with self.assertRaises(RuntimeError):
                ai.call_model("system", "hello")

    def test_speech_invalid_backend_is_runtime_error_for_valid_audio(self):
        output = io.BytesIO()
        with wave.open(output, "wb") as recording:
            recording.setparams((1, 2, 16000, 0, "NONE", ""))
            recording.writeframes(b"\x01\x00" * 160)
        with patch.dict("os.environ", {"ZIPFORMER_MODEL_DIR": "unused", "ZIPFORMER_BACKEND": "unknown"}):
            with self.assertRaises(RuntimeError):
                speech.transcribe_wav(output.getvalue())

    def test_local_tts_loading_failure_is_runtime_error(self):
        with patch.dict("os.environ", {"VIENEU_TTS_BACKEND": "local"}), patch.object(tts, "_engine", side_effect=ImportError("secret-local-config")):
            with self.assertRaises(RuntimeError) as caught:
                tts.synthesize_wav("Xin chào.")
        self.assertNotIn("secret", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
