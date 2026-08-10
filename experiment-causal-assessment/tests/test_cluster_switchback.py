import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from ecae_common import ECAEError
from evaluate_cluster_effect import evaluate_cluster_effect
from evaluate_switchback import evaluate_switchback


class ClusterSwitchbackTests(unittest.TestCase):
    def cluster_request(self):
        clusters=[{"cluster_id":str(i),"arm":"c" if i<2 else "t","size":100,"outcome_summary":{"mean":i,"variance":1.0}} for i in range(4)]
        return {"estimand":"individual_average","clusters":clusters,"assignment_unit":"cluster","standard_error_unit":"cluster","analysis_weighting":"individual_equal","few_cluster_inference":"CR2_Satterthwaite","registered_diagnostics":["ICC","cluster_size_distribution","cluster_leverage","effective_degrees_of_freedom"]}

    def switchback_request(self):
        periods=[]
        for i in range(4):
            periods.append({"period_id":str(i),"arm":"c" if i%2==0 else "t","start":f"2026-08-10T0{i}:00:00Z","end":f"2026-08-10T0{i+1}:00:00Z","outcome_summary":{"mean":i},"washout_excluded":True})
        return {"periods":periods,"period_length_seconds":3600,"max_response_lag_seconds":300,"washout_seconds":300,"carryover_sensitivity":True,"carryover_model":"lag1","max_carryover_periods":1,"randomization_scheme":"custom_sequence","allowed_sequences_hash":"a"*64,"observed_sequence_registered":True,"test_statistic_registered":True,"timezone":"UTC","serial_dependence_plan":"randomization_inference","periodicity_controls":["hour_of_day"]}

    def test_cluster_backend_fails_closed(self):
        with self.assertRaises(ECAEError) as context:
            evaluate_cluster_effect(self.cluster_request())
        self.assertEqual(context.exception.code,"BACKEND_UNAVAILABLE")

    def test_cluster_estimand_weight_mismatch_rejected_before_backend(self):
        value=self.cluster_request(); value["analysis_weighting"]="equal_cluster"
        with self.assertRaises(ECAEError) as context: evaluate_cluster_effect(value)
        self.assertEqual(context.exception.code,"ESTIMAND_WEIGHT_MISMATCH")

    def test_cluster_duplicate_id_rejected_before_backend(self):
        value=self.cluster_request(); value["clusters"][1]["cluster_id"]="0"
        with self.assertRaises(ECAEError) as context: evaluate_cluster_effect(value)
        self.assertEqual(context.exception.code,"INVALID_CLUSTER_ID")

    def test_switchback_rejects_uncontrolled_carryover_before_backend(self):
        value=self.switchback_request(); value.update({"period_length_seconds":60,"max_response_lag_seconds":120,"washout_seconds":0,"carryover_model":"none"})
        with self.assertRaises(ECAEError) as context:
            evaluate_switchback(value)
        self.assertEqual(context.exception.code,"CARRYOVER_UNCONTROLLED")

    def test_switchback_qualified_design_still_needs_backend(self):
        with self.assertRaises(ECAEError) as context:
            evaluate_switchback(self.switchback_request())
        self.assertEqual(context.exception.code,"BACKEND_UNAVAILABLE")

    def test_switchback_sequence_commitment_required(self):
        value=self.switchback_request(); value["allowed_sequences_hash"]="not-a-hash"
        with self.assertRaises(ECAEError) as context: evaluate_switchback(value)
        self.assertEqual(context.exception.code,"SEQUENCE_NOT_REGISTERED")

    def test_switchback_overlapping_periods_rejected(self):
        value=self.switchback_request(); value["periods"][1]["start"]="2026-08-10T00:30:00Z"; value["periods"][1]["end"]="2026-08-10T01:30:00Z"
        with self.assertRaises(ECAEError) as context: evaluate_switchback(value)
        self.assertEqual(context.exception.code,"PERIOD_OVERLAP")


if __name__=="__main__": unittest.main()
