#!/usr/bin/env python3
from __future__ import annotations
import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"scripts"))
from copo import *  # noqa: E402,F403

H="a"*64
LEDGER=json.loads((ROOT/"evaluations/fixtures/trusted-packet-ledger.json").read_text())
def receipt(owner, decision="accepted"):
    authority=DOMAIN_BY_ID[owner]["owned_decision_types"][0] if owner in DOMAIN_BY_ID else {"F01":"causal_qualification","F02":"localization_comparability","ERDG":"governance_validation"}[owner]
    governance={"schema_version":"2.0.0","runtime_version":"COPO-2026.07","object_version":"v1","as_of_time":"2026-08-11T00:00:00Z","owner":owner,"status":decision,"allowed_uses":["receipt_validation"],"forbidden_uses":["external_write"],"input_hash":H,"content_hash":H,"state_hash":H}
    r={"receipt_id":f"R-{owner}","request_ref":"Q","cycle_id":"C1","scope_ref":"S1","owner":owner,"owner_authority":authority,"decision":decision,"accepted_fields":[f"A-{owner}"],"allowed_uses":["operating_posture_synthesis","approved_action_sequencing"],"packet_version":1,"expires_at":"2027-01-01T00:00:00Z","governance":governance,"external_write":False};r["packet_hash"]=canonical_hash(receipt_signed_payload(r));governance["content_hash"]=r["packet_hash"];return r

def qualify(route, receipts, gates, f02="comparable", requested="scale"):
    return posture_qualification(route,receipts,gates,f02,requested,cycle_id="C1",now="2026-08-11T00:00:00Z",trusted_ledger=LEDGER)

def scope_fixture():
    g=governance_metadata("D14","draft","2026-08-11T00:00:00Z","scope")
    return {"scope_id":"S1","schema_version":"2.0.0","runtime_version":"COPO-2026.07","scope_version":1,"cycle_id":"C1","object":{"object_id":"O1","object_version":"v1","object_type":"portfolio","granularity":"sku","included":["A"],"excluded":[]},"market":{"country":"US","jurisdiction":"US","platform":"Amazon","site":"US","store":"S","channel":"marketplace","locale":"en-US"},"time":{"as_of_time":"2026-08-11T00:00:00Z","timezone":"UTC","baseline":{"start":"2026-06-01T00:00:00Z","end":"2026-06-30T00:00:00Z"},"observation":{"start":"2026-07-01T00:00:00Z","end":"2026-07-31T00:00:00Z"},"diagnostic":{"start":"2026-08-01T00:00:00Z","end":"2026-08-10T00:00:00Z"},"maturity":{"start":"2026-08-12T00:00:00Z","end":"2026-09-01T00:00:00Z"},"decision_valid_until":"2026-08-20T00:00:00Z"},"economics":{"currency":"USD","fx_as_of":"2026-08-11T00:00:00Z","tax_basis":"net","settlement_cycle":"14d","unit":"order","profit_level":"contribution"},"comparison":{"method":"mom","comparability":"comparable","reasons":[]},"data_quality":{"completeness":"complete","freshness":"current","authorization":"authorized","missing":[],"conflicts":[]},"lineage":{"input_snapshot_ref":"SNAP","input_hash":H,"state_hash":H},"governance":g,"external_write":False}

