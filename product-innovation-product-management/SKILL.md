---
name: product-innovation-product-management
description: 默认用中文执行跨境电商产品创新与产品管理决策。用于把市场机会、VOC、用户任务、竞品事实和经营约束转化为可验证的产品机会、产品定义、MVP、规格、变体、包装、验证与路线图；当用户要求定义新品、取舍功能规格、设计MVP、管理产品版本、判断产品Claim、处理规格漂移、产品迭代、收缩或停产时使用。不替代资本投资、定价利润、供应商采购、量产质量、法律准入、库存履约、页面内容或外部执行主权。
---

# 产品创新与产品管理

运行时版本：`PIPM-2026.01`。

成熟度：`controlled pilot`。WP2—WP10 的专家级L1—L3仓库门与专业深度复审已通过，包括真实执行评测、十个业务消费者和ERDG的本域适配、Golden业务链、404项正反断言、双轨差异、回滚演练和防篡改评审包；独立Owner权威切换仍保持关闭，L4仍需要授权真实回放。

## 任务边界

最终决定产品机会如何转为产品任务，以及产品定义、MVP、需求、规格、变体、包装、验证范围、路线图、迭代与停产建议。不得决定市场资本进入、最终价格利润、供应商和量产放行、法律准入、库存数量、页面动作、广告动作或外部执行。

## 专业性与决策可用性硬约束

任何建议必须绑定对象版本、证据与反对证据、可复算机制、非补偿门、反事实、成功、停止、回滚、退出和结果回填。平均分不得覆盖关键尾部失败，自动PASS不得替代独立评审。

## 入口与交付层级

简单可逆判断使用Decision Card，跨机制产品决定使用Decision Memo，高风险、多国家、不可逆或退出判断使用Diligence。九类专业报告保持独立专属字段。

## 跨域边界与双向数据交换

D03只输出产品主权内的事实和建议；其他域通过版本化输入/输出卡接受、拒绝、部分接受或请求重算。任何方向的数据交换都不得越权回写对方主权。

标准治理入口为[专业深度治理](references/professional-depth-governance.md)、[Skill集成协议](references/skill-integration-protocol.md)、[数据合同与自动化](references/data-contract-and-automation.md)和[专业报告交付](references/output-protocols/professional-report-delivery.md)。完整主权与禁止越权规则见[能力章程与主权](references/charter-and-sovereignty.md)。规范对象、版本和 PLC0—PLC8 状态见[规范对象与生命周期](references/canonical-object-and-lifecycle.md)。输入分级、缺失语义、正交证据与决策闭环见[输入、证据与决策骨架](references/input-evidence-and-decision-skeleton.md)。产品机会、MVP、规格、变体、包装、路线图和追踪模型见[专业模型与确定性计算](references/professional-models-and-calculation.md)。涉及成本、利润、价格或现金约束时读取[D06 重算与跨域合同](references/d06-recomputation-and-cross-domain.md)。涉及制造/质量请求、市场准入问题、外部专业意见或国家平台适配时读取[D04、D05与本地化专家合同](references/d04-d05-localization-professional-contracts.md)。生成报告、处理连续追问、事故或回滚时读取[专业输出、连续决策与回滚](references/professional-output-continuity-and-rollback.md)。迁移或消费D03产品事实时读取[消费者迁移、接受与回滚](references/consumer-migration-and-acceptance.md)。

## WP2 工作流

