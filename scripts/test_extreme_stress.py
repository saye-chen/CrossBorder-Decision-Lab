#!/usr/bin/env python3
import importlib.util,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]; s=importlib.util.spec_from_file_location("v",R/"scripts/validate_extreme_stress.py"); v=importlib.util.module_from_spec(s); s.loader.exec_module(v)
class T(unittest.TestCase):
 def rows(self): return {x["id"]:x for x in json.loads((R/"evaluations/extreme-stress-scenarios.json").read_text())["scenarios"]}
 def test_all_stress_scenarios_execute(self): self.assertEqual(v.validate(),[])
 def test_redline_cannot_win_portfolio(self): x=self.rows()["ES-01"]; self.assertNotIn("B",v.run(x)["selected"])
 def test_late_versions_and_duplicates_are_safe(self): r=v.run(self.rows()["ES-04"]); self.assertEqual((r["duplicate_effect"],r["late_version_effect"]),("no_op","ignored"))
 def test_regulatory_change_is_selective(self): r=v.run(self.rows()["ES-05"]); self.assertIn("claim",r["invalidated"]); self.assertIn("price_history",r["preserved"])
 def test_capacity_prioritizes_redline(self): self.assertEqual(v.run(self.rows()["ES-07"])["execute"],["recall"])
if __name__=="__main__": unittest.main(verbosity=2)
