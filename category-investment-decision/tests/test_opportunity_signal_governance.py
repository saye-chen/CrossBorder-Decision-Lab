#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/opportunity_signals.py"
SPEC = importlib.util.spec_from_file_location("opportunity_signals", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def card() -> dict:
    return {
        "signal_id": "SIG-1", "signal_version": "OSL-v1",
        "decision_object": {"product_concept_id": "P1", "category_node": "N1", "parent_asin": "A1", "child_asin": "A2", "keyword_cluster_id": "K1", "country": "US", "platform": "Amazon", "currency": "USD"},
        "signal_type": "NEW_PRODUCT_BREAKOUT",
        "observation_window": {"start": "2026-05-01", "end": "2026-07-31"},
        "source_evidence_ids": ["E1"], "observed_facts": ["ten_week_series"],
        "derived_metrics": [{"name": "persistence", "value": "0.8"}], "assumptions": [],
        "counter_evidence": ["promotion checked"], "alternative_explanations": ["brand traffic"],
        "quality": {"completeness": 0.9, "freshness": "current", "independence": "independent", "sample_bias": "low"},
        "confidence": "medium", "allowed_use": ["candidate_generation"],
        "forbidden_use": ["automatic_score_override", "automatic_investment_action"],
        "validation_actions": ["profit recomputation"], "expiry_date": "2026-08-31", "status": "candidate",
        "source_family_id": "F1", "role": "support", "decision_impact": 0.8, "information_gain": 0.7, "analysis_cost": 1,
    }


class SignalGovernanceTests(unittest.TestCase):
    def test_valid_card_is_deterministically_bound(self):
        result = module.validate_signal_card(card(), as_of=date(2026, 8, 4))
        self.assertTrue(result["input_hash"].startswith("sha256:"))
        self.assertTrue(result["model_hash"].startswith("sha256:"))

    def test_missing_is_not_zero_and_error_fails_closed(self):
        mapped = module.adapt_field({}, {"source_field": "cr3", "kind": "ratio", "scale": "0-100"}, source="fixture", evidence_id="E1")
        self.assertIsNone(mapped["value"])
        self.assertEqual(module.normalize_ratio(45, "0-100"), module.Decimal("0.45"))
        with self.assertRaises(module.ContractError):
            module.adapt_field({"error": "rate_limit"}, {"source_field": "sales"}, source="fixture", evidence_id="E2")

    def test_missing_evidence_requires_blocked(self):
        fixture = card(); fixture["source_evidence_ids"] = []
        with self.assertRaisesRegex(module.ContractError, "missing raw evidence"):
            module.validate_signal_card(fixture, as_of=date(2026, 8, 4))
        fixture["status"] = "blocked"
        module.validate_signal_card(fixture, as_of=date(2026, 8, 4))

    def test_signal_cannot_take_investment_authority(self):
        fixture = card(); fixture["invest"] = True
        with self.assertRaisesRegex(module.ContractError, "no investment authority"):
            module.validate_signal_card(fixture, as_of=date(2026, 8, 4))

    def test_expiry_and_countercheck_gates(self):
        fixture = card(); fixture["expiry_date"] = "2026-08-01"
        with self.assertRaisesRegex(module.ContractError, "expired"):
            module.validate_signal_card(fixture, as_of=date(2026, 8, 4))
        fixture = card(); fixture["counter_evidence"] = []; fixture["alternative_explanations"] = []; fixture["confidence"] = "high"
        with self.assertRaisesRegex(module.ContractError, "low confidence"):
            module.validate_signal_card(fixture, as_of=date(2026, 8, 4))

    def test_prefilter_keeps_required_veto_and_deduplicates_family(self):
        base = card()
        required = copy.deepcopy(base); required["signal_type"] = "NEW_PRODUCT_BREAKOUT"
        duplicate = copy.deepcopy(base); duplicate["signal_id"] = "SIG-2"; duplicate["quality"]["completeness"] = 0.2
        playbook = {"decision_object": base["decision_object"], "required_signals": ["NEW_PRODUCT_BREAKOUT"], "veto_signals": ["RESOLVABLE_PRODUCT_GAP"]}
        result = module.prefilter([required, duplicate], playbook)
        self.assertEqual(result["composition_status"], "candidate")
        self.assertEqual(len(result["selected"]), 1)
        veto = copy.deepcopy(base); veto["signal_id"] = "SIG-3"; veto["signal_type"] = "RESOLVABLE_PRODUCT_GAP"; veto["source_family_id"] = "F2"
        self.assertEqual(module.prefilter([required, veto], playbook)["composition_status"], "blocked")

    def test_budget_exhaustion_is_partial_not_fake_complete(self):
        signals = []
        for index in range(4):
            item = copy.deepcopy(card()); item["signal_id"] = f"SIG-{index}"; item["source_family_id"] = f"F-{index}"
            signals.append(item)
        playbook = {"decision_object": card()["decision_object"], "required_signals": ["NEW_PRODUCT_BREAKOUT"]}
        result = module.prefilter(signals, playbook, {"max_signals": 3})
        self.assertEqual((result["composition_status"], result["execution_completion"]), ("inconclusive", "partial"))

    def test_recovery_queue_hard_order_and_weight_contract(self):
        weights = {"capital": "0.2", "irreversibility": "0.2", "time": "0.2", "blast_radius": "0.15", "decision_sensitivity": "0.15", "evidence_criticality": "0.1"}
        low_cash_safety = {"queue": "R0"}
        high_cash = {"queue": "R1", "weights": weights, "metrics": {key: 1 for key in weights}}
        self.assertLess(module.recovery_priority(low_cash_safety)[0], module.recovery_priority(high_cash)[0])
        bad = copy.deepcopy(high_cash); bad["weights"]["capital"] = "0.3"
        with self.assertRaisesRegex(module.ContractError, "sum to 1"):
            module.recovery_priority(bad)

    def test_evidence_quality_gate_blocks_missing_and_deduplicates_families(self):
        evidence = [
            {"evidence_id": "E1", "status": "current", "expiry_date": "2026-08-31", "source_family_id": "F1"},
            {"evidence_id": "E2", "status": "current", "expiry_date": "2026-08-31", "source_family_id": "F1"},
        ]
        result = module.evidence_quality_gate(evidence, ["E1", "E2"], as_of=date(2026, 8, 4))
        self.assertEqual((result["status"], result["independent_source_families"]), ("validated", 1))
        self.assertEqual(module.evidence_quality_gate(evidence, ["E1", "E3"], as_of=date(2026, 8, 4))["status"], "blocked")
        stale = copy.deepcopy(evidence); stale[0]["expiry_date"] = "2026-08-01"
        self.assertEqual(module.evidence_quality_gate(stale, ["E1"], as_of=date(2026, 8, 4))["status"], "inconclusive")

    def test_field_trap_registry_is_versioned_and_fail_closed(self):
        path = Path(__file__).resolve().parents[1] / "references/external-data-field-trap-registry.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(module.validate_field_trap_registry(payload)["trap_count"], 2)
        bad = copy.deepcopy(payload); bad["traps"][0]["fallback"] = "default_zero"
        with self.assertRaisesRegex(module.ContractError, "optimistic fallback"):
            module.validate_field_trap_registry(bad)

    def test_cidm_plco_packet_requires_proof_and_preserves_sovereignty(self):
        packet = {
            "packet_version": "CIDM-PLCO-v1", "decision_object": card()["decision_object"], "cidm_decision_id": "D1",
            "product_facts": [], "proof_assets": [{"proof_id": "P1", "type": "test"}], "unsupported_claims": [], "prohibited_claims": ["cures disease"],
            "target_segments": [], "purchase_jobs": [], "purchase_objections": [], "keyword_clusters": [], "validated_pain_points": [],
            "differentiation_claims": [{"claim": "tested load", "proof_id": "P1"}], "price_position": {}, "weakest_assumption": "conversion",
            "experiment_hypotheses": [], "allowed_use": ["listing_and_store_acceptance_design"], "forbidden_use": ["investment_score_override"],
        }
        self.assertEqual(module.validate_cidm_plco_packet(packet)["status"], "valid")
        bad = copy.deepcopy(packet); bad["differentiation_claims"][0]["proof_id"] = "MISSING"
        with self.assertRaisesRegex(module.ContractError, "existing proof_id"):
            module.validate_cidm_plco_packet(bad)
        bad = copy.deepcopy(packet); bad["invest"] = True
        with self.assertRaisesRegex(module.ContractError, "investment authority"):
            module.validate_cidm_plco_packet(bad)

    def test_rapid_card_preserves_decision_boundaries(self):
        rapid = {"decision": "谨慎小测", "confidence": "low", "lifecycle": "LC-2", "supporting_evidence": ["E1"], "counter_evidence": ["E2"], "weakest_assumption": "WTP", "priority_actions": ["a", "b", "c"], "do_not_do_yet": ["大货"], "missing_data": [{"field": "returns", "impact": "profit"}], "minimum_credible_validation": {"sample": 30}, "go": ["positive CM"], "stop": ["redline"]}
        self.assertEqual(module.validate_rapid_decision_card(rapid)["status"], "valid")
        rapid["do_not_do_yet"] = []
        with self.assertRaisesRegex(module.ContractError, "cannot be empty"):
            module.validate_rapid_decision_card(rapid)

    def test_dag_discloses_partial_failure_and_blocks_dependants(self):
        tasks = [
            {"task_id": "base", "dependencies": []},
            {"task_id": "reviews", "dependencies": ["base"]},
            {"task_id": "score", "dependencies": ["reviews"]},
        ]
        def runner(task):
            if task["task_id"] == "reviews":
                raise RuntimeError("rate limited")
            return {"evidence_id": "E-" + task["task_id"]}
        result = module.run_research_dag(tasks, runner, max_workers=2)
        states = {row["task_id"]: row["status"] for row in result["results"]}
        self.assertEqual(result["execution_completion"], "partial")
        self.assertEqual(states, {"base": "complete", "reviews": "failed", "score": "blocked"})

    def test_five_playbooks_are_governed_and_veto_is_noncompensatory(self):
        path = Path(__file__).resolve().parents[1] / "references/opportunity-combination-playbooks.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(module.validate_playbook_registry(payload)["playbook_count"], 5)
        playbook = payload["playbooks"][0]
        signal = card(); signal["status"] = "validated"
        result = module.compose_playbook(playbook, [signal], [])
        self.assertEqual((result["composition_status"], result["forbidden_output"]), ("proposed", "automatic_investment_action"))
        blocked = module.compose_playbook(playbook, [signal], ["negative_contribution_profit"])
        self.assertEqual(blocked["composition_status"], "blocked")

    def test_playbook_deduplicates_same_source_family(self):
        path = Path(__file__).resolve().parents[1] / "references/opportunity-combination-playbooks.json"
        playbook = json.loads(path.read_text(encoding="utf-8"))["playbooks"][0]
        one = card(); one["status"] = "validated"
        two = copy.deepcopy(one); two["signal_id"] = "SIG-2"; two["quality"]["completeness"] = 0.1
        result = module.compose_playbook(playbook, [one, two], [])
        self.assertEqual(result["selected_signal_ids"], ["SIG-1"])

    def test_runtime_mode_defaults_online_and_keeps_mcp_reserved(self):
        path = Path(__file__).resolve().parents[1] / "references/external-research-runtime-mode.json"
        runtime = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(runtime["default_research_mode"], "online_realtime")
        self.assertEqual(runtime["external_connector_mode"], "reserved_interface")
        self.assertFalse(runtime["mcp_required"])
        self.assertEqual(runtime["installed_provider_clients"], [])
        self.assertEqual(runtime["fallbacks"]["connector_unavailable"], "continue_online_research")
        self.assertEqual(runtime["fallbacks"]["connector_empty_response"], "unknown_not_zero")


if __name__ == "__main__":
    unittest.main(verbosity=2)
