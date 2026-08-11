import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from lcca_common import canonical_hash,LCCAError
from convert_quantity import convert
from grade_transferability import grade
from evaluate_comparability import evaluate
from build_localization_handoff import build
class PropertyTests(unittest.TestCase):
 def test_hash_order_invariant(self): self.assertEqual(canonical_hash({'b':2,'a':1}),canonical_hash({'a':1,'b':2}))
 def test_round_trip_bounded(self):
  a=convert({'conversion_type':'unit','value':'10','source_unit':'kg','target_unit':'lb','precision':'0.000001','external_write':False});b=convert({'conversion_type':'unit','value':a['value'],'source_unit':'lb','target_unit':'kg','precision':'0.000001','external_write':False});self.assertLessEqual(abs(float(b['value'])-10),0.000001)
 def test_redline_monotonic(self):
  base={'assessment_status':'assessed','target_evidence':True,'parameter_difference':True,'external_write':False};self.assertEqual(grade(base)['grade'],'L3');self.assertEqual(grade({**base,'redline_conflict':True})['grade'],'L1')
 def test_unresolved_difference_never_aggregates(self):
  l={'metric_id':'x','unit':'kg','currency':None,'tax_basis':None,'time_window':'a','object_granularity':'sku'};r={**l,'unit':'lb'};self.assertFalse(evaluate({'left':l,'right':r,'external_write':False})['aggregation_allowed'])
 def test_same_language_alone_does_not_transfer(self): self.assertEqual(grade({'assessment_status':'assessed','target_evidence':False,'same_language':True,'external_write':False})['grade'],'L2')
 def test_write_mutation_blocked(self):
  with self.assertRaises(LCCAError): build({'external_write':True})
if __name__=='__main__':unittest.main()
