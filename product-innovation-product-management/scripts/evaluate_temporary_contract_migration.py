#!/usr/bin/env python3
"""Classify dual-run migration differences and compute a fail-closed decision."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def evaluate(payload: dict) -> dict:
    mappings = payload.get("mappings", [])
    differences = payload.get("differences", [])
    accepted = all(x.get("status") == "accepted" for x in payload.get("consumer_acceptance", []))
    mapping_by_source = {x["source_field"]: x for x in mappings}
    blockers: list[str] = []
    classified: list[dict] = []
    for diff in differences:
        source = diff["source_field"]
        mapping = mapping_by_source.get(source)
        if not mapping:
            classification, criticality = "unmapped", diff.get("criticality", "major")
        else:
            classification, criticality = mapping["classification"], mapping["criticality"]
        severity = "P0" if criticality == "safety_critical" else "P1" if criticality == "major" else "P2"
        classified.append({"source_field": source, "classification": classification, "severity": severity})
        if severity in {"P0", "P1"} or classification in {"lossy", "unmapped"}:
            blockers.append(f"{source}:{classification}:{severity}")
    if not payload.get("legacy_read_preserved"):
        blockers.append("legacy_read_not_preserved")
    if not accepted:
        blockers.append("consumer_acceptance_open")
    if payload.get("temporary_snapshot_id") != payload.get("formal_snapshot_id"):
        blockers.append("snapshot_mismatch")
    return {"status": "rollback" if blockers else "accept", "differences": sorted(classified, key=lambda x: x["source_field"]), "blockers": sorted(blockers)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"PIPM_MIGRATION=BLOCKED:{exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
