#!/usr/bin/env python3
"""Tests for VLB scripts and analytical framework reference files.

Covers:
1. score_video.py — weighted scoring logic, weight table integrity, edge cases
2. unit_economics.py — contribution margin, max CPA, reverse mode, ROI
3. video-type-typology.md — framework content integrity
4. category-video-expression.md — framework content integrity
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root (test is inside video-link-breakdown/scripts/)
SCRIPTS = ROOT / "video-link-breakdown" / "scripts"
REFERENCES = ROOT / "video-link-breakdown" / "references"

# Allow importing score_video module directly
sys.path.insert(0, str(SCRIPTS))

SCORE_SCRIPT = SCRIPTS / "score_video.py"
ECONOMICS_SCRIPT = SCRIPTS / "unit_economics.py"
TYPOLOGY_REF = REFERENCES / "video-type-typology.md"
CATEGORY_REF = REFERENCES / "category-video-expression.md"


def run_script(script_path, args):
    """Run a script and return parsed JSON output."""
    result = subprocess.run(
        ["python3", str(script_path)] + args,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {result.stderr}")
    return json.loads(result.stdout)


# ─── score_video.py tests ───────────────────────────────────────────────────


class ScoreVideoWeightIntegrity(unittest.TestCase):
    """Verify the weight table sums to 100 for each video type."""

    def test_all_types_sum_to_100(self):
        """Each video type's weights must sum to exactly 100."""
        from score_video import WEIGHT_TABLE
        for video_type, weights in WEIGHT_TABLE.items():
            total = sum(weights.values())
            self.assertEqual(
                total, 100,
                f"Weight table for '{video_type}' sums to {total}, expected 100",
            )

    def test_six_types_defined(self):
        """Must define exactly 6 video types."""
        from score_video import WEIGHT_TABLE
        expected = {"带货", "知识", "情绪", "娱乐", "人设", "电商成交"}
        self.assertEqual(set(WEIGHT_TABLE.keys()), expected)

    def test_ecommerce_has_product_match(self):
        """电商成交 type must have product_match dimension; others must not."""
        from score_video import WEIGHT_TABLE
        for video_type, weights in WEIGHT_TABLE.items():
            if video_type == "电商成交":
                self.assertIn("product_match", weights)
            else:
                self.assertNotIn("product_match", weights)


