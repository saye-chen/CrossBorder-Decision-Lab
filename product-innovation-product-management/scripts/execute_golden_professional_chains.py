#!/usr/bin/env python3
"""Scenario-owned inputs and real professional execution for the ten D03 Goldens."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
_MODULES: dict[str, Any] = {}


def module(filename: str):
    if filename not in _MODULES:
        spec = importlib.util.spec_from_file_location(
            "golden_" + filename.replace(".", "_"), ROOT / "scripts" / filename
        )
        value = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(value)
        _MODULES[filename] = value
    return _MODULES[filename]


def _state_payload(event_type: str) -> dict[str, Any]:
    recalculating = event_type in {"product_fact_change", "retire"}
    state = {
        "chain_id": "GOLDEN-CHAIN",
        "chain_revision": 0,
        "next_sequence": 1,
        "current_decision_id": "D-v1",
        "current_version": "v1",
        "object_ref": {"object_id": "P-GOLDEN", "object_version": "p1"},
        "product_lifecycle_stage": "PLC7" if event_type == "retire" else "PLC4",
        "decision_state": "proposed",
        "acceptance_state": "accepted",
        "action_state": "proposed",
        "history": [{
            "decision_id": "D-v1", "version": "v1", "status": "proposed",
            "is_current": True, "object_version": "p1", "input_hash": "sha256:old",
            "created_at": "2026-07-28T00:00:00Z", "supersedes": None,
        }],
        "events": [], "dependencies": {}, "pending_acceptance": [],
        "unresolved_items": [],
        "lineage": {"state_hash": "sha256:old", "runtime_version": "PIPM-2026.01"},
    }
    event = {
        "event_id": "E-GOLDEN", "turn_id": "T-GOLDEN", "sequence": 1,
        "expected_revision": 0, "idempotency_key": "golden-event-0001",
        "event_type": event_type, "occurred_at": "2026-07-28T01:00:00Z",
        "recorded_at": "2026-07-28T01:01:00Z", "object_id": "P-GOLDEN",
        "object_version": "p1", "old_input_hash": "sha256:old",
        "new_input_hash": "sha256:new" if recalculating else "sha256:old",
        "changed_node_ids": ["SPEC-1"] if recalculating else [], "external_write": False,
    }
    payload: dict[str, Any] = {"state": state, "event": event}
    if recalculating:
        payload["new_decision"] = {
            "decision_id": "D-v2", "version": "v2", "status": "proposed",
            "object_version": "p1", "input_hash": "sha256:new",
            "created_at": "2026-07-28T01:01:00Z",
        }
    return payload


def scenario_input(name: str) -> dict[str, Any]:
    values: dict[str, dict[str, Any]] = {
        "amazon-opportunity-mvp": {
            "engine": "evaluate_product_models.py", "operation": "model",
            "payload": {"model": "mvp_coverage", "assumptions": [
                {"id": "A-demand", "critical": True, "coverage": "1", "threshold": "0.8"},
                {"id": "A-use", "critical": True, "coverage": "0.9", "threshold": "0.8"},
            ], "hard_gates": [{"id": "amazon-policy", "status": "passed"}]},
            "mutation": {"path": ["payload", "assumptions", 1, "coverage"], "value": "0.2"},
        },
        "tiktok-proxy-correction": {
            "engine": "evaluate_product_models.py", "operation": "model",
            "payload": {"model": "unmet_need", "importance": "0.85", "satisfaction": "0.35",
                        "support_weight": "2", "conflict_weight": "3", "hard_gates": []},
            "mutation": {"path": ["payload", "support_weight"], "value": "8"},
        },
        "dtc-return-redesign": {
            "engine": "evaluate_product_models.py", "operation": "model",
            "payload": {"model": "packaging_impact", "length_cm": "30", "width_cm": "20",
                        "height_cm": "10", "dimensional_divisor_cm3_per_kg": "5000",
                        "protection_score": "0.92", "minimum_protection_score": "0.85",
                        "hard_gates": []},
            "mutation": {"path": ["payload", "protection_score"], "value": "0.6"},
        },
        "multi-country-variant": {
            "engine": "evaluate_product_models.py", "operation": "model",
            "payload": {"model": "constraint_feasibility", "specifications": [
                {"id": "voltage-DE", "value": "230", "min": "220", "max": "240", "unit": "V"},
                {"id": "voltage-US", "value": "120", "min": "110", "max": "125", "unit": "V"},
            ], "selected_features": ["dual-voltage"], "mutually_exclusive": [],
                "dependencies": [["dual-voltage", "country-label-set"]], "hard_gates": []},
            "mutation": {"path": ["payload", "selected_features"], "value": ["dual-voltage", "country-label-set"]},
        },
        "variant-cannibalization": {
            "engine": "evaluate_product_models.py", "operation": "model",
            "payload": {"model": "variant_portfolio", "incremental_demand": "1000",
                        "cannibalized_demand": "250", "complexity_demand_equivalent": "150",
                        "hard_gates": []},
            "mutation": {"path": ["payload", "cannibalized_demand"], "value": "900"},
        },
        "material-change-multidomain": {
            "engine": "compute_product_change_impact.py", "operation": "product_change",
            "payload": {"changed_fields": ["material"], "all_fields": [
                "material", "weight", "packaging", "landed_cost", "claim", "market_access"
            ], "dependencies": {
                "material": ["weight", "claim", "market_access"], "weight": ["packaging", "landed_cost"],
                "packaging": [], "landed_cost": [], "claim": [], "market_access": []
            }},
            "mutation": {"path": ["payload", "dependencies", "market_access"], "value": ["material"]},
        },
        "unsupported-claim": {
            "engine": "evaluate_product_models.py", "operation": "model",
            "payload": {"model": "traceability", "requirements": [
                {"id": "REQ-1", "specification_ids": ["SPEC-1"]}
            ], "specifications": [
                {"id": "SPEC-1", "requirement_id": "REQ-1", "verification_ids": ["VER-1"]}
            ], "claims": [
                {"id": "CLAIM-1", "specification_id": "MISSING", "verification_ids": []}
            ], "verifications": [{"id": "VER-1"}], "hard_gates": []},
            "mutation": {"path": ["payload", "claims", 0], "value": {
                "id": "CLAIM-1", "specification_id": "SPEC-1", "verification_ids": ["VER-1"]
            }},
        },
        "critical-tail-failure": {
            "engine": "evaluate_product_models.py", "operation": "model",
            "payload": {"model": "constraint_feasibility", "specifications": [
                {"id": "mean-strength", "value": "100", "min": "90", "max": "110", "unit": "N"},
                {"id": "p01-tail-strength", "value": "72", "min": "80", "max": "110", "unit": "N"},
            ], "selected_features": [], "mutually_exclusive": [], "dependencies": [], "hard_gates": []},
            "mutation": {"path": ["payload", "specifications", 1, "value"], "value": "82"},
        },
        "specification-drift": {
            "engine": "evaluate_temporary_contract_migration.py", "operation": "migration",
            "payload": {"mappings": [{"source_field": "specification", "target_field": "specification",
                                      "classification": "lossless", "criticality": "safety_critical"}],
                        "differences": [], "consumer_acceptance": [{"consumer": "D06", "status": "accepted"}],
                        "legacy_read_preserved": True, "temporary_snapshot_id": "SPEC-v2",
                        "formal_snapshot_id": "SPEC-v1"},
            "mutation": {"path": ["payload", "formal_snapshot_id"], "value": "SPEC-v2"},
        },
        "stop-retire": {
            "engine": "update_continuous_product_decision.py", "operation": "continuity",
            "payload": _state_payload("retire"),
            "mutation": {"path": ["payload", "event", "expected_revision"], "value": 99},
        },
    }
    return copy.deepcopy(values[name])


def apply_mutation(value: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(value)
    cursor: Any = mutated
    path = mutated["mutation"]["path"]
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = copy.deepcopy(mutated["mutation"]["value"])
    return mutated


def execute(value: dict[str, Any], mutation: bool = False) -> dict[str, Any]:
    work = apply_mutation(value) if mutation else copy.deepcopy(value)
    try:
        if work["operation"] == "model":
            result = module(work["engine"]).evaluate(work["payload"])["result"]
            return {"execution_state": "completed", "decision_status": result["status"], "output": result}
        if work["operation"] == "product_change":
            result = module(work["engine"]).compute(work["payload"])
            return {"execution_state": "completed", "decision_status": "proposed", "output": result}
        if work["operation"] == "migration":
            result = module(work["engine"]).evaluate(work["payload"])
            return {"execution_state": "completed", "decision_status": result["status"], "output": result}
        if work["operation"] == "continuity":
            result = module(work["engine"]).update(work["payload"])
            return {"execution_state": "completed", "decision_status": result["state"]["decision_state"], "output": result}
    except Exception as exc:
        return {"execution_state": "blocked", "decision_status": "blocked",
                "output": {"error_type": type(exc).__name__, "error": str(exc)}}
    return {"execution_state": "blocked", "decision_status": "blocked",
            "output": {"error_type": "UnknownOperation"}}
