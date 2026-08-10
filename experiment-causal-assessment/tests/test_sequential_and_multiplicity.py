import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from adjust_multiplicity import adjust_multiplicity
from ecae_common import ECAEError
from evaluate_guardrails import evaluate_guardrails
from evaluate_sequential_result import evaluate_sequential_result


class SequentialMultiplicityTests(unittest.TestCase):
    def group_sequential_request(self):
        return {"sequential_paradigm":"group_sequential","alpha":0.05,"sided":2,"efficacy_spending":"obrien_fleming","futility_binding":False,"design_frozen_before_outcomes":True,"information_fractions":[0.5,1.0],"looks":[{"information_fraction":0.5,"boundary":2.8,"alpha_spent":0.005},{"information_fraction":1.0,"boundary":1.98,"alpha_spent":0.05}]}

    def anytime_request(self):
        return {"sequential_paradigm":"anytime_valid","anytime_method":"e_process","method_frozen_before_outcomes":True,"observation_process":"bounded iid difference in means","looks":[{"e_value_or_cs":1.4,"confidence_sequence":{"lower":-0.2,"upper":0.5}}]}

    def test_holm_known_values(self):
        result=adjust_multiplicity({"method":"holm","alpha":0.05,"hypotheses":[{"hypothesis_id":"h1","family_id":"f","p_value":0.01},{"hypothesis_id":"h2","family_id":"f","p_value":0.03},{"hypothesis_id":"h3","family_id":"f","p_value":0.04}]})
        values={item["hypothesis_id"]:item["adjusted_p_value"] for item in result["families"][0]["hypotheses"]}
        self.assertAlmostEqual(values["h1"],0.03)
        self.assertAlmostEqual(values["h2"],0.06)
        self.assertAlmostEqual(values["h3"],0.06)

    def test_bh_marked_exploratory(self):
        result=adjust_multiplicity({"method":"benjamini_hochberg","hypotheses":[{"hypothesis_id":"h1","family_id":"f","p_value":0.01},{"hypothesis_id":"h2","family_id":"f","p_value":0.2}]})
        self.assertTrue(result["exploratory_only"])

    def test_p_value_one_is_valid(self):
        result=adjust_multiplicity({"method":"none_single_primary","hypotheses":[{"hypothesis_id":"h1","family_id":"f","p_value":1.0}]})
        self.assertEqual(result["families"][0]["hypotheses"][0]["adjusted_p_value"],1.0)

    def test_guardrail_stops_independently(self):
        result=evaluate_guardrails({"guardrails":[{"guardrail_id":"refund","harm_direction":"higher_is_harmful","harm_threshold":0.01,"interval":{"lower":0.02,"upper":0.04},"decision_rule":"stop_on_confirmed_harm","registered_before_launch":True}]})
        self.assertTrue(result["stop_for_harm"])

    def test_valid_fixed_horizon(self):
        result=evaluate_sequential_result({"sequential_paradigm":"fixed_horizon","looks":[{"is_final":True,"outcome_reviewed":True,"result_ref":"r"}]})
        self.assertEqual(result["status"],"valid_final_look")

    def test_fixed_horizon_peeking_rejected(self):
        with self.assertRaises(ECAEError) as context:
            evaluate_sequential_result({"sequential_paradigm":"fixed_horizon","looks":[{"is_final":False,"outcome_reviewed":True},{"is_final":True,"outcome_reviewed":True}]})
        self.assertEqual(context.exception.code,"FIXED_HORIZON_VIOLATION")

    def test_unfrozen_group_sequential_rejected_before_backend(self):
        with self.assertRaises(ECAEError) as context:
            evaluate_sequential_result({"sequential_paradigm":"group_sequential","looks":[{}]})
        self.assertEqual(context.exception.code,"SEQUENTIAL_VALUE_INVALID")

    def test_group_sequential_backend_fails_closed(self):
        with self.assertRaises(ECAEError) as context:
            evaluate_sequential_result(self.group_sequential_request())
        self.assertEqual(context.exception.code,"BACKEND_UNAVAILABLE")

    def test_group_sequential_alpha_spending_cannot_decrease(self):
        value=self.group_sequential_request(); value["looks"][1]["alpha_spent"]=0.004
        with self.assertRaises(ECAEError) as context: evaluate_sequential_result(value)
        self.assertEqual(context.exception.code,"ALPHA_SPENDING_INVALID")

    def test_anytime_backend_rejection_fails_closed(self):
        with self.assertRaises(ECAEError) as context: evaluate_sequential_result(self.anytime_request())
        self.assertEqual(context.exception.code,"BACKEND_UNAVAILABLE")

    def test_anytime_invalid_confidence_sequence_rejected_first(self):
        value=self.anytime_request(); value["looks"][0]["confidence_sequence"]={"lower":1.0,"upper":0.0}
        with self.assertRaises(ECAEError) as context: evaluate_sequential_result(value)
        self.assertEqual(context.exception.code,"ANYTIME_OUTPUT_INVALID")


if __name__=="__main__": unittest.main()
