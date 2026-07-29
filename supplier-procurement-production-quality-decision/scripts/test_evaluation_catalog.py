#!/usr/bin/env python3
import importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location("v",ROOT/"scripts/validate_evaluation_catalog.py");v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
r_spec=importlib.util.spec_from_file_location("r",ROOT/"scripts/run_evaluation_catalog.py");r=importlib.util.module_from_spec(r_spec);r_spec.loader.exec_module(r)
class CatalogTest(unittest.TestCase):
 def test_catalog(self):self.assertEqual(v.validate(json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text())),[])
 def test_all_160_execute(self):
  out=r.run(json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text()));self.assertEqual((out["passed"],out["total"],out["failed"]),(160,160,[]))
 def test_duplicate_fails(self):
  d=json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text());d["cases"][1]["id"]=d["cases"][0]["id"];self.assertIn("duplicate_ids",v.validate(d))
 def test_multiturn_fails(self):
  d=json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text());next(x for x in d["cases"] if x["group"]=="multi_turn")["turns"]=3;self.assertIn("multiturn_four_turns_required",v.validate(d))
if __name__=="__main__":unittest.main(verbosity=2)
