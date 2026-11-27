import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase import agent, tools
from codebase.service import CBCService
from codebase.reference_data import REFERENCE_INTERVALS


def study_report(age="21w3d", **changes):
    return {"pregnancy_status": "pregnant", "adult_confirmed": True,
            "gestational_age": age, "reference_mode": "study",
            "rows": [{"analyte": "HGB", "value": "108", "unit": "g/L"}], **changes}


class StudyReferenceTest(unittest.TestCase):
    def test_result_only_selects_published_trimester_range_and_converts_units(self):
        result = tools.compare_cbc(study_report())
        self.assertEqual(result["status"], "ok", result)
        row = result["rows"][0]
        self.assertEqual((row["value"], row["ref_low"], row["ref_high"], row["unit"], row["status"]),
                         ("10.8", "9.71", "13.17", "g/dL", "within"))
        self.assertEqual(result["trimester"], 2)
        self.assertEqual(result["reference_mode"], "study")
        self.assertIn("10.1186/s12884-023-06106-2", result["reference_source"]["url"])

    def test_infers_study_for_missing_or_blank_reference_fields(self):
        report = study_report()
        report.pop("reference_mode")
        for extra in ({}, {"ref_low": None, "ref_high": "", "ref_unit": None}):
            report["rows"][0].update(extra)
            self.assertEqual(tools.compare_cbc(report)["reference_mode"], "study")

    def test_trimester_day_boundaries_follow_shared_workbook(self):
        for age, trimester, low in (("13w6d", 1, "10.33"), ("14w0d", 2, "9.71"),
                                    ("28w0d", 2, "9.71"), ("28w6d", 2, "9.71"),
                                    ("29w0d", 3, "9.8")):
            with self.subTest(age=age):
                result = tools.compare_cbc(study_report(age))
                self.assertEqual(result["trimester"], trimester)
                self.assertEqual(result["rows"][0]["ref_low"], low)

    def test_missing_unit_and_bad_context_stop_before_model(self):
        for changes in ({"rows": [{"analyte": "HGB", "value": 108}]},
                        {"gestational_age": None}, {"gestational_age": "28w7d"},
                        {"gestational_age": "99w0d"}, {"adult_confirmed": False},
                        {"pregnancy_status": "not_pregnant"}, {"reference_mode": "guess"}):
            with self.subTest(changes=changes), patch.object(agent, "call_model", side_effect=AssertionError("must not call")):
                result = agent.answer(json.dumps({"report": study_report(**changes), "question": "HGB thế nào?"}))
                self.assertIn(result["status"], ("needs_input", "out_of_scope"))

    def test_study_mode_ignores_even_conflicting_lab_bounds(self):
        report = study_report(rows=[{"analyte": "HGB", "value": "108", "unit": "g/L",
                                   "ref_low": "999", "ref_high": "1", "ref_unit": "%"}])
        result = tools.compare_cbc(report)
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(result["rows"][0]["ref_low"], "9.71")

    def test_partial_lab_range_is_not_silently_replaced(self):
        report = study_report(rows=[{"analyte": "HGB", "value": "108", "unit": "g/L", "ref_low": "110"}])
        report.pop("reference_mode")
        self.assertEqual(tools.compare_cbc(report)["status"], "needs_input")
        report["reference_mode"] = "lab"
        self.assertEqual(tools.compare_cbc(report)["status"], "needs_input")

    def test_published_bounds_are_inclusive(self):
        for value, expected in (("9.709", "below"), ("9.71", "within"),
                                ("13.17", "within"), ("13.171", "above")):
            result = tools.compare_cbc(study_report(rows=[{"analyte": "HGB", "value": value, "unit": "g/dL"}]))
            self.assertEqual(result["rows"][0]["status"], expected)

    def test_supported_eight_study_rows_can_be_analyzed_in_each_trimester(self):
        for age, trimester in (("10w0d", "1"), ("21w3d", "2"), ("32w0d", "3")):
            rows = [{"analyte": code, "unit": entry["unit"],
                     "value": str((Decimal(entry[trimester][0]) + Decimal(entry[trimester][1])) / 2)}
                    for code, entry in REFERENCE_INTERVALS.items() if code in
                    ("HGB", "RBC", "HCT", "MCV", "MCH", "MCHC", "WBC", "PLT")]
            result = agent.analyze_report(study_report(age, rows=rows))
            self.assertEqual(result["status"], "analyzed", result)
            self.assertEqual(result["counts"], {"below": 0, "within": 8, "above": 0})

    def test_unit_conversions_keep_study_and_absolute_percent_rows_distinct(self):
        rows = [{"analyte": "HCT", "value": "0.35", "unit": "L/L"},
                {"analyte": "MCHC", "value": "320", "unit": "g/L"}]
        result = tools.compare_cbc(study_report(rows=rows))
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual([r["value"] for r in result["rows"]], ["35", "32"])
        self.assertTrue(all(row["status"] == "within" for row in result["rows"]))
        rows[-1]["unit"] = "%"
        self.assertEqual(tools.compare_cbc(study_report(rows=rows))["status"], "needs_input")

    def test_explanations_name_study_instead_of_claiming_bounds_from_lab(self):
        analysis = agent.analyze_report(study_report())
        self.assertEqual(analysis["status"], "analyzed")
        self.assertIn("nghiên cứu", analysis["output"])
        self.assertNotIn("khoảng tham chiếu ghi trên phiếu", analysis["output"])
        self.assertNotIn("cao hơn khoảng trên phiếu", analysis["output"])
        self.assertIn("không", analysis["reference_note"].lower())
        with patch.object(agent, "call_model", return_value={"text": "", "model": "fake"}):
            reply = agent.answer(json.dumps({"report": study_report(), "question": "HGB thế nào?"}))
        self.assertEqual(reply["status"], "explained")
        self.assertIn("tam cá nguyệt 2", reply["output"])
        self.assertNotIn("ghi trên phiếu", reply["output"])
        self.assertTrue(any("06106-2" in source["url"] for source in reply["sources"]))

    def test_reference_mode_survives_sqlite_round_trip_and_changes_revision(self):
        with tempfile.TemporaryDirectory() as folder:
            service = CBCService(Path(folder) / "test.sqlite3")
            session = service.create_session()
            saved = service.confirm_report(session, study_report(), confirmed=True, expected_revision=0)
            state = CBCService(service.path).get_session(session)
            self.assertEqual(state["report"]["reference_mode"], "study")
            self.assertEqual(state["report"]["reference_version"], "pham2023-tables-v1")
            self.assertEqual(saved["session"]["report"], state["report"])
            self.assertEqual(agent.analyze_report(state["report"])["rows"][0]["ref_low"], "9.71")
            lab_report = study_report(reference_mode="lab", rows=[{
                "analyte": "HGB", "value": "108", "unit": "g/L",
                "ref_low": "110", "ref_high": "140", "ref_unit": "g/L"}])
            service.confirm_report(session, lab_report, confirmed=True, expected_revision=1)
            self.assertEqual(service.get_session(session)["revision"], 2)

    def test_unknown_reference_version_requires_reconfirmation_before_model(self):
        with patch.object(agent, "call_model", side_effect=AssertionError("must not call")):
            result = agent.answer(json.dumps({"report": study_report(reference_version="future-or-retired-table"),
                                              "question": "HGB thế nào?"}))
        self.assertEqual(result["status"], "needs_input")
        self.assertIn("bảng tham chiếu", result["output"])

    def test_explicit_lab_mode_on_legacy_report_preserves_existing_history(self):
        from test_cbc_ai import report as lab_report
        with tempfile.TemporaryDirectory() as folder:
            service = CBCService(Path(folder) / "test.sqlite3")
            session = service.create_session()
            service.confirm_report(session, lab_report(), confirmed=True, expected_revision=0)
            with patch("codebase.service.answer", return_value={"status": "explained", "output": "saved"}):
                service.ask(session, "HGB?", expected_revision=1, request_id="saved")
            service.confirm_report(session, lab_report(reference_mode="lab"), confirmed=True, expected_revision=1)
            self.assertEqual(service.get_session(session)["revision"], 1)
            self.assertEqual(len(service.history(session)), 1)


if __name__ == "__main__":
    unittest.main()
