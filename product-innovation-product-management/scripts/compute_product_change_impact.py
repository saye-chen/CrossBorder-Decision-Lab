#!/usr/bin/env python3
"""Compute deterministic field-level selective recomputation."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


class ImpactError(ValueError):
    pass


def compute(payload: dict) -> dict:
    changed = set(payload.get("changed_fields", []))
    graph = payload.get("dependencies", {})
    universe = set(payload.get("all_fields", [])) | set(graph) | {x for values in graph.values() for x in values}
    if not changed or not changed <= universe:
        raise ImpactError("changed_fields must be non-empty known fields")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ImpactError(f"dependency cycle at {node}")
        if node in visited:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            visit(child)
        visiting.remove(node)
        visited.add(node)

    for node in sorted(universe):
        visit(node)
    affected = set(changed)
    queue = sorted(changed)
    while queue:
        node = queue.pop(0)
        for child in sorted(graph.get(node, [])):
            if child not in affected:
                affected.add(child)
                queue.append(child)
    claim_fields = payload.get("claim_fields", {})
    expired = sorted(cid for cid, field in claim_fields.items() if field in affected)
    rejected = set(payload.get("rejected_claim_ids", []))
    reaccept = sorted(set(expired) - rejected)
    return {
        "status": "partial" if rejected else "complete",
        "changed_fields": sorted(changed),
        "recompute_fields": sorted(affected - changed),
        "preserved_fields": sorted(universe - affected),
        "expired_claim_ids": expired,
        "reaccept_claim_ids": reaccept,
        "blocked_reason": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = compute(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ImpactError) as exc:
        print(f"PIPM_RECOMPUTE=BLOCKED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
