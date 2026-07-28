#!/usr/bin/env python3
"""Twenty-four WP7 expert continuity, report, rollback and impact assertions."""
from __future__ import annotations
import copy
import importlib.util
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
def load(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file);mod=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(mod);return mod
state_mod=load("pipm_state","update_continuous_product_decision.py")
impact_mod=load("pipm_impact7","compute_decision_impact_closure.py")
report_mod=load("pipm_report","validate_professional_report.py")

def state():
    return {"chain_id":"CH1","chain_revision":0,"next_sequence":1,"current_decision_id":"D1","current_version":"v1","object_ref":{"object_id":"P1","object_version":"p1"},"product_lifecycle_stage":"PLC3","decision_state":"proposed","acceptance_state":"pending","action_state":"proposed","history":[{"decision_id":"D1","version":"v1","status":"proposed","is_current":True,"object_version":"p1","input_hash":"sha256:a","created_at":"2026-07-28T00:00:00Z","supersedes":None}],"events":[],"dependencies":{},"pending_acceptance":[],"unresolved_items":[],"lineage":{"state_hash":"sha256:x","runtime_version":"PIPM-2026.01"}}
def event(kind="evidence_update"):
    return {"event_id":"E1","turn_id":"T1","sequence":1,"expected_revision":0,"idempotency_key":"idem-0001","event_type":kind,"occurred_at":"2026-07-28T01:00:00Z","recorded_at":"2026-07-28T01:01:00Z","object_id":"P1","object_version":"p1","old_input_hash":"sha256:a","new_input_hash":"sha256:b" if kind in state_mod.RECALCULATING else "sha256:a","changed_node_ids":["EV1"] if kind in state_mod.RECALCULATING else [],"external_write":False}
def new():
    return {"decision_id":"D2","version":"v2","status":"proposed","object_version":"p1","input_hash":"sha256:b","created_at":"2026-07-28T01:01:00Z"}
def payload(kind="evidence_update"):
    x={"state":state(),"event":event(kind)}
    if kind in state_mod.RECALCULATING:x["new_decision"]=new()
    return x
def graph():
    return {"nodes":{"EV1":{"type":"evidence","object_version":"p1"},"C1":{"type":"claim","object_version":"p1"},"K1":{"type":"calculation","object_version":"p1"},"S1":{"type":"specification","object_version":"p1"},"R1":{"type":"report","object_version":"p1"},"A1":{"type":"action","object_version":"p1"},"X1":{"type":"acceptance","object_version":"p1"},"KEEP":{"type":"claim","object_version":"p1"}},"edges":{"EV1":["C1"],"C1":["K1"],"K1":["S1"],"S1":["R1"],"R1":["A1","X1"],"A1":[],"X1":[],"KEEP":[]},"changed_node_ids":["EV1"]}
def report(kind="product_definition"):
    specifics={k:"fixture" for k in report_mod.REQUIRED[kind]}
    r={"report_id":"R1","report_type":kind,"chain_id":"CH1","decision_id":"D1","is_current":True,"object_ref":{"object_id":"P1","object_version":"p1"},"scope":{"country":"US"},"as_of_time":"2026-07-28T00:00:00Z","recorded_at":"2026-07-28T01:00:00Z","decision_state":"proposed","current_conclusion":"controlled candidate","history_refs":["D0@v0"],"evidence":[{"id":"EV1"}],"counterevidence":[{"id":"EV2"}],"conflicts":[],"missing_and_expired":[],"calculations":[{"id":"K1"}],"no_action":{"effect":"delay"},"candidates":[{"id":"recommended"}],"dependencies":["D06"],"actions":[{"state":"proposed"}],"success_conditions":["test passes"],"stop_conditions":["redline"],"rollback":{"restore":"v0"},"exit_conditions":["retire"],"allowed_uses":["decision_support"],"forbidden_uses":["external_execution"],"specific_content":specifics,"lineage":{"input_hash":"sha256:a","report_hash":"sha256:","runtime_version":"PIPM-2026.01"},"maturity":"controlled pilot","external_write":False}
    r["lineage"]["report_hash"]=report_mod.report_hash(r);return r

