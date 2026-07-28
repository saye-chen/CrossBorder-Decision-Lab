#!/usr/bin/env python3
"""Deterministic PPFC primitives for business-model and stress evaluations."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from ppfc_common import PPFCError, dec, exact


def marginal_scale(stages: list[dict[str, Any]]) -> dict[str, Any]:
    if len(stages) < 2:
        raise PPFCError("MARGINAL_STAGE_REQUIRED")
    ordered = sorted(stages, key=lambda row: dec(row["spend"], "spend", nonnegative=True))
    results = []
    for previous, current in zip(ordered, ordered[1:]):
        delta_spend = dec(current["spend"], "spend") - dec(previous["spend"], "spend")
        if delta_spend <= 0:
            raise PPFCError("SPEND_MUST_STRICTLY_INCREASE")
        delta_profit = dec(current["contribution"], "contribution") - dec(previous["contribution"], "contribution")
        results.append({
            "from": previous["spend"],
            "to": current["spend"],
            "marginal_contribution": exact(delta_profit),
            "marginal_return": exact(delta_profit / delta_spend),
        })
    blocked = any(dec(row["marginal_contribution"], "marginal_contribution") < 0 for row in results)
    return {"status": "blocked_negative_marginal" if blocked else "validated", "steps": results}


def causal_ceiling(evidence_level: str, attributed_value: Any) -> dict[str, Any]:
    value = dec(attributed_value, "attributed_value", nonnegative=True)
    causal = evidence_level in {"E6", "E7"}
    return {
        "status": "validated" if causal else "proposed",
        "attributed_value": exact(value),
        "incremental_value": exact(value) if causal else None,
    }


def net_recovery_value(expected_proceeds: Any, disposal_cost: Any, holding_cost: Any = "0") -> str:
    return exact(
        dec(expected_proceeds, "expected_proceeds", nonnegative=True)
        - dec(disposal_cost, "disposal_cost", nonnegative=True)
        - dec(holding_cost, "holding_cost", nonnegative=True)
    )


def b2b_terms(
    revenue: Any,
    product_and_service_cost: Any,
    bad_debt_rate: Any,
    financing_cost: Any,
) -> dict[str, Any]:
    gross = dec(revenue, "revenue", nonnegative=True)
    bad_debt = gross * dec(bad_debt_rate, "bad_debt_rate", nonnegative=True)
    contribution = (
        gross
        - dec(product_and_service_cost, "product_and_service_cost", nonnegative=True)
        - bad_debt
        - dec(financing_cost, "financing_cost", nonnegative=True)
    )
    return {"bad_debt": exact(bad_debt), "contribution": exact(contribution)}


def subscription_economics(
    first_order_contribution: Any,
    recurring_contribution: Any,
    retention_rate: Any,
    periods: int,
    acquisition_cost: Any,
) -> dict[str, Any]:
    if periods < 1:
        raise PPFCError("PERIODS_MUST_BE_POSITIVE")
    retention = dec(retention_rate, "retention_rate", nonnegative=True)
    if retention > 1:
        raise PPFCError("RETENTION_RATE_EXCEEDS_ONE")
    lifetime = dec(first_order_contribution, "first_order_contribution")
    recurring = dec(recurring_contribution, "recurring_contribution")
    survival = Decimal("1")
    for _ in range(1, periods):
        survival *= retention
        lifetime += recurring * survival
    net = lifetime - dec(acquisition_cost, "acquisition_cost", nonnegative=True)
    return {"contribution_clv": exact(lifetime), "net_after_cac": exact(net)}


def bundle_incremental(
    bundle_revenue: Any,
    bundle_cost: Any,
    displaced_standalone_contribution: Any,
    incremental_evidence: bool,
) -> dict[str, Any]:
    contribution = (
        dec(bundle_revenue, "bundle_revenue", nonnegative=True)
        - dec(bundle_cost, "bundle_cost", nonnegative=True)
        - dec(displaced_standalone_contribution, "displaced_standalone_contribution", nonnegative=True)
    )
    return {
        "status": "validated" if incremental_evidence else "proposed",
        "incremental_contribution": exact(contribution) if incremental_evidence else None,
        "scenario_contribution": exact(contribution),
    }


def preorder_gate(
    collected_cash: Any,
    delivery_cost: Any,
    refund_liability: Any | None,
    delivery_evidence: bool,
) -> dict[str, Any]:
    if refund_liability is None:
        return {"status": "blocked", "reason": "REFUND_LIABILITY_MISSING"}
    net_cash = (
        dec(collected_cash, "collected_cash", nonnegative=True)
        - dec(delivery_cost, "delivery_cost", nonnegative=True)
        - dec(refund_liability, "refund_liability", nonnegative=True)
    )
    return {
        "status": "validated" if delivery_evidence and net_cash >= 0 else "blocked",
        "net_cash_after_liability": exact(net_cash),
    }


def cac_boundaries(
    first_order_contribution: Any,
    mature_contribution_clv: Any,
    clv_evidence_level: str,
) -> dict[str, Any]:
    first = dec(first_order_contribution, "first_order_contribution")
    mature = dec(mature_contribution_clv, "mature_contribution_clv")
    return {
        "first_order_cac_ceiling": exact(max(first, Decimal("0"))),
        "lifetime_cac_ceiling": exact(max(mature, Decimal("0"))) if clv_evidence_level in {"E6", "E7"} else None,
        "lifetime_status": "validated" if clv_evidence_level in {"E6", "E7"} else "hypothesis_only",
    }


def joint_stress(
    revenue: Any,
    cvr_multiplier: Any,
    refund_rate: Any,
    fee_rate: Any,
    costs: Any,
    cash_limit: Any,
) -> dict[str, Any]:
    stressed_gross = dec(revenue, "revenue", nonnegative=True) * dec(cvr_multiplier, "cvr_multiplier", nonnegative=True)
    net = stressed_gross * (Decimal("1") - dec(refund_rate, "refund_rate", nonnegative=True))
    fees = net * dec(fee_rate, "fee_rate", nonnegative=True)
    contribution = net - fees - dec(costs, "costs", nonnegative=True)
    peak_funding = max(-contribution, Decimal("0"))
    blocked = contribution < 0 or peak_funding > dec(cash_limit, "cash_limit", nonnegative=True)
    return {
        "status": "blocked" if blocked else "stressed",
        "net_revenue": exact(net),
        "fees": exact(fees),
        "contribution": exact(contribution),
        "peak_funding": exact(peak_funding),
    }


def spreadsheet_value(value: Any) -> Decimal:
    if isinstance(value, str) and value in {"#NAME?", "#DIV/0!", "#N/A", "#VALUE!"}:
        raise PPFCError(f"SPREADSHEET_ERROR:{value}")
    return dec(value, "spreadsheet_value")
