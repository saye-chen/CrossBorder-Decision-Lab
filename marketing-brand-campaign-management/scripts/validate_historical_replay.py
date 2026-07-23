#!/usr/bin/env python3
"""Validate authorized mature MBCM historical replay entry gate."""
from mbcm_common import require, run_cli, ModelError, boolean, sequence, text
def validate(d):
    require(d,"production_ready","cases")
    if d["production_ready"] is not False: raise ModelError("production_ready:validator_only")
    boolean(d["production_ready"],"production_ready")
    valid=[]; case_ids=[]
    for i,c in enumerate(sequence(d["cases"],"cases")):
        require(c,"case_id","authorized","deidentified","decision","action","execution_version",
                "mature_outcome","evidence_hashes","independent_review","scenario_type")
        case_id=text(c["case_id"],f"cases[{i}].case_id"); case_ids.append(case_id)
        authorized=boolean(c["authorized"],f"cases[{i}].authorized")
        deidentified=boolean(c["deidentified"],f"cases[{i}].deidentified")
        reviewed=boolean(c["independent_review"],f"cases[{i}].independent_review")
        if not isinstance(c["mature_outcome"],dict): raise ModelError(f"cases[{i}].mature_outcome:object_required")
        hashes=sequence(c["evidence_hashes"],f"cases[{i}].evidence_hashes",allow_empty=False)
        if any(not isinstance(x,str) or not x.startswith("sha256:") or len(x)!=71 for x in hashes):
            raise ModelError(f"cases[{i}].evidence_hashes:sha256_required")
        ok=authorized and deidentified and reviewed and bool(c["mature_outcome"])
        if ok: valid.append(c)
    if len(case_ids)!=len(set(case_ids)): raise ModelError("cases:duplicate_case_id")
    types={c["scenario_type"] for c in valid}
    failure=bool(types&{"failure","incident","reduce","exit"})
    ready=len(valid)>=3 and len(types)>=2 and failure
    return {"valid_cases":len(valid),"heterogeneous_types":sorted(types),
            "failure_or_exit_covered":failure,"production_ready":ready,
            "maturity":"production_validated" if ready else "controlled pilot"}
if __name__=="__main__": run_cli(validate,"validate_historical_replay")
