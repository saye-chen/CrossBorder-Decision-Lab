#!/usr/bin/env python3
import copy,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
GROUPS=[("decision",36),("calculation",36),("cross_domain",28),("multi_turn",24),("complex",20),("extreme",16)]
DECISIONS=["supplier_selection","procurement_commitment","sample_approval","production_release","batch_quality_release","supplier_recovery_exit"]
MODES=["spot","trader","OEM","ODM","own_factory","subcontract"]
RISKS=["general","food_contact","beauty","child_toy","electrical","battery","textile","health_related"]
CONTINUITY_FIELDS=["approved_material_version","supplier_facility","ctq_tolerance","measurement_method","sampling_plan","process_route","capacity_commitment","batch_lineage","compliance_gate","delivery_window","capa_evidence","quality_cost","reliability_mission","subcontractor_identity","inspection_result","release_quantity","currency_basis","tooling_status","control_plan","complaint_escape","inventory_disposition","professional_opinion","product_specification","decision_owner"]
MODEL_FIXTURES=[
 ("quote_normalization",{"currency":"CNY","fx_rate":.14,"quantity":100,"unit_price":10,"extra_costs":[20]}),
 ("bom_rollup",{"components":[{"quantity":2,"unit_cost":3,"scrap_rate":.02}]}),
 ("should_cost",{"currency":"USD","unit":"piece","as_of_time":"2026-07-29T00:00:00Z","direct_material":5,"direct_labor":2,"machine_process":1,"manufacturing_overhead":1,"packaging_testing":.5,"risk_allowance":.5,"reasonable_margin_rate":.1}),
 ("total_cost_of_ownership",{"currency":"USD","unit":"piece","as_of_time":"2026-07-29T00:00:00Z","d06_inputs_accepted":True,"d07_inputs_accepted":True,"purchase":100,"inspection":3,"quality_failure":7,"delay":5,"switch_exit":10,"recoverable_value":2}),
 ("capacity",{"available_hours":10,"units_per_hour":10,"yield_rate":.9,"changeover_hours":1,"uptime_rate":.8,"demand":50}),
 ("lead_time",{"stage_days":[2,3,4],"risk_buffer_days":1}),
 ("concentration",{"shares":[.5,.3,.2]}),
 ("measurement_system",{"study_variation":1,"tolerance":10}),
 ("process_stability",{"values":[10,10.1,9.9,10,10.05],"max_range":.3}),
 ("process_capability",{"measurement_system_acceptable":True,"process_stable":True,"mean":10,"sigma":1,"lsl":4,"usl":16}),
 ("fmea",{"severity":9,"occurrence":2,"detection":3}),
 ("sampling",{"lot_id":"L1","lot_size":1000,"sampling_plan_id":"PLAN-1","defect_class":"major","sample_representative":True,"random_selection":True,"sample_size":80,"defects":1,"accept_number":1,"reject_number":2,"critical_defects":0}),
 ("escape_risk",{"sample_size":80,"defects":0}),
 ("cost_of_quality",{"prevention":1,"appraisal":2,"internal_failure":3,"external_failure":4,"recall":5}),
 ("reliability",{"test_hours":100,"failures":1}),
 ("delivery_reliability",{"orders":10,"on_time_in_full":9}),
 ("recovery_choice",{"options":[{"id":"A","feasible":True,"loss":10,"days":2},{"id":"B","feasible":True,"loss":12,"days":1}]}),
 ("quantity_reconciliation",{"input":100,"qualified":90,"nonconforming":5,"rework":2,"scrapped":1,"wip":1,"explained_variance":1})
]
EXTREME_GUARDS=[
 ("identity_match","identity_conflict"),("facility_disclosed","undisclosed_subcontract"),
 ("sources_independent","correlated_supply_sources"),("material_matches_approved","unapproved_material_change"),
 ("sample_representative","sample_not_representative"),("measurement_acceptable","measurement_system_failure"),
 ("batch_lineage_complete","batch_lineage_break"),("quantity_balanced","quantity_not_conserved"),
 ("segregation_of_duties","self_approval"),("current_version","stale_or_concurrent_version"),
 ("critical_defects","critical_defect"),("capacity_feasible","capacity_overload"),
 ("compliance_gate","compliance_gate_missing"),("capa_recurrence","capa_not_effective"),
 ("bypass_requested","gate_bypass_requested"),("evidence_conflict","evidence_conflict_requires_review")
]
DECISION_VALID={
 "supplier_selection":{"identity_verified":True,"facility_verified":True,"network_disclosed":True,"evidence_traceable":True,"segregation_of_duties":True,"critical_redline":False,"correlated_sources":False},
 "procurement_commitment":{"supplier_approved":True,"specification_current":True,"bom_current":True,"quote_current":True,"capital_gate":"passed","cash_gate":"passed","compliance_gate":"passed","quality_agreement":True,"quantity":100,"moq":50,"external_execution_requested":False},
 "sample_approval":{"sample_identity":True,"source_traceable":True,"specification_current":True,"measurement_acceptable":True,"ctq_complete":True,"failed_ctqs":0,"sample_type":"first_article"},
 "production_release":{"sample_approved":True,"specification_current":True,"bom_current":True,"process_route_current":True,"control_plan_ready":True,"measurement_acceptable":True,"capacity_feasible":True,"compliance_gate":"passed","segregation_of_duties":True,"release_quantity":100},
 "batch_quality_release":{"production_released":True,"batch_lineage_complete":True,"inspection_complete":True,"quantity_balanced":True,"measurement_acceptable":True,"segregation_of_duties":True,"critical_defects":0,"inspection_decision":"accept"},
 "supplier_recovery_exit":{"affected_scope_known":True,"containment_active":True,"owner_assigned":True,"evidence_preserved":True,"capa_claimed":True,"capa_effectiveness_verified":True,"options":[{"id":"switch"}]}
}
DECISION_FAILURE_FIELD={"supplier_selection":"identity_verified","procurement_commitment":"cash_gate","sample_approval":"measurement_acceptable","production_release":"control_plan_ready","batch_quality_release":"batch_lineage_complete","supplier_recovery_exit":"containment_active"}
FIXTURE_BY_MODEL=dict(MODEL_FIXTURES)
DECISION_REQUIRED_MODELS={
 "supplier_selection":["capacity","concentration"],
 "procurement_commitment":["quote_normalization","bom_rollup","should_cost","total_cost_of_ownership"],
 "sample_approval":["measurement_system"],
 "production_release":["process_stability","capacity"],
 "batch_quality_release":["sampling","quantity_reconciliation","escape_risk"],
 "supplier_recovery_exit":["recovery_choice","cost_of_quality"],
}
INVALID_FIXTURES={
 "quote_normalization":{"currency":"USD","fx_rate":0,"quantity":0,"unit_price":1},
 "bom_rollup":{"components":[{"quantity":1,"unit_cost":1,"scrap_rate":1}]},
 "should_cost":{"currency":"USD"},
 "total_cost_of_ownership":{"currency":"USD","unit":"piece","as_of_time":"2026-07-29T00:00:00Z","d06_inputs_accepted":False,"d07_inputs_accepted":True},
 "capacity":{"available_hours":0},
 "lead_time":{"stage_days":[]},
 "concentration":{"shares":[.8,.8]},
 "measurement_system":{"study_variation":1,"tolerance":0},
 "process_stability":{"values":[1,2]},
 "process_capability":{"measurement_system_acceptable":False,"process_stable":True,"mean":1,"sigma":1,"lsl":0,"usl":2},
 "fmea":{"severity":11,"occurrence":1,"detection":1},
 "sampling":{"sample_size":80,"defects":0,"accept_number":1,"critical_defects":0},
 "escape_risk":{"sample_size":0,"defects":0},
 "cost_of_quality":{"prevention":1},
 "reliability":{"test_hours":0,"failures":0},
 "delivery_reliability":{"orders":0,"on_time_in_full":0},
 "recovery_choice":{"options":[]},
 "quantity_reconciliation":{"input":1},
}
def decision_payload(decision,variant):
    payload=copy.deepcopy(DECISION_VALID[decision])
    payload["model_inputs"]={model:copy.deepcopy(FIXTURE_BY_MODEL[model]) for model in DECISION_REQUIRED_MODELS[decision]}
    if decision in {"supplier_selection","production_release"}:payload["model_inputs"]["capacity"]["demand"]=30+(variant%20)
    elif decision=="procurement_commitment":
        payload["quantity"]=100+variant;payload["model_inputs"]["quote_normalization"]["quantity"]=100+variant;payload["model_inputs"]["should_cost"]["volume"]=100+variant
    elif decision=="sample_approval":payload["model_inputs"]["measurement_system"]["study_variation"]=.5+(variant%20)/100
    elif decision=="batch_quality_release":payload["model_inputs"]["sampling"]["lot_size"]=1000+variant
    else:payload["model_inputs"]["recovery_choice"]["options"][0]["loss"]=10+variant
    import hashlib
    def h(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    payload["evidence_bindings"]=[{"id":f"E-{decision}-{variant}","object_version":"v1","hash":"a"*64,"supported_fields":[f"model_inputs.{model}" for model in DECISION_REQUIRED_MODELS[decision]],"input_hashes":{model:h(payload["model_inputs"][model]) for model in DECISION_REQUIRED_MODELS[decision]}}]
    return payload
def build():
    cases=[];n=0
    for group,count in GROUPS:
        for i in range(count):
            n+=1
            decision=DECISIONS[(n-1)%6]
            case={"id":f"SPPQ-{n:03d}","group":group,"decision_type":decision,"manufacturing_mode":MODES[(n-1)%6],"risk_route":RISKS[(n-1)%8],"evidence_state":["complete","missing","conflicting","expired","suspected_fraud","unverifiable"][(n-1)%6],"expected_guard":f"{group}_guard_{i%8}","unique_mechanism":f"{group}:{i:02d}","turns":4 if group=="multi_turn" else 1}
            if group=="calculation":
                model,fixture=MODEL_FIXTURES[i%len(MODEL_FIXTURES)]
                valid=i<len(MODEL_FIXTURES)
                case["executable"]={"kind":"model","model":model,"input":copy.deepcopy(fixture if valid else INVALID_FIXTURES[model]),"expected":"pass" if valid else "blocked"}
            elif group=="multi_turn":
                status=["planned","committed","in_progress","shipped"][i%4]
                turns=[{"delta_type":["Addendum","Revision","Recalculation","Rebase"][j],"changed":CONTINUITY_FIELDS[(i+j)%len(CONTINUITY_FIELDS)],"impacted":["evidence_recheck","dependent_model_recompute","consumer_reacceptance","action_ceiling_review"][j],"new_version":f"v{j+2}"} for j in range(4)]
                case["executable"]={"kind":"continuity","turn_sequence":turns,"preserved":f"preserved_{i}","action_status":status,"expected":"recovery" if status!="planned" else "v5"}
            elif group=="cross_domain":
                target=["D01","D03","D05","D06","D07","D13","ERDG"][i%7];mode=["accepted","rejected","partially_accepted","overreach"][i%4]
                case["executable"]={"kind":"cross_domain","source":"D04","target":target,"authority":"capital_allocation" if mode=="overreach" else "supplier_quality","response":"pending" if mode=="overreach" else mode,"accepted_fields":["qualified_batch"] if mode=="partially_accepted" else ["qualified_batch","capacity_commitment"] if mode=="accepted" else [],"rejection_reasons":["owner_rejected"] if mode=="rejected" else [],"expected":"blocked" if mode=="overreach" else mode}
            elif group in {"complex","extreme"}:
                field,guard=EXTREME_GUARDS[i%len(EXTREME_GUARDS)]
                inp={"independent_results":[f"unaffected_{i}"]}
                if field in {"critical_defects"}:inp[field]=1
                elif field in {"capa_recurrence","bypass_requested","evidence_conflict"}:inp[field]=True
                elif field=="compliance_gate":inp.update(compliance_required=True,compliance_gate="blocked")
                else:inp[field]=False
                extra_guards=[]
                for offset in ([5] if group=="complex" else [5,9]):
                    extra_field,extra_guard=EXTREME_GUARDS[(i+offset)%len(EXTREME_GUARDS)]
                    if extra_field=="critical_defects":inp[extra_field]=1
                    elif extra_field in {"capa_recurrence","bypass_requested","evidence_conflict"}:inp[extra_field]=True
                    elif extra_field=="compliance_gate":inp.update(compliance_required=True,compliance_gate="blocked")
                    else:inp[extra_field]=False
                    extra_guards.append(extra_guard)
                expected="inconclusive" if field=="evidence_conflict" else "blocked"
                case["executable"]={"kind":"composite","decision_type":decision,"decision_input":decision_payload(decision,i+100),"scenario_input":inp,"target_guards":[guard]+extra_guards,"response_mode":["rejected","partially_accepted","accepted_then_rejected","consumer_conflict"][i%4],"expected":"blocked"}
            else:
                valid=i%2==0;payload=decision_payload(decision,i)
                if not valid:payload[DECISION_FAILURE_FIELD[decision]]=False
                case["executable"]={"kind":"decision","decision_type":decision,"input":payload,"expected":"validated" if valid else ("recovery_required" if decision=="supplier_recovery_exit" else "blocked")}
            cases.append(case)
    return {"runtime_version":"SPPQ-2026.07","total":len(cases),"groups":dict(GROUPS),"cases":cases}
def main():
    target=ROOT/"evaluations/evaluation-catalog.json"
    target.write_text(json.dumps(build(),ensure_ascii=False,indent=2)+"\n")
    print(target)
if __name__=="__main__":main()
