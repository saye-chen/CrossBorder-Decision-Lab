#!/usr/bin/env python3
from plco_common import fail, required, run_cli

VALID={"E0","E1","E2","E3","E4","E5"}
def validate(data):
    entries=data.get("evidence",[]); claims=data.get("claims",[])
    ids=set(); fps={}; errors=[]
    for i,e in enumerate(entries):
        required(e,("evidence_id","level","fingerprint","observed_at","allowed_uses"),f"evidence[{i}] ")
        if e["level"] not in VALID: errors.append(f"{e['evidence_id']}: invalid level")
        if e["evidence_id"] in ids: errors.append(f"duplicate evidence_id {e['evidence_id']}")
        ids.add(e["evidence_id"]); fps.setdefault(e["fingerprint"],[]).append(e["evidence_id"])
    for c in claims:
        required(c,("claim_id","claim_type","evidence_ids"),"claim ")
        unknown=set(c["evidence_ids"])-ids
        if unknown: errors.append(f"{c['claim_id']}: unknown evidence {sorted(unknown)}")
        levels={e["level"] for e in entries if e["evidence_id"] in c["evidence_ids"]}
        if c["claim_type"]=="causal" and not levels.intersection({"E4","E5"}): errors.append(f"{c['claim_id']}: causal claim lacks E4/E5")
    return {"status":"pass" if not errors else "fail","errors":errors,
            "duplicate_fingerprint_groups":[v for v in fps.values() if len(v)>1],"evidence_count":len(entries)}
if __name__ == "__main__": run_cli(validate,"PLCO-evidence-1")
