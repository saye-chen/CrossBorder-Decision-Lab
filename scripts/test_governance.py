#!/usr/bin/env python3
"""Regression tests for change-impact governance and shared contract entrypoints."""
from __future__ import annotations
import importlib.util, json, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("impact", ROOT / "scripts/analyze_change_impact.py")
impact = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(impact)

class ImpactGovernance(unittest.TestCase):
    def test_nine_domain_maturity_ledger_is_explicit_and_replays_are_blocked(self):
        status = subprocess.run(["python3", str(ROOT/"scripts/validate_domain_maturity.py")], capture_output=True, text=True)
        self.assertEqual(status.returncode, 0, (status.stdout, status.stderr))
        ledger = json.loads((ROOT/"governance/domain-maturity-status.json").read_text(encoding="utf-8"))
        self.assertEqual(len(ledger["domains"]), 9)
        self.assertTrue(all(d["maturity"] == "controlled pilot" and d["l4"] == "not_passed" and d["authorized_real_cases"] == 0 for d in ledger["domains"]))
        for domain in ledger["domains"][:5]:
            replay = ROOT/domain["replay_manifest"]
            result = subprocess.run(["python3",str(ROOT/domain["skill"]/"scripts/validate_historical_replay.py"),str(replay)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,(domain["skill"],result.stdout,result.stderr))
            self.assertFalse(json.loads(result.stdout)["production_ready"])

    def test_cidm_scoring_change_closes_over_consumers_tests_and_goldens(self):
        result = impact.analyze(["category-investment-decision/references/scoring-model.md"])
        contract = result["affected_contracts"]["cidm-scoring"]
        self.assertIn("video-link-breakdown/references/cidm-integration.md", contract["consumers"])
        self.assertIn("scripts/test_domain_stress.py", contract["tests"])
        self.assertIn("evaluations/golden-reports/cidm-full.md", contract["evaluations"])

    def test_unknown_path_is_explicitly_unmapped(self):
        result = impact.analyze(["unknown/contract.md"])
        self.assertEqual(result["unmapped_paths"], ["unknown/contract.md"])

    def test_dot_prefixed_paths_are_preserved_and_exact_dot_slash_is_removed(self):
        workflow = ".github/workflows/expert-release.yml"
        result = impact.analyze([workflow, f"./{workflow}"])
        self.assertEqual(result["changed_paths"], [workflow])
        self.assertIn("repository-release-governance", result["affected_contracts"])
        self.assertNotIn(workflow, result["unmapped_paths"])

    def test_repository_release_governance_maps_its_release_chain(self):
        paths = [
            ".github/workflows/expert-release.yml",
            "governance/change-impact-manifest.json",
            "scripts/validate_repo.py",
            "scripts/test_full_repository_audit.py",
        ]
        result = impact.analyze(paths)
        contract = result["affected_contracts"]["repository-release-governance"]
        self.assertEqual(contract["changed"], sorted(paths))

    def test_tests_and_evaluations_are_watched_change_paths(self):
        paths = ["scripts/test_domain_stress.py", "evaluations/golden-reports/cim-full.md"]
        result = impact.analyze(paths)
        self.assertIn("decision-contract-core", result["affected_contracts"])
        self.assertIn("cim-monitoring-and-integration", result["affected_contracts"])
        self.assertEqual(result["unmapped_paths"], [])

    def test_runtime_and_vlb_handoff_consumers_include_new_release_dependencies(self):
        manifest = json.loads((ROOT / "governance/change-impact-manifest.json").read_text(encoding="utf-8"))
        contracts = manifest["contracts"]
        capm = "creator-affiliate-partnership-management"
        for contract_id in ("aamo-runtime", "lifd-runtime", "plco-runtime"):
            self.assertIn(capm, contracts[contract_id]["consumers"])
        workflow = ".github/workflows/expert-release.yml"
        self.assertIn(workflow, contracts["eight-skill-governance-baseline"]["consumers"])
        handoff_consumers = contracts["cidm-vlb-production-handoff"]["consumers"]
        self.assertIn("requirements-dev.txt", handoff_consumers)
        self.assertIn(workflow, handoff_consumers)

    def test_all_nine_domain_entrypoints_execute_shared_contract(self):
        payload = {"mode":"single", "decision_type":"content_creative", "decision_owner":"video-link-breakdown",
                   "participating_skills":["video-link-breakdown"], "runtime_versions":{"video-link-breakdown":"VLB-2026.10"},
                   "participant_results":{"video-link-breakdown":{"status":"contributed"}},
                   "professional_core":{"object_boundary":"o","conclusion":"Test","evidence_summary":["E1"],"counterevidence":["E2"],"commercial_constraints":["budget"],"risks_and_redlines":["risk"],"actions":["test"],"success_conditions":["pass"],"stop_conditions":["stop"],"limitations_and_missing_data":["missing"]},
                   "objects":[{"canonical_id":"o","country":"US","platform":"P","category":"C","lifecycle":"L"}],
                   "evidence":[{"id":"E1","source_skill":"video-link-breakdown","evidence_type":"authorized_fixture","evidence_class":"direct","source_ref":"fixture:E1","observed_at":"2026-07-17","fingerprint":"fixture-E1"}],
                   "claims":[{"id":"C1","producer_skill":"video-link-breakdown","claim_domain":"content_creative","state":"validated","object_id":"o","evidence_ids":["E1"],"allowed_uses":["decision_support"],"forbidden_uses":[],"effective_now":True}],"calculations":[],"required_calculation_ids":[],"unresolved_redlines":[],"adjustments":[]}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "contract.json"; path.write_text(json.dumps(payload), encoding="utf-8")
            for skill in ["category-investment-decision","competitive-intelligence-monitoring","video-link-breakdown","consumer-insights-customer-growth","advertising-analysis-measurement-optimization","logistics-inventory-fulfillment-decision","platform-store-listing-conversion","creator-affiliate-partnership-management","marketing-brand-campaign-management"]:
                result = subprocess.run(["python3", str(ROOT/skill/"scripts/validate_decision_contract.py"), str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, (skill, result.stderr))

if __name__ == "__main__": unittest.main(verbosity=2)
