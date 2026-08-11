import math
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_switchback_sensitivity import evaluate_switchback_sensitivity


def rows(carryover: float = 0.0):
    arms = [0, 0, 1, 1, 0, 1, 0, 1] * 4
    values = []
    for index, arm in enumerate(arms):
        lag = arms[index - 1] if index else 0
        outcome = 10 + 2 * arm + carryover * lag + 0.4 * math.sin(2 * math.pi * index / 8)
        values.append({"period_index": index, "arm": arm, "outcome": outcome})
    return values


class SwitchbackSensitivityTests(unittest.TestCase):
    def test_registered_lag_periodicity_and_hac_are_estimated(self):
        result = evaluate_switchback_sensitivity({"rows": rows(0.5), "registered_lag_order": 1, "maximum_lag_order": 1, "registered_periodicities": [8], "hac_lag": 2, "coefficient_stability_tolerance": 0.5})
        self.assertAlmostEqual(result["registered_model"]["coefficients"]["current_treatment"], 2.0, places=10)
        self.assertAlmostEqual(result["registered_model"]["coefficients"]["lag_1"], 0.5, places=10)
        self.assertEqual(result["serial_dependence_interval"], "Newey_West_Bartlett_HAC")
        self.assertTrue(result["periodicity_terms_estimated"])

    def test_material_carryover_instability_downgrades(self):
        result = evaluate_switchback_sensitivity({"rows": rows(1.5), "registered_lag_order": 1, "maximum_lag_order": 1, "registered_periodicities": [8], "hac_lag": 2, "coefficient_stability_tolerance": 0.1})
        self.assertEqual(result["status"], "downgrade_required")
        self.assertFalse(result["business_action_authorized"])


if __name__ == "__main__":
    unittest.main()
