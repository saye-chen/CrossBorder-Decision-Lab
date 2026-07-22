#!/usr/bin/env python3
"""Validate PLCO authorized historical replays; synthetic fixtures never qualify."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

REQUIRED = {
    "case_id", "object_id", "page_version_before", "page_version_after",
    "as_of_time", "authorized_input_file", "input_hash", "frozen_decision",
    "primary_metric", "guardrails", "observed_outcome", "outcome_maturity_time",
    "outcome_hash", "outcome_file", "rollback_was_available", "reviewer",
    "authorization_ref", "source_type",
}
FORBIDDEN_SOURCES = {"synthetic", "golden", "fixture", "demo"}


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(payload: dict, base: Path) -> dict:
    errors: list[str] = []
    cases = payload.get("cases", [])
    if not isinstance(cases, list):
        return {"valid": False, "errors": ["cases_must_be_list"], "production_ready": False}
    evidence_root = (base / payload.get("evidence_root", ".")).resolve()
    minimum = int(payload.get("minimum_authorized_cases", 3))
    ids: set[str] = set()
    authorized = 0

    for index, case in enumerate(cases):
        missing = sorted(key for key in REQUIRED if case.get(key) in (None, "", []))
        if missing:
            errors.append(f"case_{index}_missing:{','.join(missing)}")
        case_id = str(case.get("case_id", ""))
        if case_id in ids:
            errors.append(f"duplicate_case_id:{case_id}")
        ids.add(case_id)
        if str(case.get("source_type", "")).lower() in FORBIDDEN_SOURCES:
            errors.append(f"case_{index}_synthetic_source_forbidden")
        if case.get("page_version_before") == case.get("page_version_after"):
            errors.append(f"case_{index}_page_version_not_changed")
        if case.get("rollback_was_available") is not True:
            errors.append(f"case_{index}_rollback_not_available")
        try:
            if parse_time(str(case.get("outcome_maturity_time"))) <= parse_time(str(case.get("as_of_time"))):
                errors.append(f"case_{index}_outcome_not_after_decision")
        except (TypeError, ValueError):
            errors.append(f"case_{index}_invalid_time")

        artifacts_ok = True
        for file_key, hash_key in [("authorized_input_file", "input_hash"), ("outcome_file", "outcome_hash")]:
            target = (evidence_root / str(case.get(file_key, ""))).resolve()
            claimed = str(case.get(hash_key, ""))
            if evidence_root not in target.parents and target != evidence_root:
                errors.append(f"case_{index}_{file_key}_outside_root"); artifacts_ok = False
            elif not target.is_file():
                errors.append(f"case_{index}_{file_key}_missing"); artifacts_ok = False
            elif not re.fullmatch(r"sha256:[0-9a-f]{64}", claimed):
                errors.append(f"case_{index}_{hash_key}_invalid"); artifacts_ok = False
            elif digest(target) != claimed.removeprefix("sha256:"):
                errors.append(f"case_{index}_{hash_key}_mismatch"); artifacts_ok = False
        if not case.get("concurrent_changes_recorded"):
            errors.append(f"case_{index}_concurrent_changes_not_recorded")
        if artifacts_ok and str(case.get("source_type", "")).lower() not in FORBIDDEN_SOURCES and not missing:
            authorized += 1

    if authorized < minimum:
        errors.append(f"authorized_cases_below_minimum:{authorized}<{minimum}")
    return {"valid": not errors, "errors": errors, "authorized_cases": authorized, "minimum_authorized_cases": minimum, "production_ready": not errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = validate(payload, args.input.parent)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
