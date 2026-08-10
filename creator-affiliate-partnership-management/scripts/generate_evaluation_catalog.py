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

SOLO += [
    ("product_claim_evidence", "产品功效证据不足时限制Brief和寄样", "Q1", "G2", "blocked", ["draft_brief", "ship_sample"], ["draft_brief"]),
    ("product_variant_mismatch", "寄样SKU与已验证产品事实版本不一致", "Q2", "G2", "blocked", ["verify_variant", "ship_sample"], ["verify_variant"]),
    ("brief_claim_recovery", "补齐产品声明证据后恢复受限Brief", "Q3", "G2", "pass", ["approve_claim", "ship_sample"], ["approve_claim", "ship_sample"]),
    ("platform_disclosure", "商业内容披露状态不明", "Q2", "G3", "inconclusive", ["verify_disclosure", "publish"], ["verify_disclosure"]),
    ("country_rule_expired", "国家广告规则卡已经过期", "Q2", "G3", "blocked", ["refresh_rule", "publish"], ["refresh_rule"]),
    ("settlement_legal_hold", "争议订单只冻结受影响结算", "Q3", "G3", "pass", ["hold_disputed", "pay_uncontested"], ["hold_disputed", "pay_uncontested"]),
    ("sample_atp_shortage", "样品ATP不足时如何分配", "Q2", "G5", "blocked", ["reserve_sample", "mass_ship"], ["reserve_sample"]),
    ("warehouse_capacity", "活动峰值仓容不足", "Q3", "G5", "blocked", ["limit_commitment", "scale"], ["limit_commitment"]),
    ("sample_delivery_recovery", "补充样品和物流能力后分批恢复", "Q3", "G5", "pass", ["staged_ship", "scale"], ["staged_ship", "scale"]),
    ("positive_first_collaboration", "合格达人首次小规模合作", "Q3", "G4", "pass", ["sign", "ship_sample"], ["sign", "ship_sample"]),
    ("positive_affiliate_settlement", "联盟成熟订单正常对账结算", "Q3", "G6", "pass", ["reconcile", "pay"], ["reconcile", "pay"]),
    ("positive_rights_renewal", "权利续签后恢复指定用途", "Q3", "G1B", "pass", ["renew", "reuse"], ["renew", "reuse"]),
    ("brief_revision_limit", "修改次数达到合同上限", "Q3", "G3", "blocked", ["accept_or_remedy", "add_unpaid_revision"], ["accept_or_remedy"]),
    ("sample_loss_economics", "低发布率导致寄样损失", "Q3", "G4", "blocked", ["reduce_batch", "mass_ship"], ["reduce_batch"]),
    ("creator_ltv_renewal", "用成熟贡献LTV判断续约上限", "Q3", "G4", "pass", ["renew", "raise_fee"], ["renew", "raise_fee"]),
    ("workforce_capacity", "BD人效不足时限制扩池", "Q2", "G5", "inconclusive", ["measure_capacity", "mass_recruit"], ["measure_capacity"]),
    ("amazon_program_route", "Amazon联盟计划正常路由", "Q2", "G3", "inconclusive", ["verify_current_program", "launch"], ["verify_current_program"]),
    ("shopee_creator_route", "Shopee达人计划正常路由", "Q2", "G3", "inconclusive", ["verify_current_program", "launch"], ["verify_current_program"]),
    ("lazada_creator_route", "Lazada达人计划正常路由", "Q2", "G3", "inconclusive", ["verify_current_program", "launch"], ["verify_current_program"]),
    ("dtc_affiliate_route", "DTC联盟网络正常路由", "Q2", "G6", "inconclusive", ["instrument", "claim_incremental"], ["instrument"]),
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

CROSS += [
    ("cidm_portfolio_cash", ["CIDM"], "现金谷底限制资本承诺但不改投资主权", "submit_cash_boundary"),
    ("cim_sanction_signal", ["CIM"], "公开制裁信号只触发核验而非定罪", "verify_identity"),
    ("vlb_failed_brief", ["VLB"], "内容失效需拆分机制与商务验收责任", "split_diagnosis"),
    ("cig_promise_harm", ["CIG"], "客户伤害信号触发承诺审查和有限冻结", "review_promise"),
    ("aamo_rights_expiry", ["AAMO"], "投流中权利临近到期只提交用途状态", "submit_rights_expiry"),
    ("lifd_sample_allocation", ["LIFD"], "有限样品按已批准优先级分配", "request_allocation"),
    ("plco_tracking_break", ["PLCO"], "挂链追踪故障拆分页面与结算影响", "bound_tracking_impact"),
    ("cidm_ltv_input", ["CIDM"], "达人LTV只作为资本输入且保留不确定性", "submit_ltv_interval"),
    ("cim_creator_migration", ["CIM"], "竞品达人迁移事件不自动触发我方抢签", "investigate_migration"),
    ("vlb_claim_boundary", ["VLB"], "内容机制建议不得覆盖产品声明证据门", "route_claim_evidence"),
    ("cig_deidentified_promise", ["CIG"], "仅传去识别客户承诺上下文", "send_deidentified_context"),
    ("aamo_incrementality_return", ["AAMO"], "增量结果回传后重算权利成本上限", "recompute_ceiling"),
    ("lifd_recall_exit", ["LIFD"], "召回期间关闭受影响合作并保留结算义务", "bounded_exit"),
    ("plco_repaired_link", ["PLCO"], "页面修复确认后恢复链接相关验收", "conditional_restore"),
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

MULTI += [
    ("product_evidence_recovery", ["draft_brief", "verify_claim", "approve_claim", "ship_sample"]),
    ("sample_capacity_recovery", ["reserve_sample", "reduce_batch", "confirm_atp", "staged_ship"]),
    ("affiliate_activation", ["recruit", "onboard", "first_click", "first_mature_order"]),
    ("settlement_dispute", ["reconcile", "hold_disputed", "resolve", "pay_uncontested"]),
    ("creator_positive_renewal", ["test", "measure", "renew", "expand_conditionally"]),
    ("platform_rule_refresh", ["hold_publish", "refresh_rule", "independent_check", "conditional_publish"]),
    ("brief_revision_recovery", ["request_revision", "review", "accept", "close_delivery"]),
    ("rights_withdrawal_close", ["freeze_use", "map_derivatives", "remove_affected", "close_rights"]),
    ("fraud_false_positive", ["bounded_hold", "review", "clear_partner", "restore_settlement"]),
    ("cash_trough_replan", ["hold_commitment", "rephase_cash", "approve_ceiling", "conditional_sign"]),
    ("new_country_launch", ["verify_rule", "verify_rights", "verify_payee", "pilot_launch"]),
    ("program_exit", ["stop_recruitment", "reconcile_open_orders", "pay_uncontested", "close_program"]),
]

EXTREME = [
    "account_takeover", "deepfake_voice", "creator_death", "mcn_bankruptcy", "platform_exit", "cookie_stuffing",
    "chargeback_wave", "minor_without_guardian", "data_breach", "internal_kickback", "sanctions_beneficiary",
    "consent_withdrawal_derivatives", "war_logistics_failure", "payment_rail_outage", "algorithmic_discrimination",
    "viral_stockout", "recall_during_campaign", "double_p0_rights_and_fraud", "p0_high_profit_conflict",
    "recovered_account_rights_still_blocked",
]

PROPERTY = [
    ("nonfinite_economics", "G4", "NaN或Infinity不得进入经济动作"),
    ("negative_count", "G5", "负样品或订单计数必须拒绝"),
    ("rate_over_one", "G4", "转化率大于一必须拒绝"),
    ("currency_pollution", "G4", "币种改变未重算必须阻断"),
    ("object_substitution", "G1A", "对象替换不得继承证据"),
    ("evidence_copy", "G1A", "复制同一证据不得增加独立性"),
    ("expired_dynamic_rule", "G3", "过期规则不得作为当前门槛"),
    ("attribution_renamed_incremental", "G6", "归因改名增量必须失败"),
    ("allowed_forbidden_overlap", "G1B", "允许与禁止用途重叠必须失败"),
    ("stale_rights_version", "G1B", "旧权利版本不得授权当前用途"),
    ("superseded_action_resurrection", "G1B", "被替代动作不得复活"),
    ("score_overrides_p0", "G1A", "高分不得覆盖P0"),
]

def capability(family: str) -> str:
    if family in {name for name, _, _ in PROPERTY} or any(k in family for k in ("evidence_upgrade", "evidence_withdrawal", "duplicate_message", "late_old_data", "missing_parent", "partial_timeout")): return "data_automation_quality"
    if any(k in family for k in ("affiliate", "order", "settlement", "cookie", "network_migration", "program_exit", "chargeback", "refund")): return "affiliate_operations"
    if any(k in family for k in ("rights", "contract", "consent", "privacy", "ai_identity")): return "rights_contract_exit"
    if any(k in family for k in ("sample", "brief", "delivery", "capacity", "stock", "recall", "product", "plco", "content")): return "sample_brief_delivery"
    if any(k in family for k in ("quote", "commission", "cash", "ltv", "portfolio", "economics", "workforce", "cidm", "aamo", "positive_first_collaboration")): return "economics_negotiation_portfolio"
    if any(k in family for k in ("platform", "country", "amazon", "shopee", "lazada", "dtc")): return "platform_country"
    if any(k in family for k in ("incident", "takeover", "fraud", "breach", "sanction", "death", "bankruptcy", "war", "outage", "kickback", "deepfake")): return "incident_recovery"
    return "creator_diligence_lifecycle"

def route_gate(family: str, default: str) -> str:
    if any(k in family for k in ("product", "claim", "brief", "content", "acceptance")): return "G2"
    if any(k in family for k in ("platform", "country", "disclosure", "legal", "tax", "sanction", "privacy")): return "G3"
    if any(k in family for k in ("sample", "capacity", "stock", "delivery", "recall", "logistics", "fulfillment", "warehouse", "viral")): return "G5"
    if any(k in family for k in ("quote", "commission", "cash", "ltv", "portfolio", "economics", "workforce", "renewal")): return "G4"
    if any(k in family for k in ("rights", "consent", "contract")): return "G1B"
    return default

def decorate(case: dict, family: str, gate: str, status: str) -> dict:
    case.update({"capability_group":capability(family), "primary_mechanism":family,
                 "lifecycle_phase":"recovery" if "recovery" in family or status == "blocked" else "operate",
                 "outcome_class":"failure" if status == "blocked" else "edge" if status == "inconclusive" else "normal",
                 "primary_gate":gate})
    return case


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
                                "causal_label": "legacy_c_label_non_equivalent" if causal in {"C2", "C3"} else "attributed_or_inconclusive"},
            "expected_intermediate_state": {"gate": target, "gate_status": status},
            "calculation_expectations": [], "evidence_conflicts": [], "report_type": "Decision Card"}


