#!/usr/bin/env python3
"""Validate MBCM decisions through ERDG plus MBCM-owned invariants."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from mbcm_common import require, text, run_cli, ModelError

ROOT=Path(__file__).resolve().parents[2]
CORE_PATH=ROOT/"governance/erdg/scripts/validate_contract.py"
SPEC=importlib.util.spec_from_file_location("erdg_decision_contract",CORE_PATH)
CORE=importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(CORE)

QUESTIONS={f"Q{i:02d}" for i in range(1,14)}
STAGES={f"L{i}" for i in range(9)}
def validate(d):
    if "mode" in d and "decision_owner" in d:
        errors=CORE.validate(d)
        if errors:
            raise ModelError("erdg:"+("|".join(errors)))
        return {"valid":True,"contract_type":"erdg_shared","decision_owner":d["decision_owner"],
                "erdg_contract":"ERDG-CONTRACT-2026.07"}
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
