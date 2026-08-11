import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from build_causal_handoff import build_causal_handoff
from calculate_incremental_economics import calculate_incremental_economics
from ecae_common import ECAEError, content_hash
from grade_causal_claim import grade_causal_claim
from validate_schema import validate_object


def decision_grade_input():
    return {"question_type":"causal","design":"two_arm_randomized","identification":{"potential_outcomes_contract":True,"causal_graph_contract":True,"estimand_registered":True,"identification_statement":True},"eligibility_gates":{f"Q{i}":"pass" for i in range(1,11)},"capability_tier":"native_executable","diagnostics":[],"sensitivity_status":"pass","precision_status":"decision_adequate","reproducibility_status":"deterministic_replay_pass","economic_status":"value_supported","economic_parameters_qualified":True,"review_status":"independent_accepted","data_status":"mature"}


class GradeHandoffTests(unittest.TestCase):
    def test_ce5_requires_all_noncompensatory_gates(self):
        result=grade_causal_claim(decision_grade_input())
        self.assertEqual(result["causal_evidence_grade"],"CE5")

    def test_identification_failure_caps_ce3(self):
        value=decision_grade_input(); value["identification"]["causal_graph_contract"]=False
        self.assertEqual(grade_causal_claim(value)["causal_evidence_grade"],"CE3")

    def test_independent_review_missing_caps_ce4(self):
        value=decision_grade_input(); value["review_status"]="internal_reviewed"
        self.assertEqual(grade_causal_claim(value)["causal_evidence_grade"],"CE4")

    def test_business_value_cannot_rescue_failed_q4(self):
        value=decision_grade_input(); value["eligibility_gates"]["Q4"]="fail"; value["economic_status"]="value_supported"
        self.assertEqual(grade_causal_claim(value)["causal_evidence_grade"],"CE3")

    def test_incremental_economics_interval(self):
        result=calculate_incremental_economics({"causal_evidence_grade":"CE4","effect_interval":{"lower":0.01,"point":0.02,"upper":0.03},"eligible_volume":10000,"effect_unit":"orders","qualified_unit_value":{"lower":5,"point":6,"upper":7,"currency":"USD","source_ref":"D06-PARAM","version":"1.0","valid_until":"2027-01-01T00:00:00Z"},"costs":{"implementation":100,"opportunity":50,"risk":0},"as_of_time":"2026-08-10T00:00:00Z"})
        self.assertEqual(result["incremental_value_interval"]["point"],1050)
        self.assertEqual(result["economic_status"],"value_supported")

    def test_ce3_cannot_be_called_incremental_economics(self):
        with self.assertRaises(ECAEError):
            calculate_incremental_economics({"causal_evidence_grade":"CE3"})

    def test_handoff_hash_and_schema(self):
        result={"object_id":"ECAE-RESULT-DEMO","status":"reviewed","causal_evidence_grade":"CE4","claim_ceiling":"CE4","estimand_ref":"ECAE-ESTIMAND-DEMO","allowed_wording":["bounded causal effect"],"prohibited_wording":["universal"],"reproducibility_bundle_ref":"ECAE-REPRO-DEMO","review_status":"internal_reviewed","limitations":["US only"]}
        handoff=build_causal_handoff({"causal_result":result,"consumer":"D08","created_at":"2026-08-10T00:00:00Z","expires_at":"2026-09-10T00:00:00Z","applicability":{"population":"eligible US sessions","platforms":["Amazon"],"countries":["US"],"time_window":"2026Q3","treatment_version":"v2"},"invalidation_triggers":["metric changes"],"recompute_triggers":["late outcomes mature"]})
        self.assertEqual(handoff["content_hash"],content_hash(handoff))
        self.assertFalse(handoff["external_write"])
        self.assertTrue(validate_object(handoff,"causal-handoff.schema.json")["valid"])


if __name__=="__main__": unittest.main()
