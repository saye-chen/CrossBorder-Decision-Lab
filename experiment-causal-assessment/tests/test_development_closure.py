import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_development_closure import audit


class DevelopmentClosureTests(unittest.TestCase):
    def test_stored_development_closure_is_reproducible(self):
        stored = json.loads((ROOT / "evaluations/development-closure.json").read_text(encoding="utf-8"))
        self.assertEqual(audit(), stored)
        self.assertTrue(stored["development_complete"])
        self.assertEqual(stored["remaining_work_class"], "l4_external_only")
        self.assertFalse(stored["production_ready"])
        self.assertFalse(stored["external_write_authorized"])

    def test_development_closure_does_not_promote_external_evidence(self):
        stored = json.loads((ROOT / "evaluations/development-closure.json").read_text(encoding="utf-8"))
        self.assertTrue(all(item.startswith("L4 ") for item in stored["remaining_work"]))
        self.assertIn("L4 authorized real-data decision replay, mature outcomes, calibration, drift review, and external assurance", stored["remaining_work"])


if __name__ == "__main__":
    unittest.main()
