#!/usr/bin/env python3
"""Deterministically reconcile PPFC orders, revenue, costs, inventory, and cash."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


DECIMAL_FIELDS = (
    "gross_sales",
    "discounts",
    "pass_through_tax",
    "refunds",
    "other_reversals",
)
EVIDENCE_RANK = {f"E{index}": index for index in range(8)}
BLOCKED_EVIDENCE_STATUS = {"invalid", "conflicted"}


class ReconciliationError(ValueError):
    pass


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def decimal_string(value: Any, field: str, *, nonnegative: bool = False) -> Decimal:
    if not isinstance(value, str):
        raise ReconciliationError(f"{field}: authoritative numeric value must be a decimal string")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ReconciliationError(f"{field}: invalid decimal string") from exc
    if not number.is_finite():
        raise ReconciliationError(f"{field}: non-finite values are forbidden")
    if nonnegative and number < 0:
        raise ReconciliationError(f"{field}: negative value is forbidden")
    return number


def exact(value: Decimal) -> str:
    if value == 0:
        return "0"
    rendered = format(value.normalize(), "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def unique(items: list[dict[str, Any]], key_fields: tuple[str, ...], label: str) -> list[str]:
    seen: set[tuple[Any, ...]] = set()
    duplicates: list[str] = []
    for item in items:
        key = tuple(item.get(field) for field in key_fields)
        if None in key or "" in key:
            duplicates.append(f"{label}:missing_key:{key}")
        elif key in seen:
            duplicates.append(f"{label}:duplicate:{'|'.join(map(str, key))}")
        seen.add(key)
    return duplicates


def referenced_evidence(payload: dict[str, Any]) -> set[str]:
    refs = set(payload.get("evidence_ids", []))
    for collection in ("order_lines", "cost_components", "cash_events"):
        refs.update(item.get("evidence_id") for item in payload.get(collection, []) if item.get("evidence_id"))
    return refs


def reconcile(payload: dict[str, Any]) -> dict[str, Any]:
    blocking: list[str] = []
    warnings: list[str] = []
    missing_evidence: list[str] = []

    required_top = {
        "reconciliation_id", "subject_id", "as_of_time", "currency", "tax_basis",
        "quantity_unit", "order_lines", "cost_components", "inventory",
        "cash_events", "reported_totals", "evidence_ids", "evidence_records",
    }
    missing_top = sorted(required_top - set(payload))
    if missing_top:
        raise ReconciliationError(f"missing required top-level fields: {missing_top}")
    currency = payload["currency"]
    if not isinstance(currency, str) or len(currency) != 3 or currency.upper() != currency:
        blocking.append("INVALID_CURRENCY")

    orders = payload["order_lines"]
    costs = payload["cost_components"]
    cash = payload["cash_events"]
    if not all(isinstance(value, list) for value in (orders, costs, cash)):
        raise ReconciliationError("order_lines, cost_components and cash_events must be arrays")
    blocking.extend(unique(orders, ("order_id", "order_line_id", "state_version"), "order_line"))
    blocking.extend(unique(costs, ("deduplication_key",), "cost"))
    blocking.extend(unique(cash, ("cash_event_id",), "cash_event"))

    totals = {name: Decimal("0") for name in DECIMAL_FIELDS}
    fulfilled_units = Decimal("0")
    refunded_units = Decimal("0")
    valid_order_lines = 0
    for index, line in enumerate(orders):
        if line.get("currency") != currency:
            blocking.append(f"ORDER_CURRENCY_MISMATCH:{index}")
        state = line.get("state")
        quantity = decimal_string(line.get("quantity"), f"order_lines[{index}].quantity", nonnegative=True)
        fulfilled = decimal_string(line.get("fulfilled_quantity"), f"order_lines[{index}].fulfilled_quantity", nonnegative=True)
        refunded = decimal_string(line.get("refunded_quantity"), f"order_lines[{index}].refunded_quantity", nonnegative=True)
        if fulfilled > quantity or refunded > fulfilled:
            blocking.append(f"ORDER_QUANTITY_STATE_INVALID:{index}")
        if state in {"cancelled", "payment_failed"}:
            if any(decimal_string(line.get(name), f"order_lines[{index}].{name}") != 0 for name in DECIMAL_FIELDS):
                blocking.append(f"NON_RECOGNIZABLE_ORDER_HAS_REVENUE:{index}")
            continue
        valid_order_lines += 1
        fulfilled_units += fulfilled
        refunded_units += refunded
        for name in DECIMAL_FIELDS:
            amount = decimal_string(line.get(name), f"order_lines[{index}].{name}", nonnegative=name != "gross_sales")
            totals[name] += amount
        if state == "refunded" and refunded != fulfilled:
            warnings.append(f"REFUNDED_STATE_QUANTITY_MISMATCH:{index}")

    recognized = (
        totals["gross_sales"]
        - totals["discounts"]
        - totals["pass_through_tax"]
        - totals["refunds"]
        - totals["other_reversals"]
    )
    total_cost = Decimal("0")
    for index, cost in enumerate(costs):
        if cost.get("currency") != currency:
            blocking.append(f"COST_CURRENCY_MISMATCH:{index}")
        total_cost += decimal_string(cost.get("amount"), f"cost_components[{index}].amount")
        for field in ("cost_nature", "behavior", "decision_relevance", "recognition", "calculation_basis", "allocation_basis"):
            if not cost.get(field):
                blocking.append(f"COST_CLASSIFICATION_MISSING:{index}:{field}")

    cash_inflows = Decimal("0")
    cash_outflows = Decimal("0")
    for index, event in enumerate(cash):
        if event.get("currency") != currency:
            blocking.append(f"CASH_CURRENCY_MISMATCH:{index}")
        amount = decimal_string(event.get("amount"), f"cash_events[{index}].amount", nonnegative=True)
        direction = event.get("direction")
        if direction == "inflow":
            cash_inflows += amount
        elif direction == "outflow":
            cash_outflows += amount
        else:
            blocking.append(f"INVALID_CASH_DIRECTION:{index}")

    inventory = payload["inventory"]
    inv = {
        name: decimal_string(inventory.get(name), f"inventory.{name}", nonnegative=True)
        for name in (
            "opening", "inbound", "released_reserve", "return_resellable",
            "fulfilled", "sample_allocated", "new_reserve", "writeoff", "reported_closing",
        )
    }
    computed_closing = (
        inv["opening"] + inv["inbound"] + inv["released_reserve"] + inv["return_resellable"]
        - inv["fulfilled"] - inv["sample_allocated"] - inv["new_reserve"] - inv["writeoff"]
    )
    inventory_difference = computed_closing - inv["reported_closing"]
    if computed_closing < 0:
        blocking.append("NEGATIVE_COMPUTED_CLOSING_INVENTORY")
    if inv["fulfilled"] != fulfilled_units:
        blocking.append("FULFILLED_UNITS_DO_NOT_MATCH_INVENTORY")

    computed = {
        **{name: exact(value) for name, value in totals.items()},
        "recognized_net_revenue": exact(recognized),
        "total_cost": exact(total_cost),
        "cash_inflows": exact(cash_inflows),
        "cash_outflows": exact(cash_outflows),
        "unique_order_lines": str(valid_order_lines),
        "fulfilled_units": exact(fulfilled_units),
        "refunded_units": exact(refunded_units),
    }
    tolerance = decimal_string(payload.get("rounding_tolerance", "0"), "rounding_tolerance", nonnegative=True)
    reported = payload["reported_totals"]
    differences: dict[str, str] = {}
    for name in (*DECIMAL_FIELDS, "recognized_net_revenue", "total_cost", "cash_inflows", "cash_outflows"):
        actual = Decimal(computed[name])
        expected = decimal_string(reported.get(name), f"reported_totals.{name}")
        delta = actual - expected
        differences[name] = exact(delta)
        if abs(delta) > tolerance:
            blocking.append(f"REPORTED_TOTAL_MISMATCH:{name}")
        elif delta != 0:
            warnings.append(f"ROUNDING_DIFFERENCE:{name}")
    if abs(inventory_difference) > tolerance:
        blocking.append("INVENTORY_NOT_CONSERVED")
    elif inventory_difference != 0:
        warnings.append("INVENTORY_ROUNDING_DIFFERENCE")

    records = payload["evidence_records"]
    blocking.extend(unique(records, ("evidence_id",), "evidence"))
    evidence_by_id = {record.get("evidence_id"): record for record in records}
    for evidence_id in sorted(referenced_evidence(payload)):
        record = evidence_by_id.get(evidence_id)
        if record is None:
            missing_evidence.append(str(evidence_id))
            continue
        grade = record.get("evidence_grade")
        status = record.get("processing_status")
        fingerprint = record.get("fingerprint")
        if grade not in EVIDENCE_RANK or grade == "E0":
            blocking.append(f"EVIDENCE_UNUSABLE:{evidence_id}")
        if status in BLOCKED_EVIDENCE_STATUS:
            blocking.append(f"EVIDENCE_{str(status).upper()}:{evidence_id}")
        elif status in {"raw", "stale"}:
            warnings.append(f"EVIDENCE_{str(status).upper()}:{evidence_id}")
        if not isinstance(fingerprint, str) or len(fingerprint) != 64:
            blocking.append(f"EVIDENCE_FINGERPRINT_INVALID:{evidence_id}")
    if missing_evidence:
        blocking.append("MISSING_REFERENCED_EVIDENCE")

    blocking = sorted(set(blocking))
    warnings = sorted(set(warnings))
    critical_grades = [
        EVIDENCE_RANK.get(record.get("evidence_grade"), 0)
        for record in records
        if record.get("evidence_id") in referenced_evidence(payload)
    ]
    if blocking:
        status, quality, ceiling = "blocked", "DQ0", "evidence_request_only"
    elif warnings or (critical_grades and min(critical_grades) <= 1):
        status, quality, ceiling = "reconciled_with_warnings", "DQ1", "hypothesis_only"
    elif critical_grades and min(critical_grades) >= 3 and all(
        record.get("processing_status") == "verified"
        for record in records
        if record.get("evidence_id") in referenced_evidence(payload)
    ):
        status, quality, ceiling = "reconciled", "DQ3", "submit_for_acceptance"
    else:
        status, quality, ceiling = "reconciled", "DQ2", "scenario_comparison"

    input_hash = canonical_hash(payload)
    result_without_hash = {
        "reconciliation_id": payload["reconciliation_id"],
        "subject_id": payload["subject_id"],
        "status": status,
        "data_quality": quality,
        "action_ceiling": ceiling,
        "computed_totals": computed,
        "inventory_bridge": {
            "computed_closing": exact(computed_closing),
            "reported_closing": exact(inv["reported_closing"]),
            "difference": exact(inventory_difference),
        },
        "differences": differences,
        "blocking_errors": blocking,
        "warnings": warnings,
        "missing_evidence": missing_evidence,
        "input_hash": input_hash,
    }
    return {**result_without_hash, "result_hash": canonical_hash(result_without_hash)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = reconcile(payload)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ReconciliationError) as exc:
        print(f"PPFC_RECONCILIATION=FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"PPFC_RECONCILIATION={result['status'].upper()}")
    return 0 if result["status"] in {"reconciled", "reconciled_with_warnings"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
