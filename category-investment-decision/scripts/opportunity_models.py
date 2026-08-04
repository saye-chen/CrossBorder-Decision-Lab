#!/usr/bin/env python3
"""Deterministic models for the eight CIDM opportunity-signal families."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Callable


class ModelError(ValueError):
    pass


def _decimal(value: Any, field: str) -> Decimal:
    if value is None:
        raise ModelError(f"{field} is unknown")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ModelError(f"{field} must be numeric") from exc
    if not number.is_finite():
        raise ModelError(f"{field} must be finite")
    return number


def _hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()


def _result(signal_type: str, status: str, metrics: dict[str, Any], facts: list[str], alternatives: list[str], actions: list[str], input_value: Any) -> dict[str, Any]:
    return {"signal_type": signal_type, "status": status, "metrics": metrics, "observed_facts": facts, "alternative_explanations": alternatives, "validation_actions": actions, "input_hash": _hash(input_value), "model_version": "OSL-MODELS-v1"}


def new_product_breakout(data: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    sales = data.get("weekly_sales")
    if not isinstance(sales, list) or not sales or any(value is None for value in sales):
        return _result("NEW_PRODUCT_BREAKOUT", "inconclusive", {}, [], ["trend_series_missing"], ["obtain_8_to_12_week_series"], data)
    if data.get("parent_first_seen") is None or data.get("child_first_seen") is None:
        return _result("NEW_PRODUCT_BREAKOUT", "inconclusive", {}, [], ["parent_child_identity_unknown"], ["verify_parent_child_history"], data)
    if data.get("parent_age_days", 0) > calibration["max_parent_age_days"]:
        return _result("NEW_PRODUCT_BREAKOUT", "rejected", {}, ["parent_is_not_new"], ["child_asin_relaunch"], [], data)
    positive_weeks = sum(_decimal(value, "weekly_sales") >= _decimal(calibration["weekly_sales_floor"], "weekly_sales_floor") for value in sales)
    persistence = Decimal(positive_weeks) / Decimal(len(sales))
    promotion_sales = _decimal(data.get("promotion_sales", 0), "promotion_sales")
    total_sales = sum((_decimal(value, "weekly_sales") for value in sales), Decimal("0"))
    contamination = promotion_sales / total_sales if total_sales > 0 else Decimal("1")
    metrics = {"breakout_persistence": str(persistence), "promotion_contamination": str(contamination), "weeks": len(sales)}
    if data.get("review_inheritance") or data.get("variant_merge_event"):
        return _result("NEW_PRODUCT_BREAKOUT", "rejected", metrics, ["identity_or_review_history_contaminated"], ["inherited_social_proof"], [], data)
    if contamination > _decimal(calibration["max_promotion_contamination"], "max_promotion_contamination"):
        return _result("NEW_PRODUCT_BREAKOUT", "rejected", metrics, ["promotion_dominates_observed_sales"], ["deal_or_offsite_spike"], ["retest_outside_promotion"], data)
    status = "candidate" if persistence >= _decimal(calibration["min_persistence"], "min_persistence") else "rejected"
    return _result("NEW_PRODUCT_BREAKOUT", status, metrics, ["parent_identity_checked", "weekly_continuity_calculated"], ["brand_traffic", "stockout_or_replenishment_effect"], ["verify_nonbrand_demand", "recompute_full_profit"], data)


def distributed_keyword_demand(data: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    trend = data.get("trend")
    if not isinstance(trend, list) or len(trend) < calibration["min_periods"] or any(value is None for value in trend):
        return _result("DISTRIBUTED_KEYWORD_DEMAND", "inconclusive", {}, [], ["insufficient_trend_window"], ["obtain_calibrated_history"], data)
    if data.get("brand_term") or data.get("purchase_intent") not in {"high", "medium"}:
        return _result("DISTRIBUTED_KEYWORD_DEMAND", "rejected", {}, ["brand_or_low_purchase_intent"], ["navigation_or_information_demand"], [], data)
    first, last = _decimal(trend[0], "trend"), _decimal(trend[-1], "trend")
    growth = (last - first) / first if first > 0 else Decimal("0")
    concentration = _decimal(data.get("purchase_concentration"), "purchase_concentration")
    if concentration < 0 or concentration > 1:
        raise ModelError("purchase_concentration must use 0-1 scale")
    facts = ["nonbrand_purchase_intent_checked", "trend_window_checked", "purchase_concentration_checked"]
    if data.get("same_period_growth") and growth <= _decimal(data["same_period_growth"], "same_period_growth"):
        return _result("DISTRIBUTED_KEYWORD_DEMAND", "inconclusive", {"growth": str(growth), "concentration": str(concentration)}, facts, ["seasonality_explains_growth"], ["test_out_of_season"], data)
    status = "candidate" if growth >= _decimal(calibration["min_growth"], "min_growth") and concentration <= _decimal(calibration["max_concentration"], "max_concentration") else "rejected"
    return _result("DISTRIBUTED_KEYWORD_DEMAND", status, {"growth": str(growth), "concentration": str(concentration)}, facts, ["event_demand", "mixed_search_intent"], ["map_keyword_to_product_concept", "estimate_acquisition_cost"], data)


def market_entry_structure(data: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    shares = data.get("brand_shares")
    survival = data.get("new_entry_survival_rate")
    if not isinstance(shares, list) or not shares or survival is None:
        return _result("MARKET_ENTRY_STRUCTURE", "inconclusive", {}, [], ["concentration_or_survival_unknown"], ["obtain_parent_deduplicated_shares"], data)
    numbers = [_decimal(value, "brand_share") for value in shares]
    if any(value < 0 or value > 1 for value in numbers) or sum(numbers) > Decimal("1.000001"):
        raise ModelError("brand shares must use 0-1 scale and sum to at most 1")
    ordered = sorted(numbers, reverse=True)
    cr3 = sum(ordered[:3], Decimal("0")); hhi = sum((value * value for value in numbers), Decimal("0"))
    survival_value = _decimal(survival, "new_entry_survival_rate")
    status = "candidate" if cr3 <= _decimal(calibration["max_cr3"], "max_cr3") and survival_value >= _decimal(calibration["min_survival"], "min_survival") and data.get("entry_wedge") else "rejected"
    return _result("MARKET_ENTRY_STRUCTURE", status, {"cr3": str(cr3), "hhi": str(hhi), "new_entry_survival_rate": str(survival_value)}, ["parent_asin_and_brand_normalization_required"], ["fragmented_price_war", "advertising_barrier", "subbrand_fragmentation"], ["validate_entry_wedge"], data)


def economic_feasibility(data: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, dict) or set(scenarios) != {"base", "stress", "upside"}:
        return _result("ECONOMIC_FEASIBILITY", "blocked", {}, [], ["three_scenario_economics_missing"], ["recompute_complete_costs"], data)
    required_costs = {"price", "cogs", "inbound", "referral", "fulfillment", "return", "warranty", "promo", "advertising"}
    margins: dict[str, Decimal] = {}
    for name, scenario in scenarios.items():
        if set(scenario) != required_costs:
            return _result("ECONOMIC_FEASIBILITY", "blocked", {}, [], [f"{name}_costs_incomplete"], ["recompute_complete_costs"], data)
        price = _decimal(scenario["price"], f"{name}.price")
        costs = sum((_decimal(scenario[key], f"{name}.{key}") for key in required_costs - {"price"}), Decimal("0"))
        margins[name] = price - costs
    status = "candidate" if margins["base"] > _decimal(calibration["minimum_base_contribution"], "minimum_base_contribution") and margins["stress"] >= _decimal(calibration["minimum_stress_contribution"], "minimum_stress_contribution") else "rejected"
    return _result("ECONOMIC_FEASIBILITY", status, {key + "_contribution": str(value) for key, value in margins.items()}, ["complete_cost_buckets_recomputed"], ["fee_or_return_rate_drift", "cash_peak_unknown"], ["validate_cash_peak_and_payback"], data)


def effective_supply_gap(data: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    if data.get("prohibited"):
        return _result("VALIDATED_SUPPLY_GAP", "blocked", {}, ["prohibited_gap"], ["compliance_or_safety_prohibition"], [], data)
    required = ["validated_demand", "available_products", "relevance", "availability", "quality_acceptance"]
    if any(data.get(key) is None for key in required):
        return _result("VALIDATED_SUPPLY_GAP", "inconclusive", {}, [], ["demand_or_supply_component_unknown"], ["complete_attribute_matrix"], data)
    demand = _decimal(data["validated_demand"], "validated_demand")
    effective = _decimal(data["available_products"], "available_products")
    for key in ("relevance", "availability", "quality_acceptance"):
        factor = _decimal(data[key], key)
        if factor < 0 or factor > 1:
            raise ModelError(f"{key} must use 0-1 scale")
        effective *= factor
    gap = demand - effective
    status = "candidate" if data.get("demand_evidence_ids") and gap >= _decimal(calibration["minimum_gap"], "minimum_gap") else "rejected"
    return _result("VALIDATED_SUPPLY_GAP", status, {"effective_supply": str(effective), "opportunity_gap": str(gap)}, ["demand_and_supply_jointly_evaluated"], ["structural_no_demand", "inventory_complexity"], ["run_minimum_gap_experiment"], data)


def resolvable_product_gap(data: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    records = data.get("coded_events")
    if not isinstance(records, list) or not records:
        return _result("RESOLVABLE_PRODUCT_GAP", "inconclusive", {}, [], ["coded_voc_missing"], ["collect_traceable_voc"], data)
    unique = {event.get("event_id"): event for event in records if event.get("event_id") and event.get("evidence_id")}
    by_theme: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in unique.values():
        if event.get("severity") not in {"S0", "S1", "S2", "S3", "S4"}:
            raise ModelError("VOC severity must be S0-S4")
        by_theme[event.get("theme", "open_class")].append(event)
    candidates = []
    for theme, events in sorted(by_theme.items()):
        severe = [event for event in events if int(event["severity"][1]) >= calibration["minimum_severity"]]
        sources = {event.get("source_family_id") for event in severe if event.get("source_family_id")}
        controllable = [event for event in severe if event.get("controllability") == "controllable"]
        candidates.append({"theme": theme, "unique_events": len(events), "severe_events": len(severe), "source_families": len(sources), "controllable_events": len(controllable), "evidence_ids": sorted({event["evidence_id"] for event in events})})
    qualified = [item for item in candidates if item["severe_events"] >= calibration["minimum_events"] and item["source_families"] >= calibration["minimum_source_families"] and item["controllable_events"] == item["severe_events"]]
    status = "candidate" if qualified else "rejected"
    return _result("RESOLVABLE_PRODUCT_GAP", status, {"themes": candidates, "qualified_themes": [item["theme"] for item in qualified]}, ["sample_counts_not_market_prevalence"], ["service_or_logistics_root_cause", "user_misuse", "willingness_to_pay_unknown"], ["route_technical_cost_risk_validation"], data)


def traffic_replicability(data: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    periods = data.get("periods")
    if not isinstance(periods, list) or len(periods) < calibration["minimum_periods"]:
        return _result("TRAFFIC_REPLICABILITY", "inconclusive", {}, [], ["single_period_tool_estimate"], ["obtain_multi_period_second_source"], data)
    if len({item.get("source_family_id") for item in periods if item.get("source_family_id")}) < calibration["minimum_source_families"]:
        return _result("TRAFFIC_REPLICABILITY", "inconclusive", {}, [], ["sources_not_independent"], ["obtain_independent_source"], data)
    nonbrand = [_decimal(item.get("nonbrand_organic_ratio"), "nonbrand_organic_ratio") for item in periods]
    if any(value < 0 or value > 1 for value in nonbrand):
        raise ModelError("nonbrand organic ratio must use 0-1 scale")
    average = sum(nonbrand, Decimal("0")) / Decimal(len(nonbrand))
    status = "candidate" if average >= _decimal(calibration["minimum_nonbrand_ratio"], "minimum_nonbrand_ratio") else "rejected"
    return _result("TRAFFIC_REPLICABILITY", status, {"average_nonbrand_organic_ratio": str(average), "periods": len(periods)}, ["brand_and_nonbrand_separated"], ["offsite_or_recommendation_misattribution"], ["validate_ad_pause_or_rank_stability"], data)


def seasonal_window(data: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    years = data.get("seasonal_years")
    if not isinstance(years, list) or len(years) < calibration["minimum_years"]:
        return _result("SEASONAL_PREPOSITIONING_WINDOW", "inconclusive", {}, [], ["multi_year_history_missing"], ["obtain_two_or_more_years"], data)
    try:
        peak = date.fromisoformat(data["peak_start"]); as_of = date.fromisoformat(data["as_of"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ModelError("peak_start and as_of must be ISO dates") from exc
    lead = sum(int(data.get(key, 0)) for key in ("production_lead_days", "international_lead_days", "inbound_buffer_days"))
    latest = peak - timedelta(days=lead)
    if not data.get("inventory_exit_path"):
        return _result("SEASONAL_PREPOSITIONING_WINDOW", "blocked", {"latest_order_date": latest.isoformat()}, ["no_inventory_exit"], ["season_end_residual_inventory"], [], data)
    status = "candidate" if as_of <= latest else "expired"
    return _result("SEASONAL_PREPOSITIONING_WINDOW", status, {"latest_order_date": latest.isoformat(), "lead_days": lead}, ["multi_year_seasonality_checked"], ["event_or_weather_shift", "late_arrival"], ["run_late_low_high_demand_scenarios"], data)


MODELS: dict[str, Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]] = {
    "NEW_PRODUCT_BREAKOUT": new_product_breakout,
    "DISTRIBUTED_KEYWORD_DEMAND": distributed_keyword_demand,
    "MARKET_ENTRY_STRUCTURE": market_entry_structure,
    "ECONOMIC_FEASIBILITY": economic_feasibility,
    "VALIDATED_SUPPLY_GAP": effective_supply_gap,
    "RESOLVABLE_PRODUCT_GAP": resolvable_product_gap,
    "TRAFFIC_REPLICABILITY": traffic_replicability,
    "SEASONAL_PREPOSITIONING_WINDOW": seasonal_window,
}


def evaluate(signal_type: str, data: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    if signal_type not in MODELS:
        raise ModelError(f"unsupported signal model: {signal_type}")
    if not calibration:
        raise ModelError("calibration is required; no global thresholds are embedded")
    result = MODELS[signal_type](data, calibration)
    result["calibration_hash"] = _hash(calibration)
    return result
