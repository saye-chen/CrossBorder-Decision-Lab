#!/usr/bin/env python3
"""MBCM executable depth, math, continuity, sovereignty and coverage tests."""
from __future__ import annotations
import hashlib, json, pathlib, sys, unittest
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import campaign_economics, offer_economics, incrementality_bridge, pull_forward_cannibalization
import resource_portfolio, brand_investment_scenarios, capacity_stress, risk_and_sensitivity
import clearance_exit_economics, validate_units_currency_time, evaluate_marketing_decision, decision_state
import validate_incident
from mbcm_common import ModelError, sha

class Models(unittest.TestCase):
    def campaign(self,discount=100,refunds=50):
        return campaign_economics.calculate({"quantity":100,"unit_price":20,"merchant_discount":discount,
          "refunds":refunds,"tax":100,"cogs":700,"fulfillment":200,"platform_fees":100,
          "service_cost":50,"channel_cost":200,"offer_cost":50,"campaign_fixed_cost":100,"currency":"USD"})
    def test_campaign_oracle_and_monotonicity(self):
        self.assertEqual(self.campaign()["campaign_contribution"],350)
        self.assertLess(self.campaign(discount=200)["campaign_contribution"],self.campaign()["campaign_contribution"])
        self.assertLess(self.campaign(refunds=100)["campaign_contribution"],self.campaign()["campaign_contribution"])
    def offer(self,discount=3,noninc=True):
        return offer_economics.calculate({"eligible":200,"redeemed_orders":100,"incremental_orders":30 if noninc else 100,
          "merchant_discount_per_redeemed":discount,"gift_cost_per_redeemed":1,"shipping_subsidy_per_redeemed":0,
          "guarantee_cost":10,"fraud_loss":5,"service_cost":5,"incremental_cm_per_order":20,
          "pull_forward_loss":20,"cannibalization_loss":20,"fixed_cost":40,"currency":"USD"})
    def test_offer_nonincremental_and_monotonicity(self):
        x=self.offer(); self.assertEqual(x["non_incremental_redeemed_orders"],70)
        self.assertEqual(x["incremental_offer_contribution"],100)
        self.assertLess(self.offer(discount=4)["incremental_offer_contribution"],x["incremental_offer_contribution"])
        with self.assertRaises(ModelError): offer_economics.calculate({**{"eligible":1,"redeemed_orders":1,"incremental_orders":2,
          "merchant_discount_per_redeemed":0,"gift_cost_per_redeemed":0,"shipping_subsidy_per_redeemed":0,
          "guarantee_cost":0,"fraud_loss":0,"service_cost":0,"incremental_cm_per_order":1,
          "pull_forward_loss":0,"cannibalization_loss":0,"fixed_cost":0,"currency":"USD"}})
        with self.assertRaises(ModelError): offer_economics.calculate({"eligible":1,"redeemed_orders":2,"incremental_orders":1,
          "merchant_discount_per_redeemed":0,"gift_cost_per_redeemed":0,"shipping_subsidy_per_redeemed":0,
          "guarantee_cost":0,"fraud_loss":0,"service_cost":0,"incremental_cm_per_order":1,
          "pull_forward_loss":0,"cannibalization_loss":0,"fixed_cost":0,"currency":"USD"})
    def test_incrementality_separates_attribution(self):
        x=incrementality_bridge.calculate({"observed_orders":120,"attributed_orders":90,"counterfactual_orders":100,
          "incremental_net_revenue":600,"incremental_cogs":200,"incremental_fulfillment":50,
          "incremental_platform_fees":30,"incremental_service_returns":20,"incremental_channel_cost":100,
          "incremental_offer_cost":50,"incremental_fixed_cost":20,"ci_lower_orders":-2,"ci_upper_orders":42,"currency":"USD"})
        self.assertEqual(x["incremental_orders"],20); self.assertEqual(x["mature_incremental_contribution"],130)
        self.assertFalse(x["causal_claim_allowed"]); self.assertFalse(x["attribution_equals_incrementality"])
    def test_pull_forward_cannibalization(self):
        x=pull_forward_cannibalization.calculate({"expected_post_units":100,"observed_post_units":80,
          "baseline_cm_per_unit":5,"siblings":[{"counterfactual_units":50,"observed_units":40,"baseline_cm":4}],
          "channel_shifts":[{"orders":10,"new_channel_cm":6,"original_channel_cm":8}],"currency":"USD"})
        self.assertEqual((x["pull_forward_loss"],x["cannibalization_loss"],x["channel_shift_value"]),(100,40,-20))
    def test_resource_bounds_marginal_and_hhi(self):
        x=resource_portfolio.calculate({"approved_envelope":1000,"currency":"USD","candidates":[
          {"id":"A","allocation":600,"minimum":100,"maximum":700,"marginal_incremental_value":1.5,"gate_passed":True},
          {"id":"B","allocation":400,"minimum":0,"maximum":500,"marginal_incremental_value":-0.2,"gate_passed":True}]})
        self.assertAlmostEqual(x["hhi"],0.52); self.assertEqual(x["negative_marginal_ids"],["B"])
        self.assertEqual(x["scale_allowed_ids"],["A"])
    def test_brand_scenario_uses_d06_rate(self):
        x=brand_investment_scenarios.calculate({"currency":"USD","discount_rate":0.1,"scenarios":[
          {"id":"stage","current_investment":100,"future_incremental_contributions":[80,80],
           "avoided_costs":[0,0],"risk_loss":10,"approved_max_loss":150}]})
        self.assertTrue(x["scenarios"][0]["positive_value"]); self.assertTrue(x["scenarios"][0]["within_loss_boundary"])
    def test_capacity_minimum_and_monotonicity(self):
        base={"baseline_demand":100,"incremental_demand":30,"pull_forward_demand":10,"uncertainty_buffer":10,
              "capacities":{"inventory":200,"fulfillment":160,"service":140,"financial":180}}
        x=capacity_stress.calculate(base); self.assertEqual(x["supported_campaign_volume"],20)
        lower=capacity_stress.calculate({**base,"capacities":{**base["capacities"],"service":120}})
        self.assertLess(lower["supported_campaign_volume"],x["supported_campaign_volume"])
    def test_risk_sensitivity_and_exit_redline(self):
        r=risk_and_sensitivity.calculate({"base_value":100,"nonrecoverable_spend":20,"nonrecoverable_offer_cost":10,
          "unavoidable_fulfillment":5,"contract_exit_cost":3,"incident_reserve":2,"currency":"USD",
          "variables":[{"id":"incrementality","low_impact":-150,"high_impact":30}]})
        self.assertEqual(r["maximum_committed_loss"],40); self.assertTrue(r["sensitivities"][0]["crosses_zero"])
        e=clearance_exit_economics.calculate({"currency":"USD","options":[
          {"id":"high-redline","net_revenue":1000,"channel_cost":10,"offer_cost":10,"fulfillment_returns":10,
           "service_complaint":0,"channel_conflict":0,"brand_risk":0,"residual_asset_value":0,"residual_liabilities":0,"redline":True},
          {"id":"safe","net_revenue":200,"channel_cost":20,"offer_cost":20,"fulfillment_returns":20,
           "service_complaint":10,"channel_conflict":0,"brand_risk":0,"residual_asset_value":10,"residual_liabilities":0,"redline":False}]})
        self.assertEqual(e["preferred_feasible_option"],"safe")
    def test_unit_currency_time_guard(self):
        x=validate_units_currency_time.validate({"records":[
          {"currency":"USD","tax_basis":"net","timezone":"UTC","unit":"order","window_start":"2026-01-01T00:00:00Z","window_end":"2026-02-01T00:00:00Z"},
          {"currency":"EUR","tax_basis":"net","timezone":"UTC","unit":"order","window_start":"2026-01-01T00:00:00Z","window_end":"2026-02-01T00:00:00Z"}]})
        self.assertFalse(x["aggregation_allowed"])
        with self.assertRaises(ModelError):
            validate_units_currency_time.validate({"records":[{"currency":"USD","tax_basis":"net",
              "timezone":"UTC","unit":"order","window_start":"01/02/2026","window_end":"02/02/2026"}]})
    def test_nonfinite_and_mutation_guards(self):
        with self.assertRaises(ModelError):
            campaign_economics.calculate({"quantity":float("nan"),"unit_price":20,"merchant_discount":0,
              "refunds":0,"tax":0,"cogs":0,"fulfillment":0,"platform_fees":0,"service_cost":0,
              "channel_cost":0,"offer_cost":0,"campaign_fixed_cost":0,"currency":"USD"})
        oracle=self.campaign()["campaign_contribution"]
        mutated_gross_only=100*20-100
        self.assertNotEqual(oracle,mutated_gross_only,
          "测试必须能杀死忽略退款、税、履约、渠道、Offer与固定成本的错误公式")

