#!/usr/bin/env python3
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path
from comprehension_test_scorer import ComprehensionError, score
from replay_sample_selector import ReplayError, TYPES, validate

ROOT = Path(__file__).resolve().parents[1]

def replay_payload():
    cases = []
    for sample_type in sorted(TYPES):
        for index in range(4):
            cases.append({"case_id": f"{sample_type}-{index}", "sample_type": sample_type, "selector_role": "independent_reviewer", "implementation_owner_role": "engineer", "model_hash": "sha256:model", "input_hash": "sha256:input", "sample_list_hash": "sha256:list", "decision_cutoff": "2025-01-01T00:00:00Z", "input_evidence_cutoff": "2024-12-31T00:00:00Z", "label_contract": {"contract_version": "OUTCOME-v1", "evaluation_horizon_days": 180, "primary_outcome": "risk_adjusted_contribution_profit", "success_threshold": {"minimum": 1}, "failure_threshold": {"maximum": 0}, "counterfactual_baseline": "do_not_enter", "label_source_ids": ["L1"], "label_confidence": "high", "locked_at": "2025-01-01T00:00:00Z", "result_revealed_at": "2025-07-02T00:00:00Z", "censored": False}})
    return {"cases": cases}

def comprehension_payload():
    responses = []
    roles = ["category_research", "operations", "supply_or_procurement", "capital_decision", "newcomer"]
    for role in roles:
        for index in range(4):
            responses.append({"participant_id": f"{role}-{index}", "role": role, "participated_in_implementation": False, "scores": {"decision": 2, "risk_confidence": 1, "top3_actions": 1, "do_not_do_yet": 1, "missing_data": 1, "go_stop": 1, "sovereignty": 1}, "redline_misread": False, "do_not_do_yet_misread": False, "stop_misread": False, "raw_response_id": f"RAW-{role}-{index}", "completion_seconds": 120})
    return {"responses": responses}

class ReplayAndComprehensionTests(unittest.TestCase):
    def test_replay_requires_five_types_four_each_and_role_isolation(self):
        result = validate(replay_payload())
        self.assertEqual(result["case_count"], 20)
        self.assertFalse(result["production_validity_proven"])
        bad = replay_payload(); bad["cases"][0]["selector_role"] = "engineer"
        with self.assertRaisesRegex(ReplayError, "implementer"):
            validate(bad)

    def test_replay_rejects_future_leakage_and_post_reveal_label_lock(self):
        bad = replay_payload(); bad["cases"][0]["input_evidence_cutoff"] = "2025-01-02T00:00:00Z"
        with self.assertRaisesRegex(ReplayError, "future evidence"):
            validate(bad)
        bad = replay_payload(); bad["cases"][0]["label_contract"]["locked_at"] = "2025-08-01T00:00:00Z"
        with self.assertRaisesRegex(ReplayError, "before result reveal"):
            validate(bad)

    def test_comprehension_formal_gate_and_severe_misread(self):
        result = score(comprehension_payload())
        self.assertEqual((result["status"], result["average_score"]), ("passed", "8"))
        bad = comprehension_payload(); bad["responses"][0]["stop_misread"] = True
        self.assertEqual(score(bad)["status"], "failed")

    def test_comprehension_rejects_implementers_and_role_shortfall(self):
        bad = comprehension_payload(); bad["responses"][0]["participated_in_implementation"] = True
        with self.assertRaisesRegex(ComprehensionError, "Implementers|implementers"):
            score(bad)
        bad = comprehension_payload(); bad["responses"] = bad["responses"][:-1]
        with self.assertRaisesRegex(ComprehensionError, "at least 20"):
            score(bad)

    def test_templates_remain_empty_external_gates(self):
        replay = json.loads((ROOT / "evaluations/opportunity-replay-template.json").read_text())
        comprehension = json.loads((ROOT / "evaluations/non-implementer-comprehension-template.json").read_text())
        self.assertEqual((replay["status"], replay["production_ready"], replay["cases"]), ("not_started", False, []))
        self.assertEqual((comprehension["status"], comprehension["production_ready"], comprehension["responses"]), ("not_started", False, []))

if __name__ == "__main__":
    unittest.main(verbosity=2)
