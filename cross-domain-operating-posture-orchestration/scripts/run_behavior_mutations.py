#!/usr/bin/env python3
"""Replace production behaviors and prove the bound test fails for each mutant."""
from __future__ import annotations
import copy, importlib.util, io, json, sys, unittest
from contextlib import contextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
SPEC=importlib.util.spec_from_file_location("copo_bound_tests",ROOT/"tests/test_copo.py");TESTS=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(TESTS)

MUTANTS={
 "d14_professional_final":("validate_graph",lambda graph:None,"test_d14_cannot_support_domain_finding"),
 "d14_capital_approval":("authority_owner",lambda decision_type:"D14","test_registry_is_independent_sovereignty_oracle"),
 "remove_noncompensable_gate":("posture_qualification",lambda *a,**k:{"status":"owner_approval_pending"},"test_any_required_gate_blocks_scale"),
 "partial_failure_overall_pass":("validate_receipt",lambda *a,**k:"accepted","test_partial_acceptance_stays_explicit"),
 "missing_owner_approved":("posture_qualification",lambda *a,**k:{"status":"owner_approval_pending"},"test_missing_required_owner_never_approves"),
 "ce1_ce3_to_causal":("validate_graph",lambda graph:None,"test_only_f01_qualifies_causality"),
 "f02_not_comparable_aggregated":("posture_qualification",lambda *a,**k:{"status":"owner_approval_pending"},"test_noncomparability_is_noncompensable"),
 "expired_current":("validate_receipt",lambda *a,**k:"accepted","test_stale_receipt_cannot_overwrite"),
 "old_overwrites_new":("validate_receipt",lambda *a,**k:"accepted","test_stale_receipt_cannot_overwrite"),
 "conflict_majority_vote":("conflict_owner",lambda *a,**k:"D14","test_conflict_not_closed_by_vote"),
 "posture_approves_action":("build_coordination_plan",lambda *a,**k:{"owner_action_refs":["unsafe"]},"test_coordination_plan_cannot_invent_action"),
 "plan_invents_action":("build_coordination_plan",lambda *a,**k:{"owner_action_refs":["unsafe"]},"test_coordination_plan_cannot_use_d14_action"),
 "external_write_true":("validate_receipt",lambda *a,**k:"accepted","test_external_write_mutation_is_killed"),
 "manual_completion":("validate_computed_status",lambda *a,**k:None,"test_manual_completion_cannot_override_gate"),
 "same_source_independence":("validate_independent_evidence",lambda *a,**k:None,"test_same_source_cannot_fake_independence"),
}

@contextmanager
def replacement(name,behavior):
    original=getattr(TESTS,name);setattr(TESTS,name,behavior)
    try:yield
    finally:setattr(TESTS,name,original)

def run_case(test_name:str)->bool:
    suite=unittest.TestSuite([TESTS.TestCopo(test_name)]);result=unittest.TextTestRunner(stream=io.StringIO(),verbosity=0).run(suite)
    return not result.wasSuccessful()

def view_mutation_killed()->bool:
    original=TESTS.json.loads
    def mutated(text):
        row=original(text)
        if isinstance(row,dict) and "view" in row:row=copy.deepcopy(row);row["computes"]=["unsafe_gate"]
        return row
    with replacement("json",type("MutatedJson",(),{"loads":staticmethod(mutated)})):
        return run_case("test_views_are_render_only")

def run()->dict[str,bool]:
    results={}
    for mid,(name,behavior,test_name) in MUTANTS.items():
        with replacement(name,behavior):results[mid]=run_case(test_name)
    results["view_recomputes_gate"]=view_mutation_killed()
    return results

if __name__=="__main__":
    results=run();failed=[mid for mid,killed in results.items() if not killed]
    print(json.dumps(results,sort_keys=True));print("COPO_BEHAVIOR_MUTATIONS=PASS" if not failed else "COPO_BEHAVIOR_MUTATIONS=FAIL:"+",".join(failed));raise SystemExit(0 if not failed else 2)
