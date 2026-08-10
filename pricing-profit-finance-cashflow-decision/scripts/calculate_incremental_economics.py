#!/usr/bin/env python3
"""Calculate D06 incremental economics only from a qualified F01 receipt or an explicit noncausal scenario."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

from ppfc_common import PPFCError, dec, exact
from validate_ecae_financial_handoff import receipt_from


def _interval(value: object, field: str) -> dict[str, Decimal]:
    if not isinstance(value, dict) or set(value) != {"lower", "point", "upper"}:
        raise PPFCError(f"{field}: requires lower point upper")
    result = {key: dec(value[key], f"{field}.{key}") for key in ("lower", "point", "upper")}
    if not (result["lower"] <= result["point"] <= result["upper"]):
        raise PPFCError(f"{field}: interval must be ordered")
    return result


def _product_bounds(a: dict[str, Decimal], b: dict[str, Decimal]) -> tuple[Decimal, Decimal]:
    products = [a[left] * b[right] for left in ("lower", "upper") for right in ("lower", "upper")]
    return min(products), max(products)


def calculate(data: dict, *, migration: dict | None = None) -> dict:
    if "effect_estimate" in data or "effect_interval" in data or "incremental_contribution" in data:
        raise PPFCError("bare causal or legacy incremental fields are forbidden; use a qualified F01 receipt")
    mode = data.get("economics_mode", "incremental_causal")
    if mode not in {"incremental_causal", "noncausal_scenario"}:
        raise PPFCError("economics_mode invalid")
    volume = dec(data.get("eligible_volume"), "eligible_volume", nonnegative=True)
    if volume <= 0:
        raise PPFCError("eligible_volume must be positive")
    costs = {key: dec(data.get("costs", {}).get(key, "0"), f"costs.{key}", nonnegative=True) for key in ("implementation", "opportunity", "risk")}
    total_cost = sum(costs.values(), Decimal("0"))
    receipt = None
    if mode == "incremental_causal":
        try:
            receipt = receipt_from(data, migration=migration)
        except ValueError as exc:
            raise PPFCError(str(exc)) from exc
        if receipt is None or not receipt["incremental_economics_allowed"] or receipt["incremental_input_state"] != "qualified":
            return {
                "status": "inconclusive", "economics_mode": "incremental_causal", "incremental_input_state": "unknown",
                "causal_claim_allowed": False, "incremental_economics": None,
                "reasons": ["QUALIFIED_F01_RECEIPT_REQUIRED"], "business_owner_decision_required": True,
                "financial_decision_owner": "PPFC", "external_write": False,
            }
        effect = _interval(receipt["effect_interval"], "receipt.effect_interval")
        snapshot = receipt["economic_parameter_snapshot"]
        unit_value = _interval(snapshot["unit_contribution_interval"], "receipt.economic_parameter_snapshot.unit_contribution_interval")
        scenario_type = "causal_incremental"
        causal_allowed = True
        source = {"receipt_id": receipt["receipt_id"], "receipt_hash": receipt["receipt_hash"], "causal_result_ref": receipt["causal_result_ref"], "parameter_snapshot_id": snapshot["snapshot_id"], "parameter_snapshot_hash": snapshot["content_hash"]}
    else:
        label = data.get("noncausal_scenario_label")
        if not isinstance(label, str) or not label.strip():
            raise PPFCError("noncausal_scenario_label is required")
        if data.get("ecae_financial_receipt") is not None or data.get("ecae_handoff_context") is not None:
            raise PPFCError("noncausal scenario cannot carry an F01 receipt")
        effect = _interval(data.get("scenario_effect_interval"), "scenario_effect_interval")
        snapshot = data.get("scenario_economic_parameter_snapshot")
        if not isinstance(snapshot, dict):
            raise PPFCError("scenario_economic_parameter_snapshot is required")
        unit_value = _interval(snapshot.get("unit_contribution_interval"), "scenario_economic_parameter_snapshot.unit_contribution_interval")
        if not isinstance(snapshot.get("currency"), str) or not snapshot["currency"]:
            raise PPFCError("scenario_economic_parameter_snapshot.currency is required")
        scenario_type = "noncausal_scenario"
        causal_allowed = False
        source = {"scenario_label": label, "causal_receipt": None}
    gross_lower, gross_upper = _product_bounds(effect, unit_value)
    gross_lower *= volume
    gross_point = effect["point"] * unit_value["point"] * volume
    gross_upper *= volume
    net = {"lower": gross_lower - total_cost, "point": gross_point - total_cost, "upper": gross_upper - total_cost}
    status = "value_supported" if net["lower"] > 0 else "value_not_supported" if net["upper"] < 0 else "downside_risk" if net["point"] < 0 else "precision_insufficient"
    return {
        "status": "calculated", "economic_status": status, "economics_mode": mode, "scenario_type": scenario_type,
        "incremental_input_state": "qualified" if causal_allowed else "not_applicable_noncausal_scenario",
        "causal_claim_allowed": causal_allowed, "currency": snapshot["currency"], "eligible_volume": exact(volume),
        "effect_interval": {key: exact(value) for key, value in effect.items()},
        "unit_contribution_interval": {key: exact(value) for key, value in unit_value.items()},
        "gross_value_interval": {"lower": exact(gross_lower), "point": exact(gross_point), "upper": exact(gross_upper)},
        "costs": {**{key: exact(value) for key, value in costs.items()}, "total": exact(total_cost)},
        "net_value_interval": {key: exact(value) for key, value in net.items()},
        "marketing_roi_incremental": exact(net["point"] / total_cost) if causal_allowed and total_cost > 0 else None,
        "source_lineage": source, "business_owner_decision_required": True, "financial_decision_owner": "PPFC",
        "automatic_price_or_cash_action_allowed": False, "external_write": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = calculate(json.loads(args.input.read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["status"] == "calculated" else 2
    except (OSError, json.JSONDecodeError, PPFCError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc), "causal_claim_allowed": False, "external_write": False}, ensure_ascii=False, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
