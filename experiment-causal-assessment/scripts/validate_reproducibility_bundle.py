#!/usr/bin/env python3
"""Validate ECAE reproducibility hashes, backend proofs, replay, and dependencies."""

from __future__ import annotations

from datetime import timezone
import re

from ecae_common import ECAEError, cli_main, parse_time


HASH_FIELDS=["protocol_hash","population_hash","assignment_hash","dataset_hash","code_hash","environment_hash","parameter_hash","result_hash"]


def validate_reproducibility_bundle(value:dict)->dict:
    missing=[field for field in HASH_FIELDS if not isinstance(value.get(field),str) or re.fullmatch(r"[a-f0-9]{64}",value[field]) is None]
    if missing: raise ECAEError("REPRO_HASH_INCOMPLETE","Required SHA-256 hashes are missing or malformed",missing)
    randomness=value.get("randomness_contract",{})
    randomness_missing=[field for field in ["generator","algorithm","seed_commitment","parallelism"] if not randomness.get(field)]
    if randomness_missing: raise ECAEError("RANDOMNESS_CONTRACT_INCOMPLETE","Randomness contract is incomplete",randomness_missing)
    run=value.get("run_manifest",{})
    if not all(field in run for field in ["command","started_at","completed_at","exit_status","log_ref"]):
        raise ECAEError("RUN_MANIFEST_INCOMPLETE","Run manifest is incomplete")
    if parse_time(run["completed_at"],"completed_at")<parse_time(run["started_at"],"started_at"):
        raise ECAEError("RUN_TIME_INVALID","Run completion precedes start")
    if run["exit_status"]!=0: raise ECAEError("RUN_FAILED","Reproduction run did not exit successfully")
    backend_failures=[]
    for proof in value.get("backend_proofs",[]):
        if not all(proof.get(field) for field in ["backend_id","version","parity_evidence_ref","verified_at","expires_at"]): backend_failures.append({"backend_id":proof.get("backend_id"),"reason":"incomplete"}); continue
        if parse_time(proof["expires_at"],"expires_at")<=parse_time(run["completed_at"],"completed_at"): backend_failures.append({"backend_id":proof["backend_id"],"reason":"expired_at_run"})
    if backend_failures: raise ECAEError("BACKEND_PROOF_INVALID","Backend proof failed",backend_failures)
    graph=value.get("dependency_graph")
    if not isinstance(graph,list) or not graph: raise ECAEError("DEPENDENCY_GRAPH_EMPTY","Dependency graph is required")
    replay_level=value.get("replay_level")
    replay_status=value.get("replay_status")
    deterministic_pass=replay_level in {"deterministic_replay","decision_replay"} and replay_status=="pass"
    return {"valid":True,"hashes_bound":HASH_FIELDS,"backend_proofs_valid":True,"dependency_edges":len(graph),"replay_level":replay_level,"replay_status":replay_status,"deterministic_replay_pass":deterministic_pass,"claim_ceiling":"CE5" if deterministic_pass else "CE4","invalidation_triggers":value.get("invalidation_triggers",[])}


if __name__=="__main__":
    cli_main(validate_reproducibility_bundle,__doc__ or "Validate reproducibility bundle")
