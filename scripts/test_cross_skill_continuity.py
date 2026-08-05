#!/usr/bin/env python3
import importlib.util,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]; s=importlib.util.spec_from_file_location("c",R/"scripts/cross_skill_continuity.py"); c=importlib.util.module_from_spec(s); s.loader.exec_module(c)
def load(path,name): q=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(q);q.loader.exec_module(m);return m
class T(unittest.TestCase):
 def fixture(self):return json.loads((R/"evaluations/cross-skill-continuity-scenarios.json").read_text())
 def test_all_bidirectional_feedback_routes_are_selective(self):
  f=self.fixture();self.assertEqual(set(f["required_feedback_events"]),set(c.FEEDBACK_ROUTES))
  for event in f["required_feedback_events"]:
   out=c.impact(event,["investment_posture","specification","unrelated"]);self.assertTrue(out);self.assertTrue(all(x["reaccept"] and "unrelated" in x["preserved"] for x in out.values()))
 def test_all_state_transitions_have_effect_and_history(self):
  for old,new in self.fixture()["required_transitions"]: self.assertTrue(c.transition(old,new)["history_preserved"])
 def test_peer_conflict_uses_evidence_not_votes(self):
  claims=[{"id":"weak-majority-1","value":"go","object_match":True,"current":True,"reproducible":True,"evidence_grade":2,"independent_sources":1},{"id":"weak-majority-2","value":"go","object_match":True,"current":True,"reproducible":True,"evidence_grade":2,"independent_sources":1},{"id":"strong","value":"stop","object_match":True,"current":True,"reproducible":True,"evidence_grade":4,"independent_sources":2}]
  self.assertEqual(c.adjudicate(claims)["winner"],"strong");claims.append({"id":"redline","value":"blocked","object_match":True,"current":True,"reproducible":True,"evidence_grade":1,"independent_sources":1,"redline":True});self.assertEqual(c.adjudicate(claims)["state"],"blocked")
 def test_duplicate_late_timeout_and_partial_are_fail_closed(self):
  f=self.fixture();l=c.Ledger();self.assertEqual([l.receive(x) for x in f["message_sequence"]],f["expected_effects"]);self.assertEqual(l.current_versions["O1"],2)
 def test_recovery_requires_every_requirement(self):
  self.assertEqual(c.recovery(["retest","owner_accept"],["retest"])["state"],"blocked");self.assertEqual(c.recovery(["retest","owner_accept"],["retest","owner_accept"])["state"],"recovered")
 def test_parallel_fifty_objects_are_isolated_and_deterministic(self):
  ledger=c.Ledger()
  first=[ledger.receive({"message_id":f"M{i}","object_id":f"O{i}","version":2,"content_hash":f"h{i}","status":"contributed"}) for i in range(50)]
  late=[ledger.receive({"message_id":f"L{i}","object_id":f"O{i}","version":1,"content_hash":f"old{i}","status":"contributed"}) for i in range(50)]
  self.assertEqual(first,["accepted"]*50);self.assertEqual(late,["late_version_ignored"]*50);self.assertEqual(len(ledger.current_versions),50)
  self.assertEqual(ledger.receive({"message_id":"conflict","object_id":"O1","version":2,"content_hash":"different","status":"contributed"}),"same_version_conflict")
 def test_peer_tie_remains_inconclusive(self):
  claims=[{"id":"a","value":"go","object_match":True,"current":True,"reproducible":True,"evidence_grade":4,"independent_sources":2},{"id":"b","value":"stop","object_match":True,"current":True,"reproducible":True,"evidence_grade":4,"independent_sources":2}]
  self.assertEqual(c.adjudicate(claims)["reason"],"unresolved_peer_conflict")
 def test_d05_packets_execute_real_consumer_validators(self):
  packets=json.loads((R/"legal-tax-intellectual-property-market-access-decision/evaluations/d05-consumer-packets.json").read_text())["packets"]
  paths={"D03":R/"product-innovation-product-management/scripts/validate_d05_consumer.py","D04":R/"supplier-procurement-production-quality-decision/scripts/validate_d05_consumer.py","D08":R/"platform-store-listing-conversion/scripts/validate_d05_consumer.py"}
  for d,path in paths.items():self.assertEqual(load(path,d).validate(packets[d]),[],d)
  bad=dict(packets["D03"]);bad["d05_owned_decisions"]=["product_definition"];self.assertTrue(load(paths["D03"],"D03bad").validate(bad))
  bad=dict(packets["D04"]);bad["quality_gate"]="blocked";self.assertTrue(load(paths["D04"],"D04bad").validate(bad))
  bad=json.loads(json.dumps(packets["D08"]));bad["claims"][1]["publish"]=True;self.assertTrue(load(paths["D08"],"D08bad").validate(bad))
 def test_partial_failure_invalidates_only_dependent_claims(self):
  claims=[{"id":"inventory","depends_on":["LIFD"],"state":"validated"},{"id":"page","depends_on":["PLCO"],"state":"validated"},{"id":"combined","depends_on":["LIFD","PLCO"],"state":"validated"}]
  r=c.partial_failure(["LIFD"],claims);self.assertEqual(r["affected"],["combined","inventory"]);self.assertEqual(r["preserved"],["page"]);self.assertFalse(r["overall_pass"])
if __name__=="__main__":unittest.main(verbosity=2)
