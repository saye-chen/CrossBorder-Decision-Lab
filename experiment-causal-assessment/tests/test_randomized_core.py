import math
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from apply_covariate_adjustment import apply_covariate_adjustment
from calculate_mde_precision import calculate_mde_precision
from calculate_sample_size import calculate_sample_size
from ecae_common import ECAEError
from evaluate_randomized_effect import evaluate_randomized_effect
from validate_exposure_outcome import validate_exposure_outcome
from validate_randomization import validate_randomization


class RandomizedCoreTests(unittest.TestCase):
    def test_continuous_sample_size_matches_formula(self):
        result=calculate_sample_size({"metric_type":"continuous","alpha":0.05,"power":0.8,"minimum_important_effect":1,"baseline_variance":4,"allocation_ratio":1,"attrition_rate":0})
        self.assertEqual(result["n_control"],63)
        self.assertEqual(result["n_treatment"],63)

    def test_binary_sample_size_is_finite(self):
        result=calculate_sample_size({"metric_type":"binary","baseline_rate":0.1,"minimum_important_effect":0.02,"alpha":0.05,"power":0.8,"attrition_rate":0.1})
        self.assertGreater(result["n_total"],1000)

    def test_mde_inverse(self):
        result=calculate_mde_precision({"metric_type":"continuous","n_control":100,"n_treatment":100,"baseline_variance":4,"alpha":0.05,"power":0.8,"confidence_level":0.95})
        self.assertAlmostEqual(result["standard_error_at_null"],math.sqrt(0.08),12)
        self.assertGreater(result["mde_absolute"],result["confidence_half_width_at_null"])

    def test_continuous_itt_known_difference(self):
        result=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"continuous","control_arm":"c","groups":{"c":[1,2,3,4],"t":[2,3,4,5]}})
        self.assertAlmostEqual(result["comparisons"][0]["estimate_absolute"],1.0)

    def test_binary_uses_newcombe_not_wald(self):
        result=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"binary","control_arm":"c","groups":{"c":[0,0,0,0,0],"t":[1,0,0,0,0]}})
        comparison=result["comparisons"][0]
        self.assertEqual(comparison["confidence_interval"]["method"],"newcombe_hybrid_score_v1")
        self.assertLessEqual(comparison["confidence_interval"]["upper"],1)

    def test_ratio_of_totals_delta(self):
        result=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"ratio","control_arm":"c","groups":{"c":[{"numerator":1,"denominator":2},{"numerator":2,"denominator":4}],"t":[{"numerator":2,"denominator":2},{"numerator":4,"denominator":4}]}})
        self.assertAlmostEqual(result["comparisons"][0]["estimate_absolute"],0.5)

    def test_cuped_preserves_unadjusted_and_reduces_variance(self):
        records=[]
        for index in range(20):
            arm="t" if index%2 else "c"
            x=float(index)
            records.append({"arm":arm,"outcome":2*x+(1 if arm=="t" else 0),"covariates":{"x":x}})
        result=apply_covariate_adjustment({"records":records,"covariates":[{"name":"x","temporal_status":"pre_treatment"}],"control_arm":"c"})
        self.assertIn("unadjusted",result)
        self.assertGreater(result["variance_reduction_fraction"],0.9)

    def test_cuped_rejects_post_treatment(self):
        with self.assertRaises(ECAEError):
            apply_covariate_adjustment({"records":[{"arm":"c","outcome":1,"covariates":{"x":1}}]*4,"covariates":[{"name":"x","temporal_status":"post_treatment"}],"control_arm":"c"})

    def test_srm_pass_and_fail(self):
        proof={"proof_type":"hash_bucket","value":"abc"}
        passed=validate_randomization({"observed_counts":{"c":500,"t":500},"expected_probabilities":{"c":0.5,"t":0.5},"assignment_proof":proof})
        failed=validate_randomization({"observed_counts":{"c":700,"t":300},"expected_probabilities":{"c":0.5,"t":0.5},"assignment_proof":proof})
        self.assertEqual(passed["status"],"pass")
        self.assertIn("SRM_DETECTED",failed["blockers"])

    def test_exposure_maturity_can_block(self):
        arm={"assigned":100,"eligible_exposure":100,"actually_exposed":98,"outcome_observed":99,"outcome_mature":90,"contaminated":0,"duplicate_units":0}
        result=validate_exposure_outcome({"arms":{"c":arm,"t":arm},"thresholds":{"max_outcome_missing_rate":0.05,"max_contamination_rate":0.01,"max_crossarm_missingness_difference":0.02}})
        self.assertEqual(result["status"],"fail")
        self.assertTrue(any("OUTCOME_NOT_MATURE" in item for item in result["blockers"]))


if __name__=="__main__": unittest.main()
