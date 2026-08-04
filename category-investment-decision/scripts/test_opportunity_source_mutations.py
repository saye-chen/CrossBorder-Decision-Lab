#!/usr/bin/env python3
"""Execute substantive source mutations and require the independent oracle to kill each one."""
from __future__ import annotations
import json
import unittest
from pathlib import Path
import independent_opportunity_oracles as oracle

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = Path(__file__).resolve().with_name("opportunity_models.py")

MUTATIONS = [
    ("parent_age_direction", "data.get(\"parent_age_days\", 0) > calibration[\"max_parent_age_days\"]", "data.get(\"parent_age_days\", 0) < calibration[\"max_parent_age_days\"]", "O-01"),
    ("promotion_direction", "contamination > _decimal(calibration[\"max_promotion_contamination\"]", "contamination < _decimal(calibration[\"max_promotion_contamination\"]", "O-01"),
    ("persistence_direction", "persistence >= _decimal(calibration[\"min_persistence\"]", "persistence <= _decimal(calibration[\"min_persistence\"]", "O-01"),
    ("keyword_growth_direction", "growth >= _decimal(calibration[\"min_growth\"]", "growth <= _decimal(calibration[\"min_growth\"]", "O-02"),
    ("concentration_direction", "concentration <= _decimal(calibration[\"max_concentration\"]", "concentration >= _decimal(calibration[\"max_concentration\"]", "O-02"),
    ("cr3_direction", "cr3 <= _decimal(calibration[\"max_cr3\"]", "cr3 >= _decimal(calibration[\"max_cr3\"]", "O-03"),
    ("survival_direction", "survival_value >= _decimal(calibration[\"min_survival\"]", "survival_value <= _decimal(calibration[\"min_survival\"]", "O-03"),
    ("base_profit_direction", "margins[\"base\"] > _decimal(calibration[\"minimum_base_contribution\"]", "margins[\"base\"] < _decimal(calibration[\"minimum_base_contribution\"]", "O-04"),
    ("stress_profit_direction", "margins[\"stress\"] >= _decimal(calibration[\"minimum_stress_contribution\"]", "margins[\"stress\"] < _decimal(calibration[\"minimum_stress_contribution\"]", "O-04"),
    ("gap_direction", "gap >= _decimal(calibration[\"minimum_gap\"]", "gap <= _decimal(calibration[\"minimum_gap\"]", "O-05"),
    ("controllability_direction", "event.get(\"controllability\") == \"controllable\"", "event.get(\"controllability\") != \"controllable\"", "O-06"),
    ("traffic_direction", "average >= _decimal(calibration[\"minimum_nonbrand_ratio\"]", "average <= _decimal(calibration[\"minimum_nonbrand_ratio\"]", "O-07"),
    ("season_deadline_direction", "as_of <= latest", "as_of >= latest", "O-08"),
]

class OpportunityMutationTests(unittest.TestCase):
    def test_all_thirteen_mutations_are_killed(self):
        source = SOURCE_PATH.read_text(encoding="utf-8")
        cases = {case["id"]: case for case in json.loads((ROOT / "evaluations/opportunity-oracle-fixtures.json").read_text(encoding="utf-8"))["cases"]}
        killed = []
        for name, old, new, case_id in MUTATIONS:
            self.assertEqual(source.count(old), 1, f"mutation anchor drifted: {name}")
            namespace = {"__name__": "mutated_opportunity_models"}
            exec(compile(source.replace(old, new), f"<{name}>", "exec"), namespace)
            case = cases[case_id]
            expected = oracle.evaluate(case["signal_type"], case["data"], case["calibration"])
            try:
                actual = namespace["evaluate"](case["signal_type"], case["data"], case["calibration"])
                mismatch = (actual["status"], actual["metrics"]) != (expected["status"], expected["metrics"])
            except Exception:
                mismatch = True
            if mismatch: killed.append(name)
        self.assertEqual(killed, [item[0] for item in MUTATIONS])

if __name__ == "__main__":
    unittest.main(verbosity=2)
