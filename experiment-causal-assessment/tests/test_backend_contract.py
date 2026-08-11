import json
import ast
import pathlib
import sys
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from backend_contract import require_verified_backend
from ecae_common import ECAEError
from probe_backend_environment import _r_source_revision, _r_version, probe_candidate
from validate_backend_registry import validate_backend_registry
from validate_schema import validate_object


class BackendContractTests(unittest.TestCase):
    def test_registry_unique_and_fail_closed(self):
        registry=json.loads((ROOT/"backends/backend-registry.json").read_text())
        ids=[item["backend_id"] for item in registry["backends"]]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(all(item["status"]!="verified" for item in registry["backends"]))
        with self.assertRaises(ECAEError) as context: require_verified_backend("cluster_inference")
        self.assertEqual(context.exception.code,"BACKEND_UNAVAILABLE")

    def test_registry_and_candidate_lock_are_consistent(self):
        registry=json.loads((ROOT/"backends/backend-registry.json").read_text())
        ids=[item["backend_id"] for item in registry["backends"]]
        result=validate_backend_registry(registry)
        self.assertTrue(result["valid"])
        self.assertEqual(result["verified_count"],0)
        self.assertGreaterEqual(result["candidate_count"],7)
        cluster=next(item for item in registry["backends"] if item["backend_id"]=="cluster_inference")
        self.assertEqual(cluster["adapter_ref"],"backends/adapters/cluster_clubsandwich.R")
        self.assertTrue((ROOT/cluster["adapter_ref"]).is_file())
        sequential=next(item for item in registry["backends"] if item["backend_id"]=="group_sequential")
        self.assertEqual(sequential["adapter_ref"],"backends/adapters/group_sequential_gsdesign.R")
        self.assertTrue((ROOT/sequential["adapter_ref"]).is_file())
        switchback=next(item for item in registry["backends"] if item["backend_id"]=="switchback_inference")
        self.assertEqual(switchback["adapter_ref"],"backends/adapters/switchback_ri2.R")
        self.assertTrue((ROOT/switchback["adapter_ref"]).is_file())
        wp07_ids={"staggered_did","synthetic_control","synthetic_did","rdd_local","weak_iv","observational_aipw","observational_dml"}
        wp07=[item for item in registry["backends"] if item["backend_id"] in wp07_ids]
        self.assertEqual({item["backend_id"] for item in wp07},wp07_ids)
        self.assertTrue(all(item["status"]!="verified" and item["adapter_ref"] for item in wp07))
        self.assertTrue(all((ROOT/item["adapter_ref"]).is_file() for item in wp07))
        self.assertNotIn("synthetic_counterfactual",ids)
        self.assertNotIn("rdd_iv",ids)
        self.assertNotIn("observational_dr",ids)
        hte=next(item for item in registry["backends"] if item["backend_id"]=="hte_uplift")
        self.assertEqual(hte["selected_candidate_id"],"hte_uplift_econml")
        self.assertEqual(hte["status"],"installed_unverified")
        self.assertTrue((ROOT/hte["adapter_ref"]).is_file())

    def test_wp07_development_report_is_non_promotional(self):
        report=json.loads((ROOT/"evaluations/wp07-backend-development.json").read_text())
        self.assertTrue(validate_object(report,"wp07-backend-development.schema.json",verify_hash=False)["valid"])
        self.assertEqual(report["release_effect"]["registry_verified_count"],0)
        self.assertFalse(report["release_effect"]["wp07_release_complete"])
        for candidate in report["candidate_results"]:
            adapter=ROOT/candidate["adapter_ref"]
            ast.parse(adapter.read_text(encoding="utf-8"),filename=str(adapter))
            self.assertTrue(all(vector["status"]=="pass" for vector in candidate["vectors"]))

    def test_github_candidate_is_commit_pinned(self):
        lock=json.loads((ROOT/"backends/backend-lock.json").read_text())
        synthdid=next(item for item in lock["candidates"] if item["candidate_id"]=="synthetic_did_synthdid")
        self.assertRegex(synthdid["source_revision"],r"^[0-9a-f]{40}$")
        self.assertEqual(synthdid["probe_evidence"]["official_beta_warning"],True)

    def test_wp08_hte_development_report_is_non_promotional(self):
        report=json.loads((ROOT/"evaluations/wp08-backend-development.json").read_text())
        self.assertTrue(validate_object(report,"wp08-backend-development.schema.json",verify_hash=False)["valid"])
        self.assertEqual(report["release_effect"]["registry_verified_count"],0)
        self.assertFalse(report["release_effect"]["wp08_release_complete"])
        adapter=ROOT/report["candidate"]["adapter_ref"]
        ast.parse(adapter.read_text(encoding="utf-8"),filename=str(adapter))
        oracle=ROOT/report["development_oracle"]["adapter_ref"]
        self.assertTrue(oracle.is_file())
        self.assertEqual(report["development_oracle"]["execution_status"],"pass_not_external_parity")
        self.assertTrue(all(vector["status"]=="pass" for vector in report["vectors"]))
        heterogeneous=next(vector for vector in report["vectors"] if vector["vector_id"]=="randomized_two_stratum_heterogeneity")
        self.assertLess(heterogeneous["observations"]["candidate_minus_treat_all_interval"][1],0)
        self.assertTrue(heterogeneous["observations"]["heterogeneity_supported_by_frozen_gate"])
        self.assertFalse(heterogeneous["observations"]["policy_supported_by_frozen_gate"])
        null=next(vector for vector in report["vectors"] if vector["vector_id"]=="randomized_constant_effect_no_positive_heterogeneity_support")
        self.assertLess(null["observations"]["Qini"],0)
        self.assertFalse(null["observations"]["heterogeneity_supported_by_frozen_gate"])

    def test_wp08_primary_and_independent_oracle_are_version_locked(self):
        lock=json.loads((ROOT/"backends/backend-lock.json").read_text())
        candidates={item["candidate_id"]:item for item in lock["candidates"]}
        self.assertEqual(candidates["hte_uplift_econml"]["version"],"0.16.0")
        self.assertEqual(candidates["hte_uplift_grf"]["version"],"2.6.1")
        self.assertEqual(candidates["hte_uplift_grf"]["role"],"independent_parity_oracle")

    def test_group_sequential_development_parity_is_non_promotional_and_within_tolerance(self):
        report=json.loads((ROOT/"evaluations/group-sequential-development-parity.json").read_text())
        self.assertTrue(validate_object(report,"backend-development-parity.schema.json",verify_hash=False)["valid"])
        self.assertTrue((ROOT/report["source_script_ref"]).is_file())
        self.assertFalse(report["release_effect"]["registry_verified"])
        for vector in report["vectors"]:
            self.assertLessEqual(vector["maximum_absolute_boundary_difference"],report["tolerances"]["maximum_absolute_boundary_difference"])
            self.assertLessEqual(vector["maximum_absolute_cumulative_alpha_difference"],report["tolerances"]["maximum_absolute_cumulative_alpha_difference"])

    def test_switchback_development_report_preserves_claim_limits(self):
        report=json.loads((ROOT/"evaluations/switchback-ri-development.json").read_text())
        self.assertTrue(validate_object(report,"switchback-ri-development.schema.json",verify_hash=False)["valid"])
        self.assertTrue((ROOT/report["adapter_ref"]).is_file())
        self.assertFalse(report["release_effect"]["registry_verified"])
        self.assertFalse(report["release_effect"]["average_effect_interval_supported"])
        self.assertFalse(report["release_effect"]["carryover_periodicity_sensitivity_pending"])
        self.assertTrue((ROOT/"evaluations/switchback-sensitivity-development.json").is_file())
        self.assertTrue(all(item["expected_error"]==item["observed_error"] for item in report["mutations"]))

    def test_runtime_probe_requires_exact_version(self):
        candidate={"package":"pyfixest","version":"0.60.0","ecosystem":"pypi"}
        exact=probe_candidate(candidate,python_version=lambda package:"0.60.0")
        drift=probe_candidate(candidate,python_version=lambda package:"0.60.1")
        self.assertEqual(exact["status"],"available")
        self.assertEqual(drift["status"],"version_mismatch")

    def test_runtime_probe_reports_missing_r_without_mutation(self):
        candidate={"package":"clubSandwich","version":"0.7.0","ecosystem":"cran"}
        def missing(package): raise FileNotFoundError("Rscript")
        result=probe_candidate(candidate,r_version=missing)
        self.assertEqual(result["status"],"runtime_unavailable")
        self.assertIsNone(result["observed_version"])

    def test_r_probe_honors_isolated_runtime_override(self):
        completed=type("Completed",(),{"returncode":0,"stdout":"0.7.0","stderr":""})()
        with patch.dict("os.environ",{"ECAE_RSCRIPT_BACKEND":"/isolated/Rscript"},clear=False), patch("probe_backend_environment.subprocess.run",return_value=completed) as run:
            self.assertEqual(_r_version("clubSandwich"),"0.7.0")
        self.assertEqual(run.call_args.args[0][0],"/isolated/Rscript")

    def test_github_runtime_requires_exact_installed_source_revision(self):
        candidate={"package":"synthdid","version":"0.0.9","ecosystem":"github","source_revision":"a"*40}
        completed=type("Completed",(),{"returncode":0,"stdout":"b"*40,"stderr":""})()
        with patch("probe_backend_environment._r_source_revision",return_value="b"*40):
            result=probe_candidate(candidate,r_version=lambda package:"0.0.9")
        self.assertEqual(result["status"],"source_revision_mismatch")
        self.assertEqual(result["expected_source_revision"],"a"*40)

    def test_lock_preserves_observed_candidate_failures(self):
        lock=json.loads((ROOT/"backends/backend-lock.json").read_text())
        candidates={item["candidate_id"]:item for item in lock["candidates"]}
        self.assertEqual(candidates["cluster_crv3_pyfixest"]["probe_evidence"]["randomization_inference_fixed_vector"],"fail_key_error")
        self.assertEqual(candidates["anytime_confseq"]["disposition"],"rejected_for_binding")

    def test_unknown_backend_rejected(self):
        with self.assertRaises(ECAEError) as context: require_verified_backend("does_not_exist")
        self.assertEqual(context.exception.code,"BACKEND_NOT_REGISTERED")


if __name__=="__main__": unittest.main()
