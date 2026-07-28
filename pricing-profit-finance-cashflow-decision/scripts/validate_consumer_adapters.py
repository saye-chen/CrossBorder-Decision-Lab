#!/usr/bin/env python3
"""Validate PPFC consumer adapters and execute exact dual-run equivalence cases."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any

from calculate_pricing_economics import calculate_scenario
from evaluate_business_model_scenario import subscription_economics
from evaluate_consumer_financial_boundaries import (
    logistics_financial_boundary,
    partnership_commission_boundary,
    promotion_financial_boundary,
    recoverable_contribution_boundary,
)


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
EXPECTED_DOMAINS = {"CIDM", "AAMO", "CIG", "LIFD", "CAPM", "MBCM", "PLCO"}
ALLOWED_STATUSES = {"adapter_ready", "dual_run_equivalent"}
ALLOWED_DIFFERENCES = {"definition", "precision", "parameter", "business_model", "defect"}


def load_module(name: str, relative: str):
    path = REPO / relative
    script_directory = str(path.parent)
    if script_directory not in sys.path:
        sys.path.insert(0, script_directory)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {relative}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cidm_dual_run() -> bool:
    payload = {"price": 100, "product": 20, "commission_rate": 0.1, "ad_rate": 0.2}
    with tempfile.TemporaryDirectory(prefix="ppfc-cidm-eq-") as directory:
        source = Path(directory) / "input.json"
        source.write_text(json.dumps(payload), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(REPO / "category-investment-decision/scripts/profit_model.py"), "--input-json", str(source)],
            check=True, capture_output=True, text=True,
        )
    legacy = json.loads(completed.stdout)
    ppfc = calculate_scenario({
        "currency": "USD", "price": "100", "quantity": "1",
        "discount_rate": "0", "pass_through_tax_rate": "0", "refund_rate": "0",
        "other_reversals": "0", "product_cogs": "20", "fulfillment_cost": "0",
        "expected_return_cost": "0", "variable_marketing_cost": "0",
        "variable_service_cost": "0", "avoidable_period_cost": "0",
        "allocated_operating_expense": "0", "ad_spend": "20",
        "required_profit": "0", "risk_buffer": "0",
        "fees": [{"fee_id": "platform", "type": "rate", "basis": "recognized_net_revenue", "rate": "0.1"}],
    })
    return (
        Decimal(str(legacy["profit_before_ads"])) == Decimal(ppfc["profit_bridge"]["pre_ad_contribution"])
        and Decimal(str(legacy["net_profit"])) == Decimal(ppfc["profit_bridge"]["operating_profit"])
    )


def aamo_dual_run() -> bool:
    module = load_module("ppfc_aamo_economics", "advertising-analysis-measurement-optimization/scripts/ad_economics.py")
    legacy = module.calculate({
        "mode": "fixed", "revenue": 1000, "pre_ad_cm_rate": 0.3, "fixed_cost": 200
    })
    ppfc = calculate_scenario({
        "currency": "USD", "price": "1000", "quantity": "1",
        "discount_rate": "0", "pass_through_tax_rate": "0", "refund_rate": "0",
        "other_reversals": "0", "product_cogs": "700", "fulfillment_cost": "0",
        "expected_return_cost": "0", "variable_marketing_cost": "0",
        "variable_service_cost": "0", "avoidable_period_cost": "0",
        "allocated_operating_expense": "0", "ad_spend": "200",
        "required_profit": "0", "risk_buffer": "0", "fees": [],
    })
    return (
        Decimal(str(legacy["ad_contribution_profit"])) == Decimal(ppfc["profit_bridge"]["operating_profit"])
        and abs(legacy["break_even_platform_roas"] - float(ppfc["metrics"]["BREAK_EVEN_ROAS_NET"])) < 0.000001
    )


def cig_dual_run() -> bool:
    payload = {"expected_contribution_margins": [60, 60], "survival": [1, 0.5], "cac": 50}
    with tempfile.TemporaryDirectory(prefix="ppfc-cig-eq-") as directory:
        source = Path(directory) / "input.json"
        output = Path(directory) / "output.json"
        source.write_text(json.dumps(payload), encoding="utf-8")
        subprocess.run(
            [sys.executable, str(REPO / "consumer-insights-customer-growth/scripts/calculate_clv.py"), "--input", str(source), "--output", str(output)],
            check=True, capture_output=True, text=True,
        )
        legacy = json.loads(output.read_text(encoding="utf-8"))
    ppfc = subscription_economics("60", "60", "0.5", 2, "50")
    return (
        Decimal(str(legacy["gross_customer_value"])) == Decimal(ppfc["contribution_clv"])
        and Decimal(str(legacy["net_clv"])) == Decimal(ppfc["net_after_cac"])
    )


def lifd_dual_run() -> bool:
    module = load_module("ppfc_lifd_economics", "logistics-inventory-fulfillment-decision/scripts/logistics_economics.py")
    legacy_input = {
        "purchase_price": 10, "main_haul": 2, "pick_pack": 1,
        "carrier_base": 3, "holding": 1, "selling_price": 20,
        "minimum_contribution": 2,
    }
    legacy = module.run(legacy_input)
    ppfc = logistics_financial_boundary({key: str(value) for key, value in legacy_input.items()})
    return (
        Decimal(str(legacy["landed_cost_per_unit"])) == Decimal(ppfc["landed_cost_per_unit"])
        and Decimal(str(legacy["fulfillment_cost_per_order"])) == Decimal(ppfc["fulfillment_cost_per_order"])
        and Decimal(str(legacy["total_relevant_cost"])) == Decimal(ppfc["total_relevant_cost"])
        and Decimal(str(legacy["contribution"])) == Decimal(ppfc["contribution"])
    )


def capm_dual_run() -> bool:
    module = load_module("ppfc_capm_economics", "creator-affiliate-partnership-management/scripts/partnership_economics.py")
    legacy_input = {
        "mature_net_revenue": 1000, "commission_base": 900, "target_profit": 100,
        "non_commission_costs": [
            {"cost_id": "cogs", "amount": 400},
            {"cost_id": "fulfillment", "amount": 100},
        ],
    }
    legacy = module.commission_ceiling(legacy_input)
    ppfc = partnership_commission_boundary({
        **{key: str(value) for key, value in legacy_input.items() if key != "non_commission_costs"},
        "non_commission_costs": [
            {"cost_id": item["cost_id"], "amount": str(item["amount"])}
            for item in legacy_input["non_commission_costs"]
        ],
    })
    return (
        abs(legacy["max_commission_rate"] - float(ppfc["max_commission_rate"])) < 0.000000001
        and Decimal(str(legacy["available_for_commission"])) == Decimal(ppfc["available_for_commission"])
    )


def mbcm_dual_run() -> bool:
    module = load_module("ppfc_mbcm_offer", "marketing-brand-campaign-management/scripts/offer_economics.py")
    legacy_input = {
        "eligible": 200, "redeemed_orders": 100, "incremental_orders": 30,
        "merchant_discount_per_redeemed": 3, "gift_cost_per_redeemed": 1,
        "shipping_subsidy_per_redeemed": 0, "guarantee_cost": 10,
        "fraud_loss": 5, "service_cost": 5, "incremental_cm_per_order": 20,
        "pull_forward_loss": 20, "cannibalization_loss": 20, "fixed_cost": 40,
        "currency": "USD",
    }
    legacy = module.calculate(legacy_input)
    ppfc = promotion_financial_boundary({
        key: str(value) for key, value in legacy_input.items() if key != "currency"
    })
    return (
        Decimal(str(legacy["non_incremental_redeemed_orders"])) == Decimal(ppfc["non_incremental_redeemed_orders"])
        and Decimal(str(legacy["total_offer_burden"])) == Decimal(ppfc["total_offer_burden"])
        and Decimal(str(legacy["incremental_offer_contribution"])) == Decimal(ppfc["incremental_offer_contribution"])
        and abs(legacy["break_even_incremental_order_rate"] - float(ppfc["break_even_incremental_order_rate"])) < 0.000000001
    )


def plco_dual_run() -> bool:
    module = load_module("ppfc_plco_value", "platform-store-listing-conversion/scripts/calculate_recoverable_value.py")
    legacy_input = {
        "qualified_visits": 1000, "conversion_gap": 0.05, "recoverable_share": 0.5,
        "mature_contribution_per_order": {"low": 2, "high": 4},
        "implementation_cost": 10, "currency": "USD",
    }
    legacy = module.calculate(legacy_input)
    ppfc = recoverable_contribution_boundary({
        "qualified_visits": "1000", "conversion_gap": "0.05", "recoverable_share": "0.5",
        "mature_contribution_per_order": {"low": "2", "high": "4"},
        "implementation_cost": "10",
    })
    return (
        Decimal(str(legacy["recoverable_orders"])) == Decimal(ppfc["recoverable_orders"])
        and [Decimal(str(value)) for value in legacy["contribution_range"]]
        == [Decimal(value) for value in ppfc["contribution_range"]]
    )


EXACT_RUNNERS = {
    "CIDM": cidm_dual_run,
    "AAMO": aamo_dual_run,
    "CIG": cig_dual_run,
    "LIFD": lifd_dual_run,
    "CAPM": capm_dual_run,
    "MBCM": mbcm_dual_run,
    "PLCO": plco_dual_run,
}


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("external_write") is not False:
        errors.append("EXTERNAL_WRITE_FORBIDDEN")
    adapters = payload.get("adapters", [])
    migration = json.loads(
        (ROOT / "evaluations/migration-compatibility.json").read_text(encoding="utf-8")
    )
    migration_status = {
        item["domain"]: item["migration_status"]
        for item in migration["consumers"]
        if item["domain"] != "ERDG"
    }
    if {item.get("domain") for item in adapters} != EXPECTED_DOMAINS:
        errors.append("CONSUMER_ADAPTER_INVENTORY_INCOMPLETE")
    for adapter in adapters:
        domain = adapter.get("domain", "UNKNOWN")
        if migration_status.get(domain) != adapter.get("status"):
            errors.append(f"{domain}:MIGRATION_LEDGER_STATUS_MISMATCH")
        if adapter.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{domain}:INVALID_MIGRATION_STATUS")
        for field in ("source_calculator", "source_fields", "ppfc_fields", "shared_outputs", "retained_sovereignty", "forbidden_writeback"):
            if not adapter.get(field):
                errors.append(f"{domain}:MISSING:{field}")
        calculator = adapter.get("source_calculator")
        if calculator and not (REPO / calculator).is_file():
            errors.append(f"{domain}:SOURCE_CALCULATOR_MISSING")
        if adapter.get("status") == "dual_run_equivalent":
            runner = EXACT_RUNNERS.get(domain)
            if runner is None or not runner():
                errors.append(f"{domain}:DUAL_RUN_DIFFERENCE")
        else:
            if adapter.get("difference_class") not in ALLOWED_DIFFERENCES:
                errors.append(f"{domain}:UNCLASSIFIED_DIFFERENCE")
            if not adapter.get("difference_reason"):
                errors.append(f"{domain}:DIFFERENCE_REASON_MISSING")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", nargs="?", type=Path,
        default=ROOT / "evaluations/consumer-adapters.json",
    )
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    errors = validate(payload)
    result = {
        "valid": not errors,
        "adapter_count": len(payload.get("adapters", [])),
        "dual_run_equivalent": sum(item.get("status") == "dual_run_equivalent" for item in payload.get("adapters", [])),
        "adapter_ready": sum(item.get("status") == "adapter_ready" for item in payload.get("adapters", [])),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