class WP7(unittest.TestCase):
    def blocked(self,x,marker):
        with self.assertRaisesRegex(state_mod.StateError,marker):state_mod.update(x)
    def test_01_two_current_block(self):
        x=payload();x["state"]["history"].append({**x["state"]["history"][0],"decision_id":"DX"})
        self.blocked(x,"exactly one")
    def test_02_pointer_mismatch_block(self):
        x=payload();x["state"]["current_decision_id"]="DX";self.blocked(x,"pointer")
    def test_03_idempotent_retry_noop(self):
        first=state_mod.update(payload());x=payload();x["state"]=first["state"];self.assertTrue(state_mod.update(x)["idempotent_replay"])
    def test_04_stale_revision_block(self):
        x=payload();x["event"]["expected_revision"]=2;self.blocked(x,"revision")
    def test_05_out_of_order_sequence_block(self):
        x=payload();x["event"]["sequence"]=3;self.blocked(x,"sequence")
    def test_06_clarification_cannot_change_hash(self):
        x=payload("clarification");x["event"]["new_input_hash"]="sha256:z";self.blocked(x,"non-calculating")
    def test_07_scenario_requires_new_immutable_version(self):
        x=payload("scenario_override");x["new_decision"].update(decision_id="D1",version="v1");self.blocked(x,"immutable")
    def test_08_selective_closure_preserves_unaffected(self):
        out=impact_mod.compute(graph());self.assertEqual(out["preserved"],["KEEP"]);self.assertIn("R1",out["recomputed"])
    def test_09_evidence_withdrawal_expires_downstream(self):
        out=impact_mod.compute(graph());self.assertEqual(out["expired"],["A1","C1","R1","X1"])
    def test_10_cycle_blocks(self):
        x=graph();x["edges"]["X1"]=["EV1"]
        with self.assertRaisesRegex(impact_mod.ImpactError,"cycle"):impact_mod.compute(x)
    def test_11_orphan_blocks(self):
        x=graph();x["edges"]["EV1"].append("MISSING")
        with self.assertRaisesRegex(impact_mod.ImpactError,"orphan"):impact_mod.compute(x)
    def test_12_cross_version_blocks(self):
        x=graph();x["nodes"]["X1"]["object_version"]="p2"
        with self.assertRaisesRegex(impact_mod.ImpactError,"cross-version"):impact_mod.compute(x)
    def test_13_product_change_sets_reacceptance(self):
        x=payload("product_fact_change");x["event"]["object_version"]="p2";x["new_decision"]["object_version"]="p2"
        self.assertEqual(state_mod.update(x)["state"]["acceptance_state"],"pending")
    def test_14_acceptance_does_not_change_decision(self):
        out=state_mod.update(payload("cross_domain_accept"))["state"];self.assertEqual(out["decision_state"],"proposed");self.assertEqual(out["acceptance_state"],"accepted")
    def test_15_retired_object_cannot_reactivate(self):
        x=payload("retire");x["state"]["product_lifecycle_stage"]="PLC8";self.blocked(x,"retired")
    def test_16_rollback_never_reactivates_old_record(self):
        x=payload("rollback");x["rollback_plan"]={"executed_actions":[],"compensating_actions":[],"residual_exposure":[]}
        out=state_mod.update(x)["state"];self.assertFalse(out["history"][0]["is_current"]);self.assertEqual(len(out["history"]),2)
    def test_17_executed_action_requires_compensation(self):
        x=payload("rollback");x["rollback_plan"]={"executed_actions":["sample_sent"],"compensating_actions":[],"residual_exposure":[]};self.blocked(x,"compensation")
    def test_18_late_event_is_marked_not_backwritten(self):
        x=payload();x["state"]["events"]=[{**event("clarification"),"idempotency_key":"older-0002","occurred_at":"2026-07-28T02:00:00Z"}]
        out=state_mod.update(x)["state"];self.assertTrue(out["events"][-1]["late_arrival"]);self.assertEqual(len(out["history"]),2)
    def test_19_partial_failure_preserves_valid_nodes(self):
        x=graph();x["nodes"]["S1"]["criticality"]="safety_critical";out=impact_mod.compute(x);self.assertEqual(out["preserved"],["KEEP"]);self.assertEqual(out["blocked"],["S1"])
    def test_20_missing_specialized_report_fields_block(self):
        r=report();r["specific_content"].pop("non_goals");r["lineage"]["report_hash"]=report_mod.report_hash(r)
        self.assertTrue(any("missing_specialized" in e for e in report_mod.validate(r)))
    def test_21_report_hash_mismatch_blocks(self):
        r=report();r["current_conclusion"]="tampered";self.assertIn("report_hash_mismatch",report_mod.validate(r))
    def test_22_all_nine_report_types_have_distinct_contracts(self):
        self.assertEqual(len(report_mod.REQUIRED),9);self.assertEqual(len({frozenset(v) for v in report_mod.REQUIRED.values()}),9)
        for kind in report_mod.REQUIRED:self.assertEqual(report_mod.validate(report(kind)),[])
    def test_23_incident_stops_action_and_blocks_decision(self):
        out=state_mod.update(payload("incident_or_recall"))["state"];self.assertEqual((out["decision_state"],out["action_state"]),("blocked","stopped"))
    def test_24_external_execution_and_l4_claim_block(self):
        r=report();r["external_write"]=True;r["maturity"]="production"
        errors=report_mod.validate(r);self.assertTrue(any("schema" in e for e in errors))

if __name__=="__main__":unittest.main(verbosity=2)
