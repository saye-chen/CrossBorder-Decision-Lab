#!/usr/bin/env python3
"""Validate one D14 decision bundle or, without input, the release contract."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from validate_copo import validate
from copo import build_coordination_plan, posture_qualification, validate_canonical_route, validate_outcome_replay, validate_schema_payload, validate_scope

def validate_bundle(path: Path) -> list[str]:
    try:
        bundle=json.loads(path.read_text())
        validate_schema_payload("decision-bundle.schema.json",bundle);validate_scope(bundle["scope"]);validate_schema_payload("scenario-route.schema.json",bundle["route"]);validate_canonical_route(bundle["route"])
        if bundle["scope"]["scope_id"] != bundle["route"]["scope_ref"] or bundle["scope"]["cycle_id"] != bundle["trusted_ledger"]["cycle_id"]: raise ValueError("bundle scope/cycle binding mismatch")
        posture_qualification(bundle["route"],bundle["receipts"],bundle["gates"],bundle["f02_comparability"],bundle["requested_posture"],cycle_id=bundle["scope"]["cycle_id"],now=bundle["now"],trusted_ledger=bundle["trusted_ledger"])
        plan=build_coordination_plan(bundle["route"],bundle["receipts"],bundle["owner_actions"],cycle_id=bundle["scope"]["cycle_id"],now=bundle["now"],trusted_ledger=bundle["trusted_ledger"])
        if bundle.get("replay") is not None: validate_outcome_replay(bundle["replay"],set(plan["owner_action_refs"]))
        return []
    except Exception as exc:return [str(exc)]


if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--input",type=Path);args=parser.parse_args()
    errors = validate_bundle(args.input) if args.input else validate()
    print("COPO_DECISION_CONTRACT=PASS" if not errors else "COPO_DECISION_CONTRACT=FAIL\n- " + "\n- ".join(errors))
    raise SystemExit(0 if not errors else 2)
