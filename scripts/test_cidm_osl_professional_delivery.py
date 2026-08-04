#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

quality = load(ROOT / "scripts/evaluate_report_quality.py", "quality")
osl = load(ROOT / "category-investment-decision/scripts/validate_osl_professional_report.py", "osl_report")
REPORT = ROOT / "evaluations/golden-reports/cidm-osl-opportunity-full.md"

class TestOSLProfessionalDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = REPORT.read_text(encoding="utf-8")

    def test_generic_expert_gate_scores_100(self):
        result = quality.score_report(self.text, "full")
        self.assertEqual(result["result"], "PASS", result)
        self.assertEqual(result["score"], 100, result)

    def test_osl_specific_gate_passes(self):
        self.assertEqual(osl.validate(self.text), [])

    def test_each_osl_section_is_release_critical(self):
        for heading in osl.REQUIRED_SECTIONS:
            mutated = self.text.replace(f"## {heading}", f"## REMOVED-{heading}", 1)
            with self.subTest(heading=heading):
                self.assertTrue(osl.validate(mutated))

    def test_each_domain_is_release_critical(self):
        for domain in ["CIM", "PPFC", "SPPQ", "LIFD", "PLCO", "CIDM"]:
            mutated = self.text.replace(f"| {domain} |", "| OMITTED |", 1)
            with self.subTest(domain=domain):
                self.assertIn(f"shallow_domain_review:{domain}", osl.validate(mutated))

    def test_unsafe_mutations_fail(self):
        mutations = [
            ("online_realtime", "offline_default"),
            ("mcp_required=false", "mcp_required=true"),
            ("决策结论：`Do Not Do Yet`", "决策结论：`Go`"),
            ("资本承诺为 0", "资本承诺待定"),
            ("REALITY_RECOVERY", "RECOVERY_REMOVED"),
        ]
        for old, new in mutations:
            with self.subTest(old=old):
                self.assertTrue(osl.validate(self.text.replace(old, new)))

if __name__ == "__main__":
    unittest.main()
