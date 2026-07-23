#!/usr/bin/env python3
import importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parent

def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/f"{name}.py")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

design=load("design_incrementality_experiment")
causal=load("estimate_causal_incrementality")
media=load("estimate_media_response")

class CausalMeasurement(unittest.TestCase):
    def test_cluster_design_effect_increases_required_sample(self):
        base={"baseline_rate":.10,"absolute_mde":.02,"alpha":.05,"power":.8}
        iid=design.design(base); clustered=design.design({**base,"average_cluster_size":100,"icc":.05})
        self.assertGreater(clustered["required_observations_per_arm"],iid["required_observations_per_arm"])
        self.assertEqual(clustered["estimand"],"intention_to_treat")

    def test_clustered_itt_uses_assignment_clusters(self):
        out=causal.estimate({"method":"clustered_itt","treatment_clusters":[12,13,11,14],
                             "control_clusters":[9,10,8,11]})
        self.assertAlmostEqual(out["effect"],3)
        self.assertTrue(out["diagnostics"]["cluster_level_inference"])
        self.assertEqual(out["estimand"],"intention_to_treat_per_assignment_cluster")

    def test_did_and_parallel_trend_gate(self):
        good=causal.estimate({"method":"did","treatment_pre":[10,11,12],"control_pre":[8,9,10],
                              "treatment_post":[18,19],"control_post":[12,13],"maximum_pretrend_slope":.01})
        self.assertTrue(good["identified"]); self.assertAlmostEqual(good["effect"],4)
        bad=causal.estimate({"method":"did","treatment_pre":[10,14,20],"control_pre":[10,10,10],
                             "treatment_post":[24,25],"control_post":[11,12],"maximum_pretrend_slope":.1})
        self.assertFalse(bad["identified"])

    def test_synthetic_control_fit_and_weights(self):
        out=causal.estimate({"method":"synthetic_control","treated_pre":[10,12,14,16],
            "donor_pre":[[10,12,14,16],[20,18,16,14]],"treated_post":[20,22],
            "donor_post":[[18,20],[12,10]],"learning_rate":.001,"iterations":4000,"maximum_pre_rmse":.2})
        self.assertAlmostEqual(sum(out["weights"]),1,places=6)
        self.assertLess(out["diagnostics"]["pre_rmse"],.2)
        self.assertTrue(out["identified"])

    def test_adstock_hill_has_real_time_holdout(self):
        spend=[0,10,20,30,40,50,60,50,40,30,20,10,5,15,25,35]
        feature=media.hill(media.adstock(spend,.3),25,1)
        outcome=[5+40*x for x in feature]
        out=media.fit({"spend":spend,"outcome":outcome,"holdout_periods":4,
                       "decay_grid":[0,.3,.6],"half_saturation_grid":[15,25,40],"hill_slope_grid":[1]})
        self.assertEqual(out["decay"],.3); self.assertEqual(out["half_saturation"],25)
        self.assertTrue(out["identified"]); self.assertLess(out["holdout_rmse"],1e-8)

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError): design.design({"baseline_rate":.1,"absolute_mde":0})
        with self.assertRaises(ValueError): causal.estimate({"method":"did","treatment_pre":[1],"control_pre":[1]})
        with self.assertRaises(ValueError): media.fit({"spend":[1,2],"outcome":[1,2]})

    def test_cli_writes_auditable_output(self):
        with tempfile.TemporaryDirectory() as td:
            inp=Path(td)/"in.json"; out=Path(td)/"out.json"
            inp.write_text(json.dumps({"baseline_rate":.1,"absolute_mde":.02}))
            result=subprocess.run(["python3",str(ROOT/"design_incrementality_experiment.py"),
                                   "--input",str(inp),"--output",str(out)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn("spillover_check",json.loads(out.read_text())["preregistration_required"])

if __name__=="__main__": unittest.main(verbosity=2)
