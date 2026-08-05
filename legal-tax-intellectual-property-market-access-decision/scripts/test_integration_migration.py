#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; spec=importlib.util.spec_from_file_location("v",ROOT/"scripts/validate_integration_migration.py"); v=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(v)

class IntegrationMigrationTest(unittest.TestCase):
    def test_current_adapter_is_fail_closed(self):
        adapter=v.load(ROOT.parent/"governance/erdg/adapters/legal-tax-intellectual-property-market-access-decision/adapter.json"); self.assertEqual(v.validate_adapter(adapter),[])
        adapter["external_write"]=True; self.assertIn("adapter cannot write externally",v.validate_adapter(adapter))
    def test_partial_response_requires_explicit_fields(self):
        response={"contract":"D05-CONSUMER-RESPONSE-DRAFT-1","response_id":"R1","message_id":"M1","consumer_domain":"D03","status":"partially_accepted","accepted_fields":["claim"],"rejected_fields":["material"],"reasons":["version mismatch"],"recompute_scope":["material"],"current_state_updated":True}
        self.assertEqual(v.validate_response(response),[]); response["rejected_fields"]=[]; self.assertTrue(v.validate_response(response))
    def test_pending_migration_stays_rollback_ready(self):
        migration=v.load(ROOT/"evaluations/migration-map.json"); self.assertEqual(v.validate_migration(migration),[])
        migration["rollback_status"]="not_required"; self.assertIn("unaccepted consumers require rollback readiness",v.validate_migration(migration))
    def test_safety_field_cannot_be_lossy_and_ceiling_cannot_rise(self):
        migration=v.load(ROOT/"evaluations/migration-map.json"); migration["mappings"][0]["classification"]="lossy"; migration["action_ceiling_comparison"]="higher"
        errors=v.validate_migration(migration); self.assertIn("safety critical mappings must be lossless",errors); self.assertIn("migration cannot raise or obscure action ceiling",errors)

if __name__=="__main__": unittest.main(verbosity=2)
