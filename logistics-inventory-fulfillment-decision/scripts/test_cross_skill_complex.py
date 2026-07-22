#!/usr/bin/env python3
import json,unittest
from pathlib import Path
from decision_state import impacted
P=Path(__file__).parent.parent.parent/"evaluations/d07/cross-skill-complex-scenarios.json"

class CrossSkill(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.rows=json.loads(P.read_text(encoding="utf-8"))
 def test_lifd_leads_and_owner_boundaries_exist(self):
  self.assertGreaterEqual(len(self.rows),10)
  for r in self.rows:
   self.assertEqual(r["primary"],"LIFD");self.assertTrue(r["participants"]);self.assertTrue(r["proposed"]);self.assertTrue(r["forbidden"])
 def test_partial_failure_conflict_and_multidimensional_exist(self):
  self.assertTrue(any("partial_failure" in r for r in self.rows));self.assertTrue(any("conflict" in r for r in self.rows))
  complex_case=max(self.rows,key=lambda r:len(r["changed_fields"]))
  self.assertGreaterEqual(len(complex_case["changed_fields"]),6)
  for m in ["forecast","replenishment","allocation","routing","promising","capacity","reverse_exit"]:self.assertIn(m,impacted(complex_case["changed_fields"]))
 def test_redlines_cannot_be_empty_or_self_approved(self):
  for r in self.rows:
   self.assertFalse(any("LIFD批准" in x for x in r["proposed"]));self.assertFalse(set(r["proposed"]) & set(r["forbidden"]))

if __name__=="__main__":unittest.main(verbosity=2)
