import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase import api


def report():
    return {"pregnancy_status": "pregnant", "adult_confirmed": True, "gestational_age": "20w0d",
            "rows": [{"analyte": "HGB", "value": "10.8", "unit": "g/dL", "ref_low": "11",
                      "ref_high": "14", "ref_unit": "g/dL"}]}


class APITest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.env = patch.dict(os.environ, {"APP_USERNAME": "demo", "APP_PASSWORD": "test-password",
                                          "APP_SECRET": "x" * 32, "CORS_ORIGINS": "http://localhost:3000"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.app = api.create_app(Path(self.directory.name) / "test.sqlite3")
        self.client = self.enterContext(TestClient(self.app))
        login = self.client.post("/v1/auth/login", json={"username": "demo", "password": "test-password"})
        self.assertEqual(login.status_code, 200, login.text)
        self.headers = {"Authorization": "Bearer " + login.json()["access_token"]}

    def request(self, method, path, **kwargs):
        return self.client.request(method, path, headers=self.headers, **kwargs)

    def test_public_health_docs_and_protected_catalog(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})
        self.assertEqual(self.client.get("/openapi.json").status_code, 200)
        self.assertEqual(self.client.get("/v1/catalog").status_code, 401)
        catalog = self.request("GET", "/v1/catalog").json()
        self.assertEqual(len(catalog), 24)
        self.assertEqual(set(catalog[0]), {"code", "name", "unit", "group"})

    def test_session_confirm_analysis_chat_retry_stale_and_delete(self):
        state = self.request("POST", "/v1/sessions").json()
        session = "/v1/sessions/" + state["session_id"]
        self.assertEqual(state["revision"], 0)
        saved = self.request("PUT", session + "/report", json={"report": report(), "confirmed": True, "expected_revision": 0})
        self.assertEqual(saved.status_code, 200, saved.text)
        self.assertEqual(saved.json()["revision"], 1)
        self.assertIn("analysis", saved.json())
        self.assertEqual(self.request("GET", session + "/analysis?expected_revision=0").status_code, 409)
        self.assertEqual(self.request("GET", session + "/analysis?expected_revision=1").status_code, 200)
        body = {"question": "HGB thế nào?", "expected_revision": 1, "request_id": "retry-id"}
        with patch("codebase.service.answer", return_value={"status": "explained", "output": "Test answer"}) as answer:
            first = self.request("POST", session + "/chat", json=body)
            second = self.request("POST", session + "/chat", json=body)
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.json()["output"], "Test answer")
        self.assertEqual(second.json()["usage"]["model_calls"], 0)
        self.assertEqual(answer.call_count, 1)
        self.assertEqual(len(self.request("GET", session + "/history").json()["messages"]), 1)
        self.assertEqual(self.request("POST", session + "/invalidate", json={"expected_revision": 1}).status_code, 200)
        self.assertEqual(self.request("POST", session + "/chat", json=body).status_code, 409)
        self.assertEqual(self.request("DELETE", session).status_code, 204)
        self.assertEqual(self.request("GET", session).status_code, 404)

    def test_strict_schemas_reject_extra_bool_numeric_and_missing_revision(self):
        bad_report = report()
        bad_report["rows"][0]["value"] = True
        for payload in (bad_report, {**report(), "extra": "forbidden"}, {**report(), "rows": []}):
            self.assertEqual(self.request("POST", "/v1/reports/validate", json=payload).status_code, 422)
        path = "/v1/sessions/" + self.request("POST", "/v1/sessions").json()["session_id"]
        self.assertEqual(self.request("POST", path + "/chat", json={"question": "hi"}).status_code, 422)
        self.assertEqual(self.request("GET", path + "/analysis").status_code, 422)
        self.assertEqual(self.request("POST", path + "/invalidate", json={"expected_revision": True}).status_code, 422)

    def test_uploads_and_synthesis_use_existing_boundaries(self):
        with patch.object(api.vision, "extract_report", return_value={"rows": [], "warnings": ["review"]}):
            response = self.request("POST", "/v1/reports/extract", files={"file": ("report.png", b"image", "image/png")})
        self.assertEqual(response.json(), {"rows": [], "warnings": ["review"]})
        with patch.object(api.speech, "transcribe_wav", return_value="HGB"):
            response = self.request("POST", "/v1/speech/transcribe", files={"file": ("speech.wav", b"wav", "audio/wav")})
        self.assertEqual(response.json(), {"text": "HGB"})
        with patch.object(api.tts, "synthesize_wav", return_value=b"RIFF-test"):
            response = self.request("POST", "/v1/speech/synthesize", json={"text": "HGB"})
        self.assertEqual(response.content, b"RIFF-test")
        self.assertEqual(response.headers["content-type"], "audio/wav")

    def test_busy_and_upstream_errors_do_not_leak_secrets(self):
        self.app.state.model_lock.acquire()
        try:
            response = self.request("POST", "/v1/speech/synthesize", json={"text": "hello"})
        finally:
            self.app.state.model_lock.release()
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["retry-after"], "1")
        with patch.object(api.tts, "synthesize_wav", side_effect=RuntimeError("secret-api-key")):
            response = self.request("POST", "/v1/speech/synthesize", json={"text": "hello"})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("secret-api-key", response.text)

    def test_chat_usage_is_measured_and_cached_retry_has_no_new_tokens(self):
        path = "/v1/sessions/" + self.request("POST", "/v1/sessions").json()["session_id"]
        self.request("PUT", path + "/report", json={"report": report(), "confirmed": True, "expected_revision": 0})

        @api.tracing.model_call
        def model_answer(_payload):
            return {"text": "answer", "model": "test-model", "tokens_in": 7, "tokens_out": 11,
                    "status": "explained", "output": "answer"}

        body = {"question": "HGB?", "expected_revision": 1, "request_id": "measured-retry"}
        with patch("codebase.service.answer", side_effect=model_answer):
            first = self.request("POST", path + "/chat", json=body).json()
            second = self.request("POST", path + "/chat", json=body).json()
        self.assertEqual((first["usage"]["tokens_in"], first["usage"]["tokens_out"]), (7, 11))
        self.assertEqual((second["usage"]["tokens_in"], second["usage"]["tokens_out"]), (0, 0))

    def test_bounded_file_reads_reject_oversize_uploads(self):
        with patch.object(api, "IMAGE_LIMIT", 8), patch.object(api.vision, "extract_report", side_effect=AssertionError("must not infer")):
            response = self.request("POST", "/v1/reports/extract", files={"file": ("big.png", b"x" * 9, "image/png")})
        self.assertEqual(response.status_code, 413)

    def test_cors_preflight_accepts_only_configured_origin(self):
        for origin, expected in (("http://localhost:3000", 200), ("https://wrong.example", 400)):
            response = self.client.options("/v1/catalog", headers={"Origin": origin, "Access-Control-Request-Method": "GET"})
            self.assertEqual(response.status_code, expected)

    def test_browser_can_read_retry_after(self):
        self.app.state.model_lock.acquire()
        try:
            response = self.client.post("/v1/speech/synthesize", json={"text": "hello"},
                                        headers={**self.headers, "Origin": "http://localhost:3000"})
        finally:
            self.app.state.model_lock.release()
        self.assertIn("retry-after", response.headers.get("access-control-expose-headers", "").lower())

    def test_confirm_returns_committed_snapshot_when_invalidated_after_commit(self):
        service = self.app.state.service
        path = "/v1/sessions/" + self.request("POST", "/v1/sessions").json()["session_id"]
        original = service.confirm_report

        def confirm_then_invalidate(session_id, *args, **kwargs):
            saved = original(session_id, *args, **kwargs)
            service.invalidate_report(session_id, expected_revision=1)
            return saved

        with patch.object(service, "confirm_report", side_effect=confirm_then_invalidate):
            response = self.request("PUT", path + "/report", json={
                "report": report(), "confirmed": True, "expected_revision": 0})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["revision"], 1)
        self.assertEqual(response.json()["report"], report())
        self.assertEqual(response.json()["analysis"]["status"], "analyzed")
        self.assertEqual(self.request("GET", path).json()["revision"], 2)

    def test_factory_defers_database_creation_until_lifespan(self):
        target = Path(self.directory.name) / "deferred.sqlite3"
        api.create_app(target)
        self.assertFalse(target.exists())

    def test_cors_rejects_wildcards_and_paths(self):
        for origin in ("*", "https://*.example.com", "https://example.com/path", "https://example.com/"):
            with self.subTest(origin=origin), patch.dict(os.environ, {"CORS_ORIGINS": origin}):
                with self.assertRaises(ValueError):
                    api.create_app(Path(self.directory.name) / "unused.sqlite3")


if __name__ == "__main__":
    unittest.main()
