import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from lcca_common import LCCAError
from validate_scope import validate
from evaluate_dynamic_fact import evaluate
from convert_quantity import convert
from evaluate_comparability import evaluate as compare
from grade_transferability import grade
from build_localization_handoff import build

class CoreTests(unittest.TestCase):
 def test_scope(self):
  p={'object_id':'S1','country_code':'US','jurisdiction_id':'US-CA','platform_id':'amazon','platform_site_id':'amazon.com','locale':'en-US','decision_time':'2026-08-11T00:00:00Z','external_write':False};self.assertEqual(validate(p)['status'],'qualified')
  p.pop('locale');self.assertRaises(LCCAError,validate,p)
 def test_dynamic_fact(self):
  p={'object_id':'F1','decision_time':'2026-08-11T00:00:00Z','valid_from':'2026-08-01T00:00:00Z','valid_until':'2026-08-20T00:00:00Z','recorded_at':'2026-08-02T00:00:00Z','source':{'source_id':'official','content_fingerprint':'a'*64},'external_write':False};self.assertEqual(evaluate(p)['status'],'qualified')
  p['decision_time']='2026-09-01T00:00:00Z';self.assertEqual(evaluate(p)['status'],'expired')
 def test_decimal_conversion_and_tax_gate(self):
  p={'conversion_type':'currency','value':'10.00','source_unit':'USD','target_unit':'CNY','base_currency':'USD','quote_currency':'CNY','rate':'7.1234','precision':'0.01','external_write':False};self.assertEqual(convert(p)['value'],'71.23')
  p={'conversion_type':'tax_basis','value':'100','source_unit':'net','target_unit':'gross','rate':'0.2','precision':'0.01','direction':'exclusive_to_inclusive','external_write':False};self.assertRaises(LCCAError,convert,p)
 def test_comparability_not_causal(self):
  row={'metric_id':'profit','unit':'currency','currency':'USD','tax_basis':'exclusive','time_window':'2026-07','object_granularity':'sku'};out=compare({'left':row,'right':dict(row),'external_write':False});self.assertTrue(out['aggregation_allowed']);self.assertFalse(out['causal_claim'])
 def test_transfer_grades(self):
  base={'assessment_status':'assessed','target_evidence':True,'external_write':False};self.assertEqual(grade({**base,'redline_conflict':True})['grade'],'L1');self.assertEqual(grade({**base,'parameter_difference':True})['grade'],'L3');self.assertEqual(grade({**base,'same_frozen_scope':True,'same_version':True,'evidence_current':True})['grade'],'L4')
  self.assertIsNone(grade({'assessment_status':'not_assessed','external_write':False})['grade'])
 def test_handoff_never_upgrades(self):
  p={'handoff_id':'H1','source_domain':'D06','target_domain':'D01','scope_ref':'S1','comparability_status':'comparable','transfer_status':'L3','source_action_ceiling':'reversible_action','f02_action_ceiling':'controlled_test','external_write':False};out=build(p);self.assertEqual(out['action_ceiling'],'controlled_test');self.assertFalse(out['claim_upgrade_allowed'])
 def test_external_write_blocked(self):
  self.assertRaises(LCCAError,grade,{'assessment_status':'not_assessed','external_write':True})
if __name__=='__main__':unittest.main()
