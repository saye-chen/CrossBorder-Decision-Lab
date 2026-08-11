import math
import pathlib
import random
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from calculate_sample_size import calculate_sample_size
from ecae_common import content_hash
from evaluate_randomized_effect import evaluate_randomized_effect


class PropertySimulationTests(unittest.TestCase):
    def test_group_swap_flips_effect_and_interval(self):
        original=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"continuous","control_arm":"c","groups":{"c":[1,2,3,4],"t":[4,5,6,7]}})["comparisons"][0]
        swapped=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"continuous","control_arm":"t","groups":{"c":[1,2,3,4],"t":[4,5,6,7]}})["comparisons"][0]
        self.assertAlmostEqual(original["estimate_absolute"],-swapped["estimate_absolute"])
        self.assertAlmostEqual(original["confidence_interval"]["lower"],-swapped["confidence_interval"]["upper"])

    def test_unit_scaling_preserves_p_and_scales_effect(self):
        data={"c":[1,2,3,4,5],"t":[2,4,5,7,8]}
        base=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"continuous","control_arm":"c","groups":data})["comparisons"][0]
        scaled=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"continuous","control_arm":"c","groups":{arm:[10*x for x in values] for arm,values in data.items()}})["comparisons"][0]
        self.assertAlmostEqual(scaled["estimate_absolute"],10*base["estimate_absolute"])
        self.assertAlmostEqual(scaled["p_value_unadjusted"],base["p_value_unadjusted"])

    def test_larger_mde_needs_no_more_sample(self):
        small=calculate_sample_size({"metric_type":"continuous","minimum_important_effect":0.5,"baseline_variance":1})
        large=calculate_sample_size({"metric_type":"continuous","minimum_important_effect":1.0,"baseline_variance":1})
        self.assertGreater(small["n_total"],large["n_total"])

    def test_hash_is_key_order_invariant(self):
        self.assertEqual(content_hash({"a":1,"b":2}),content_hash({"b":2,"a":1}))

    def test_continuous_null_type_one_with_monte_carlo_band(self):
        rng=random.Random(20260810)
        repeats,n,alpha=1200,80,0.05
        rejected=0
        for _ in range(repeats):
            c=[rng.gauss(0,1) for _ in range(n)]
            t=[rng.gauss(0,1) for _ in range(n)]
            result=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"continuous","control_arm":"c","groups":{"c":c,"t":t}})["comparisons"][0]
            rejected += result["p_value_unadjusted"] < alpha
        rate=rejected/repeats
        mcse=math.sqrt(alpha*(1-alpha)/repeats)
        band=max(0.005,3*mcse)
        self.assertLessEqual(abs(rate-alpha),band)

    def test_binary_score_interval_null_coverage_with_monte_carlo_band(self):
        rng=random.Random(20260811)
        repeats,n,target=1000,60,0.95
        covered=0
        for _ in range(repeats):
            c=[1 if rng.random()<0.08 else 0 for _ in range(n)]
            t=[1 if rng.random()<0.08 else 0 for _ in range(n)]
            interval=evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"binary","control_arm":"c","groups":{"c":c,"t":t}})["comparisons"][0]["confidence_interval"]
            covered += interval["lower"]<=0<=interval["upper"]
        rate=covered/repeats
        mcse=math.sqrt(target*(1-target)/repeats)
        band=max(0.005,3*mcse)
        self.assertGreaterEqual(rate,target-band)


if __name__=="__main__": unittest.main()
