#!/usr/bin/env python3
"""Generate an auditable CE0-CE5 grade from non-compensatory evidence gates."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main


GRADE_ORDER=["CE0","CE1","CE2","CE3","CE4","CE5"]
QUESTION_CEILING={"insufficient":"CE0","descriptive":"CE1","associational":"CE2","predictive":"CE3","attributed":"CE3","causal":"CE5"}
DESIGN_CEILING={
    "two_arm_randomized":"CE5","multi_arm_randomized":"CE5","stratified_randomized":"CE5","cluster_randomized":"CE5","geo_holdout":"CE5","switchback":"CE5",
    "did_2x2":"CE4","staggered_did":"CE5","synthetic_control":"CE4","sdid":"CE4","rdd":"CE5","iv":"CE4","aipw":"CE4","tmle":"CE4","dml":"CE4","matching_weighting":"CE4","hte_uplift":"CE4",
    "network_interference":"CE4","longitudinal_dynamic":"CE4","mediation":"CE4","bandit_off_policy":"CE4"
}
CRITICAL_GATES={"Q2","Q3","Q4","Q5","Q6","Q8","Q9"}


def _minimum(*grades:str)->str:
    return min(grades,key=GRADE_ORDER.index)


def grade_causal_claim(value:dict)->dict:
    question_type=value.get("question_type","insufficient")
    if question_type not in QUESTION_CEILING:
        raise ECAEError("INVALID_QUESTION_TYPE","Unknown question_type")
    ceiling=QUESTION_CEILING[question_type]
    reasons=[{"rule":"QUESTION_TYPE","ceiling":ceiling}]
    blockers=[]
    if value.get("unresolved_conflict") is True:
        ceiling="CE0"; blockers.append("UNRESOLVED_CONFLICT"); reasons.append({"rule":"UNRESOLVED_CONFLICT","ceiling":"CE0"})
    if value.get("data_status") in {"failed","untraceable","not_mature"}:
        ceiling=_minimum(ceiling,"CE0"); blockers.append("DATA_INELIGIBLE"); reasons.append({"rule":"DATA_INELIGIBLE","ceiling":"CE0"})
    if question_type=="causal" and ceiling!="CE0":
        design=value.get("design")
        if design not in DESIGN_CEILING:
            ceiling=_minimum(ceiling,"CE3"); blockers.append("DESIGN_NOT_REGISTERED"); reasons.append({"rule":"DESIGN_NOT_REGISTERED","ceiling":"CE3"})
        else:
            ceiling=_minimum(ceiling,DESIGN_CEILING[design]); reasons.append({"rule":"DESIGN_LIMIT","ceiling":DESIGN_CEILING[design]})
        identification=value.get("identification",{})
        required_identification=["potential_outcomes_contract","causal_graph_contract","estimand_registered","identification_statement"]
        failed_identification=[field for field in required_identification if identification.get(field) is not True]
        if failed_identification:
            ceiling=_minimum(ceiling,"CE3"); blockers.append("IDENTIFICATION_INCOMPLETE"); reasons.append({"rule":"DUAL_IDENTIFICATION_REQUIRED","ceiling":"CE3","failed":failed_identification})
        gates=value.get("eligibility_gates",{})
        gate_failures=sorted(gate for gate in CRITICAL_GATES if gates.get(gate)!="pass")
        if gate_failures:
            ceiling=_minimum(ceiling,"CE3"); blockers.append("CRITICAL_ELIGIBILITY_GATE"); reasons.append({"rule":"CRITICAL_ELIGIBILITY_GATE","ceiling":"CE3","failed":gate_failures})
        tier=value.get("capability_tier")
        if tier=="verified_backend" and value.get("backend_verified") is not True:
            ceiling=_minimum(ceiling,"CE3"); blockers.append("BACKEND_NOT_VERIFIED"); reasons.append({"rule":"BACKEND_NOT_VERIFIED","ceiling":"CE3"})
        elif tier in {"protocol_only","research_only",None}:
            if not (tier=="protocol_only" and value.get("external_analysis_independently_verified") is True):
                ceiling=_minimum(ceiling,"CE3"); blockers.append("METHOD_NOT_EXECUTABLE_OR_VERIFIED"); reasons.append({"rule":"CAPABILITY_TIER","ceiling":"CE3"})
        diagnostics=value.get("diagnostics",[])
        if any(item.get("status") in {"fail","unknown"} and item.get("severity")=="block_causal" for item in diagnostics):
            ceiling=_minimum(ceiling,"CE3"); blockers.append("BLOCKING_DIAGNOSTIC"); reasons.append({"rule":"BLOCKING_DIAGNOSTIC","ceiling":"CE3"})
        if any(item.get("status") in {"fail","unknown"} and item.get("severity")=="block_ce5" for item in diagnostics):
            ceiling=_minimum(ceiling,"CE4"); reasons.append({"rule":"CE5_DIAGNOSTIC_FAILED","ceiling":"CE4"})
        if value.get("sensitivity_status") not in {"pass","not_applicable"}:
            ceiling=_minimum(ceiling,"CE3"); blockers.append("SENSITIVITY_INCOMPLETE"); reasons.append({"rule":"SENSITIVITY_INCOMPLETE","ceiling":"CE3"})
        deviation_caps=value.get("deviation_grade_caps",[])
        for cap in deviation_caps:
            if cap not in GRADE_ORDER:
                raise ECAEError("INVALID_DEVIATION_CAP",f"Invalid deviation grade cap: {cap}")
            ceiling=_minimum(ceiling,cap)
        if deviation_caps: reasons.append({"rule":"DEVIATION_CAP","ceiling":_minimum(*deviation_caps)})
        if value.get("precision_status")!="decision_adequate":
            ceiling=_minimum(ceiling,"CE4"); reasons.append({"rule":"PRECISION_NOT_DECISION_ADEQUATE","ceiling":"CE4"})
        if value.get("reproducibility_status")!="deterministic_replay_pass":
            ceiling=_minimum(ceiling,"CE4"); reasons.append({"rule":"REPRODUCIBILITY_NOT_DECISION_GRADE","ceiling":"CE4"})
        if value.get("economic_status") not in {"value_supported","value_not_supported","downside_risk"} or value.get("economic_parameters_qualified") is not True:
            ceiling=_minimum(ceiling,"CE4"); reasons.append({"rule":"ECONOMIC_INTERPRETATION_NOT_QUALIFIED","ceiling":"CE4"})
        if value.get("review_status")!="independent_accepted":
            ceiling=_minimum(ceiling,"CE4"); reasons.append({"rule":"INDEPENDENT_REVIEW_REQUIRED_FOR_CE5","ceiling":"CE4"})
    wording={
        "CE0":{"allowed":["无法判断","需补证或重做"],"prohibited":["有效","相关","因果","净增量"]},
        "CE1":{"allowed":["观察到","发生了"],"prohibited":["导致","预测","归因","净增量"]},
        "CE2":{"allowed":["与之相关","共同变化"],"prohibited":["由其造成","带来净增量"]},
        "CE3":{"allowed":["预测","平台归因","规则归因"],"prohibited":["真实因果效果","净增量"]},
        "CE4":{"allowed":["在指定范围与假设下的因果效应"],"prohibited":["普遍有效","无条件扩张"]},
        "CE5":{"allowed":["可供指定决定使用的净增量区间"],"prohibited":["自动执行","跨环境普遍有效"]}
    }[ceiling]
    return {"causal_evidence_grade":ceiling,"claim_ceiling":ceiling,"blockers":sorted(set(blockers)),"rule_trace":reasons,"allowed_wording":wording["allowed"],"prohibited_wording":wording["prohibited"],"business_owner_decision_required":True,"external_write":False}


if __name__=="__main__":
    cli_main(grade_causal_claim,__doc__ or "Grade causal claim")
