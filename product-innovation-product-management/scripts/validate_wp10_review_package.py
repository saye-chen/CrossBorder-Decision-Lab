#!/usr/bin/env python3
"""Fail closed on stale evidence or premature D03 independent-review claims."""
from __future__ import annotations

import json
from pathlib import Path

from build_wp10_review_package import EVIDENCE, REPO, REVIEW_ROLES, ROOT, file_hash

OUT = ROOT / "evaluations/review-package"


def validate() -> list[str]:
    errors: list[str] = []
    index_path = OUT / "evidence-index.json"
    signoff_path = OUT / "independent-signoff.json"
    checklist_path = OUT / "review-checklist.json"
    if not all(path.is_file() for path in (index_path, signoff_path, checklist_path)):
        return ["REVIEW_PACKAGE_FILE_MISSING"]
    index = json.loads(index_path.read_text(encoding="utf-8"))
    signoff = json.loads(signoff_path.read_text(encoding="utf-8"))
    checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
    rows = {row["path"]: row["sha256"] for row in index.get("evidence", [])}
    if set(rows) != set(EVIDENCE):
        errors.append("EVIDENCE_INVENTORY_DRIFT")
    for relative in EVIDENCE:
        path = REPO / relative
        if not path.is_file() or rows.get(relative) != file_hash(path):
            errors.append(f"EVIDENCE_HASH_DRIFT:{relative}")
    roles = signoff.get("required_roles", [])
    if {row.get("role") for row in roles} != set(REVIEW_ROLES):
        errors.append("REVIEW_ROLE_COVERAGE")
    expected_index_hash = file_hash(index_path)
    if any(row.get("evidence_index_hash") != expected_index_hash for row in roles):
        errors.append("SIGNOFF_INDEX_BINDING")
    pending = signoff.get("overall_status") == "pending_independent_review"
    if pending and any(row.get("decision") != "pending" for row in roles):
        errors.append("PARTIAL_SIGNOFF_STATE_INVALID")
    if not pending:
        for row in roles:
            if (
                row.get("decision") != "approved"
                or row.get("independent_of_implementation") is not True
                or row.get("conflict_of_interest") not in {"none", "disclosed_and_mitigated"}
                or not row.get("reviewer_id")
                or not row.get("signed_at")
            ):
                errors.append(f"INVALID_SIGNOFF:{row.get('role')}")
    if index.get("maturity_constraint") != {
        "l3": "not_passed_until_independent_signoff",
        "l4": "controlled_pilot",
        "authoritative": False,
        "external_write": False,
    }:
        errors.append("MATURITY_SHORTCUT")
    if any(value != "pending_reviewer" for key, value in checklist.items() if key != "blocking_rule"):
        errors.append("CHECKLIST_PREMATURELY_CLOSED")
    return errors


if __name__ == "__main__":
    found = validate()
    if found:
        raise SystemExit("PIPM_WP10_PACKAGE=BLOCKED\n-" + "\n-".join(found))
    print("PIPM_WP10_PACKAGE=READY_FOR_INDEPENDENT_REVIEW")
