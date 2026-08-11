#!/usr/bin/env python3
"""Fail closed on L4 until real authorized evidence is independently reviewed."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "governance/l4-external-assurance-registry.json"
HASH = re.compile(r"^[a-f0-9]{64}$")


def evaluate(registry: dict | None = None) -> tuple[list[str], bool]:
    errors: list[str] = []
    registry = registry or json.loads(REGISTRY.read_text())
    architecture = json.loads((ROOT / "governance/domain-architecture-registry.json").read_text())
    current = {x["domain_id"] for x in architecture["domains"] if x["availability"] == "current"}
    rows = registry.get("domains", [])
    if {x.get("domain_id") for x in rows} != current or len(rows) != len(current):
        errors.append("L4 registry must cover every current domain exactly once")
    minimum = registry.get("minimum_authorized_replays_per_domain")
    required = set(registry.get("required_case_fields", []))
    prohibited = set(registry.get("prohibited_evidence", []))
    all_passed = True
    for row in rows:
        cases = row.get("cases", [])
        passed = len(cases) >= minimum and row.get("status") == "passed"
        if row.get("status") == "passed" and len(cases) < minimum:
            errors.append(f"{row.get('domain_id')}: false L4 pass without minimum real replays")
        for case in cases:
            missing = required - set(case)
            if missing:
                errors.append(f"{row.get('domain_id')}:{case.get('case_id','?')}: missing {sorted(missing)}")
                continue
            if case.get("evidence_type") in prohibited or case.get("synthetic") is not False:
                errors.append(f"{row.get('domain_id')}:{case.get('case_id')}: synthetic or prohibited evidence")
            for field in ("input_hash", "output_hash"):
                if not HASH.fullmatch(str(case.get(field, ""))):
                    errors.append(f"{row.get('domain_id')}:{case.get('case_id')}: invalid {field}")
            if case.get("independent_reviewer") == case.get("implementer") or case.get("review_decision") != "accepted":
                errors.append(f"{row.get('domain_id')}:{case.get('case_id')}: independent review invalid")
        all_passed = all_passed and passed
    if registry.get("production_ready") is not all_passed:
        if registry.get("production_ready") is True:
            errors.append("system production-ready claim exceeds domain evidence")
    if not all_passed and registry.get("system_status") != "separate_not_passed":
        errors.append("open L4 gate status must remain separate_not_passed")
    return errors, all_passed


if __name__ == "__main__":
    errors, passed = evaluate()
    if errors:
        print("L4_EXTERNAL_ASSURANCE=INVALID\n- " + "\n- ".join(errors))
        raise SystemExit(2)
    print("L4_EXTERNAL_ASSURANCE=PASSED" if passed else "L4_EXTERNAL_ASSURANCE=SEPARATE_NOT_PASSED")