def build() -> dict:
    cases = []
    for idx, (family, prompt, quality, target, status, candidates, allowed) in enumerate(SOLO, 1):
        case_id = f"CAPM-S{idx:02d}"
        cases.append(decorate({"id": case_id, "family": family, "mode": "solo", "owner_skill": "CAPM", "participants": [],
                      **executable(case_id, prompt, quality, target, status, candidates, allowed),
                      "required_assertions": ["object_version", "gate_state", "allowed_and_blocked_actions", "stop_rollback_exit"],
                      "forbidden": ["unverified_dynamic_threshold", "sovereignty_overreach", "attributed_as_incremental"]}, family, target, status))
    for idx, (family, participants, prompt, expected) in enumerate(CROSS, 1):
        case_id = f"CAPM-X{idx:02d}"; target=route_gate(family,"G6"); ex = executable(case_id, prompt, "Q2", target, "inconclusive", [expected, "scale"], [expected])
        ex["report_type"] = "Decision Memo"
        cases.append(decorate({"id": case_id, "family": family, "mode": "cross_skill", "owner_skill": "CAPM", "participants": participants,
                      **ex, "expected_cross_skill_status": {p: "proposed" for p in participants},
                      "required_assertions": ["owner_field_merge", "partial_failure_isolation", "receiver_acceptance"],
                      "forbidden": ["receiver_sovereignty_takeover", "silent_history_overwrite"]}, family, target, "inconclusive"))
    for idx, (family, action_sequence) in enumerate(MULTI, 1):
        case_id = f"CAPM-M{idx:02d}"; target=route_gate(family,"G1B"); status="inconclusive"; ex = executable(case_id, family, "Q2", target, status, ["investigate", "reuse"], ["investigate"])
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
        case=decorate({"id": case_id, "family": family, "mode": "multi_turn", "owner_skill": "CAPM", "participants": [], **ex,
                      "turns": turns, "expected_transition": action_sequence,
                      "required_assertions": ["parent_chain", "affected_closure", "no_silent_overwrite", "idempotency"],
                      "forbidden": ["old_action_resurrection", "cross_object_evidence_inheritance"]}, family, target, status)
        if idx > 12: case["outcome_class"]="normal"; case["lifecycle_phase"]="recovery"
        cases.append(case)
    for idx, family in enumerate(EXTREME, 1):
        case_id = f"CAPM-Z{idx:02d}"; ex = executable(case_id, family, "Q2", "G1A", "blocked", ["preserve_evidence", "pay", "publish", "scale"], ["preserve_evidence"])
        ex["report_type"] = "Incident & Recovery"
        cases.append(decorate({"id": case_id, "family": family, "mode": "extreme", "owner_skill": "CAPM", "participants": ["LCR"] if "rights" in family or "sanctions" in family else [], **ex,
                      "incident_controls": {"freeze_scope": family, "preserve_uncontested_obligations": True, "recovery_requires": ["owner_acceptance", "fresh_evidence", "bounded_restore"]},
                      "required_assertions": ["p0_overrides_score", "bounded_freeze", "uncontested_obligations_preserved", "recovery_sequence"],
                      "forbidden": ["global_freeze", "high_profit_override", "unverified_public_accusation"]}, family, "G1A", "blocked"))
    for idx, (family, gate, prompt) in enumerate(PROPERTY, 1):
        case_id=f"CAPM-P{idx:02d}"; ex=executable(case_id,prompt,"Q2",gate,"blocked",["preserve_evidence","high_risk_action"],["preserve_evidence"])
        cases.append(decorate({"id":case_id,"family":family,"mode":"property","owner_skill":"CAPM","participants":[],**ex,
                              "property_mutation":family,"required_assertions":["mutation_changes_result","deterministic_failure"],
                              "forbidden":["silent_coercion","score_compensation"]},family,gate,"blocked"))
    coverage={mode:sum(c["mode"]==mode for c in cases) for mode in ("solo","cross_skill","multi_turn","extreme","property")}
    distributions={key:{value:sum(c[key]==value for c in cases) for value in sorted({c[key] for c in cases})} for key in ("primary_gate","capability_group","outcome_class","lifecycle_phase")}
    return {"catalog_version": "CAPM-EVAL-2026.07", "count": len(cases), "coverage": coverage, "distributions":distributions, "cases": cases}


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "evaluations/fixtures/evaluation-catalog.json"
    payload = build(); output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {payload['count']} executable cases to {output}")
