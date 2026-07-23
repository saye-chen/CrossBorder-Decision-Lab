#!/usr/bin/env python3
"""Prevent silent statistical drift while every Skill remains standalone."""
import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(name,path,extra):
    sys.path.insert(0,str(extra))
    try:
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
    finally: sys.path.pop(0)

A=load("aamo_stats",ROOT/"advertising-analysis-measurement-optimization/scripts/aamo_statistics.py",
       ROOT/"advertising-analysis-measurement-optimization/scripts")
M=load("mbcm_stats",ROOT/"marketing-brand-campaign-management/scripts/statistics_common.py",
       ROOT/"marketing-brand-campaign-management/scripts")

class StatisticalPrimitiveParity(unittest.TestCase):
    def test_contract_version_and_core_formulas_match(self):
        self.assertEqual(A.STATISTICS_CONTRACT_VERSION,M.STATISTICS_CONTRACT_VERSION)
        x=[1,2,4,8,16]; y=[3,5,9,17,33]
        for fn,args in ((A.mean,(x,)),(A.variance,(x,)),(A.covariance,(x,y))):
            peer=getattr(M,fn.__name__)
            self.assertAlmostEqual(fn(*args),peer(*args),places=12)
        ao=A.ols(x,y); mo=M.ols(x,y)
        for key in ("intercept","slope","slope_se","r_squared"):
            self.assertAlmostEqual(ao[key],mo[key],places=12)
        self.assertEqual(A.project_simplex([-.2,.3,2]),M.project_simplex([-.2,.3,2]))

    def test_each_domain_is_standalone(self):
        atext=(ROOT/"advertising-analysis-measurement-optimization/scripts/aamo_statistics.py").read_text()
        mtext=(ROOT/"marketing-brand-campaign-management/scripts/statistics_common.py").read_text()
        self.assertNotIn("marketing-brand-campaign-management",atext)
        self.assertNotIn("advertising-analysis-measurement-optimization",mtext)

if __name__=="__main__": unittest.main(verbosity=2)
