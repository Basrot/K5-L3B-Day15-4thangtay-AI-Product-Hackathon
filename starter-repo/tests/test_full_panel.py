"""Synthetic examples only; reference limits here are not clinical defaults."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codebase"))
import tools


def compare(rows):
    return tools.compare_cbc({"pregnancy_status": "pregnant", "adult_confirmed": True,
                              "gestational_age": "21w3d", "rows": rows})


def row(code, unit, value="2", low="1", high="3", ref_unit=None):
    return {"analyte": code, "unit": unit, "value": value, "ref_low": low,
            "ref_high": high, "ref_unit": ref_unit or unit}


class FullPanelTest(unittest.TestCase):
    def test_all_twenty_four_analytes_are_comparable(self):
        units = {
            "RBC": "10^12/L", "HGB": "g/L", "HCT": "%", "MCV": "fL", "MCH": "pg",
            "MCHC": "g/L", "RDW": "%", "RDW_SD": "fL", "WBC": "10^9/L",
            "NEUT_ABS": "10^9/L", "NEUT_PCT": "%", "LYMPH_ABS": "10^9/L", "LYMPH_PCT": "%",
            "MONO_ABS": "10^9/L", "MONO_PCT": "%", "EOS_ABS": "10^9/L", "EOS_PCT": "%",
            "BASO_ABS": "10^9/L", "BASO_PCT": "%", "PLT": "10^9/L", "MPV": "fL",
            "PT": "s", "APTT": "s", "FIB": "g/L",
        }
        self.assertEqual(set(tools.ANALYTES), set(units))
        result = compare([row(code, unit) for code, unit in units.items()])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["rows"]), 24)
        self.assertTrue(all(item["status"] == "within" for item in result["rows"]))

    def test_dimension_conversions_preserve_exact_boundaries(self):
        cases = [
            ("RBC", "10¹²/L", "4.25", "10⁶/µL", "4.25"),
            ("HCT", "L/L", "0.425", "%", "42.5"),
            ("HCT", "%", "42.5", "L/L", "0.425"),
            ("HGB", "g/dL", "12.3", "g/L", "123"),
            ("MCHC", "g/L", "345", "g/dL", "34.5"),
            ("FIB", "mg/dL", "425.5", "g/L", "4.255"),
            ("FIB", "g/L", "4.255", "mg/dL", "425.5"),
            ("NEUT_ABS", "10³/uL", "4.25", "10⁹/L", "4.25"),
        ]
        for code, unit, value, reference_unit, expected in cases:
            with self.subTest(code=code, unit=unit):
                result = compare([row(code, unit, value, "0", expected, reference_unit)])
                self.assertEqual(result["status"], "ok")
                self.assertEqual((result["rows"][0]["value"], result["rows"][0]["status"]),
                                 (expected, "within"))

    def test_catalog_normalizes_explicit_differentials_and_workbook_names(self):
        import catalog
        for alias, expected in {"RDW-SD": "RDW_SD", "RDW-CV": "RDW", "NEUT#": "NEUT_ABS",
                                "NEU%": "NEUT_PCT", "LYM#": "LYMPH_ABS", "LYMPH%": "LYMPH_PCT",
                                "MONO_abs": "MONO_ABS", "EO%": "EOS_PCT", "BAS#": "BASO_ABS"}.items():
            with self.subTest(alias=alias):
                self.assertEqual(catalog.normalize_analyte(alias), expected)
        self.assertEqual(set(catalog.DEFAULT_UNITS), set(catalog.ANALYTES))
        self.assertEqual(set(catalog.GROUPS), set(catalog.ANALYTES))
        headers = (
            "RBC_10e12_L", "HGB_g_dL", "HCT_pct", "MCV_fL", "MCH_pg", "MCHC_g_dL",
            "RDW_pct", "RDW_SD_fL", "WBC_10e9_L", "NEUT_abs_10e9_L", "NEUT_pct",
            "LYMPH_abs_10e9_L", "LYMPH_pct", "MONO_abs_10e9_L", "MONO_pct",
            "EOS_abs_10e9_L", "EOS_pct", "BASO_abs_10e9_L", "BASO_pct", "PLT_10e9_L",
            "MPV_fL", "PT_s", "APTT_s", "FIB_mg_dL",
        )
        self.assertEqual([catalog.normalize_analyte(header) for header in headers], list(catalog.ANALYTES))
        result = compare([row("NEUT#", "10^9/L"), row("NEUT%", "%")])
        self.assertEqual(result["status"], "ok")
        self.assertEqual([r["analyte"] for r in result["rows"]], ["NEUT_ABS", "NEUT_PCT"])

    def test_rejects_ambiguous_codes_units_duplicates_and_missing_lab_ranges(self):
        invalid = [
            [row("NEUT", "10^9/L")], [row("NEUT_ABS", "%")], [row("NEUT_PCT", "10^9/L")],
            [row("RBC", "10^9/L")], [row("WBC", "10e9/L")], [row("PT", "%")],
            [row("NEUT#", "10^9/L"), row("NEUT_ABS", "10^9/L")],
            [row("MCV", "fL", low=None)], [dict(row("FIB", "g/L"), ref_unit=None)],
            [], [row("HGB", "g/L")] * 25,
        ]
        for rows in invalid:
            with self.subTest(rows=rows):
                self.assertEqual(compare(rows)["status"], "needs_input")


if __name__ == "__main__":
    unittest.main()
