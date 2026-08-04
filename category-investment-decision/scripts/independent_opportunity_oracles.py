#!/usr/bin/env python3
"""Independent OSL-v1 calculations. Deliberately does not import main signal models."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Any


class OracleError(ValueError):
    pass


def d(value: Any) -> Decimal:
    if value is None:
        raise OracleError("unknown numeric input")
    result = Decimal(str(value))
    if not result.is_finite():
        raise OracleError("non-finite numeric input")
    return result


def breakout(data: dict[str, Any], c: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    weekly = data.get("weekly_sales")
    if not weekly or any(value is None for value in weekly): return "inconclusive", {}
    if data.get("parent_first_seen") is None or data.get("child_first_seen") is None: return "inconclusive", {}
    if data.get("parent_age_days", 0) > c["max_parent_age_days"]: return "rejected", {}
    persistence = Decimal(sum(d(value) >= d(c["weekly_sales_floor"]) for value in weekly)) / Decimal(len(weekly))
    total = sum((d(value) for value in weekly), Decimal(0))
    contamination = d(data.get("promotion_sales", 0)) / total if total > 0 else Decimal(1)
    metrics = {"breakout_persistence": str(persistence), "promotion_contamination": str(contamination), "weeks": len(weekly)}
    if data.get("review_inheritance") or data.get("variant_merge_event") or contamination > d(c["max_promotion_contamination"]): return "rejected", metrics
    return ("candidate" if persistence >= d(c["min_persistence"]) else "rejected"), metrics


def keyword(data: dict[str, Any], c: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    values = data.get("trend")
    if not values or len(values) < c["min_periods"] or any(value is None for value in values): return "inconclusive", {}
    if data.get("brand_term") or data.get("purchase_intent") not in {"high", "medium"}: return "rejected", {}
    concentration = d(data.get("purchase_concentration"))
    if not 0 <= concentration <= 1: raise OracleError("ratio scale")
    growth = (d(values[-1]) - d(values[0])) / d(values[0]) if d(values[0]) > 0 else Decimal(0)
    metrics = {"growth": str(growth), "concentration": str(concentration)}
    if data.get("same_period_growth") and growth <= d(data["same_period_growth"]): return "inconclusive", metrics
    return ("candidate" if growth >= d(c["min_growth"]) and concentration <= d(c["max_concentration"]) else "rejected"), metrics


def structure(data: dict[str, Any], c: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    shares, survival = data.get("brand_shares"), data.get("new_entry_survival_rate")
    if not shares or survival is None: return "inconclusive", {}
    values = sorted((d(value) for value in shares), reverse=True)
    if any(not 0 <= value <= 1 for value in values) or sum(values) > d("1.000001"): raise OracleError("share scale")
    cr3 = sum(values[:3], Decimal(0)); hhi = sum((value ** 2 for value in values), Decimal(0))
    metrics = {"cr3": str(cr3), "hhi": str(hhi), "new_entry_survival_rate": str(d(survival))}
    passed = cr3 <= d(c["max_cr3"]) and d(survival) >= d(c["min_survival"]) and bool(data.get("entry_wedge"))
    return ("candidate" if passed else "rejected"), metrics


def economics(data: dict[str, Any], c: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, dict) or set(scenarios) != {"base", "stress", "upside"}: return "blocked", {}
    keys = {"price", "cogs", "inbound", "referral", "fulfillment", "return", "warranty", "promo", "advertising"}
    margins = {}
    for name, scenario in scenarios.items():
        if set(scenario) != keys: return "blocked", {}
        margins[name] = d(scenario["price"]) - sum((d(scenario[key]) for key in keys - {"price"}), Decimal(0))
    metrics = {name + "_contribution": str(value) for name, value in margins.items()}
    passed = margins["base"] > d(c["minimum_base_contribution"]) and margins["stress"] >= d(c["minimum_stress_contribution"])
    return ("candidate" if passed else "rejected"), metrics


def supply_gap(data: dict[str, Any], c: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if data.get("prohibited"): return "blocked", {}
    keys = ["validated_demand", "available_products", "relevance", "availability", "quality_acceptance"]
    if any(data.get(key) is None for key in keys): return "inconclusive", {}
    effective = d(data["available_products"])
    for key in ("relevance", "availability", "quality_acceptance"):
        factor = d(data[key])
        if not 0 <= factor <= 1: raise OracleError("factor scale")
        effective *= factor
    gap = d(data["validated_demand"]) - effective
    metrics = {"effective_supply": str(effective), "opportunity_gap": str(gap)}
    passed = bool(data.get("demand_evidence_ids")) and gap >= d(c["minimum_gap"])
    return ("candidate" if passed else "rejected"), metrics


def voc_gap(data: dict[str, Any], c: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    records = data.get("coded_events")
    if not records: return "inconclusive", {}
    unique = {item.get("event_id"): item for item in records if item.get("event_id") and item.get("evidence_id")}
    themes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in unique.values(): themes[item.get("theme", "open_class")].append(item)
    rows, qualified = [], []
    for theme, items in sorted(themes.items()):
        severe = [item for item in items if int(item["severity"][1]) >= c["minimum_severity"]]
        families = {item.get("source_family_id") for item in severe if item.get("source_family_id")}
        controlled = [item for item in severe if item.get("controllability") == "controllable"]
        row = {"theme": theme, "unique_events": len(items), "severe_events": len(severe), "source_families": len(families), "controllable_events": len(controlled), "evidence_ids": sorted({item["evidence_id"] for item in items})}
        rows.append(row)
        if len(severe) >= c["minimum_events"] and len(families) >= c["minimum_source_families"] and len(controlled) == len(severe): qualified.append(theme)
    return ("candidate" if qualified else "rejected"), {"themes": rows, "qualified_themes": qualified}


def traffic(data: dict[str, Any], c: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    periods = data.get("periods")
    if not periods or len(periods) < c["minimum_periods"]: return "inconclusive", {}
    if len({item.get("source_family_id") for item in periods if item.get("source_family_id")}) < c["minimum_source_families"]: return "inconclusive", {}
    values = [d(item.get("nonbrand_organic_ratio")) for item in periods]
    if any(not 0 <= value <= 1 for value in values): raise OracleError("ratio scale")
    average = sum(values, Decimal(0)) / Decimal(len(values))
    return ("candidate" if average >= d(c["minimum_nonbrand_ratio"]) else "rejected"), {"average_nonbrand_organic_ratio": str(average), "periods": len(periods)}


def seasonal(data: dict[str, Any], c: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    years = data.get("seasonal_years")
    if not years or len(years) < c["minimum_years"]: return "inconclusive", {}
    peak, as_of = date.fromisoformat(data["peak_start"]), date.fromisoformat(data["as_of"])
    lead = sum(int(data.get(key, 0)) for key in ("production_lead_days", "international_lead_days", "inbound_buffer_days"))
    latest = peak - timedelta(days=lead); metrics = {"latest_order_date": latest.isoformat(), "lead_days": lead}
    if not data.get("inventory_exit_path"): return "blocked", metrics
    return ("candidate" if as_of <= latest else "expired"), metrics


ORACLES = {"NEW_PRODUCT_BREAKOUT": breakout, "DISTRIBUTED_KEYWORD_DEMAND": keyword, "MARKET_ENTRY_STRUCTURE": structure, "ECONOMIC_FEASIBILITY": economics, "VALIDATED_SUPPLY_GAP": supply_gap, "RESOLVABLE_PRODUCT_GAP": voc_gap, "TRAFFIC_REPLICABILITY": traffic, "SEASONAL_PREPOSITIONING_WINDOW": seasonal}


def evaluate(signal_type: str, data: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    if signal_type not in ORACLES: raise OracleError("unsupported oracle")
    status, metrics = ORACLES[signal_type](data, calibration)
    return {"signal_type": signal_type, "status": status, "metrics": metrics, "oracle_version": "OSL-ORACLE-v1"}
