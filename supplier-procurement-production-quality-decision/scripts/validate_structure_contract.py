#!/usr/bin/env python3
import json,pathlib,sys
import jsonschema
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    required=["SKILL.md","agents/openai.yaml","references/charter-object-network.md","references/evidence-measurement-governance.md","references/decision-models.md","references/cross-domain-migration.md","references/continuity-report-evaluation.md","scripts/normalize_dirty_inputs.py","scripts/independent_oracles.py","schemas/decision.schema.json","schemas/cross-domain-envelope.schema.json","schemas/continuous-state.schema.json","schemas/professional-report.schema.json","evaluations/evaluation-catalog.json","evaluations/golden-professional-reports.json","evaluations/historical-replay-template.json","evaluations/operator-routing-cases.json"]
    missing=[x for x in required if not (ROOT/x).is_file()]
    for p in (ROOT/"schemas").glob("*.json"):
        s=json.loads(p.read_text());jsonschema.Draft202012Validator.check_schema(s)
    reference_files=list((ROOT/"references").rglob("*.md"))
    reference_text="\n".join(p.read_text() for p in reference_files)
    reference_lines=sum(len(p.read_text().splitlines()) for p in reference_files)
    if reference_lines<500:missing.append(f"professional_reference_depth:{reference_lines}<500")
    required_anchors=[
        "HHI =","Should-cost","TCO =","有效产能 =","RPN =","P/T =","ndc =",
        "UCL/LCL =","Cp =","Cpk =","3 / n","COQ =","failure rate =",
        "REALITY_RECOVERY","十四段完整结构",
    ]
    absent=[anchor for anchor in required_anchors if anchor not in reference_text]
    if absent:missing.append(f"professional_reference_anchors:{absent}")
    per_file_anchors={
        "references/charter-object-network.md":["六类主权与对象","主键与版本","供应网络图","变更影响闭包","职责分离"],
        "references/evidence-measurement-governance.md":["证据登记最小字段","Chain of custody","数据质量维度","测量不确定度","证明上限"],
        "references/decision-models.md":["供应商选择","Should-cost","产能、节拍与交期","测量系统","过程稳定与能力","抽样、AQL","可靠性","复杂场景组合"],
        "references/cross-domain-migration.md":["域间主权矩阵","消费者响应","部分失败","D05 临时专业意见","迁移双轨与回滚"],
        "references/continuity-report-evaluation.md":["Current Decision State","Delta 分类","状态传播","现实恢复","评测 oracle","L1—L4 边界"],
        "references/data-contract-and-automation.md":["字段语义","幂等与并发","哈希与可重放","隐私与最小化","脏数据处理"],
        "references/professional-depth-governance.md":["十项深度门","机制而非篇幅","校准纪律","结论上限"],
        "references/skill-integration-protocol.md":["标准 envelope","发送方义务","消费者义务","七条联动闭环","部分失败示例"],
        "references/output-protocols/professional-report-delivery.md":["十四段完整结构","六类报告最低专业内容","数字与账本","反证","执行控制"],
    }
    for relative,anchors in per_file_anchors.items():
        text=(ROOT/relative).read_text()
        absent=[anchor for anchor in anchors if anchor not in text]
        if absent:missing.append(f"semantic_coverage:{relative}:{absent}")
    core=(ROOT/"scripts/sppq_core.py").read_text()
    for route in ("should_cost","total_cost_of_ownership","process_stability","process_capability","sampling","reliability","recovery_choice"):
        if f'"{route}":' not in core:missing.append(f"executable_model_route:{route}")
    if missing:raise SystemExit(f"SPPQ structure missing:{missing}")
    print("SPPQ structure contract passed")
if __name__=="__main__":main()
