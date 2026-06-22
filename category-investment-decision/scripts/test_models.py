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
