#!/usr/bin/env python3
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from opportunity_models import ModelError, evaluate


class OpportunityModelTests(unittest.TestCase):
    def test_breakout_rejects_parent_relaunch_and_promotion_spike(self):
        calibration = {"max_parent_age_days": 90, "weekly_sales_floor": 50, "max_promotion_contamination": "0.4", "min_persistence": "0.75"}
        base = {"weekly_sales": [60] * 8, "parent_first_seen": "2026-06-01", "child_first_seen": "2026-07-01", "parent_age_days": 30, "promotion_sales": 0}
        self.assertEqual(evaluate("NEW_PRODUCT_BREAKOUT", base, calibration)["status"], "candidate")
        relaunch = dict(base, parent_age_days=1000)
        self.assertEqual(evaluate("NEW_PRODUCT_BREAKOUT", relaunch, calibration)["status"], "rejected")
        promotion = dict(base, promotion_sales=400)
        self.assertEqual(evaluate("NEW_PRODUCT_BREAKOUT", promotion, calibration)["status"], "rejected")

    def test_breakout_without_series_is_inconclusive(self):
        calibration = {"max_parent_age_days": 90, "weekly_sales_floor": 50, "max_promotion_contamination": "0.4", "min_persistence": "0.75"}
        self.assertEqual(evaluate("NEW_PRODUCT_BREAKOUT", {}, calibration)["status"], "inconclusive")

    def test_keyword_rejects_brand_and_scale_errors(self):
        calibration = {"min_periods": 4, "min_growth": "0.2", "max_concentration": "0.5"}
        base = {"trend": [100, 110, 120, 140], "brand_term": False, "purchase_intent": "high", "purchase_concentration": "0.4"}
        self.assertEqual(evaluate("DISTRIBUTED_KEYWORD_DEMAND", base, calibration)["status"], "candidate")
        self.assertEqual(evaluate("DISTRIBUTED_KEYWORD_DEMAND", dict(base, brand_term=True), calibration)["status"], "rejected")
        with self.assertRaisesRegex(ModelError, "0-1"):
            evaluate("DISTRIBUTED_KEYWORD_DEMAND", dict(base, purchase_concentration=40), calibration)

    def test_market_structure_needs_survival_and_entry_wedge(self):
        calibration = {"max_cr3": "0.6", "min_survival": "0.2"}
        base = {"brand_shares": ["0.2", "0.15", "0.1", "0.05"], "new_entry_survival_rate": "0.3", "entry_wedge": "underserved size"}
        result = evaluate("MARKET_ENTRY_STRUCTURE", base, calibration)
        self.assertEqual((result["status"], result["metrics"]["cr3"]), ("candidate", "0.45"))
        self.assertEqual(evaluate("MARKET_ENTRY_STRUCTURE", dict(base, entry_wedge=""), calibration)["status"], "rejected")
        self.assertEqual(evaluate("MARKET_ENTRY_STRUCTURE", {"brand_shares": ["0.2"]}, calibration)["status"], "inconclusive")

    def test_economics_requires_complete_three_scenarios(self):
        keys = {"price": 100, "cogs": 20, "inbound": 5, "referral": 15, "fulfillment": 10, "return": 5, "warranty": 2, "promo": 5, "advertising": 10}
        calibration = {"minimum_base_contribution": 0, "minimum_stress_contribution": 0}
        result = evaluate("ECONOMIC_FEASIBILITY", {"scenarios": {"base": keys, "stress": keys, "upside": keys}}, calibration)
        self.assertEqual(result["status"], "candidate")
        self.assertEqual(result["metrics"]["base_contribution"], "28")
        incomplete = {"scenarios": {"base": keys}}
        self.assertEqual(evaluate("ECONOMIC_FEASIBILITY", incomplete, calibration)["status"], "blocked")

    def test_supply_gap_needs_demand_and_respects_prohibition(self):
        calibration = {"minimum_gap": 20}
        base = {"validated_demand": 100, "available_products": 50, "relevance": ".8", "availability": ".5", "quality_acceptance": ".5", "demand_evidence_ids": ["E1"]}
        result = evaluate("VALIDATED_SUPPLY_GAP", base, calibration)
        self.assertEqual((result["status"], result["metrics"]["effective_supply"]), ("candidate", "10.000"))
        self.assertEqual(evaluate("VALIDATED_SUPPLY_GAP", dict(base, prohibited=True), calibration)["status"], "blocked")
        no_demand = dict(base, validated_demand=0, demand_evidence_ids=[])
        self.assertEqual(evaluate("VALIDATED_SUPPLY_GAP", no_demand, calibration)["status"], "rejected")

    def test_voc_is_traceable_and_does_not_call_sample_share_market_share(self):
        calibration = {"minimum_severity": 3, "minimum_events": 2, "minimum_source_families": 2}
        events = [
            {"event_id": "1", "evidence_id": "E1", "theme": "leak", "severity": "S3", "source_family_id": "reviews", "controllability": "controllable"},
            {"event_id": "2", "evidence_id": "E2", "theme": "leak", "severity": "S4", "source_family_id": "returns", "controllability": "controllable"},
            {"event_id": "2", "evidence_id": "E2", "theme": "leak", "severity": "S4", "source_family_id": "returns", "controllability": "controllable"},
        ]
        result = evaluate("RESOLVABLE_PRODUCT_GAP", {"coded_events": events}, calibration)
        self.assertEqual(result["status"], "candidate")
        self.assertEqual(result["metrics"]["qualified_themes"], ["leak"])
        self.assertIn("sample_counts_not_market_prevalence", result["observed_facts"])

    def test_traffic_requires_independent_multi_period_evidence(self):
        calibration = {"minimum_periods": 2, "minimum_source_families": 2, "minimum_nonbrand_ratio": ".5"}
        periods = [{"source_family_id": "F1", "nonbrand_organic_ratio": ".6"}, {"source_family_id": "F2", "nonbrand_organic_ratio": ".8"}]
        self.assertEqual(evaluate("TRAFFIC_REPLICABILITY", {"periods": periods}, calibration)["status"], "candidate")
        same = [{"source_family_id": "F1", "nonbrand_organic_ratio": ".9"}] * 2
        self.assertEqual(evaluate("TRAFFIC_REPLICABILITY", {"periods": same}, calibration)["status"], "inconclusive")

    def test_seasonal_window_needs_two_years_and_exit(self):
        calibration = {"minimum_years": 2}
        base = {"seasonal_years": [2024, 2025], "peak_start": "2026-11-01", "as_of": "2026-08-01", "production_lead_days": 30, "international_lead_days": 30, "inbound_buffer_days": 10, "inventory_exit_path": "outlet"}
        result = evaluate("SEASONAL_PREPOSITIONING_WINDOW", base, calibration)
        self.assertEqual((result["status"], result["metrics"]["latest_order_date"]), ("candidate", "2026-08-23"))
        self.assertEqual(evaluate("SEASONAL_PREPOSITIONING_WINDOW", dict(base, inventory_exit_path=""), calibration)["status"], "blocked")
        self.assertEqual(evaluate("SEASONAL_PREPOSITIONING_WINDOW", dict(base, as_of="2026-09-01"), calibration)["status"], "expired")

    def test_calibration_is_mandatory_and_bound(self):
        with self.assertRaisesRegex(ModelError, "calibration is required"):
            evaluate("NEW_PRODUCT_BREAKOUT", {}, {})
        calibration = {"minimum_years": 2}
        result = evaluate("SEASONAL_PREPOSITIONING_WINDOW", {"seasonal_years": [2024]}, calibration)
        self.assertTrue(result["calibration_hash"].startswith("sha256:"))

    def test_cli_rejects_extra_fields_and_emits_deterministic_result(self):
        script = Path(__file__).resolve().with_name("opportunity_signal_engine.py")
        payload = {"signal_type": "SEASONAL_PREPOSITIONING_WINDOW", "data": {"seasonal_years": [2024]}, "calibration": {"minimum_years": 2}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            valid = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertEqual(json.loads(valid.stdout)["status"], "inconclusive")
            payload["invest"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            invalid = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
            self.assertNotEqual(invalid.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
