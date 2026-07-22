#!/usr/bin/env python3
from plco_common import fail, integer, run_cli

def evaluate(data):
    variants=data.get("variants",[]); seen=set(); issues=[]; total=0
    for v in variants:
        vid=v.get("variant_id")
        if not vid or vid in seen: issues.append({"variant_id":vid,"issue":"missing_or_duplicate_id"})
        seen.add(vid); attrs=tuple(sorted(v.get("attributes",{}).items()))
        if not attrs: issues.append({"variant_id":vid,"issue":"missing_attributes"})
        sig=str(attrs)
        if sig in {x[0] for x in []}: pass
        inv=integer(v.get("inventory",0),f"{vid}.inventory"); total+=inv
        if v.get("product_identity")!=data.get("product_identity"): issues.append({"variant_id":vid,"issue":"different_product_identity"})
    signatures=[tuple(sorted(v.get("attributes",{}).items())) for v in variants]
    if len(signatures)!=len(set(signatures)): issues.append({"issue":"indistinguishable_variants"})
    return {"status":"pass" if not issues else "fail","issues":issues,"variant_count":len(variants),"total_inventory":total}
if __name__ == "__main__": run_cli(evaluate,"PLCO-variant-1")
