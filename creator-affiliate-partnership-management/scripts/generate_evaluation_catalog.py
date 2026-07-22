#!/usr/bin/env python3
"""Generate decision-distinct, executable CAPM evaluation fixtures."""
from __future__ import annotations
import json
from pathlib import Path

HIGH_RISK = {"pay", "sign", "ship_sample", "publish", "reuse", "paid_amplification", "scale"}

SOLO = [
    ("creator_identity", "只有达人链接，是否建联", "Q1", "G1A", "inconclusive", ["contact", "pay"], ["contact"]),
    ("quote_walkaway", "固定费与佣金报价边界", "Q3", "G4", "pass", ["negotiate", "sign"], ["negotiate", "sign"]),
    ("sample_title", "首次寄样与货权", "Q2", "G5", "inconclusive", ["ship_sample", "scale"], ["ship_sample"]),
    ("affiliate_commission", "联盟佣金阶梯", "Q3", "G4", "pass", ["change_commission", "scale"], ["change_commission", "scale"]),
    ("late_delivery", "延迟交付与合同补救", "Q3", "G3", "pass", ["remedy", "withhold_disputed"], ["remedy", "withhold_disputed"]),
    ("rights_expiry", "权利到期与衍生内容", "Q3", "G1B", "blocked", ["reuse", "renew"], ["renew"]),
    ("order_reconciliation", "联盟订单异常守恒", "Q3", "G6", "inconclusive", ["hold_disputed", "claim_incremental"], ["hold_disputed"]),
    ("portfolio_concentration", "头部依赖与替代漏斗", "Q3", "G4", "pass", ["renew", "build_backup"], ["renew", "build_backup"]),
    ("minor_or_guardian", "疑似未成年人", "Q1", "G1A", "blocked", ["contact_guardian", "pay", "sign"], ["contact_guardian"]),
    ("payee_mismatch", "签约付款收款主体不一致", "Q2", "G1A", "blocked", ["verify_payee", "pay"], ["verify_payee"]),
    ("ai_identity_rights", "AI配音与数字分身", "Q3", "G1B", "blocked", ["organic_publish", "ai_clone"], ["organic_publish"]),
    ("privacy_withdrawal", "撤回同意与传播闭包", "Q3", "G3", "blocked", ["preserve_legal_record", "reuse"], ["preserve_legal_record"]),
    ("recruitment_funnel", "达人招募反向漏斗", "Q2", "G4", "inconclusive", ["outreach", "mass_pay"], ["outreach"]),
    ("contract_renewal", "续约、降级或退出", "Q3", "G4", "pass", ["renew", "exit"], ["renew", "exit"]),
    ("network_migration", "联盟网络迁移与未结订单", "Q2", "G6", "inconclusive", ["parallel_reconcile", "close_old_network"], ["parallel_reconcile"]),
    ("tax_fx_cash", "多币种预扣税与现金谷底", "Q2", "G4", "inconclusive", ["parameterize", "pay"], ["parameterize"]),
]

CROSS = [
    ("cidm_capital", ["CIDM"], "CAPM成熟经济只能作为资本输入", "renew"),
    ("cidm_conflict", ["CIDM"], "战略价值高但合作下界为负", "hold"),
    ("cim_competitor_creator", ["CIM"], "竞品达人动作不能推导我方报价", "investigate"),
    ("cim_proxy_conflict", ["CIM"], "公开代理与授权后台冲突", "verify"),
    ("vlb_high_score_rights_fail", ["VLB"], "内容机制高分不能覆盖权利失败", "renew_rights"),
    ("vlb_brief_boundary", ["VLB"], "CAPM只管商务Brief必做项", "route_brief"),
    ("cig_complaint_acceptance", ["CIG"], "客户投诉证据影响验收但不越权触达", "repair_acceptance"),
    ("cig_retention_negative", ["CIG"], "复购下界负时降级续约", "reduce"),
    ("aamo_paid_candidate", ["AAMO"], "CAPM只提交付费权利候选", "submit_candidate"),
    ("aamo_negative_incrementality", ["AAMO"], "归因正增量负停止放大", "stop_scale"),
    ("lifd_capacity", ["LIFD"], "库存不足阻断规模承诺", "limit_commitment"),
    ("plco_broken_link", ["PLCO"], "页面故障与达人交付责任拆分", "repair_link"),
    ("content_paid_inventory", ["VLB", "AAMO", "LIFD"], "高内容分但权利与库存限制投放", "partial_success"),
    ("partial_timeout", ["CIG", "AAMO", "LIFD"], "一个超时不污染其他结果", "bounded_result"),
]

