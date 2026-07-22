#!/usr/bin/env python3
import unittest,tempfile,hashlib
from pathlib import Path
from validate_historical_replay import run
def case(i,root,source="authorized_historical"):
 inp=root/f"in{i}.json";out=root/f"out{i}.json";inp.write_text(f'{{"case":{i}}}');out.write_text(f'{{"result":{i}}}')
 h=lambda p:"sha256:"+hashlib.sha256(p.read_bytes()).hexdigest()
 return {"case_id":f"H{i}","object_id":f"SKU{i}|US|W1","as_of_time":"2026-01-01T00:00:00+00:00","input_file":inp.name,"input_hash":h(inp),"model_version":"LIFD-2026.04","decision":"constrain","observed_outcome":"no_oversell","outcome_time":"2026-02-01T00:00:00+00:00","outcome_file":out.name,"outcome_hash":h(out),"decision_correct":True,"calibration_notes":"capacity gate matched outcome","source_type":source,"authorization_ref":f"AUTH-{i}","source_system":"authorized_warehouse_export","reviewer":"independent-reviewer","reviewed_at":"2026-02-02T00:00:00+00:00"}
class Replay(unittest.TestCase):
 def test_empty_or_synthetic_cannot_claim_production_ready(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);self.assertFalse(run({"evidence_root":td,"cases":[]})["production_ready"]);self.assertFalse(run({"evidence_root":td,"cases":[case(1,root,"synthetic"),case(2,root,"synthetic"),case(3,root,"synthetic")]})["production_ready"])
 def test_three_authorized_complete_cases_pass(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);self.assertTrue(run({"evidence_root":td,"cases":[case(1,root),case(2,root),case(3,root)]})["production_ready"])
 def test_missing_outcome_evidence_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);rows=[case(1,root),case(2,root),case(3,root)];rows[1]["outcome_hash"]="";self.assertFalse(run({"evidence_root":td,"cases":rows})["production_ready"])
if __name__=="__main__":unittest.main(verbosity=2)
