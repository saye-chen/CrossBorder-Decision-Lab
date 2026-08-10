#!/usr/bin/env python3
"""Allocate a protected shared pool without converting unknown incrementality to zero."""

from __future__ import annotations

from common import main, n, num
from validate_ecae_inventory_handoff import receipt_from


VALUE_COMPONENTS = (
    "avoided_stockout_loss",
    "service_value",
    "incremental_fulfillment",
    "transfer_cost",
    "misallocation_risk",
)
MODES = {"qualified_incremental", "noncausal_scenario"}


def _known_components(platform: dict) -> tuple[dict, list[str]]:
    missing = [field for field in VALUE_COMPONENTS if field not in platform]
    if missing:
        return {}, missing
    return {field: n(platform, field) for field in VALUE_COMPONENTS}, []


def _base_value(components: dict) -> float:
    return (
        components["avoided_stockout_loss"]
        + components["service_value"]
        - components["incremental_fulfillment"]
        - components["transfer_cost"]
        - components["misallocation_risk"]
    )


def run(data: dict, migration: dict | None = None) -> dict:
    mode = data.get("allocation_value_mode", "qualified_incremental")
    if mode not in MODES:
        raise ValueError(f"allocation_value_mode must be one of {sorted(MODES)}")
    total = n(data, "total_eligible_inventory")
    operational = n(data, "operational_reserve")
    platforms = data.get("platforms", [])
    if not isinstance(platforms, list) or not platforms:
        raise ValueError("platforms must be a non-empty array")
    identifiers = [platform.get("id") for platform in platforms]
    if any(not isinstance(identifier, str) or not identifier.strip() for identifier in identifiers):
        raise ValueError("every platform requires a non-empty string id")
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("platform ids must be unique")

    rows = []
    base_total = 0.0
    blockers: list[str] = []
    for platform in platforms:
        platform_id = platform["id"]
        base = n(platform, "base_protection") + n(platform, "event_reservation") + n(platform, "after_sales_reserve")
        base_total += base
        components, missing_components = _known_components(platform)
        max_extra = n(platform, "max_extra")
        row = {
            "id": platform_id,
            "base": base,
            "max_extra": max_extra,
            "value": None,
            "value_components": components,
            "contribution_input": {"state": "unknown"},
        }
        if missing_components:
            row["missing_value_components"] = missing_components
            blockers.extend(f"{platform_id}:MISSING_VALUE_COMPONENT:{field}" for field in missing_components)

        if "incremental_contribution" in platform:
            blockers.append(f"{platform_id}:LEGACY_INCREMENTAL_INPUT_FORBIDDEN")

        if mode == "noncausal_scenario":
            if "ecae_inventory_receipt" in platform or "ecae_handoff_context" in platform:
                blockers.append(f"{platform_id}:SCENARIO_AND_CAUSAL_INPUT_CONFLICT")
            if "scenario_contribution" not in platform:
                blockers.append(f"{platform_id}:MISSING_SCENARIO_CONTRIBUTION")
            else:
                scenario_contribution = num(platform["scenario_contribution"], "scenario_contribution", minimum=None)
                row["contribution_input"] = {"state": "scenario_not_incremental", "value": scenario_contribution}
                if not missing_components:
                    row["value"] = _base_value(components) + scenario_contribution
        else:
            receipt = receipt_from(platform, migration=migration)
            if receipt is None:
                blockers.append(f"{platform_id}:INCREMENTAL_CONTRIBUTION_UNKNOWN")
            else:
                row["ecae_receipt"] = {
                    "receipt_id": receipt["receipt_id"],
                    "decision": receipt["decision"],
                    "reasons": receipt["reasons"],
                    "ranking_use_allowed": receipt["ranking_use_allowed"],
                }
                if receipt["incremental_value_state"] != "qualified" or receipt["ranking_use_allowed"] is not True:
                    blockers.append(f"{platform_id}:INCREMENTAL_CONTRIBUTION_UNKNOWN")
                else:
                    contribution = num(receipt["incremental_contribution"], "incremental_contribution", minimum=None)
                    row["contribution_input"] = {
                        "state": "qualified",
                        "value": contribution,
                        "receipt_id": receipt["receipt_id"],
                    }
                    if not missing_components:
                        row["value"] = _base_value(components) + contribution
        rows.append(row)

    shared_pool = total - operational - base_total
    policy = {
        "business_owner_decision_required": True,
        "inventory_decision_owner": "LIFD",
        "automatic_inventory_allocation_allowed": False,
        "external_write": False,
    }
    if shared_pool < 0:
        for row in rows:
            row["extra"] = 0.0
            row["total"] = row["base"]
        return {
            "decision": "blocked",
            "reasons": ["BASE_PROTECTION_EXCEEDS_ELIGIBLE_INVENTORY"],
            "shortfall": round(-shared_pool, 6),
            "allocations": rows,
            "conserved": False,
            **policy,
        }

    if blockers:
        for row in rows:
            row["extra"] = None
            row["total_committed"] = row["base"]
        return {
            "decision": "inconclusive",
            "value_semantics": "unknown_never_zero_fill" if mode == "qualified_incremental" else "scenario_input_incomplete",
            "reasons": sorted(set(blockers)),
            "shared_pool_initial": round(shared_pool, 6),
            "unallocated": round(shared_pool, 6),
            "allocations": rows,
            "conserved": abs(sum(row["base"] for row in rows) + operational + shared_pool - total) < 1e-9,
            **policy,
        }

    if shared_pool == 0:
        for row in rows:
            row["extra"] = 0.0
            row["total"] = row["base"]
        return {
            "decision": "base_only",
            "value_semantics": "qualified_incremental" if mode == "qualified_incremental" else "scenario_not_incremental",
            "shared_pool_initial": 0.0,
            "unallocated": 0.0,
            "allocations": rows,
            "conserved": abs(sum(row["total"] for row in rows) + operational - total) < 1e-9,
            **policy,
        }

    pool = shared_pool
    for row in sorted(rows, key=lambda candidate: (-candidate["value"], candidate["id"])):
        extra = min(pool, row["max_extra"]) if row["value"] > 0 else 0.0
        row["extra"] = extra
        row["total"] = row["base"] + extra
        pool -= extra
    for row in rows:
        row.setdefault("extra", 0.0)
        row.setdefault("total", row["base"])
    return {
        "decision": "proposed_allocation" if mode == "qualified_incremental" else "scenario_allocation",
        "value_semantics": "qualified_incremental" if mode == "qualified_incremental" else "scenario_not_incremental",
        "causal_wording_allowed": mode == "qualified_incremental",
        "shared_pool_initial": round(shared_pool, 6),
        "unallocated": round(pool, 6),
        "allocations": rows,
        "conserved": abs(sum(row["total"] for row in rows) + operational + pool - total) < 1e-9,
        **policy,
    }


if __name__ == "__main__":
    main(run)