class TestCopo(unittest.TestCase):
    def test_scope_schema_and_time_semantics_are_one_unbypassable_entrypoint(self):
        validate_scope(scope_fixture())
        bad=scope_fixture();bad["time"]["baseline"]={"start":"apple","end":"banana"}
        with self.assertRaisesRegex(CopoError,"COPO_SCOPE_CONFLICT"):validate_scope(bad)
        overlap=scope_fixture();overlap["time"]["observation"]["start"]="2026-06-15T00:00:00Z"
        with self.assertRaisesRegex(CopoError,"baseline overlaps observation"):validate_scope(overlap)

    def test_self_consistent_forged_ledger_is_rejected_without_erdg_signature(self):
        route=route_scenario("profit_deterioration","S1");forged=copy.deepcopy(LEDGER)
        forged["entries"][5]["packet_hash"]="b"*64
        unsigned={k:v for k,v in forged.items() if k not in {"ledger_hash","signature"}}
        forged["ledger_hash"]=canonical_hash(unsigned)
        with self.assertRaisesRegex(CopoError,"ERDG ledger signature invalid"):posture_qualification(route,[receipt("D06")],{x:"passed" for x in route["gates"]},"comparable","repair",cycle_id="C1",now="2026-08-11T00:00:00Z",trusted_ledger=forged)
    def test_routes_all_launch_scenarios(self):
        for name in SCENARIOS: self.assertEqual(route_scenario(name,"S1")["scenario"],name)
    def test_unsupported_scenario_fails(self):
        with self.assertRaisesRegex(CopoError,"COPO_UNSUPPORTED_SCENARIO"): route_scenario("other","S1")
    def test_registry_is_independent_sovereignty_oracle(self):
        self.assertEqual(authority_owner("investment"),"D01"); self.assertEqual(authority_owner("pricing_profit"),"D06")
    def test_d14_cannot_support_domain_finding(self):
        graph={"nodes":[{"node_id":"n","node_type":"domain_finding","owner":"D14","state":"domain_supported","evidence_refs":[]}],"edges":[]}
        with self.assertRaisesRegex(CopoError,"COPO_SOVEREIGNTY_OVERREACH"): validate_graph(graph)
    def test_only_f01_qualifies_causality(self):
        graph={"nodes":[{"node_id":"n","node_type":"causal_claim","owner":"D06","state":"causally_qualified","evidence_refs":[]}],"edges":[]}
        with self.assertRaisesRegex(CopoError,"COPO_CAUSAL_CEILING_EXCEEDED"): validate_graph(graph)
    def test_graph_rejects_duplicate_nodes_and_self_loops(self):
        duplicate={"nodes":[{"node_id":"N","node_type":"candidate_explanation","owner":"D14","state":"candidate","evidence_refs":[]},{"node_id":"N","node_type":"candidate_explanation","owner":"D14","state":"candidate","evidence_refs":[]}],"edges":[]}
        with self.assertRaisesRegex(CopoError,"duplicate diagnostic node"):validate_graph(duplicate)
        loop={"nodes":[{"node_id":"N","node_type":"candidate_explanation","owner":"D14","state":"candidate","evidence_refs":[]}],"edges":[{"from":"N","to":"N","relation":"requires"}]}
        with self.assertRaisesRegex(CopoError,"self-loop"):validate_graph(loop)
    def test_graph_rejects_cycles_and_invalidated_support(self):
        nodes=[{"node_id":"A","node_type":"candidate_explanation","owner":"D14","state":"candidate","evidence_refs":[]},{"node_id":"B","node_type":"candidate_explanation","owner":"D14","state":"candidate","evidence_refs":[]}]
        with self.assertRaisesRegex(CopoError,"dependency cycle"):validate_graph({"nodes":nodes,"edges":[{"from":"A","to":"B","relation":"requires"},{"from":"B","to":"A","relation":"requires"}]})
        invalid={"nodes":[{"node_id":"A","node_type":"domain_finding","owner":"D06","state":"invalidated","evidence_refs":["E"]},{"node_id":"B","node_type":"candidate_explanation","owner":"D14","state":"candidate","evidence_refs":[]}],"edges":[{"from":"A","to":"B","relation":"supports"}]}
        with self.assertRaisesRegex(CopoError,"cannot support"):validate_graph(invalid)
    def test_noncomparability_is_noncompensable(self):
        route=route_scenario("profit_deterioration","S1"); rs=[receipt(x) for x in route["required_owners"]]
        out=qualify(route,rs,{x:"passed" for x in route["gates"]},"not_comparable","repair")
        self.assertEqual((out["status"],out["action_ceiling"]),("blocked","analysis_only"))
    def test_missing_required_owner_never_approves(self):
        route=route_scenario("sales_decline","S1"); rs=[receipt(x) for x in route["required_owners"][:-1]]
        out=qualify(route,rs,{x:"passed" for x in route["gates"]},"comparable","repair")
        self.assertEqual(out["error"],"COPO_REQUIRED_OWNER_MISSING")
    def test_any_required_gate_blocks_scale(self):
        route=route_scenario("scale_readiness","S1"); rs=[receipt(x) for x in route["required_owners"]]; gates={x:"passed" for x in route["gates"]}; gates[route["gates"][0]]="blocked"
        self.assertEqual(qualify(route,rs,gates,"comparable","scale")["status"],"blocked")
    def test_all_gates_only_reach_owner_review(self):
        route=route_scenario("scale_readiness","S1"); rs=[receipt(x) for x in route["required_owners"]]
        out=qualify(route,rs,{x:"passed" for x in route["gates"]},"comparable","scale")
        self.assertEqual(out["status"],"owner_approval_pending")
    def test_posture_cannot_bypass_typed_receipt_validation(self):
        route=route_scenario("scale_readiness","S1");forged=[{"owner":x,"decision":"accepted"} for x in route["required_owners"]]
        with self.assertRaises(CopoError):qualify(route,forged,{x:"passed" for x in route["gates"]})
    def test_coordination_plan_cannot_invent_action(self):
        route=route_scenario("profit_deterioration","S1")
        with self.assertRaisesRegex(CopoError,"COPO_SOVEREIGNTY_OVERREACH"): build_coordination_plan(route,[receipt("D06")],[{"owner":"D06","action_ref":"A1","approval_ref":"missing"}],cycle_id="C1",now="2026-08-11T00:00:00Z",trusted_ledger=LEDGER)
    def test_coordination_plan_cannot_use_d14_action(self):
        route=route_scenario("profit_deterioration","S1")
        with self.assertRaisesRegex(CopoError,"COPO_SOVEREIGNTY_OVERREACH"): build_coordination_plan(route,[receipt("D06")],[{"owner":"D14","action_ref":"A1","approval_ref":"R-D06"}],cycle_id="C1",now="2026-08-11T00:00:00Z",trusted_ledger=LEDGER)
    def test_coordination_plan_binds_action_to_same_owner_scope_and_field(self):
        route=route_scenario("profit_deterioration","S1")
        out=build_coordination_plan(route,[receipt("D06")],[{"owner":"D06","scope_ref":"S1","action_ref":"A-D06","approval_ref":"R-D06"}],cycle_id="C1",now="2026-08-11T00:00:00Z",trusted_ledger=LEDGER)
        self.assertEqual(out["owner_action_refs"],["A-D06"])
    def test_cross_owner_cannot_borrow_approval(self):
        route=route_scenario("profit_deterioration","S1")
        with self.assertRaisesRegex(CopoError,"COPO_SOVEREIGNTY_OVERREACH"):build_coordination_plan(route,[receipt("D06")],[{"owner":"D09","scope_ref":"S1","action_ref":"A-D09","approval_ref":"R-D06"}],cycle_id="C1",now="2026-08-11T00:00:00Z",trusted_ledger=LEDGER)
    def test_plan_rejects_expired_or_bad_hash_receipt_before_sequencing(self):
        route=route_scenario("profit_deterioration","S1");expired=receipt("D06");expired["expires_at"]="2000-01-01T00:00:00Z"
        with self.assertRaisesRegex(CopoError,"COPO_PACKET_(EXPIRED|HASH_MISMATCH)"):build_coordination_plan(route,[expired],[{"owner":"D06","scope_ref":"S1","action_ref":"A-D06","approval_ref":"R-D06"}],cycle_id="C1",now="2026-08-11T00:00:00Z",trusted_ledger=LEDGER)
        bad=receipt("D06");bad["packet_hash"]="b"*64
        with self.assertRaisesRegex(CopoError,"COPO_PACKET_HASH_MISMATCH"):build_coordination_plan(route,[bad],[{"owner":"D06","scope_ref":"S1","action_ref":"A-D06","approval_ref":"R-D06"}],cycle_id="C1",now="2026-08-11T00:00:00Z",trusted_ledger=LEDGER)
    def test_blocked_receipt_is_not_accepted(self):
        with self.assertRaisesRegex(CopoError,"COPO_PARTIAL_ACCEPTANCE"):validate_receipt(receipt("D06","blocked"),{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":1},"2026-01-01T00:00:00Z")
    def test_dependency_oracle_detects_cycle(self):
        with self.assertRaisesRegex(CopoError,"COPO_CONFLICT_UNRESOLVED"): topological_order({"A":["B"],"B":["A"]})
    def test_impact_closure_is_selective(self):
        self.assertEqual(impact_closure({"E1"},{"E1":["F1"],"F1":["P1"],"X":["Y"]}),["E1","F1","P1"])
    def test_unique_current_posture(self):
        with self.assertRaisesRegex(CopoError,"COPO_ILLEGAL_STATE_TRANSITION"): current_effective([{"status":"active"},{"status":"active"}])
    def test_stale_receipt_cannot_overwrite(self):
        r=receipt("D06"); r["packet_version"]=1
        with self.assertRaisesRegex(CopoError,"COPO_STALE_VERSION"): validate_receipt(r,{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":2},"2026-01-01T00:00:00Z")
    def test_hash_pollution_is_rejected(self):
        r=receipt("D06")
        with self.assertRaisesRegex(CopoError,"COPO_PACKET_HASH_MISMATCH"): validate_receipt(r,{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":1,"packet_payload":{"x":1}},"2026-01-01T00:00:00Z")
    def test_self_consistent_forged_hash_cannot_bypass_trusted_ledger(self):
        r=receipt("D06")
        with self.assertRaisesRegex(CopoError,"trusted packet ledger"):validate_receipt(r,{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":1,"packet_hash":"b"*64},"2026-01-01T00:00:00Z")
    def test_partial_acceptance_stays_explicit(self):
        r=receipt("D06","partially_accepted")
        self.assertEqual(validate_receipt(r,{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":1},"2026-01-01T00:00:00Z"),"COPO_PARTIAL_ACCEPTANCE")
    def test_external_write_mutation_is_killed(self):
        r=receipt("D06"); r["external_write"]=True
        with self.assertRaisesRegex(CopoError,"COPO_EXTERNAL_WRITE_FORBIDDEN"): validate_receipt(r,{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":1},"2026-01-01T00:00:00Z")
    def test_conflict_not_closed_by_vote(self):
        self.assertEqual(conflict_owner("capital"),"D01")
        with self.assertRaisesRegex(CopoError,"COPO_CONFLICT_UNRESOLVED"): conflict_owner("professional_conclusion","D14")
    def test_same_source_cannot_fake_independence(self):
        with self.assertRaisesRegex(CopoError,"COPO_SOVEREIGNTY_OVERREACH"): validate_independent_evidence([{"source_group":"platform"},{"source_group":"platform"}])
    def test_manual_completion_cannot_override_gate(self):
        with self.assertRaisesRegex(CopoError,"COPO_ILLEGAL_STATE_TRANSITION"): validate_computed_status("approved","blocked")
    def test_views_are_render_only(self):
        for path in (ROOT/"view-models").glob("*.json"):
            self.assertEqual(json.loads(path.read_text())["computes"],[])
    def test_approved_posture_requires_approval_and_nonblocked_gates(self):
        import jsonschema
        common_doc=json.loads((ROOT/"schemas/common.schema.json").read_text());common=common_doc["$defs"]["governance"]
        schema=json.loads((ROOT/"schemas/operating-posture.schema.json").read_text());schema["properties"]["governance"]=common;schema["$defs"]=common_doc["$defs"]
        governance={"schema_version":"2.0.0","runtime_version":"COPO-2026.07","object_version":"v1","as_of_time":"2026-08-11T00:00:00Z","owner":"D14","status":"approved","allowed_uses":["orchestration"],"forbidden_uses":["external_write"],"input_hash":H,"content_hash":H,"state_hash":H}
        posture={"posture_id":"P1","cycle_id":"C1","scope_ref":"S1","posture":"scale","status":"approved","owner_approval_refs":[],"gate_results":{"capital":"blocked"},"supersedes":None,"stop_conditions":["stop"],"rollback_conditions":["rollback"],"governance":governance,"external_write":False}
        errors=list(jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).iter_errors(posture))
        self.assertGreaterEqual(len(errors),2)

if __name__=="__main__": unittest.main(verbosity=2)
