#!/usr/bin/env python3
import importlib.util,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]; s=importlib.util.spec_from_file_location("v",R/"scripts/validate_l4_replays.py"); v=importlib.util.module_from_spec(s); s.loader.exec_module(v)
class T(unittest.TestCase):
 def test_empty_template_blocks(self): self.assertIn("minimum authorized replay count not met",v.validate(json.loads((R/"evaluations/historical-replay-template.json").read_text())))
 def test_synthetic_cannot_pass(self):
  c={"case_id":"1","authorization_ref":"a","deidentified":True,"object_hash":"a"*64,"jurisdictions":["US"],"topics":["tax"],"input_hash":"b"*64,"output_hash":"c"*64,"observed_outcome_ref":"o","independent_reviewer_ref":"r","review_decision":"approved","signed_at":"2026-08-05T00:00:00Z","synthetic":True}; x={"minimum_authorized_cases":1,"production_ready":False,"cases":[c]}; self.assertTrue(v.validate(x))
if __name__=="__main__": unittest.main(verbosity=2)
