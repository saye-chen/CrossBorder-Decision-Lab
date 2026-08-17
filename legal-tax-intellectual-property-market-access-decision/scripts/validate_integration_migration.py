#!/usr/bin/env python3
"""Validate the current D05 ERDG adapter, consumer responses and migration safety."""
from __future__ import annotations
import json
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[1]

def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def schema_errors(name,value):
    try:
        schema=load(ROOT/"schemas"/name); jsonschema.validate(value,schema,format_checker=jsonschema.FormatChecker()); return []
    except (OSError,json.JSONDecodeError,jsonschema.ValidationError) as exc: return [str(exc)]

def validate_adapter(value):
    errors=[]
    if value.get("version")!="2.0.0": errors.append("adapter must use the current v2 contract")
    if "availability" in value or "staging_only" in value: errors.append("current adapter cannot retain staging flags")
    if value.get("accepts_v1") is not False: errors.append("adapter must reject v1")
    if value.get("external_write") is not False: errors.append("adapter cannot write externally")
    if value.get("contract")!="ERDG-CONTRACT-2026.07": errors.append("adapter contract mismatch")
    if "professional_opinion" in value.get("owned_decision_types",[]): errors.append("adapter cannot own professional opinions")
    return errors

def validate_response(value):
    errors=schema_errors("consumer-response.schema.json",value)
    if errors: return errors
    accepted=set(value["accepted_fields"]); rejected=set(value["rejected_fields"])
    if accepted & rejected: errors.append("accepted and rejected fields overlap")
    if value["status"]=="accepted" and rejected: errors.append("accepted response cannot reject fields")
    if value["status"]=="rejected" and accepted: errors.append("rejected response cannot accept fields")
    if value["status"]=="partially_accepted" and (not accepted or not rejected): errors.append("partial response requires accepted and rejected fields")
    if value["status"]!="pending" and not value["current_state_updated"]: errors.append("non-pending response must update current state")
    return errors

def validate_migration(value):
    errors=schema_errors("formal-migration.schema.json",value)
    if errors: return errors
    mappings=value.get("mappings",[])
    if not isinstance(mappings,list) or not mappings: errors.append("migration mappings must be non-empty")
    if any(not isinstance(m,dict) or not m.get("source_field") or (m.get("classification")=="lossless" and not m.get("target_field")) for m in mappings): errors.append("lossless migration mappings require source and target fields")
    consumers=value.get("consumer_acceptance",[])
    if not isinstance(consumers,list) or not consumers: errors.append("consumer acceptance must be non-empty")
    if any(c.get("status") not in {"accepted","rejected","pending"} for c in consumers if isinstance(c,dict)): errors.append("invalid consumer acceptance status")
    if value.get("rollback_status") not in {"ready","triggered","completed","not_required"}: errors.append("invalid rollback status")
    if any(m["criticality"]=="safety_critical" and m["classification"]!="lossless" for m in value["mappings"]): errors.append("safety critical mappings must be lossless")
    statuses={x["status"] for x in value["consumer_acceptance"]}
    if statuses!={"accepted"} and value["rollback_status"] not in {"ready","triggered","completed"}: errors.append("unaccepted consumers require rollback readiness")
    if value["action_ceiling_comparison"] in {"higher","incomparable"}: errors.append("migration cannot raise or obscure action ceiling")
    return errors


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adapter", type=Path)
    parser.add_argument("response", type=Path)
    parser.add_argument("migration", type=Path)
    args = parser.parse_args()
    adapter_errors = validate_adapter(load(args.adapter))
    response_errors = validate_response(load(args.response))
    migration_errors = validate_migration(load(args.migration))
    errors = [f"adapter:{x}" for x in adapter_errors] + [f"response:{x}" for x in response_errors] + [f"migration:{x}" for x in migration_errors]
    print(json.dumps({"status": "pass" if not errors else "blocked", "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not errors else 1)
