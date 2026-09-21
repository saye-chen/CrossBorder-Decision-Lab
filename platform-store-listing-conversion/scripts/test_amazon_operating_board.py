#!/usr/bin/env python3
"""Contract tests for Amazon cadence-aware operating boards."""

from __future__ import annotations

import copy
import json
import pathlib
import sys
import unittest


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from validate_amazon_operating_board import validate  # noqa: E402


OPS_PATH = ROOT / "platform-store-listing-conversion/references/amazon-operating-workflows-and-metrics.json"


def board() -> dict:
    return {
        "platform": "Amazon",
        "board_id": "board-amz-001",
        "store_profile_id": "sp-amz-us-brand-fba-001",
        "operating_archetype_id": "AMZ-3P-BRAND-FBA",
        "overlay_ids": ["AMZ-BRAND-ASSET-LAYER"],
        "marketplace_id": "ATVPDKIKX0DER",
        "date": "2026-09-21",
        "cadence": "daily",
        "lifecycle_phase": "steady_state",
        "workstream_id": "AMZ-OPS-06-ADS-RETAIL-READINESS",
        "task_id": "task-ads-retail-001",
        "trigger": "daily_close",
        "owner_domain": "advertising_analysis_measurement_optimization",
        "input_evidence_ids": ["E-AMZ-ADS-001", "E-AMZ-OFFER-001"],
        "metric_snapshot_ids": ["snapshot-001"],
        "metric_ids": ["M-AD-SPEND", "M-BUYABILITY-RATE"],
        "metric_scope": "offer",
        "metric_class": "outcome",
        "decision_question": "广告消耗是否发生在当前可购买 Offer 上",
        "current_state": "observed",
        "unknowns": [],
        "action_ceiling": "controlled_pilot_only",
        "success_conditions": ["对象键、Offer 和广告窗口一致"],
        "stop_conditions": ["可购买状态或身份发生冲突"],
        "rollback_ref": "rb-amz-ads-001",
        "next_due": "2026-09-22T09:00:00+08:00",
        "as_of_time": "2026-09-21T08:00:00+08:00",
        "external_write": False,
        "metric_records": [
            {"metric_id": "M-AD-SPEND", "metric_scope": "ads_profile", "metric_class": "outcome", "object_key": "ads-profile-001|ATVPDKIKX0DER|2026-09-20", "value_state": "observed", "value": "120.00", "unit": "currency", "currency": "USD", "window_start": "2026-09-20", "window_end": "2026-09-20", "observed_at": "2026-09-21T08:00:00+08:00", "source_contract": "amazon-ads-performance", "evidence_id": "E-AMZ-ADS-001", "definition_version": "PLCO-AMAZON-OPS-2026.07", "comparable_to": "same_profile_same_marketplace", "attribution_type": "click_through", "maturity_state": "immature", "unknown_reason": None},
            {"metric_id": "M-BUYABILITY-RATE", "metric_scope": "offer", "metric_class": "outcome", "object_key": "B000000001|seller-sku-001|2026-09-20", "value_state": "observed", "value": "1.0", "unit": "ratio", "currency": None, "window_start": "2026-09-20", "window_end": "2026-09-20", "observed_at": "2026-09-21T08:00:00+08:00", "source_contract": "seller-central-offer-readiness", "evidence_id": "E-AMZ-OFFER-001", "definition_version": "PLCO-AMAZON-OPS-2026.07", "comparable_to": "same_offer_same_marketplace", "attribution_type": "not_applicable", "maturity_state": "observed", "unknown_reason": None},
        ],
    }


class AmazonOperatingBoard(unittest.TestCase):
    def test_complete_board_passes(self):
        result = validate(board())
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["action_limit"], "controlled_pilot_only")

    def test_missing_metric_reason_or_external_write_fails_closed(self):
        candidate = copy.deepcopy(board())
        candidate["metric_records"][0]["value_state"] = "unknown"
        candidate["metric_records"][0]["unknown_reason"] = None
        candidate["external_write"] = True
        result = validate(candidate)
        self.assertEqual(result["status"], "fail")
        self.assertIn("metric_record[0]:unknown_reason_required", result["errors"])
        self.assertIn("external_write_must_be_false", result["errors"])

    def test_wrong_cadence_or_metric_dimension_is_rejected(self):
        candidate = copy.deepcopy(board())
        candidate["cadence"] = "monthly"
        candidate["workstream_id"] = "AMZ-OPS-02-CATALOG-LISTING"
        candidate["metric_scope"] = "not_a_scope"
        result = validate(candidate)
        self.assertEqual(result["status"], "fail")
        self.assertIn("cadence_not_supported_by_workstream", result["errors"])
        self.assertIn("invalid_metric_scope", result["errors"])

    def test_unknown_current_state_is_conditional(self):
        candidate = copy.deepcopy(board())
        candidate["current_state"] = ""
        result = validate(candidate)
        self.assertEqual(result["status"], "conditional")
        self.assertEqual(result["action_limit"], "conditional_only")


if __name__ == "__main__":
    unittest.main(verbosity=2)
