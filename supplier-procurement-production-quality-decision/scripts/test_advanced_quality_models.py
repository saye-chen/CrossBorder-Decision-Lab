#!/usr/bin/env python3
import unittest
from advanced_quality_models import *
class T(unittest.TestCase):
 def test_anova_grr_balanced_and_rejects_unbalanced(self):
  rows=[{"part":p,"operator":o,"replicate":r,"value":10+p+.1*o+.02*r} for p in range(3) for o in range(2) for r in range(2)];self.assertEqual(anova_grr({"measurements":rows})["design"],"balanced_crossed_anova");rows.pop();self.assertRaises(QualityModelError,anova_grr,{"measurements":rows})
 def test_western_electric_detects_same_side(self): self.assertFalse(western_electric({"values":[1]*8,"center":0,"sigma":1})["stable"])
 def test_weibull_rejects_censoring(self): self.assertGreater(weibull_rank_fit({"failure_times":[10,20,40],"right_censored":0})["beta_shape"],0);self.assertRaises(QualityModelError,weibull_rank_fit,{"failure_times":[10,20,40],"right_censored":1})
 def test_sampling_requires_approved_source(self): self.assertRaises(QualityModelError,sampling_plan_lookup,{"standard":"ISO","inspection_level":"II","aql":"1.0","lot_size":1000},{})
if __name__=="__main__":unittest.main(verbosity=2)
