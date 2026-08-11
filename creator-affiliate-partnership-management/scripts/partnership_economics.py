#!/usr/bin/env python3
"""CAPM C01/C02/C03/C08/C12 economics with cost de-duplication."""
from __future__ import annotations
import argparse
from capm_common import emit, load_json, require_number, sha256_json
from validate_ecae_handoff import qualified_receipt_from


def unique_costs(costs: list[dict]) -> tuple[float, list[str]]:
    seen: set[str] = set()
    total = 0.0
    keys = []
    for item in costs:
        key = str(item.get("cost_id", "")).strip()
        if not key:
            raise ValueError("cost_id is required")
        if key in seen:
            raise ValueError(f"duplicate cost_id: {key}")
        seen.add(key)
        keys.append(key)
        total += require_number(item.get("amount"), f"cost[{key}].amount")
    return total, keys


def commission_ceiling(data: dict) -> dict:
    revenue = require_number(data.get("mature_net_revenue"), "mature_net_revenue")
    base = require_number(data.get("commission_base"), "commission_base", minimum=1e-12)
    target = require_number(data.get("target_profit"), "target_profit")
    costs, ids = unique_costs(data.get("non_commission_costs", []))
    available = revenue - costs - target
    rate = max(0.0, available / base)
    return {"status": "blocked" if available <= 0 else "validated", "max_commission_rate": rate,
            "available_for_commission": available, "non_commission_cost": costs, "cost_ids": ids}


def fixed_fee_ceiling(data: dict) -> dict:
    revenue = require_number(data.get("mature_revenue"), "mature_revenue")
    target = require_number(data.get("target_profit"), "target_profit")
    costs, ids = unique_costs(data.get("non_fixed_costs", []))
    ceiling = revenue - costs - target
    return {"status": "blocked" if ceiling <= 0 else "validated", "max_fixed_fee": max(0.0, ceiling),
            "raw_ceiling": ceiling, "non_fixed_cost": costs, "cost_ids": ids}


def partnership_return(data: dict) -> dict:
    investment = require_number(data.get("controllable_investment"), "controllable_investment", minimum=1e-12)
    contribution = require_number(data.get("contribution"), "contribution", minimum=None)
    legacy_causal = data.get("causal_evidence_level", "C0")
    receipt = qualified_receipt_from(data)
    incremental_qualified = bool(receipt and receipt["incremental_claim_allowed"])
    metric = "incremental_return" if incremental_qualified else "attributed_return"
    return {"status": "validated" if incremental_qualified else "inconclusive",
            "metric": metric, "value": (contribution - investment) / investment,
            "forbidden_metric": None if incremental_qualified else "incremental_return",
            "legacy_causal_label": legacy_causal,
            "legacy_label_non_equivalent": legacy_causal in {"C2", "C3"},
            "ecae_consumer_receipt": receipt}


def program_profit(data: dict) -> dict:
    low = require_number(data.get("incremental_contribution_low"), "incremental_contribution_low", minimum=None)
    mid = require_number(data.get("incremental_contribution_mid"), "incremental_contribution_mid", minimum=None)
    high = require_number(data.get("incremental_contribution_high"), "incremental_contribution_high", minimum=None)
    if not low <= mid <= high:
        raise ValueError("incremental contribution must satisfy low <= mid <= high")
    costs, ids = unique_costs(data.get("program_costs", []))
    profits = [low - costs, mid - costs, high - costs]
    cash_events = data.get("cash_events", [])
    if not isinstance(cash_events, list): raise ValueError("cash_events must be an array")
    balance = require_number(data.get("opening_cash", 0), "opening_cash", minimum=None)
    trough = balance
    ordered_events = []
    for index, event in enumerate(cash_events):
        if not event.get("event_id") or not event.get("at"): raise ValueError(f"cash_events[{index}] missing event_id or at")
        amount = require_number(event.get("amount"), f"cash_events[{index}].amount", minimum=None)
        ordered_events.append((event["at"], event["event_id"], amount))
    if ordered_events != sorted(ordered_events): raise ValueError("cash_events must be ordered by at and event_id")
    for _, _, amount in ordered_events:
        balance += amount; trough = min(trough, balance)
    status = "blocked" if profits[0] < 0 or trough < 0 else "validated"
    receipt = qualified_receipt_from(data)
    incremental_qualified = bool(receipt and receipt["incremental_claim_allowed"])
    return {"status": status, "profit_low": profits[0], "profit_mid": profits[1], "profit_high": profits[2],
            "program_cost": costs, "cost_ids": ids, "cash_trough": trough, "ending_cash": balance,
            "partner_exit_rule": "marginal_value_and_obligations_review_required",
            "evidence_semantics": "qualified_incremental" if incremental_qualified else "scenario_not_incremental",
            "forbidden_claim": None if incremental_qualified else "incremental_program_profit",
            "ecae_consumer_receipt": receipt}


ACTIONS = {"commission_ceiling": commission_ceiling, "fixed_fee_ceiling": fixed_fee_ceiling,
           "partnership_return": partnership_return, "program_profit": program_profit}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=ACTIONS)
    parser.add_argument("input", nargs="?")
    args = parser.parse_args()
    data = load_json(args.input)
    result = ACTIONS[args.action](data)
    result.update({"runtime_version": "CAPM-2026.07", "input_hash": sha256_json(data)})
    emit(result)


if __name__ == "__main__":
    main()
