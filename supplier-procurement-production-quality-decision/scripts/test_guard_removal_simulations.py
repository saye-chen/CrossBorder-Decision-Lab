#!/usr/bin/env python3
import importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(name,file):
 s=importlib.util.spec_from_file_location(name,ROOT/"scripts"/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
contract=load("contract","validate_decision_contract.py");cross=load("cross","validate_cross_domain_envelope.py");core=load("core","sppq_core.py");continuity=load("continuity","update_continuous_decision.py");catalog=load("catalog","validate_evaluation_catalog.py")
def decision():
 return {"runtime_version":"SPPQ-2026.07","erdg_contract":"ERDG-CONTRACT-2026.07","decision_id":"D1","decision_type":"production_release","decision_owner":"supplier-procurement-production-quality-decision","object":{"object_id":"O","object_version":"v1","as_of_time":"2026-07-29T00:00:00+08:00"},"status":"validated","evidence":[{"id":"E"}],"calculations":[],"gates":{"identity":True,"sovereignty":True,"version":True,"evidence":True,"segregation":True,"external_action":False,"compliance":"passed"},"lineage":{"input_hash":"a"*64,"output_hash":"b"*64},"external_write":False,"production_ready":False}
class GuardRemovalSimulations(unittest.TestCase):
 def test_remove_owner_guard_fails(self):
  d=decision();d["decision_owner"]="D03";self.assertTrue(contract.validate(d))
 def test_remove_compliance_guard_fails(self):
  d=decision();d["gates"]["compliance"]="blocked";self.assertIn("compliance_gate_required",contract.validate(d))
 def test_remove_segregation_guard_fails(self):
  d=decision();d["gates"]["segregation"]=False;self.assertIn("validated_requires_segregation",contract.validate(d))
 def test_external_write_guard_fails(self):
  d=decision();d["external_write"]=True;self.assertTrue(contract.validate(d))
 def test_critical_defect_guard_is_specific(self):
  out=core.scenario_gate({"critical_defects":1,"independent_results":["safe"]});self.assertEqual(out["failures"],["critical_defect"]);self.assertEqual(out["preserved_results"],["safe"])
 def test_correlated_supply_guard_is_specific(self):
  out=core.scenario_gate({"sources_independent":False});self.assertEqual(out["failures"],["correlated_supply_sources"])
 def test_shipped_action_cannot_be_silently_rebased(self):
  state={"object_id":"O","current_version":"v1","current_effective_decision":{"id":"D"},"history":[],"open_gates":[],"active_actions":[{"action_id":"A","status":"shipped","depends_on":["spec"]}],"accepted_fields":[],"invalidated_fields":[],"recompute_scope":[]}
  out=continuity.update({"object_id":"O","expected_version":"v1","delta_type":"Rebase","state":state,"new_version":"v2","new_decision":{"id":"D2"},"changed_fields":["spec"],"all_fields":["spec","supplier"],"impact_map":{"spec":["batch"]}})
  self.assertEqual(out["recovery_required"][0]["action_id"],"A");self.assertIn("REALITY_RECOVERY",out["open_gates"])
 def test_catalog_without_executable_binding_fails(self):
  d=json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text());d["cases"][0].pop("executable");self.assertIn("every_case_must_be_executable",catalog.validate(d))
if __name__=="__main__":unittest.main(verbosity=2)
