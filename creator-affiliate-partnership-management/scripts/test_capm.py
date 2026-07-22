#!/usr/bin/env python3
"""Executable CAPM domain tests: normal, boundary, failure, property and governance."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from affiliate_order_reconciliation import reconcile
from decision_state import validate as validate_state
from partnership_economics import commission_ceiling, fixed_fee_ceiling, partnership_return, program_profit
from portfolio_concentration import calculate as concentration
from reverse_funnel import calculate as funnel
from validate_cross_skill_handoff import validate as validate_handoff
from validate_historical_replay import validate as validate_replay
from validate_rights_contract import validate as validate_rights
from evaluate_capm_decision import evaluate as evaluate_decision
from validate_schema_instance import validate as validate_schema

quality_spec = importlib.util.spec_from_file_location("report_quality", ROOT.parents[0] / "scripts/evaluate_report_quality.py")
report_quality = importlib.util.module_from_spec(quality_spec); assert quality_spec and quality_spec.loader; quality_spec.loader.exec_module(report_quality)


def hashes() -> dict:
    return {"input_hash": "a" * 64, "output_hash": "b" * 64, "schema_hash": "c" * 64}


def envelope(**updates) -> dict:
    data = {"contract_id": "CAPM_to_AAMO_authorization", "contract_version": "1.0.0", "message_id": "m1", "idempotency_key": "capm-content-1-paid-v1",
            "correlation_id": "c1", "sender": {"skill": "creator-affiliate-partnership-management", "runtime_version": "CAPM-2026.07"},
            "receiver": {"skill": "advertising-analysis-measurement-optimization", "runtime_version": "AAMO-2026.08"},
            "object": {"canonical_id": "content-1", "object_type": "content", "object_version": "v1"},
            "scope": {"platform": "tiktok", "country": "US", "currency": "USD", "timezone": "America/New_York", "as_of_time": "2026-07-22T00:00:00Z"},
            "status": "proposed", "source_evidence_level": "S3", "causal_evidence_level": "C0",
            "claim_ids": ["cl1"], "evidence_ids": ["ev1"], "calculation_ids": ["calc1"],
            "allowed_uses": ["paid assessment"], "forbidden_uses": ["change rights"], "blocked_actions": [],
            "accepted_by_receiver": {"status": "pending", "reason": None, "checked_at": None}, "lineage": hashes(),
            "validity": {"valid_from": "2026-07-22T00:00:00Z", "expires_at": "2026-08-22T00:00:00Z", "recompute_trigger": ["rights change"]},
            "payload": {"rights_ready": True}}
    data.update(updates)
    return data


class EconomicsTests(unittest.TestCase):
    def test_commission_ceiling(self):
        r = commission_ceiling({"mature_net_revenue": 1000, "commission_base": 900, "target_profit": 100,
                                "non_commission_costs": [{"cost_id": "cogs", "amount": 400}, {"cost_id": "fulfillment", "amount": 100}]})
        self.assertAlmostEqual(r["max_commission_rate"], 400 / 900)

    def test_duplicate_cost_is_blocked(self):
        with self.assertRaisesRegex(ValueError, "duplicate cost_id"):
            commission_ceiling({"mature_net_revenue": 100, "commission_base": 100, "target_profit": 0,
                                "non_commission_costs": [{"cost_id": "refund", "amount": 10}, {"cost_id": "refund", "amount": 10}]})

    def test_negative_ceiling_blocks_cash(self):
        r = fixed_fee_ceiling({"mature_revenue": 100, "target_profit": 20, "non_fixed_costs": [{"cost_id": "all", "amount": 90}]})
        self.assertEqual((r["status"], r["max_fixed_fee"]), ("blocked", 0))

    def test_attributed_not_incremental(self):
        r = partnership_return({"controllable_investment": 100, "contribution": 150, "causal_evidence_level": "C0"})
        self.assertEqual((r["metric"], r["status"]), ("attributed_return", "inconclusive"))

    def test_incremental_requires_c2(self):
        r = partnership_return({"controllable_investment": 100, "contribution": 150, "causal_evidence_level": "C2"})
        self.assertEqual(r["metric"], "incremental_return")

    def test_program_interval_order(self):
        with self.assertRaisesRegex(ValueError, "low <= mid <= high"):
            program_profit({"incremental_contribution_low": 10, "incremental_contribution_mid": 5,
                            "incremental_contribution_high": 20, "program_costs": []})


class ModelTests(unittest.TestCase):
    def test_reverse_funnel(self):
        r = funnel({"target_deliveries": 20, "stages": [{"name": "reply", "rate": .2}, {"name": "publish", "rate": .5}]})
        self.assertEqual(r["required_candidates"], 200)

    def test_funnel_rejects_zero(self):
        with self.assertRaises(ValueError): funnel({"target_deliveries": 1, "stages": [{"name": "x", "rate": 0}]})

    def test_concentration_order_invariant(self):
        a = concentration({"basis": "profit", "values": {"a": 60, "b": 30, "c": 10}})
        b = concentration({"basis": "profit", "values": {"c": 10, "a": 60, "b": 30}})
        self.assertAlmostEqual(a["hhi"], b["hhi"])

    def test_order_conservation(self):
        r = reconcile({"raw_attributed": 500, "duplicate": 20, "confirmed_fraud": 30, "mature_refund_chargeback": 50, "mature_valid": 400, "pending": 0, "causal_evidence_level": "C0"})
        self.assertTrue(r["conservation"]); self.assertEqual(r["causal_status"], "inconclusive")

    def test_order_conservation_failure(self):
        with self.assertRaisesRegex(ValueError, "conservation"):
            reconcile({"raw_attributed": 10, "mature_valid": 9})


class RightsAndStateTests(unittest.TestCase):
    def rights(self):
        grid = {"platform": ["tiktok"], "use": ["organic"], "territory": ["US"], "edit": ["trim"], "identity_use": ["credit"], "ai_use": ["none"]}
        return {"rights_id": "r1", "content_id": "c1", "creator_id": "cr1", "start_at": "2026-01-01T00:00:00Z", "end_at": "2027-01-01T00:00:00Z", "as_of_time": "2026-07-22T00:00:00Z", "granted": grid, "requested": grid, "requested_actions": ["publish"], "evidence_ids": ["e1"]}

    def test_rights_exact_use(self): self.assertEqual(validate_rights(self.rights())["status"], "validated")

    def test_rights_do_not_infer_ai(self):
        data = self.rights(); data["requested"] = dict(data["requested"]); data["requested"]["ai_use"] = ["voice_clone"]
        self.assertEqual(validate_rights(data)["status"], "blocked")

    def test_expired_rights(self):
        data = self.rights(); data["as_of_time"] = "2028-01-01T00:00:00Z"
        self.assertIn("outside_valid_period", validate_rights(data)["blocked_reasons"])

    def test_progressive_superseded_action(self):
        parent = {"report_id": "r1", "object_id": "o1", "object_version": "v1", "current_actions": ["publish"]}
        data = {"report_id": "r2", "parent_report_id": "r1", "object_id": "o1", "object_version": "v2", "changed_fields": ["rights"], "new_evidence_ids": ["e2"], "affected_claims": ["c1"], "affected_calculations": ["calc1"], "preserved_constraints": ["g1"], "superseded_actions": ["publish"], "current_actions": ["publish"], "next_recompute_trigger": ["new rights"]}
        self.assertFalse(validate_state(data, parent)["valid"])

    def test_progressive_valid_parent_chain(self):
        parent = {"report_id": "r1", "object_id": "o1", "object_version": "v1", "current_actions": ["investigate"]}
        data = {"report_id": "r2", "parent_report_id": "r1", "object_id": "o1", "object_version": "v2", "changed_fields": ["rights"], "new_evidence_ids": ["e2"], "affected_claims": ["c1"], "affected_calculations": ["calc1"], "preserved_constraints": ["g1"], "superseded_actions": [], "current_actions": ["investigate", "renew"], "next_recompute_trigger": ["new rights"]}
        self.assertTrue(validate_state(data, parent)["valid"])


class IntegrationGovernanceTests(unittest.TestCase):
    def test_valid_envelope(self): self.assertTrue(validate_handoff(envelope())["valid"])

    def test_validated_needs_evidence(self):
        self.assertFalse(validate_handoff(envelope(status="validated", evidence_ids=[]))["valid"])

    def test_incremental_label_blocked_at_c0(self):
        self.assertFalse(validate_handoff(envelope(payload={"incremental_orders": 10}))["valid"])

    def test_allowed_forbidden_conflict(self):
        self.assertFalse(validate_handoff(envelope(allowed_uses=["x"], forbidden_uses=["x"]))["valid"])

    def test_idempotency_duplicate_is_blocked(self):
        self.assertFalse(validate_handoff(envelope(), {"capm-content-1-paid-v1"})["valid"])

    def test_expired_message_is_blocked(self):
        data = envelope(); data["scope"] = dict(data["scope"], as_of_time="2026-09-01T00:00:00Z")
        self.assertFalse(validate_handoff(data)["valid"])

    def test_unavailable_receiver_cannot_accept(self):
        self.assertFalse(validate_handoff(envelope(receiver={"skill": "LCR", "runtime_version": "unavailable"}, accepted_by_receiver={"status": "accepted", "reason": None, "checked_at": "2026-07-22T00:00:00Z"}))["valid"])

    def test_replay_gate_stays_controlled(self):
        r = validate_replay({"production_ready": False, "cases": []})
        self.assertEqual((r["production_ready"], r["maturity"]), (False, "controlled pilot"))

    def test_replay_rejects_formal_but_unreviewed_cases(self):
        case = {"case_id": "c", "case_type": "creator", "authorization_reference": "auth", "deidentified": True,
                "input_hash": "a"*64, "result_hash": "b"*64, "actual_outcome": "profit", "maturity_checked_at": "2026-07-22",
                "independent_review": True, "bias_and_calibration": "ok", "failure_or_exit_covered": True}
        self.assertFalse(validate_replay({"production_ready": True, "cases": [case, dict(case, case_id="c2", case_type="affiliate"), dict(case, case_id="c3")]})["valid"])

    def test_schemas_parse(self):
        for path in (ROOT / "schemas").glob("*.json"): json.loads(path.read_text(encoding="utf-8"))

    def test_schemas_execute_not_just_parse(self):
        cross = json.loads((ROOT / "schemas/cross_skill_envelope.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_schema(envelope(), cross), [])
        invalid = envelope(); invalid["scope"] = dict(invalid["scope"], country="USA")
        self.assertTrue(validate_schema(invalid, cross))
        rights_schema = json.loads((ROOT / "schemas/rights_record.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_schema(RightsAndStateTests().rights(), rights_schema), [])

    def test_required_governance_and_unique_kernels(self):
        required = [ROOT / "references/professional-depth-governance.md", ROOT / "references/skill-integration-protocol.md",
                    ROOT / "references/data-contract-and-automation.md", ROOT / "references/output-protocols/professional-report-delivery.md"]
        kernels = []
        paths = list(dict.fromkeys(required + list((ROOT / "references").glob("*.md"))))
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIn("专属决策内核", text, path)
            kernels.append(text.split("专属决策内核", 1)[1])
        self.assertEqual(len(kernels), len(set(kernels)))

    def test_evaluation_catalog(self):
        data = json.loads((ROOT / "evaluations/fixtures/evaluation-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(data["count"], 62)
        self.assertEqual(data["coverage"], {"solo": 16, "cross_skill": 14, "multi_turn": 12, "extreme": 20})
        cases = data["cases"]
        self.assertEqual(len({json.dumps(c["script_input"], sort_keys=True) for c in cases}), 62)
        self.assertEqual({c["mode"] for c in cases}, {"solo", "cross_skill", "multi_turn", "extreme"})
        for case in cases:
            result = evaluate_decision(case["script_input"])
            for field, expected in case["expected_output"].items():
                self.assertEqual(result[field], expected, (case["id"], field))
            self.assertTrue(case["required_assertions"] and case["forbidden"])
            if case["mode"] == "cross_skill": self.assertTrue(case["participants"])
            if case["mode"] == "multi_turn":
                self.assertGreaterEqual(len(case["turns"]), 4)
                self.assertEqual([turn["current_actions"][0] for turn in case["turns"]], case["expected_transition"])
                previous = None
                for turn in case["turns"]:
                    result = validate_state(turn, previous)
                    self.assertEqual(result["valid"], turn["expected_valid"], (case["id"], turn, result))
                    previous = turn
            if case["mode"] == "extreme":
                self.assertTrue(case["incident_controls"]["preserve_uncontested_obligations"])
                self.assertEqual(len(case["incident_controls"]["recovery_requires"]), 3)
        participants = {p for case in cases if case["mode"] == "cross_skill" for p in case["participants"]}
        self.assertEqual(participants, {"CIDM", "CIM", "VLB", "CIG", "AAMO", "LIFD", "PLCO"})
        transitions = {tuple(case["expected_transition"]) for case in cases if case["mode"] == "multi_turn"}
        self.assertEqual(len(transitions), 12)

    def test_all_five_golden_reports_pass_full_professional_gate(self):
        files = sorted((ROOT / "evaluations/golden").glob("*.md"))
        self.assertEqual(len(files), 5)
        for path in files:
            result = report_quality.score_report(path.read_text(encoding="utf-8"), "full")
            self.assertEqual((result["result"], result["score"]), ("PASS", 100.0), (path, result))

    def test_golden_critical_section_mutations_fail(self):
        text = (ROOT / "evaluations/golden/decision-memo.md").read_text(encoding="utf-8")
        for heading in ("证据与反证", "经济与计算", "主权与联动", "行动计划"):
            mutated = text.replace(f"## {heading}", f"## 已删除-{heading}")
            self.assertEqual(report_quality.score_report(mutated, "full")["result"], "FAIL", heading)


if __name__ == "__main__": unittest.main(verbosity=2)
