import copy
import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ecae_common import ECAEError, content_hash
from evaluate_consumer_production_run import evaluate_consumer_production_run, f01_source_tree_hash
from validate_consumer_migration import contract_for
from validate_consumer_production_plan import validate_consumer_production_plan


CASE_CLASSES = ["normal", "near_decision_threshold", "negative_or_harm", "expired", "invalidation_triggered", "scope_mismatch", "missing_required_field"]


def migration():
    return json.loads((ROOT / "integrations/consumer-migration.json").read_text(encoding="utf-8"))


def result():
    return {"claim_class": "descriptive", "grade_label": "CE2", "scope_key": "US|Amazon|P1|T1|2026-08", "numeric_value": 1.0, "allowed_actions": ["review"]}


def package(run_class="fixture_non_production"):
    domain_id = "D07"
    contract = contract_for(migration(), domain_id)
    adapter = json.loads((REPO / "logistics-inventory-fulfillment-decision/integrations/experiment-causal-assessment/adapter.json").read_text(encoding="utf-8"))
    cases = []
    for index, case_class in enumerate(CASE_CLASSES, 1):
        case_result = result()
        if case_class == "negative_or_harm":
            case_result["numeric_value"] = -1.0
        if case_class in {"expired", "invalidation_triggered", "scope_mismatch", "missing_required_field"}:
            case_result = {"claim_class": "inconclusive", "grade_label": "CE0", "scope_key": "US|Amazon|P1|T1|2026-08", "numeric_value": None, "allowed_actions": ["request_recompute"] if case_class in {"expired", "invalidation_triggered"} else []}
        cases.append({
            "case_id": f"CASE-{index}",
            "case_class": case_class,
            "snapshot_hash": f"{index:064x}",
            "legacy_result": copy.deepcopy(case_result),
            "f01_result": copy.deepcopy(case_result),
            "difference_disposition": "not_required",
            "evidence_refs": [f"fixture://legacy/{index}", f"fixture://f01/{index}"],
        })
    return {
        "schema_version": "1.0.0",
        "run_id": "ECAE-CONSUMER-RUN-D07-FIXTURE-1",
        "migration_id": migration()["migration_id"],
        "domain_id": domain_id,
        "run_class": run_class,
        "execution_mode": "read_only_shadow_dual_run",
        "frozen_before_results": True,
        "owner_assignment": {"identity": "Miles Chen", "role": "D07_consumer_owner", "independent_of_ecae_implementation": True, "responsibility_accepted": True},
        "data_snapshot": {"source_ref": "fixture://snapshot", "snapshot_hash": "f" * 64, "authorized": True, "read_only": True, "captured_at": "2026-08-10T00:00:00Z", "maximum_event_time": "2026-08-09T23:59:59Z", "business_timezone": "Asia/Shanghai"},
        "code_binding": {"legacy_code_ref": "fixture://legacy", "legacy_code_hash": "1" * 64, "f01_commit_hash": "a" * 40 if run_class == "production_dual_run" else None, "f01_source_tree_hash": f01_source_tree_hash(), "adapter_hash": content_hash(adapter), "contract_hash": content_hash(contract), "environment_refs": ["fixture://legacy-env", "fixture://f01-env"]},
        "numeric_tolerance": 1e-9,
        "cases": cases,
        "rollback_drill": {"executed": True, "trigger": "expiry", "causal_wording_allowed": False, "incremental_state": "unknown", "blocked_actions_enforced": True, "recompute_request_created": True, "business_write_observed": False, "evidence_refs": ["fixture://rollback"]},
        "business_actions_executed": False,
        "external_write": False,
    }


