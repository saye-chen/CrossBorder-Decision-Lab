#!/usr/bin/env python3
"""Compile and fail-close an ECAE experiment/causal protocol bundle."""

from __future__ import annotations

from collections import Counter

from ecae_common import ECAEError, backend_registry_path, cli_main, load_json, parse_time, require_fields, require_probability


DESIGN_TIERS = {
    "two_arm_randomized": "native_executable",
    "multi_arm_randomized": "native_executable",
    "stratified_randomized": "native_executable",
    "did_2x2": "native_executable",
    "cluster_randomized": "verified_backend",
    "geo_holdout": "verified_backend",
    "switchback": "verified_backend",
    "staggered_did": "verified_backend",
    "synthetic_control": "verified_backend",
    "sdid": "verified_backend",
    "rdd": "verified_backend",
    "iv": "verified_backend",
    "aipw": "verified_backend",
    "tmle": "verified_backend",
    "dml": "verified_backend",
    "matching_weighting": "verified_backend",
    "hte_uplift": "verified_backend",
    "network_interference": "protocol_only",
    "longitudinal_dynamic": "protocol_only",
    "mediation": "protocol_only",
    "bandit_off_policy": "protocol_only",
}
CRITICAL_CAUSAL_GATES = {"Q2", "Q3", "Q4", "Q5", "Q6", "Q8", "Q9"}
DESIGN_BACKENDS = {
    "cluster_randomized":"cluster_inference", "switchback":"switchback_inference", "staggered_did":"staggered_did",
    "synthetic_control":"synthetic_control", "sdid":"synthetic_did", "rdd":"rdd_local", "iv":"weak_iv",
    "aipw":"observational_aipw", "tmle":"observational_tmle", "dml":"observational_dml", "hte_uplift":"hte_uplift",
}


