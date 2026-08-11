#!/usr/bin/env python3
from __future__ import annotations
import copy, json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"));sys.path.insert(0,str(ROOT/"tests"))
from copo import TRUSTED_LEDGER, governance_metadata, route_scenario  # noqa:E402
from validate_decision_contract import validate_bundle  # noqa:E402
from test_copo import receipt, scope_fixture  # noqa:E402

class DecisionBundleTest(unittest.TestCase):
    def bundle(self):
        route=route_scenario("profit_deterioration","S1");route["governance"]=governance_metadata("D14","draft","2026-08-11T00:00:00Z","route")
        receipts=[receipt(x) for x in route["required_owners"]]
        return {"scope":scope_fixture(),"route":route,"receipts":receipts,"trusted_ledger":copy.deepcopy(TRUSTED_LEDGER),"gates":{x:"passed" for x in route["gates"]},"f02_comparability":"comparable","requested_posture":"repair","owner_actions":[],"now":"2026-08-11T00:00:00Z","external_write":False}
    def run_bundle(self,bundle):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"bundle.json";path.write_text(json.dumps(bundle));return validate_bundle(path)
    def test_complete_bundle_passes(self):self.assertEqual(self.run_bundle(self.bundle()),[])
    def test_invalid_scope_cannot_bypass_bundle_validator(self):
        bundle=self.bundle();bundle["scope"]["time"]["baseline"]={"start":"apple","end":"banana"}
        self.assertTrue(any("schema" in x for x in self.run_bundle(bundle)))
    def test_caller_cannot_weaken_authoritative_route(self):
        bundle=self.bundle();bundle["route"].update({"required_owners":["D06"],"conditional_owners":[],"gates":["FAKE_GATE"],"dependencies":{"D06":[]}});bundle["receipts"]=[receipt("D06")];bundle["gates"]={"FAKE_GATE":"passed"}
        self.assertTrue(any("authoritative scenario contract" in x for x in self.run_bundle(bundle)))
    def test_signed_hash_covers_approved_action_content(self):
        bundle=self.bundle();bundle["receipts"][0]["accepted_fields"].append("UNAPPROVED-ACTION")
        self.assertTrue(any("packet hash is not bound" in x for x in self.run_bundle(bundle)))
    def test_forged_self_consistent_ledger_fails_signature(self):
        bundle=self.bundle();bundle["trusted_ledger"]["entries"][0]["packet_hash"]="b"*64
        self.assertTrue(any("hash mismatch" in x or "signature invalid" in x for x in self.run_bundle(bundle)))

if __name__=="__main__":unittest.main(verbosity=2)
