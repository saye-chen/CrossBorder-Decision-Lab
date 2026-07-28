#!/usr/bin/env python3

import copy
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("reconcile_economic_ledger.py")
SPEC = importlib.util.spec_from_file_location("ppfc_reconcile", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def evidence(evidence_id="E1", grade="E3", status="verified"):
    return {
        "evidence_id": evidence_id,
        "subject_id": "SKU-1",
        "evidence_grade": grade,
        "source_type": "authorized_first_party",
        "source_ref": f"fixture:{evidence_id}",
        "observed_at": "2026-07-28T00:00:00Z",
        "recorded_at": "2026-07-28T00:00:00Z",
        "verified_at": "2026-07-28T00:00:00Z",
        "valid_until": "2026-08-28T00:00:00Z",
        "processing_status": status,
        "fingerprint": "a" * 64,
        "allowed_uses": ["current_object_calculation"],
        "forbidden_uses": [],
        "conflict_evidence_ids": [],
        "notes": None,
    }


def valid_payload():
    return {
        "reconciliation_id": "REC-1",
        "subject_id": "SKU-1",
        "as_of_time": "2026-07-28T12:00:00Z",
        "currency": "USD",
        "tax_basis": "pass_through_excluded",
        "quantity_unit": "piece",
        "order_lines": [
            {
                "order_id": "O1", "order_line_id": "L1", "state_version": "v1",
                "state": "fulfilled", "quantity": "2", "fulfilled_quantity": "2",
                "refunded_quantity": "0", "gross_sales": "200", "discounts": "10",
                "pass_through_tax": "20", "refunds": "0", "other_reversals": "0",
                "currency": "USD", "evidence_id": "E1"
            },
            {
                "order_id": "O2", "order_line_id": "L1", "state_version": "v2",
                "state": "partially_refunded", "quantity": "1", "fulfilled_quantity": "1",
                "refunded_quantity": "1", "gross_sales": "100", "discounts": "0",
                "pass_through_tax": "10", "refunds": "90", "other_reversals": "0",
                "currency": "USD", "evidence_id": "E1"
            }
        ],
        "cost_components": [
            {
                "cost_id": "C1", "deduplication_key": "invoice-1-line-1",
                "cost_nature": "product", "behavior": "per_unit",
                "decision_relevance": "avoidable", "recognition": "cogs",
                "calculation_basis": "fulfilled_unit", "allocation_basis": "direct",
                "amount": "90", "currency": "USD", "evidence_id": "E1"
            },
            {
                "cost_id": "C2", "deduplication_key": "platform-bill-1",
                "cost_nature": "platform", "behavior": "revenue_rate",
                "decision_relevance": "marginal", "recognition": "period_expense",
                "calculation_basis": "tax_exclusive_revenue", "allocation_basis": "direct",
                "amount": "27", "currency": "USD", "evidence_id": "E1"
            }
        ],
        "inventory": {
            "opening": "100", "inbound": "20", "released_reserve": "0",
            "return_resellable": "1", "fulfilled": "3", "sample_allocated": "10",
            "new_reserve": "5", "writeoff": "1", "reported_closing": "102"
        },
        "cash_events": [
            {
                "cash_event_id": "CE1", "occurred_at": "2026-07-28T01:00:00Z",
                "direction": "inflow", "event_type": "platform_settlement",
                "amount": "180", "currency": "USD", "settlement_status": "settled",
                "evidence_id": "E1"
            },
            {
                "cash_event_id": "CE2", "occurred_at": "2026-07-28T02:00:00Z",
                "direction": "outflow", "event_type": "procurement",
                "amount": "120", "currency": "USD", "settlement_status": "settled",
                "evidence_id": "E1"
            }
        ],
        "reported_totals": {
            "gross_sales": "300", "discounts": "10", "pass_through_tax": "30",
            "refunds": "90", "other_reversals": "0", "recognized_net_revenue": "170",
            "total_cost": "117", "cash_inflows": "180", "cash_outflows": "120"
        },
        "evidence_ids": ["E1"],
        "evidence_records": [evidence()],
        "rounding_tolerance": "0"
    }


class ReconciliationTests(unittest.TestCase):
    def test_happy_path_reconciles_exactly_at_dq3(self):
        result = MODULE.reconcile(valid_payload())
        self.assertEqual(result["status"], "reconciled")
        self.assertEqual(result["data_quality"], "DQ3")
        self.assertEqual(result["computed_totals"]["recognized_net_revenue"], "170")
        self.assertEqual(result["inventory_bridge"]["difference"], "0")
        self.assertFalse(result["blocking_errors"])
        self.assertEqual(len(result["input_hash"]), 64)
        self.assertEqual(len(result["result_hash"]), 64)

    def test_duplicate_order_line_blocks(self):
        payload = valid_payload()
        payload["order_lines"].append(copy.deepcopy(payload["order_lines"][0]))
        result = MODULE.reconcile(payload)
        self.assertEqual(result["status"], "blocked")
        self.assertTrue(any("order_line:duplicate" in error for error in result["blocking_errors"]))

    def test_duplicate_cost_deduplication_key_blocks(self):
        payload = valid_payload()
        duplicate = copy.deepcopy(payload["cost_components"][0])
        duplicate["cost_id"] = "C3"
        payload["cost_components"].append(duplicate)
        payload["reported_totals"]["total_cost"] = "207"
        result = MODULE.reconcile(payload)
        self.assertIn("cost:duplicate:invoice-1-line-1", result["blocking_errors"])

    def test_reported_total_difference_cannot_be_plugged(self):
        payload = valid_payload()
        payload["reported_totals"]["recognized_net_revenue"] = "171"
        result = MODULE.reconcile(payload)
        self.assertEqual(result["differences"]["recognized_net_revenue"], "-1")
        self.assertIn("REPORTED_TOTAL_MISMATCH:recognized_net_revenue", result["blocking_errors"])

    def test_inventory_nonconservation_blocks(self):
        payload = valid_payload()
        payload["inventory"]["reported_closing"] = "103"
        result = MODULE.reconcile(payload)
        self.assertIn("INVENTORY_NOT_CONSERVED", result["blocking_errors"])

    def test_fulfilled_order_and_inventory_quantity_must_match(self):
        payload = valid_payload()
        payload["inventory"]["fulfilled"] = "2"
        payload["inventory"]["reported_closing"] = "103"
        result = MODULE.reconcile(payload)
        self.assertIn("FULFILLED_UNITS_DO_NOT_MATCH_INVENTORY", result["blocking_errors"])

    def test_currency_mismatch_blocks(self):
        payload = valid_payload()
        payload["cost_components"][0]["currency"] = "EUR"
        result = MODULE.reconcile(payload)
        self.assertIn("COST_CURRENCY_MISMATCH:0", result["blocking_errors"])

    def test_binary_float_is_rejected(self):
        payload = valid_payload()
        payload["order_lines"][0]["gross_sales"] = 200.0
        with self.assertRaises(MODULE.ReconciliationError):
            MODULE.reconcile(payload)

    def test_missing_referenced_evidence_blocks(self):
        payload = valid_payload()
        payload["cash_events"][0]["evidence_id"] = "E-MISSING"
        result = MODULE.reconcile(payload)
        self.assertIn("E-MISSING", result["missing_evidence"])
        self.assertIn("MISSING_REFERENCED_EVIDENCE", result["blocking_errors"])

    def test_stale_evidence_degrades_to_dq1(self):
        payload = valid_payload()
        payload["evidence_records"][0]["processing_status"] = "stale"
        result = MODULE.reconcile(payload)
        self.assertEqual(result["status"], "reconciled_with_warnings")
        self.assertEqual(result["data_quality"], "DQ1")
        self.assertEqual(result["action_ceiling"], "hypothesis_only")

    def test_cancelled_order_with_revenue_blocks(self):
        payload = valid_payload()
        payload["order_lines"][0]["state"] = "cancelled"
        result = MODULE.reconcile(payload)
        self.assertIn("NON_RECOGNIZABLE_ORDER_HAS_REVENUE:0", result["blocking_errors"])

    def test_input_and_result_hashes_are_idempotent(self):
        first = MODULE.reconcile(valid_payload())
        second = MODULE.reconcile(valid_payload())
        self.assertEqual(first["input_hash"], second["input_hash"])
        self.assertEqual(first["result_hash"], second["result_hash"])


if __name__ == "__main__":
    unittest.main()
