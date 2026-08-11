import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from lcca_common import LCCAError
from evaluate_migration import evaluate
from evaluate_consumer_handoff import evaluate as consume
from evaluate_rollback import evaluate as rollback
class MigrationTests(unittest.TestCase):
 def payload(self):
  return {'field_mappings':[{'source_field':'country_code','target_field':'scope.country_code','loss':'none','criticality':'major'}],'dual_run':{'same_input_hash':'sha256:x','source_input_hash':'sha256:x','target_input_hash':'sha256:x'},'differences':[],'consumer_acceptance':[{'consumer_id':f'D{i:02d}','status':'accepted_controlled_pilot','rollback_verified':True,'production_accepted':False} for i in range(1,14)],'rollback':{'supported':True,'source_readable':True},'external_write':False}
 def test_cutover_ready_needs_all_consumers(self):
  p=self.payload();self.assertEqual(evaluate(p)['status'],'cutover_ready');p['consumer_acceptance'].pop();self.assertEqual(evaluate(p)['status'],'blocked')
 def test_material_critical_mapping_blocks(self):
  p=self.payload();p['field_mappings'][0]['loss']='material';self.assertEqual(evaluate(p)['status'],'blocked')
 def test_consumer_ceiling(self):
  h={'contract':'LCCA-HANDOFF-1.0','target_domain':'D01','claim_upgrade_allowed':False,'source_action_ceiling':'controlled_test','action_ceiling':'analysis_only','comparability_status':'comparable','external_write':False};a={'consumer_id':'D01','rollback_supported':True};self.assertEqual(consume({'consumer_id':'D01','handoff':h,'adapter':a,'external_write':False})['status'],'accepted_controlled_pilot');h['action_ceiling']='human_approved_execution';self.assertRaises(LCCAError,consume,{'consumer_id':'D01','handoff':h,'adapter':a,'external_write':False})
 def test_rollback_restores_state(self):
  p={'state':'cutover','source_readable':True,'source_snapshot_hash':'sha256:old','target_current_refs':['new'],'dependent_refs':['D01:x'],'external_write':False};out=rollback(p);self.assertEqual(out['state'],'rolled_back');self.assertEqual(out['restored_current_hash'],'sha256:old')
if __name__=='__main__':unittest.main()
