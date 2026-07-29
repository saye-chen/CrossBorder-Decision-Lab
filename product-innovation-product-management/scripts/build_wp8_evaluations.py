#!/usr/bin/env python3
"""Deterministically build the checked-in WP8 evaluation catalog and artifacts."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"evaluations"
MODES={"standard":10,"boundary":12,"failure":15,"adversarial":12,"property":12,"cross_skill":16,"multi_turn":12,"extreme":12}
ARCHETYPES=["commodity","oem_odm","electronics","regulated","consumable","apparel","durable","connected_device"]
PLCS=[f"PLC{i}" for i in range(9)]
PLATFORMS=["Amazon","TikTok Shop","Shopify/DTC","unknown"]
REGIONS=["US","DE","SG","ZZ"]
REPORTS=["product_opportunity_brief","product_definition","mvp_decision","product_specification_decision","variant_packaging_decision","product_validation_report","product_change_impact_report","product_roadmap","product_stop_retire_decision"]
EVENTS=["clarification","evidence_update","product_fact_change","scope_change","scenario_override","validation_result","cross_domain_accept","cross_domain_reject","action_update","incident_or_recall","rollback","retire"]
PARTICIPANTS=["pricing-profit-finance-cashflow-decision","future-d04","future-d05","category-investment-decision","competitive-intelligence-monitoring","video-link-breakdown","consumer-insights-customer-growth","logistics-inventory-fulfillment-decision","platform-store-listing-conversion","advertising-analysis-measurement-optimization","creator-affiliate-partnership-management","marketing-brand-campaign-management","governance/erdg"]
RISKS=["safety","regulated","negative_profit","cash","unmanufacturable","unfulfillable","claim","version_pollution","tool_failure","retirement"]
GOLDEN_NAMES=["amazon-opportunity-mvp","tiktok-proxy-correction","dtc-return-redesign","multi-country-variant","variant-cannibalization","material-change-multidomain","unsupported-claim","critical-tail-failure","specification-drift","stop-retire"]
EXECUTABLES=["evaluate_product_models.py","validate_wp3_package.py","validate_cross_domain_envelope.py","compute_product_change_impact.py","validate_wp6_contracts.py","evaluate_temporary_contract_migration.py","update_continuous_product_decision.py","compute_decision_impact_closure.py","validate_professional_report.py"]
CATEGORY_MAP={"standard":"standard","boundary":"boundary","failure":"failure","adversarial":"adversarial","property":"property","cross_skill":"cross_domain","multi_turn":"multi_turn","extreme":"extreme"}

def dump(path:Path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def sha(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def make_case(mode,index,global_index):
    risk=RISKS[global_index%len(RISKS)]; hard=mode in {"failure","adversarial","extreme"} and global_index%3==0
    evidence="missing" if mode in {"boundary","failure"} and global_index%4==0 else "conflict" if mode in {"adversarial","extreme"} and global_index%4==1 else "verified"
    tool="partial" if risk=="tool_failure" else "ok"; version_match=not(risk=="version_pollution")
    expected="blocked" if hard or not version_match else "inconclusive" if evidence!="verified" or tool=="partial" or PLATFORMS[global_index%4]=="unknown" else "proposed"
    participants=[] if mode not in {"cross_skill","extreme"} else [PARTICIPANTS[global_index%len(PARTICIPANTS)],PARTICIPANTS[(global_index+3)%len(PARTICIPANTS)]]
    return {"id":f"PIPM-{mode[:2].upper()}-{index:02d}","category":CATEGORY_MAP[mode],"mode":mode,"mutation_class":"authorization_boundary","scenario_signature":f"{mode}|{ARCHETYPES[global_index%8]}|{PLCS[global_index%9]}|{risk}|{global_index}","owner_skill":"product-innovation-product-management","archetype":ARCHETYPES[global_index%8],"plc":PLCS[global_index%9],"platform":PLATFORMS[global_index%4],"region":REGIONS[global_index%4],"report_type":REPORTS[global_index%9],"event_type":EVENTS[global_index%12],"participants":participants,"risk":risk,"primary_mechanism":["product_model","evidence_gate","continuity","cross_domain","rollback"][global_index%5],"exercised_script":EXECUTABLES[global_index%len(EXECUTABLES)],"fixture":{"hard_gate_failed":hard,"evidence_state":evidence,"tool_state":tool,"version_match":version_match,"external_write":False},"expected":{"status":expected,"maturity":"controlled pilot","must":["object_version","primary_mechanism","stop_rollback_exit","lineage"],"forbidden":["external_write","redline_compensation","synthetic_l4"]},"mutation":{"field":"external_write","value":True,"expected_status":"blocked"},"runner":"scripts/run_wp8_evaluations.py"}
def make_report(i,name):
    spec={k:f"{name}:{k}" for k in __import_report().REQUIRED[REPORTS[i%9]]}
    report={"report_id":f"G-{i+1}","report_type":REPORTS[i%9],"chain_id":f"CH-{i+1}","decision_id":f"D-{i+1}","is_current":True,"object_ref":{"object_id":f"P-{i+1}","object_version":"v1"},"scope":{"country":REGIONS[i%3],"platform":PLATFORMS[i%3]},"as_of_time":"2026-07-28T00:00:00Z","recorded_at":"2026-07-28T01:00:00Z","decision_state":"proposed","current_conclusion":f"controlled recommendation for {name}","history_refs":["baseline@v0"],"evidence":[{"id":"E1","state":"verified"}],"counterevidence":[{"id":"E2"}],"conflicts":[],"missing_and_expired":[],"calculations":[{"id":"K1","value":"1","unit":"index"}],"no_action":{"effect":"learning delayed"},"candidates":[{"id":"conservative"},{"id":"recommended"},{"id":"stress"}],"dependencies":["D06"],"actions":[{"state":"proposed","owner":"product"}],"success_conditions":["registered validation passes"],"stop_conditions":["hard gate fails"],"rollback":{"restore":"baseline@v0"},"exit_conditions":["retire if falsified"],"allowed_uses":["decision_support"],"forbidden_uses":["external_execution"],"specific_content":spec,"lineage":{"input_hash":"sha256:"+sha({"golden":name}),"report_hash":"sha256:","runtime_version":"PIPM-2026.07"},"maturity":"controlled pilot","external_write":False}
    report["lineage"]["report_hash"]=__import_report().report_hash(report);return report
_REPORT=None
def __import_report():
    global _REPORT
    if _REPORT is None:
        spec=importlib.util.spec_from_file_location("report_validator",ROOT/"scripts/validate_professional_report.py");_REPORT=importlib.util.module_from_spec(spec);spec.loader.exec_module(_REPORT)
    return _REPORT
_CHAINS=None
def __import_chains():
    global _CHAINS
    if _CHAINS is None:
        spec=importlib.util.spec_from_file_location("golden_chains",ROOT/"scripts/execute_golden_professional_chains.py");_CHAINS=importlib.util.module_from_spec(spec);spec.loader.exec_module(_CHAINS)
    return _CHAINS
def main():
    cases=[];n=0
    for mode,count in MODES.items():
        for i in range(1,count+1):cases.append(make_case(mode,i,n));n+=1
    coverage={"mode_counts":MODES,"archetypes":sorted({x["archetype"] for x in cases}),"plcs":sorted({x["plc"] for x in cases}),"platforms":sorted({x["platform"] for x in cases}),"regions":sorted({x["region"] for x in cases}),"reports":sorted({x["report_type"] for x in cases}),"events":sorted({x["event_type"] for x in cases}),"participants":sorted({p for x in cases for p in x["participants"]}),"risks":sorted({x["risk"] for x in cases})}
    dump(OUT/"fixtures/evaluation-catalog.json",{"catalog_version":"PIPM-EVAL-2026.07","count":len(cases),"coverage":coverage,"cases":cases})
    bindings=[]
    for x in cases:
        bindings.append({
            "id":x["id"],
            "runner":x["runner"],
            "engine":x["exercised_script"],
            "positive":{
                "engine_call":"engine_pass(valid)",
                "decision_call":"execute(case)",
                "expected_engine_assertion":"accepted",
                "expected_decision_status":x["expected"]["status"],
            },
            "counterexample":{
                "engine_call":"engine_pass(mutation)",
                "decision_call":"execute(case, mutation=True)",
                "mutation_class":x["mutation_class"],
                "mutation":x["mutation"],
                "expected_engine_assertion":"rejected_or_blocked",
                "expected_decision_status":"blocked",
            },
        })
    dump(OUT/"fixtures/evaluation-execution-map.json",{"version":"PIPM-EXEC-2026.07","catalog":"evaluation-catalog.json","assertion_semantics":{"positive_per_case":2,"counterexample_per_case":2,"professional_engine_assertions":202,"decision_assertions":202,"total_assertions":404},"bindings":bindings})
    dump(OUT/"coverage-matrix.json",coverage)
    multi=[{"id":f"PIPM-MT-{i:02d}","object_id":f"P-{i}","turns":[{"sequence":j,"event_type":EVENTS[(i+j)%12],"must_preserve":["object_id","history"],"must_answer":["changed","preserved","action_effect"],"forbidden":["silent_overwrite","second_current"]} for j in range(1,5)]} for i in range(1,13)]
    dump(OUT/"multiturn-challenges.json",multi)
    extreme=[{"id":f"PIPM-EX-{i:02d}","name":f"{RISKS[(i-1)%10]} multi-domain extreme","participants":[PARTICIPANTS[(i-1)%13],PARTICIPANTS[(i+2)%13]],"failed":[PARTICIPANTS[(i+5)%13]] if i%3==0 else [],"must":["hard_gate","partial_failure","residual_exposure","rollback_or_exit"],"forbidden":["majority_vote","redline_compensation"],"failure_injection":["timeout","stale_evidence","version_conflict","irreversible_action"][(i-1)%4]} for i in range(1,13)]
    dump(OUT/"extreme-scenarios.json",extreme)
    for i,name in enumerate(GOLDEN_NAMES):
        execution=__import_chains().scenario_input(name)
        actual=__import_chains().execute(execution);mutated=__import_chains().execute(execution,True)
        fixture={"id":f"G-{i+1}","name":name,"object_version":"v1","plc":PLCS[i%9],"platform":PLATFORMS[i%4],"region":REGIONS[i%4],"primary_mechanism":execution["operation"],"counterexample":execution["mutation"],"expected_status":actual["decision_status"],"execution":execution,"input_hash":sha(execution)}
        report=make_report(i,name)
        binding={"engine":execution["engine"],"operation":execution["operation"],"input_hash":"sha256:"+sha(execution),"mechanism_output_hash":"sha256:"+sha(actual),"decision_status":actual["decision_status"]}
        report["specific_content"]["execution_binding"]=binding;report["decision_state"]=actual["decision_status"] if actual["decision_status"] in {"proposed","validated","rejected","blocked","inconclusive"} else "inconclusive";report["current_conclusion"]=f"{name}: {actual['decision_status']} from {execution['engine']}";report["lineage"]["input_hash"]=binding["input_hash"];report["lineage"]["report_hash"]=__import_report().report_hash(report)
        oracle={"expected_status":actual["decision_status"],"expected_execution_state":actual["execution_state"],"expected_output_hash":"sha256:"+sha(actual),"required_assertions":["lineage","hard_gate","stop_rollback_exit","scenario_owned_input","mechanism_output_binding"],"mutation":{"expected_status":mutated["decision_status"],"expected_execution_state":mutated["execution_state"],"expected_output_hash":"sha256:"+sha(mutated),"must_differ":actual!=mutated}}
        dump(OUT/f"golden/{name}-fixture.json",fixture);dump(OUT/f"golden/{name}-report.json",report);dump(OUT/f"golden/{name}-oracle.json",oracle)
    print(f"PIPM_WP8_BUILD=PASS cases={len(cases)} golden={len(GOLDEN_NAMES)} multiturn={len(multi)} extreme={len(extreme)}")
if __name__=="__main__":main()
