import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_backend_development_qualification import ADAPTERS, fixtures


class BackendDevelopmentQualificationTests(unittest.TestCase):
    def test_all_locked_executable_adapters_have_deterministic_fixture(self):
        first, second = fixtures(), fixtures()
        self.assertEqual(first, second)
        self.assertEqual(set(first), set(ADAPTERS))
        self.assertEqual(len(ADAPTERS), 12)
        for _, relative in ADAPTERS.values():
            self.assertTrue((ROOT / relative).is_file())

    def test_fixtures_cover_futility_did_dml_and_grf(self):
        frozen = fixtures()
        self.assertTrue(frozen["group_sequential_gsdesign"]["futility_binding"])
        self.assertEqual(frozen["staggered_did_callaway_santanna"]["bootstrap_iterations"], 999)
        self.assertEqual(frozen["observational_dml_doubleml"]["folds"], 2)
        self.assertEqual(frozen["hte_uplift_grf"]["num_trees"], 500)

    def test_persistent_qualification_records_every_adapter_without_promotion(self):
        report = json.loads((ROOT / "evaluations/persistent-backend-development-qualification.json").read_text(encoding="utf-8"))
        self.assertEqual(set(report["adapter_results"]), set(ADAPTERS))
        self.assertTrue(report["all_adapters_pass"])
        self.assertTrue(all(item["status"] == "pass" for item in report["adapter_results"].values()))
        self.assertEqual(report["release_effect"]["verified_backend_count"], 0)
        self.assertFalse(report["release_effect"]["registry_promotion_authorized"])
        self.assertFalse(report["release_effect"]["business_action_authorized"])


if __name__ == "__main__":
    unittest.main()