class ScoreVideoComputation(unittest.TestCase):
    """Verify scoring computation is correct."""

    def test_perfect_scores_100(self):
        """All 10s should give weighted total = 100."""
        output = run_script(SCORE_SCRIPT, [
            "--type", "带货",
            "--hook", "10", "--rhythm", "10", "--density", "10",
            "--persuasion", "10", "--originality", "10",
            "--replication", "10", "--conversion", "10",
        ])
        self.assertEqual(output["weighted_total"], 100.0)

    def test_all_ones_gives_weight_sum_div_10(self):
        """All 1s should give weighted total = sum(weights)/10 = 10."""
        output = run_script(SCORE_SCRIPT, [
            "--type", "带货",
            "--hook", "1", "--rhythm", "1", "--density", "1",
            "--persuasion", "1", "--originality", "1",
            "--replication", "1", "--conversion", "1",
        ])
        self.assertEqual(output["weighted_total"], 10.0)

    def test_ecommerce_with_product_match(self):
        """电商成交 with product_match should include it in breakdown."""
        output = run_script(SCORE_SCRIPT, [
            "--type", "电商成交",
            "--hook", "7", "--rhythm", "6", "--density", "5",
            "--persuasion", "8", "--originality", "6",
            "--replication", "7", "--conversion", "8",
            "--product-match", "9",
        ])
        dims = [d["dimension"] for d in output["breakdown"]]
        self.assertIn("产品-视频匹配", dims)
        self.assertEqual(output["dimensions_scored"], 8)

    def test_missing_dimension_flagged(self):
        """Missing dimensions should be reported."""
        output = run_script(SCORE_SCRIPT, [
            "--type", "带货",
            "--hook", "8", "--rhythm", "7",
        ])
        self.assertIn("missing_dimensions", output)
        self.assertGreater(len(output["missing_dimensions"]), 0)

    def test_invalid_score_rejected(self):
        """Score outside 1-10 should fail."""
        result = subprocess.run(
            ["python3", str(SCORE_SCRIPT), "--type", "带货", "--hook", "11"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)

    def test_confidence_override(self):
        """Explicit --confidence should override auto-detection."""
        output = run_script(SCORE_SCRIPT, [
            "--type", "带货",
            "--hook", "8", "--rhythm", "7", "--density", "6",
            "--persuasion", "8", "--originality", "7",
            "--replication", "9", "--conversion", "5",
            "--confidence", "high",
        ])
        self.assertEqual(output["confidence"], "high")


# ─── unit_economics.py tests ────────────────────────────────────────────────


class UnitEconomicsComputation(unittest.TestCase):
    """Verify unit economics calculations."""

    BASE_ARGS = [
        "--price", "29.99",
        "--product", "5.0", "--packaging", "1.0", "--shipping", "3.5",
        "--commission-rate", "0.15", "--payment-rate", "0.03",
        "--return-rate", "0.08", "--return-loss-rate", "0.5",
    ]

    def test_contribution_margin_positive(self):
        """Basic case should have positive contribution margin."""
        output = run_script(ECONOMICS_SCRIPT, self.BASE_ARGS)
        self.assertGreater(output["contribution_margin"], 0)
        self.assertEqual(output["unit_economics_status"], "positive_contribution_no_cpa")

    def test_max_cpa_less_than_contribution(self):
        """Max CPA should be less than contribution margin when target margin > 0."""
        output = run_script(ECONOMICS_SCRIPT, self.BASE_ARGS + [
            "--target-margin-rate", "0.10",
        ])
        self.assertLess(output["max_cpa"], output["contribution_margin"])

    def test_cpa_headroom(self):
        """When actual CPA < max CPA, status should be viable."""
        output = run_script(ECONOMICS_SCRIPT, self.BASE_ARGS + [
            "--cpa", "4.0", "--target-margin-rate", "0.10",
        ])
        self.assertEqual(output["unit_economics_status"], "viable")
        self.assertGreater(output["cpa_headroom"], 0)

    def test_cpa_exceeds_max(self):
        """When actual CPA > max CPA, status should flag it."""
        output = run_script(ECONOMICS_SCRIPT, self.BASE_ARGS + [
            "--cpa", "20.0", "--target-margin-rate", "0.10",
        ])
        self.assertEqual(output["unit_economics_status"], "cpa_exceeds_max")

    def test_batch_break_even_orders(self):
        """Batch break-even orders should be computed when fixed costs > 0."""
        output = run_script(ECONOMICS_SCRIPT, self.BASE_ARGS + [
            "--batch-fixed-costs", "2000",
        ])
        self.assertIn("break_even_orders", output)
        self.assertGreater(output["break_even_orders"], 0)

    def test_reverse_mode(self):
        """Reverse mode should compute minimum price."""
        output = run_script(ECONOMICS_SCRIPT, [
            "--reverse", "--cpa", "5.0",
            "--product", "5.0", "--packaging", "1.0", "--shipping", "3.5",
            "--commission-rate", "0.15", "--payment-rate", "0.03",
            "--return-rate", "0.08", "--return-loss-rate", "0.5",
            "--target-margin-rate", "0.10",
        ])
        self.assertEqual(output["mode"], "reverse")
        self.assertGreater(output["minimum_price"], 0)
        self.assertGreaterEqual(output["recommended_price"], output["minimum_price"])

    def test_roi_with_orders(self):
        """ROI should be computed when content cost and orders are provided."""
        output = run_script(ECONOMICS_SCRIPT, self.BASE_ARGS + [
            "--cpa", "4.0", "--content-cost", "500",
            "--promotion-cost", "1000", "--orders", "300",
        ])
        self.assertIn("roi_pct", output)
        self.assertIsNotNone(output["roi_pct"])

    def test_negative_contribution(self):
        """Very high costs should result in negative contribution."""
        output = run_script(ECONOMICS_SCRIPT, [
            "--price", "10.0",
            "--product", "8.0", "--packaging", "3.0", "--shipping", "5.0",
            "--commission-rate", "0.15", "--payment-rate", "0.03",
        ])
        self.assertEqual(output["unit_economics_status"], "negative_contribution")


# ─── Reference framework integrity tests ─────────────────────────────────────


class VideoTypeTypologyIntegrity(unittest.TestCase):
    """Verify video-type-typology.md contains required framework elements."""

    def setUp(self):
        self.text = TYPOLOGY_REF.read_text(encoding="utf-8")

    def test_five_types_defined(self):
        """Must define all 5 video types."""
        for type_name in ["货架视频", "内容视频", "广告素材", "品牌视频", "达人视频"]:
            self.assertIn(type_name, self.text, f"Missing video type: {type_name}")

    def test_evaluation_criteria_matrix(self):
        """Must include evaluation criteria comparison across types."""
        self.assertIn("评价标准", self.text)

    def test_scoring_model_connection(self):
        """Must reference scoring-model.md for weight mapping."""
        self.assertIn("scoring-model", self.text)

    def test_category_cross_reference(self):
        """Must reference category-video-expression.md for cross-use."""
        self.assertIn("category-video-expression", self.text)


class CategoryVideoExpressionIntegrity(unittest.TestCase):
    """Verify category-video-expression.md contains required framework elements."""

    def setUp(self):
        self.text = CATEGORY_REF.read_text(encoding="utf-8")

    def test_nine_categories_defined(self):
        """Must define all 9 categories."""
        categories = [
            "3C", "美妆", "家居", "服饰", "食品",
            "母婴", "户外", "宠物", "汽配",
        ]
        for cat in categories:
            self.assertIn(cat, self.text, f"Missing category: {cat}")

    def test_beat_preferences(self):
        """Must include beat preference information per category."""
        self.assertIn("节拍", self.text)

    def test_evidence_type_preference(self):
        """Must include evidence type preference per category."""
        self.assertIn("证据", self.text)

    def test_duration_range(self):
        """Must include typical duration range per category."""
        self.assertIn("时长", self.text)

    def test_diagnostic_checklist(self):
        """Must include a diagnostic checklist."""
        self.assertIn("诊断", self.text)


if __name__ == "__main__":
    unittest.main()