class DecisionAndContinuity(unittest.TestCase):
    def gates(self,overrides=None):
        overrides=overrides or {}
        return [{"gate":f"G{i}","status":overrides.get(f"G{i}","passed"),"owner":"MBCM"} for i in range(9)]
    def test_evidence_ceiling_and_sovereignty(self):
        base={"dq_level":"DQ2","claim_level":"C2","gates":self.gates(),"requested_action":"campaign_design",
              "requested_owner":"MBCM","reversibility":"reversible"}
        self.assertEqual(evaluate_marketing_decision.evaluate(base)["decision_state"],"test")
        bad={**base,"dq_level":"DQ3","claim_level":"C3","requested_action":"ad_bid","requested_owner":"MBCM"}
        self.assertEqual(evaluate_marketing_decision.evaluate(bad)["decision_state"],"escalate")
        blocked={**base,"gates":self.gates({"G3":"failed"})}
        self.assertEqual(evaluate_marketing_decision.evaluate(blocked)["decision_state"],"stop")
    def test_parent_hash_and_selective_recompute(self):
        parent={"decision_id":"D1","object_id":"O1","constraints":["cash"]}
        d={"parent_state":parent,"parent_hash":sha(parent),"object_id":"O1","object_version":"v2",
           "changed_fields":["price"],"new_evidence_ids":[],"preserved_constraints":["cash"],
           "dependency_map":{"economics":["price"],"offer":["economics"],"inventory":["demand"]}}
        x=decision_state.update(d); self.assertEqual(x["affected_nodes"],["economics","offer"])
        with self.assertRaises(ModelError): decision_state.update({**d,"parent_hash":"sha256:bad"})
        with self.assertRaises(ModelError): decision_state.update({**d,"preserved_constraints":[]})

    def test_adversarial_boolean_guards(self):
        with self.assertRaises(ModelError):
            resource_portfolio.calculate({"approved_envelope":1,"currency":"USD","candidates":[
              {"id":"A","allocation":1,"minimum":0,"maximum":1,
               "marginal_incremental_value":1,"gate_passed":"false"}]})
        with self.assertRaises(ModelError):
            clearance_exit_economics.calculate({"currency":"USD","options":[
              {"id":"A","net_revenue":1,"channel_cost":0,"offer_cost":0,"fulfillment_returns":0,
               "service_complaint":0,"channel_conflict":0,"brand_risk":0,"residual_asset_value":0,
               "residual_liabilities":0,"redline":"false"}]})

    def test_incident_requires_versioned_objects_and_containment(self):
        valid={"incident_id":"I-1","incident_type":"I03","severity":"S2",
          "objects":[{"object_id":"O1","object_version":"v2"}],"confirmed_facts":["wrong eligibility"],
          "unknowns":["affected count"],"containment":["pause offer"],"owner":"MBCM",
          "next_checkpoint":"2026-07-24T00:00:00+08:00"}
        self.assertTrue(validate_incident.validate(valid)["valid"])
        with self.assertRaises(ModelError):
            validate_incident.validate({**valid,"objects":[{"object_id":"O1"}]})