def validate_protocol_bundle(value: dict) -> dict:
    require_fields(value, ["protocol"])
    protocol = value["protocol"]
    require_fields(protocol, ["design", "capability_tier", "eligibility_gates", "assignment", "metric_refs", "sample_plan", "sequential_paradigm", "hypothesis_family_refs", "preregistration_time"] , "$.protocol")

    design = protocol["design"]
    expected_tier = DESIGN_TIERS.get(design)
    if expected_tier is None:
        raise ECAEError("UNSUPPORTED_DESIGN", f"Design is not registered: {design}")
    if protocol["capability_tier"] != expected_tier:
        raise ECAEError("CAPABILITY_TIER_MISMATCH", f"{design} must use {expected_tier}", {"declared": protocol["capability_tier"]})

    gates = protocol["eligibility_gates"]
    gate_ids = [gate.get("gate_id") for gate in gates]
    counts = Counter(gate_ids)
    expected_ids = {f"Q{i}" for i in range(1, 11)}
    if set(gate_ids) != expected_ids or any(count != 1 for count in counts.values()):
        raise ECAEError("INVALID_GATE_SET", "Eligibility gates must contain Q1-Q10 exactly once", {"observed": gate_ids})
    incomplete_gates = [gate.get("gate_id") for gate in gates if not gate.get("rationale") or not gate.get("evidence_refs")]
    if incomplete_gates:
        raise ECAEError("GATE_EVIDENCE_INCOMPLETE", "Every Q1-Q10 gate needs rationale and evidence_refs", incomplete_gates)
    gate_status = {gate["gate_id"]: gate.get("status") for gate in gates}
    failed = sorted(gate for gate, status in gate_status.items() if status in {"fail", "unknown", "conflict"})
    critical_failed = sorted(CRITICAL_CAUSAL_GATES.intersection(failed))

    assignment = protocol["assignment"]
    require_fields(assignment, ["arms", "allocation", "algorithm"], "$.protocol.assignment")
    if len(assignment["arms"]) != len(assignment["allocation"]):
        raise ECAEError("ALLOCATION_LENGTH_MISMATCH", "arms and allocation must have equal length")
    if abs(sum(assignment["allocation"]) - 1.0) > 1e-12:
        raise ECAEError("ALLOCATION_NOT_NORMALIZED", "Allocation probabilities must sum to one")
    if not protocol["metric_refs"] or not protocol["hypothesis_family_refs"]:
        raise ECAEError("ANALYSIS_CONTRACT_INCOMPLETE", "At least one metric and hypothesis family are required")
    sample = protocol["sample_plan"]
    require_fields(sample, ["alpha", "power", "minimum_important_effect", "baseline_source", "attrition_allowance"], "$.protocol.sample_plan")
    require_probability(sample["alpha"], "sample_plan.alpha")
    require_probability(sample["power"], "sample_plan.power")
    require_probability(sample["attrition_allowance"], "sample_plan.attrition_allowance", allow_zero=True)
    if not isinstance(sample["minimum_important_effect"], (int, float)) or isinstance(sample["minimum_important_effect"], bool) or sample["minimum_important_effect"] == 0:
        raise ECAEError("INVALID_MINIMUM_IMPORTANT_EFFECT", "minimum_important_effect must be a non-zero number")

    question = value.get("causal_question")
    is_causal = question is None or question.get("question_type") == "causal"
    if question and question.get("question_type") == "causal":
        require_fields(question, ["estimand_ref", "causal_graph_ref", "decision_to_change"], "$.causal_question")
        if not question.get("decision_to_change", "").strip():
            raise ECAEError("NOT_ACTIONABLE", "Causal question must identify a decision to change")

    analysis_plan = value.get("analysis_plan")
    if analysis_plan:
        if analysis_plan.get("sequential_paradigm") != protocol["sequential_paradigm"]:
            raise ECAEError("SEQUENTIAL_PARADIGM_MISMATCH", "Protocol and analysis plan use different sequential paradigms")
        post_treatment = [item.get("name") for item in analysis_plan.get("covariates", []) if item.get("temporal_status") == "post_treatment"]
        if post_treatment:
            raise ECAEError("BAD_CONTROL", "Post-treatment covariates are forbidden in the primary adjustment set", post_treatment)

    if "launch_time" in value and parse_time(protocol["preregistration_time"], "preregistration_time") >= parse_time(value["launch_time"], "launch_time"):
        raise ECAEError("LATE_PREREGISTRATION", "Preregistration must precede launch")

    ceiling = "CE5"
    eligible = True
    blockers: list[str] = []
    if any(status != "pass" for status in gate_status.values()):
        eligible = False
        blockers.append("ALL_Q1_Q10_MUST_PASS_TO_LAUNCH")
    if protocol["capability_tier"] in {"protocol_only", "research_only"}:
        eligible = False
        ceiling = "CE3"
        blockers.append("METHOD_NOT_EXECUTABLE_IN_ECAE")
    backend_status = None
    backend_id = DESIGN_BACKENDS.get(design)
    if protocol["capability_tier"] == "verified_backend":
        registry = load_json(backend_registry_path())
        matches = [item for item in registry.get("backends",[]) if item.get("backend_id")==backend_id]
        backend_status = matches[0].get("status") if len(matches)==1 else "not_registered"
        if backend_status != "verified":
            eligible = False
            ceiling = "CE3"
            blockers.append("VERIFIED_BACKEND_UNAVAILABLE")
    if is_causal and critical_failed:
        eligible = False
        ceiling = "CE3"
        blockers.extend(f"{gate}_NOT_PASSED" for gate in critical_failed)
    if gate_status.get("Q1") != "pass":
        eligible = False
        ceiling = "CE0"
        blockers.append("QUESTION_NOT_ACTIONABLE")
    if gate_status.get("Q10") != "pass":
        eligible = False
        blockers.append("ECONOMIC_RATIONALE_NOT_PASSED")
        if ceiling == "CE5":
            ceiling = "CE4"

    return {
        "protocol_valid": True,
        "eligible_to_launch": eligible,
        "design": design,
        "capability_tier": expected_tier,
        "backend_id": backend_id,
        "backend_status": backend_status,
        "failed_or_unknown_gates": failed,
        "blockers": sorted(set(blockers)),
        "claim_ceiling": ceiling,
        "business_owner_decision_required": True,
        "external_write": False,
    }


if __name__ == "__main__":
    cli_main(validate_protocol_bundle, __doc__ or "Validate protocol")
