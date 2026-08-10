#!/usr/bin/env python3
"""Validate cluster/geo design inputs and route to a verified inference backend."""

from __future__ import annotations

import math

from backend_contract import require_verified_backend
from ecae_common import ECAEError, cli_main


def evaluate_cluster_effect(value: dict) -> dict:
    estimand = value.get("estimand")
    clusters = value.get("clusters")
    if estimand not in {"cluster_average","individual_average"}:
        raise ECAEError("ESTIMAND_NOT_FROZEN", "Cluster design must choose cluster_average or individual_average")
    if not isinstance(clusters, list) or len(clusters) < 4:
        raise ECAEError("INSUFFICIENT_CLUSTERS", "At least four clusters are required even to route the analysis")
    if any(not all(field in item for field in ["cluster_id","arm","size","outcome_summary"]) for item in clusters):
        raise ECAEError("INVALID_CLUSTER_RECORD", "Each cluster needs id, arm, size, and outcome_summary")
    cluster_ids = [item["cluster_id"] for item in clusters]
    if any(not isinstance(item, str) or not item for item in cluster_ids) or len(cluster_ids) != len(set(cluster_ids)):
        raise ECAEError("INVALID_CLUSTER_ID", "Cluster ids must be non-empty and unique")
    if any(not isinstance(item["size"], int) or isinstance(item["size"], bool) or item["size"] <= 0 for item in clusters):
        raise ECAEError("INVALID_CLUSTER_SIZE", "Cluster size must be a positive integer")
    means = [item["outcome_summary"].get("mean") if isinstance(item["outcome_summary"], dict) else None for item in clusters]
    if any(not isinstance(mean, (int, float)) or isinstance(mean, bool) or not math.isfinite(mean) for mean in means):
        raise ECAEError("INVALID_CLUSTER_OUTCOME", "Each outcome_summary requires a finite numeric mean")
    if any("variance" in item["outcome_summary"] and (not isinstance(item["outcome_summary"]["variance"], (int, float)) or isinstance(item["outcome_summary"]["variance"], bool) or item["outcome_summary"]["variance"] < 0 or not math.isfinite(item["outcome_summary"]["variance"])) for item in clusters):
        raise ECAEError("INVALID_CLUSTER_VARIANCE", "Cluster outcome variance must be finite and non-negative when supplied")
    arms = {item["arm"] for item in clusters}
    if len(arms) < 2 or any(sum(1 for item in clusters if item["arm"] == arm) < 2 for arm in arms):
        raise ECAEError("INSUFFICIENT_CLUSTERS_PER_ARM", "Each arm needs at least two clusters")
    if any(not isinstance(arm, str) or not arm for arm in arms):
        raise ECAEError("INVALID_ARM", "Cluster arm labels must be non-empty strings")
    contrast = value.get("contrast")
    if len(arms) == 2 and contrast is None:
        ordered = sorted(arms)
        contrast = {"reference": ordered[0], "treatment": ordered[1]}
    if not isinstance(contrast, dict) or set(contrast) != {"reference", "treatment"} or contrast["reference"] not in arms or contrast["treatment"] not in arms or contrast["reference"] == contrast["treatment"]:
        raise ECAEError("CONTRAST_NOT_FROZEN", "A valid treatment-versus-reference contrast must be frozen")
    if value.get("assignment_unit") != "cluster" or value.get("standard_error_unit") != "cluster":
        raise ECAEError("UNIT_MISMATCH", "Assignment and inference must be cluster-compatible")
    expected_weighting = "equal_cluster" if estimand == "cluster_average" else "individual_equal"
    if value.get("analysis_weighting") != expected_weighting:
        raise ECAEError("ESTIMAND_WEIGHT_MISMATCH", f"{estimand} requires analysis_weighting={expected_weighting}")
    if value.get("few_cluster_inference") not in {"CR2_Satterthwaite", "randomization_inference", "wild_cluster_bootstrap"}:
        raise ECAEError("CLUSTER_INFERENCE_NOT_FROZEN", "Few-cluster inference method must be preregistered")
    diagnostics = value.get("registered_diagnostics")
    required_diagnostics = {"ICC", "cluster_size_distribution", "cluster_leverage", "effective_degrees_of_freedom"}
    if not isinstance(diagnostics, list) or not required_diagnostics.issubset(set(diagnostics)):
        raise ECAEError("CLUSTER_DIAGNOSTICS_NOT_FROZEN", "ICC, cluster size, leverage, and effective degrees of freedom diagnostics are required")
    backend = require_verified_backend("cluster_inference")
    return {"status":"ready_for_backend_execution","backend":backend,"estimand":estimand,"contrast":contrast,"analysis_weighting":expected_weighting,"cluster_count":len(clusters),"required_outputs":["effect","CR2_or_RI_interval","degrees_of_freedom","ICC","cluster_leverage","sensitivity"]}


if __name__ == "__main__":
    cli_main(evaluate_cluster_effect, __doc__ or "Evaluate cluster effect")
