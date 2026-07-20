#!/usr/bin/env python3
from common import main
from pathlib import Path
import hashlib,re
REQUIRED=["case_id","object_id","as_of_time","input_file","input_hash","model_version","decision","observed_outcome","outcome_time","outcome_file","outcome_hash","decision_correct","calibration_notes","source_type","authorization_ref","source_system","reviewer","reviewed_at"]
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run(d):
    cases=d.get("cases",[]);errors=[];ids=set();authorized=0;root=Path(d.get("evidence_root","." )).resolve();allowed=set(d.get("authorization_requirements",{}).get("allowed_source_types",["authorized_historical"]))
    for i,c in enumerate(cases):
        missing=[k for k in REQUIRED if c.get(k) in [None,""]]
        if missing: errors.append(f"case_{i}_missing:{','.join(missing)}")
        if c.get("case_id") in ids: errors.append(f"duplicate_case_id:{c.get('case_id')}")
        ids.add(c.get("case_id"))
        artifacts_ok=True
        for kind in ["input","outcome"]:
            raw=c.get(f"{kind}_hash","");target=(root/str(c.get(f"{kind}_file",""))).resolve()
            if root not in target.parents and target!=root: errors.append(f"case_{i}_{kind}_file_outside_root");artifacts_ok=False
            elif not target.is_file(): errors.append(f"case_{i}_{kind}_file_missing");artifacts_ok=False
            elif not re.fullmatch(r"sha256:[0-9a-f]{64}",str(raw)): errors.append(f"case_{i}_{kind}_hash_invalid");artifacts_ok=False
            elif digest(target)!=str(raw).removeprefix("sha256:"): errors.append(f"case_{i}_{kind}_hash_mismatch");artifacts_ok=False
        if c.get("source_type") in allowed and artifacts_ok: authorized+=1
        if c.get("decision_correct") not in [True,False]: errors.append(f"case_{i}_decision_correct_not_boolean")
    minimum=int(d.get("minimum_authorized_cases",3))
    if authorized<minimum: errors.append(f"authorized_cases_below_minimum:{authorized}<{minimum}")
    return {"valid":not errors,"errors":errors,"authorized_cases":authorized,"minimum_authorized_cases":minimum,"production_ready":not errors}
if __name__=="__main__":main(run)
