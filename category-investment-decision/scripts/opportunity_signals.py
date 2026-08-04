#!/usr/bin/env python3
"""Deterministic, fail-closed CIDM opportunity-signal governance kernel."""
from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "references/opportunity-signal-config.json"
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
OBJECT_KEYS = ("product_concept_id", "category_node", "country", "platform", "currency")
FORBIDDEN_ACTION_FIELDS = {"invest", "investment_action", "capital_posture", "order_quantity", "production_ready"}
REQUIRED_CARD_FIELDS = {
    "signal_id", "signal_version", "decision_object", "signal_type", "observation_window",
    "source_evidence_ids", "observed_facts", "derived_metrics", "assumptions",
    "counter_evidence", "alternative_explanations", "quality", "confidence",
    "allowed_use", "forbidden_use", "validation_actions", "expiry_date", "status",
}
TRAP_STATES = {"observed", "confirmed", "guarded_by_test", "resolved", "stale"}
PACKET_ALLOWED_USE = {"listing_and_store_acceptance_design"}
PACKET_FORBIDDEN_USE = {"investment_score_override"}


class ContractError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode()).hexdigest()


def normalize_ratio(value: Any, scale: str) -> Decimal | None:
    if value is None:
        return None
    try:
        ratio = Decimal(str(value))
    except InvalidOperation as exc:
        raise ContractError("ratio must be numeric or unknown") from exc
    if scale == "0-100":
        ratio /= Decimal("100")
    elif scale != "0-1":
        raise ContractError("ratio scale must be 0-1 or 0-100")
    if ratio < 0 or ratio > 1:
        raise ContractError("normalized ratio outside 0-1")
    return ratio


def adapt_field(raw: dict[str, Any], mapping: dict[str, str], *, source: str, evidence_id: str) -> dict[str, Any]:
    """Map one external field without converting missing/error responses to zero."""
    source_field = mapping["source_field"]
    if raw.get("error") is not None:
        raise ContractError("source response contains an error")
    value = raw.get(source_field)
    if mapping.get("kind") == "ratio":
        value = normalize_ratio(value, mapping.get("scale", "unknown"))
        value = None if value is None else str(value)
    return {
        "value": value,
        "unit": mapping.get("unit"),
        "scale": "0-1" if mapping.get("kind") == "ratio" else mapping.get("scale"),
        "currency": mapping.get("currency"),
        "observation_date": raw.get("observation_date"),
        "window_start": raw.get("window_start"),
        "window_end": raw.get("window_end"),
        "source": source,
        "source_field": source_field,
        "estimation_status": mapping.get("estimation_status", "estimated"),
        "confidence": mapping.get("confidence", "unknown"),
        "raw_evidence_id": evidence_id,
    }


