#!/usr/bin/env python3
import json,unittest
from pathlib import Path
from decision_state import impacted
ROOT=Path(__file__).parent.parent.parent
CH=ROOT/"logistics-inventory-fulfillment-decision/evaluations/multiturn-challenges.json";REPORTS=[ROOT/"evaluations/golden-reports/d07-full.md",ROOT/"evaluations/golden/d07-single.md"]

class MultiTurnReport(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.rows=json.loads(CH.read_text(encoding="utf-8"));cls.texts=[x.read_text(encoding="utf-8") for x in REPORTS]
 def test_six_consecutive_challenges_have_explicit_answers(self):
  self.assertGreaterEqual(len(self.rows),6)
  for text in self.texts:
   for r in self.rows:
    for phrase in r["must_answer"]: self.assertIn(phrase,text,f"{r['id']} missing {phrase}")
 def test_changed_inputs_have_recompute_scope(self):
  for r in self.rows:
   if r["changed_fields"]: self.assertTrue(impacted(r["changed_fields"]),r["id"])
 def test_report_is_not_only_positive_case(self):
  for text in self.texts:
   for phrase in ["部分失败","证据冲突","多维叠加","停止条件","回滚","退出"]:self.assertIn(phrase,text)

if __name__=="__main__":unittest.main(verbosity=2)
