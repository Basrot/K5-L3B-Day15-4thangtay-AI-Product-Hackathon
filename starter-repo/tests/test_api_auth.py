import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase.api_auth import issue_token, verify_token


class AuthTest(unittest.TestCase):
    def setUp(self):
        self.config = patch.dict(os.environ, {
            "APP_USERNAME": "demo", "APP_PASSWORD": "testing-password", "APP_SECRET": "s" * 32,
        })
        self.config.start()
        self.addCleanup(self.config.stop)

    def test_valid_token_round_trip_and_modified_token_is_rejected(self):
        result = issue_token("demo", "testing-password")
        self.assertEqual(verify_token(result["access_token"]), "demo")
        self.assertEqual(result["token_type"], "bearer")
        self.assertEqual(result["expires_in"], 3600)
        token = result["access_token"]
        body, signature = token.split(".")
        with self.assertRaises(HTTPException) as error:
            verify_token(body + "." + ("a" if signature[0] != "a" else "b") + signature[1:])
        self.assertEqual(error.exception.status_code, 401)

    def test_expired_token_is_rejected(self):
        with patch("codebase.api_auth.time.time", return_value=1000):
            result = issue_token("demo", "testing-password")
        with patch("codebase.api_auth.time.time", return_value=4600):
            with self.assertRaises(HTTPException) as error:
                verify_token(result["access_token"])
        self.assertEqual(error.exception.status_code, 401)

    def test_bad_password_is_rejected_and_missing_secret_has_clear_status(self):
        with self.assertRaises(HTTPException) as error:
            issue_token("demo", "wrong")
        self.assertEqual(error.exception.status_code, 401)
        with patch.dict(os.environ, {"APP_SECRET": ""}):
            with self.assertRaises(HTTPException) as error:
                issue_token("demo", "testing-password")
        self.assertEqual(error.exception.status_code, 503)
