#!/usr/bin/env python3
"""Fail-closed semantic validator for PPFC cross-domain envelopes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ppfc_common import PPFCError, parse_time

PPFC = "pricing-profit-finance-cashflow-decision"
DOMAINS = {
    PPFC, "category-investment-decision", "competitive-intelligence-monitoring",
    "video-link-breakdown", "consumer-insights-customer-growth",
    "advertising-analysis-measurement-optimization",
    "logistics-inventory-fulfillment-decision",
    "platform-store-listing-conversion",
    "creator-affiliate-partnership-management",
    "marketing-brand-campaign-management",
}
PAYLOAD_TYPES = {"input_fact", "economic_constraint", "recompute_request", "acceptance", "rejection", "result_observation"}
STATUSES = {"proposed", "validated", "blocked", "inconclusive", "superseded"}
EXTERNAL_ACTIONS = {"external_write", "change_price", "change_budget", "place_order", "send_sample", "sign_contract", "release_funds"}


def require(value: Any, message: str) -> None:
    if not value:
        raise PPFCError(message)


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    required = {
        "contract", "message_id", "message_version", "correlation_id", "idempotency_key",
        "sender", "receiver", "object_ref", "scope", "payload_type", "status", "claims",
        "evidence_ids", "calculations", "allowed_uses", "forbidden_uses",
        "blocked_actions", "accepted_by_receiver", "validity", "lineage",
    }
    missing = sorted(required - set(payload))
    require(not missing, f"missing required fields: {missing}")
    require(payload["contract"] == "PPFC-XDOMAIN-2026.01", "unsupported contract")
    require(payload["sender"] in DOMAINS and payload["receiver"] in DOMAINS, "unknown domain")
    require(payload["sender"] != payload["receiver"], "sender and receiver must differ")
    require(payload["payload_type"] in PAYLOAD_TYPES, "invalid payload_type")
    require(payload["status"] in STATUSES, "invalid status")
    require(isinstance(payload["claims"], list) and payload["claims"], "claims must be non-empty")
    require(isinstance(payload["evidence_ids"], list) and payload["evidence_ids"], "evidence_ids must be non-empty")
    allowed, forbidden = set(payload["allowed_uses"]), set(payload["forbidden_uses"])
    require(not (allowed & forbidden), "allowed and forbidden uses overlap")
    require(EXTERNAL_ACTIONS <= forbidden, "all external actions must be forbidden")
    require(not payload["accepted_by_receiver"], "cross-domain message cannot self-assert receiver acceptance")
    object_ref = payload["object_ref"]
    require(all(object_ref.get(k) for k in ("object_id", "object_version", "object_type")), "incomplete object_ref")
    scope = payload["scope"]
    require(all(scope.get(k) for k in ("country", "platform", "currency", "tax_basis", "as_of_time")), "incomplete scope")
    parse_time(scope["as_of_time"], "scope.as_of_time")
    validity = payload["validity"]
    valid_from = parse_time(validity.get("valid_from"), "validity.valid_from")
    recorded_at = parse_time(validity.get("recorded_at"), "validity.recorded_at")
    if validity.get("valid_to") is not None:
        require(parse_time(validity["valid_to"], "validity.valid_to") > valid_from, "valid_to must follow valid_from")
    require(recorded_at >= valid_from, "recorded_at cannot precede valid_from")
    lineage = payload["lineage"]
    require(lineage.get("runtime_version") == "PPFC-2026.01", "runtime version mismatch")
    require(str(lineage.get("input_hash", "")).startswith("sha256:"), "lineage.input_hash is required")
    require(lineage.get("parameter_snapshot_id"), "parameter snapshot is required")
    if payload["sender"] == PPFC:
        require(payload["payload_type"] in {"economic_constraint", "recompute_request", "result_observation"}, "PPFC cannot own source-domain facts or acceptance")
        require(payload["status"] in {"proposed", "blocked", "inconclusive", "superseded"}, "PPFC outbound result cannot self-validate receiver action")
    if payload["payload_type"] in {"acceptance", "rejection"}:
        require(payload["receiver"] == PPFC, "acceptance or rejection must return to PPFC")
        require(payload["sender"] != PPFC, "PPFC cannot accept on behalf of receiving domain")
    if payload["status"] in {"blocked", "inconclusive"}:
        require(payload["blocked_actions"], "blocked or inconclusive message requires blocked_actions")
    return {"valid": True, "contract": payload["contract"], "status": payload["status"], "action_ceiling": "analysis_only" if payload["status"] != "proposed" else "controlled_test"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise PPFCError("root must be object")
        result = validate(payload)
    except (OSError, json.JSONDecodeError, PPFCError) as exc:
        print(f"PPFC_XDOMAIN=BLOCKED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
