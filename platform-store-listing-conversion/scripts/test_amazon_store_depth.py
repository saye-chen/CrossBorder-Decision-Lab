#!/usr/bin/env python3
"""Contract tests for Amazon store-aware routing."""

from __future__ import annotations

import copy
import json
import pathlib
import sys
import unittest


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from validate_amazon_store_profile import validate  # noqa: E402


REGISTRY_PATH = ROOT / "platform-store-listing-conversion/references/amazon-store-operating-models.json"
OPS_PATH = ROOT / "platform-store-listing-conversion/references/amazon-operating-workflows-and-metrics.json"


def registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def profile(archetype: str = "AMZ-3P-BRAND-FBA") -> dict:
    common = {
        "platform": "Amazon",
        "store_profile_id": "sp-amz-us-brand-fba-001",
        "seller_account_id": "seller-account-001",
        "seller_id": "seller-001",
        "legal_entity_id": "entity-001",
        "marketplace_id": "ATVPDKIKX0DER",
        "marketplace_site": "amazon.com",
        "storefront_id": "storefront-001",
        "brand_id": "brand-001",
        "seller_role": "brand_owner",
        "selling_program": "seller_central_3p",
        "fulfillment_mode": "fba",
        "inventory_owner": "seller",
        "catalog_owner": "brand",
        "brand_authorization_state": "confirmed",
        "ads_profile_id": "ads-profile-001",
        "account_health_state": "healthy",
        "tax_scope": "us-marketplace-tax-scope-001",
        "as_of_time": "2026-09-21T00:00:00+08:00",
        "evidence_ids": ["E-AMZ-STORE-001", "E-AMZ-OFFER-001"],
        "archetype_id": archetype,
        "overlays": ["AMZ-BRAND-ASSET-LAYER"],
        "external_write": False,
    }
    if archetype == "AMZ-3P-BRAND-MFN":
        common["fulfillment_mode"] = "mfn"
    elif archetype == "AMZ-3P-RESELLER-FBA":
        common.update({"seller_role": "authorized_reseller", "catalog_owner": "shared"})
    elif archetype == "AMZ-3P-RESELLER-MFN":
        common.update({"seller_role": "authorized_reseller", "catalog_owner": "shared", "fulfillment_mode": "mfn"})
    elif archetype == "AMZ-1P-VENDOR":
        common.update({
            "seller_role": "vendor_1p",
            "selling_program": "vendor_central_1p",
            "fulfillment_mode": "vendor_fulfilled",
            "inventory_owner": "vendor",
            "catalog_owner": "manufacturer",
            "brand_id": None,
            "brand_authorization_state": "not_applicable",
            "overlays": [],
            "vendor_code": "vendor-001",
        })
    return common


class AmazonStoreDepth(unittest.TestCase):
    def test_registry_has_five_base_models_three_overlays_and_seven_surfaces(self):
        data = registry()
        self.assertEqual(len(data["operating_archetypes"]), 5)
        self.assertEqual(len(data["overlays"]), 3)
        self.assertGreaterEqual(len(data["decision_surfaces"]), 7)
        self.assertEqual(len({x["id"] for x in data["operating_archetypes"]}), 5)
        self.assertEqual(len({x["id"] for x in data["overlays"]}), 3)

    def test_known_profiles_pass(self):
        for archetype in (
            "AMZ-3P-BRAND-FBA", "AMZ-3P-BRAND-MFN", "AMZ-3P-RESELLER-FBA",
            "AMZ-3P-RESELLER-MFN", "AMZ-1P-VENDOR",
        ):
            result = validate(profile(archetype))
            self.assertEqual(result["status"], "pass", (archetype, result))

    def test_missing_identity_blocks(self):
        candidate = profile()
        del candidate["seller_account_id"]
        result = validate(candidate)
        self.assertEqual(result["status"], "fail")
        self.assertIn("missing:seller_account_id", " ".join(result["errors"]))

    def test_overlay_cannot_be_base_archetype(self):
        candidate = profile()
        candidate["archetype_id"] = "AMZ-BRAND-ASSET-LAYER"
        result = validate(candidate)
        self.assertEqual(result["status"], "fail")
        self.assertIn("overlay_is_not_operating_profile", result["errors"])

    def test_fba_and_mfn_cannot_inherit_each_others_economics(self):
        candidate = profile()
        candidate["fulfillment_mode"] = "mfn"
        result = validate(candidate)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any(x.startswith("archetype_mismatch:fulfillment_mode") for x in result["errors"]))

    def test_unknown_is_conditional_not_pass(self):
        candidate = profile()
        candidate["fulfillment_mode"] = "unknown"
        result = validate(candidate)
        self.assertEqual(result["status"], "conditional")
        self.assertNotEqual(result["status"], "pass")

    def test_b2b_and_brand_asset_are_explicit_overlays(self):
        candidate = profile()
        candidate["overlays"] = ["AMZ-BUSINESS-B2B", "AMZ-BRAND-ASSET-LAYER"]
        candidate["business_customer_mode"] = "enabled"
        result = validate(candidate)
        self.assertEqual(result["status"], "pass", result)

    def test_platform_card_and_skill_are_wired(self):
        card_data = json.loads((ROOT / "platform-store-listing-conversion/references/platform-expert-cards.json").read_text(encoding="utf-8"))
        amazon = next(card for card in card_data["cards"] if card["platform"] == "Amazon")
        self.assertTrue(amazon["store_profile_required"])
        self.assertEqual(len(amazon["store_archetypes"]), 5)
        self.assertEqual(len(amazon["overlays"]), 3)
        skill = (ROOT / "platform-store-listing-conversion/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("validate_amazon_store_profile.py", skill)
        self.assertIn("FBA/MFN/Vendor", skill)

    def test_operating_workflows_split_cadence_metrics_and_report_routes(self):
        data = json.loads(OPS_PATH.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["workstreams"]), 11)
        workstream_ids = {item["id"] for item in data["workstreams"]}
        metric_ids = {item["id"] for item in data["metric_catalog"]}
        self.assertEqual(len(metric_ids), len(data["metric_catalog"]))
        for item in data["workstreams"]:
            self.assertTrue(set(item["metrics"]) <= metric_ids, item["id"])
            self.assertTrue(item["daily_tasks"] and item["decision_questions"])
        self.assertEqual(set(data["archetype_daily_routes"]), {
            "AMZ-3P-BRAND-FBA", "AMZ-3P-BRAND-MFN", "AMZ-3P-RESELLER-FBA",
            "AMZ-3P-RESELLER-MFN", "AMZ-1P-VENDOR",
        })
        for route in data["archetype_daily_routes"].values():
            for cadence in ("intraday", "daily", "weekly", "monthly"):
                self.assertTrue(route[cadence], cadence)
            self.assertTrue(set(sum((route[cadence] for cadence in ("intraday", "daily", "weekly", "monthly")), [])) <= workstream_ids)
        for phase in ("prelaunch", "launch", "steady_state", "growth", "incident", "migration", "exit"):
            self.assertTrue(set(data["lifecycle_routes"][phase]["workstreams"]) <= workstream_ids, phase)
            self.assertTrue(set(data["lifecycle_routes"][phase]["metrics"]) <= metric_ids, phase)
        self.assertEqual(len(data["report_routing"]), 8)
        required = set(data["daily_board_contract"]["required_fields"])
        self.assertTrue({"operating_archetype_id", "lifecycle_phase", "cadence", "workstream_id", "metric_scope", "metric_class", "action_ceiling"} <= required)


if __name__ == "__main__":
    unittest.main(verbosity=2)
