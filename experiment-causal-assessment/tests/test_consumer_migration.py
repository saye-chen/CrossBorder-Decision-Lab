import copy
import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

from compare_legacy_f01 import compare_legacy_f01
from ecae_common import ECAEError, content_hash
from evaluate_consumer_handoff import evaluate_consumer_handoff
from evaluate_consumer_rollback import evaluate_consumer_rollback
from validate_consumer_acceptance import validate_consumer_acceptance
from validate_consumer_migration import contract_for, validate_consumer_migration
from validate_schema import validate_object


def load_migration():
    return json.loads((ROOT / "integrations" / "consumer-migration.json").read_text(encoding="utf-8"))


def handoff(domain_id="D01", grade="CE4", *, expires_at="2026-09-10T00:00:00+08:00", review_status="internal_reviewed"):
    value = {
        "schema_version": "1.0.0",
        "object_id": f"ECAE-HANDOFF-TEST-{domain_id}",
        "object_version": "1.0.0",
        "status": "handed_off",
        "as_of_time": "2026-08-10T00:00:00+08:00",
        "owner": "ECAE",
        "created_at": "2026-08-10T00:00:00+08:00",
        "updated_at": "2026-08-10T00:00:00+08:00",
        "source_refs": ["ECAE-RESULT-TEST"],
        "lineage_refs": ["ECAE-BUNDLE-TEST"],
        "jurisdiction_refs": [],
        "parameter_refs": [],
        "assumption_refs": [],
        "limitations": ["fixture_non_production"],
        "producer": "ECAE",
        "consumer": domain_id,
        "causal_result_ref": "ECAE-RESULT-TEST",
        "estimand_ref": "ECAE-ESTIMAND-TEST",
        "causal_evidence_grade": grade,
        "claim_ceiling": grade,
        "allowed_actions": ["consider_within_consumer_decision_contract"],
        "prohibited_actions": ["automatic_external_write", "treat_as_final_business_decision", "upgrade_causal_grade"],
        "allowed_wording": ["qualified effect within the bound scope"],
        "prohibited_wording": ["guaranteed", "universal", "automatic business decision"],
        "applicability": {
            "population": "authorized_population_v1",
            "platforms": ["Amazon-US"],
            "countries": ["US"],
            "time_window": "2026-08-01/2026-08-31",
            "treatment_version": "T1"
        },
        "invalidation_triggers": ["treatment_changed", "data_correction"],
        "recompute_triggers": ["metric_definition_changed", "cost_parameter_changed"],
        "expires_at": expires_at,
        "reproducibility_bundle_ref": "ECAE-BUNDLE-TEST",
        "review_status": review_status,
        "business_owner_decision_required": True,
        "external_write": False,
        "content_hash": "PENDING"
    }
    value["content_hash"] = content_hash(value)
    return value


def qualified_payload(contract):
    fields = contract["use_requirements"][0]["required_payload_fields"]
    values = {
        "effect_estimate": 1.5,
        "effect_interval": [0.5, 2.5],
        "economic_parameter_snapshot": "PPFC-PARAM-1",
        "incremental_contribution": 12.5,
        "policy_value_interval": [1.0, 3.0],
        "policy_constraints": ["consent", "frequency_cap"],
    }
    return {field: values[field] for field in fields}


def evaluation_input(migration, domain_id, *, grade="CE4", expires_at="2026-09-10T00:00:00+08:00"):
    contract = contract_for(migration, domain_id)
    requirement = contract["use_requirements"][0]
    return {
        "migration": migration,
        "domain_id": domain_id,
        "intended_use": requirement["use"],
        "requested_claim_grade": requirement["minimum_grade"],
        "handoff": handoff(domain_id, grade, expires_at=expires_at),
        "as_of_time": "2026-08-15T00:00:00+08:00",
        "active_events": [],
        "target_context": {"platform": "Amazon-US", "country": "US", "population": "authorized_population_v1", "treatment_version": "T1"},
        "consumer_payload": qualified_payload(contract),
    }


def acceptance_record(migration, domain_id="D01", identity="CIDM Owner"):
    contract = contract_for(migration, domain_id)
    use = contract["use_requirements"][0]["use"]
    value = {
        "schema_version": "1.0.0",
        "record_id": f"ECAE-CONSUMER-ACCEPTANCE-{domain_id}-FIXTURE-1",
        "migration_id": migration["migration_id"],
        "domain_id": domain_id,
        "contract_version": contract["contract_version"],
        "contract_content_hash": content_hash(contract),
        "acceptance_scope": "controlled_pilot_non_production",
        "decision": "accepted",
        "reviewed_at": "2026-08-20T00:00:00+08:00",
        "expires_at": "2026-10-20T00:00:00+08:00",
        "reviewer": {"identity": identity, "role": contract["acceptance"]["consumer_owner_role"], "affiliation": "consumer_domain", "independent_of_producer_implementation": True},
        "authorization_basis": "test fixture",
        "evidence_refs": ["ECAE-WP11-CONSUMER-DUAL-RUN-FIXTURE"],
        "accepted_uses": [use],
        "conditions": [],
        "consumer_owner_attestation": True,
        "producer_self_acceptance": False,
        "production_evidence_claimed": False,
        "external_write": False,
        "content_hash": "0" * 64,
    }
    value["content_hash"] = content_hash(value)
    return value


