#!/usr/bin/env python3
"""Evaluate mixed shelf, ad, creator, video and live batch economics exactly."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from ppfc_common import PPFCError, canonical_hash, dec, exact, parse_time


def require(condition: Any, message: str) -> None:
    if not condition: raise PPFCError(message)


def sample_target(quantity: int, policy: dict[str, Any]) -> int:
    rate = dec(policy["rate"], "sample_policy.rate", nonnegative=True)
    require(rate <= 1, "sample rate must not exceed 1")
    rounding = {"floor": ROUND_FLOOR, "ceil": ROUND_CEILING, "half_up": ROUND_HALF_UP}[policy["rounding"]]
    target = int((Decimal(quantity) * rate).to_integral_value(rounding=rounding))
    require(policy["minimum"] <= policy["maximum"], "sample minimum exceeds maximum")
    return min(policy["maximum"], max(policy["minimum"], target))


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    batch = payload["batch"]; initial = batch["initial_quantity"]
    partitions = ["sample", "test", "initial_defect", "after_sales_reserve", "safety_stock", "sellable_open"]
    require(sum(batch[key] for key in partitions) == initial, "BATCH_CAPACITY_NOT_CONSERVED")
    target = sample_target(initial, payload["sample_policy"])
    require(batch["sample"] == target, "SAMPLE_ALLOCATION_DOES_NOT_MATCH_POLICY")
    policy = payload["sample_policy"]
    require(policy["posted"] <= batch["sample"], "posted samples exceed allocation")
    require(policy["rights_verified"] <= policy["posted"], "rights verified exceeds posted")

    orders = payload["orders"]; order_ids = [item.get("order_id") for item in orders]
    require(all(order_ids) and len(set(order_ids)) == len(order_ids), "DUPLICATE_OR_MISSING_ORDER")
    unique_net_revenue = Decimal("0"); fulfilled_units = 0; refund_total = Decimal("0")
    order_revenue: dict[str, Decimal] = {}
    for order in orders:
        gross = dec(order["gross_revenue"], "order.gross_revenue", nonnegative=True)
        refund = dec(order.get("refund", "0"), "order.refund", nonnegative=True)
        require(refund <= gross, "refund exceeds gross revenue")
        net = gross - refund if order.get("paid", True) else Decimal("0")
        units = int(order.get("fulfilled_units", 0)) if order.get("paid", True) else 0
        require(units >= 0, "fulfilled units negative")
        unique_net_revenue += net; refund_total += refund; fulfilled_units += units
        order_revenue[order["order_id"]] = net
    require(fulfilled_units <= batch["sellable_open"], "FULFILLMENT_EXCEEDS_ATP")

    raw_claimed = Decimal("0"); weights: dict[str, Decimal] = defaultdict(Decimal)
    for claim in payload["channel_claims"]:
        order_id = claim["order_id"]; require(order_id in order_revenue, "claim references unknown order")
        raw_claimed += dec(claim["claimed_revenue"], "claim.claimed_revenue", nonnegative=True)
        weight = dec(claim.get("attribution_weight", "0"), "claim.attribution_weight", nonnegative=True)
        require(weight <= 1, "attribution weight exceeds 1"); weights[order_id] += weight
    for order_id, total in weights.items():
        require(total == 1, f"ATTRIBUTION_WEIGHTS_NOT_ONE:{order_id}")
    allocated_attributed = sum((order_revenue[oid] * weight for oid, weight in weights.items()), Decimal("0"))
    require(allocated_attributed <= unique_net_revenue, "attributed revenue exceeds unique revenue")

    cost_by_key: dict[str, tuple[str, Decimal]] = {}; cost_by_category: dict[str, Decimal] = defaultdict(Decimal)
    for cost in payload["costs"]:
        key = cost["deduplication_key"]; amount = dec(cost["amount"], "cost.amount", nonnegative=True)
        signature = (cost["category"], amount)
        if key in cost_by_key:
            require(cost_by_key[key] == signature, f"CONFLICTING_DUPLICATE_COST:{key}")
            continue
        cost_by_key[key] = signature; cost_by_category[cost["category"]] += amount
    total_cost = sum(cost_by_category.values(), Decimal("0"))
    sample_categories = {"sample_landed", "sample_shipping", "creator_fee", "content_production", "rights", "paid_amplification", "sample_management", "sample_loss"}
    sample_investment = sum((amount for category, amount in cost_by_category.items() if category in sample_categories), Decimal("0")) - cost_by_category.get("sample_recovery", Decimal("0"))
    economic_profit = unique_net_revenue + dec(payload["ending_inventory_nrv"], "ending_inventory_nrv") - total_cost

    cash_balance = Decimal("0"); minimum_cash = Decimal("0"); total_cash = Decimal("0"); recovery_time = None
    events = sorted(payload["cash_events"], key=lambda item: parse_time(item["occurred_at"], "cash.occurred_at"))
    seen_events = set()
    for event in events:
        require(event["event_id"] not in seen_events, "duplicate cash event"); seen_events.add(event["event_id"])
        amount = dec(event["amount"], "cash.amount")
        cash_balance += amount; total_cash += amount; minimum_cash = min(minimum_cash, cash_balance)
        if minimum_cash < 0 and cash_balance >= 0 and recovery_time is None: recovery_time = event["occurred_at"]
    peak_funding = -minimum_cash
    cash_limit = dec(payload["cash_limit"], "cash_limit", nonnegative=True)
    blockers = []
    if peak_funding > cash_limit: blockers.append("CASH_LIMIT_EXCEEDED")
    if policy["posted"] == 0 and cost_by_category.get("paid_amplification", Decimal("0")) > 0:
        blockers.append("NO_POSTED_CONTENT_FOR_AMPLIFICATION")
    if policy["posted"] > policy["rights_verified"] and cost_by_category.get("paid_amplification", Decimal("0")) > 0:
        blockers.append("CONTENT_RIGHTS_NOT_VERIFIED")
    if payload["incrementality_status"] in {"not_claimed", "attributed_only"}:
        incremental_contribution = None
    else:
        incremental_contribution = exact(economic_profit)
    return {
        "status": "blocked" if blockers else "validated",
        "sample_target": target, "sellable_open": batch["sellable_open"], "unique_orders": len(orders),
        "fulfilled_units": fulfilled_units, "unique_net_revenue": exact(unique_net_revenue),
        "raw_claimed_revenue": exact(raw_claimed), "allocated_attributed_revenue": exact(allocated_attributed),
        "refund_total": exact(refund_total), "deduplicated_total_cost": exact(total_cost),
        "sample_investment": exact(sample_investment), "ending_inventory_nrv": payload["ending_inventory_nrv"],
        "batch_economic_profit": exact(economic_profit), "batch_cash_result": exact(total_cash),
        "peak_funding_required": exact(peak_funding), "cash_recovery_time": recovery_time,
        "incremental_contribution": incremental_contribution, "blockers": blockers,
        "input_hash": "sha256:" + canonical_hash(payload),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, KeyError, PPFCError, ValueError) as exc:
        print(f"PPFC_MIXED_BATCH=BLOCKED: {exc}", file=sys.stderr); return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
