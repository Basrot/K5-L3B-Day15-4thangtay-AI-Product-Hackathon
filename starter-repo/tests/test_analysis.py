import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase.agent import analyze_report


class AnalysisTest(unittest.TestCase):
    def test_full_table_and_counts_agree_with_individual_rows(self):
        report = {
            "adult_confirmed": True, "pregnancy_status": "pregnant", "gestational_age": "21w3d",
            "rows": [
                {"analyte": "HGB", "value": "108", "unit": "g/L", "ref_low": "11",
                 "ref_high": "14", "ref_unit": "g/dL"},
                {"analyte": "WBC", "value": "8", "unit": "10^9/L", "ref_low": "6",
                 "ref_high": "15", "ref_unit": "10^9/L"},
                {"analyte": "PLT", "value": "450", "unit": "10^9/L", "ref_low": "150",
                 "ref_high": "400", "ref_unit": "10^9/L"},
            ],
        }
        result = analyze_report(report)
        self.assertEqual(result["status"], "analyzed")
        self.assertEqual(result["counts"], {"below": 1, "within": 1, "above": 1})
        self.assertEqual(len(result["rows"]), 3)
        self.assertIn("HGB", result["output"])
        self.assertIn("PLT", result["output"])
        self.assertTrue(result["sources"])

    def test_invalid_report_returns_fields_to_fix_and_no_partial_analysis(self):
        result = analyze_report({"rows": []})
        self.assertEqual(result["status"], "needs_input")
        self.assertNotIn("counts", result)
