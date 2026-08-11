import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from compute_invalidation_closure import compute_invalidation_closure
from ecae_common import ECAEError
from validate_reproducibility_bundle import validate_reproducibility_bundle


H="a"*64


class ReproducibilityTests(unittest.TestCase):
    def valid_bundle(self):
        value={field:H for field in ["protocol_hash","population_hash","assignment_hash","dataset_hash","code_hash","environment_hash","parameter_hash","result_hash"]}
        value.update({"randomness_contract":{"generator":"PCG","algorithm":"hash_bucket","seed_commitment":"abc","parallelism":"serial"},"backend_proofs":[],"run_manifest":{"command":["python","analysis.py"],"started_at":"2026-08-10T00:00:00Z","completed_at":"2026-08-10T00:01:00Z","exit_status":0,"log_ref":"log"},"replay_level":"deterministic_replay","replay_status":"pass","dependency_graph":[{"from":"protocol","to":"result","relation":"produces"}],"invalidation_triggers":["protocol changes"]})
        return value

    def test_deterministic_replay_can_support_ce5(self):
        result=validate_reproducibility_bundle(self.valid_bundle())
        self.assertTrue(result["deterministic_replay_pass"])
        self.assertEqual(result["claim_ceiling"],"CE5")

    def test_failed_run_rejected(self):
        value=self.valid_bundle(); value["run_manifest"]["exit_status"]=1
        with self.assertRaises(ECAEError) as context: validate_reproducibility_bundle(value)
        self.assertEqual(context.exception.code,"RUN_FAILED")

    def test_non_hex_hash_rejected(self):
        value=self.valid_bundle(); value["dataset_hash"]="z"*64
        with self.assertRaises(ECAEError) as context: validate_reproducibility_bundle(value)
        self.assertEqual(context.exception.code,"REPRO_HASH_INCOMPLETE")

    def test_invalidation_closure(self):
        result=compute_invalidation_closure({"changed_refs":["metric"],"dependency_graph":[{"from":"metric","to":"dataset","relation":"consumes"},{"from":"dataset","to":"result","relation":"produces"},{"from":"result","to":"handoff","relation":"produces"}]})
        self.assertEqual([item["ref"] for item in result["affected_refs"]],["dataset","result","handoff"])


if __name__=="__main__": unittest.main()
