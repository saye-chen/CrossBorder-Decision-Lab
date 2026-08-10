import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ClusterHandMatrixTests(unittest.TestCase):
    def test_cr2_matches_equal_cluster_hand_truth(self):
        report = json.loads((ROOT / "evaluations/cluster-hand-matrix-development.json").read_text(encoding="utf-8"))
        self.assertTrue(report["all_checks_pass"])
        self.assertFalse(report["release_effect"]["registry_verified"])
        tolerance = report["tolerance"]
        self.assertTrue(all(value <= tolerance for value in report["absolute_differences"].values()))
        self.assertEqual(report["hand_truth"]["satterthwaite_degrees_of_freedom"], 6)


if __name__ == "__main__":
    unittest.main()
