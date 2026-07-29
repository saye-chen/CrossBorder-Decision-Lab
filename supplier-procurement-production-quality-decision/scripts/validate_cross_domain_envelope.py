#!/usr/bin/env python3
import json,pathlib,sys
import jsonschema
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/"schemas/cross-domain-envelope.schema.json").read_text())
KNOWN={"D01","D03","D04","D05","D06","D07","D13","ERDG"}
OWNED={"D01":"capital_allocation","D03":"product_definition","D04":"supplier_quality","D05":"legal_access","D06":"pricing_profit","D07":"inventory_allocation","D13":"customer_compensation","ERDG":"governance_validation"}
def validate(d):
    errors=[]
    try:jsonschema.Draft202012Validator(SCHEMA,format_checker=jsonschema.FormatChecker()).validate(d)
    except jsonschema.ValidationError as e:errors.append(f"schema:{e.message}")
    if d.get("source_domain") not in KNOWN or d.get("target_domain") not in KNOWN:errors.append("unknown_domain")
    if d.get("source_domain")==d.get("target_domain"):errors.append("self_handoff")
    if set(d.get("allowed_uses",[]))&set(d.get("forbidden_uses",[])):errors.append("allowed_forbidden_overlap")
    if d.get("authority") in {"capital_allocation","product_definition","legal_access","pricing_profit","inventory_allocation","customer_compensation"} and d.get("source_domain")=="D04":errors.append("D04_authority_overreach")
    if d.get("consumer_response")=="partially_accepted" and not d.get("accepted_fields"):errors.append("partial_acceptance_requires_fields")
    if d.get("consumer_response")=="rejected" and not d.get("rejection_reasons"):errors.append("rejection_requires_reasons")
    requested=set(d.get("requested_fields",[]));accepted=set(d.get("accepted_fields",[]))
    if not accepted.issubset(requested):errors.append("accepted_fields_not_requested")
    if d.get("consumer_response")=="accepted" and accepted!=requested:errors.append("accepted_response_requires_all_requested_fields")
    lineage=d.get("lineage",{})
    for key in ("input_hash","packet_hash"):
        if len(str(lineage.get(key,"")))!=64:errors.append(f"invalid_{key}")
    return errors
def apply_consumer_response(d):
    errors=validate(d)
    if errors:return {"status":"blocked","errors":errors,"accepted_fields":[],"invalidated_fields":[],"recompute_scope":[]}
    response=d["consumer_response"];requested=list(d["requested_fields"])
    if response=="accepted":
        return {"status":"accepted","accepted_fields":requested,"invalidated_fields":[],"recompute_scope":[]}
    if response=="partially_accepted":
        accepted=list(d["accepted_fields"]);invalid=[x for x in requested if x not in accepted]
        return {"status":"partially_accepted","accepted_fields":accepted,"invalidated_fields":invalid,"recompute_scope":invalid}
    if response=="rejected":
        return {"status":"rejected","accepted_fields":[],"invalidated_fields":requested,"recompute_scope":requested,"reasons":d["rejection_reasons"]}
    return {"status":"pending","accepted_fields":[],"invalidated_fields":[],"recompute_scope":[]}
def main():
    d=json.loads(pathlib.Path(sys.argv[1]).read_text());e=validate(d)
    if e:raise SystemExit("SPPQ cross-domain rejected:\n- "+"\n- ".join(e))
    print("SPPQ cross-domain envelope accepted")
if __name__=="__main__":main()
