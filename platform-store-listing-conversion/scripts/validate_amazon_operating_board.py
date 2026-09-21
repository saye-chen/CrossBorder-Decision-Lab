#!/usr/bin/env python3
"""Fail-closed validator for Amazon daily/weekly operating boards."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any


SKILL_ROOT = pathlib.Path(__file__).resolve().parents[1]
OPS_PATH = SKILL_ROOT / "references/amazon-operating-workflows-and-metrics.json"
STORE_PATH = SKILL_ROOT / "references/amazon-store-operating-models.json"


def _unknown(value: Any) -> bool:
    return value is None or value == "" or (isinstance(value, str) and value in {"unknown", "UNKNOWN"})


def _load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(board: dict, ops: dict | None = None, store: dict | None = None) -> dict:
    ops = ops or _load(OPS_PATH)
    store = store or _load(STORE_PATH)
    errors: list[str] = []
    warnings: list[str] = []
    contract = ops["daily_board_contract"]
    for field in contract["required_fields"]:
        if field not in board:
            errors.append(f"missing:{field}")
    if board.get("platform") != "Amazon":
        errors.append("platform_must_be_Amazon")
    if board.get("external_write") is not False:
        errors.append("external_write_must_be_false")
    if not isinstance(board.get("input_evidence_ids"), list) or not board.get("input_evidence_ids"):
        errors.append("input_evidence_ids_must_be_nonempty_array")
    if not isinstance(board.get("metric_snapshot_ids"), list) or not board.get("metric_snapshot_ids"):
        errors.append("metric_snapshot_ids_must_be_nonempty_array")
    if not isinstance(board.get("metric_ids"), list) or not board.get("metric_ids"):
        errors.append("metric_ids_must_be_nonempty_array")

    archetype_ids = {item["id"] for item in store.get("operating_archetypes", [])}
    if board.get("operating_archetype_id") not in archetype_ids:
        errors.append("unknown_or_missing_operating_archetype")
    lifecycle_ids = {item["id"] for item in ops.get("state_machine", [])}
    if board.get("lifecycle_phase") not in lifecycle_ids:
        errors.append("unknown_or_missing_lifecycle_phase")
    if board.get("cadence") not in ops["dimensions"]["work_rhythm"]:
        errors.append("invalid_cadence")
    if board.get("metric_scope") not in ops["dimensions"]["metric_scope"]:
        errors.append("invalid_metric_scope")
    if board.get("metric_class") not in ops["dimensions"]["metric_class"]:
        errors.append("invalid_metric_class")
    if board.get("action_ceiling") not in ops["dimensions"]["action_ceiling"]:
        errors.append("invalid_action_ceiling")

    workstreams = {item["id"]: item for item in ops.get("workstreams", [])}
    workstream = workstreams.get(board.get("workstream_id"))
    if workstream is None:
        errors.append("unknown_or_missing_workstream")
    else:
        if board.get("cadence") not in workstream.get("cadence", []):
            errors.append("cadence_not_supported_by_workstream")
        applies = set(workstream.get("applies_to", []))
        if "all_operating_archetypes" not in applies and board.get("operating_archetype_id") not in applies:
            errors.append("workstream_not_available_for_archetype")

    metric_catalog = {item["id"]: item for item in ops.get("metric_catalog", [])}
    for metric_id in board.get("metric_ids", []):
        if metric_id not in metric_catalog:
            errors.append(f"unknown_metric:{metric_id}")
    records = board.get("metric_records", [])
    if not isinstance(records, list):
        errors.append("metric_records_must_be_array")
        records = []
    record_required = set(contract["metric_record_required_fields"])
    for index, record in enumerate(records):
        missing = sorted(field for field in record_required if field not in record)
        errors.extend(f"metric_record[{index}]:missing:{field}" for field in missing)
        metric = metric_catalog.get(record.get("metric_id"))
        if metric is None:
            errors.append(f"metric_record[{index}]:unknown_metric")
            continue
        if record.get("metric_scope") != metric.get("scope"):
            errors.append(f"metric_record[{index}]:metric_scope_mismatch")
        if record.get("metric_class") != metric.get("class"):
            errors.append(f"metric_record[{index}]:metric_class_mismatch")
        if record.get("value_state") in {"unknown", "conflict"} and _unknown(record.get("unknown_reason")):
            errors.append(f"metric_record[{index}]:unknown_reason_required")
        if record.get("value_state") in {"observed", "derived", "inferred"} and _unknown(record.get("evidence_id")):
            errors.append(f"metric_record[{index}]:evidence_required")

    for field in ("decision_question", "current_state", "action_ceiling", "success_conditions", "stop_conditions", "rollback_ref", "next_due", "as_of_time"):
        if _unknown(board.get(field)):
            warnings.append(f"unknown:{field}")

    if errors:
        status = "fail"
    elif warnings:
        status = "conditional"
    else:
        status = "pass"
    return {"status": status, "errors": errors, "warnings": warnings, "action_limit": "blocked" if errors else ("conditional_only" if warnings else board.get("action_ceiling"))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=pathlib.Path)
    args = parser.parse_args()
    result = validate(json.loads(args.board.read_text(encoding="utf-8")))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"pass", "conditional"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
