import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from backend_contract import require_verified_backend
from build_causal_handoff import build_causal_handoff
from ecae_common import ECAEError
from grade_causal_claim import grade_causal_claim
from validate_causal_handoff import validate_causal_handoff
from validate_randomization import validate_randomization


def base_grade():
    return {"question_type":"causal","design":"two_arm_randomized","identification":{"potential_outcomes_contract":True,"causal_graph_contract":True,"estimand_registered":True,"identification_statement":True},"eligibility_gates":{f"Q{i}":"pass" for i in range(1,11)},"capability_tier":"native_executable","diagnostics":[],"sensitivity_status":"pass","precision_status":"decision_adequate","reproducibility_status":"deterministic_replay_pass","economic_status":"value_supported","economic_parameters_qualified":True,"review_status":"independent_accepted","data_status":"mature"}


class MutationTests(unittest.TestCase):
    def test_M01_delete_identification_gate_is_killed(self):
        value=base_grade(); value["identification"].pop("causal_graph_contract")
        self.assertLessEqual(int(grade_causal_claim(value)["causal_evidence_grade"][-1]),3)

    def test_M02_ce3_cannot_be_upgraded_by_business_value(self):
        value=base_grade(); value["question_type"]="attributed"
        self.assertEqual(grade_causal_claim(value)["causal_evidence_grade"],"CE3")

    def test_M03_ignore_srm_is_killed(self):
        result=validate_randomization({"observed_counts":{"c":800,"t":200},"expected_probabilities":{"c":0.5,"t":0.5},"assignment_proof":{"proof_type":"hash","value":"x"}})
        self.assertEqual(result["claim_impact"],"block_causal_until_resolved")

    def test_M08_remove_sensitivity_is_killed(self):
        value=base_grade(); value["sensitivity_status"]="missing"
        self.assertEqual(grade_causal_claim(value)["causal_evidence_grade"],"CE3")

    def test_M09_expired_handoff_is_killed(self):
        result={"object_id":"ECAE-RESULT-MUTATION","status":"reviewed","causal_evidence_grade":"CE4","claim_ceiling":"CE4","estimand_ref":"ECAE-ESTIMAND-MUTATION","allowed_wording":[],"prohibited_wording":["universal"],"reproducibility_bundle_ref":"ECAE-REPRO-MUTATION","review_status":"internal_reviewed","limitations":[]}
        handoff=build_causal_handoff({"causal_result":result,"consumer":"D08","created_at":"2026-01-01T00:00:00Z","expires_at":"2026-02-01T00:00:00Z","applicability":{"population":"p","platforms":["x"],"countries":["US"],"time_window":"w","treatment_version":"v"},"invalidation_triggers":["x"],"recompute_triggers":["y"]})
        with self.assertRaises(ECAEError) as context: validate_causal_handoff({"handoff":handoff,"consumer":"D08","as_of_time":"2026-08-10T00:00:00Z"})
        self.assertEqual(context.exception.code,"HANDOFF_EXPIRED")

    def test_M10_backend_failure_never_falls_back(self):
        with self.assertRaises(ECAEError) as context: require_verified_backend("observational_dml")
        self.assertEqual(context.exception.code,"BACKEND_UNAVAILABLE")


if __name__=="__main__": unittest.main()
