#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("wp3",ROOT/"scripts/validate_wp3_package.py")
WP3=importlib.util.module_from_spec(SPEC);assert SPEC and SPEC.loader;SPEC.loader.exec_module(WP3)

def good():
    return {
      "input":{"input_id":"i1","object_id":"p1","object_version":"v1","country":"US","platform":"Amazon","product_lifecycle_stage":"PLC3","decision_question":"freeze definition?","input_level":"M2","fields":[{"field_id":"weight","value_state":"observed","value":"1.2","unit":"kg","source_id":"s1"}],"source_ids":["s1"],"as_of_time":"2026-07-28T00:00:00Z"},
      "evidence":[{"evidence_id":"e1","object_id":"p1","source_type":"authorized_first_party","processing_status":"verified","source_ref":"fixture:e1","observed_at":"2026-07-28T00:00:00Z","expires_at":None,"fingerprint":"a"*64,"allowed_uses":["product_definition"],"forbidden_uses":["causal_claim"]}],
      "claim":[{"claim_id":"c1","owner_domain":"product-innovation-product-management","object_id":"p1","state":"validated","grade":"descriptive","evidence_ids":["e1"],"allowed_uses":["product_definition"],"forbidden_uses":["external_execution"],"weakest_assumption":"sample represents target","falsification_condition":"target failure"}],
      "calculation":[{"calculation_id":"k1","calculator":"fixture","calculator_version":"1","input_ids":["i1"],"input_hash":"b"*64,"output_hash":"c"*64,"status":"complete","units":{"weight":"kg"},"result":{"feasible":True}}],
      "decision":{"decision_id":"d1","owner_domain":"product-innovation-product-management","object_id":"p1","object_version":"v1","decision_question":"freeze definition?","state":"validated","version":"v1","evidence_ids":["e1"],"claim_ids":["c1"],"calculation_ids":["k1"],"hard_gates":[{"gate_id":"identity","status":"passed"}],"no_action":{"effect":"delay"},"candidates":[{"id":"recommended"}],"actions":[{"owner":"product"}],"success_conditions":["verification passes"],"stop_conditions":["redline"],"rollback":{"version":"v0"},"external_write":False}
    }

class WP3Contracts(unittest.TestCase):
    def test_valid_package(self): self.assertEqual(WP3.validate(good()),[])
    def test_causal_is_blocked_before_f01(self):
        x=good();x["claim"][0]["grade"]="causal";self.assertTrue(any("causal_blocked" in e for e in WP3.validate(x)))
    def test_open_gate_cannot_validate(self):
        x=good();x["decision"]["hard_gates"][0]["status"]="unknown";self.assertIn("decision:unresolved_gate_must_block",WP3.validate(x))
    def test_missing_is_not_zero(self):
        x=good();x["input"]["fields"][0].update(value_state="missing",value=0);self.assertTrue(any("silently_zero" in e for e in WP3.validate(x)))
    def test_calculation_cannot_be_evidence_source(self):
        x=good();x["evidence"][0]["source_type"]="calculation";self.assertTrue(any("not one of" in e for e in WP3.validate(x)))

if __name__=="__main__": unittest.main(verbosity=2)