class CoverageAndDepth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/"evaluations/fixtures/evaluation-catalog.json").read_text())
    def test_120_distinct_and_mode_distribution(self):
        self.assertEqual(self.catalog["total"],120)
        self.assertEqual(self.catalog["counts"],{"standalone":36,"cross_skill":28,"multi_turn":20,"extreme":16,"property":12,"adversarial":8})
        mechanisms=[x["mechanism"] for x in self.catalog["cases"]]
        self.assertEqual(len(set(mechanisms)),120)
    def test_six_dimensional_coverage(self):
        c=self.catalog["coverage"]
        self.assertEqual(len(c["scenarios"]),13); self.assertEqual(len(c["questions"]),13)
        self.assertEqual(len(c["lifecycles"]),9); self.assertEqual(len(c["gates"]),9)
        self.assertEqual(len(c["platforms"]),9); self.assertEqual(len(c["categories"]),9)
        self.assertEqual(len(c["operating_modes"]),8); self.assertEqual(len(c["states"]),8)
        self.assertEqual(c["stress_levels"],["T1","T2","T3","T4","T5","T6"])
        self.assertEqual(len(c["estimation_methods"]),10)
        self.assertEqual(len(self.catalog["high_risk_combinations"]),16)
    def test_multiturn_has_six_real_state_changes(self):
        rows=[x for x in self.catalog["cases"] if x["mode"]=="multi_turn"]
        self.assertTrue(all(len(x["turns"])>=6 for x in rows))
        self.assertTrue(all(all(t["must_preserve"] and t["must_recompute"] for t in x["turns"]) for x in rows))
        self.assertTrue(all(len({t["change"] for t in x["turns"]})==6 for x in rows))
    def test_references_have_distinct_mechanisms(self):
        required=["segmentation-positioning-and-brand.md","gtm-readiness-and-launch.md",
          "offer-campaign-and-calendar.md","channel-orchestration-and-resource-direction.md",
          "brand-health-incrementality-and-learning.md","incident-recovery-reduction-and-exit.md"]
        texts=[(ROOT/"references"/x).read_text() for x in required]
        self.assertEqual(len(texts),len(set(hashlib.sha256(x.encode()).hexdigest() for x in texts)))
        for t in texts:
            self.assertTrue(any(k in t for k in ("失败","阻断","停止")))
            self.assertTrue(any(k in t for k in ("输出","动作","恢复","回滚")))
    def test_goldens_are_ten_distinct_professional_outputs(self):
        files=sorted((ROOT/"evaluations/golden").glob("*.md"))
        self.assertEqual(len(files),10)
        markers=set()
        for p in files:
            t=p.read_text(); self.assertIn("MBCM-2026.01",t); self.assertIn("controlled pilot",t)
            self.assertIn("停止",t); self.assertIn("回滚",t)
            markers.add(next(x for x in t.splitlines() if x.startswith("专属机制：")))
        self.assertEqual(len(markers),10)

if __name__=="__main__": unittest.main(verbosity=2)