class ConsumerMigrationContractTests(unittest.TestCase):
    def test_schema_registry_assets_and_evidence_gates_validate(self):
        migration = load_migration()
        result = validate_consumer_migration(migration)
        self.assertTrue(validate_object(migration, "consumer-migration.schema.json", verify_hash=False)["valid"])
        self.assertEqual(result["consumer_count"], 13)
        self.assertEqual(result["local_fixture_verified"], 13)
        self.assertEqual(result["local_rollback_verified"], 13)
        self.assertEqual(result["production_dual_runs_completed"], 0)
        self.assertEqual(result["controlled_pilot_consumer_acceptances"], 13)
        self.assertEqual(result["production_consumer_acceptances"], 0)
        self.assertTrue(result["wp11_controlled_pilot_complete"])
        self.assertFalse(result["l4_production_acceptance_complete"])

    def test_all_domains_are_exact_and_registry_bound(self):
        migration = load_migration()
        domains = [item["domain_id"] for item in migration["consumers"]]
        self.assertEqual(domains, [f"D{i:02d}" for i in range(1, 14)])
        registry = json.loads((REPO / "governance" / "domain-architecture-registry.json").read_text(encoding="utf-8"))
        authoritative = {item["domain_id"]: item for item in registry["domains"]}
        for item in migration["consumers"]:
            self.assertEqual((item["skill"], item["runtime_prefix"]), (authoritative[item["domain_id"]]["skill"], authoritative[item["domain_id"]]["runtime_prefix"]))

    def test_no_legacy_label_can_auto_upgrade(self):
        migration = load_migration()
        for item in migration["consumers"]:
            self.assertEqual(item["legacy_automatic_ceiling"], "CE0")
            self.assertLessEqual(int(item["legacy_reassessment_ceiling"][-1]), 3)
            self.assertTrue(item["prohibited_legacy_mappings"])
        d10 = contract_for(migration, "D10")
        self.assertIn("C2_to_CE4", d10["prohibited_legacy_mappings"])
        self.assertEqual(d10["domain_specific_mappings"][0]["classification"], "non_equivalent")

    def test_empty_legacy_inventory_needs_explicit_reason(self):
        migration = load_migration()
        for domain_id in ("D04", "D05"):
            assets = contract_for(migration, domain_id)["legacy_assets"]
            self.assertEqual(assets["paths"], [])
            self.assertTrue(assets["absence_reason"])
        broken = copy.deepcopy(migration)
        contract_for(broken, "D04")["legacy_assets"]["absence_reason"] = None
        with self.assertRaises(ECAEError) as raised:
            validate_consumer_migration(broken)
        self.assertEqual(raised.exception.code, "LEGACY_ASSET_ABSENCE_UNEXPLAINED")

    def test_fixture_evidence_cannot_close_production_gate(self):
        migration = load_migration()
        self.assertTrue(migration["completion_gate"]["local_contract_implementation_complete"])
        self.assertTrue(migration["completion_gate"]["all_controlled_pilot_consumer_acceptances_signed"])
        self.assertTrue(migration["completion_gate"]["wp11_controlled_pilot_complete"])
        self.assertFalse(migration["completion_gate"]["all_production_dual_runs_completed"])
        self.assertFalse(migration["completion_gate"]["all_production_consumer_acceptances_signed"])
        self.assertFalse(migration["completion_gate"]["l4_production_acceptance_complete"])
        broken = copy.deepcopy(migration)
        broken["completion_gate"]["l4_production_acceptance_complete"] = True
        with self.assertRaises(ECAEError) as raised:
            validate_consumer_migration(broken)
        self.assertEqual(raised.exception.code, "L4_PRODUCTION_GATE_MISMATCH")

    def test_d06_d07_and_d10_consumer_side_adapters_are_controlled_pilot_accepted(self):
        migration = load_migration()
        d06 = contract_for(migration, "D06")
        self.assertEqual(d06["dual_run"]["local_fixture_ref"], "pricing-profit-finance-cashflow-decision/integrations/experiment-causal-assessment/acceptance.json")
        acceptance = json.loads((REPO / d06["dual_run"]["local_fixture_ref"]).read_text(encoding="utf-8"))
        self.assertTrue(acceptance["automated_contract_accepted"])
        self.assertFalse(acceptance["production_dual_run_completed"])
        self.assertFalse(acceptance["independent_owner_accepted"])
        self.assertTrue(acceptance["controlled_pilot_owner_accepted"])
        result = subprocess.run(
            [sys.executable, "pricing-profit-finance-cashflow-decision/integrations/experiment-causal-assessment/validate_adapter.py"],
            cwd=REPO, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("controlled_pilot_owner_acceptance=accepted", result.stdout)

        d07 = contract_for(migration, "D07")
        self.assertEqual(d07["dual_run"]["local_fixture_ref"], "logistics-inventory-fulfillment-decision/integrations/experiment-causal-assessment/acceptance.json")
        acceptance = json.loads((REPO / d07["dual_run"]["local_fixture_ref"]).read_text(encoding="utf-8"))
        self.assertTrue(acceptance["automated_contract_accepted"])
        self.assertFalse(acceptance["production_dual_run_completed"])
        self.assertFalse(acceptance["independent_owner_accepted"])
        self.assertTrue(acceptance["controlled_pilot_owner_accepted"])
        result = subprocess.run(
            [sys.executable, "logistics-inventory-fulfillment-decision/integrations/experiment-causal-assessment/validate_adapter.py"],
            cwd=REPO, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("controlled_pilot_owner_acceptance=accepted", result.stdout)

        d10 = contract_for(migration, "D10")
        self.assertEqual(d10["dual_run"]["local_fixture_ref"], "creator-affiliate-partnership-management/integrations/experiment-causal-assessment/acceptance.json")
        acceptance = json.loads((REPO / d10["dual_run"]["local_fixture_ref"]).read_text(encoding="utf-8"))
        self.assertTrue(acceptance["automated_contract_accepted"])
        self.assertFalse(acceptance["production_dual_run_completed"])
        self.assertFalse(acceptance["independent_owner_accepted"])
        self.assertTrue(acceptance["controlled_pilot_owner_accepted"])
        result = subprocess.run(
            [sys.executable, "creator-affiliate-partnership-management/integrations/experiment-causal-assessment/validate_adapter.py"],
            cwd=REPO, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("controlled_pilot_owner_acceptance=accepted", result.stdout)


class ConsumerHandoffTests(unittest.TestCase):
    def test_qualified_handoff_is_accepted_for_all_thirteen_controlled_pilot_uses(self):
        migration = load_migration()
        for domain_id in [f"D{i:02d}" for i in range(1, 14)]:
            inp = evaluation_input(migration, domain_id)
            result = evaluate_consumer_handoff(inp)
            self.assertEqual(result["decision"], "accept", domain_id)
            self.assertTrue(result["causal_wording_allowed"], domain_id)
            self.assertTrue(result["business_owner_decision_required"], domain_id)
            self.assertFalse(result["external_write"], domain_id)

    def test_low_grade_degrades_instead_of_becoming_causal(self):
        migration = load_migration()
        for domain_id in [f"D{i:02d}" for i in range(1, 14)]:
            inp = evaluation_input(migration, domain_id, grade="CE2")
            result = evaluate_consumer_handoff(inp)
            self.assertEqual(result["decision"], "degrade", domain_id)
            self.assertEqual(result["effective_use"], "descriptive_only", domain_id)
            self.assertFalse(result["causal_wording_allowed"], domain_id)

    def test_expiry_and_active_trigger_request_recompute(self):
        migration = load_migration()
        expired = evaluation_input(migration, "D01", expires_at="2026-08-14T00:00:00+08:00")
        result = evaluate_consumer_handoff(expired)
        self.assertEqual(result["decision"], "request_recompute")
        self.assertIn("HANDOFF_EXPIRED", result["reasons"])
        self.assertTrue(result["recompute_required"])
        triggered = evaluation_input(migration, "D01")
        triggered["active_events"] = ["treatment_changed", "cost_parameter_changed"]
        result = evaluate_consumer_handoff(triggered)
        self.assertEqual(result["decision"], "request_recompute")
        self.assertIn("INVALIDATION_TRIGGER:treatment_changed", result["reasons"])
        self.assertIn("RECOMPUTE_TRIGGER:cost_parameter_changed", result["reasons"])

    def test_scope_mismatch_rejects(self):
        inp = evaluation_input(load_migration(), "D08")
        inp["target_context"]["country"] = "GB"
        result = evaluate_consumer_handoff(inp)
        self.assertEqual(result["decision"], "reject")
        self.assertIn("COUNTRY_OUT_OF_SCOPE", result["reasons"])

    def test_d07_missing_incremental_value_is_not_zero_filled(self):
        inp = evaluation_input(load_migration(), "D07")
        inp["consumer_payload"] = {}
        result = evaluate_consumer_handoff(inp)
        self.assertEqual(result["decision"], "reject")
        self.assertIn("MISSING_QUALIFIED_PAYLOAD:incremental_contribution", result["reasons"])
        self.assertTrue(result["incremental_zero_fill_forbidden"])

    def test_exact_owner_acceptance_can_enable_only_the_accepted_use(self):
        migration = load_migration()
        contract = contract_for(migration, "D01")
        use = contract["use_requirements"][0]["use"]
        inp = evaluation_input(migration, "D01")
        result = evaluate_consumer_handoff(inp)
        self.assertEqual(result["decision"], "accept")
        self.assertEqual(result["effective_use"], use)
        self.assertTrue(result["causal_wording_allowed"])
        self.assertFalse(result["external_write"])


class ConsumerAcceptanceTests(unittest.TestCase):
    def test_signed_consumer_owner_record_validates(self):
        migration = load_migration()
        record = acceptance_record(migration)
        self.assertTrue(validate_object(record, "consumer-acceptance.schema.json")["valid"])
        result = validate_consumer_acceptance({"migration": migration, "record": record})
        self.assertTrue(result["valid"])
        self.assertEqual(result["decision"], "accepted")

    def test_producer_cannot_self_accept(self):
        migration = load_migration()
        record = acceptance_record(migration, identity="ECAE")
        with self.assertRaises(ECAEError) as raised:
            validate_consumer_acceptance({"migration": migration, "record": record})
        self.assertEqual(raised.exception.code, "PRODUCER_SELF_ACCEPTANCE_FORBIDDEN")

    def test_acceptance_cannot_create_uncontracted_use(self):
        migration = load_migration()
        record = acceptance_record(migration)
        record["accepted_uses"] = ["automatic_capital_execution"]
        record["content_hash"] = content_hash(record)
        with self.assertRaises(ECAEError) as raised:
            validate_consumer_acceptance({"migration": migration, "record": record})
        self.assertEqual(raised.exception.code, "UNCONTRACTED_USE_ACCEPTED")


class DifferenceAndRollbackTests(unittest.TestCase):
    def dual_input(self, domain_id="D01"):
        base = {"claim_class": "descriptive", "grade_label": "CE2", "scope_key": "US|Amazon|P1|T1|2026-08", "numeric_value": 1.25, "allowed_actions": ["review"]}
        return {"migration": load_migration(), "domain_id": domain_id, "fixture_id": "FIXTURE-1", "run_class": "fixture_non_production", "legacy_result": copy.deepcopy(base), "f01_result": copy.deepcopy(base)}

    def test_exact_semantics_are_equivalent(self):
        report = compare_legacy_f01(self.dual_input())
        self.assertEqual(report["difference_class"], "equivalent")
        self.assertTrue(report["eligible_for_acceptance"])
        self.assertFalse(report["external_write"])

    def test_capm_c2_incremental_mapping_is_blocking(self):
        value = self.dual_input("D10")
        value["legacy_result"].update({"claim_class": "incremental", "grade_label": "C2"})
        value["f01_result"].update({"claim_class": "causal", "grade_label": "CE4"})
        report = compare_legacy_f01(value)
        self.assertFalse(report["eligible_for_acceptance"])
        self.assertIn("legacy_causal_or_incremental_semantics_not_grandfathered", report["blocking_reasons"])
        self.assertIn("legacy_grade_requires_semantic_reassessment", report["blocking_reasons"])

    def test_newly_permissive_action_is_blocking_but_restriction_is_expected(self):
        permissive = self.dual_input()
        permissive["f01_result"]["allowed_actions"] = ["review", "scale"]
        report = compare_legacy_f01(permissive)
        self.assertFalse(report["eligible_for_acceptance"])
        restrictive = self.dual_input()
        restrictive["legacy_result"]["allowed_actions"] = ["review", "scale"]
        report = compare_legacy_f01(restrictive)
        self.assertEqual(report["difference_class"], "expected_restriction")
        self.assertTrue(report["eligible_for_acceptance"])
        self.assertTrue(report["requires_consumer_disposition"])

    def test_rollback_is_idempotent_noncausal_and_unknown_never_zero(self):
        migration = load_migration()
        for domain_id in [f"D{i:02d}" for i in range(1, 14)]:
            value = {"migration": migration, "domain_id": domain_id, "reason": "handoff expired"}
            first = evaluate_consumer_rollback(value)
            second = evaluate_consumer_rollback(value)
            self.assertEqual(first, second, domain_id)
            self.assertFalse(first["causal_wording_allowed"], domain_id)
            self.assertEqual(first["incremental_value"]["state"], "unknown", domain_id)
            self.assertNotIn("value", first["incremental_value"], domain_id)
            self.assertTrue(first["recompute_request"]["required"], domain_id)
            self.assertFalse(first["external_write"], domain_id)


if __name__ == "__main__":
    unittest.main()
