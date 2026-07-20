#!/usr/bin/env python3
"""Release-gate tests for expert reports, cross-skill scenarios and failure behavior."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "evaluations" / "golden"
CROSS_GOLDEN = ROOT / "evaluations" / "cross-skill"
FULL_GOLDEN = ROOT / "evaluations" / "golden-reports"
ADVERSARIAL = ROOT / "evaluations" / "adversarial-cases"
SCENARIOS = json.loads((ROOT / "evaluations" / "cross-skill-scenarios.json").read_text(encoding="utf-8"))["scenarios"]
spec = importlib.util.spec_from_file_location("report_eval", ROOT / "scripts" / "evaluate_report_quality.py")
report_eval = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(report_eval)

SKILLS = {
    "category-investment-decision": ROOT / "category-investment-decision" / "SKILL.md",
    "competitive-intelligence-monitoring": ROOT / "competitive-intelligence-monitoring" / "SKILL.md",
    "video-link-breakdown": ROOT / "video-link-breakdown" / "SKILL.md",
    "consumer-insights-customer-growth": ROOT / "consumer-insights-customer-growth" / "SKILL.md",
    "advertising-analysis-measurement-optimization": ROOT / "advertising-analysis-measurement-optimization" / "SKILL.md",
    "logistics-inventory-fulfillment-decision": ROOT / "logistics-inventory-fulfillment-decision" / "SKILL.md",
    "platform-store-listing-conversion": ROOT / "platform-store-listing-conversion" / "SKILL.md",
}


def run_json(script: Path, payload: object, expect_ok: bool = True) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as td:
        inp, out = Path(td) / "input.json", Path(td) / "output.json"
        inp.write_text(json.dumps(payload), encoding="utf-8")
        result = subprocess.run(["python3", str(script), "--input", str(inp), "--output", str(out)], capture_output=True, text=True)
        if expect_ok and result.returncode:
            raise AssertionError(result.stderr)
        if not expect_ok and result.returncode == 0:
            raise AssertionError(f"unsafe input unexpectedly accepted: {payload}")
        return result


class GoldenReportGate(unittest.TestCase):
    def test_all_seven_single_skill_golden_reports_score_100(self):
        files = sorted(GOLDEN.glob("*.md"))
        self.assertEqual(len(files), 7)
        for file in files:
            with self.subTest(report=file.name):
                result = report_eval.score_report(file.read_text(encoding="utf-8"), "contract")
                self.assertEqual(result["result"], "PASS")
                self.assertEqual(result["score"], 100)

    def test_full_golden_reports_pass_semantic_depth_gate(self):
        files = sorted(FULL_GOLDEN.glob("*.md"))
        self.assertGreaterEqual(len(files), 2)
        for file in files:
            with self.subTest(report=file.name):
                result = report_eval.score_report(file.read_text(encoding="utf-8"), "full")
                self.assertEqual(result["result"], "PASS", result)
                self.assertEqual(result["score"], 100, result)

    def test_keyword_stuffing_and_fake_reproducibility_fail(self):
        for file in ADVERSARIAL.glob("*.md"):
            with self.subTest(report=file.name):
                result = report_eval.score_report(file.read_text(encoding="utf-8"), "contract")
                self.assertEqual(result["result"], "FAIL", result)

    def test_progressive_lineage_golden_passes_deterministic_validator(self):
        script = ROOT / "category-investment-decision/scripts/validate_report_lineage.py"
        bundle = ROOT / "evaluations/lineage/cidm-progressive-rebase.json"
        result = subprocess.run(["python3", str(script), str(bundle)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_removing_each_critical_module_fails_or_lowers_below_gate(self):
        text = (GOLDEN / "d09-single.md").read_text(encoding="utf-8")
        removals = ["证据与反证", "经济与计算", "主权与联动", "行动计划", "停止条件"]
        for phrase in removals:
            with self.subTest(removed=phrase):
                mutated = text.replace(phrase, "")
                result = report_eval.score_report(mutated)
                self.assertEqual(result["result"], "FAIL")

    def test_every_p0_redline_forces_failure(self):
        base = (GOLDEN / "cidm-single.md").read_text(encoding="utf-8")
        injections = ["伪造事实：是", "主权越界：是", "因果越界：是", "隐私违规：是", "可复算：否", "未解决红线：是，立即放量 Scale"]
        for injection in injections:
            with self.subTest(redline=injection):
                self.assertEqual(report_eval.score_report(base + "\n" + injection, "fixture")["result"], "FAIL")


class CrossSkillScenarioGate(unittest.TestCase):
    def test_ten_cross_skill_golden_reports_pass(self):
        files = sorted(CROSS_GOLDEN.glob("*.md"))
        self.assertEqual(len(files), 10)
        for file in files:
            with self.subTest(report=file.name):
                self.assertEqual(report_eval.score_report(file.read_text(encoding="utf-8"), "contract")["result"], "PASS")

    def test_ten_complex_scenarios_are_unique_and_complete(self):
        self.assertEqual(len(SCENARIOS), 10)
        self.assertEqual(len({s["id"] for s in SCENARIOS}), 10)
        expected = {"Test", "Repair", "Hold", "Reduce", "Blocked", "Inconclusive", "Stop"}
        self.assertTrue(expected <= {s["expected"] for s in SCENARIOS})
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario["id"]):
                self.assertIn(scenario["primary"], SKILLS)
                self.assertGreaterEqual(len(scenario["participants"]), 1)
                self.assertTrue(scenario["must"] and scenario["forbidden"])
                self.assertTrue(set(scenario["participants"]) <= set(SKILLS))

    def test_each_scenario_has_one_primary_and_no_primary_in_participants(self):
        for scenario in SCENARIOS:
            self.assertNotIn(scenario["primary"], scenario["participants"], scenario["id"])

    def test_all_seven_skills_are_exercised_and_inventory_conflict_routes_d07(self):
        exercised = {s["primary"] for s in SCENARIOS}
        exercised |= {p for s in SCENARIOS for p in s["participants"]}
        self.assertEqual(exercised, set(SKILLS))
        inventory_case = next(s for s in SCENARIOS if s["id"] == "XS-06")
        self.assertIn("logistics-inventory-fulfillment-decision", inventory_case["participants"])

    def test_partial_failure_and_conflict_scenarios_exist(self):
        self.assertTrue(any("failed" in scenario for scenario in SCENARIOS))
        self.assertGreaterEqual(sum("conflict" in scenario for scenario in SCENARIOS), 8)

    def test_d09_routing_is_runtime_visible_in_all_other_skills(self):
        for name, path in SKILLS.items():
            if name == "advertising-analysis-measurement-optimization":
                continue
            with self.subTest(skill=name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("advertising-analysis-measurement-optimization", text)
                self.assertIn("inconclusive", text)

    def test_cross_scenarios_forbid_known_authority_failures(self):
        forbidden = " ".join(item for scenario in SCENARIOS for item in scenario["forbidden"])
        for phrase in ["D09直接Go", "广告决定补货", "D09执行CRM", "跨品类直接调分", "多数投票", "正面分数覆盖负利润"]:
            self.assertIn(phrase, forbidden)


class AdversarialModelGate(unittest.TestCase):
    def test_d09_rejects_nonfinite_duplicate_and_invalid_inputs(self):
        d09 = ROOT / "advertising-analysis-measurement-optimization" / "scripts"
        run_json(d09 / "ad_economics.py", {"mode":"fixed","revenue":float("nan"),"pre_ad_cm_rate":.3,"fixed_cost":10}, False)
        run_json(d09 / "marginal_analysis.py", [{"spend":100,"mature_revenue":200,"contribution_profit":20},{"spend":100,"mature_revenue":210,"contribution_profit":21}], False)
        run_json(d09 / "evaluate_incrementality.py", {"treatment":{"n":10,"value":10,"variance":-1},"control":{"n":10,"value":8,"variance":1}}, False)
        run_json(d09 / "allocate_budget.py", {"budget":-1,"candidates":[]}, False)

    def test_cig_rejects_impossible_survival_and_experiment_counts(self):
        cig = ROOT / "consumer-insights-customer-growth" / "scripts"
        run_json(cig / "calculate_clv.py", {"expected_contribution_margins":[10],"survival":[1.2]}, False)
        run_json(cig / "evaluate_growth_experiment.py", {"treatment":{"n":10,"successes":11},"control":{"n":10,"successes":2}}, False)

    def test_cim_rejects_mixed_objects_and_unsorted_snapshots(self):
        script = ROOT / "competitive-intelligence-monitoring" / "scripts" / "detect_changes.py"
        run_json(script, [{"product_id":"A","snapshot_at":"2026-02-01","price":1},{"product_id":"B","snapshot_at":"2026-01-01","price":2}], False)

    def test_order_invariance_for_d09_budget_candidates(self):
        script = ROOT / "advertising-analysis-measurement-optimization" / "scripts" / "allocate_budget.py"
        payload = {"budget":200,"candidates":[{"id":"a","step":100,"max_budget":200,"marginal_contribution_per_currency":.2},{"id":"b","step":100,"max_budget":200,"marginal_contribution_per_currency":.1}]}
        with tempfile.TemporaryDirectory() as td:
            def output(data):
                inp,out=Path(td)/"i.json",Path(td)/"o.json";inp.write_text(json.dumps(data));subprocess.run(["python3",str(script),"--input",str(inp),"--output",str(out)],check=True);return {x["id"]:x["allocated"] for x in json.loads(out.read_text())["allocations"]}
            self.assertEqual(output(payload), output({**payload,"candidates":list(reversed(payload["candidates"]))}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
