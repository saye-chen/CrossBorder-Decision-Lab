#!/usr/bin/env python3
"""Regression tests for deterministic models and core skill invariants."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"


def run_script(name, *args, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *map(str, args)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


class ProfitModelTests(unittest.TestCase):
    def test_known_unit_economics(self):
        result = run_script(
            "profit_model.py", "--price", 100, "--product", 20,
            "--commission-rate", 0.1, "--ad-rate", 0.2,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["net_profit"], 50.0)
        self.assertEqual(data["net_margin_pct"], 50.0)
        self.assertEqual(data["break_even_ad_rate_pct"], 70.0)

    def test_rejects_invalid_rate(self):
        result = run_script("profit_model.py", "--price", 10, "--ad-rate", 1.1)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rates must be between 0 and 1", result.stderr)


class PortfolioTests(unittest.TestCase):
    def test_constraints_and_redline(self):
        payload = {
            "constraints": {
                "desired_items": 3, "budget": 45000,
                "max_operational_load": 10, "max_per_category": 2,
                "max_per_platform": 2,
            },
            "candidates": [
                {"id": "A", "name": "A", "score": 78, "confidence": "high", "investment": 12000, "operational_load": 3, "category": "beauty", "platform": "amazon", "supplier": "S1", "redline": False},
                {"id": "B", "name": "B", "score": 82, "confidence": "medium", "investment": 20000, "operational_load": 4, "category": "home", "platform": "amazon", "supplier": "S2", "redline": False},
                {"id": "C", "name": "C", "score": 74, "confidence": "high", "investment": 10000, "operational_load": 2, "category": "pet", "platform": "tiktok", "supplier": "S3", "redline": False},
                {"id": "D", "name": "D", "score": 80, "confidence": "low", "investment": 8000, "operational_load": 2, "category": "beauty", "platform": "tiktok", "supplier": "S4", "redline": False},
                {"id": "E", "name": "E", "score": 90, "confidence": "high", "investment": 9000, "operational_load": 2, "category": "electronics", "platform": "amazon", "supplier": "S5", "redline": True},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = run_script("portfolio_selector.py", path)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual([item["id"] for item in data["selected"]], ["A", "B", "C"])
        self.assertEqual(data["excluded_redline"][0]["id"], "E")
        self.assertLessEqual(data["total_investment"], 45000)


class WorkspaceTests(unittest.TestCase):
    def test_marked_create_and_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "TMPDIR": tmp}
            created = run_script(
                "workspace_manager.py", "create", "--slug", "regression",
                "--task-id", "test-task", env=env,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            path = Path(json.loads(created.stdout)["path"])
            self.assertTrue((path / ".task-owner.json").is_file())
            cleaned = run_script(
                "workspace_manager.py", "cleanup", path,
                "--task-id", "test-task", env=env,
            )
            self.assertEqual(cleaned.returncode, 0, cleaned.stderr)
            self.assertFalse(path.exists())


class VocAnalyzerTests(unittest.TestCase):
    def test_deduplicates_and_aggregates_coded_records(self):
        records = [
            {"text": "Lid leaks", "source": "Amazon", "competitor": "A", "rating": 1, "sentiment": "negative", "themes": "leak|lid"},
            {"text": "  lid   leaks ", "source": "Reddit", "competitor": "A", "rating": 2, "sentiment": "negative", "themes": "leak"},
            {"text": "Hard to clean", "source": "Reddit", "competitor": "B", "rating": 2, "sentiment": "negative", "themes": ["cleaning"]},
            {"text": "", "source": "Amazon"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "voc.json"
            path.write_text(json.dumps(records), encoding="utf-8")
            result = run_script("analyze_voc.py", path)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["records"]["raw"], 4)
        self.assertEqual(data["records"]["unique_with_text"], 2)
        self.assertEqual(data["records"]["duplicates_or_reposts"], 1)
        self.assertEqual(data["records"]["missing_text"], 1)
        self.assertTrue(any("qualitative" in warning for warning in data["warnings"]))

    def test_flags_invalid_rating(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "voc.json"
            path.write_text(json.dumps([{"text": "Example", "rating": 8}]), encoding="utf-8")
            result = run_script("analyze_voc.py", path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["distributions"]["ratings"]["invalid"], 1)


class ExperimentEvaluationTests(unittest.TestCase):
    @staticmethod
    def payload(**overrides):
        base = {
            "experiment": "test",
            "spend": 100,
            "revenue": 200,
            "counts": {"impressions": 1000, "clicks": 100, "landing_visits": 80, "leads": 16, "purchases": 4, "refunds": 0},
            "minimums": {"landing_visits": 50},
            "gates": [
                {"metric": "lead_rate", "operator": ">=", "threshold": 0.15, "kind": "primary"},
                {"metric": "refund_rate", "operator": "<=", "threshold": 0.1, "kind": "redline"},
            ],
        }
        base.update(overrides)
        return base

    def evaluate(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "experiment.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = run_script("evaluate_experiment.py", path)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_continue_when_all_gates_pass(self):
        result = self.evaluate(self.payload())
        self.assertEqual(result["decision"], "CONTINUE")
        self.assertAlmostEqual(result["metrics"]["ctr"], 0.1)
        self.assertAlmostEqual(result["metrics"]["cac"], 25)

    def test_inconclusive_when_minimum_not_met(self):
        result = self.evaluate(self.payload(minimums={"landing_visits": 100}))
        self.assertEqual(result["decision"], "INCONCLUSIVE")

    def test_stop_when_redline_fails(self):
        changed = self.payload()
        changed["counts"]["refunds"] = 2
        self.assertEqual(self.evaluate(changed)["decision"], "STOP")

    def test_iterate_when_primary_fails(self):
        changed = self.payload()
        changed["gates"][0]["threshold"] = 0.3
        self.assertEqual(self.evaluate(changed)["decision"], "ITERATE")

    def test_rejects_impossible_funnel(self):
        changed = self.payload()
        changed["counts"]["refunds"] = 5
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "experiment.json"
            path.write_text(json.dumps(changed), encoding="utf-8")
            result = run_script("evaluate_experiment.py", path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refunds cannot exceed purchases", result.stderr)


class CoreInvariantTests(unittest.TestCase):
    def test_core_model_unchanged(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        weights = "市场需求 20、竞争可进入性 20、利润空间 20、内容传播 10、供应链可控性 10、风险可控性 10、机会窗口 10"
        self.assertIn(weights, text)
        self.assertEqual(sum(f"### STEP{index}：" in text for index in range(1, 9)), 8)
        for threshold in ("80-100", "65-79.9", "50-64.9", "<50"):
            self.assertIn(threshold, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
