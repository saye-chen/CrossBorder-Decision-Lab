#!/usr/bin/env python3
"""Validate PPFC professional output completeness and authority boundaries."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ppfc_common import PPFCError, parse_time

REQUIRED = {
    "report_id", "report_version", "report_type", "decision_id", "decision_version", "status",
    "is_current", "object_ref", "scope", "as_of_time", "current_conclusion", "history_refs",
    "evidence", "counterevidence", "conflicts", "missing_data", "baseline", "candidates",
    "calculations", "parameter_snapshot_id", "economics", "metrics", "sensitivity",
    "attribution_incrementality", "actions", "success_conditions", "stop_conditions",
    "rollback_conditions", "exit_conditions", "allowed_uses", "forbidden_uses", "lineage",
}
EXTERNAL = {"external_write", "change_price", "change_budget", "place_order", "release_funds"}


def validate(report: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(REQUIRED - set(report))
    if missing: raise PPFCError(f"missing report fields: {missing}")
    parse_time(report["as_of_time"], "as_of_time")
    for field in ("evidence", "counterevidence", "candidates", "calculations", "metrics", "actions", "success_conditions", "stop_conditions", "rollback_conditions", "exit_conditions", "allowed_uses", "forbidden_uses"):
        if not isinstance(report[field], list) or not report[field]: raise PPFCError(f"{field} must be non-empty")
    if set(report["allowed_uses"]) & set(report["forbidden_uses"]):
        raise PPFCError("allowed and forbidden uses overlap")
    if not EXTERNAL <= set(report["forbidden_uses"]):
        raise PPFCError("external actions must remain forbidden")
    lineage = report["lineage"]
    if lineage.get("runtime_version") != "PPFC-2026.01": raise PPFCError("runtime version mismatch")
    for key in ("input_hash", "output_hash"):
        if not str(lineage.get(key, "")).startswith("sha256:"): raise PPFCError(f"lineage.{key} required")
    if report["status"] in {"validated", "accepted", "executed", "observed", "closed"} and report["missing_data"]:
        raise PPFCError("mature status cannot retain unresolved missing_data")
    return {"valid": True, "report_type": report["report_type"], "status": report["status"], "decision_id": report["decision_id"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        report = json.loads(args.input.read_text(encoding="utf-8")); result = validate(report)
    except (OSError, json.JSONDecodeError, PPFCError) as exc:
        print(f"PPFC_REPORT=BLOCKED: {exc}", file=sys.stderr); return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
