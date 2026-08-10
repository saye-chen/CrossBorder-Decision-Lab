#!/usr/bin/env python3
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("l4", ROOT / "scripts/validate_l4_external_assurance.py")
l4 = importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(l4)


class L4ExternalAssuranceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.registry = json.loads(l4.REGISTRY.read_text())

    def test_honest_open_gate_is_valid_but_not_passed(self):
        errors, passed = l4.evaluate(copy.deepcopy(self.registry))
        self.assertEqual(errors, [])
        self.assertFalse(passed)

    def test_empty_cases_cannot_be_relabelled_passed(self):
        data = copy.deepcopy(self.registry)
        data["domains"][0]["status"] = "passed"
        errors, passed = l4.evaluate(data)
        self.assertFalse(passed)
        self.assertTrue(any("false L4 pass" in x for x in errors))

    def test_system_production_claim_cannot_override_domains(self):
        data = copy.deepcopy(self.registry)
        data["production_ready"] = True
        errors, _ = l4.evaluate(data)
        self.assertIn("system production-ready claim exceeds domain evidence", errors)


if __name__ == "__main__": unittest.main(verbosity=2)