def _valid_date(value: Any) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def validate_signal_card(card: dict[str, Any], *, as_of: date | None = None) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(REQUIRED_CARD_FIELDS - set(card))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    forbidden_present = sorted(FORBIDDEN_ACTION_FIELDS & set(card))
    if forbidden_present:
        errors.append("signal layer has no investment authority: " + ", ".join(forbidden_present))
    obj = card.get("decision_object", {})
    if not isinstance(obj, dict) or any(not obj.get(key) for key in OBJECT_KEYS):
        errors.append("decision_object lacks canonical object keys")
    window = card.get("observation_window", {})
    has_window = isinstance(window, dict) and _valid_date(window.get("start")) and _valid_date(window.get("end"))
    evidence_ids = card.get("source_evidence_ids")
    status = card.get("status")
    if status not in CONFIG["statuses"]["signal"]:
        errors.append("invalid SignalStatus")
    if not has_window and status not in {"inconclusive", "blocked"}:
        errors.append("missing observation window requires inconclusive or blocked")
    if not isinstance(evidence_ids, list) or not evidence_ids:
        if status != "blocked":
            errors.append("missing raw evidence requires blocked")
    if card.get("signal_type") not in CONFIG["signal_names"]:
        errors.append("unregistered canonical signal name")
    if set(card.get("allowed_use", [])) - set(CONFIG["allowed_use"]):
        errors.append("unsupported allowed_use")
    if not set(CONFIG["forbidden_use"]).issubset(set(card.get("forbidden_use", []))):
        errors.append("mandatory forbidden_use guard missing")
    if not card.get("counter_evidence") and not card.get("alternative_explanations") and card.get("confidence") != "low":
        errors.append("no countercheck cannot exceed low confidence")
    expiry = card.get("expiry_date")
    if expiry and not _valid_date(expiry):
        errors.append("invalid expiry_date")
    effective_as_of = as_of or date.today()
    if _valid_date(expiry) and date.fromisoformat(expiry) < effective_as_of and status != "expired":
        errors.append("expired evidence must have expired status")
    if errors:
        raise ContractError("; ".join(errors))
    result = dict(card)
    result["input_hash"] = sha256(card)
    result["model_hash"] = sha256(CONFIG)
    result["validated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return result


def prefilter(signals: list[dict[str, Any]], playbook: dict[str, Any], budget: dict[str, int] | None = None) -> dict[str, Any]:
    limits = dict(CONFIG["composition_budget"])
    if budget:
        limits.update(budget)
    target = playbook["decision_object"]
    applicable = [s for s in signals if all(s.get("decision_object", {}).get(k) == target.get(k) for k in OBJECT_KEYS)]
    applicable = [s for s in applicable if s.get("status") not in {"expired", "rejected"} and s.get("evidence_status", "current") not in {"invalidated", "superseded"}]
    vetoes = [s for s in applicable if s.get("signal_type") in set(playbook.get("veto_signals", []))]
    if vetoes:
        return {"composition_status": "blocked", "stop_reason": "veto_condition", "selected": vetoes, "execution_completion": "complete"}
    required_types = set(playbook.get("required_signals", []))
    present = {s.get("signal_type") for s in applicable}
    if not required_types.issubset(present):
        return {"composition_status": "inconclusive", "stop_reason": "required_signal_missing", "selected": [], "execution_completion": "complete"}
    by_family: dict[str, dict[str, Any]] = {}
    counters: list[dict[str, Any]] = []
    for signal in applicable:
        family = signal.get("source_family_id") or signal["signal_id"]
        if signal.get("role") == "counter":
            counters.append(signal)
        current = by_family.get(family)
        rank = (signal.get("quality", {}).get("completeness", 0), signal.get("expiry_date", ""))
        old_rank = ((current or {}).get("quality", {}).get("completeness", -1), (current or {}).get("expiry_date", ""))
        if current is None or rank > old_rank:
            by_family[family] = signal
    def priority(item: dict[str, Any]) -> float:
        cost = max(float(item.get("analysis_cost", 1)), 0.0001)
        return float(item.get("decision_impact", 0)) * float(item.get("information_gain", 0)) * float(item.get("quality", {}).get("completeness", 0)) / cost
    required = [s for s in by_family.values() if s.get("signal_type") in required_types]
    supporting = sorted((s for s in by_family.values() if s not in required and s.get("role") != "counter"), key=priority, reverse=True)
    counters = sorted(counters, key=priority, reverse=True)
    selected = required + supporting[:limits["max_supporting_per_playbook"]] + counters[:limits["max_counter_per_playbook"]]
    if len(applicable) > limits["max_signals"]:
        return {"composition_status": "inconclusive", "stop_reason": "signal_budget_exhausted", "selected": selected, "execution_completion": "partial"}
    return {"composition_status": "candidate", "stop_reason": None, "selected": selected, "execution_completion": "complete"}


def recovery_priority(event: dict[str, Any]) -> tuple[int, Decimal, tuple[Any, ...]]:
    queue = event.get("queue")
    if queue not in {"R0", "R1", "R2", "R3", "R4"}:
        raise ContractError("recovery queue must be R0-R4")
    if queue == "R0":
        return (0, Decimal("100"), ())
    weights = event.get("weights", {})
    metrics = event.get("metrics", {})
    if set(weights) != {"capital", "irreversibility", "time", "blast_radius", "decision_sensitivity", "evidence_criticality"}:
        raise ContractError("recovery weights incomplete")
    normalized_weights = {k: Decimal(str(v)) for k, v in weights.items()}
    weight_values = list(normalized_weights.values())
    if any(v < 0 for v in weight_values) or sum(weight_values) != Decimal("1"):
        raise ContractError("recovery weights must be nonnegative and sum to 1")
    if set(metrics) != set(weights):
        raise ContractError("recovery metrics incomplete")
    metric_values = {k: Decimal(str(v)) for k, v in metrics.items()}
    if any(v < 0 or v > 1 for v in metric_values.values()):
        raise ContractError("recovery metrics must be normalized to 0-1")
    score = Decimal("100") * sum(normalized_weights[k] * metric_values[k] for k in normalized_weights)
    return (int(queue[1]), score.quantize(Decimal("0.01")), (metrics["time"], event.get("net_capital_at_risk", 0), event.get("decision_deadline", ""), event.get("detected_at", "")))


def evidence_quality_gate(evidence: list[dict[str, Any]], required_ids: list[str], *, as_of: date) -> dict[str, Any]:
    """Evaluate completeness, freshness and source-family independence without optimistic defaults."""
    by_id = {item.get("evidence_id"): item for item in evidence}
    missing = sorted(set(required_ids) - set(by_id))
    stale: list[str] = []
    invalid: list[str] = []
    families: set[str] = set()
    for evidence_id in required_ids:
        item = by_id.get(evidence_id)
        if not item:
            continue
        if item.get("status") in {"invalidated", "missing", "superseded"}:
            invalid.append(evidence_id)
        expires = item.get("expiry_date")
        if not _valid_date(expires):
            invalid.append(evidence_id)
        elif date.fromisoformat(expires) < as_of or item.get("status") == "stale":
            stale.append(evidence_id)
        family = item.get("source_family_id")
        if not family:
            invalid.append(evidence_id)
        else:
            families.add(family)
    if missing or invalid:
        status = "blocked"
    elif stale:
        status = "inconclusive"
    else:
        status = "validated"
    return {
        "status": status,
        "missing_evidence_ids": missing,
        "stale_evidence_ids": sorted(set(stale)),
        "invalid_evidence_ids": sorted(set(invalid)),
        "independent_source_families": len(families),
        "requested_evidence_count": len(required_ids),
    }


def validate_field_trap_registry(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    traps = payload.get("traps")
    if not isinstance(traps, list) or not traps:
        raise ContractError("field trap registry requires traps")
    seen: set[str] = set()
    required = {"trap_id", "source", "tool", "observed_at", "documented_field", "observed_field", "symptom", "decision_impact", "detection", "fallback", "status", "owner", "expiry_review", "evidence_id"}
    for trap in traps:
        trap_id = trap.get("trap_id")
        if not trap_id or trap_id in seen:
            errors.append("trap_id must be unique and nonempty")
        seen.add(trap_id)
        absent = required - set(trap)
        if absent:
            errors.append(f"{trap_id}: missing {sorted(absent)}")
        if trap.get("status") not in TRAP_STATES:
            errors.append(f"{trap_id}: invalid lifecycle status")
        if not _valid_date(trap.get("observed_at")) or not _valid_date(trap.get("expiry_review")):
            errors.append(f"{trap_id}: invalid review dates")
        if trap.get("decision_impact") and not trap.get("detection"):
            errors.append(f"{trap_id}: high-impact trap lacks contract test")
        if trap.get("fallback") in {"default_zero", "silent_empty", "assume_success"}:
            errors.append(f"{trap_id}: optimistic fallback forbidden")
    if errors:
        raise ContractError("; ".join(errors))
    return {"status": "valid", "trap_count": len(traps), "registry_hash": sha256(payload)}


def validate_cidm_plco_packet(packet: dict[str, Any]) -> dict[str, Any]:
    required = {"packet_version", "decision_object", "cidm_decision_id", "product_facts", "proof_assets", "unsupported_claims", "prohibited_claims", "target_segments", "purchase_jobs", "purchase_objections", "keyword_clusters", "validated_pain_points", "differentiation_claims", "price_position", "weakest_assumption", "experiment_hypotheses", "allowed_use", "forbidden_use"}
    errors: list[str] = []
    absent = required - set(packet)
    if absent:
        errors.append("missing packet fields: " + ", ".join(sorted(absent)))
    obj = packet.get("decision_object", {})
    if any(not obj.get(key) for key in OBJECT_KEYS):
        errors.append("packet decision object incomplete")
    if set(packet.get("allowed_use", [])) != PACKET_ALLOWED_USE:
        errors.append("PLCO packet allowed_use must be listing acceptance only")
    if not PACKET_FORBIDDEN_USE.issubset(set(packet.get("forbidden_use", []))):
        errors.append("PLCO packet must forbid investment score override")
    proof_ids = {asset.get("proof_id") for asset in packet.get("proof_assets", []) if isinstance(asset, dict)}
    for claim in packet.get("differentiation_claims", []):
        if not isinstance(claim, dict) or not claim.get("claim") or claim.get("proof_id") not in proof_ids:
            errors.append("every differentiation claim requires an existing proof_id")
    prohibited = set(packet.get("prohibited_claims", []))
    if any(claim.get("claim") in prohibited for claim in packet.get("differentiation_claims", []) if isinstance(claim, dict)):
        errors.append("prohibited claim cannot enter differentiation claims")
    if FORBIDDEN_ACTION_FIELDS & set(packet):
        errors.append("PLCO packet cannot change investment authority")
    if errors:
        raise ContractError("; ".join(errors))
    return {"status": "valid", "packet_hash": sha256(packet)}


def validate_rapid_decision_card(card: dict[str, Any]) -> dict[str, Any]:
    required = {"decision", "confidence", "lifecycle", "supporting_evidence", "counter_evidence", "weakest_assumption", "priority_actions", "do_not_do_yet", "missing_data", "minimum_credible_validation", "go", "stop"}
    absent = required - set(card)
    errors: list[str] = []
    if absent:
        errors.append("missing decision-card fields: " + ", ".join(sorted(absent)))
    if card.get("decision") not in {"建议进入", "谨慎小测", "仅观察/内容测款", "不建议进入"}:
        errors.append("decision must use CIDM four-tier conclusion")
    if len(card.get("priority_actions", [])) != 3:
        errors.append("priority_actions must contain exactly three actions")
    if not card.get("counter_evidence"):
        errors.append("decision card requires counterevidence")
    if not card.get("do_not_do_yet") or not card.get("stop"):
        errors.append("Do Not Do Yet and Stop cannot be empty")
    if errors:
        raise ContractError("; ".join(errors))
    return {"status": "valid", "card_hash": sha256(card)}


def run_research_dag(tasks: list[dict[str, Any]], runner: Any, *, max_workers: int = 4) -> dict[str, Any]:
    """Run dependency-ready acquisition tasks; disclose partial failure and block dependants."""
    if max_workers < 1:
        raise ContractError("max_workers must be positive")
    task_map = {task.get("task_id"): task for task in tasks}
    if None in task_map or len(task_map) != len(tasks):
        raise ContractError("task_id must be unique and nonempty")
    results: dict[str, dict[str, Any]] = {}
    pending = set(task_map)
    while pending:
        ready = sorted(task_id for task_id in pending if set(task_map[task_id].get("dependencies", [])) <= set(results))
        if not ready:
            raise ContractError("research DAG contains a cycle or unknown dependency")
        runnable: list[str] = []
        for task_id in ready:
            dependencies = task_map[task_id].get("dependencies", [])
            if any(results[dependency]["status"] != "complete" for dependency in dependencies):
                results[task_id] = {"task_id": task_id, "status": "blocked", "reason": "dependency_failed", "evidence_id": None}
                pending.remove(task_id)
            else:
                runnable.append(task_id)
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(runner, task_map[task_id]): task_id for task_id in runnable}
            for future in as_completed(futures):
                task_id = futures[future]
                try:
                    value = future.result()
                    if not isinstance(value, dict) or not value.get("evidence_id"):
                        raise ContractError("runner returned no evidence_id")
                    results[task_id] = {"task_id": task_id, "status": "complete", **value}
                except Exception as exc:  # explicit failure record; no silent empty conversion
                    results[task_id] = {"task_id": task_id, "status": "failed", "reason": type(exc).__name__, "evidence_id": None}
                pending.remove(task_id)
    failed = [task_id for task_id, result in results.items() if result["status"] != "complete"]
    return {
        "execution_completion": "complete" if not failed else "partial",
        "results": [results[task_id] for task_id in sorted(results)],
        "failed_or_blocked_tasks": sorted(failed),
        "output_hash": sha256(results),
    }


def validate_playbook_registry(payload: dict[str, Any]) -> dict[str, Any]:
    playbooks = payload.get("playbooks")
    if not isinstance(playbooks, list) or len(playbooks) != 5:
        raise ContractError("exactly five governed combination playbooks are required")
    ids: set[str] = set()
    allowed_outputs = {"validation_plan", "competition_entry_evidence_card", "product_concept_validation_card", "profit_and_capital_tolerance_card", "season_entry_or_stop"}
    for playbook in playbooks:
        playbook_id = playbook.get("playbook_id")
        if not playbook_id or playbook_id in ids:
            raise ContractError("playbook_id must be unique and nonempty")
        ids.add(playbook_id)
        if not playbook.get("required_signals"):
            raise ContractError(f"{playbook_id}: required_signals cannot be empty")
        if any(name not in CONFIG["signal_names"] for name in playbook.get("required_signals", []) + playbook.get("supporting_signals", []) + playbook.get("counter_signals", [])):
            raise ContractError(f"{playbook_id}: unregistered signal name")
        if not playbook.get("veto_conditions"):
            raise ContractError(f"{playbook_id}: veto_conditions cannot be empty")
        if playbook.get("allowed_output") not in allowed_outputs:
            raise ContractError(f"{playbook_id}: output exceeds governed boundary")
    return {"status": "valid", "playbook_count": len(playbooks), "registry_hash": sha256(payload)}


def compose_playbook(playbook: dict[str, Any], signals: list[dict[str, Any]], active_vetoes: list[str]) -> dict[str, Any]:
    """Compose evaluated signal families without voting, score addition, or investment actions."""
    triggered_vetoes = sorted(set(playbook.get("veto_conditions", [])) & set(active_vetoes))
    if triggered_vetoes:
        return {"playbook_id": playbook["playbook_id"], "composition_status": "blocked", "triggered_vetoes": triggered_vetoes, "allowed_output": playbook["allowed_output"], "selected_signal_ids": []}
    current = [signal for signal in signals if signal.get("status") not in {"expired", "rejected", "blocked"}]
    required = set(playbook.get("required_signals", []))
    validated_types = {signal.get("signal_type") for signal in current if signal.get("status") in {"candidate", "proposed", "validated"}}
    if not required.issubset(validated_types):
        return {"playbook_id": playbook["playbook_id"], "composition_status": "inconclusive", "triggered_vetoes": [], "allowed_output": playbook["allowed_output"], "selected_signal_ids": []}
    allowed_types = required | set(playbook.get("supporting_signals", [])) | set(playbook.get("counter_signals", []))
    selected: dict[str, dict[str, Any]] = {}
    for signal in current:
        if signal.get("signal_type") not in allowed_types:
            continue
        family = signal.get("source_family_id") or signal.get("signal_id")
        if not family:
            raise ContractError("composed signal requires signal_id or source_family_id")
        existing = selected.get(family)
        rank = (signal.get("status") == "validated", signal.get("quality", {}).get("completeness", 0))
        old_rank = ((existing or {}).get("status") == "validated", (existing or {}).get("quality", {}).get("completeness", -1))
        if existing is None or rank > old_rank:
            selected[family] = signal
    return {"playbook_id": playbook["playbook_id"], "composition_status": "proposed", "triggered_vetoes": [], "allowed_output": playbook["allowed_output"], "selected_signal_ids": sorted(signal["signal_id"] for signal in selected.values()), "forbidden_output": "automatic_investment_action", "composition_hash": sha256({"playbook": playbook, "signals": selected})}
