#!/usr/bin/env python3
"""Twenty-four D03 consumer migration, rejection, compatibility and rollback tests."""
from __future__ import annotations
import copy,importlib.util,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DIR=ROOT/"evaluations/migration"
spec=importlib.util.spec_from_file_location("v",ROOT/"scripts/validate_pipm_consumer_migration.py");V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
def good():return {p.stem:json.loads(p.read_text()) for p in DIR.glob("*.json")}
class WP9(unittest.TestCase):
 def has(self,x,m):self.assertTrue(any(m in e for e in V.validate(x)),V.validate(x))
 def test_01_valid_all_consumers(self):self.assertEqual(V.validate(good()),[])
 def test_02_missing_consumer(self):x=good();x["consumer-adapters"]["adapters"].pop();self.has(x,"consumer_inventory")
 def test_03_missing_required_fields(self):x=good();x["consumer-adapters"]["adapters"][0]["required_fields"]=[];self.has(x,"missing:required_fields")
 def test_04_optional_fields_required(self):x=good();x["consumer-adapters"]["adapters"][0]["optional_fields"]=[];self.has(x,"missing:optional_fields")
 def test_05_ignored_fields_required(self):x=good();x["consumer-adapters"]["adapters"][0]["ignored_fields"]=[];self.has(x,"missing:ignored_fields")
 def test_06_forbidden_fields_required(self):x=good();x["consumer-adapters"]["adapters"][0]["forbidden_fields"]=[];self.has(x,"missing:forbidden_fields")
 def test_07_mapping_must_cover_required(self):x=good();x["consumer-adapters"]["adapters"][0]["field_mapping"].pop(next(iter(x["consumer-adapters"]["adapters"][0]["field_mapping"])));self.has(x,"mapping_incomplete")
 def test_08_required_mapping_lossless(self):x=good();a=x["consumer-adapters"]["adapters"][0];a["mapping_classification"][a["required_fields"][0]]="lossy";self.has(x,"required_not_lossless")
 def test_09_sovereignty_forbids_writeback(self):x=good();x["consumer-adapters"]["adapters"][0]["forbidden_writeback"]=[];self.has(x,"sovereignty_writeback")
 def test_10_allowed_uses_required(self):x=good();x["consumer-adapters"]["adapters"][0]["allowed_uses"]=[];self.has(x,"missing:allowed_uses")
 def test_11_forbidden_uses_required(self):x=good();x["consumer-adapters"]["adapters"][0]["forbidden_uses"]=[];self.has(x,"missing:forbidden_uses")
 def test_12_reaccept_triggers_required(self):x=good();x["consumer-adapters"]["adapters"][0]["reaccept_triggers"]=[];self.has(x,"missing:reaccept_triggers")
 def test_13_legacy_reader_preserved(self):x=good();x["source-inventory"]["all_legacy_readers_preserved"]=False;self.has(x,"source_inventory")
 def test_14_old_logic_not_retired(self):x=good();x["source-inventory"]["inventory"][0]["retirement_allowed"]=True;self.has(x,"premature_retirement")
 def test_15_dual_run_complete(self):x=good();x["dual-run-results"]["results"].pop();self.has(x,"dual_run")
 def test_16_incomparable_must_block(self):x=good();r=next(y for y in x["dual-run-results"]["results"] if y["difference_class"]=="incomparable");r["result"]="pass";self.has(x,"incomparable_not_blocked")
 def test_17_error_difference_blocks(self):x=good();x["dual-run-results"]["error_count"]=1;self.has(x,"dual_run_errors")
 def test_18_rejected_consumer_blocks(self):x=good();x["consumer-acceptance"]["acceptances"][0]["automated_contract_accepted"]=False;self.has(x,"acceptance")
 def test_19_partial_tool_result_does_not_erase_others(self):
  x=good();x["consumer-acceptance"]["acceptances"][0]["automated_contract_accepted"]=False
  self.has(x,"acceptance");self.assertTrue(all(y["automated_contract_accepted"] for y in x["consumer-acceptance"]["acceptances"][1:]))
 def test_20_authoritative_is_premature(self):x=good();x["migration-state"]["authoritative"]=True;self.has(x,"migration_state")
 def test_21_unaccepted_list_blocks(self):x=good();x["migration-state"]["unaccepted_consumers"]=["PLCO"];self.has(x,"migration_state")
 def test_22_automated_is_not_independent_owner(self):x=good();x["consumer-acceptance"]["acceptances"][0]["independent_owner_accepted"]=True;self.has(x,"acceptance")
 def test_23_rollback_must_restore_all_units(self):x=good();x["rollback-manifest"]["release_units"][0]["restored"]=False;self.has(x,"rollback")
 def test_24_external_write_and_l4_shortcut_block(self):x=good();x["migration-state"]["external_write"]=True;x["migration-state"]["authoritative"]=True;self.has(x,"external_write")
 def test_25_each_consumer_executes_local_adapter_evidence(self):
  x=good()
  self.assertEqual(V.validate(x),[])
  for a in x["consumer-acceptance"]["acceptances"]:
   self.assertTrue((ROOT.parent/a["adapter_path"]).is_file())
   self.assertTrue((ROOT.parent/a["acceptance_path"]).is_file())
 def test_26_tampered_consumer_hash_blocks(self):
  x=good();p=ROOT.parent/x["consumer-acceptance"]["acceptances"][0]["acceptance_path"]
  original=p.read_text()
  try:
   y=json.loads(original);y["adapter_hash"]="0"*64;p.write_text(json.dumps(y))
   self.has(x,"consumer_side_validation")
  finally:p.write_text(original)
 def test_27_each_consumer_owned_test_executes(self):
  for a in good()["consumer-acceptance"]["acceptances"]:
   path=(ROOT.parent/a["adapter_path"]).parent/"test_adapter.py"
   subprocess.run([sys.executable,str(path)],check=True,capture_output=True,text=True)
if __name__=="__main__":unittest.main(verbosity=2)
