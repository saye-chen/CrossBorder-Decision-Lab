#!/usr/bin/env python3
"""Validate repository-owned license and privacy release boundaries."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "governance/release-compliance-policy.json"


def validate() -> list[str]:
    errors: list[str] = []
    if not POLICY.is_file():
        return ["release compliance policy is missing"]
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    license_spec = policy.get("repository_license", {})
    license_path = ROOT / str(license_spec.get("path", ""))
    if not license_path.is_file():
        errors.append("repository license is missing")
    requirements = ROOT / "requirements-dev.txt"
    lines = {
        line.strip()
        for line in requirements.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    declared = policy.get("direct_dependencies", [])
    declared_requirements = {row.get("requirement") for row in declared}
    if lines != declared_requirements:
        errors.append("direct dependency declaration does not match requirements-dev.txt")
    for row in declared:
        if not row.get("declared_license") or not row.get("source"):
            errors.append(f"dependency lacks license source: {row.get('requirement')}")
        if row.get("legal_conclusion") is not False:
            errors.append(f"dependency improperly claims legal conclusion: {row.get('requirement')}")
    privacy = policy.get("data_privacy", {})
    required_true = (
        "repository_must_not_contain_raw_personal_data",
        "real_replay_requires_authorization_reference",
        "real_replay_requires_deidentification",
        "public_competitor_data_must_not_be_person_matched_to_first_party_customers",
    )
    for key in required_true:
        if privacy.get(key) is not True:
            errors.append(f"privacy boundary must be true: {key}")
    if privacy.get("external_write_default") is not False:
        errors.append("external write must default false")
    if privacy.get("owner_review_status") != "controlled_external_gate":
        errors.append("privacy owner review must remain an external gate")
    replay_schema = json.loads(
        (ROOT / "governance/erdg/schemas/replay.schema.json").read_text(encoding="utf-8")
    )
    required = set(replay_schema.get("required", []))
    if not {"authorized", "deidentified"}.issubset(required):
        errors.append("ERDG replay schema does not require authorization and deidentification")
    maturity = json.loads(
        (ROOT / "governance/domain-maturity-status.json").read_text(encoding="utf-8")
    )
    if any(row.get("authorized_real_cases", 0) and row.get("l4") == "passed" for row in maturity["domains"]):
        errors.append("L4 claim requires accountable privacy owner review outside this automated gate")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print("Release compliance boundary validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
