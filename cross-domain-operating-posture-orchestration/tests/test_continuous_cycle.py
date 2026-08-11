#!/usr/bin/env python3
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from copo import *  # noqa
class TestContinuousCycle(unittest.TestCase):
 def state(self):return {"cycle_id":"C1","object_version":2,"state_version":1,"events":[],"state_hash":"a"*64}
 def event(self,mid="M1",version=2):return {"message_id":mid,"cycle_id":"C1","object_version":version,"external_write":False}
 def test_all_thirteen_professional_receipts_are_preservable(self):
  state=self.state()
  for i in range(1,14):state=apply_cycle_event(state,self.event(f"M-D{i:02d}"))
  self.assertEqual(len(state["events"]),13);self.assertEqual(state["state_version"],14)
 def test_duplicate_message_is_idempotent(self):
  once=apply_cycle_event(self.state(),self.event());twice=apply_cycle_event(once,self.event());self.assertEqual(once,twice)
 def test_same_message_id_with_different_content_is_rejected(self):
  once=apply_cycle_event(self.state(),self.event())
  changed=self.event();changed["value"]="tampered"
  with self.assertRaisesRegex(CopoError,"COPO_PACKET_HASH_MISMATCH"):apply_cycle_event(once,changed)
 def test_old_version_late_event_is_rejected(self):
  with self.assertRaisesRegex(CopoError,"COPO_STALE_VERSION"):apply_cycle_event(self.state(),self.event(version=1))
 def test_scope_change_creates_child_cycle(self):self.assertTrue(requires_child_cycle({"market"}));self.assertTrue(requires_child_cycle({"owner_decision"}))
 def test_formatting_change_does_not_create_child_cycle(self):self.assertFalse(requires_child_cycle({"formatting","explanation"}))
 def test_impact_closure_preserves_unaffected_consumers(self):self.assertEqual(impact_closure({"R-D06"},{"R-D06":["P1"],"P1":["V1"],"R-D08":["V2"]}),["P1","R-D06","V1"])
 def test_outcome_replay_requires_approved_actions(self):
  replay={"owner_action_refs":["A2"],"observed_outcomes":["O1"],"incidents":[],"external_write":False}
  with self.assertRaisesRegex(CopoError,"COPO_SOVEREIGNTY_OVERREACH"):validate_outcome_replay(replay,{"A1"})
 def test_incident_only_replay_is_valid(self):validate_outcome_replay({"owner_action_refs":[],"observed_outcomes":[],"incidents":["I1"],"external_write":False},set())
 def test_empty_replay_fails(self):
  with self.assertRaisesRegex(CopoError,"COPO_SCOPE_MISSING"):validate_outcome_replay({"owner_action_refs":[],"observed_outcomes":[],"incidents":[],"external_write":False},set())
if __name__=="__main__":unittest.main(verbosity=2)
