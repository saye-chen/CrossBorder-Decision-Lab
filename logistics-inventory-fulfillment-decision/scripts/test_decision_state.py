#!/usr/bin/env python3
import unittest
from decision_state import run,impacted

def base():
 return {"as_of_time":"2026-07-17T10:00:00+08:00","reports":[
  {"report_id":"R1","object_id":"SKU1|POOL1|US|AMZ|W1|2026W30","parent_ids":[],"is_current":False,"changed_fields":[],"recalculated_modules":[],"evidence":[],"actions":[]},
  {"report_id":"R2","object_id":"SKU1|POOL1|US|AMZ|W1|2026W30","parent_ids":["R1"],"is_current":True,"changed_fields":["lead_time"],"recalculated_modules":impacted(["lead_time"]),"evidence":[{"evidence_id":"E1","expires_at":"2026-07-18T00:00:00+08:00"}],"actions":[{"action_id":"A1","status":"executing"}]}
 ]}

class StateTests(unittest.TestCase):
 def test_valid_lineage(self): self.assertTrue(run(base())["valid"])
 def test_two_current_blocked(self):
  d=base();d["reports"][0]["is_current"]=True;self.assertIn("current_count:SKU1|POOL1|US|AMZ|W1|2026W30:2",run(d)["errors"])
 def test_cycle_blocked(self):
  d=base();d["reports"][0]["parent_ids"]=["R2"];self.assertTrue(any("lineage_cycle" in x for x in run(d)["errors"]))
 def test_cross_object_inheritance_blocked(self):
  d=base();d["reports"][1]["object_id"]="SKU2|POOL1|US|AMZ|W1|2026W30";self.assertTrue(any("cross_object_parent" in x for x in run(d)["errors"]))
 def test_missing_incremental_recompute_blocked(self):
  d=base();d["reports"][1]["changed_fields"]=["inventory"];d["reports"][1]["recalculated_modules"]=["ledger"];self.assertTrue(any("missing_incremental_recompute" in x for x in run(d)["errors"]))
 def test_expired_evidence_is_visible(self):
  d=base();d["as_of_time"]="2026-07-19T10:00:00+08:00";self.assertEqual(run(d)["expired_evidence"],["SKU1|POOL1|US|AMZ|W1|2026W30:E1"])
 def test_multidimensional_impact_union(self):
  got=impacted(["demand","lead_time","warehouse_capacity","return_rate"])
  for x in ["forecast","replenishment","routing","promising","capacity","reverse_exit","exit"]: self.assertIn(x,got)
 def test_illegal_action_jump_blocked(self):
  d=base();d["reports"][0]["actions"]=[{"action_id":"A1","status":"proposed"}];d["reports"][1]["actions"]=[{"action_id":"A1","status":"completed"}]
  self.assertTrue(any("illegal_action_transition" in x for x in run(d)["errors"]))
 def test_stopping_execution_requires_recovery(self):
  d=base();d["reports"][0]["actions"]=[{"action_id":"A1","status":"executing"}];d["reports"][1]["actions"]=[{"action_id":"A1","status":"stopped"}]
  self.assertEqual(sum("missing_action_recovery" in x for x in run(d)["errors"]),4)
 def test_cross_domain_action_cannot_self_approve(self):
  d=base();d["reports"][1]["actions"]=[{"action_id":"AD","status":"validated","owner_domain":"AAMO"}]
  self.assertTrue(any("cross_domain_self_approval" in x for x in run(d)["errors"]))
 def test_parent_evidence_cannot_silently_disappear(self):
  d=base();d["reports"][0]["evidence"]=[{"evidence_id":"OLD"}];d["reports"][1]["evidence"]=[]
  self.assertTrue(any("evidence_silently_dropped" in x for x in run(d)["errors"]))
 def test_executing_action_cannot_silently_disappear(self):
  d=base();d["reports"][0]["actions"]=[{"action_id":"RUN","status":"executing"}];d["reports"][1]["actions"]=[]
  self.assertTrue(any("active_action_silently_dropped" in x for x in run(d)["errors"]))
 def test_rolling_time_window_triggers_full_operational_recompute(self):
  got=impacted(["time_window"])
  for x in ["forecast","replenishment","routing","allocation","capacity","promising","reverse_exit"]:self.assertIn(x,got)

if __name__=="__main__":unittest.main(verbosity=2)
