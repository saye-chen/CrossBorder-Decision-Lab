#!/usr/bin/env python3
"""Executable marketing-science estimation, property and adversarial tests."""
from __future__ import annotations
import pathlib, sys, unittest
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import experiment_design, causal_effects, uncertainty_engine, offer_response_optimization
import channel_response, aggregate_customer_economics, brand_value_bridge
import channel_curve_estimation
import seasonality_competition, incident_recovery_quantification
from mbcm_common import ModelError

class ExperimentAndCausality(unittest.TestCase):
    def test_power_increases_with_noise_and_clusters(self):
        base={"baseline_mean":100,"baseline_sd":20,"relative_mde":0.05,"alpha":0.05,
              "power":0.8,"cluster_size":100,"intracluster_correlation":0,
              "weekly_observations_per_cluster":25}
        plain=experiment_design.calculate(base)
        clustered=experiment_design.calculate({**base,"intracluster_correlation":0.05})
        noisy=experiment_design.calculate({**base,"baseline_sd":30})
        self.assertGreater(clustered["adjusted_sample_per_arm"],plain["adjusted_sample_per_arm"])
        self.assertGreater(noisy["individual_sample_per_arm"],plain["individual_sample_per_arm"])
        self.assertGreaterEqual(clustered["clusters_per_arm"],2)

    def test_did_parallel_trend_and_interval(self):
        d={"method":"did","treatment_pre":[10,11,12,13],"treatment_post":[15,16,18,19],
           "control_pre":[20,21,22,23],"control_post":[21,22,23,24],
           "parallel_trend_tolerance":0.01,"alpha":0.05}
        result=causal_effects.calculate(d)
        self.assertTrue(result["parallel_trend_passed"])
        self.assertAlmostEqual(result["effect"],4.5)
        bad=causal_effects.calculate({**d,"treatment_pre":[10,12,14,16]})
        self.assertFalse(bad["parallel_trend_passed"])
        self.assertEqual(bad["action_limit"],"causal_claim_blocked")

    def test_itt_cace_and_synthetic_control(self):
        cace=causal_effects.calculate({"method":"itt_cace","assigned_treatment_mean":12,
          "assigned_control_mean":10,"treatment_compliance":0.8,"control_compliance":0.2})
        self.assertAlmostEqual(cace["cace"],2/0.6)
        synthetic=causal_effects.calculate({"method":"synthetic_control","treated_pre":[2,2,2],
          "donor_pre":[[1,2,3],[3,2,1]],"treated_post":3,"donor_post":[4,2],
          "maximum_pre_rmse":0.01,"learning_rate":0.01,"iterations":500})
        self.assertTrue(synthetic["fit_passed"])
        self.assertAlmostEqual(sum(synthetic["donor_weights"]),1)
        self.assertAlmostEqual(synthetic["effect"],0,places=5)
        matched=causal_effects.calculate({"method":"geo_match",
          "treated_geos":[{"id":"T1","metrics":{"sales":1.0,"trend":0.1}}],
          "control_geos":[{"id":"C1","metrics":{"sales":1.1,"trend":0.1}}],
          "metric_weights":{"sales":1,"trend":4},"maximum_distance":0.2})
        self.assertTrue(matched["all_pairs_balanced"])

    def test_bootstrap_and_monte_carlo_are_seeded(self):
        payload={"method":"bootstrap_mean_difference","seed":7,"iterations":500,
                 "treatment":[2,3,4,5],"control":[1,2,2,3]}
        self.assertEqual(uncertainty_engine.calculate(payload),uncertainty_engine.calculate(payload))
        mc=uncertainty_engine.calculate({"method":"monte_carlo_contribution","seed":3,"iterations":1000,
          "revenue":{"mean":100,"sd":5},"costs":[{"mean":70,"sd":5}]})
        self.assertGreater(mc["probability_positive"],0.9)
        posterior=uncertainty_engine.calculate({"method":"beta_binomial_update","seed":9,"iterations":1000,
          "prior_alpha":1,"prior_beta":1,"successes":60,"trials":100})
        self.assertGreater(posterior["mean"],0.5)

