import json
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from test_cbc_ai import report
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase.service import CBCService


class SessionTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "sessions.sqlite3"
        self.service = CBCService(self.path)

    def tearDown(self):
        self.directory.cleanup()

    def test_report_must_be_confirmed_and_valid(self):
        session = self.service.create_session()
        with self.assertRaises(ValueError):
            self.service.confirm_report(session, report(), confirmed=False, expected_revision=0)
        with self.assertRaises(ValueError):
            self.service.confirm_report(session, report(rows=[]), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
        with self.assertRaises(ValueError):
            self.service.ask(session, "HGB là gì?", expected_revision=1)

    def test_confirmed_report_and_history_survive_restart(self):
        session = self.service.create_session()
        saved = self.service.confirm_report(
            session, report(), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
        with patch("codebase.service.answer", return_value={"status": "explained", "output": "HGB mẫu"}):
            self.service.ask(session, "HGB là gì?", expected_revision=1)
        reopened = CBCService(self.path)
        self.assertEqual(reopened.get_session(session)["report"], saved["session"]["report"])
        self.assertEqual(reopened.history(session)[0]["question"], "HGB là gì?")
        self.assertEqual(reopened.history(session)[0]["result"]["output"], "HGB mẫu")

    def test_revision_change_while_model_is_running_discards_stale_answer(self):
        session = self.service.create_session()
        self.service.confirm_report(session, report(), confirmed=True, expected_revision=self.service.get_session(session)['revision'])

        def change_report(_text, **_kwargs):
            self.service.confirm_report(session, report(gestational_age="22w0d"), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
            return {"status": "explained", "output": "Kết quả cũ"}

        with patch("codebase.service.answer", side_effect=change_report):
            with self.assertRaisesRegex(ValueError, "thay đổi"):
                self.service.ask(session, "HGB là gì?", expected_revision=1)
        self.assertEqual(self.service.history(session), [])

    def test_retry_with_same_request_id_returns_saved_answer(self):
        session = self.service.create_session()
        self.service.confirm_report(session, report(), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
        with patch("codebase.service.answer", return_value={"status": "explained", "output": "HGB mẫu"}):
            first = self.service.ask(session, "HGB là gì?", expected_revision=1, request_id="request-1")
        with patch("codebase.service.answer", side_effect=AssertionError("duplicate call")):
            self.assertEqual(self.service.ask(session, "HGB là gì?", expected_revision=1, request_id="request-1"), first)
        self.assertEqual(len(self.service.history(session)), 1)
        with self.assertRaises(ValueError):
            self.service.ask(session, "WBC là gì?", expected_revision=1, request_id="request-1")

    def test_two_sessions_are_isolated_and_deletion_removes_history(self):
        one, two = self.service.create_session(), self.service.create_session()
        self.service.confirm_report(one, report(), confirmed=True, expected_revision=self.service.get_session(one)['revision'])
        self.assertIsNone(self.service.get_session(two)["report"])
        with patch("codebase.service.answer", return_value={"status": "explained", "output": "HGB mẫu"}):
            self.service.ask(one, "HGB là gì?", expected_revision=1)
        self.service.delete_session(one)
        with self.assertRaises(KeyError):
            self.service.get_session(one)
        self.assertEqual(self.service.history(two), [])

    def test_invalidation_requires_confirmation_again(self):
        session = self.service.create_session()
        self.service.confirm_report(session, report(), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
        self.service.invalidate_report(session, expected_revision=1)
        with self.assertRaises(ValueError):
            self.service.ask(session, "HGB là gì?", expected_revision=1)

    def test_old_confirmation_cannot_overwrite_new_report(self):
        session = self.service.create_session()
        self.service.confirm_report(session, report(), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
        with self.assertRaisesRegex(ValueError, "thay đổi"):
            self.service.confirm_report(session, report(gestational_age="22w0d"),
                                        confirmed=True, expected_revision=0)
        self.assertEqual(self.service.get_session(session)["report"]["gestational_age"], "21w3d")

    def test_question_from_old_report_is_rejected_before_model_call(self):
        session = self.service.create_session()
        self.service.confirm_report(session, report(), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
        self.service.confirm_report(session, report(gestational_age="22w0d"), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
        with patch("codebase.service.answer", side_effect=AssertionError("stale model call")):
            with self.assertRaisesRegex(ValueError, "thay đổi"):
                self.service.ask(session, "HGB là gì?", expected_revision=1)

    def test_reconfirming_identical_report_preserves_history(self):
        session = self.service.create_session()
        self.service.confirm_report(session, report(), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
        with patch("codebase.service.answer", return_value={"status": "explained", "output": "mẫu"}):
            self.service.ask(session, "HGB là gì?", expected_revision=1)
        self.service.confirm_report(session, report(), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
        self.assertEqual(len(self.service.history(session)), 1)

    def test_stale_invalidation_preserves_current_report(self):
        session = self.service.create_session()
        self.service.confirm_report(session, report(), confirmed=True, expected_revision=self.service.get_session(session)['revision'])
        with self.assertRaisesRegex(ValueError, "thay đổi"):
            self.service.invalidate_report(session, expected_revision=0)
        self.assertIsNotNone(self.service.get_session(session)["report"])


if __name__ == "__main__":
    unittest.main()
