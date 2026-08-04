#!/usr/bin/env python3
"""Deterministic REALITY_RECOVERY impact, priority and closure governance."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from decimal import Decimal, InvalidOperation
from typing import Any

RECOVERY_STATES = {"detected", "frozen", "triaged", "recalculating", "partially_recovered", "recovered", "escalated", "closed"}
ACTIVE_ACTIONS = {"planned", "approved", "executing"}
RESOLVED_CONSUMER_STATES = {"recovered", "escalated", "closed"}


class RecoveryError(ValueError):
    pass


def _decimal(value: Any, field: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise RecoveryError(f"{field} must be decimal-compatible") from exc
    if not number.is_finite():
        raise RecoveryError(f"{field} must be finite")
    return number


def _hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()


def impact_closure(root_ids: list[str], edges: list[dict[str, str]]) -> list[str]:
    graph: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        source, target = edge.get("source"), edge.get("target")
        if not source or not target:
            raise RecoveryError("lineage edge requires source and target")
        graph[source].add(target)
    visited = set(root_ids)
    queue = deque(root_ids)
    while queue:
        current = queue.popleft()
        for target in sorted(graph[current]):
            if target not in visited:
                visited.add(target); queue.append(target)
    return sorted(visited)


def net_capital_at_risk(assets: list[dict[str, Any]]) -> Decimal:
    """Calculate asset-bound risk capital once; duplicate asset IDs are rejected."""
    seen: set[str] = set()
    total = Decimal("0")
    fields = {"committed_cash", "recoverable_cash", "inventory_cost", "inventory_recovery_value", "cancellation_penalty", "incremental_loss"}
    for asset in assets:
        asset_id = asset.get("asset_id")
        if not asset_id or asset_id in seen:
            raise RecoveryError("asset_id must be unique and nonempty")
        seen.add(asset_id)
        unknown = set(asset) - fields - {"asset_id"}
        if unknown:
            raise RecoveryError(f"unknown capital fields: {sorted(unknown)}")
        values = {field: _decimal(asset.get(field, 0), field) for field in fields}
        if any(value < 0 for value in values.values()):
            raise RecoveryError("capital components must be nonnegative")
        if values["committed_cash"] and values["inventory_cost"]:
            raise RecoveryError("same asset cannot count committed cash and inventory cost together")
        total += values["committed_cash"] - values["recoverable_cash"] + values["inventory_cost"] - values["inventory_recovery_value"] + values["cancellation_penalty"] + values["incremental_loss"]
    return total


def classify_queue(consumer: dict[str, Any], calibration: dict[str, Any]) -> str:
    flags = set(consumer.get("risk_flags", []))
    if flags & {"human_safety", "illegal", "recall", "hygiene", "account_level_redline"}:
        return "R0"
    if flags & {"irreversible_action_imminent", "loss_expanding", "payment_imminent", "production_release_imminent", "launch_imminent"}:
        return "R1"
    capital = net_capital_at_risk(consumer.get("assets", []))
    threshold = _decimal(calibration.get("r2_net_capital_threshold"), "r2_net_capital_threshold")
    if capital >= threshold:
        return "R2"
    if consumer.get("decision_tier_may_change") or int(consumer.get("blast_radius", 0)) >= int(calibration.get("r3_blast_radius_threshold")):
        return "R3"
    return "R4"


def build_root_batch(event: dict[str, Any], edges: list[dict[str, str]], consumers: list[dict[str, Any]], calibration: dict[str, Any]) -> dict[str, Any]:
    root_ids = event.get("invalidated_evidence_ids")
    if not isinstance(root_ids, list) or not root_ids:
        raise RecoveryError("invalidated_evidence_ids are required")
    affected = set(impact_closure(root_ids, edges))
    impacted = []
    for consumer in consumers:
        dependencies = set(consumer.get("dependency_ids", []))
        if not dependencies & affected:
            continue
        queue = classify_queue(consumer, calibration)
        capital = net_capital_at_risk(consumer.get("assets", []))
        action_status = consumer.get("action_status")
        impacted.append({
            "consumer_id": consumer["consumer_id"],
            "decision_id": consumer["decision_id"],
            "previous_effective_decision_id": consumer.get("current_effective_decision_id"),
            "queue": queue,
            "net_capital_at_risk": str(capital),
            "recovery_status": "frozen",
            "action_status": "paused" if action_status in ACTIVE_ACTIONS else action_status,
            "recalculation_complete": False,
            "gates_rechecked": False,
            "consumer_notified": False,
            "new_effective_decision_id": None,
            "resolution_action": None,
        })
    if not impacted:
        raise RecoveryError("invalidated evidence has no registered consumers")
    queue = min((item["queue"] for item in impacted), key=lambda value: int(value[1]))
    batch = {
        "batch_id": event.get("batch_id"),
        "root_evidence_ids": sorted(root_ids),
        "affected_lineage_ids": sorted(affected),
        "queue": queue,
        "recovery_status": "frozen",
        "created_at": event.get("detected_at"),
        "consumers": sorted(impacted, key=lambda item: (int(item["queue"][1]), item["consumer_id"])),
        "external_actions_automated": False,
        "current_effective_decision_policy": "one_per_object",
    }
    if not batch["batch_id"] or not batch["created_at"]:
        raise RecoveryError("batch_id and detected_at are required")
    batch["batch_hash"] = _hash(batch)
    return batch


def apply_consumer_recovery(batch: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    if batch.get("recovery_status") == "closed":
        raise RecoveryError("closed recovery batch is append-only")
    matches = [item for item in batch.get("consumers", []) if item["consumer_id"] == update.get("consumer_id")]
    if len(matches) != 1:
        raise RecoveryError("consumer update must resolve exactly one registered consumer")
    consumer = matches[0]
    target = update.get("recovery_status")
    if target not in {"recalculating", "partially_recovered", "recovered", "escalated"}:
        raise RecoveryError("invalid consumer recovery target")
    if target in {"recovered", "escalated"}:
        required = {"recalculation_complete", "gates_rechecked", "consumer_notified", "resolution_action"}
        if any(not update.get(field) for field in required):
            raise RecoveryError("resolved consumer lacks recomputation, gates, notification or resolution")
        if target == "recovered" and not update.get("new_effective_decision_id"):
            raise RecoveryError("recovered consumer requires one new effective decision")
        if update.get("new_effective_decision_id") == consumer.get("previous_effective_decision_id") and update.get("decision_changed"):
            raise RecoveryError("changed decision cannot retain the previous effective decision id")
    consumer.update({key: value for key, value in update.items() if key != "consumer_id"})
    states = {item["recovery_status"] for item in batch["consumers"]}
    if states <= RESOLVED_CONSUMER_STATES:
        batch["recovery_status"] = "recovered" if "escalated" not in states else "escalated"
    elif states & RESOLVED_CONSUMER_STATES:
        batch["recovery_status"] = "partially_recovered"
    else:
        batch["recovery_status"] = "recalculating"
    batch["batch_hash"] = _hash({key: value for key, value in batch.items() if key != "batch_hash"})
    return batch


def close_batch(batch: dict[str, Any], closure: dict[str, Any]) -> dict[str, Any]:
    if batch.get("recovery_status") not in {"recovered", "escalated"}:
        raise RecoveryError("partial consumer recovery cannot close root batch")
    if any(item.get("recovery_status") not in RESOLVED_CONSUMER_STATES for item in batch.get("consumers", [])):
        raise RecoveryError("all consumers must be resolved")
    required = {"replacement_evidence_status", "root_cause_test_id", "loss_recorded", "owner_recorded", "prevention_action"}
    if any(not closure.get(field) for field in required):
        raise RecoveryError("closure evidence is incomplete")
    if closure["replacement_evidence_status"] not in {"validated", "unrecoverable"}:
        raise RecoveryError("replacement evidence status must be validated or unrecoverable")
    batch["closure"] = closure
    batch["recovery_status"] = "closed"
    batch["closed_at"] = closure.get("closed_at")
    if not batch["closed_at"]:
        raise RecoveryError("closed_at is required")
    batch["batch_hash"] = _hash({key: value for key, value in batch.items() if key != "batch_hash"})
    return batch
