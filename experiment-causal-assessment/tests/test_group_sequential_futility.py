import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class GroupSequentialFutilityTests(unittest.TestCase):
    def test_binding_and_nonbinding_beta_spending_vectors_pass(self):
        report = json.loads((ROOT / "evaluations/group-sequential-futility-development-parity.json").read_text(encoding="utf-8"))
        self.assertFalse(report["release_effect"]["registry_verified"])
        self.assertTrue(report["all_vectors_accepted"])
        self.assertEqual({item["binding_futility"] for item in report["vectors"]}, {True, False})
        for vector in report["vectors"]:
            self.assertTrue(vector["accepted"])
            self.assertLessEqual(vector["maximum_absolute_differences"]["upper"], report["tolerances"]["boundary"])
            self.assertLessEqual(vector["maximum_absolute_differences"]["lower"], report["tolerances"]["boundary"])
            self.assertLessEqual(vector["maximum_absolute_differences"]["alpha"], report["tolerances"]["spending"])
            self.assertLessEqual(vector["maximum_absolute_differences"]["beta"], report["tolerances"]["spending"])

    def test_primary_adapter_no_longer_blocks_registered_futility(self):
        adapter = (ROOT / "backends/adapters/group_sequential_gsdesign.R").read_text(encoding="utf-8")
        self.assertNotIn("SEQUENTIAL_FUTILITY_UNSUPPORTED", adapter)
        self.assertIn("cumulative_beta_spent", adapter)


if __name__ == "__main__":
    unittest.main()