MULTI = [
    ("evidence_upgrade", ["investigate", "contact", "ship_sample", "sign"]),
    ("evidence_withdrawal", ["sign", "sign", "investigate", "exit"]),
    ("quote_rounds", ["negotiate", "negotiate", "walk_away", "conditional_sign"]),
    ("rights_expiry_renewal", ["reuse", "renew", "organic_only", "reuse"]),
    ("refund_maturity_flip", ["test", "test", "reduce", "stop_scale"]),
    ("duplicate_message", ["ship_sample", "ship_sample", "ship_sample", "reconcile_once"]),
    ("concurrent_contract_branches", ["negotiate", "branch_review", "resolve_conflict", "sign_one_version"]),
    ("late_old_data", ["test", "hold_old_data", "recompute", "test"]),
    ("new_creator_object", ["investigate", "contact", "close_old_chain", "open_new_chain"]),
    ("country_migration", ["organic_only", "rule_check", "rights_check", "conditional_publish"]),
    ("incident_recovery", ["bounded_freeze", "verify", "partial_restore", "close_incident"]),
    ("missing_parent", ["investigate", "block_orphan", "repair_lineage", "resume"]),
]

EXTREME = [
    "account_takeover", "deepfake_voice", "creator_death", "mcn_bankruptcy", "platform_exit", "cookie_stuffing",
    "chargeback_wave", "minor_without_guardian", "data_breach", "internal_kickback", "sanctions_beneficiary",
    "consent_withdrawal_derivatives", "war_logistics_failure", "payment_rail_outage", "algorithmic_discrimination",
    "viral_stockout", "recall_during_campaign", "double_p0_rights_and_fraud", "p0_high_profit_conflict",
    "recovered_account_rights_still_blocked",
]


def gates(target: str, status: str, allowed: list[str], candidates: list[str]) -> dict:
    result = {}
    for gate in ("G1A", "G1B", "G2", "G3", "G4", "G5", "G6"):
        state = status if gate == target else "pass"
        result[gate] = {"status": state, "blocked_actions": sorted(set(candidates) - set(allowed)) if gate == target else [],
                        "recovery_evidence": [f"{gate.lower()}_recovery"] if state != "pass" else [],
                        "owner_skill": "creator-affiliate-partnership-management"}
    return result


def executable(case_id: str, prompt: str, quality: str, target: str, status: str, candidates: list[str], allowed: list[str], causal: str = "C0") -> dict:
    inp = {"decision_id": case_id, "prompt": prompt,
           "object": {"canonical_id": f"object-{case_id.lower()}", "object_version": "v1", "object_type": "partnership"},
           "scope": {"platform": "TikTok", "country": "US", "currency": "USD", "timezone": "America/New_York", "as_of_time": "2026-07-22T00:00:00Z"},
           "input_quality": quality, "causal_evidence_level": causal,
           "evidence": [{"evidence_id": f"E-{case_id}", "level": "S3" if quality in {"Q2", "Q3"} else "S1"}],
           "gates": gates(target, status, allowed, candidates), "candidate_actions": candidates}
    expected_allowed = set(allowed)
    if quality in {"Q0", "Q1"}: expected_allowed -= HIGH_RISK
    expected_blocked = set(candidates) - expected_allowed
    if target in {"G1A", "G1B", "G2", "G3"} and status == "blocked": posture = "Blocked"
    elif not expected_allowed: posture = "Hold"
    elif expected_allowed & HIGH_RISK: posture = "Conditional Go" if quality == "Q3" else "Test"
    else: posture = "Investigate"
    return {"script": "scripts/evaluate_capm_decision.py", "script_input": inp,
            "expected_output": {"posture": posture, "allowed_actions": sorted(expected_allowed), "blocked_actions": sorted(expected_blocked),
                                "causal_label": "incremental_eligible" if causal in {"C2", "C3"} else "attributed_or_inconclusive"},
            "expected_intermediate_state": {"gate": target, "gate_status": status},
            "calculation_expectations": [], "evidence_conflicts": [], "report_type": "Decision Card"}


