#!/usr/bin/env python3
"""Contract tests for Amazon Ads depth, routing and fail-closed decisions."""

from __future__ import annotations

import copy
import json
import pathlib
import sys
import unittest


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from validate_amazon_ads_operating_profile import validate  # noqa: E402


MODEL_PATH = ROOT / "advertising-analysis-measurement-optimization/references/amazon-ads-operating-model.json"
CONNECTOR_PATH = ROOT / "governance/connectors/field-contracts/amazon-ads-performance.json"
GOLDEN_PATH = ROOT / "advertising-analysis-measurement-optimization/evaluations/golden/amazon-ads-operator-memo.md"


def model() -> dict:
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


def profile(ad_type: str = "sponsored_products") -> dict:
    value = {
        "platform": "Amazon",
        "store_profile_id": "sp-amz-us-brand-fba-001",
        "ads_profile_id": "ads-profile-001",
        "seller_account_id": "seller-account-001",
        "seller_id": "seller-001",
        "legal_entity_id": "entity-001",
        "marketplace_id": "ATVPDKIKX0DER",
        "marketplace_site": "amazon.com",
        "currency": "USD",
        "timezone": "America/Los_Angeles",
        "selling_program": "seller_central_3p",
        "seller_role": "brand_owner",
        "fulfillment_mode": "fba",
        "inventory_owner": "seller",
        "catalog_owner": "brand",
        "brand_authorization_state": "confirmed",
        "ad_type": ad_type,
        "campaign_id": "campaign-001",
        "campaign_status": "enabled",
        "lifecycle": "steady_state",
        "budget_or_spend_scope": "daily_budget",
        "ad_group_id": "ad-group-001",
        "ad_id": "ad-001",
        "target_id": "target-001",
        "targeting_family": "keyword",
        "target_type": "keyword",
        "keyword": "running shoes",
        "match_type": "exact",
        "query_or_search_term": "running shoes",
        "promoted_asin": "B000000001",
        "brand_asset_version": "brand-asset-v3",
        "destination_version": "store-v2",
        "retail_readiness_state": "ready",
        "attribution_type": "click_through",
        "maturity_state": "mature",
        "date": "2026-09-20",
        "as_of_time": "2026-09-21T00:00:00+08:00",
        "evidence_ids": ["E-AMZ-ADS-001", "E-AMZ-RETAIL-001"],
        "external_write": False,
    }
    if ad_type == "dsp":
        value.update({
            "targeting_family": "audience",
            "target_type": "audience",
            "audience_id": "audience-001",
            "audience_rule": "prospecting_lookalike_30d",
            "measurement_design": "geo_holdout_v1",
        })
    if ad_type == "sponsored_display":
        value.update({"targeting_family": "product", "target_type": "product"})
    if ad_type == "sponsored_brands":
        value.update({"targeting_family": "keyword", "target_type": "keyword"})
    return value


class AmazonAdsDepth(unittest.TestCase):
    def test_model_covers_ad_types_hierarchy_taxonomy_workflows_and_reports(self):
        data = model()
        self.assertEqual({item["id"] for item in data["ad_types"]}, {
            "sponsored_products", "sponsored_brands", "sponsored_display", "dsp",
        })
        self.assertGreaterEqual(len(data["campaign_hierarchy"]), 9)
        self.assertGreaterEqual(len(data["targeting_taxonomy"]), 5)
        self.assertGreaterEqual(len(data["workflows"]), 9)
        self.assertEqual(len(data["store_archetype_routes"]), 5)
        self.assertGreaterEqual(len(data["report_routes"]), 4)

    def test_all_workflow_metric_references_resolve(self):
        data = model()
        metric_ids = {item["id"] for item in data["metric_catalog"]}
        self.assertEqual(len(metric_ids), len(data["metric_catalog"]))
        for workflow in data["workflows"]:
            self.assertTrue(set(workflow["metrics"]) <= metric_ids, workflow["id"])
        for route in data["report_routes"]:
            self.assertTrue(set(route["required_workflows"]) <= {x["id"] for x in data["workflows"]})

    def test_valid_profiles_are_pilot_only(self):
        for ad_type in ("sponsored_products", "sponsored_brands", "sponsored_display", "dsp"):
            result = validate(profile(ad_type))
            self.assertEqual(result["status"], "pass", (ad_type, result))
            self.assertEqual(result["action_limit"], "controlled_pilot_only")

    def test_missing_retail_readiness_blocks_scale(self):
        candidate = profile()
        del candidate["retail_readiness_state"]
        result = validate(candidate)
        self.assertEqual(result["status"], "fail")
        self.assertIn("missing:retail_readiness_state", result["errors"])

    def test_brand_permission_is_required_for_sponsored_brands(self):
        candidate = profile("sponsored_brands")
        candidate["brand_authorization_state"] = "expired"
        result = validate(candidate)
        self.assertEqual(result["status"], "fail")
        self.assertIn("brand_authorization_not_eligible", result["errors"])

    def test_dsp_requires_audience_and_measurement_design(self):
        candidate = profile("dsp")
        del candidate["audience_id"]
        del candidate["measurement_design"]
        result = validate(candidate)
        self.assertEqual(result["status"], "fail")
        self.assertIn("missing:audience_id:dsp", result["errors"])
        self.assertIn("missing:measurement_design:dsp", result["errors"])

    def test_unknown_evidence_is_conditional_not_pass(self):
        candidate = profile()
        candidate["maturity_state"] = "unknown"
        result = validate(candidate)
        self.assertEqual(result["status"], "conditional")
        self.assertEqual(result["action_limit"], "conditional_only")

    def test_external_write_is_blocked(self):
        candidate = profile()
        candidate["external_write"] = True
        result = validate(candidate)
        self.assertEqual(result["status"], "fail")
        self.assertIn("external_write_must_be_false", result["errors"])

    def test_connector_covers_operating_grain(self):
        data = json.loads(CONNECTOR_PATH.read_text(encoding="utf-8"))
        canonical = {item["canonical_field"] for item in data["fields"]}
        required = {
            "profile_id", "seller_account_id", "marketplace_id", "ad_type", "campaign_id",
            "ad_group_id", "target_id", "keyword", "match_type", "query_or_search_term",
            "product_target_asin", "category_target", "negative_target", "bid", "budget",
            "budget_status", "placement_adjustment", "delivery_status", "retail_eligibility",
            "attributed_units", "orders", "attribution_type", "click_through_orders",
            "view_through_orders", "maturity_state", "query_source", "harvest_or_negative_state",
        }
        self.assertTrue(required <= canonical, sorted(required - canonical))
        self.assertTrue(set(data["object_key"]) <= canonical)

    def test_operator_memo_is_execution_rich(self):
        text = GOLDEN_PATH.read_text(encoding="utf-8")
        for marker in (
            "首屏结论", "对象、身份与版本", "广告类型与架构", "三本账", "低交付与不消耗诊断",
            "搜索词、目标与否定", "预算、出价与广告位", "零售准备度", "归因、蚕食与增量",
            "店铺类型路由", "每日主板", "每周与每月经营板", "异常恢复与回滚", "跨域交接",
            "success_conditions", "stop_conditions", "rollback_ref", "external_write=false",
        ):
            self.assertIn(marker, text, marker)


if __name__ == "__main__":
    unittest.main(verbosity=2)
