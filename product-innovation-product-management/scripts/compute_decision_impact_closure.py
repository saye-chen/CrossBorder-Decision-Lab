#!/usr/bin/env python3
"""Compute typed evidence-to-action decision impact closure."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

TYPES = {"evidence", "claim", "calculation", "specification", "report", "action", "acceptance"}


class ImpactError(ValueError):
    pass


def compute(payload: dict) -> dict:
    nodes = payload.get("nodes", {})
    edges = payload.get("edges", {})
    changed = set(payload.get("changed_node_ids", []))
    if not changed or not changed <= set(nodes):
        raise ImpactError("unknown or empty changed nodes")
    versions = {v.get("object_version") for v in nodes.values()}
    if len(versions) != 1:
        raise ImpactError("cross-version dependency graph")
    for node, meta in nodes.items():
        if meta.get("type") not in TYPES:
            raise ImpactError(f"invalid node type:{node}")
    for source, targets in edges.items():
        if source not in nodes:
            raise ImpactError(f"orphan source:{source}")
        if any(target not in nodes for target in targets):
            raise ImpactError(f"orphan target:{source}")
    visiting: set[str] = set(); visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting: raise ImpactError("dependency cycle")
        if node in visited: return
        visiting.add(node)
        for child in edges.get(node, []): visit(child)
        visiting.remove(node); visited.add(node)
    for node in nodes: visit(node)
    affected = set(changed); queue = sorted(changed)
    while queue:
        source = queue.pop(0)
        for target in sorted(edges.get(source, [])):
            if target not in affected: affected.add(target); queue.append(target)
    by_type = {kind: sorted(x for x in affected if nodes[x]["type"] == kind) for kind in TYPES}
    return {
        "changed": sorted(changed),
        "expired": sorted(x for x in affected if nodes[x]["type"] in {"claim", "report", "action", "acceptance"}),
        "recomputed": sorted(x for x in affected if nodes[x]["type"] in {"calculation", "specification", "report"}),
        "reaccepted": by_type["acceptance"],
        "preserved": sorted(set(nodes) - affected),
        "blocked": sorted(x for x in affected if nodes[x].get("criticality") == "safety_critical"),
    }


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("input",type=Path); args=parser.parse_args()
    try: result=compute(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError,json.JSONDecodeError,ImpactError) as exc: print(f"PIPM_IMPACT=BLOCKED:{exc}",file=sys.stderr); return 1
    print(json.dumps(result,ensure_ascii=False,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
