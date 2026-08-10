import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from ecae_common import ECAEError
from evaluate_did import evaluate_did
from evaluate_rdd_iv import evaluate_rdd_iv
from evaluate_synthetic_counterfactual import evaluate_synthetic_counterfactual


class QuasiExperimentalTests(unittest.TestCase):
    @staticmethod
    def staggered_value():
        return {"design":"staggered","estimator":"group_time_ATT","control_group":"not_yet_treated","estimand":"ATT(g,t)","treatment_timing_frozen":True,"no_anticipation":True,"anticipation_periods":0,"all_covariates_pretreatment":True,"panel_structure":"panel","simultaneous_confidence_band":True,"pretrend_event_window":[-3,-1],"composition_policy":"balanced_panel_sensitivity","reversal_policy":"no_reversal","spillover_assessment":"no_cross_unit_exposure_argument"}

    @staticmethod
    def donors():
        return [{"donor_id":"a","contaminated":False,"metric_comparable":True,"structural_break":False},{"donor_id":"b","contaminated":False,"metric_comparable":True,"structural_break":False},{"donor_id":"c","contaminated":False,"metric_comparable":True,"structural_break":False}]

    @staticmethod
    def rdd_value():
        return {"method":"RDD","running_variable":"score","running_variable_frozen":True,"cutoff":0,"cutoff_frozen":True,"assignment_type":"sharp","bandwidth_rule":"mserd","kernel":"triangular","local_polynomial_order":1,"robust_bias_correction":True,"manipulation_test":"rddensity_registered","covariate_continuity":"registered","placebo_cutoffs":[-1,1],"bandwidth_sensitivity":[.5,1,1.5],"polynomial_sensitivity":[1,2],"donut_sensitivity":"registered","local_population":"near cutoff"}

    def test_2x2_did_analytical_truth(self):
        cells={
            "treated_pre":{"n":100,"mean":10,"variance":4},"treated_post":{"n":100,"mean":15,"variance":4},
            "control_pre":{"n":100,"mean":8,"variance":4},"control_post":{"n":100,"mean":10,"variance":4}
        }
        result=evaluate_did({"design":"2x2","no_anticipation":True,"common_shock_argument":"same demand shock","cells":cells,"data_structure":"independent_repeated_cross_sections"})
        self.assertAlmostEqual(result["estimate"],3.0)
        self.assertEqual(result["claim_ceiling"],"CE4")

    def test_staggered_twfe_prohibited(self):
        with self.assertRaises(ECAEError) as context:
            evaluate_did({"design":"staggered","estimator":"TWFE","control_group":"not_yet_treated"})
        self.assertEqual(context.exception.code,"NAIVE_TWFE_PROHIBITED")

    def test_staggered_contract_routes_only_to_unverified_group_time_backend(self):
        with self.assertRaises(ECAEError) as context:
            evaluate_did(self.staggered_value())
        self.assertEqual(context.exception.code,"BACKEND_UNAVAILABLE")

    def test_staggered_pointwise_event_study_is_prohibited(self):
        value=self.staggered_value(); value["simultaneous_confidence_band"]=False
        with self.assertRaises(ECAEError) as context: evaluate_did(value)
        self.assertEqual(context.exception.code,"POINTWISE_EVENT_STUDY_PROHIBITED")

    def test_scm_contract_then_backend_failure(self):
        value={"method":"SCM","estimand":"treated_unit_gap","donor_pool":self.donors(),"donor_pool_frozen_before_post_outcomes":True,"intervention_time_frozen":True,"pre_period_count":8,"post_period_count":3,"uncertainty_method":"in_space_placebo_rank","donor_dominance_threshold":.6,"treated_unit_count":1,"registered_sensitivity":["in_space_placebo","time_placebo","leave_one_out","pre_fit","weight_concentration"]}
        with self.assertRaises(ECAEError) as context:
            evaluate_synthetic_counterfactual(value)
        self.assertEqual(context.exception.code,"BACKEND_UNAVAILABLE")

    def test_sdid_staggered_adoption_is_blocked(self):
        value={"method":"SDID","estimand":"ATT","donor_pool":self.donors(),"donor_pool_frozen_before_post_outcomes":True,"intervention_time_frozen":True,"pre_period_count":8,"post_period_count":3,"uncertainty_method":"placebo","donor_dominance_threshold":.6,"adoption_pattern":"staggered","registered_sensitivity":["in_space_placebo","time_placebo","leave_one_out","pre_fit","weight_concentration","time_weight_concentration"]}
        with self.assertRaises(ECAEError) as context: evaluate_synthetic_counterfactual(value)
        self.assertEqual(context.exception.code,"SDID_ADOPTION_SCOPE")

    def test_rdd_local_contract_then_backend_failure(self):
        with self.assertRaises(ECAEError) as context:
            evaluate_rdd_iv(self.rdd_value())
        self.assertEqual(context.exception.code,"BACKEND_UNAVAILABLE")

    def test_rdd_global_polynomial_primary_is_blocked(self):
        value=self.rdd_value(); value["local_polynomial_order"]=3
        with self.assertRaises(ECAEError) as context: evaluate_rdd_iv(value)
        self.assertEqual(context.exception.code,"RDD_PRIMARY_ORDER_INVALID")

    def test_iv_requires_weak_robust_inference_and_then_fails_closed(self):
        value={"method":"IV","instrument":"z","treatment":"d","outcome":"y","estimand":"LATE","relevance_evidence":"first stage registered","exclusion_argument":"exclusion DAG argument","independence_argument":"as-if random assignment","monotonicity_argument":"no defiers in target mechanism","complier_population":"eligible compliers","estimator":"LIML","weak_instrument_robust_inference":"both","first_stage_diagnostics":"rank and strength","reduced_form":"registered"}
        with self.assertRaises(ECAEError) as context: evaluate_rdd_iv(value)
        self.assertEqual(context.exception.code,"BACKEND_UNAVAILABLE")


if __name__=="__main__": unittest.main()
