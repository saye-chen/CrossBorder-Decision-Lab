#!/usr/bin/env python3
"""Generate 120 decision-distinct MBCM evaluation cases deterministically."""
from __future__ import annotations
import json, pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
SCENARIOS=[f"S{i:02d}" for i in range(1,14)]
QUESTIONS=[f"Q{i:02d}" for i in range(1,14)]
GATES=[f"G{i}" for i in range(9)]
PLATFORMS=[f"P{i}" for i in range(1,10)]
CATEGORIES=[f"C{i}" for i in range(1,10)]
MODES=[f"M{i}" for i in range(1,9)]
STATES=["proceed","test","hold","repair","reduce","stop","escalate","inconclusive"]
PARTICIPANTS=["CIDM","CIM","LIFD","PLCO","AAMO","CAPM","VLB","CIG","D05","D06","D14","F01"]
COUNTS={"standalone":36,"cross_skill":28,"multi_turn":20,"extreme":16,"property":12,"adversarial":8}
ESTIMATION_METHODS=["power_mde","did","synthetic_control","itt_cace","bootstrap_monte_carlo",
                    "offer_elasticity","adstock_saturation","cohort_clv","seasonality_competition","incident_recovery"]
TURN_CHANGES=["clarify_object","correct_price_or_cost","new_participant_arrives",
              "execution_version_changes","early_result_arrives","mature_result_arrives"]
HIGH_RISK_COMBINATIONS=[
 "discount_without_incrementality","brand_spend_without_loss_boundary","launch_without_gtm_gate",
 "campaign_without_capacity","attribution_as_causality","clearance_without_brand_redline",
 "channel_conflict_without_owner","mixed_currency_aggregation","stale_version_execution",
 "missing_rights_for_asset","inventory_shortfall_during_scale","fraud_signal_during_offer",
 "negative_marginal_return_scale","unknown_platform_high_commitment",
 "incident_with_external_write","exit_with_residual_liability"]

def case(mode,n,offset):
    i=offset+n
    scenario=SCENARIOS[i%len(SCENARIOS)]; question=QUESTIONS[(i*5)%len(QUESTIONS)]
    gate=GATES[(i*7)%len(GATES)]; state=STATES[(i*3)%len(STATES)]
    row={"id":f"MBCM-{mode[:2].upper()}-{n+1:03d}","mode":mode,"scenario":scenario,
         "question":question,"lifecycle":f"L{i%9}","platform_archetype":PLATFORMS[(i*2)%9],
         "category_archetype":CATEGORIES[(i*4)%9],"operating_mode":MODES[(i*3)%8],
         "primary_gate":gate,"expected_state":state,
         "estimation_method":ESTIMATION_METHODS[i%len(ESTIMATION_METHODS)],
         "stress_level":f"T{(i%6)+1}",
         "must":["object_version","evidence_action_ceiling","action_stop_rollback"],
         "forbidden":["sovereignty_overreach","attribution_equals_incrementality"],
         "failure_assertion":f"{gate} failure cannot be compensated by marketing score"}
    if mode=="cross_skill":
        row["participants"]=sorted({PARTICIPANTS[i%len(PARTICIPANTS)],PARTICIPANTS[(i+5)%len(PARTICIPANTS)]})
    row["mechanism"]=":".join(str(row[k]) for k in (
        "scenario","question","lifecycle","platform_archetype","category_archetype",
        "operating_mode","primary_gate","expected_state"))
    row["decision_input"]={"object_id":f"OBJECT-{(i%17)+1:02d}","object_version":f"v{(i%4)+1}",
        "as_of_time":"2026-07-23T00:00:00+08:00","dq_level":f"DQ{i%4}",
        "claim_level":f"C{i%5}","reversibility":"reversible" if i%3 else "partially_reversible"}
    row["expected_assertions"]={"state":state,"primary_gate":gate,
        "must_preserve_sovereignty":True,"must_include_no_action_candidate":True,
        "must_include_stop_and_rollback":True}
    if mode=="multi_turn":
        row["turns"]=[{"turn":x+1,"change":TURN_CHANGES[x],"must_preserve":["object_id","constraints"],
                       "must_recompute":[f"node_{(i+x)%7}"]} for x in range(6)]
    if mode=="extreme": row["incident"]=f"I{(i%10)+1:02d}"
    if mode=="property": row["property"]=("monotonicity","conservation","unit_guard","version_invariance")[i%4]
    if mode=="adversarial": row["attack"]=("fabricated_data","sovereignty","version_pollution","hallucinated_rule","partial_failure","l4_fraud")[i%6]
    return row

def main():
    cases=[]; offset=0
    for mode,count in COUNTS.items():
        cases.extend(case(mode,n,offset) for n in range(count)); offset+=count
    manifest={"schema_version":"1.0","runtime":"MBCM-2026.01","counts":COUNTS,"total":len(cases),
      "high_risk_combinations":HIGH_RISK_COMBINATIONS,
      "coverage":{"scenarios":sorted({x["scenario"] for x in cases}),"questions":sorted({x["question"] for x in cases}),
        "lifecycles":sorted({x["lifecycle"] for x in cases}),"gates":sorted({x["primary_gate"] for x in cases}),
        "platforms":sorted({x["platform_archetype"] for x in cases}),"categories":sorted({x["category_archetype"] for x in cases}),
        "operating_modes":sorted({x["operating_mode"] for x in cases}),"states":sorted({x["expected_state"] for x in cases}),
        "stress_levels":sorted({x["stress_level"] for x in cases}),
        "estimation_methods":sorted({x["estimation_method"] for x in cases})},
      "cases":cases}
    target=ROOT/"evaluations/fixtures/evaluation-catalog.json"
    target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"generated={len(cases)} path={target}")
if __name__=="__main__": main()
