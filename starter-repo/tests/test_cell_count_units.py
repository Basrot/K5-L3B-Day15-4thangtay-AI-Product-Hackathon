import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codebase import tools, vision


def report(rows):
    return {"pregnancy_status": "pregnant", "adult_confirmed": True,
            "gestational_age": "24w2d", "reference_mode": "study", "rows": rows}


class CellCountUnitTest(unittest.TestCase):
    def test_tera_and_giga_aliases_preserve_the_numbers(self):
        result = tools.compare_cbc(report([
            {"analyte": "RBC", "value": "5.62", "unit": "T/L"},
            {"analyte": "WBC", "value": "20.4", "unit": "G/L"},
            {"analyte": "PLT", "value": "254", "unit": "G/L"},
        ]))
        self.assertEqual(result["status"], "ok")
        self.assertEqual([(r["value"], r["unit"]) for r in result["rows"]],
                         [("5.62", "10¹²/L"), ("20.4", "10⁹/L"), ("254", "10⁹/L")])

    def test_cell_counts_reject_mass_units_and_wrong_orders_of_magnitude(self):
        for code, unit in (("WBC", "g/dL"), ("WBC", "g/L"), ("PLT", "g/dL"),
                           ("RBC", "G/L"), ("PLT", "T/L"), ("WBC", "10e9/L")):
            with self.subTest(code=code, unit=unit):
                self.assertEqual(tools.compare_cbc(report([
                    {"analyte": code, "value": "20.4", "unit": unit}
                ]))["status"], "needs_input")

    def test_wrong_wbc_unit_has_actionable_feedback(self):
        result = tools.compare_cbc(report([{"analyte": "WBC", "value": "20.4", "unit": "g/dL"}]))
        self.assertIn("nồng độ", result["issues"][0])
        self.assertIn("phiếu gốc", result["issues"][0])

    def test_ocr_keeps_uncertain_unit_and_warns_instead_of_silently_correcting(self):
        data = {"rows": [{"analyte": "WBC", "value": "20.4", "unit": "g/dL",
                          "ref_low": None, "ref_high": None, "ref_unit": None}], "warnings": []}
        result = vision._validate_result(data)
        self.assertEqual(result["rows"][0]["unit"], "g/dL")
        self.assertTrue(any("WBC" in warning and "đơn vị" in warning for warning in result["warnings"]))