1. 识别 enterprise、brand、product family、product、market product 与 SKU/variant。
2. 冻结对象版本、国家、平台、业务有效时间与系统记录时间。
3. 判断当前 `product_lifecycle_stage`，不得与 L1—L4 成熟度混用。
4. 只在 D03 主权内形成 `proposed/validated/rejected/blocked/inconclusive`。
5. 将跨域请求保持 `proposed`，交对应主权域确认。
6. 所有共享决定先运行 `scripts/validate_decision_contract.py`，执行 `ERDG-CONTRACT-2026.01`。
7. 规范对象与生命周期实例运行 `scripts/validate_wp2_contracts.py`。
8. WP3 决策包运行 `scripts/validate_wp3_package.py`；F01建成前因果Claim必须阻断。
9. WP4 使用 `scripts/evaluate_product_models.py` 路由八类模型；所有数值使用十进制字符串。
10. D03—D06 字段变化先运行 `scripts/compute_product_change_impact.py`，再由 `scripts/validate_cross_domain_envelope.py` 校验逐 Claim 回执、幂等与版本边界。
11. D04/D05 临时交接、本地化、专业意见和正式迁移包统一运行 `scripts/validate_wp6_contracts.py`；双轨差异使用 `scripts/evaluate_temporary_contract_migration.py`。
12. 连续追问使用 `scripts/update_continuous_product_decision.py`，影响传播使用 `scripts/compute_decision_impact_closure.py`，九类输出统一运行 `scripts/validate_professional_report.py`。
13. 专业评测运行 `scripts/run_wp8_evaluations.py` 和 `scripts/validate_wp8_coverage.py`；任何 mutation 未失败、覆盖缩减或 L4 提前升级均阻断。
14. 消费者迁移运行 `scripts/validate_pipm_consumer_migration.py`；自动合同接受不得冒充独立Owner接受，旧读路径在独立Owner签署和权威切换前保持有效。
15. 独立评审包运行 `scripts/validate_wp10_review_package.py`；自动测试、自评或部分签署不得冒充最终L3签署，L4不得由合成案例关闭。

ERDG 适配器位于 `governance/erdg/adapters/product-innovation-product-management/adapter.json`，只校验结构、红线、状态和血缘，`external_write=false`。

## 失败关闭

- 对象、版本、国家平台或时间不可判：`blocked`。
- 产品阶段使用 `L0—L8` 而非 `PLC0—PLC8`：拒绝。
- 非 D03 主权决定被标记 validated：拒绝。
- evidence、Claim、calculation 或成熟度被混为单轴等级：拒绝。
- `production_ready=true` 或请求外部写入：ERDG 阻断。
- 缺少 D04/D05/D06 等主权结论时，仅保留 D03 自有事实，受影响动作降级。

## 临时空间

需要临时文件时使用 `mktemp -d` 创建任务专属目录，并写入 `.task-owner.json` 标记任务边界。只删除本任务创建且所有权可验证的临时目录；清理后验证目录不存在，清理失败则报告路径，不扩大删除范围。不得使用仓库根目录、用户目录或 `${TMPDIR:-/tmp}` 作为递归删除目标。

## 当前验收

运行：

```bash
python3 product-innovation-product-management/scripts/test_wp2_contracts.py
python3 product-innovation-product-management/scripts/validate_wp2_structure.py
python3 product-innovation-product-management/scripts/test_wp3_package.py
python3 product-innovation-product-management/scripts/validate_wp3_package.py <package.json>
python3 product-innovation-product-management/scripts/test_product_models.py
python3 product-innovation-product-management/scripts/evaluate_product_models.py <model-input.json>
python3 product-innovation-product-management/scripts/test_wp5_cross_domain.py
python3 product-innovation-product-management/scripts/compute_product_change_impact.py <impact-input.json>
python3 product-innovation-product-management/scripts/validate_cross_domain_envelope.py <message.json>
python3 product-innovation-product-management/scripts/test_wp6_expert_contracts.py
python3 product-innovation-product-management/scripts/validate_wp6_contracts.py <wp6-package.json>
python3 product-innovation-product-management/scripts/evaluate_temporary_contract_migration.py <migration-run.json>
python3 product-innovation-product-management/scripts/test_wp7_continuity_and_reports.py
python3 product-innovation-product-management/scripts/update_continuous_product_decision.py <state-event.json>
python3 product-innovation-product-management/scripts/compute_decision_impact_closure.py <dependency-graph.json>
python3 product-innovation-product-management/scripts/validate_professional_report.py <report.json>
python3 product-innovation-product-management/scripts/test_wp8_evaluations.py
python3 product-innovation-product-management/scripts/run_wp8_evaluations.py
python3 product-innovation-product-management/scripts/validate_wp8_coverage.py
python3 product-innovation-product-management/scripts/test_wp9_migration.py
python3 product-innovation-product-management/scripts/validate_pipm_consumer_migration.py
```

L1—L3专家级仓库门通过不代表独立Owner权威切换、正式D04/D05专业意见或L4 Production已完成。