def build() -> dict:
    cases = []
    for idx, (family, prompt, quality, target, status, candidates, allowed) in enumerate(SOLO, 1):
        case_id = f"CAPM-S{idx:02d}"
        cases.append({"id": case_id, "family": family, "mode": "solo", "owner_skill": "CAPM", "participants": [],
                      **executable(case_id, prompt, quality, target, status, candidates, allowed),
                      "required_assertions": ["object_version", "gate_state", "allowed_and_blocked_actions", "stop_rollback_exit"],
                      "forbidden": ["unverified_dynamic_threshold", "sovereignty_overreach", "attributed_as_incremental"]})
    for idx, (family, participants, prompt, expected) in enumerate(CROSS, 1):
        case_id = f"CAPM-X{idx:02d}"; ex = executable(case_id, prompt, "Q2", "G6", "inconclusive", [expected, "scale"], [expected])
        ex["report_type"] = "Decision Memo"
        cases.append({"id": case_id, "family": family, "mode": "cross_skill", "owner_skill": "CAPM", "participants": participants,
                      **ex, "expected_cross_skill_status": {p: "proposed" for p in participants},
                      "required_assertions": ["owner_field_merge", "partial_failure_isolation", "receiver_acceptance"],
                      "forbidden": ["receiver_sovereignty_takeover", "silent_history_overwrite"]})
    for idx, (family, action_sequence) in enumerate(MULTI, 1):
        case_id = f"CAPM-M{idx:02d}"; ex = executable(case_id, family, "Q2", "G1B", "inconclusive", ["investigate", "reuse"], ["investigate"])
        ex["report_type"] = "Progressive Decision"
        turns = []
        previous_actions: set[str] = set()
        for n in range(1, 5):
            parent_id = None if n == 1 else f"{case_id}-R{n-1}"
            if family == "missing_parent" and n == 2: parent_id = "missing-report"
            current_actions = {action_sequence[n-1]}
            turns.append({"turn": n, "event": family, "report_id": f"{case_id}-R{n}", "parent_report_id": parent_id,
                          "object_id": f"object-{case_id.lower()}", "object_version": f"v{n}", "changed_fields": [] if n == 1 else [family],
                          "new_evidence_ids": [] if n == 1 else [f"{case_id}-E{n}"], "affected_claims": [] if n == 1 else [f"{case_id}-CL1"],
                          "affected_calculations": [] if n == 1 else [f"{case_id}-C1"], "preserved_constraints": ["G1A"],
                          "superseded_actions": sorted(previous_actions - current_actions), "current_actions": sorted(current_actions),
                          "next_recompute_trigger": ["new evidence"], "expected_valid": not (family == "missing_parent" and n == 2)})
            previous_actions = current_actions
        cases.append({"id": case_id, "family": family, "mode": "multi_turn", "owner_skill": "CAPM", "participants": [], **ex,
                      "turns": turns, "expected_transition": action_sequence,
                      "required_assertions": ["parent_chain", "affected_closure", "no_silent_overwrite", "idempotency"],
                      "forbidden": ["old_action_resurrection", "cross_object_evidence_inheritance"]})
    for idx, family in enumerate(EXTREME, 1):
        case_id = f"CAPM-Z{idx:02d}"; ex = executable(case_id, family, "Q2", "G1A", "blocked", ["preserve_evidence", "pay", "publish", "scale"], ["preserve_evidence"])
        ex["report_type"] = "Incident & Recovery"
        cases.append({"id": case_id, "family": family, "mode": "extreme", "owner_skill": "CAPM", "participants": ["LCR"] if "rights" in family or "sanctions" in family else [], **ex,
                      "incident_controls": {"freeze_scope": family, "preserve_uncontested_obligations": True, "recovery_requires": ["owner_acceptance", "fresh_evidence", "bounded_restore"]},
                      "required_assertions": ["p0_overrides_score", "bounded_freeze", "uncontested_obligations_preserved", "recovery_sequence"],
                      "forbidden": ["global_freeze", "high_profit_override", "unverified_public_accusation"]})
    return {"catalog_version": "CAPM-EVAL-2026.02", "count": len(cases), "coverage": {"solo": 16, "cross_skill": 14, "multi_turn": 12, "extreme": 20}, "cases": cases}


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "evaluations/fixtures/evaluation-catalog.json"
    payload = build(); output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {payload['count']} executable cases to {output}")
