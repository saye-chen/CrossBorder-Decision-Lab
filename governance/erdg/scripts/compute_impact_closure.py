#!/usr/bin/env python3
"""Compute deterministic downstream ERDG recomputation closure."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

MAX_LINEAGE_NODES = 10000
MAX_LINEAGE_EDGES = 50000


def compute(payload: dict[str, Any]) -> dict[str, Any]:
    nodes = payload.get("nodes")
    edges = payload.get("edges")
    changed = payload.get("changed_ids")
    if not isinstance(nodes, list) or not isinstance(edges, list) or not isinstance(changed, list):
        raise ValueError("nodes, edges and changed_ids must be lists")
    if len(nodes) > MAX_LINEAGE_NODES:
        raise ValueError(f"nodes exceeds capacity limit {MAX_LINEAGE_NODES}")
    if len(edges) > MAX_LINEAGE_EDGES:
        raise ValueError(f"edges exceeds capacity limit {MAX_LINEAGE_EDGES}")
    ids = {node.get("id") for node in nodes if isinstance(node, dict) and node.get("id")}
    if len(ids) != len(nodes):
        raise ValueError("nodes require unique non-empty ids")
    unknown_changed = set(changed) - ids
    if unknown_changed:
        raise ValueError(f"unknown changed ids: {sorted(unknown_changed)}")
    downstream: dict[str, set[str]] = defaultdict(set)
    indegree: dict[str, int] = {node_id: 0 for node_id in ids}
    for index, edge in enumerate(edges):
        source, target = edge.get("from"), edge.get("to")
        if source not in ids or target not in ids:
            raise ValueError(f"edges[{index}] references unknown node")
        if target not in downstream[source]:
            downstream[source].add(target)
            indegree[target] += 1
    queue = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
    ordered = []
    while queue:
        node_id = queue.popleft()
        ordered.append(node_id)
        for target in sorted(downstream[node_id]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(ordered) != len(ids):
        raise ValueError("cyclic lineage graph")
    affected = set(changed)
    queue = deque(changed)
    while queue:
        for target in downstream[queue.popleft()]:
            if target not in affected:
                affected.add(target)
                queue.append(target)
    closure = [node_id for node_id in ordered if node_id in affected]
    return {"status": "recompute_required", "changed_ids": changed, "affected_ids": closure, "unaffected_ids": [node_id for node_id in ordered if node_id not in affected]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(compute(payload), ensure_ascii=False, indent=2))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
