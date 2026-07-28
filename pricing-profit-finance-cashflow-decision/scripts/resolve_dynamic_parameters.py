#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ppfc_common import PPFCError, canonical_hash, parse_time


SCOPE_FIELDS = (
    "country_code", "platform_id", "contract_id", "store_id", "category_id",
    "product_id", "sku_id", "channel_id", "campaign_id", "fulfillment_mode",
    "carrier_id", "service_id", "route_id", "zone_id", "transport_mode",
    "cargo_type", "payment_method", "settlement_plan",
)


def scope_matches(scope: dict[str, Any], context: dict[str, Any]) -> bool:
    return all(value in {None, "*"} or context.get(field) == value for field, value in scope.items())


def resolve_one(code: str, rules: list[dict[str, Any]], context: dict[str, Any], business_time, knowledge_time) -> dict:
    related = [rule for rule in rules if rule.get("semantic_code") == code]
    active = []
    expired_seen = False
    for rule in related:
        start = parse_time(rule.get("valid_from"), "valid_from")
        end = parse_time(rule["valid_to"], "valid_to") if rule.get("valid_to") else None
        recorded = parse_time(rule.get("recorded_at"), "recorded_at")
        superseded = parse_time(rule["superseded_at"], "superseded_at") if rule.get("superseded_at") else None
        if business_time < start or (end and business_time >= end):
            expired_seen = True
            continue
        if knowledge_time < recorded or (superseded and knowledge_time >= superseded):
            continue
        if rule.get("approval_status") != "approved" or not scope_matches(rule.get("scope", {}), context):
            continue
        specificity = sum(1 for field in SCOPE_FIELDS if rule.get("scope", {}).get(field) not in {None, "*"})
        active.append((specificity, int(rule.get("priority", 0)), rule))
    if not active:
        return {"semantic_code": code, "status": "EXPIRED_PARAMETER" if expired_seen else "MISSING_PARAMETER"}
    top_key = max((specificity, priority) for specificity, priority, _ in active)
    top = [rule for specificity, priority, rule in active if (specificity, priority) == top_key]
    identities = {(rule.get("parameter_id"), rule.get("version"), rule.get("value"), rule.get("rule_expression")) for rule in top}
    if len(identities) != 1:
        return {"semantic_code": code, "status": "BLOCKED_AMBIGUOUS_RULE", "candidate_rule_ids": sorted(rule["parameter_id"] for rule in top)}
    selected = top[0]
    return {
        "semantic_code": code, "status": "resolved",
        "parameter_id": selected["parameter_id"], "parameter_version": selected["version"],
        "value": selected.get("value"), "rule_expression": selected.get("rule_expression"),
        "currency": selected.get("currency"), "unit": selected.get("unit"),
        "calculation_basis": selected["calculation_basis"],
        "source_id": selected["source"]["source_id"],
    }


def resolve(payload: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("context")
    rules = payload.get("rules")
    codes = payload.get("required_semantic_codes")
    if not isinstance(context, dict) or not isinstance(rules, list) or not isinstance(codes, list) or not codes:
        raise PPFCError("context, rules and non-empty required_semantic_codes are required")
    business_time = parse_time(payload.get("business_as_of_time"), "business_as_of_time")
    knowledge_time = parse_time(payload.get("knowledge_as_of_time"), "knowledge_as_of_time")
    results = [resolve_one(code, rules, context, business_time, knowledge_time) for code in sorted(set(codes))]
    unresolved = [item for item in results if item["status"] != "resolved"]
    snapshot = {
        "business_as_of_time": payload["business_as_of_time"],
        "knowledge_as_of_time": payload["knowledge_as_of_time"],
        "context": context,
        "resolved": [item for item in results if item["status"] == "resolved"],
        "unresolved": unresolved,
    }
    return {
        "status": "resolved" if not unresolved else "blocked",
        **snapshot,
        "snapshot_hash": canonical_hash(snapshot),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = resolve(json.loads(args.input.read_text()))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "resolved" else 2
    except (OSError, json.JSONDecodeError, PPFCError, KeyError, TypeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
