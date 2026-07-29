#!/usr/bin/env python3
"""Calculate ERDG E0-E8 economic layers using authoritative decimal arithmetic."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from erdg_common import decimal_string, decimal_value, quantize_money

DEDUCTIONS = {
    "E1": ("discounts", "cancellations", "refunds", "taxes_and_withholding"),
    "E2": ("product_cost", "packaging_cost", "production_cost"),
    "E3": ("first_mile_cost", "freight_cost", "warehousing_cost", "fulfillment_cost", "last_mile_cost", "return_logistics_cost"),
    "E4": ("platform_fees", "payment_fees", "channel_fees", "transaction_fees"),
    "E5": ("advertising_cost", "creator_cost", "marketing_cost", "incremental_acquisition_cost"),
    "E6": ("customer_service_cost", "after_sales_cost", "compensation_cost"),
    "E7": ("expected_risk_loss",),
}


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    currency = payload.get("currency")
    if not isinstance(currency, str) or len(currency) != 3 or currency.upper() != currency:
        raise ValueError("currency must be a three-letter uppercase code")
    amounts = payload.get("amounts")
    if not isinstance(amounts, dict):
        raise ValueError("amounts must be an object")
    if "gross_sales" not in amounts:
        raise ValueError("amounts.gross_sales is required")
    unknown = set(amounts) - {"gross_sales", "operating_cash_adjustment"} - {name for fields in DEDUCTIONS.values() for name in fields}
    if unknown:
        raise ValueError(f"unknown economic amounts: {sorted(unknown)}")
    parsed = {name: decimal_value(value, f"amounts.{name}") for name, value in amounts.items()}
    e0 = parsed["gross_sales"]
    layers: dict[str, Decimal] = {"E0": e0}
    prior = e0
    for layer, fields in DEDUCTIONS.items():
        deduction = sum((parsed.get(field, Decimal("0")) for field in fields), Decimal("0"))
        prior -= deduction
        layers[layer] = prior
    e8 = layers["E7"] + parsed.get("operating_cash_adjustment", Decimal("0"))
    if "operating_cash_adjustment" in parsed:
        bridge = payload.get("cash_bridge")
        if not isinstance(bridge, dict) or not all(bridge.get(field) for field in ("cash_flow_calculation_id", "basis", "evidence_ref")):
            raise ValueError("operating_cash_adjustment requires a traceable cash_bridge")
    layers["E8"] = e8
    scale = payload.get("scale", 2)
    if not isinstance(scale, int):
        raise ValueError("scale must be an integer")
    return {
        "contract": "ERDG-CONTRACT-2026.07",
        "currency": currency,
        "tax_basis": payload.get("tax_basis"),
        "layers_exact": {key: decimal_string(value) for key, value in layers.items()},
        "layers_display": {key: quantize_money(value, scale) for key, value in layers.items()},
        "scale": scale,
        "average_marginal_separated": bool(payload.get("economic_mode") in {"average", "marginal"}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(calculate(payload), ensure_ascii=False, indent=2))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
