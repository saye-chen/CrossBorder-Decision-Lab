#!/usr/bin/env python3
import unittest
from evaluate_competitive_decision import evaluate
class CompetitiveDecisionPipeline(unittest.TestCase):
 def test_mixed_object_is_blocked(self):
  d={"object_id":"A","snapshots":[{"object_id":"A","observed_at":"2026-01-01","display_condition":"x"},{"object_id":"B","observed_at":"2026-01-02","display_condition":"x"},{"object_id":"A","observed_at":"2026-01-03","display_condition":"x"}],"signals":[],"opportunity_window":{"deployment_days":1,"conservative_remaining_days":2}}
  self.assertEqual(evaluate(d)["posture"],"Blocked")
 def test_window_closes_before_deployment(self):
  s=[{"object_id":"A","observed_at":f"2026-01-0{i}","display_condition":"x"} for i in range(1,4)]
  d={"object_id":"A","snapshots":s,"signals":[{"id":"p","value":10,"baseline":0,"threshold":2,"consecutive_confirmations":2,"evidence_type":"direct"}],"opportunity_window":{"deployment_days":20,"conservative_remaining_days":5}}
  self.assertEqual(evaluate(d)["posture"],"Watch")
if __name__=="__main__":unittest.main(verbosity=2)