class ConsumerProductionAcceptanceTests(unittest.TestCase):
    def test_plan_binds_all_thirteen_contracts_without_false_production_evidence(self):
        plan = json.loads((ROOT / "integrations/consumer-production-acceptance-plan.json").read_text(encoding="utf-8"))
        output = validate_consumer_production_plan(plan)
        self.assertEqual(output["domain_count"], 13)
        self.assertEqual(output["wave_1"], ["D06", "D07", "D10"])
        self.assertEqual(output["owners_assigned"], 13)
        self.assertEqual(output["fixture_preflights_passed"], 13)
        self.assertEqual(output["production_runs_bound"], 0)
        self.assertFalse(output["l4_production_acceptance_complete"])

    def test_fixture_dual_run_cannot_become_owner_acceptance_evidence(self):
        output = evaluate_consumer_production_run(package())
        self.assertEqual(output["case_count"], 7)
        self.assertFalse(output["eligible_for_owner_acceptance"])
        self.assertEqual(output["next_state"], "evidence_incomplete_or_nonproduction")
        self.assertFalse(output["external_write"])

    def test_fixture_must_bind_current_owner_and_source_tree(self):
        wrong_owner = package()
        wrong_owner["owner_assignment"]["identity"] = "Another Owner"
        with self.assertRaises(ECAEError) as raised:
            evaluate_consumer_production_run(wrong_owner)
        self.assertEqual(raised.exception.code, "PRODUCTION_RUN_OWNER_IDENTITY_MISMATCH")
        stale_source = package()
        stale_source["code_binding"]["f01_source_tree_hash"] = "0" * 64
        with self.assertRaises(ECAEError) as raised:
            evaluate_consumer_production_run(stale_source)
        self.assertEqual(raised.exception.code, "FIXTURE_F01_SOURCE_TREE_HASH_MISMATCH")

    def test_complete_read_only_production_package_can_reach_owner_review_only(self):
        output = evaluate_consumer_production_run(package("production_dual_run"))
        self.assertTrue(output["eligible_for_owner_acceptance"])
        self.assertEqual(output["next_state"], "ready_for_owner_review")
        self.assertTrue(output["consumer_owner_decision_required"])
        self.assertTrue(output["producer_self_acceptance_forbidden"])
        self.assertFalse(output["business_actions_executed"])

    def test_expected_restriction_requires_explicit_owner_disposition(self):
        value = package("production_dual_run")
        value["cases"][0]["legacy_result"]["allowed_actions"] = ["review", "scale"]
        value["cases"][0]["difference_disposition"] = "pending"
        output = evaluate_consumer_production_run(value)
        self.assertFalse(output["eligible_for_owner_acceptance"])
        self.assertEqual(output["disposition_failures"], ["CASE-1"])
        value["cases"][0]["difference_disposition"] = "owner_acknowledged_restriction"
        self.assertTrue(evaluate_consumer_production_run(value)["eligible_for_owner_acceptance"])

    def test_blocking_semantic_difference_never_reaches_owner_acceptance(self):
        value = package("production_dual_run")
        value["cases"][0]["legacy_result"].update({"claim_class": "incremental", "grade_label": "C2"})
        value["cases"][0]["f01_result"].update({"claim_class": "causal", "grade_label": "CE4"})
        value["cases"][0]["difference_disposition"] = "pending"
        output = evaluate_consumer_production_run(value)
        self.assertFalse(output["eligible_for_owner_acceptance"])
        self.assertEqual(output["blocking_cases"], ["CASE-1"])
        self.assertEqual(output["next_state"], "blocking_difference")

    def test_fail_closed_case_cannot_preserve_a_numeric_causal_value(self):
        value = package("production_dual_run")
        expired = next(item for item in value["cases"] if item["case_class"] == "expired")
        expired["legacy_result"] = result()
        expired["f01_result"] = result()
        output = evaluate_consumer_production_run(value)
        self.assertFalse(output["eligible_for_owner_acceptance"])
        self.assertEqual(output["fail_closed_semantic_failures"], [expired["case_id"]])

    def test_missing_required_case_class_is_rejected(self):
        value = package()
        value["cases"].pop()
        with self.assertRaises(ECAEError) as raised:
            evaluate_consumer_production_run(value)
        self.assertIn(raised.exception.code, {"SCHEMA_VALIDATION_FAILED", "PRODUCTION_RUN_CASE_MATRIX_INCOMPLETE"})


if __name__ == "__main__":
    unittest.main()
