#!/usr/bin/env python3
import importlib.util,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]; s=importlib.util.spec_from_file_location("v",R/"scripts/validate_consumer_acceptance.py"); v=importlib.util.module_from_spec(s); s.loader.exec_module(v)
class T(unittest.TestCase):
 def data(self): return json.loads((R/"evaluations/consumer-contract-acceptance.json").read_text())
 def test_three_consumers_are_machine_verified_but_owner_pending(self): self.assertEqual(v.validate(self.data()),[]); self.assertTrue(all(x["independent_owner_status"]=="pending" for x in self.data()["records"]));self.assertTrue(all(x["automated_contract_status"]=="verified_by_consumer_validator" for x in self.data()["records"]))
 def test_sovereignty_removal_fails(self): x=self.data(); x["records"][0]["preserved_sovereignty"]=[]; self.assertIn("D03 contract lacks fields or sovereignty",v.validate(x))
 def test_external_write_fails(self): x=self.data(); x["records"][2]["external_write"]=True; self.assertIn("D08 external write forbidden",v.validate(x))
 def test_pending_owner_must_block(self): x=self.data(); x["next_stage_effect"]="allowed"; self.assertIn("pending owner acceptance must block next stage",v.validate(x))
if __name__=="__main__": unittest.main(verbosity=2)
