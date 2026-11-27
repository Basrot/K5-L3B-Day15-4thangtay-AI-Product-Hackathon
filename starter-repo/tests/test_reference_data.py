"""Checks against published point estimates, not the parenthesized 90% CIs."""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codebase"))

from catalog import ANALYTES, DEFAULT_UNITS


class PublishedReferenceDataTest(unittest.TestCase):
    def test_has_three_ordered_decimal_intervals_for_exactly_the_catalog(self):
        from reference_data import REFERENCE_INTERVALS

        self.assertEqual(set(REFERENCE_INTERVALS), set(ANALYTES))
        for code, entry in REFERENCE_INTERVALS.items():
            with self.subTest(code=code):
                self.assertEqual(set(entry), {"unit", "1", "2", "3"})
                self.assertEqual(entry["unit"], DEFAULT_UNITS[code])
                for trimester in ("1", "2", "3"):
                    low, high = entry[trimester]
                    self.assertIsInstance(low, str)
                    self.assertIsInstance(high, str)
                    self.assertGreaterEqual(Decimal(low), 0)
                    self.assertLess(Decimal(low), Decimal(high))

    def test_eight_main_analytes_match_published_tables_and_abstract_anchors(self):
        from reference_data import REFERENCE_INTERVALS

        # PT trimester 2 follows Table 3 (11.60), not the abstract typo (11.66).
        expected = {
            "RBC": (("3.73", "5.32"), ("3.33", "4.98"), ("3.54", "4.98")),
            "HGB": (("10.33", "13.95"), ("9.71", "13.17"), ("9.80", "13.97")),
            "HCT": (("32.22", "42.29"), ("30.26", "40.07"), ("31.11", "42.70")),
            "WBC": (("6.33", "15.24"), ("6.99", "15.55"), ("6.22", "14.14")),
            "PLT": (("169.66", "413.88"), ("172.34", "372.19"), ("151.30", "417.14")),
            "PT": (("10.30", "12.88"), ("9.80", "11.60"), ("9.60", "11.40")),
            "APTT": (("25.40", "35.46"), ("24.05", "33.23"), ("23.40", "31.80")),
            "FIB": (("280.28", "559.00"), ("347.75", "593.35"), ("330.28", "628.56")),
        }
        for code, triplet in expected.items():
            with self.subTest(code=code):
                self.assertEqual(tuple(REFERENCE_INTERVALS[code][t] for t in ("1", "2", "3")), triplet)

    def test_differential_absolute_counts_and_percentages_keep_distinct_rows(self):
        from reference_data import REFERENCE_INTERVALS

        for code, absolute, percent in (
            ("NEUT", ("4.57", "12.25"), ("59.72", "79.61")),
            ("LYMPH", ("1.24", "3.03"), ("11.94", "29.31")),
            ("MONO", ("0.38", "1.28"), ("4.17", "10.26")),
            ("EOS", ("0.04", "0.50"), ("0.34", "4.64")),
            ("BASO", ("0.01", "0.09"), ("0.10", "0.76")),
        ):
            with self.subTest(code=code):
                self.assertEqual(REFERENCE_INTERVALS[code + "_ABS"]["2"], absolute)
                self.assertEqual(REFERENCE_INTERVALS[code + "_PCT"]["2"], percent)

    def test_source_scope_and_table_abstract_discrepancy_are_explicit(self):
        from reference_data import SCOPE_NOTE, SOURCE_NOTES, STUDY_SOURCE

        self.assertEqual(STUDY_SOURCE["url"], "https://doi.org/10.1186/s12884-023-06106-2")
        self.assertEqual(STUDY_SOURCE["year"], 2023)
        self.assertEqual(len(STUDY_SOURCE["table_urls"]), 2)
        self.assertIn("DxH 900", STUDY_SOURCE["instruments"])
        self.assertIn("ACL TOP 550", STUDY_SOURCE["instruments"])
        self.assertIn("Hùng Vương", STUDY_SOURCE["population"])
        self.assertIn("không", SCOPE_NOTE.lower())
        self.assertIn("chẩn đoán", SCOPE_NOTE)
        self.assertIn("xác nhận", SCOPE_NOTE)
        self.assertIn("11.60", " ".join(SOURCE_NOTES))
        self.assertIn("11.66", " ".join(SOURCE_NOTES))


if __name__ == "__main__":
    unittest.main()
