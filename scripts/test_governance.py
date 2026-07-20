#!/usr/bin/env python3
"""Regression tests for change-impact governance and shared contract entrypoints."""
from __future__ import annotations
import importlib.util, json, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("impact", ROOT / "scripts/analyze_change_impact.py")
impact = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(impact)

class ImpactGovernance(unittest.TestCase):
    def test_cidm_scoring_change_closes_over_consumers_tests_and_goldens(self):
        result = impact.analyze(["category-investment-decision/references/scoring-model.md"])
        contract = result["affected_contracts"]["cidm-scoring"]
        self.assertIn("video-link-breakdown/references/cidm-integration.md", contract["consumers"])
        self.assertIn("scripts/test_domain_stress.py", contract["tests"])
        self.assertIn("evaluations/golden-reports/cidm-full.md", contract["evaluations"])

    def test_unknown_path_is_explicitly_unmapped(self):
        result = impact.analyze(["unknown/contract.md"])
        self.assertEqual(result["unmapped_paths"], ["unknown/contract.md"])

    def test_all_seven_domain_entrypoints_execute_shared_contract(self):
        payload = {"mode":"single", "decision_type":"content_creative", "decision_owner":"video-link-breakdown",
                   "participating_skills":["video-link-breakdown"], "runtime_versions":{"video-link-breakdown":"VLB-2026.09"},
                   "participant_results":{"video-link-breakdown":{"status":"contributed"}},
                   "professional_core":{"object_boundary":"o","conclusion":"Test","evidence_summary":["E1"],"counterevidence":["E2"],"commercial_constraints":["budget"],"risks_and_redlines":["risk"],"actions":["test"],"success_conditions":["pass"],"stop_conditions":["stop"],"limitations_and_missing_data":["missing"]},
                   "objects":[{"canonical_id":"o","country":"US","platform":"P","category":"C","lifecycle":"L"}],
                   "evidence":[{"id":"E1","source_skill":"video-link-breakdown","evidence_type":"authorized_fixture","evidence_class":"direct","source_ref":"fixture:E1","observed_at":"2026-07-17","fingerprint":"fixture-E1"}],
                   "claims":[{"id":"C1","producer_skill":"video-link-breakdown","claim_domain":"content_creative","state":"validated","object_id":"o","evidence_ids":["E1"],"allowed_uses":["decision_support"],"forbidden_uses":[],"effective_now":True}],"calculations":[],"required_calculation_ids":[],"unresolved_redlines":[],"adjustments":[]}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "contract.json"; path.write_text(json.dumps(payload), encoding="utf-8")
            for skill in ["category-investment-decision","competitive-intelligence-monitoring","video-link-breakdown","consumer-insights-customer-growth","advertising-analysis-measurement-optimization","logistics-inventory-fulfillment-decision","platform-store-listing-conversion"]:
                result = subprocess.run(["python3", str(ROOT/skill/"scripts/validate_decision_contract.py"), str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, (skill, result.stderr))

if __name__ == "__main__": unittest.main(verbosity=2)
