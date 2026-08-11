import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ecae_common import ECAEError
from evaluate_doubly_robust_effect import evaluate_doubly_robust_effect
from evaluate_heterogeneous_effect import evaluate_heterogeneous_effect
from evaluate_long_term_surrogate import evaluate_long_term_surrogate
from evaluate_sensitivity import evaluate_sensitivity
from evaluate_transportability import evaluate_transportability


class ObservationalHTETests(unittest.TestCase):
    @staticmethod
    def observational_value(method="DML"):
        return {"method":method,"target_trial":"point treatment emulation","estimand":"ATE","dag_ref":"d","adjustment_set":["x"],"all_covariates_pretreatment":True,"cross_fitting":True,"cross_fit_folds":5,"out_of_fold_nuisance_predictions":True,"overlap_diagnostics":"propensity and effective sample","nuisance_models":"locked","nuisance_model_selection_frozen":True,"trimming_policy":"locked","negative_control_or_placebo":"negative outcome","unmeasured_confounding_sensitivity":"tipping point","influence_function_interval":True,"seed_contract":"fixed seed and fold hash","overlap_status":"pass"}

    @staticmethod
    def hte_value():
        return {
            "estimand":"GATE","mode":"confirmatory","source_design":"randomized","source_estimand":"ATE",
            "source_causal_grade":"CE5","treatment_versions":["control-v1","treatment-v1"],"target_population":"registered eligible users",
            "effect_modifier_set":["country","prior_orders"],"all_effect_modifiers_pretreatment":True,
            "honest_evaluation":True,"development_sample_ref":"snapshot:development","evaluation_sample_ref":"snapshot:evaluation",
            "samples_disjoint":True,"sample_split_or_crossfit":True,"split_assignment_frozen":True,"split_hash":"sha256:split",
            "model_selection_frozen":True,"hyperparameter_tuning_scope":"development only","seed_contract":"seed and repeated split ledger",
            "overlap_diagnostics":"arm support and propensity","overlap_status":"pass","subgroup_or_score_definition":"pre-registered country x prior-order groups",
            "definition_frozen_before_evaluation":True,"holdout_policy_value":True,"policy_rule_frozen_before_evaluation":True,
            "baseline_policies":["treat_all","treat_none","current_policy"],"capacity_constraint":"at most 40 percent",
            "cost_policy":"versioned incremental cost","fairness_review_ref":"fairness:review-pending","multiple_testing_policy":"Holm family",
            "calibration_plan":"BLP and GATE calibration","stability_plan":"repeated splits, seeds, and drift",
            "individual_true_effect_claimed":False,"evaluation_outcomes_used_for_training":False,
        }

    @staticmethod
    def transport_value(source_grade="CE5"):
        return {
            "source_environment":"Amazon US","target_environment":"Amazon UK","source_grade":source_grade,
            "source_estimand":"ATE 90-day contribution","target_estimand":"ATE 90-day contribution",
            "source_population":"US eligible users","target_population":"UK eligible users","selection_diagram_ref":"dag:selection-v1",
            "selection_exchangeability_assumption":True,"consistency_assumption":True,"treatment_version_equivalent":True,
            "outcome_measurement_equivalent":True,"effect_modifiers":["prior_orders","price_band"],
            "effect_modifier_sufficiency_argument":"selection nodes blocked by registered modifiers","all_effect_modifiers_pretreatment":True,
            "target_population_evidence":"time-frozen UK snapshot","sampling_score_model":"locked logistic plus spline",
            "sampling_score_cross_fitted":True,"transport_estimator":"doubly_robust_transport","support_overlap_status":"pass",
            "weight_diagnostics":{"source_sample_size":1000,"effective_sample_size":720,"maximum_normalized_weight":4.2,"tail_weight_mass":0.08},
            "transport_precision_policy":{"minimum_effective_sample_size":500,"maximum_normalized_weight":6.0,"maximum_tail_weight_mass":0.12},
            "weight_truncation_policy":"frozen 1/99 percent sensitivity only","weight_sensitivity":"untruncated, truncated, standardization",
            "mechanism_stability_argument":"same fulfillment and checkout mechanism","temporal_drift_assessment":"no material registered drift",
            "bridge_validation_plan":"UK local randomized holdout","bridge_validation_completed":True,
            "f02_applicability_ref":"F02:UK-v1","f02_applicability_status":"pass",
        }

    @staticmethod
    def surrogate_value(mode="surrogate_index"):
        return {
            "long_term_estimand":"ATE on 365-day contribution","long_term_outcome":"365-day contribution","outcome_horizon":"365 days",
            "decision_horizon":"30 days","evidence_mode":mode,"intervention_family":"registered retention offers",
            "target_population":"eligible first-order customers","treatment_version":"offer-v1","short_term_surrogates":["30-day repeat","60-day engagement"],
            "surrogate_measurement_times":["30d","60d"],"experimental_sample_ref":"exp:2025","long_term_outcome_sample_ref":"historical:2024",
            "samples_comparable":True,"surrogacy_assumption":True,"comparability_assumption":True,
            "all_surrogates_post_assignment_pre_outcome":True,"surrogate_model_cross_fitted":True,"surrogate_model_frozen":True,
            "historical_validation":True,"treatment_family_validation":True,"negative_or_failure_cases":["discount changed proxy but harmed margin"],
            "measurement_maturity_status":"mature","censoring_competing_risk_plan":"IPCW plus competing closure risk",
            "missingness_sensitivity":"MNAR tipping point","surrogacy_violation_sensitivity":"direct-path bias grid",
            "bridge_validation_plan":"direct long-term validation cohort","bridge_validation_completed":True,
        }

    def test_bad_control_blocks_observational(self):
        value = self.observational_value(); value["all_covariates_pretreatment"] = False
        with self.assertRaises(ECAEError) as context: evaluate_doubly_robust_effect(value)
        self.assertEqual(context.exception.code, "BAD_CONTROL")

    def test_qualified_observational_still_needs_backend(self):
        with self.assertRaises(ECAEError) as context: evaluate_doubly_robust_effect(self.observational_value())
        self.assertEqual(context.exception.code, "BACKEND_UNAVAILABLE")

    def test_nuisance_leakage_is_blocked_before_backend(self):
        value = self.observational_value(); value["out_of_fold_nuisance_predictions"] = False
        with self.assertRaises(ECAEError) as context: evaluate_doubly_robust_effect(value)
        self.assertEqual(context.exception.code, "NUISANCE_LEAKAGE")

    def test_tmle_is_explicitly_unavailable_not_substituted(self):
        with self.assertRaises(ECAEError) as context: evaluate_doubly_robust_effect(self.observational_value("TMLE"))
        self.assertEqual(context.exception.code, "BACKEND_UNAVAILABLE")

    def test_hte_individual_true_effect_prohibited(self):
        value = self.hte_value(); value["individual_true_effect_claimed"] = True
        with self.assertRaises(ECAEError) as context: evaluate_heterogeneous_effect(value)
        self.assertEqual(context.exception.code, "INDIVIDUAL_CAUSAL_CLAIM_PROHIBITED")

    def test_hte_evaluation_leakage_blocks_before_backend(self):
        value = self.hte_value(); value["evaluation_outcomes_used_for_training"] = True
        with self.assertRaises(ECAEError) as context: evaluate_heterogeneous_effect(value)
        self.assertEqual(context.exception.code, "HTE_EVALUATION_LEAKAGE")

    def test_hte_posttreatment_modifier_is_rejected(self):
        value = self.hte_value(); value["all_effect_modifiers_pretreatment"] = False
        with self.assertRaises(ECAEError) as context: evaluate_heterogeneous_effect(value)
        self.assertEqual(context.exception.code, "POSTTREATMENT_MODIFIER")

    def test_hte_policy_baselines_must_include_all_none_current(self):
        value = self.hte_value(); value["baseline_policies"] = ["treat_none", "current_policy"]
        with self.assertRaises(ECAEError) as context: evaluate_heterogeneous_effect(value)
        self.assertEqual(context.exception.code, "POLICY_BASELINES_INCOMPLETE")

    def test_hte_confirmatory_multiplicity_cannot_be_none(self):
        value = self.hte_value(); value["multiple_testing_policy"] = "none"
        with self.assertRaises(ECAEError) as context: evaluate_heterogeneous_effect(value)
        self.assertEqual(context.exception.code, "HTE_MULTIPLICITY_UNCONTROLLED")

    def test_qualified_hte_still_fails_closed_without_verified_backend(self):
        with self.assertRaises(ECAEError) as context: evaluate_heterogeneous_effect(self.hte_value())
        self.assertEqual(context.exception.code, "BACKEND_UNAVAILABLE")

    def test_sensitivity_missing_blocks_ce4(self):
        result = evaluate_sensitivity({"method_family":"did","analyses":[{"threat":"parallel_trends","status":"pass"}]})
        self.assertEqual(result["claim_impact"], "block_ce4")

    def test_surrogate_endpoint_alone_remains_ce3(self):
        result = evaluate_long_term_surrogate(self.surrogate_value("surrogate_endpoint_only"))
        self.assertEqual(result["claim_ceiling"], "CE3")
        self.assertIn("SURROGATE_ENDPOINT_ONLY", result["blockers"])

    def test_favorable_surrogate_cannot_be_used_as_long_term_proof(self):
        value = self.surrogate_value(); value["treatment_effect_on_surrogate_used_as_long_term_proof"] = True
        with self.assertRaises(ECAEError) as context: evaluate_long_term_surrogate(value)
        self.assertEqual(context.exception.code, "SURROGATE_PARADOX_RISK")

    def test_dynamic_long_term_treatment_routes_to_protocol_only(self):
        value = self.surrogate_value(); value["dynamic_treatment_or_time_varying_confounding"] = True
        result = evaluate_long_term_surrogate(value)
        self.assertEqual(result["status"], "protocol_only_longitudinal_g_method_required")
        self.assertEqual(result["claim_ceiling"], "CE3")

    def test_mature_direct_long_term_outcome_does_not_need_surrogate(self):
        value = self.surrogate_value("direct_long_term")
        for field in ("short_term_surrogates","surrogate_measurement_times","samples_comparable","surrogacy_assumption","comparability_assumption","all_surrogates_post_assignment_pre_outcome","surrogate_model_cross_fitted","surrogate_model_frozen","historical_validation","treatment_family_validation","negative_or_failure_cases","surrogacy_violation_sensitivity","bridge_validation_plan"):
            value.pop(field, None)
        result = evaluate_long_term_surrogate(value)
        self.assertEqual(result["status"], "qualified_for_direct_long_term_analysis")
        self.assertFalse(result["long_term_effect_estimated"])

    def test_transport_defaults_to_ce3_without_bridge(self):
        value = self.transport_value(); value["bridge_validation_completed"] = False
        result = evaluate_transportability(value)
        self.assertEqual(result["target_grade_ceiling"], "CE3")
        self.assertIn("BRIDGE_VALIDATION_PENDING", result["blockers"])

    def test_transport_protocol_never_inherits_ce5(self):
        result = evaluate_transportability(self.transport_value("CE5"))
        self.assertEqual(result["target_grade_ceiling"], "CE4")
        self.assertFalse(result["target_grade_awarded"])

    def test_transport_never_upgrades_low_source_grade(self):
        result = evaluate_transportability(self.transport_value("CE2"))
        self.assertEqual(result["target_grade_ceiling"], "CE2")

    def test_transport_weight_dominance_blocks_support(self):
        value = self.transport_value(); value["weight_diagnostics"]["maximum_normalized_weight"] = 12.0
        result = evaluate_transportability(value)
        self.assertEqual(result["transport_status"], "not_yet_supported")
        self.assertIn("TRANSPORT_WEIGHT_DOMINANCE", result["blockers"])


if __name__ == "__main__":
    unittest.main()
