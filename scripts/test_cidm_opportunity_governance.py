#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().with_name("validate_cidm_opportunity_governance.py")
SPEC = importlib.util.spec_from_file_location("cidm_osl_governance", SCRIPT)
module = importlib.util.module_from_spec(SPEC); assert SPEC and SPEC.loader; SPEC.loader.exec_module(module)

class CIDMOpportunityGovernanceTests(unittest.TestCase):
    def test_current_dod_and_all_work_packages_are_consistent(self):
        errors, summary = module.validate()
        self.assertEqual(errors, [])
        self.assertEqual(summary["work_packages"], 22)
        self.assertEqual(summary["detailed_requirements"], 118)
        self.assertEqual(summary["external_gates_open"], 3)
        self.assertFalse(summary["production_ready"])
        self.assertEqual(summary["maturity"], "controlled pilot")

if __name__ == "__main__": unittest.main(verbosity=2)
