#!/usr/bin/env python3
"""Compute deterministic PPFC dependency closure and recomputation actions."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from ppfc_common import PPFCError, canonical_hash


def compute(payload: dict[str, Any]) -> dict[str, Any]:
    nodes, edges, changed = payload.get("nodes"), payload.get("edges"), payload.get("changed_ids")
    if not isinstance(nodes, list) or not isinstance(edges, list) or not isinstance(changed, list):
        raise PPFCError("nodes, edges and changed_ids must be lists")
    ids = [node.get("id") for node in nodes if isinstance(node, dict)]
    if len(ids) != len(nodes) or any(not item for item in ids) or len(set(ids)) != len(ids):
        raise PPFCError("nodes require unique non-empty ids")
    node_by_id = {node["id"]: node for node in nodes}
    unknown = sorted(set(changed) - set(ids))
    if unknown:
        raise PPFCError(f"unknown changed ids: {unknown}")
    downstream: dict[str, set[str]] = defaultdict(set)
    indegree = {item: 0 for item in ids}
    for edge in edges:
        source, target = edge.get("from"), edge.get("to")
        if source not in indegree or target not in indegree:
            raise PPFCError("edge references unknown node")
        if target not in downstream[source]:
            downstream[source].add(target); indegree[target] += 1
    queue = deque(sorted(item for item, degree in indegree.items() if degree == 0))
    ordered = []
    while queue:
        item = queue.popleft(); ordered.append(item)
        for target in sorted(downstream[item]):
            indegree[target] -= 1
            if indegree[target] == 0: queue.append(target)
    if len(ordered) != len(ids):
        raise PPFCError("cyclic dependency graph")
    affected = set(changed); queue = deque(changed)
    while queue:
        for target in downstream[queue.popleft()]:
            if target not in affected:
                affected.add(target); queue.append(target)
    affected_ordered = [item for item in ordered if item in affected]
    unaffected = [item for item in ordered if item not in affected]
    actions = {"expire": [], "recompute": [], "reaccept": [], "rollback_review": []}
    for item in affected_ordered:
        node = node_by_id[item]
        action = node.get("on_change", "recompute")
        if action not in actions: raise PPFCError(f"invalid on_change action: {action}")
        actions[action].append(item)
    identity = {
        "changed_ids": sorted(changed), "affected_ids": affected_ordered,
        "input_hash": payload.get("input_hash"), "parameter_snapshot_id": payload.get("parameter_snapshot_id"),
        "model_version": payload.get("model_version"),
    }
    return {
        "status": "recompute_required" if affected_ordered else "no_change",
        "affected_ids": affected_ordered, "unaffected_ids": unaffected, "actions": actions,
        "impact_hash": "sha256:" + canonical_hash(identity),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8")); result = compute(payload)
    except (OSError, json.JSONDecodeError, PPFCError) as exc:
        print(f"PPFC_IMPACT=BLOCKED: {exc}", file=sys.stderr); return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
