import io
import json
import os
import sys
import unittest
import wave
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase import tts


def wav_bytes(frames=240):
    output = io.BytesIO()
    with wave.open(output, "wb") as recording:
        recording.setparams((1, 2, 24000, 0, "NONE", ""))
        recording.writeframes(b"\x00\x00" * frames)
    return output.getvalue()


class Response(io.BytesIO):
    def __init__(self, data, content_type="audio/wav"):
        super().__init__(data)
        self.headers = {"Content-Type": content_type}


class TTSAPITest(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"VIENEU_TTS_BACKEND": "api", "VIENEU_API_KEY": "test-secret",
                                                 "VIENEU_MODEL": "vieneu-v4", "VIENEU_VOICE": "confirmed-voice-id"})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_official_https_request_has_auth_voice_model_and_spoken_text(self):
        expected = wav_bytes()
        captured = {}

        def respond(request, timeout):
            captured.update(url=request.full_url, method=request.method, headers=dict(request.header_items()),
                            body=json.loads(request.data), timeout=timeout)
            return Response(expected)

        with patch.object(tts, "urlopen", side_effect=respond):
            result = tts.synthesize_wav("HGB 10.8 g/dL")
        self.assertEqual(result, expected)
        self.assertEqual(captured["url"], "https://api.vieneu.io/api/v1/audio/speech")
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["headers"]["Authorization"], "Bearer test-secret")
        self.assertEqual(captured["body"], {"input": "huyết sắc tố 10 phẩy 8 gam trên đề xi lít",
                                           "voice": "confirmed-voice-id", "model": "vieneu-v4", "response_format": "wav",
                                           "aiRefine": False, "applyPronunciation": False})
        self.assertEqual(captured["timeout"], 90)

    def test_default_backend_is_api_and_missing_key_does_not_load_local_model(self):
        os.environ.pop("VIENEU_TTS_BACKEND", None)
        os.environ.pop("VIENEU_API_KEY", None)
        with patch.object(tts, "_engine", side_effect=AssertionError("local fallback")), patch.object(tts, "urlopen", side_effect=AssertionError("network")):
            with self.assertRaisesRegex(RuntimeError, r"VIENEU_API_KEY.*\.env"):
                tts.synthesize_wav("Xin chào.")

    def test_http_failure_is_sanitized_and_never_retried(self):
        for code in (401, 403, 429, 503):
            with self.subTest(code=code):
                error = HTTPError("https://api.vieneu.io/api/v1/audio/speech", code,
                                  "test-secret", {}, io.BytesIO(b"test-secret"))
                with patch.object(tts, "urlopen", side_effect=error) as request:
                    with self.assertRaises(RuntimeError) as raised:
                        tts.synthesize_wav("Xin chào.")
                self.assertIn(str(code), str(raised.exception))
                self.assertNotIn("test-secret", str(raised.exception))
                self.assertEqual(request.call_count, 1)

    def test_transport_failure_is_sanitized(self):
        for error in (URLError("test-secret"), TimeoutError("test-secret")):
            with self.subTest(error=type(error).__name__), patch.object(tts, "urlopen", side_effect=error):
                with self.assertRaises(RuntimeError) as raised:
                    tts.synthesize_wav("Xin chào.")
                self.assertNotIn("test-secret", str(raised.exception))

    def test_non_wav_empty_truncated_and_wrong_content_type_are_rejected(self):
        fixtures = [(b"", "audio/wav"), (b"not wav", "audio/wav"), (wav_bytes(0), "audio/wav"),
                    (wav_bytes()[:-20], "audio/wav"), (wav_bytes(), "application/json")]
        for data, content_type in fixtures:
            with self.subTest(length=len(data), content_type=content_type), patch.object(tts, "urlopen", return_value=Response(data, content_type)):
                with self.assertRaises(RuntimeError):
                    tts.synthesize_wav("Xin chào.")

    def test_octet_stream_with_real_wav_is_accepted(self):
        expected = wav_bytes()
        with patch.object(tts, "urlopen", return_value=Response(expected, "application/octet-stream")):
            self.assertEqual(tts.synthesize_wav("Xin chào."), expected)

    def test_oversized_response_is_rejected(self):
        with patch.object(tts, "MAX_AUDIO_BYTES", 100), patch.object(tts, "urlopen", return_value=Response(wav_bytes())):
            with self.assertRaises(RuntimeError):
                tts.synthesize_wav("Xin chào.")

    def test_unknown_backend_is_rejected(self):
        with patch.dict(os.environ, {"VIENEU_TTS_BACKEND": "other"}), patch.object(tts, "_engine", side_effect=AssertionError("unexpected local backend")):
            with self.assertRaises(RuntimeError):
                tts.synthesize_wav("Xin chào.")


if __name__ == "__main__":
    unittest.main()
