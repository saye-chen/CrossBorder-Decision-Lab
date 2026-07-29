#!/usr/bin/env python3
import copy,json,pathlib
from sppq_core import ModelError,evaluate,supplier_gate,scenario_gate
from update_continuous_decision import update
from validate_cross_domain_envelope import validate as validate_cross
from validate_cross_domain_envelope import apply_consumer_response
from decision_engines import decide
from validate_professional_report import validate as validate_report
ROOT=pathlib.Path(__file__).resolve().parents[1]
GOLDENS={row["decision_type"]:row for row in json.loads((ROOT/"evaluations/golden-professional-reports.json").read_text())["reports"]}
def execute(case):
    e=case["executable"];kind=e["kind"]
    if kind=="model":
        try:evaluate({"model":e["model"],"input":e["input"]});actual="pass"
        except ModelError:actual="blocked"
    elif kind=="supplier_gate":
        actual=supplier_gate(e["input"])["status"]
    elif kind=="decision":
        actual=decide(e["decision_type"],e["input"])["status"]
    elif kind=="continuity":
        dependencies=[x["changed"] for x in e["turn_sequence"]]
        state={"object_id":case["id"],"current_version":"v1","current_effective_decision":{"id":"old","version":"v1"},"history":[],"open_gates":[],"active_actions":[{"action_id":"A","status":e["action_status"],"depends_on":dependencies}],"accepted_fields":[],"invalidated_fields":[],"recompute_scope":[]}
        for index,turn in enumerate(e["turn_sequence"]):
            state=update({"object_id":case["id"],"expected_version":state["current_version"],"delta_type":turn["delta_type"],"state":state,"new_version":turn["new_version"],"new_decision":{"id":f"D{index}","version":turn["new_version"]},"changed_fields":[turn["changed"]],"all_fields":[turn["changed"],e["preserved"]],"impact_map":{turn["changed"]:[turn["impacted"]]}})
            if state["last_delta"]["preserved"]!=[e["preserved"]]:break
        actual="recovery" if state.get("recovery_required") else state["current_version"]
        if len(state["history"])!=4:actual="not_four_real_turns"
    elif kind=="cross_domain":
        payload={"message_id":case["id"],"source_domain":e["source"],"target_domain":e["target"],"object_id":"O","object_version":"v1","as_of_time":"2026-07-29T00:00:00Z","authority":e["authority"],"allowed_uses":["decision_support"],"forbidden_uses":["rewrite_owner_decision"],"requested_fields":["qualified_batch","capacity_commitment"],"consumer_response":e["response"],"accepted_fields":e["accepted_fields"],"rejection_reasons":e["rejection_reasons"],"lineage":{"input_hash":"a"*64,"packet_hash":"b"*64}}
        outcome=apply_consumer_response(payload);actual=outcome["status"]
        if e["response"]=="rejected" and outcome.get("recompute_scope")!=["qualified_batch","capacity_commitment"]:actual="rejection_not_propagated"
        if e["response"]=="partially_accepted" and outcome.get("recompute_scope")!=["capacity_commitment"]:actual="partial_not_propagated"
    elif kind=="scenario":
        out=scenario_gate(e["input"]);actual=out["status"]
        seen=set(out["failures"]+out["warnings"])
        if not set(e["target_guards"]).issubset(seen):actual="wrong_guard"
        if out["preserved_results"]!=e["input"]["independent_results"]:actual="partial_results_lost"
    elif kind=="composite":
        decision=decide(e["decision_type"],e["decision_input"])
        scenario=scenario_gate(e["scenario_input"])
        seen=set(scenario["failures"]+scenario["warnings"])
        if decision["status"]!="validated":actual="decision_precondition_failed"
        elif not decision.get("calculations"):actual="decision_models_not_executed"
        elif not set(e["target_guards"]).issubset(seen):actual="wrong_guard"
        elif scenario["preserved_results"]!=e["scenario_input"]["independent_results"]:actual="partial_results_lost"
        else:
            report=copy.deepcopy(GOLDENS[e["decision_type"]]);evidence_id=report["ledgers"]["evidence"][0]["id"]
            calculations=[]
            for index,row in enumerate(decision["calculations"]):
                cid=f"{case['id']}-CAL-{index}"
                calculations.append({"id":cid,"model":row["model"],"input":row["input"],"output":row["output"],"input_hash":row["input_hash"],"output_hash":row["output_hash"],"evidence_ids":[evidence_id],"recomputed":True,"status":"complete"})
            report["professional_analysis"]["calculation_ids"]=[row["id"] for row in calculations]
            report["ledgers"]["calculation"]=calculations
            report["ledgers"]["evidence"][0]["supports"]=[x for x in report["ledgers"]["evidence"][0]["supports"] if not x.startswith("calculations.")]+[f"calculations.{row['id']}" for row in calculations]
            report_errors=validate_report(report)
            requested=["decision_status","calculations"]
            def handoff(target,response,suffix):
                accepted=requested if response=="accepted" else ["decision_status"] if response=="partially_accepted" else []
                payload={"message_id":case["id"]+suffix,"source_domain":"D04","target_domain":target,"object_id":case["id"],"object_version":"v1","as_of_time":"2026-07-29T00:00:00Z","authority":"supplier_quality","allowed_uses":["decision_support"],"forbidden_uses":["rewrite_owner_decision"],"requested_fields":requested,"consumer_response":response,"accepted_fields":accepted,"rejection_reasons":["scenario_guard_failed"] if response=="rejected" else [],"lineage":{"input_hash":decision["calculations"][0]["input_hash"],"packet_hash":"b"*64}}
                return apply_consumer_response(payload)
            mode=e["response_mode"];prior_ok=True
            if mode=="rejected":cross_outcome=handoff("D07","rejected","-R")
            elif mode=="partially_accepted":cross_outcome=handoff("D07","partially_accepted","-P")
            elif mode=="accepted_then_rejected":
                prior=handoff("D07","accepted","-A");prior_ok=prior["status"]=="accepted";cross_outcome=handoff("D07","rejected","-W")
            else:
                prior=handoff("D07","accepted","-A");prior_ok=prior["status"]=="accepted";cross_outcome=handoff("D06","rejected","-C")
            state={"object_id":case["id"],"current_version":"v1","current_effective_decision":{"id":case["id"],"status":"validated"},"history":[],"open_gates":[],"active_actions":[{"action_id":"A","status":"shipped" if case["group"]=="extreme" else "committed","depends_on":["decision_status","calculations"]}],"accepted_fields":[],"invalidated_fields":[],"recompute_scope":[]}
            state=update({"object_id":case["id"],"expected_version":"v1","delta_type":"Revision","state":state,"new_version":"v2","new_decision":{"id":case["id"]+"-recovery","status":"recovery_required"},"changed_fields":cross_outcome["invalidated_fields"],"all_fields":["decision_status","calculations","independent_result"],"impact_map":{"decision_status":["downstream_release"],"calculations":["dependent_economics"]}})
            if report_errors:actual="professional_report_failed"
            elif not prior_ok or cross_outcome["status"] not in {"rejected","partially_accepted"} or not cross_outcome["recompute_scope"]:actual="cross_rejection_not_propagated"
            elif "REALITY_RECOVERY" not in state["open_gates"] or not state.get("recovery_required"):actual="reality_recovery_not_triggered"
            else:actual="blocked" if scenario["status"] in {"blocked","inconclusive"} else "validated"
    else:actual="unknown_kind"
    return {"id":case["id"],"expected":e["expected"],"actual":actual,"passed":actual==e["expected"]}
def run(catalog):
    results=[execute(x) for x in catalog["cases"]]
    return {"runtime_version":"SPPQ-2026.07","total":len(results),"passed":sum(x["passed"] for x in results),"failed":[x for x in results if not x["passed"]]}
def main():
    catalog=json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text())
    result=run(catalog)
    if result["failed"]:raise SystemExit(json.dumps(result,ensure_ascii=False,indent=2))
    print(f"SPPQ executable evaluation passed: {result['passed']}/{result['total']}")
if __name__=="__main__":main()
