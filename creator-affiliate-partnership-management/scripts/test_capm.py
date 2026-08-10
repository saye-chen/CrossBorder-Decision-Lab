#!/usr/bin/env python3
"""Executable CAPM domain tests: normal, boundary, failure, property and governance."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT.parent / "experiment-causal-assessment" / "scripts"))

from affiliate_order_reconciliation import reconcile, reconcile_touchpoints
from decision_state import validate as validate_state
from partnership_economics import commission_ceiling, fixed_fee_ceiling, partnership_return, program_profit
from portfolio_concentration import calculate as concentration, calculate_multi_basis
from operating_models import creator_ltv, rights_commercial_feasibility, sample_loss, workforce_productivity
from reverse_funnel import calculate as funnel
from validate_cross_skill_handoff import validate as validate_handoff, input_lineage_hash
from validate_historical_replay import validate as validate_replay
from validate_rights_contract import validate as validate_rights
from evaluate_capm_decision import evaluate as evaluate_decision
from validate_schema_instance import validate as validate_schema
from validate_capm_contracts import check as validate_contract
from generate_evaluation_catalog import build as build_catalog
from capm_common import sha256_json
from validate_ecae_handoff import build_receipt, validate_receipt
from ecae_common import content_hash as ecae_content_hash
from validate_consumer_migration import contract_for as ecae_contract_for, load_default_migration

quality_spec = importlib.util.spec_from_file_location("report_quality", ROOT.parents[0] / "scripts/evaluate_report_quality.py")
report_quality = importlib.util.module_from_spec(quality_spec); assert quality_spec and quality_spec.loader; quality_spec.loader.exec_module(report_quality)


def hashes() -> dict:
    return {"input_hash": "a" * 64, "output_hash": "b" * 64, "schema_hash": "c" * 64}


def envelope(**updates) -> dict:
    data = {"contract_id": "CAPM_to_AAMO_authorization", "contract_version": "1.0.0", "message_id": "m1", "idempotency_key": "capm-content-1-paid-v1",
            "correlation_id": "c1", "sender": {"skill": "creator-affiliate-partnership-management", "runtime_version": "CAPM-2026.07"},
            "receiver": {"skill": "advertising-analysis-measurement-optimization", "runtime_version": "AAMO-2026.07"},
            "object": {"canonical_id": "content-1", "object_type": "content", "object_version": "v1"},
            "scope": {"platform": "tiktok", "country": "US", "currency": "USD", "timezone": "America/New_York", "as_of_time": "2026-07-22T00:00:00Z"},
            "status": "proposed", "source_evidence_level": "S3", "causal_evidence_level": "C0",
            "claim_ids": ["cl1"], "evidence_ids": ["ev1"], "calculation_ids": ["calc1"],
            "allowed_uses": ["paid assessment"], "forbidden_uses": ["change rights"], "blocked_actions": [],
            "accepted_by_receiver": {"status": "pending", "reason": None, "checked_at": None}, "lineage": hashes(),
            "validity": {"valid_from": "2026-07-22T00:00:00Z", "expires_at": "2026-08-22T00:00:00Z", "recompute_trigger": ["rights change"]},
            "payload": {"rights_ready": True}}
    data.update(updates); data["lineage"]=dict(data["lineage"],input_hash=input_lineage_hash(data))
    return data


def ecae_context(grade: str = "CE4") -> dict:
    handoff = {
        "schema_version": "1.0.0", "object_id": "ECAE-HANDOFF-CAPM-FIXTURE", "object_version": "1.0.0",
        "status": "handed_off", "as_of_time": "2026-08-10T00:00:00+08:00", "owner": "ECAE",
        "created_at": "2026-08-10T00:00:00+08:00", "updated_at": "2026-08-10T00:00:00+08:00",
        "source_refs": ["ECAE-RESULT-CAPM"], "lineage_refs": ["ECAE-BUNDLE-CAPM"], "jurisdiction_refs": [],
        "parameter_refs": [], "assumption_refs": [], "limitations": ["fixture_non_production"],
        "producer": "ECAE", "consumer": "D10", "causal_result_ref": "ECAE-RESULT-CAPM",
        "estimand_ref": "ECAE-ESTIMAND-CAPM", "causal_evidence_grade": grade, "claim_ceiling": grade,
        "allowed_actions": ["consider_within_consumer_decision_contract"],
        "prohibited_actions": ["automatic_external_write", "treat_as_final_business_decision", "upgrade_causal_grade"],
        "allowed_wording": ["qualified partnership effect"], "prohibited_wording": ["guaranteed incrementality"],
        "applicability": {"population": "authorized_partnerships_v1", "platforms": ["TikTok-US"], "countries": ["US"], "time_window": "2026-08", "treatment_version": "PARTNER-T1"},
        "invalidation_triggers": ["treatment_changed"], "recompute_triggers": ["cost_parameter_changed"],
        "expires_at": "2026-09-10T00:00:00+08:00", "reproducibility_bundle_ref": "ECAE-BUNDLE-CAPM",
        "review_status": "internal_reviewed", "business_owner_decision_required": True, "external_write": False,
        "content_hash": "PENDING"
    }
    handoff["content_hash"] = ecae_content_hash(handoff)
    return {
        "intended_use": "incremental_partnership_support", "handoff": handoff,
        "as_of_time": "2026-08-15T00:00:00+08:00", "active_events": [],
        "target_context": {"platform": "TikTok-US", "country": "US", "population": "authorized_partnerships_v1", "treatment_version": "PARTNER-T1"},
        "consumer_payload": {"effect_estimate": 12.0, "effect_interval": [3.0, 21.0]}
    }


def pending_owner_migration() -> dict:
    migration = copy.deepcopy(load_default_migration())
    contract = ecae_contract_for(migration, "D10")
    contract["acceptance"] = {
        "scope": "controlled_pilot_non_production",
        "status": "pending_consumer_owner",
        "consumer_owner_role": "D10_consumer_owner",
        "signed_record_ref": None,
        "accepted_uses": [],
        "conditions": [],
        "production_status": "not_executed",
        "production_signed_record_ref": None,
    }
    migration["completion_gate"]["all_controlled_pilot_consumer_acceptances_signed"] = False
    migration["completion_gate"]["wp11_controlled_pilot_complete"] = False
    return migration


class EconomicsTests(unittest.TestCase):
    def test_commission_ceiling(self):
        r = commission_ceiling({"mature_net_revenue": 1000, "commission_base": 900, "target_profit": 100,
                                "non_commission_costs": [{"cost_id": "cogs", "amount": 400}, {"cost_id": "fulfillment", "amount": 100}]})
        self.assertAlmostEqual(r["max_commission_rate"], 400 / 900)

    def test_duplicate_cost_is_blocked(self):
        with self.assertRaisesRegex(ValueError, "duplicate cost_id"):
            commission_ceiling({"mature_net_revenue": 100, "commission_base": 100, "target_profit": 0,
                                "non_commission_costs": [{"cost_id": "refund", "amount": 10}, {"cost_id": "refund", "amount": 10}]})

    def test_cost_deletion_changes_result_and_lineage(self):
        original={"mature_net_revenue":1000,"commission_base":900,"target_profit":100,"non_commission_costs":[{"cost_id":"cogs","amount":400},{"cost_id":"refund","amount":100}]}
        mutated=json.loads(json.dumps(original)); mutated["non_commission_costs"].pop()
        self.assertNotEqual(commission_ceiling(original)["max_commission_rate"],commission_ceiling(mutated)["max_commission_rate"])
        self.assertNotEqual(sha256_json(original),sha256_json(mutated))

    def test_negative_ceiling_blocks_cash(self):
        r = fixed_fee_ceiling({"mature_revenue": 100, "target_profit": 20, "non_fixed_costs": [{"cost_id": "all", "amount": 90}]})
        self.assertEqual((r["status"], r["max_fixed_fee"]), ("blocked", 0))

    def test_attributed_not_incremental(self):
        r = partnership_return({"controllable_investment": 100, "contribution": 150, "causal_evidence_level": "C0"})
        self.assertEqual((r["metric"], r["status"]), ("attributed_return", "inconclusive"))

    def test_legacy_c2_is_not_incremental(self):
        r = partnership_return({"controllable_investment": 100, "contribution": 150, "causal_evidence_level": "C2"})
        self.assertEqual((r["metric"], r["status"]), ("attributed_return", "inconclusive"))
        self.assertTrue(r["legacy_label_non_equivalent"])
        self.assertEqual(r["forbidden_metric"], "incremental_return")

    def test_f01_pending_owner_keeps_return_attributed(self):
        context = ecae_context()
        receipt = build_receipt(context, migration=pending_owner_migration())
        self.assertEqual(receipt["decision"], "hold_pending_consumer_acceptance")
        self.assertFalse(receipt["incremental_claim_allowed"])

    def test_exact_owner_accepted_f01_receipt_can_qualify_incremental(self):
        migration = load_default_migration()
        receipt = build_receipt(ecae_context(), migration=migration)
        self.assertEqual(receipt["decision"], "accept")
        self.assertTrue(receipt["incremental_claim_allowed"])
        self.assertEqual(validate_receipt(receipt, migration=migration), [])

    def test_fixture_acceptance_cannot_replay_against_pending_authority(self):
        receipt = build_receipt(ecae_context())
        errors = validate_receipt(receipt, migration=pending_owner_migration())
        self.assertIn("$.accepted_by_consumer_owner:authoritative_acceptance_missing", errors)
        self.assertIn("$.consumer_owner_acceptance_ref:authoritative_reference_mismatch", errors)

    def test_expired_f01_handoff_requests_recompute(self):
        context = ecae_context()
        context["handoff"]["expires_at"] = "2026-08-14T00:00:00+08:00"
        context["handoff"]["content_hash"] = ecae_content_hash(context["handoff"])
        receipt = build_receipt(context)
        self.assertEqual(receipt["decision"], "request_recompute")
        self.assertIn("HANDOFF_EXPIRED", receipt["reasons"])
        self.assertFalse(receipt["incremental_claim_allowed"])

    def test_receipt_hash_tampering_fails_closed(self):
        receipt = build_receipt(ecae_context())
        receipt["causal_evidence_grade"] = "CE5"
        self.assertIn("$.receipt_hash:mismatch", validate_receipt(receipt))

    def test_program_profit_is_scenario_only_without_f01_receipt(self):
        result = program_profit({"incremental_contribution_low": 10, "incremental_contribution_mid": 20, "incremental_contribution_high": 30, "program_costs": []})
        self.assertEqual(result["evidence_semantics"], "scenario_not_incremental")
        self.assertEqual(result["forbidden_claim"], "incremental_program_profit")

    def test_program_interval_order(self):
        with self.assertRaisesRegex(ValueError, "low <= mid <= high"):
            program_profit({"incremental_contribution_low": 10, "incremental_contribution_mid": 5,
                            "incremental_contribution_high": 20, "program_costs": []})

    def test_program_cash_trough_blocks_new_commitment(self):
        r = program_profit({"incremental_contribution_low":100,"incremental_contribution_mid":120,"incremental_contribution_high":140,"program_costs":[],"opening_cash":10,
                            "cash_events":[{"event_id":"fee","at":"2026-01-01","amount":-20},{"event_id":"settlement","at":"2026-02-01","amount":50}]})
        self.assertEqual((r["status"],r["cash_trough"]),("blocked",-10))


class ModelTests(unittest.TestCase):
    def test_sample_loss_and_recovery(self):
        r = sample_loss({"sample_count":10,"unit_product_cost":20,"unit_logistics_cost":5,"publication_rate":.6,"recoverable_rate":.25})
        self.assertEqual((r["unpublished_count"], r["unrecovered_sample_loss"]), (4, 80))

    def test_sample_loss_rejects_invalid_rate(self):
        with self.assertRaises(ValueError): sample_loss({"sample_count":1,"unit_product_cost":1,"unit_logistics_cost":1,"publication_rate":1.1})

    def test_rights_feasibility_does_not_claim_paid_incrementality(self):
        r = rights_commercial_feasibility({"rights_fee":100,"commercial_cost_ceiling":120,"required_rights":["paid"],"granted_rights":["paid"]})
        self.assertEqual((r["aamo_status"], r["forbidden_claim"]), ("candidate_only", "paid_media_incrementality"))

    def test_rights_feasibility_blocks_missing_use(self):
        self.assertEqual(rights_commercial_feasibility({"rights_fee":10,"commercial_cost_ceiling":20,"required_rights":["ai"],"granted_rights":[]})["status"], "blocked")

    def test_creator_ltv_discounted(self):
        r = creator_ltv({"contribution_by_period":[100,100,100],"retention_rate":.5,"discount_rate":0})
        self.assertEqual(r["creator_ltv"], 175)

    def test_creator_ltv_rejects_retention_over_one(self):
        with self.assertRaises(ValueError): creator_ltv({"contribution_by_period":[1],"retention_rate":1.1,"discount_rate":0})

    def test_workforce_productivity(self):
        r = workforce_productivity({"effective_publications":40,"bd_fte":2,"periods":2,"managed_partners":100})
        self.assertEqual((r["publications_per_fte_period"],r["partners_per_fte"]),(10,50))

    def test_workforce_productivity_rejects_zero_staff(self):
        with self.assertRaises(ValueError): workforce_productivity({"effective_publications":1,"bd_fte":0,"periods":1})
    def test_reverse_funnel(self):
        r = funnel({"target_deliveries": 20, "stages": [{"name": "reply", "rate": .2}, {"name": "publish", "rate": .5}]})
        self.assertEqual(r["required_candidates"], 200)

    def test_funnel_rejects_zero(self):
        with self.assertRaises(ValueError): funnel({"target_deliveries": 1, "stages": [{"name": "x", "rate": 0}]})

    def test_concentration_order_invariant(self):
        a = concentration({"basis": "profit", "values": {"a": 60, "b": 30, "c": 10}})
        b = concentration({"basis": "profit", "values": {"c": 10, "a": 60, "b": 30}})
        self.assertAlmostEqual(a["hhi"], b["hhi"])

    def test_multi_basis_concentration_does_not_collapse_to_gmv(self):
        r = calculate_multi_basis({"bases":{"mature_contribution":{"a":90,"b":10},"rights_expiry":{"a":20,"b":80}}})
        self.assertFalse(r["single_basis_decision_forbidden"])

    def test_order_conservation(self):
        r = reconcile({"raw_attributed": 500, "duplicate": 20, "confirmed_fraud": 30, "mature_refund_chargeback": 50, "mature_valid": 400, "pending": 0, "causal_evidence_level": "C0"})
        self.assertTrue(r["conservation"]); self.assertEqual(r["causal_status"], "inconclusive")

    def test_order_conservation_failure(self):
        with self.assertRaisesRegex(ValueError, "conservation"):
            reconcile({"raw_attributed": 10, "mature_valid": 9})

    def test_duplicate_touchpoint_blocks_reconciliation(self):
        base={"raw_attributed":1,"mature_valid":1,"touchpoints":[{"order_id":"o1","partner_id":"p1","touch_type":"click"},{"order_id":"o1","partner_id":"p1","touch_type":"click"}]}
        self.assertEqual(reconcile_touchpoints(base)["touchpoint_status"], "blocked")


class RightsAndStateTests(unittest.TestCase):
    def rights(self):
        grid = {"platform": ["tiktok"], "use": ["organic"], "territory": ["US"], "edit": ["trim"], "identity_use": ["credit"], "ai_use": ["none"]}
        return {"rights_id": "r1", "rights_version":"rv1", "content_id": "c1", "content_version":"cv1", "creator_id": "cr1", "start_at": "2026-01-01T00:00:00Z", "end_at": "2027-01-01T00:00:00Z", "as_of_time": "2026-07-22T00:00:00Z", "granted": grid, "requested": grid, "requested_actions": ["publish"], "evidence_ids": ["e1"]}

    def test_rights_exact_use(self): self.assertEqual(validate_rights(self.rights())["status"], "validated")

    def test_rights_do_not_infer_ai(self):
        data = self.rights(); data["requested"] = dict(data["requested"]); data["requested"]["ai_use"] = ["voice_clone"]
        self.assertEqual(validate_rights(data)["status"], "blocked")

    def test_expired_rights(self):
        data = self.rights(); data["as_of_time"] = "2028-01-01T00:00:00Z"
        self.assertIn("outside_valid_period", validate_rights(data)["blocked_reasons"])

    def test_stale_rights_content_version_is_blocked(self):
        data=self.rights(); data["requested_content_version"]="cv2"
        self.assertIn("stale_rights_content_version",validate_rights(data)["blocked_reasons"])

    def test_progressive_superseded_action(self):
        parent = {"report_id": "r1", "object_id": "o1", "object_version": "v1", "current_actions": ["publish"]}
        data = {"report_id": "r2", "parent_report_id": "r1", "object_id": "o1", "object_version": "v2", "changed_fields": ["rights"], "new_evidence_ids": ["e2"], "affected_claims": ["c1"], "affected_calculations": ["calc1"], "preserved_constraints": ["g1"], "superseded_actions": ["publish"], "current_actions": ["publish"], "next_recompute_trigger": ["new rights"]}
        self.assertFalse(validate_state(data, parent)["valid"])

    def test_progressive_valid_parent_chain(self):
        parent = {"report_id": "r1", "object_id": "o1", "object_version": "v1", "current_actions": ["investigate"]}
        data = {"report_id": "r2", "parent_report_id": "r1", "object_id": "o1", "object_version": "v2", "changed_fields": ["rights"], "new_evidence_ids": ["e2"], "affected_claims": ["c1"], "affected_calculations": ["calc1"], "preserved_constraints": ["g1"], "superseded_actions": [], "current_actions": ["investigate", "renew"], "next_recompute_trigger": ["new rights"]}
        self.assertTrue(validate_state(data, parent)["valid"])


class IntegrationGovernanceTests(unittest.TestCase):
    def test_valid_envelope(self): self.assertTrue(validate_handoff(envelope())["valid"])

    def test_validated_needs_evidence(self):
        self.assertFalse(validate_handoff(envelope(status="validated", evidence_ids=[]))["valid"])

    def test_incremental_label_blocked_at_c0(self):
        self.assertFalse(validate_handoff(envelope(payload={"incremental_orders": 10}))["valid"])

    def test_incremental_label_also_blocked_at_legacy_c2(self):
        data = envelope(causal_evidence_level="C2", payload={"incremental_orders": 10})
        self.assertIn("invalid:incremental_without_f01_consumer_receipt", validate_handoff(data)["errors"])

    def test_decision_evaluator_never_maps_legacy_c3_to_incremental(self):
        case = copy.deepcopy(build_catalog()["cases"][0]["script_input"])
        case["causal_evidence_level"] = "C3"
        result = evaluate_decision(case)
        self.assertEqual(result["causal_label"], "legacy_c_label_non_equivalent")
        self.assertIn("incremental", result["forbidden_claims"])

    def test_affiliate_reconciliation_never_maps_legacy_c3_to_incremental(self):
        result = reconcile({"raw_attributed": 10, "mature_valid": 10, "causal_evidence_level": "C3"})
        self.assertEqual(result["causal_status"], "legacy_c_label_non_equivalent")
        self.assertFalse(result["incremental_claim_allowed"])

    def test_allowed_forbidden_conflict(self):
        self.assertFalse(validate_handoff(envelope(allowed_uses=["x"], forbidden_uses=["x"]))["valid"])

    def test_idempotency_duplicate_is_blocked(self):
        self.assertFalse(validate_handoff(envelope(), {"capm-content-1-paid-v1"})["valid"])

    def test_expired_message_is_blocked(self):
        data = envelope(); data["scope"] = dict(data["scope"], as_of_time="2026-09-01T00:00:00Z")
        self.assertFalse(validate_handoff(data)["valid"])

    def test_currency_change_without_lineage_recompute_is_blocked(self):
        data=envelope(); data["scope"]=dict(data["scope"],currency="EUR")
        self.assertIn("invalid:input_hash_mismatch",validate_handoff(data)["errors"])

    def test_copied_evidence_id_is_rejected_by_decision_evaluator(self):
        case=build_catalog()["cases"][0]["script_input"]; mutated=json.loads(json.dumps(case)); mutated["evidence"].append(dict(mutated["evidence"][0]))
        with self.assertRaisesRegex(ValueError,"unique"): evaluate_decision(mutated)

    def test_unavailable_receiver_cannot_accept(self):
        self.assertFalse(validate_handoff(envelope(receiver={"skill": "LCR", "runtime_version": "unavailable"}, accepted_by_receiver={"status": "accepted", "reason": None, "checked_at": "2026-07-22T00:00:00Z"}))["valid"])

    def test_replay_gate_stays_controlled(self):
        r = validate_replay({"production_ready": False, "cases": []})
        self.assertEqual((r["production_ready"], r["maturity"]), (False, "controlled pilot"))

    def test_replay_rejects_formal_but_unreviewed_cases(self):
        case = {"case_id": "c", "case_type": "creator", "authorization_reference": "auth", "deidentified": True,
                "input_hash": "a"*64, "result_hash": "b"*64, "actual_outcome": "profit", "maturity_checked_at": "2026-07-22",
                "independent_review": True, "bias_and_calibration": "ok", "failure_or_exit_covered": True}
        self.assertFalse(validate_replay({"production_ready": True, "cases": [case, dict(case, case_id="c2", case_type="affiliate"), dict(case, case_id="c3")]})["valid"])

    def test_schemas_parse(self):
        for path in (ROOT / "schemas").glob("*.json"): json.loads(path.read_text(encoding="utf-8"))

    def test_schemas_execute_not_just_parse(self):
        cross = json.loads((ROOT / "schemas/cross_skill_envelope.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_schema(envelope(), cross), [])
        invalid = envelope(); invalid["scope"] = dict(invalid["scope"], country="USA")
        self.assertTrue(validate_schema(invalid, cross))
        rights_schema = json.loads((ROOT / "schemas/rights_record.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_schema(RightsAndStateTests().rights(), rights_schema), [])

    def test_every_new_schema_accepts_valid_and_rejects_required_deletion(self):
        t="2026-07-22T00:00:00Z"; t2="2026-08-22T00:00:00Z"
        samples={
          "creator_candidate_card":{"creator_id":"cr1","object_version":"v1","platform":"TikTok","country":"US","as_of_time":t,"identity_status":"validated","source_evidence_level":"S3","allowed_actions":["contact"],"blocked_actions":[]},
          "creator_due_diligence":{"creator_id":"cr1","object_version":"v1","checked_at":t,"identity":"validated","audience":"estimated","brand_safety":"pass","commercial_density":"measured","fulfillment_reliability":"estimated","counterevidence":["limited history"],"decision":"test"},
          "collaboration_contract":{"collaboration_id":"co1","contract_version":"v1","creator_id":"cr1","brand_entity":"brand","payee_entity":"creator","currency":"USD","deliverables":["video"],"rights_id":"r1","payment_terms":{"milestone":"accepted"},"termination":{"notice":"written"},"effective_at":t,"expires_at":t2},
          "affiliate_partner_record":{"partner_id":"p1","object_version":"v1","program_id":"ap1","platform":"DTC","country":"US","payee_status":"validated","commission_basis":"mature_net_revenue","attribution_status":"attributed","settlement_status":"reconciled","fraud_status":"clear","lifecycle":"productive"},
          "decision_card":{"report_id":"r1","object_id":"o1","object_version":"v1","as_of_time":t,"input_quality":"Q2","gate_results":{"G1A":{},"G1B":{},"G2":{},"G3":{},"G4":{},"G5":{},"G6":{}},"decision":"test","allowed_actions":["contact"],"blocked_actions":["pay"],"success":["verified"],"stop":["P0"],"rollback":["restore v0"],"exit":["close"]},
          "decision_memo":{"card":{"report_id":"r1"},"alternatives":[{"id":"a"},{"id":"b"}],"do_nothing":{"id":"none"},"economics":{"status":"inconclusive"},"rights":{"status":"validated"},"counterevidence":["weak history"],"dependencies":[],"remaining_exposure":[]},
          "diligence_report":{"memo":{"report_id":"r1"},"objects":[{"id":"o1"}],"evidence_ledger":[{"id":"e1"}],"calculations":[{"id":"c1"}],"stress_tests":[{"id":"s1"}],"cross_skill_status":[],"review":{"status":"self_reviewed_only"}},
          "incident_report":{"incident_id":"i1","object_id":"o1","severity":"P1","detected_at":t,"freeze_scope":["payment"],"uncontested_obligations":["earned fee"],"evidence_preservation":["ledger"],"recovery_sequence":["verify"],"rollback":["restore"],"closure_evidence":[]},
          "capm_to_cidm_economics":{"partnership_id":"p1","object_version":"v1","mature_contribution_low":1,"mature_contribution_mid":2,"mature_contribution_high":3,"cash_trough":0,"causal_evidence_level":"C0","calculation_ids":["c1"],"forbidden_uses":["automatic capital change"]},
          "capm_to_aamo_authorization":{"content_id":"c1","rights_id":"r1","platform":"TikTok","country":"US","valid_from":t,"expires_at":t2,"allowed_paid_uses":["spark"],"forbidden_uses":["ai clone"],"edit_rights":["trim"],"identity_use":["credit"],"attribution_required":True,"rights_fee":100,"status":"validated"},
          "capm_to_lifd_demand_forecast":{"campaign_id":"c1","sku":"s1","country":"US","platform":"TikTok","window_start":t,"window_end":t2,"demand_low":1,"demand_mid":2,"demand_high":3,"confidence":"low","evidence_ids":["e1"],"allowed_interpretation":["capacity planning"]},
          "cim_to_capm_competitive_event":{"event_id":"e1","competitor_object_id":"co1","creator_id":"cr1","observed_at":t,"signal":{"type":"new content"},"source_evidence_level":"S1","confidence":"low","allowed_interpretation":["investigate"],"prohibited_interpretation":["copy competitor price"]},
          "capm_to_vlb_content_evidence":{"content_id":"c1","creator_id":"cr1","collaboration_id":"co1","content_version":"v1","platform":"TikTok","country":"US","published_at":t,"brief_version":"b1","required_claims":["fact"],"prohibited_claims":["cure"],"delivery_acceptance":"accepted","rights_id":"r1","performance_observations":[{"traffic_type":"unknown"}]},
          "capm_to_cig_customer_promise":{"creator_id":"cr1","content_id":"c1","claim_id":"cl1","claim_hash":"a"*64,"promise_type":"performance","product_sku":"s1","audience":"adult","platform":"TikTok","country":"US","exposure_window":{"start":t},"consent_and_privacy_basis":"authorized deidentified analysis","deidentification_status":"deidentified","evidence_ids":["e1"],"prohibited_interpretation":["creator caused complaint"]},
          "plco_to_capm_page_breakpoint":{"page_id":"p1","page_version":"v1","sku":"s1","platform":"DTC","country":"US","traffic_source_context":"creator link","creator_or_content_id":"c1","observation_window":{"start":t},"funnel_step":"pdp","breakpoint_type":"link","diagnostic_status":"validated","confounders":[],"evidence_ids":["e1"],"allowed_interpretation":["adjust acceptance"],"prohibited_interpretation":["page fixed"]}
        }
        for name,sample in samples.items():
            schema=json.loads((ROOT/f"schemas/{name}.schema.json").read_text(encoding="utf-8"))
            self.assertEqual(validate_schema(sample,schema),[],name)
            required=schema["required"][0]; invalid=dict(sample); invalid.pop(required)
            self.assertTrue(validate_schema(invalid,schema),(name,required))

    def test_cross_field_contract_interval_and_time_order(self):
        economics={"partnership_id":"p1","object_version":"v1","mature_contribution_low":3,"mature_contribution_mid":2,"mature_contribution_high":4,"cash_trough":0,"causal_evidence_level":"C0","calculation_ids":["c1"],"forbidden_uses":["capital_decision"]}
        self.assertFalse(validate_contract("capm_to_cidm_economics", economics)["valid"])
        auth={"content_id":"c1","rights_id":"r1","platform":"TikTok","country":"US","valid_from":"2027-01-01T00:00:00Z","expires_at":"2026-01-01T00:00:00Z","allowed_paid_uses":["spark"],"forbidden_uses":["spark"],"edit_rights":[],"identity_use":[],"attribution_required":True,"rights_fee":0,"status":"blocked"}
        result=validate_contract("capm_to_aamo_authorization",auth)
        self.assertTrue(any("time_order" in e for e in result["errors"])); self.assertTrue(any("overlap" in e for e in result["errors"]))

    def test_required_governance_and_unique_kernels(self):
        required = [ROOT / "references/professional-depth-governance.md", ROOT / "references/skill-integration-protocol.md",
                    ROOT / "references/data-contract-and-automation.md", ROOT / "references/output-protocols/professional-report-delivery.md"]
        kernels = []
        paths = list(dict.fromkeys(required + list((ROOT / "references").glob("*.md"))))
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIn("专属决策内核", text, path)
            kernels.append(text.split("专属决策内核", 1)[1])
        self.assertEqual(len(kernels), len(set(kernels)))

    def test_complete_s01_s13_and_a01_a08_registry(self):
        data=json.loads((ROOT/"references/scenario-lifecycle-registry.json").read_text(encoding="utf-8"))
        self.assertEqual([x["id"] for x in data["creator_scenarios"]],[f"S{i:02d}" for i in range(1,14)])
        self.assertEqual([x["id"] for x in data["affiliate_scenarios"]],[f"A{i:02d}" for i in range(1,9)])
        self.assertTrue(all(x["lifecycle"] and x["primary_gate"] for x in data["creator_scenarios"]+data["affiliate_scenarios"]))

    def test_platform_cards_are_mechanically_distinct_and_dynamic(self):
        text=(ROOT/"references/platform-expert-cards.md").read_text(encoding="utf-8")
        for platform in ("TikTok Shop","Amazon Associates","Shopify/DTC","Shopee","Lazada"): self.assertIn(f"## {platform}",text)
        self.assertGreaterEqual(text.count("### 首要失败与恢复"),5)
        self.assertGreaterEqual(text.count("### 任务时动态核验"),5)
        self.assertIn("不得套用其他站点规则",text)

    def test_open_decisions_are_explicitly_resolved(self):
        data=json.loads((ROOT.parents[0]/"governance/capm-open-decisions.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["decisions"]),8)
        self.assertTrue(all(x["status"]=="resolved" and x["question"] and x["decision"] for x in data["decisions"]))

    def test_evaluation_catalog(self):
        data = json.loads((ROOT / "evaluations/fixtures/evaluation-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(data, build_catalog(), "generated catalog must be reproducible from its source")
        self.assertEqual(data["count"], 120)
        self.assertEqual(data["coverage"], {"solo": 36, "cross_skill": 28, "multi_turn": 24, "extreme": 20, "property": 12})
        cases = data["cases"]
        self.assertEqual(len({json.dumps(c["script_input"], sort_keys=True) for c in cases}), 120)
        self.assertEqual(len({c["primary_mechanism"] for c in cases}), 120)
        self.assertEqual({c["mode"] for c in cases}, {"solo", "cross_skill", "multi_turn", "extreme", "property"})
        for case in cases:
            result = evaluate_decision(case["script_input"])
            for field, expected in case["expected_output"].items():
                self.assertEqual(result[field], expected, (case["id"], field))
            self.assertTrue(case["required_assertions"] and case["forbidden"])
            if case["mode"] == "cross_skill": self.assertTrue(case["participants"])
            if case["mode"] == "multi_turn":
                self.assertGreaterEqual(len(case["turns"]), 4)
                self.assertEqual([turn["current_actions"][0] for turn in case["turns"]], case["expected_transition"])
                previous = None
                for turn in case["turns"]:
                    result = validate_state(turn, previous)
                    self.assertEqual(result["valid"], turn["expected_valid"], (case["id"], turn, result))
                    previous = turn
            if case["mode"] == "extreme":
                self.assertTrue(case["incident_controls"]["preserve_uncontested_obligations"])
                self.assertEqual(len(case["incident_controls"]["recovery_requires"]), 3)
        participants = {p for case in cases if case["mode"] == "cross_skill" for p in case["participants"]}
        self.assertEqual(participants, {"CIDM", "CIM", "VLB", "CIG", "AAMO", "LIFD", "PLCO"})
        transitions = {tuple(case["expected_transition"]) for case in cases if case["mode"] == "multi_turn"}
        self.assertEqual(len(transitions), 24)
        gate_counts = data["distributions"]["primary_gate"]
        for gate in ("G1A","G1B","G2","G3","G4","G5","G6"): self.assertGreaterEqual(gate_counts[gate], 8, gate)
        self.assertGreaterEqual(data["distributions"]["outcome_class"]["normal"], 24)
        for group in ("affiliate_operations","creator_diligence_lifecycle","data_automation_quality","economics_negotiation_portfolio","incident_recovery","platform_country","rights_contract_exit","sample_brief_delivery"):
            self.assertGreaterEqual(data["distributions"]["capability_group"][group], 8, group)
        self.assertLessEqual(max(data["distributions"]["capability_group"].values()), 42)

    def test_all_five_golden_reports_pass_full_professional_gate(self):
        files = sorted((ROOT / "evaluations/golden").glob("*.md"))
        self.assertEqual(len(files), 5)
        for path in files:
            result = report_quality.score_report(path.read_text(encoding="utf-8"), "full")
            self.assertEqual((result["result"], result["score"]), ("PASS", 100.0), (path, result))

    def test_golden_critical_section_mutations_fail(self):
        text = (ROOT / "evaluations/golden/decision-memo.md").read_text(encoding="utf-8")
        for heading in ("证据与反证", "经济与计算", "主权与联动", "行动计划"):
            mutated = text.replace(f"## {heading}", f"## 已删除-{heading}")
            self.assertEqual(report_quality.score_report(mutated, "full")["result"], "FAIL", heading)


if __name__ == "__main__": unittest.main(verbosity=2)
