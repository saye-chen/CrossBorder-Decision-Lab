#!/usr/bin/env python3
"""Validate OSL Current DoD and WP-01..WP-22 execution registers."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOD = ROOT / "governance/cidm-opportunity-signal-current-dod.json"
WPS = ROOT / "governance/cidm-opportunity-signal-work-packages.json"
REQS = ROOT / "governance/cidm-opportunity-signal-requirements.json"
DONE = {"implemented", "implemented_contract", "implemented_controlled", "implemented_validator_only", "implemented_reserved_interface", "completed", "completed_controlled", "completed_interface"}
OPEN = {"partially_implemented", "partially_completed", "blocked_external", "not_started"}

def validate() -> tuple[list[str], dict]:
    errors = []
    dod = json.loads(DOD.read_text(encoding="utf-8")); wp = json.loads(WPS.read_text(encoding="utf-8")); detailed = json.loads(REQS.read_text(encoding="utf-8"))
    requirements = dod.get("requirements", []); ids = [item.get("id") for item in requirements]
    if len(ids) != len(set(ids)) or any(not value for value in ids): errors.append("Current DoD requirement IDs must be unique and nonempty")
    for item in requirements:
        for field in ("source", "gate", "owner", "reviewer", "status", "evidence"):
            if field not in item: errors.append(f"{item.get('id')}: missing {field}")
        if item.get("status") in OPEN and not item.get("blocker"): errors.append(f"{item.get('id')}: open item lacks blocker")
        if item.get("gate") == "external" and item.get("status") != "blocked_external": errors.append(f"{item.get('id')}: external gate cannot be auto-closed")
        for path in item.get("evidence", []):
            if not (ROOT / path).exists(): errors.append(f"{item.get('id')}: missing evidence {path}")
    detailed_rows = detailed.get("requirements", [])
    expected_ids = [f"OSL-RQ-{index:03d}" for index in range(1, 119)]
    if detailed.get("requirement_count") != 118 or [row.get("requirement_id") for row in detailed_rows] != expected_ids:
        errors.append("detailed register must contain stable OSL-RQ-001 through OSL-RQ-118")
    parent_ids = set(ids)
    for row in detailed_rows:
        for field in ("source_chapter", "source_heading", "requirement", "parent_requirement_id", "gate", "owner", "reviewer", "validation_method", "evidence", "status"):
            if field not in row: errors.append(f"{row.get('requirement_id')}: missing {field}")
        parent = row.get("parent_requirement_id")
        if parent not in parent_ids: errors.append(f"{row.get('requirement_id')}: unknown parent {parent}")
        if row.get("status") in OPEN and not row.get("blocker"): errors.append(f"{row.get('requirement_id')}: open item lacks blocker")
        for path in row.get("evidence", []):
            if not (ROOT / path).exists(): errors.append(f"{row.get('requirement_id')}: missing evidence {path}")
    packages = wp.get("work_packages", []); expected = {f"WP-{index:02d}" for index in range(1, 23)}
    by_id = {item.get("work_package_id"): item for item in packages}
    if set(by_id) != expected or len(packages) != 22: errors.append("work package register must contain WP-01 through WP-22 exactly once")
    for package_id, item in by_id.items():
        for field in ("objective", "owner_role", "accountable_role", "reviewer_role", "entry_criteria", "dependencies", "deliverables", "exit_evidence", "test_commands", "risks", "rollback", "status", "commit_or_artifact_ids"):
            if field not in item: errors.append(f"{package_id}: missing {field}")
        if package_id in {"WP-08", "WP-09", "WP-19", "WP-20"} and item.get("owner_role") == item.get("reviewer_role"): errors.append(f"{package_id}: independent reviewer required")
        if item.get("status") in {"not_started", "partially_completed", "completed_controlled", "completed_interface"} and not item.get("blocker") and package_id not in {"WP-01", "WP-02", "WP-03", "WP-04", "WP-05", "WP-06", "WP-07", "WP-08", "WP-11", "WP-12", "WP-13", "WP-14", "WP-15", "WP-16"}: errors.append(f"{package_id}: open or controlled status lacks blocker")
        for dependency in item.get("dependencies", []):
            if dependency not in by_id: errors.append(f"{package_id}: unknown dependency {dependency}")
            elif item.get("status") in {"completed", "completed_controlled", "completed_interface"} and by_id[dependency].get("status") == "not_started": errors.append(f"{package_id}: completed before dependency {dependency}")
        for path in item.get("exit_evidence", []):
            if not (ROOT / path).exists(): errors.append(f"{package_id}: missing exit evidence {path}")
    summary = {"requirements": len(requirements), "detailed_requirements": len(detailed_rows), "requirements_open": sum(item.get("status") in OPEN for item in requirements), "work_packages": len(packages), "work_packages_completed": sum(item.get("status") in {"completed", "completed_controlled", "completed_interface", "completed_contract"} for item in packages), "external_gates_open": sum(item.get("gate") == "external" for item in requirements), "production_ready": False, "maturity": "controlled pilot"}
    return errors, summary

def main() -> int:
    errors, summary = validate()
    if errors:
        print("CIDM opportunity governance validation failed:")
        for error in errors: print(f"- {error}")
        return 1
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__": raise SystemExit(main())
