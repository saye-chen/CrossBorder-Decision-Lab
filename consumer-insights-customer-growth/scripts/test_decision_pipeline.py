#!/usr/bin/env python3
import unittest
from evaluate_growth_decision import evaluate
def base():
 return {"object_id":"c1","as_of_time":"2026-01-01","purpose":"retention","identity":{"grain":"person","confidence":1},"consent":{"purpose_allowed":True,"not_withdrawn":True,"not_unsubscribed":True,"retention_valid":True},"data_quality":{"events_reconciled":True,"revenue_reconciled":True,"no_future_leakage":True},"analysis_level":"descriptive","action":{"frequency_ok":True,"inventory_ok":True,"market_allowed":True,"fairness_ok":True,"sensitive_event_clear":True}}
class GrowthDecisionPipeline(unittest.TestCase):
 def test_descriptive_cannot_contact_without_incrementality(self):self.assertEqual(evaluate(base())["decision"],"No contact")
 def test_frequency_failure_selects_no_action(self):
  d=base();d["action"]["frequency_ok"]=False;self.assertEqual(evaluate(d)["eligible_actions"],[])
if __name__=="__main__":unittest.main(verbosity=2)
