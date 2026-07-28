#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_mixed_batch_scenario import evaluate


class EvaluationCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "evaluations/fixtures/evaluation-catalog.json").read_text(encoding="utf-8"))

    def test_exactly_55_unique_blueprint_cases(self):
        cases = self.catalog["cases"]
        self.assertEqual((self.catalog["count"], len(cases)), (55, 55))
        self.assertEqual([item["id"] for item in cases], [f"PPFC-E{i:02d}" for i in range(1, 56)])

    def test_all_cases_have_mechanism_state_and_counterexample(self):
        for case in self.catalog["cases"]:
            self.assertTrue(case["mechanism"], case["id"])
            self.assertTrue(case["expected"], case["id"])
            self.assertTrue(case["counterexample"], case["id"])
            self.assertNotEqual(case["expected"], case["counterexample"], case["id"])

    def test_coverage_distribution_is_exact(self):
        counts = Counter(item["category"] for item in self.catalog["cases"])
        self.assertEqual(dict(counts), self.catalog["coverage"])

    def test_mixed_and_dynamic_extremes_are_present(self):
        mechanisms = {item["mechanism"] for item in self.catalog["cases"]}
        required = {
            "mixed_batch_10pct", "five_claim_unique_order", "creator_zero_post",
            "content_rights_missing", "live_demand_over_atp", "positive_profit_cash_breach",
            "marketing_cost_idempotency", "fee_effective_boundary", "multimodal_missing_segment",
            "fee_change_full_propagation",
        }
        self.assertTrue(required <= mechanisms)

    def test_no_case_claims_production_ready(self):
        serialized = json.dumps(self.catalog, ensure_ascii=False).lower()
        self.assertNotIn("production_ready", serialized)

    def test_mixed_batch_golden_recomputes_exactly(self):
        source = json.loads((ROOT / "evaluations/golden/mixed-batch-10pct.input.json").read_text(encoding="utf-8"))
        expected = json.loads((ROOT / "evaluations/golden/mixed-batch-10pct.expected.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluate(source), expected)


if __name__ == "__main__": unittest.main()
