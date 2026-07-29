#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from compute_parameter_change_impact import compute
from ppfc_common import PPFCError
from update_continuous_decision import update, validate_state
from validate_professional_report import validate as validate_report


def graph() -> dict:
    return {
        "nodes": [
            {"id": "fee", "on_change": "expire"}, {"id": "unit_cost", "on_change": "recompute"},
            {"id": "price", "on_change": "recompute"}, {"id": "profit", "on_change": "recompute"},
            {"id": "roas", "on_change": "recompute"}, {"id": "cash", "on_change": "recompute"},
            {"id": "action", "on_change": "reaccept"}, {"id": "report", "on_change": "recompute"},
            {"id": "unrelated_sku", "on_change": "recompute"},
        ],
        "edges": [
            {"from": "fee", "to": "unit_cost"}, {"from": "unit_cost", "to": "price"},
            {"from": "price", "to": "profit"}, {"from": "profit", "to": "roas"},
            {"from": "profit", "to": "cash"}, {"from": "roas", "to": "action"},
            {"from": "cash", "to": "action"}, {"from": "action", "to": "report"},
        ],
        "changed_ids": ["fee"], "input_hash": "sha256:old", "parameter_snapshot_id": "ps2", "model_version": "m1",
    }


def state() -> dict:
    return {
        "chain_id": "chain-1", "current_decision_id": "d1", "current_version": "v1",
        "object_ref": {"object_id": "sku-1", "object_version": "v1"},
        "history": [{"decision_id": "d1", "version": "v1", "status": "validated", "is_current": True, "input_hash": "sha256:old", "parameter_snapshot_id": "ps1", "model_version": "m1", "conclusion": "price 20", "created_at": "2026-07-28T00:00:00Z", "supersedes": None}],
        "turns": [], "dependencies": {}, "pending_acceptance": [], "unresolved_items": [],
        "lineage": {"state_hash": "sha256:state1", "runtime_version": "PPFC-2026.07"},
    }


def event(kind: str = "parameter_refresh") -> dict:
    return {"event_id": "e1", "turn_id": "t2", "event_type": kind, "occurred_at": "2026-07-29T00:00:00Z", "changed_ids": ["fee"] if kind == "parameter_refresh" else [], "old_input_hash": "sha256:old", "new_input_hash": "sha256:new" if kind == "parameter_refresh" else "sha256:old", "reason": "fee changed", "actor": "finance-owner", "idempotency_key": "idem-0002", "target_version": None}


def new_decision() -> dict:
    return {"decision_id": "d1", "version": "v2", "status": "proposed", "input_hash": "sha256:new", "parameter_snapshot_id": "ps2", "model_version": "m1", "conclusion": "price 21", "created_at": "2026-07-29T00:01:00Z"}


def report() -> dict:
    external = ["external_write", "change_price", "change_budget", "place_order", "release_funds"]
    return {
        "report_id": "r1", "report_version": "PPFC-REPORT-2026.07.1", "report_type": "decision_card",
        "decision_id": "d1", "decision_version": "v2", "status": "proposed", "is_current": True,
        "object_ref": {"object_id": "sku-1"}, "scope": {"country": "US"}, "as_of_time": "2026-07-29T00:00:00Z",
        "current_conclusion": "controlled price candidate", "history_refs": ["d1@v1"], "evidence": ["E1"],
        "counterevidence": ["demand uncertainty"], "conflicts": [], "missing_data": ["real outcome"],
        "baseline": {"price": "20"}, "candidates": [{"price": "21"}], "calculations": [{"id": "c1"}],
        "parameter_snapshot_id": "ps2", "economics": {"contribution": "2"}, "metrics": [{"code": "BREAK_EVEN_ROAS"}],
        "sensitivity": {"fee": "flip at 0.2"}, "attribution_incrementality": {"incrementality": "not_claimed"},
        "actions": [{"action": "controlled_test"}], "success_conditions": ["contribution positive"],
        "stop_conditions": ["cash breach"], "rollback_conditions": ["fee changes"], "exit_conditions": ["negative NRV"],
        "allowed_uses": ["decision_support"], "forbidden_uses": external,
        "lineage": {"input_hash": "sha256:new", "output_hash": "sha256:out", "model_version": "m1", "runtime_version": "PPFC-2026.07", "supersedes": "r0"},
    }


class OutputContinuityTests(unittest.TestCase):
    def test_selective_closure_preserves_unrelated_object(self):
        result = compute(graph())
        self.assertIn("action", result["affected_ids"])
        self.assertEqual(result["unaffected_ids"], ["unrelated_sku"])

    def test_closure_is_order_invariant(self):
        first = compute(graph())
        payload = graph(); payload["nodes"].reverse(); payload["edges"].reverse()
        self.assertEqual(first, compute(payload))

    def test_unknown_and_cycle_fail_closed(self):
        payload = graph(); payload["changed_ids"] = ["missing"]
        with self.assertRaises(PPFCError): compute(payload)
        payload = graph(); payload["edges"].append({"from": "report", "to": "fee"})
        with self.assertRaises(PPFCError): compute(payload)

    def test_parameter_followup_creates_new_current_and_reacceptance(self):
        result = update({"state": state(), "event": event(), "new_decision": new_decision()})
        current = [item for item in result["state"]["history"] if item["is_current"]]
        self.assertEqual(len(current), 1); self.assertEqual(current[0]["version"], "v2")
        self.assertIn("d1", result["state"]["pending_acceptance"])

    def test_history_is_not_overwritten(self):
        result = update({"state": state(), "event": event(), "new_decision": new_decision()})["state"]
        self.assertEqual(result["history"][0]["conclusion"], "price 20")
        self.assertEqual(result["history"][0]["status"], "superseded")

    def test_idempotent_turn_does_not_duplicate_history(self):
        first = update({"state": state(), "event": event(), "new_decision": new_decision()})["state"]
        replay = update({"state": first, "event": event(), "new_decision": new_decision()})
        self.assertTrue(replay["idempotent_replay"]); self.assertEqual(len(replay["state"]["history"]), 2)

    def test_clarification_cannot_change_input(self):
        payload = event("clarification"); payload["new_input_hash"] = "sha256:changed"
        with self.assertRaises(PPFCError): update({"state": state(), "event": payload})

    def test_two_current_versions_fail(self):
        payload = state(); duplicate = copy.deepcopy(payload["history"][0]); duplicate["version"] = "v2"
        payload["history"].append(duplicate)
        with self.assertRaises(PPFCError): validate_state(payload)

    def test_recalculation_requires_result_and_matching_hash(self):
        with self.assertRaises(PPFCError): update({"state": state(), "event": event()})
        decision = new_decision(); decision["input_hash"] = "sha256:wrong"
        with self.assertRaises(PPFCError): update({"state": state(), "event": event(), "new_decision": decision})

    def test_complete_professional_report(self):
        self.assertTrue(validate_report(report())["valid"])

    def test_report_rejects_missing_stop_or_external_write(self):
        payload = report(); payload["stop_conditions"] = []
        with self.assertRaises(PPFCError): validate_report(payload)
        payload = report(); payload["forbidden_uses"].remove("change_price")
        with self.assertRaises(PPFCError): validate_report(payload)

    def test_validated_report_cannot_hide_missing_data(self):
        payload = report(); payload["status"] = "validated"
        with self.assertRaises(PPFCError): validate_report(payload)


if __name__ == "__main__": unittest.main()
