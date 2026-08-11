import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from ecae_common import ECAEError
from validate_experiment_protocol import validate_protocol_bundle
from validate_state_transition import validate_transition


class ProtocolStateTests(unittest.TestCase):
    def valid_bundle(self):
        return json.loads((ROOT/"examples/valid/protocol-bundle.json").read_text())

    def test_valid_protocol_eligible(self):
        result=validate_protocol_bundle(self.valid_bundle())
        self.assertTrue(result["eligible_to_launch"])
        self.assertEqual(result["claim_ceiling"],"CE5")

    def test_critical_gate_fails_closed(self):
        value=self.valid_bundle()
        next(item for item in value["protocol"]["eligibility_gates"] if item["gate_id"]=="Q4")["status"]="unknown"
        result=validate_protocol_bundle(value)
        self.assertFalse(result["eligible_to_launch"])
        self.assertEqual(result["claim_ceiling"],"CE3")

    def test_noncritical_q7_failure_still_blocks_launch(self):
        value=self.valid_bundle()
        next(item for item in value["protocol"]["eligibility_gates"] if item["gate_id"]=="Q7")["status"]="fail"
        result=validate_protocol_bundle(value)
        self.assertFalse(result["eligible_to_launch"])
        self.assertIn("ALL_Q1_Q10_MUST_PASS_TO_LAUNCH",result["blockers"])

    def test_gate_without_evidence_rejected(self):
        value=self.valid_bundle()
        next(item for item in value["protocol"]["eligibility_gates"] if item["gate_id"]=="Q2")["evidence_refs"]=[]
        with self.assertRaises(ECAEError) as context: validate_protocol_bundle(value)
        self.assertEqual(context.exception.code,"GATE_EVIDENCE_INCOMPLETE")

    def test_bad_control_rejected(self):
        value=json.loads((ROOT/"examples/invalid/protocol-bad-control.json").read_text())
        with self.assertRaises(ECAEError) as context:
            validate_protocol_bundle(value)
        self.assertEqual(context.exception.code,"BAD_CONTROL")

    def test_verified_backend_design_cannot_launch_while_registry_is_unverified(self):
        value=self.valid_bundle()
        value["protocol"]["design"]="staggered_did"
        value["protocol"]["capability_tier"]="verified_backend"
        result=validate_protocol_bundle(value)
        self.assertFalse(result["eligible_to_launch"])
        self.assertEqual(result["backend_id"],"staggered_did")
        self.assertEqual(result["backend_status"],"installed_unverified")
        self.assertIn("VERIFIED_BACKEND_UNAVAILABLE",result["blockers"])

    def test_cannot_skip_preregistration(self):
        event={"from_status":"draft","to_status":"approved_to_launch","evidence_refs":["x"],"trigger":"skip","actor":"test","occurred_at":"2026-08-10T00:00:00Z","eligibility_passed":True}
        with self.assertRaises(ECAEError) as context:
            validate_transition(event)
        self.assertEqual(context.exception.code,"ILLEGAL_TRANSITION")

    def test_approved_launch_requires_eligibility(self):
        event={"from_status":"eligibility_checked","to_status":"approved_to_launch","evidence_refs":["x"],"trigger":"approval","actor":"test","occurred_at":"2026-08-10T00:00:00Z","eligibility_passed":False}
        with self.assertRaises(ECAEError) as context:
            validate_transition(event)
        self.assertEqual(context.exception.code,"ELIGIBILITY_NOT_PASSED")

    def test_valid_state_transition(self):
        event={"from_status":"eligibility_checked","to_status":"approved_to_launch","evidence_refs":["gate-report"],"trigger":"all gates pass","actor":"owner","occurred_at":"2026-08-10T00:00:00Z","eligibility_passed":True}
        self.assertTrue(validate_transition(event)["valid"])


if __name__=="__main__": unittest.main()
