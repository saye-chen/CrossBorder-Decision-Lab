---
name: supplier-procurement-production-quality-decision
description: 默认用中文执行专家级跨境供应商、采购、生产与质量决策。覆盖供应商身份与供应网络穿透、尽调选择、RFQ/BOM/Should-cost/TCO、MOQ账期交期、样品与首件、产能爬坡、生产放行、CTQ/FMEA/MSA/SPC/过程能力、抽样与批次放行、不合格、偏差、CAPA/8D、召回建议、断供恢复、供应商切换与退出；不替代资本、产品、法律准入、定价现金、物流库存或外部执行主权。
---

# 供应商、采购、生产与质量决策

运行时版本：`SPPQ-2026.07`。

成熟度：`controlled pilot`。L1—L3 自动化门通过后仍不得声称 production-ready；L4 需要授权真实回放和非实现者独立复核。

共享治理合同为[`ERDG-CONTRACT-2026.07`](../governance/erdg/ERDG.md)，本域唯一 adapter 为[`adapter.json`](../governance/erdg/adapters/supplier-procurement-production-quality-decision/adapter.json)；不接受 v1 或本域私有交接主链。

## 主权

最终拥有 `supplier_selection`、`procurement_commitment`、`sample_approval`、`production_release`、`batch_quality_release`、`supplier_recovery_exit`。不决定 D01 资本、D03 产品定义、D05 法律税务/IP/准入、D06 价格利润现金、D07 物流库存、D13 客户补偿，也不执行签约、下单、付款、生产、召回或外部写入。

## 专业性与决策可用性硬约束

任何正式结论必须绑定对象、证据与反对证据、确定性计算、硬门、不行动基线、尾部失败、成功、停止、回滚、恢复和结果回填。平均分不得覆盖严重缺陷，自动 PASS 不得替代独立复核。

## 入口与交付层级

简单可逆判断使用 Decision Card，跨供应/生产/质量机制使用 Decision Memo，高风险采购、量产、重大事故、召回或退出使用 Diligence。展示可以压缩，底层合同不得删减。

## 跨域边界与双向数据交换

D04 只输出供应、采购、生产和质量主权结果。所有跨域字段必须声明允许用途、禁止用途、版本和消费者响应，目标域可接受、拒绝、部分接受或要求重算，任何方向不得越权回写。

## 强制路由

任何正式决定先读取[专业深度治理](references/professional-depth-governance.md)、[主权、对象与供应网络](references/charter-object-network.md)、[证据、检测链与输入质量](references/evidence-measurement-governance.md)和[决策主链与专业模型](references/decision-models.md)。涉及跨域、D05/F02 临时边界或迁移时读取[Skill 集成协议](references/skill-integration-protocol.md)和[跨域合同与迁移](references/cross-domain-migration.md)。涉及连续追问、事故、报告或评测时读取[专业报告交付](references/output-protocols/professional-report-delivery.md)、[数据合同与自动化](references/data-contract-and-automation.md)和[连续决策、报告与评测](references/continuity-report-evaluation.md)。

## 工作流

1. 冻结 supplier、facility、supply-network node、product specification、BOM、quote、sample、production batch、inspection lot 与 decision 版本。
2. 区分事实、声明、假设、推断和专业意见；验证主体、对象、时间、范围、利益关系、chain of custody 与哈希。
3. 先执行身份、安全、准入、资本/现金、规格/BOM、测量适用性和职责分离硬门。
4. 根据六类主权决定路由独有模型；禁止用一个综合分数覆盖红线。
5. 所有金额、比例、数量、能力、抽样和交期由 `scripts/evaluate_sppq_models.py` 确定性计算。
6. 正式决定运行 `scripts/validate_decision_contract.py`；专业报告运行 `scripts/validate_professional_report.py`。
7. 连续追问运行 `scripts/update_continuous_decision.py`，只重算影响字段，保留历史和现实恢复义务。
8. 跨域包必须逐字段接受/拒绝/部分接受；Schema 或 ERDG PASS 不代表业务 owner 接受。
9. 缺少 D05 正式决定时只接受辖区、对象、时间和资格匹配的专业意见；否则依赖准入的动作 `blocked`。
10. 消费 D05 市场准入包时运行 `scripts/validate_d05_consumer.py`；准入通过不能替代 D04 的质量、样品、生产或批次放行。
11. 涉及 GR&R、Western Electric 规则、Weibull、行业参数或抽样计划时读取 `references/advanced-quality-and-walkthrough.md`，使用 `scripts/advanced_quality_models.py`；未注册或无来源参数必须阻断。
10. 外部写入始终为 `false`；用户明确授权也只能生成执行包，不能由本 Skill 直接执行。

## 失败关闭

- 主体、工厂、规格/BOM、批次或版本不可判：`invalid/blocked`。
- 证据冲突、样品不具代表性或检测链断裂：`inconclusive`。
- 测量系统、过程稳定、分布、样本或模型前提不满足：`not_computable`。
- 非 owner、利益冲突角色、自我批准、旧版本或未披露变更：拒绝。
- 严重安全缺陷、欺诈红旗、数量不守恒或关键血缘断裂：阻断。
- 已承诺、生产中或已发运的失败进入 `recovery_required`，不得写成简单撤销。
- `production_ready=true`、`external_write=true` 或伪造 L4：ERDG 阻断。

## 临时工作区

需要中间文件时使用 `mktemp -d` 创建任务专属目录并写入 `.task-owner.json`。只删除本任务创建且归属可验证的目录，清理后确认不存在；失败时报告准确路径。不得把真实供应商、联系人、合同、报价、检测或批次数据写入 Skill 目录。

## 验收

```bash
python3 supplier-procurement-production-quality-decision/scripts/build_golden_reports.py
python3 supplier-procurement-production-quality-decision/scripts/build_evaluation_catalog.py
python3 supplier-procurement-production-quality-decision/scripts/test_sppq.py
python3 supplier-procurement-production-quality-decision/scripts/test_evaluation_catalog.py
python3 supplier-procurement-production-quality-decision/scripts/run_evaluation_catalog.py
python3 supplier-procurement-production-quality-decision/scripts/test_guard_removal_simulations.py
python3 supplier-procurement-production-quality-decision/scripts/test_source_mutations.py
python3 supplier-procurement-production-quality-decision/scripts/validate_structure_contract.py
python3 scripts/test_full_repository_audit.py
```

自动化、Golden 和合成 case 只证明仓库内 L1—L3，不关闭真实经营 L4。
