#!/usr/bin/env python3
"""PPFC-owned financial boundary calculations fed by business-domain facts."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from ppfc_common import PPFCError, dec, exact


LANDED_KEYS = (
    "purchase_price", "tooling_amortization", "product_packaging", "origin_handling",
    "export_clearance", "main_haul", "insurance", "import_duty", "nonrecoverable_tax",
    "brokerage", "inbound_last_mile", "receiving_putaway", "expected_damage",
    "expected_shortage", "financing_until_available",
)
FULFILLMENT_KEYS = (
    "storage_allocation", "pick_pack", "order_packaging", "carrier_base", "surcharges",
    "signature_insurance", "failed_delivery", "redelivery", "outbound_loss", "return_provision",
)
RISK_KEYS = (
    "holding", "stockout_loss", "obsolescence", "reverse_loss",
    "expedite_transfer", "congestion", "service_failure", "switching_recovery",
)


def logistics_financial_boundary(data: dict[str, Any]) -> dict[str, Any]:
    landed = sum((dec(data.get(key, "0"), key, nonnegative=True) for key in LANDED_KEYS), Decimal("0"))
    fulfillment = sum((dec(data.get(key, "0"), key, nonnegative=True) for key in FULFILLMENT_KEYS), Decimal("0"))
    relevant = landed + fulfillment + sum(
        (dec(data.get(key, "0"), key, nonnegative=True) for key in RISK_KEYS),
        Decimal("0"),
    )
    result = {
        "landed_cost_per_unit": exact(landed),
        "fulfillment_cost_per_order": exact(fulfillment),
        "total_relevant_cost": exact(relevant),
    }
    if "selling_price" in data:
        contribution = dec(data["selling_price"], "selling_price", nonnegative=True) - relevant
        minimum = dec(data.get("minimum_contribution", "0"), "minimum_contribution")
        result.update({
            "contribution": exact(contribution),
            "minimum_contribution": exact(minimum),
            "financial_status": "validated" if contribution >= minimum else "blocked",
        })
    return result


def partnership_commission_boundary(data: dict[str, Any]) -> dict[str, Any]:
    revenue = dec(data["mature_net_revenue"], "mature_net_revenue", nonnegative=True)
    commission_base = dec(data["commission_base"], "commission_base", nonnegative=True)
    if commission_base == 0:
        raise PPFCError("COMMISSION_BASE_ZERO")
    target = dec(data["target_profit"], "target_profit")
    seen: set[str] = set()
    costs = Decimal("0")
    for item in data.get("non_commission_costs", []):
        cost_id = str(item.get("cost_id", "")).strip()
        if not cost_id or cost_id in seen:
            raise PPFCError("DUPLICATE_OR_MISSING_COST_ID")
        seen.add(cost_id)
        costs += dec(item["amount"], f"cost:{cost_id}", nonnegative=True)
    available = revenue - costs - target
    return {
        "status": "blocked" if available <= 0 else "validated",
        "max_commission_rate": exact(max(available / commission_base, Decimal("0"))),
        "available_for_commission": exact(available),
        "non_commission_cost": exact(costs),
    }


def promotion_financial_boundary(data: dict[str, Any]) -> dict[str, Any]:
    eligible = dec(data["eligible"], "eligible", nonnegative=True)
    redeemed = dec(data["redeemed_orders"], "redeemed_orders", nonnegative=True)
    incremental = dec(data["incremental_orders"], "incremental_orders", nonnegative=True)
    if redeemed > eligible or incremental > redeemed:
        raise PPFCError("PROMOTION_ORDER_COUNTS_INVALID")
    per_redeemed = sum((
        dec(data["merchant_discount_per_redeemed"], "merchant_discount_per_redeemed", nonnegative=True),
        dec(data["gift_cost_per_redeemed"], "gift_cost_per_redeemed", nonnegative=True),
        dec(data["shipping_subsidy_per_redeemed"], "shipping_subsidy_per_redeemed", nonnegative=True),
    ), Decimal("0"))
    variable = redeemed * per_redeemed + sum((
        dec(data["guarantee_cost"], "guarantee_cost", nonnegative=True),
        dec(data["fraud_loss"], "fraud_loss", nonnegative=True),
        dec(data["service_cost"], "service_cost", nonnegative=True),
    ), Decimal("0"))
    losses = sum((
        dec(data["pull_forward_loss"], "pull_forward_loss", nonnegative=True),
        dec(data["cannibalization_loss"], "cannibalization_loss", nonnegative=True),
        dec(data["fixed_cost"], "fixed_cost", nonnegative=True),
    ), Decimal("0"))
    total = variable + losses
    cm = dec(data["incremental_cm_per_order"], "incremental_cm_per_order")
    contribution = incremental * cm - total
    break_even = None if redeemed == 0 or cm <= 0 else total / (redeemed * cm)
    return {
        "non_incremental_redeemed_orders": exact(redeemed - incremental),
        "total_offer_burden": exact(total),
        "incremental_offer_contribution": exact(contribution),
        "break_even_incremental_order_rate": exact(break_even) if break_even is not None else None,
        "financial_status": "validated" if contribution >= 0 and cm > 0 else "blocked",
    }


def recoverable_contribution_boundary(data: dict[str, Any]) -> dict[str, Any]:
    visits = dec(data["qualified_visits"], "qualified_visits", nonnegative=True)
    gap = dec(data["conversion_gap"], "conversion_gap", nonnegative=True)
    share = dec(data["recoverable_share"], "recoverable_share", nonnegative=True)
    if gap > 1 or share > 1:
        raise PPFCError("RATE_EXCEEDS_ONE")
    margin = data["mature_contribution_per_order"]
    low = dec(margin["low"], "margin.low")
    high = dec(margin["high"], "margin.high")
    if low > high:
        raise PPFCError("MARGIN_RANGE_REVERSED")
    orders = visits * gap * share
    cost = dec(data.get("implementation_cost", "0"), "implementation_cost", nonnegative=True)
    return {
        "recoverable_orders": exact(orders),
        "contribution_range": [exact(orders * low - cost), exact(orders * high - cost)],
        "precision": "scenario_range",
    }
