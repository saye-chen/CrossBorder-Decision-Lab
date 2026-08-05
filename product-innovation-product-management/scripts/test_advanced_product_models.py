#!/usr/bin/env python3
import unittest
from evaluate_product_models import evaluate
class T(unittest.TestCase):
 def test_tolerance_stack_blocks_tail_failure(self):
  p={"model":"tolerance_stack","contributors":[{"id":"a","nominal":"10","minus":"0.10","plus":"0.10","unit":"mm"},{"id":"b","nominal":"5","minus":"0.05","plus":"0.05","unit":"mm"},{"id":"c","nominal":"2","minus":"0.03","plus":"0.03","unit":"mm"}],"assembly_min":"16.85","assembly_max":"17.15"};self.assertEqual(evaluate(p)["result"]["status"],"blocked")
 def test_risk_retirement_requires_current_evidence(self):
  p={"model":"mvp_risk_retirement","object_version":"v2","risks":[{"id":"thermal","critical":True,"test_state":"passed","evidence_id":"E1","object_version":"v1"}]};self.assertEqual(evaluate(p)["result"]["unresolved_critical"],["thermal"])
 def test_resource_roadmap_never_overcommits(self):
  p={"model":"resource_roadmap","capacity":{"engineering":"2"},"candidates":[{"id":"A","priority":"5","resource_needs":{"engineering":"2"}},{"id":"B","priority":"4","resource_needs":{"engineering":"1"}}]};r=evaluate(p)["result"];self.assertEqual(r["selected"],["A"]);self.assertEqual(r["deferred"],["B"])
if __name__=="__main__":unittest.main(verbosity=2)
