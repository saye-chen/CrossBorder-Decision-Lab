#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/candidate_funnel.py"
SPEC = importlib.util.spec_from_file_location("candidate_funnel", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def packet(stage="SCREEN", status="candidate"):
    mode = "SCAN" if stage in {"DISCOVERY", "SCREEN"} else "DILIGENCE"
    return {
        "contract_version": "CIDM-CANDIDATE-FUNNEL-v1",
        "task_card": {"task_id":"T1","country":"US","platform":"Amazon","product_scope":"pet fountain","lifecycle":"LC-1","price_band":"35-49 USD","seller_profile":"seller-agnostic","capital_limit":"unknown","loss_limit":"unknown","time_window":"2026-Q3","risk_posture":"compliance-first","objective":"validate opportunity"},
        "candidate": {
            "candidate_id":"C1","decision_object":{"product_concept_id":"P1","country":"US","platform":"Amazon"},
            "stage":stage,"research_mode":mode,"status":status,"source_evidence_ids":["E1","E2"],"source_family_ids":["F1","F2"],
            "promotion_reasons":["directional demand"],"rejection_reasons":[],"missing_data":["supplier quote"],"weakest_assumption":"willingness to pay",
            "next_validation":["obtain quote"],"stop_conditions":["IP redline"],"reentry_conditions":["new independent evidence"],
            "supply_chain_gate":{"status":"pass","checks":["mature supply"],"reasons":[],"formal_review_complete":False,"claim":"rapid_screen_only"},
            "ip_compliance_gate":{"status":"pass","checks":["obvious risk scan"],"reasons":[],"formal_review_complete":False,"claim":"rapid_screen_only"},
            "cross_platform_evidence":[{"relationship":"CONFIRMATION","platforms":["Amazon","TikTok Shop"],"observation_window":{"start":"2026-06-01","end":"2026-07-31"},"evidence_ids":["E1","E2"],"source_family_ids":["F1","F2"],"comparable_basis":"purchase intent","alternative_explanations":["shared campaign"],"decision_effect":"supports demand only"}]
        }
    }


class CandidateFunnelTests(unittest.TestCase):
    def test_valid_screen_packet(self):
        self.assertEqual(module.validate_candidate(packet())["status"], "valid")

    def test_confirmation_requires_independent_families(self):
        data = packet(); data["candidate"]["cross_platform_evidence"][0]["source_family_ids"] = ["F1"]
        with self.assertRaisesRegex(module.FunnelError, "two independent"):
            module.validate_candidate(data)

    def test_blocked_early_gate_cannot_optimistically_advance(self):
        data = packet(); data["candidate"]["ip_compliance_gate"] = {"status":"blocked","checks":["character IP"],"reasons":["unlicensed character"],"formal_review_complete":False}
        with self.assertRaisesRegex(module.FunnelError, "blocked or rejected"):
            module.validate_candidate(data)

    def test_stage_controls_research_mode_and_transitions(self):
        result = module.transition(packet(), "DEEP_DIVE", "screen passed")
        self.assertEqual((result["candidate"]["stage"], result["candidate"]["research_mode"]), ("DEEP_DIVE", "DILIGENCE"))
        with self.assertRaisesRegex(module.FunnelError, "forbidden"):
            module.transition(packet("DISCOVERY"), "INVESTMENT_CANDIDATE", "skip")

    def test_investment_candidate_requires_erdg_and_passed_gates(self):
        data = packet("INVESTMENT_CANDIDATE", "conditional_entry")
        with self.assertRaisesRegex(module.FunnelError, "ERDG passed"):
            module.validate_candidate(data)
        data["erdg_validation"] = {"status":"passed","contract":"ERDG-CONTRACT-2026.07"}
        data["candidate"]["supply_chain_gate"]["formal_review_complete"] = True
        data["candidate"]["ip_compliance_gate"]["formal_review_complete"] = True
        data["candidate"]["supply_chain_gate"]["evidence_ids"] = ["SC1"]
        data["candidate"]["ip_compliance_gate"]["evidence_ids"] = ["IP1"]
        self.assertEqual(module.validate_candidate(data)["stage"], "INVESTMENT_CANDIDATE")

    def test_unresolved_cross_platform_conflict_blocks_investment(self):
        data = packet("INVESTMENT_CANDIDATE", "conditional_entry")
        data["erdg_validation"] = {"status":"passed","contract":"ERDG-CONTRACT-2026.07"}
        data["candidate"]["supply_chain_gate"]["formal_review_complete"] = True
        data["candidate"]["ip_compliance_gate"]["formal_review_complete"] = True
        data["candidate"]["supply_chain_gate"]["evidence_ids"] = ["SC1"]
        data["candidate"]["ip_compliance_gate"]["evidence_ids"] = ["IP1"]
        data["candidate"]["cross_platform_evidence"] = [{"relationship":"CONFLICT","resolution_status":"open","platforms":["Amazon","TikTok Shop"],"observation_window":{"start":"2026-06-01","end":"2026-07-31"},"evidence_ids":["E1","E2"],"source_family_ids":["F1","F2"],"comparable_basis":"purchase intent","alternative_explanations":["channel fit"],"decision_effect":"lower confidence"}]
        with self.assertRaisesRegex(module.FunnelError, "unresolved"):
            module.validate_candidate(data)

    def test_handoff_is_proof_bound_and_never_writes(self):
        data = packet("INVESTMENT_CANDIDATE", "proposed_test")
        data["erdg_validation"] = {"status":"passed","contract":"ERDG-CONTRACT-2026.07"}
        data["candidate"]["supply_chain_gate"]["formal_review_complete"] = True
        data["candidate"]["ip_compliance_gate"]["formal_review_complete"] = True
        data["candidate"]["supply_chain_gate"]["evidence_ids"] = ["SC1"]
        data["candidate"]["ip_compliance_gate"]["evidence_ids"] = ["IP1"]
        data["handoff"] = {"destinations":["PLCO","AAMO"],"validated_facts":[{"proof_id":"P1","fact":"tested size"}],"proof_bound_claims":[{"claim":"tested size","proof_id":"P1"}],"prohibited_claims":["medical"],"target_segments":["multi-cat homes"],"purchase_jobs":["easy cleaning"],"price_profit_redlines":["positive contribution"],"hypotheses":["demo converts"],"success_conditions":["pre-registered gate"],"stop_conditions":["negative contribution"],"rollback":["restore prior state"],"outcome_writeback":"CIDM decision cycle","external_write":False}
        result = module.compile_handoff(data)
        self.assertEqual((result["status"], result["external_write"]), ("proposed", False))
        bad = copy.deepcopy(data); bad["handoff"]["external_write"] = True
        with self.assertRaisesRegex(module.FunnelError, "cannot authorize"):
            module.compile_handoff(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
