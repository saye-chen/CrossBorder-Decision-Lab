#!/usr/bin/env python3
"""Fail-closed semantic validator for the additive D03-D06 envelope."""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

PIPM = "product-innovation-product-management"
PPFC = "pricing-profit-finance-cashflow-decision"
EXTERNAL = {"external_write", "change_price", "release_funds", "place_order", "publish_listing"}


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def parse_time(value: str, field: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ContractError(f"invalid {field}") from exc


def validate(payload: dict, seen: set[tuple[str, str]] | None = None) -> dict:
    required = {"contract", "message_id", "message_version", "correlation_id", "idempotency_key", "sender", "receiver", "object_ref", "scope", "payload_type", "status", "claims", "claim_acceptance", "changed_fields", "recomputation", "allowed_uses", "forbidden_uses", "external_write", "validity", "lineage"}
    require(not (required - set(payload)), f"missing required fields: {sorted(required-set(payload))}")
    require(payload["contract"] == "PIPM-XDOMAIN-2026.01", "unsupported contract")
    require(payload["message_version"] == "PIPM-XMSG-2026.01", "unsupported message version")
    require({payload["sender"], payload["receiver"]} == {PIPM, PPFC}, "route must be D03-D06")
    require(payload["status"] in {"proposed", "blocked", "inconclusive", "superseded"}, "receiver-owned result cannot self-validate")
    require(payload["external_write"] is False, "external_write must be false")
    require(EXTERNAL <= set(payload["forbidden_uses"]), "external actions must be forbidden")
    require(not (set(payload["allowed_uses"]) & set(payload["forbidden_uses"])), "allowed and forbidden uses overlap")
    require(len(payload["idempotency_key"]) >= 8, "invalid idempotency key")
    key = (payload["message_id"], payload["idempotency_key"])
    duplicate = bool(seen is not None and key in seen)
    if seen is not None:
        seen.add(key)
    claims = payload["claims"]
    require(isinstance(claims, list) and claims, "claims must be non-empty")
    claim_ids = [x.get("claim_id") for x in claims]
    require(all(claim_ids) and len(claim_ids) == len(set(claim_ids)), "claim ids must be unique")
    decisions = payload["claim_acceptance"]
    decision_ids = [x.get("claim_id") for x in decisions]
    require(len(decision_ids) == len(set(decision_ids)) and set(decision_ids) <= set(claim_ids), "acceptance references unknown or duplicate claim")
    for item in decisions:
        require(item.get("decision") in {"accepted", "rejected", "blocked"}, "invalid claim decision")
        if item.get("decision") != "accepted":
            require(bool(item.get("reason")), "non-acceptance requires reason")
    if payload["payload_type"] in {"acceptance", "rejection"}:
        require(len(decisions) == len(claims), "response must decide every claim")
    scope = payload["scope"]
    require(all(scope.get(k) for k in ("country", "platform", "currency", "tax_basis", "as_of_time")), "incomplete scope")
    require(len(scope["currency"]) == 3 and scope["currency"].isupper(), "invalid currency")
    parse_time(scope["as_of_time"], "scope.as_of_time")
    validity = payload["validity"]
    valid_from = parse_time(validity.get("valid_from"), "validity.valid_from")
    recorded = parse_time(validity.get("recorded_at"), "validity.recorded_at")
    require(recorded >= valid_from, "recorded_at precedes valid_from")
    ref = payload["object_ref"]
    require(all(ref.get(k) for k in ("object_id", "object_version", "object_type")), "incomplete object identity/version")
    lineage = payload["lineage"]
    require(lineage.get("runtime_version") == ("PIPM-2026.01" if payload["sender"] == PIPM else "PPFC-2026.01"), "runtime/sender mismatch")
    require(str(lineage.get("input_hash", "")).startswith("sha256:"), "missing input hash")
    require(bool(lineage.get("parameter_snapshot_id")), "missing parameter snapshot")
    impact = payload["recomputation"]
    require(impact.get("status") in {"complete", "partial", "blocked"}, "invalid recomputation status")
    require(set(impact.get("changed_fields", [])) == set(payload["changed_fields"]), "changed_fields mismatch")
    return {"valid": True, "duplicate": duplicate, "effect": "no_op" if duplicate else "record_proposal", "accepted_claim_ids": sorted(x["claim_id"] for x in decisions if x["decision"] == "accepted"), "rejected_claim_ids": sorted(x["claim_id"] for x in decisions if x["decision"] != "accepted")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        value = json.loads(args.input.read_text(encoding="utf-8"))
        require(isinstance(value, dict), "root must be object")
        result = validate(value)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"PIPM_XDOMAIN=BLOCKED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
