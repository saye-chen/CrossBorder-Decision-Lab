#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from ppfc_common import PPFCError, dec, exact, rate


BASES = {"gross_revenue", "tax_exclusive_revenue", "recognized_net_revenue"}


def fee_amount(fee: dict[str, Any], bases: dict[str, Decimal], index: int) -> Decimal:
    basis_name = fee.get("basis")
    if basis_name not in BASES:
        raise PPFCError(f"fees[{index}].basis invalid")
    basis = bases[basis_name]
    kind = fee.get("type")
    fixed = dec(fee.get("fixed", "0"), f"fees[{index}].fixed", nonnegative=True)
    fee_rate = rate(fee.get("rate", "0"), f"fees[{index}].rate")
    if kind == "amount":
        amount = fixed
    elif kind == "rate":
        amount = basis * fee_rate
    elif kind == "fixed_plus_rate":
        amount = fixed + basis * fee_rate
    else:
        raise PPFCError(f"fees[{index}].type invalid")
    minimum = dec(fee.get("minimum", "0"), f"fees[{index}].minimum", nonnegative=True)
    amount = max(amount, minimum)
    if fee.get("maximum") is not None:
        amount = min(amount, dec(fee["maximum"], f"fees[{index}].maximum", nonnegative=True))
    return amount


def calculate_scenario(payload: dict[str, Any], price_override: Decimal | None = None) -> dict[str, Any]:
    price = price_override if price_override is not None else dec(payload.get("price"), "price", nonnegative=True)
    quantity = dec(payload.get("quantity", "1"), "quantity", nonnegative=True)
    if price <= 0 or quantity <= 0:
        raise PPFCError("price and quantity must be positive")
    gross = price * quantity
    discount = gross * rate(payload.get("discount_rate", "0"), "discount_rate")
    tax = (gross - discount) * rate(payload.get("pass_through_tax_rate", "0"), "pass_through_tax_rate")
    refund = (gross - discount - tax) * rate(payload.get("refund_rate", "0"), "refund_rate")
    other_reversals = dec(payload.get("other_reversals", "0"), "other_reversals", nonnegative=True)
    tax_exclusive = gross - discount - tax
    net = tax_exclusive - refund - other_reversals
    bases = {"gross_revenue": gross, "tax_exclusive_revenue": tax_exclusive, "recognized_net_revenue": net}
    fees: dict[str, Decimal] = {}
    seen: set[str] = set()
    for index, fee in enumerate(payload.get("fees", [])):
        fee_id = fee.get("fee_id")
        if not fee_id or fee_id in seen:
            raise PPFCError("fee_id must be non-empty and unique")
        seen.add(fee_id)
        fees[fee_id] = fee_amount(fee, bases, index)
    product = dec(payload.get("product_cogs"), "product_cogs", nonnegative=True) * quantity
    fulfillment = dec(payload.get("fulfillment_cost"), "fulfillment_cost", nonnegative=True) * quantity
    expected_returns = dec(payload.get("expected_return_cost", "0"), "expected_return_cost", nonnegative=True) * quantity
    marketing = dec(payload.get("variable_marketing_cost", "0"), "variable_marketing_cost", nonnegative=True)
    service = dec(payload.get("variable_service_cost", "0"), "variable_service_cost", nonnegative=True)
    avoidable_period = dec(payload.get("avoidable_period_cost", "0"), "avoidable_period_cost", nonnegative=True)
    allocated_operating = dec(payload.get("allocated_operating_expense", "0"), "allocated_operating_expense", nonnegative=True)
    ad_spend = dec(payload.get("ad_spend", "0"), "ad_spend", nonnegative=True)
    platform_payment = sum(fees.values(), Decimal("0"))
    gross_profit = net - product
    contribution1 = gross_profit - fulfillment - platform_payment - expected_returns
    contribution2 = contribution1 - marketing - service - ad_spend
    contribution3 = contribution2 - avoidable_period
    operating_profit = contribution3 - allocated_operating
    pre_ad = contribution2 + ad_spend
    required_profit = dec(payload.get("required_profit", "0"), "required_profit", nonnegative=True)
    risk_buffer = dec(payload.get("risk_buffer", "0"), "risk_buffer", nonnegative=True)
    allowable_ad = pre_ad - required_profit - risk_buffer
    metrics: dict[str, str | None] = {
        "PROFIT_MARGIN": exact(operating_profit / net) if net > 0 else None,
        "PROFIT_ON_COST": exact(operating_profit / (net - operating_profit)) if net - operating_profit > 0 else None,
        "ACOS_ATTR_NET": exact(ad_spend / net) if net > 0 else None,
        "ROAS_ATTR_NET": exact(net / ad_spend) if ad_spend > 0 else None,
        "BREAK_EVEN_ACOS_NET": exact(pre_ad / net) if net > 0 and pre_ad > 0 else None,
        "BREAK_EVEN_ROAS_NET": exact(net / pre_ad) if pre_ad > 0 else None,
        "TARGET_ROAS_NET": exact(net / allowable_ad) if allowable_ad > 0 else None,
    }
    status = "calculated" if pre_ad > 0 else "BLOCKED_NO_PRE_AD_CONTRIBUTION"
    return {
        "status": status, "currency": payload.get("currency"), "price": exact(price), "quantity": exact(quantity),
        "revenue_bridge": {
            "gross_revenue": exact(gross), "discounts": exact(discount), "pass_through_tax": exact(tax),
            "refunds": exact(refund), "other_reversals": exact(other_reversals), "recognized_net_revenue": exact(net),
        },
        "fees": {key: exact(value) for key, value in fees.items()},
        "profit_bridge": {
            "gross_profit": exact(gross_profit), "contribution_1": exact(contribution1),
            "contribution_2": exact(contribution2), "contribution_3": exact(contribution3),
            "operating_profit": exact(operating_profit), "pre_ad_contribution": exact(pre_ad),
            "allowable_ad_spend": exact(max(Decimal("0"), allowable_ad)),
        },
        "metrics": metrics,
    }


def solve_target(payload: dict[str, Any]) -> dict[str, Any]:
    target = rate(payload.get("target_profit_margin"), "target_profit_margin")
    low = dec(payload.get("search_low"), "search_low", nonnegative=True)
    high = dec(payload.get("search_high"), "search_high", nonnegative=True)
    if low <= 0 or high <= low:
        raise PPFCError("search bounds invalid")
    iterations = int(payload.get("iterations", 100))
    for _ in range(iterations):
        mid = (low + high) / 2
        result = calculate_scenario(payload, mid)
        margin = result["metrics"]["PROFIT_MARGIN"]
        if margin is not None and Decimal(margin) >= target:
            high = mid
        else:
            low = mid
    result = calculate_scenario(payload, high)
    if result["metrics"]["PROFIT_MARGIN"] is None or Decimal(result["metrics"]["PROFIT_MARGIN"]) < target:
        raise PPFCError("target margin not achievable in search bounds")
    result["solved_target_profit_margin"] = exact(target)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text())
        result = solve_target(payload) if "target_profit_margin" in payload else calculate_scenario(payload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "calculated" else 2
    except (OSError, json.JSONDecodeError, PPFCError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
