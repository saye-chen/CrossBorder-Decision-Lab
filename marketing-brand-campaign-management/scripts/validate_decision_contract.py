#!/usr/bin/env python3
"""Validate MBCM decision contract."""
from mbcm_common import require, text, run_cli, ModelError
QUESTIONS={f"Q{i:02d}" for i in range(1,14)}
STAGES={f"L{i}" for i in range(9)}
def validate(d):
    if "mode" in d and "decision_owner" in d:
        require(d,"mode","decision_type","decision_owner","participating_skills","runtime_versions",
                "participant_results","professional_core","objects","evidence","claims","calculations",
                "required_calculation_ids","unresolved_redlines","adjustments")
        if not d["objects"] or not d["evidence"] or not d["claims"]:
            raise ModelError("shared_contract:objects_evidence_claims_required")
        return {"valid":True,"contract_type":"shared","decision_owner":d["decision_owner"]}
    require(d,"decision_id","decision_version","question_type","intent","primary_object","scope",
            "lifecycle_stage","business_objective","authority","constraints","evidence_cutoff",
            "decision_deadline","reversibility")
    if d["question_type"] not in QUESTIONS: raise ModelError("question_type:invalid")
    if d["lifecycle_stage"] not in STAGES: raise ModelError("lifecycle_stage:invalid")
    text(d["decision_id"],"decision_id"); text(d["decision_version"],"decision_version")
    if not isinstance(d["primary_object"],dict) or not d["primary_object"].get("object_id"): raise ModelError("primary_object:object_id_required")
    return {"valid":True,"decision_id":d["decision_id"],"question_type":d["question_type"],
            "lifecycle_stage":d["lifecycle_stage"]}
if __name__=="__main__": run_cli(validate,"validate_decision_contract")