class ResponseAndEconomics(unittest.TestCase):
    def test_offer_elasticity_and_optimum_are_nonlinear(self):
        result=offer_response_optimization.calculate({"historical_price":[20,18,16,14],
          "historical_orders":[50,56,63,72],"reference_price":20,
          "candidate_discounts":[0,0.1,0.2,0.3],"unit_variable_cost":10,
          "fixed_cost":50,"fatigue_rate":0.4,"currency":"USD"})
        self.assertLess(result["elasticity"],0)
        self.assertIn(result["optimal_discount"],[0,0.1,0.2,0.3])
        contributions=[x["contribution"] for x in result["candidates"]]
        self.assertNotEqual(contributions[1]-contributions[0],contributions[2]-contributions[1])

    def test_channel_adstock_saturation_interaction_and_pacing(self):
        result=channel_response.calculate({"channels":[
          {"id":"search","spend":[100,100,100,100],"decay":0.5,"half_saturation":100,"shape":1,"max_response":10},
          {"id":"creator","spend":[50,0,50,0],"decay":0.7,"half_saturation":50,"shape":1.2,"max_response":8}],
          "interactions":[{"channel_a":"search","channel_b":"creator","coefficient":0.01}],
          "pacing":{"total_budget":800,"periods":8},
          "frequency_bins":[{"frequency":1,"exposed":1000,"conversions":20},
                            {"frequency":2,"exposed":800,"conversions":24},
                            {"frequency":5,"exposed":500,"conversions":10}],
          "attribution_window_values":{"short":{"search":10,"creator":5},
                                       "long":{"search":8,"creator":12}}})
        self.assertGreater(result["interaction_value"],0)
        for schedule in result["pacing_schedules"].values(): self.assertAlmostEqual(sum(schedule),800)
        self.assertGreater(result["channels"]["search"]["adstock"][1],100)
        self.assertTrue(result["window_sensitive"])
        self.assertLess(result["frequency_response"][-1]["marginal_conversion_rate"],0)
        estimated=channel_curve_estimation.calculate({"spend":[0,20,40,60,80,100,120,140],
          "response":[0,2,3.5,4.7,5.5,6.1,6.5,6.8],
          "decay_candidates":[0,0.3,0.6],"half_saturation_candidates":[30,60,100],
          "shape_candidates":[0.8,1,1.5]})
        self.assertGreater(estimated["r_squared"],0.8)

    def test_aggregate_customer_quality_and_payback(self):
        result=aggregate_customer_economics.calculate({"discount_rate_per_period":0.01,"currency":"USD",
          "cohorts":[{"cohort_id":"offer-A","acquired_customers":100,"acquisition_cost":1000,
            "retention_rates":[1,0.6,0.4],"contribution_per_active":[6,8,8],"maximum_payback_periods":3}]})
        cohort=result["cohorts"][0]
        self.assertEqual(cohort["cac"],10)
        self.assertTrue(cohort["quality_passed"])
        self.assertEqual(result["forbidden_use"],"individual_targeting_or_contact")

    def test_brand_bridge_and_price_premium(self):
        result=brand_value_bridge.calculate({"brand_proxy":[1,2,3,4,5],
          "business_outcome":[3,5,8,11,14],"brand_prices":[120,110,130],
          "matched_generic_prices":[90,100,110],"brand_quantities":[80,90,70],
          "generic_quantities":[120,100,85],"decay_rate":0.3,"currency":"USD"})
        self.assertGreater(result["proxy_to_outcome_slope"],0)
        self.assertGreater(result["average_matched_price_premium"],0.1)
        self.assertGreater(result["adstock_half_life_periods"],0)
        self.assertIn("elasticity_difference",result)

class ContextAndRecovery(unittest.TestCase):
    def test_seasonality_competition_and_post_event_depletion(self):
        years=[[80,80,90,90,100,100,100,110,120,130,150,200],
               [84,82,92,94,102,104,103,112,122,135,155,205]]
        result=seasonality_competition.calculate({"monthly_history":years,
          "event_window":[100,120,180,80,70],"own_outcome":[120,115,110,105,100],
          "competitor_pressure":[0,1,2,3,4],"own_sov":0.2,"own_som":0.3})
        self.assertAlmostEqual(sum(result["seasonal_indices"]),12)
        self.assertGreater(result["post_event_depletion_per_period"],0)
        self.assertEqual(result["recommended_competitive_posture"],"counter")

    def test_incident_controlled_impact_half_life_and_repair_npv(self):
        result=incident_recovery_quantification.calculate({"affected_pre":[100,102,98],
          "affected_post":[70,72,68],"control_pre":[100,100,100],"control_post":[98,99,97],
          "recovery_gaps":[32,16,8,4],"affected_retention":0.6,"control_retention":0.8,"repair_cost":10,
          "repair_incremental_recovery":[8,8,8],"discount_rate":0.01,"currency":"USD"})
        self.assertLess(result["controlled_incident_effect"],0)
        self.assertAlmostEqual(result["recovery_half_life_periods"],1,places=5)
        self.assertTrue(result["repair_recommended"])
        self.assertAlmostEqual(result["excess_churn_probability"],0.2)

    def test_adversarial_invalid_designs_fail(self):
        with self.assertRaises(ModelError):
            experiment_design.calculate({"baseline_mean":100,"baseline_sd":0,"relative_mde":0.05,
              "alpha":0.05,"power":0.8,"cluster_size":1,"intracluster_correlation":0,
              "weekly_observations_per_cluster":10})
        with self.assertRaises(ModelError):
            causal_effects.calculate({"method":"itt_cace","assigned_treatment_mean":12,
              "assigned_control_mean":10,"treatment_compliance":0.2,"control_compliance":0.8})

if __name__=="__main__": unittest.main(verbosity=2)
