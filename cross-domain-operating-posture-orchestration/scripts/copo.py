#!/usr/bin/env python3
"""Deterministic, fail-closed COPO development kernel."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SCENARIOS = json.loads((ROOT / "contracts/scenarios.json").read_text())
ARCH = json.loads((REPO / "governance/domain-architecture-registry.json").read_text())
DOMAIN_BY_ID = {row["domain_id"]: row for row in ARCH["domains"]}
TRUSTED_LEDGER = json.loads((ROOT / "evaluations/fixtures/trusted-packet-ledger.json").read_text())

ERRORS = {
    "scope_missing": "COPO_SCOPE_MISSING", "scope_conflict": "COPO_SCOPE_CONFLICT",
    "single_domain": "COPO_SINGLE_DOMAIN_REDIRECT", "unsupported": "COPO_UNSUPPORTED_SCENARIO",
    "owner_missing": "COPO_REQUIRED_OWNER_MISSING", "owner_rejected": "COPO_OWNER_REJECTED",
    "partial": "COPO_PARTIAL_ACCEPTANCE", "overreach": "COPO_SOVEREIGNTY_OVERREACH",
    "hash": "COPO_PACKET_HASH_MISMATCH", "expired": "COPO_PACKET_EXPIRED",
    "not_comparable": "COPO_NOT_COMPARABLE", "ceiling": "COPO_CAUSAL_CEILING_EXCEEDED",
    "gate": "COPO_NONCOMPENSABLE_GATE_BLOCKED", "timeout": "COPO_REQUIRED_STAGE_TIMEOUT",
    "conflict": "COPO_CONFLICT_UNRESOLVED", "stale": "COPO_STALE_VERSION",
    "state": "COPO_ILLEGAL_STATE_TRANSITION", "write": "COPO_EXTERNAL_WRITE_FORBIDDEN",
}

CONFLICT_OWNER = {
    "object_granularity": "ERDG", "comparability": "F02", "evidence_causality": "F01",
    "capital": "D01", "financial_basis": "D06", "contract_lineage": "ERDG",
    "business_tradeoff": "repository_or_business_owner",
}


class CopoError(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        super().__init__(f"{code}: {detail}")


def canonical_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def governance_metadata(owner: str, status: str, as_of_time: str, seed: str) -> dict[str, Any]:
    digest = canonical_hash({"owner": owner, "status": status, "as_of_time": as_of_time, "seed": seed})
    return {"schema_version": "2.0.0", "runtime_version": "COPO-2026.07", "object_version": "v1",
            "as_of_time": as_of_time, "owner": owner, "status": status,
            "allowed_uses": ["controlled_orchestration"], "forbidden_uses": ["external_write"],
            "input_hash": digest, "content_hash": digest, "state_hash": digest}


def parse_time(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise CopoError(ERRORS["scope_conflict"], f"invalid {field}") from exc
    if parsed.tzinfo is None:
        raise CopoError(ERRORS["scope_conflict"], f"timezone required for {field}")
    return parsed


def validate_schema_payload(schema_name: str, payload: dict[str, Any]) -> None:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text())
    common = json.loads((ROOT / "schemas/common.schema.json").read_text())
    schema["properties"]["governance"] = common["$defs"]["governance"]
    schema["$defs"] = {**schema.get("$defs", {}), **common["$defs"]}
    errors = sorted(jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(payload), key=lambda e: list(e.path))
    if errors:
        raise CopoError(ERRORS["scope_conflict"], "schema:" + "|".join(error.message for error in errors[:5]))


def owner_authority_valid(owner: str, authority: str) -> bool:
    if owner in DOMAIN_BY_ID:
        return authority in DOMAIN_BY_ID[owner]["owned_decision_types"]
    return (owner, authority) in {("F01", "causal_qualification"), ("F02", "localization_comparability"), ("ERDG", "governance_validation")}


def validate_scope(scope: dict[str, Any]) -> None:
    if not scope:
        raise CopoError(ERRORS["scope_missing"], "operating scope is required")
    validate_schema_payload("operating-scope.schema.json", scope)
    comparison = scope.get("comparison", {}).get("comparability")
    if comparison in {"not_comparable", "conflicted", "expired", "not_assessed"}:
        raise CopoError(ERRORS["not_comparable"], comparison)
    time = scope.get("time", {})
    for name in ("baseline", "observation", "diagnostic", "maturity"):
        window = time[name]
        if parse_time(window["start"], f"{name}.start") >= parse_time(window["end"], f"{name}.end"):
            raise CopoError(ERRORS["scope_conflict"], f"invalid {name} window")
    as_of = parse_time(time["as_of_time"], "as_of_time")
    if parse_time(time["baseline"]["end"], "baseline.end") > parse_time(time["observation"]["start"], "observation.start"):
        raise CopoError(ERRORS["scope_conflict"], "baseline overlaps observation")
    if parse_time(time["observation"]["end"], "observation.end") > parse_time(time["diagnostic"]["start"], "diagnostic.start"):
        raise CopoError(ERRORS["scope_conflict"], "observation overlaps diagnostic")
    if parse_time(time["diagnostic"]["end"], "diagnostic.end") > as_of:
        raise CopoError(ERRORS["scope_conflict"], "diagnostic extends beyond as-of")
    if parse_time(time["decision_valid_until"], "decision_valid_until") <= as_of:
        raise CopoError(ERRORS["expired"], "decision validity must be after as-of")


def validate_trusted_ledger(ledger: dict[str, Any], cycle_id: str, scope_ref: str, now: str) -> dict[str, dict[str, Any]]:
    validate_schema_payload("trusted-packet-ledger.schema.json", ledger)
    unsigned = {k: v for k, v in ledger.items() if k not in {"ledger_hash", "signature"}}
    encoded = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    if canonical_hash(unsigned) != ledger["ledger_hash"]:
        raise CopoError(ERRORS["hash"], "trusted ledger content hash mismatch")
    keys = json.loads((ROOT / "contracts/trusted-ledger-keys.json").read_text())
    key = keys.get("keys", {}).get(ledger["key_id"])
    if keys.get("authority") != "ERDG" or not key or key.get("private_key_in_repository") is not False:
        raise CopoError(ERRORS["overreach"], "ledger key is not pinned to ERDG")
    public_key=base64.b64decode(key["public_key_base64"])
    protected_fingerprint=os.environ.get("ERDG_TRUSTED_KEY_FINGERPRINT")
    if protected_fingerprint and hashlib.sha256(public_key).hexdigest()!=protected_fingerprint:
        raise CopoError(ERRORS["hash"],"ERDG key differs from protected control-plane fingerprint")
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(base64.b64decode(ledger["signature"]), encoded)
    except (InvalidSignature, ValueError) as exc:
        raise CopoError(ERRORS["hash"], "ERDG ledger signature invalid") from exc
    if ledger["cycle_id"] != cycle_id or ledger["scope_ref"] != scope_ref:
        raise CopoError(ERRORS["scope_conflict"], "ledger cycle or scope mismatch")
    issued=parse_time(ledger["issued_at"],"ledger.issued_at");current=parse_time(now,"now");ledger_expiry=parse_time(ledger["expires_at"], "ledger.expires_at")
    if issued > current or issued >= ledger_expiry or ledger_expiry <= current:
        raise CopoError(ERRORS["expired"], "trusted ledger expired")
    entries = {row["owner"]: row for row in ledger["entries"]}
    if len(entries) != len(ledger["entries"]):
        raise CopoError(ERRORS["hash"], "duplicate ledger owner")
    for row in ledger["entries"]:
        expiry=parse_time(row["expires_at"],f"ledger entry {row['owner']} expires_at")
        if expiry <= current or expiry > ledger_expiry: raise CopoError(ERRORS["expired"],f"invalid ledger entry validity for {row['owner']}")
    return entries


def route_scenario(scenario: str, scope_ref: str) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise CopoError(ERRORS["unsupported"], scenario)
    row = SCENARIOS[scenario]
    return {"route_id": f"ROUTE-{scenario}", "scope_ref": scope_ref, "scenario": scenario,
            **row, "external_write": False}

def validate_canonical_route(route: dict[str, Any]) -> None:
    canonical=route_scenario(route.get("scenario", ""),route.get("scope_ref", ""))
    fields=("route_id","scope_ref","scenario","mode","required_owners","conditional_owners","gates","dependencies","external_write")
    if any(route.get(field)!=canonical.get(field) for field in fields):
        raise CopoError(ERRORS["overreach"],"submitted route differs from authoritative scenario contract")

def receipt_signed_payload(receipt: dict[str, Any]) -> dict[str, Any]:
    fields=("receipt_id","request_ref","cycle_id","scope_ref","owner","owner_authority","decision","accepted_fields","allowed_uses","packet_version","expires_at","external_write")
    return {field:receipt.get(field) for field in fields}


def authority_owner(decision_type: str) -> str:
    owners = [row["domain_id"] for row in ARCH["domains"] if decision_type in row["owned_decision_types"]]
    if len(owners) != 1:
        raise CopoError(ERRORS["overreach"], f"authority owner count={len(owners)} for {decision_type}")
    return owners[0]


def validate_receipt(receipt: dict[str, Any], expected: dict[str, Any], now: str) -> str:
    if receipt.get("external_write") is not False:
        raise CopoError(ERRORS["write"], "receipt requests write")
    validate_schema_payload("domain-receipt.schema.json", receipt)
    for key in ("cycle_id", "scope_ref", "owner"):
        if receipt.get(key) != expected.get(key):
            raise CopoError(ERRORS["scope_conflict"], f"receipt {key} mismatch")
    governance = receipt["governance"]
    if governance["owner"] != receipt["owner"] or governance["status"] != receipt["decision"]:
        raise CopoError(ERRORS["overreach"], "receipt governance owner/status mismatch")
    if not owner_authority_valid(receipt["owner"], receipt["owner_authority"]):
        raise CopoError(ERRORS["overreach"], "receipt authority is not owned by signer")
    if expected.get("owner_authority") and receipt["owner_authority"] != expected["owner_authority"]:
        raise CopoError(ERRORS["overreach"], "unexpected owner authority")
    if receipt.get("packet_version", 0) < expected.get("packet_version", 0):
        raise CopoError(ERRORS["stale"], "older receipt version")
    computed_hash=canonical_hash(receipt_signed_payload(receipt))
    if receipt["packet_hash"] != governance["content_hash"] or receipt["packet_hash"] != computed_hash:
        raise CopoError(ERRORS["hash"], "packet hash is not bound to governance content hash")
    if expected.get("packet_hash") and receipt["packet_hash"] != expected["packet_hash"]:
        raise CopoError(ERRORS["hash"], "packet hash does not match trusted packet ledger")
    payload = expected.get("packet_payload")
    if payload is not None and receipt.get("packet_hash") != canonical_hash(payload):
        raise CopoError(ERRORS["hash"], "content hash mismatch")
    if parse_time(receipt["expires_at"], "expires_at") <= parse_time(now, "now"):
        raise CopoError(ERRORS["expired"], "receipt expired")
    decision = receipt.get("decision")
    if decision == "rejected":
        raise CopoError(ERRORS["owner_rejected"], receipt["owner"])
    if decision == "partially_accepted":
        return ERRORS["partial"]
    if decision in {"blocked", "inconclusive"}:
        raise CopoError(ERRORS["partial"], f"owner status={decision}")
    if decision != "accepted":
        raise CopoError(ERRORS["owner_rejected"], f"unsupported receipt decision={decision}")
    return "accepted"


def validate_graph(graph: dict[str, Any]) -> None:
    raw_nodes = graph.get("nodes", [])
    node_ids = [node["node_id"] for node in raw_nodes]
    if len(node_ids) != len(set(node_ids)):
        raise CopoError(ERRORS["scope_conflict"], "duplicate diagnostic node id")
    nodes = {node["node_id"]: node for node in raw_nodes}
    for node in nodes.values():
        if node["state"] == "domain_supported" and node["owner"] == "D14":
            raise CopoError(ERRORS["overreach"], "D14 cannot support a professional finding")
        if node["state"] == "causally_qualified" and node["owner"] != "F01":
            raise CopoError(ERRORS["ceiling"], "only F01 may qualify causal claims")
        if node["node_type"] == "domain_finding" and node["owner"] not in {f"D{i:02d}" for i in range(1, 14)}:
            raise CopoError(ERRORS["overreach"], "domain finding requires a professional owner")
        if node["node_type"] == "causal_claim" and node["owner"] != "F01":
            raise CopoError(ERRORS["ceiling"], "causal claim requires F01 ownership")
        if node["state"] in {"domain_supported", "causally_qualified"} and not node.get("evidence_refs"):
            raise CopoError(ERRORS["scope_missing"], "qualified graph node requires evidence")
    edges = graph.get("edges", [])
    edge_keys = [(edge["from"], edge["to"], edge["relation"]) for edge in edges]
    if len(edge_keys) != len(set(edge_keys)):
        raise CopoError(ERRORS["scope_conflict"], "duplicate diagnostic edge")
    dependencies = {node_id: [] for node_id in nodes}
    allowed_sources = {
        "supports": {"observed_change", "domain_finding", "counter_evidence", "causal_claim"},
        "contradicts": {"domain_finding", "counter_evidence"},
        "constrains": {"constraint"},
        "requires": set(node["node_type"] for node in nodes.values()),
    }
    for edge in edges:
        if edge["from"] not in nodes or edge["to"] not in nodes:
            raise CopoError(ERRORS["scope_conflict"], "graph edge references absent node")
        if edge["from"] == edge["to"]:
            raise CopoError(ERRORS["conflict"], "diagnostic graph self-loop")
        source = nodes[edge["from"]]
        if source["node_type"] not in allowed_sources[edge["relation"]]:
            raise CopoError(ERRORS["scope_conflict"], "illegal relation for source node type")
        if source["state"] in {"contradicted", "invalidated"} and edge["relation"] == "supports":
            raise CopoError(ERRORS["conflict"], "invalidated node cannot support downstream claims")
        dependencies[edge["to"]].append(edge["from"])
    topological_order(dependencies)


def conflict_owner(conflict_type: str, professional_owner: str | None = None) -> str:
    if conflict_type in {"resource_capacity", "professional_conclusion"}:
        if not professional_owner or professional_owner in {"D14", "F01", "F02", "ERDG"}:
            raise CopoError(ERRORS["conflict"], "qualified professional owner required")
        return professional_owner
    return CONFLICT_OWNER.get(conflict_type, "repository_or_business_owner")


def topological_order(dependencies: dict[str, list[str]]) -> list[str]:
    nodes = set(dependencies)
    for deps in dependencies.values(): nodes.update(deps)
    incoming = {node: 0 for node in nodes}
    outgoing = {node: [] for node in nodes}
    for node, deps in dependencies.items():
        for dep in deps:
            incoming[node] += 1; outgoing[dep].append(node)
    queue = deque(sorted(node for node, count in incoming.items() if count == 0)); result = []
    while queue:
        node = queue.popleft(); result.append(node)
        for nxt in sorted(outgoing[node]):
            incoming[nxt] -= 1
            if incoming[nxt] == 0: queue.append(nxt)
    if len(result) != len(nodes):
        raise CopoError(ERRORS["conflict"], "dependency cycle")
    return result


def posture_qualification(route: dict[str, Any], receipts: list[dict[str, Any]], gates: dict[str, str],
                          f02: str, requested: str, *, cycle_id: str, now: str,
                          trusted_ledger: dict[str, Any]) -> dict[str, Any]:
    entries = validate_trusted_ledger(trusted_ledger, cycle_id, route["scope_ref"], now)
    validated: list[dict[str, Any]] = []
    for receipt in receipts:
        owner = receipt.get("owner")
        if owner not in entries:
            raise CopoError(ERRORS["stale"], f"missing trusted packet ledger entry for {owner}")
        outcome = validate_receipt(receipt, {"cycle_id": cycle_id, "scope_ref": route["scope_ref"], "owner": owner, "owner_authority":entries[owner]["owner_authority"], "packet_version": entries[owner]["packet_version"], "packet_hash": entries[owner]["packet_hash"]}, now)
        if outcome == "accepted":
            if "operating_posture_synthesis" not in receipt["allowed_uses"]:
                raise CopoError(ERRORS["overreach"], "receipt does not allow posture synthesis")
            validated.append(receipt)
    accepted = {r["owner"] for r in validated}
    missing = sorted(set(route["required_owners"]) - accepted)
    if missing:
        return {"status": "inconclusive", "posture": requested, "action_ceiling": "analysis_only",
                "error": ERRORS["owner_missing"], "missing": missing, "external_write": False}
    if f02 != "comparable":
        return {"status": "blocked", "posture": requested, "action_ceiling": "analysis_only",
                "error": ERRORS["not_comparable"], "external_write": False}
    blocked = sorted(name for name in route["gates"] if gates.get(name) != "passed")
    if blocked:
        return {"status": "blocked", "posture": requested, "action_ceiling": "analysis_only",
                "error": ERRORS["gate"], "blocked_gates": blocked, "external_write": False}
    return {"status": "owner_approval_pending", "posture": requested,
            "action_ceiling": "owner_review_required", "external_write": False}


def build_coordination_plan(route: dict[str, Any], receipts: list[dict[str, Any]], owner_actions: list[dict[str, Any]],
                            *, cycle_id: str, now: str, trusted_ledger: dict[str, Any]) -> dict[str, Any]:
    entries = validate_trusted_ledger(trusted_ledger, cycle_id, route["scope_ref"], now)
    approved: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        owner = receipt.get("owner")
        if owner not in entries:
            raise CopoError(ERRORS["stale"], f"missing trusted packet ledger entry for {owner}")
        if validate_receipt(receipt, {"cycle_id": cycle_id, "scope_ref": route["scope_ref"], "owner": owner, "owner_authority":entries[owner]["owner_authority"], "packet_version": entries[owner]["packet_version"], "packet_hash": entries[owner]["packet_hash"]}, now) == "accepted":
            approved[receipt["receipt_id"]] = receipt
    for action in owner_actions:
        receipt = approved.get(action.get("approval_ref"))
        if (
            receipt is None
            or action.get("owner") == "D14"
            or receipt.get("owner") != action.get("owner")
            or receipt.get("scope_ref") != route.get("scope_ref")
            or action.get("scope_ref") != route.get("scope_ref")
            or "approved_action_sequencing" not in receipt.get("allowed_uses", [])
            or action.get("action_ref") not in receipt.get("accepted_fields", [])
        ):
            raise CopoError(ERRORS["overreach"], "plan may sequence only owner-approved actions")
    order = topological_order(route["dependencies"])
    return {"scenario": route["scenario"], "scope_ref": route["scope_ref"], "stage_order": order,
            "owner_action_refs": [a["action_ref"] for a in owner_actions], "external_write": False}


def impact_closure(changed: set[str], consumers: dict[str, list[str]]) -> list[str]:
    result, queue = set(changed), deque(sorted(changed))
    while queue:
        item = queue.popleft()
        for consumer in consumers.get(item, []):
            if consumer not in result: result.add(consumer); queue.append(consumer)
    return sorted(result)


def current_effective(postures: list[dict[str, Any]]) -> dict[str, Any] | None:
    active = [p for p in postures if p["status"] == "active"]
    if len(active) > 1:
        raise CopoError(ERRORS["state"], "more than one current active posture")
    return active[0] if active else None


CHILD_CYCLE_FIELDS = {"object", "market", "time", "economics", "key_claim", "owner_decision", "gate", "action_ceiling", "stop_condition", "rollback_condition"}


def requires_child_cycle(changed_fields: set[str]) -> bool:
    """Formatting and explanation-only changes stay in the current cycle."""
    return bool(changed_fields & CHILD_CYCLE_FIELDS)


def apply_cycle_event(state: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    """Append an idempotent event without overwriting history."""
    if event.get("external_write") is not False:
        raise CopoError(ERRORS["write"], "cycle event must be read-only")
    result = json.loads(json.dumps(state))
    seen = {row["message_id"]: row for row in result.get("events", [])}
    if event["message_id"] in seen:
        if canonical_hash(seen[event["message_id"]]) != canonical_hash(event):
            raise CopoError(ERRORS["hash"], "same message id carries different content")
        return result
    if event.get("cycle_id") != result.get("cycle_id"):
        raise CopoError(ERRORS["scope_conflict"], "event cycle mismatch")
    if event.get("object_version", 0) < result.get("object_version", 0):
        raise CopoError(ERRORS["stale"], "late event cannot overwrite current object")
    result.setdefault("events", []).append(event)
    result["state_version"] = result.get("state_version", 0) + 1
    result["state_hash"] = canonical_hash({k: v for k, v in result.items() if k != "state_hash"})
    return result


def validate_outcome_replay(replay: dict[str, Any], known_action_refs: set[str]) -> None:
    if replay.get("external_write") is not False:
        raise CopoError(ERRORS["write"], "outcome replay must be read-only")
    if not set(replay.get("owner_action_refs", [])).issubset(known_action_refs):
        raise CopoError(ERRORS["overreach"], "outcome references an unknown or unapproved action")
    if not replay.get("observed_outcomes") and not replay.get("incidents"):
        raise CopoError(ERRORS["scope_missing"], "replay requires observed outcomes or incidents")


def validate_independent_evidence(evidence: list[dict[str, Any]], minimum_sources: int = 2) -> None:
    source_groups = {row.get("source_group") for row in evidence if row.get("source_group")}
    if len(source_groups) < minimum_sources:
        raise CopoError(ERRORS["overreach"], "same-source evidence cannot claim independent confirmation")


def validate_computed_status(claimed: str, computed: str) -> None:
    if claimed != computed:
        raise CopoError(ERRORS["state"], "manual completion cannot override computed status")


def causal_wording_ceiling(ce_grade: str) -> str:
    if ce_grade not in {f"CE{i}" for i in range(6)}:
        raise CopoError(ERRORS["ceiling"], "unknown causal evidence grade")
    return "causal_wording_allowed" if ce_grade in {"CE4", "CE5"} else "noncausal_only"


def optional_failure_status(route: dict[str, Any], receipts: list[dict[str, Any]], *, cycle_id: str,
                            now: str, trusted_ledger: dict[str, Any]) -> str:
    entries = validate_trusted_ledger(trusted_ledger, cycle_id, route["scope_ref"], now)
    conditional = set(route["conditional_owners"])
    for receipt in receipts:
        if receipt.get("owner") not in conditional:
            continue
        try:
            entry=entries[receipt["owner"]]
            outcome = validate_receipt(receipt, {"cycle_id": cycle_id, "scope_ref": route["scope_ref"],
                                       "owner": receipt["owner"], "packet_version": entry["packet_version"],
                                       "packet_hash": entry["packet_hash"]}, now)
        except CopoError:
            return "partially_qualified"
        if outcome != "accepted":
            return "partially_qualified"
    return "qualified"


def transition_posture(status: str, event: str) -> str:
    transitions = {("active", "rollback"): "rolled_back", ("active", "stop"): "stopped",
                   ("approved", "activate"): "active", ("owner_approval_pending", "approve"): "approved"}
    target = transitions.get((status, event))
    if target is None:
        raise CopoError(ERRORS["state"], f"illegal posture transition {status}->{event}")
    return target
