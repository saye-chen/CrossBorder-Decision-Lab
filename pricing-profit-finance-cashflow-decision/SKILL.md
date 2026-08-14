---
name: pricing-profit-finance-cashflow-decision
description: 默认用中文执行专家级跨境定价、利润、财务约束与现金流决策。覆盖 Marketplace、DTC、批发、订阅、预售、定制、组合、清仓等模式的新商品定价、目标毛利/贡献、价格走廊、平台与支付费、促销经济、单位/订单/批次利润、保本 ROAS/ACOS/CAC/ROI、汇率税费、现金峰值、回收期及动态参数变化；当用户要求核算售价、利润、毛利、保本线、预算承受力、混合渠道经济、达人样品投资或费率/物流变化影响时使用。不替代品类资本、物流路线、广告投放、平台页面、达人合作、法律税务或外部执行主权。
---

# 定价、利润、财务与现金流决策

运行时版本：`PPFC-2026.07`。
目标合同：`ERDG-CONTRACT-2026.07`、`PPFC-CONTRACT-2026.07`、`PPFC-XDOMAIN-2026.07`、`F02-temporary-localization-contract-v1`；已注册 ERDG 适配器，但不等于完成域或生产就绪。
成熟度：工作包 10；L1 已通过，L2 已通过，L3 Expert 已通过，L4 `controlled pilot`

跨域统一硬门禁：正式报告和财务 handoff 交付前运行 `python3 ../governance/decision-quality/validate_domain_quality.py <report> --handoff`；缺少对象、证据、反证、假设、计算、动作、成功/停止/回滚或用途边界时，禁止输出可执行财务结论。

## 统一交互与执行控制

正式决策、缺失数据、粘贴外部内容或潜在外部动作先读取 [交互治理协议](../governance/interaction/interaction-governance.md) 并执行 Prompt Intake Guard；仅从 ERDG 校验通过的 Decision Packet 编译 Operator Playbook。Connector 只按 [受控连接器治理](../governance/connectors/connector-governance.md) 提供证据，缺失金额不得置零且不得自动调价、付款或形成财务承诺。

## 执行原则

把价格、成本、利润、投放保本线和现金风险放入同一可复算经济系统。先识别商业模式、决策目标、生命周期、价格对象、约束和证据，再选择模型；不得用一个公式覆盖所有商家。

保持以下边界：

- D06/PPFC 最终确认价格架构、价格区间、单位经济、贡献利润、财务边界、现金承受力和通用保本指标；
- CIDM 保留市场进入、资本组合、追加、收缩和退出主权；
- LIFD 保留物流网络、路线、库存、补货和履约动作主权；
- AAMO 保留广告架构、预算、出价、放量和停投主权；
- PLCO、CAPM、MBCM、CIG、CIM、VLB 保留各自业务动作与事实主权；
- ERDG 保留中立合同、单位、经济分层、风险红线和血缘校验；
- 法律、税务、海关与合规结论必须由适格主体确认。

只提交跨域 `proposed` 约束。不得自动修改外部价格、预算、订单、库存、广告或账户。

## 专业性与决策可用性硬约束

读取[专业深度与研究治理](references/professional-depth-governance.md)。任何交付都不得跳过对象、证据与反对证据、经济守恒、现金红线、反事实、动作、成功、停止、回滚、退出和结果回填；L1—L3 不得包装为真实经营效果。

## 入口与交付层级

读取[专业报告交付](references/output-protocols/professional-report-delivery.md)和[数据合同与自动化](references/data-contract-and-automation.md)。按问题风险选择 Decision Card、Memo、Diligence 或专项报告；短报告只压缩展示，不降低后台研究和门禁。

## 跨域边界与双向数据交换

读取[标准跨域集成协议](references/skill-integration-protocol.md)和[字段级跨域合同](references/cross-domain-contract-and-exception-tree.md)。PPFC 只确认共享财务边界，接收域保留具体业务动作主权；任何跨域消息都必须携带对象、版本、用途、禁止用途、状态和血缘。

## 九步工作流

1. 锁定经济对象、范围、业务时点、版本、币种、税口径和数量基准。
2. 识别商业模式、定价目标、生命周期、价格对象、约束环境和证据能力。
3. 对齐收入、成本、退款、数量、库存和现金；失败时停止点估计。
4. 执行法律、安全、授权、现金、单位、版本、动态规则与守恒 Gates。
5. 建立不行动基线和当前价格瀑布，分开利润、现金、库存资产与归因主张。
6. 生成保守、推荐、压力及必要时收缩/退出候选。
7. 对每个候选独立解析动态参数并重算价格、费率、税、贡献、现金和保本线。
8. 比较敏感性、边际结果、翻转点、最大损失、可逆性和证据上限。
9. 输出唯一当前结论、动作边界、成功、停止、回滚、退出和重算触发器。

## 对象与状态

所有运行必须遵守 [对象、生命周期与状态模型](references/object-lifecycle-and-state.md)，并使用：

- [经济对象 Schema](schemas/economic-subject.schema.json)；
- [动态参数与规则 Schema](schemas/dynamic-parameter-rule.schema.json)；
- [参数快照 Schema](schemas/parameter-snapshot.schema.json)；
- [决策状态 Schema](schemas/decision-state.schema.json)。

不得比较未对齐币税、单位、范围、时间或版本的对象。新版本不得覆盖历史对象、参数快照或决策状态。

## 动态参数纪律

稳定的是计算语义和门禁，动态的是数值、规则、范围和有效时间。平台费、支付费、佣金、税率、汇率、采购、陆海空铁、仓储、尾程、退货和风险参数不得硬编码为长期事实。

每个动态规则必须具有值或表达式、计算基数、单位币种、范围、业务有效时间、系统记录时间、来源、证据、版本、优先级、刷新触发和失败状态。

默认采用更具体且已批准的有效规则。两个同等具体规则冲突时返回 `BLOCKED_AMBIGUOUS_RULE`；缺失返回 `MISSING_PARAMETER`；只有过期规则返回 `EXPIRED_PARAMETER`。不得填零、静默沿用旧值、平均冲突值或按载入顺序选择。

## 不可补偿 Gates

任一命中即阻断相关结论：

- 法律、安全、IP、隐私、授权或现金红线未解决；
- 对象、范围、币税、单位、业务时间或版本冲突；
- 收入、退款、数量、库存或现金不守恒；
- 关键成本、费率基数、汇率、税或路线规则缺失/过期/冲突；
- 权威计算不可复算、使用二进制浮点权威值或出现非有限数；
- 平台归因、预测或相关性被当作增量；
- 批次采购、期间 COGS、库存资产和现金流被静默混用；
- 同一订单、收入、成本、退款、样品或渠道主张被重复确认；
- 平均贡献掩盖负边际贡献，或利润为正但峰值资金超限；
- 非主权域要求覆盖结论，或要求自动执行不可逆外部动作。

## 状态与动作上限

主状态：`draft → proposed → validated → accepted → executed → observed → closed`。

旁路状态：`inconclusive`、`blocked`、`rejected`、`expired`、`rolled_back`、`retired`。

- `draft/proposed` 不得直接进入 `executed`；
- `blocked` 必须有新证据和重新评审才能进入 `validated`；
- `expired` 必须刷新参数并重算；
- `validated` 只表示 D06 经济结论通过，不代表业务域已接受或执行；
- 当前工作包已建立 55 场景评测、关键 Golden/极端反例、七域双轨与回滚，并通过隔离的实质证据评审；但尚无完整授权历史回放。PPFC 对外经济约束最高为 `proposed`，接收域仍须对具体业务动作另行接受。

## 场景路由与必读文件

- 对象、版本、生命周期、状态、失败和重算：读取 [object-lifecycle-and-state.md](references/object-lifecycle-and-state.md)。
- 输入分层、证据、数据质量、唯一订单、经济账、库存与现金对账：读取 [input-evidence-and-reconciliation.md](references/input-evidence-and-reconciliation.md)。
- 商业模式、六维路由、18 类模型族和价格走廊：读取 [pricing-model-routing-and-archetypes.md](references/pricing-model-routing-and-archetypes.md)。
- 平台价格控制权、价格对象、费用/优惠栈、结算证伪与未知平台降级：读取[平台定价机制卡](references/platform-pricing-mechanism-cards.md)。
- 价格场景、利润桥、ROAS/ACOS/CAC/ROI：读取 [unit-economics-roas-and-price-recalculation.md](references/unit-economics-roas-and-price-recalculation.md)。
- 动态参数、规则优先级、快照及陆海空铁逐段计费：读取 [dynamic-parameter-and-freight-rules.md](references/dynamic-parameter-and-freight-rules.md)。
- 跨域字段、异常树、局部失败、主权与冲突裁决：读取 [cross-domain-contract-and-exception-tree.md](references/cross-domain-contract-and-exception-tree.md)。
- 国家、平台、币税单位、结算日历、临时覆盖和 F02 迁移：读取 [localization-temporary-contract.md](references/localization-temporary-contract.md)。
- 专业报告类型、强制字段、连续追问、唯一当前结论和选择性重算：读取 [professional-output-and-continuity.md](references/professional-output-and-continuity.md)。
- 混合批次、样品、五触点、库存、归因、成本去重、现金和 55 场景评测：读取 [mixed-batch-evaluation-contract.md](references/mixed-batch-evaluation-contract.md)。
- 旧域经济能力、权威源、消费者、双轨等价、差异分类、退役条件和整包回滚：读取 [migration-compatibility-and-rollback.md](references/migration-compatibility-and-rollback.md)。
- 后续工作包只在获得授权、脱敏且含实际结果的案例后推进 L4 历史回放与生产门；不存在的 reference 不得伪引用。

输入和对账使用：

- [输入信封 Schema](schemas/input-envelope.schema.json)；
- [证据记录 Schema](schemas/evidence-record.schema.json)；
- [经济对账包 Schema](schemas/economic-reconciliation.schema.json)；
- [对账结果 Schema](schemas/reconciliation-result.schema.json)。
- [期间收入与利润差额桥 Schema](schemas/period-delta-bridge.schema.json)。
- [跨域信封 Schema](schemas/cross-domain-envelope.schema.json)；
- [异常报告 Schema](schemas/exception-report.schema.json)。
- [临时本地化合同 Schema](schemas/localization-temporary-contract.schema.json)；
- [本地化迁移 Schema](schemas/localization-migration.schema.json)。
- [专业报告 Schema](schemas/professional-report.schema.json)；
- [连续决策状态 Schema](schemas/continuous-decision-state.schema.json)；
- [决策变更事件 Schema](schemas/decision-change-event.schema.json)。
- [混合批次场景 Schema](schemas/mixed-batch-scenario.schema.json)。

运行 `python3 scripts/reconcile_economic_ledger.py --input <input.json> --output <output.json>` 进行确定性对账。关键身份、币税、单位、唯一性或守恒失败时必须返回非零状态；不得继续生成可执行定价结论。

运行 `python3 scripts/build_period_delta_bridge.py <input.json> --output <output.json>` 在对象、版本、币税、单位、时区和窗口冻结后构建期间收入与经营利润差额桥。该桥由 D06 签发，只允许 D14 引用作跨域财务守恒；不得被解释为因果、资本批准或业务动作批准。

模型计算使用：

- [定价路由 Schema](schemas/pricing-route.schema.json)、[价格场景 Schema](schemas/pricing-scenario.schema.json) 和 [动态物流路线 Schema](schemas/freight-route.schema.json) 约束输入；
- `scripts/route_pricing_model.py`：六维路由、18 类模型族和未知模式降级；
- `scripts/resolve_dynamic_parameters.py`：按范围、双时间、审批和具体性解析唯一规则；
- `scripts/calculate_dynamic_freight.py`：陆海空铁及多式联运逐段计费；
- `scripts/calculate_pricing_economics.py`：每个候选价独立重算收入费率、利润桥和保本指标。
- `scripts/validate_cross_domain_envelope.py`：校验双向交接、字段血缘、部分失败、允许/禁止用途和接收状态；
- `scripts/validate_decision_contract.py`：统一进入 ERDG 权威合同或 PPFC 跨域合同；
- `scripts/validate_localization_contract.py`：校验临时 F02 合同、到期降级、双轨差异、显式接受和可回滚迁移；
- `scripts/validate_professional_report.py`：校验报告完整性、计算血缘和动作边界；
- `scripts/compute_parameter_change_impact.py`：计算参数或事实变化的确定性依赖闭包；
- `scripts/update_continuous_decision.py`：以不可变事件更新连续决策链并保持唯一当前结论；
- `scripts/evaluate_mixed_batch_scenario.py`：复算样品容量、唯一订单、五方主张、成本去重、批次利润、库存 NRV 和现金峰值；
- `scripts/evaluate_business_model_scenario.py`：复算边际扩量、因果动作上限、NRV、B2B、订阅、套装、预售、CAC 与联合压力；
- `scripts/evaluate_consumer_financial_boundaries.py`：消费业务域提交的事实并复算物流成本、伙伴佣金、促销和页面可恢复价值的共享财务边界；
- `scripts/validate_ecae_financial_handoff.py`：构建并校验 D06 消费者侧 F01 回执；只有已接受、未过期、哈希一致的 CE4/CE5 效应与经济参数快照可进入增量经济；
- `scripts/calculate_incremental_economics.py`：由 D06 以 Decimal 复算合格效应的增量价值区间；无合格回执时只允许显式 `noncausal_scenario`，禁止把归因或裸旧字段写成增量；
- `scripts/build_period_delta_bridge.py`：以 Decimal 复算期间净收入和经营利润差额桥，分别验证期内恒等式与跨期差额守恒；
- `scripts/validate_evaluation_execution.py`：逐一执行 55 个登记场景绑定的正向和反例断言，任何缺绑、错绑或执行失败均阻断；
- `scripts/validate_migration_compatibility.py`：校验权威源与消费者清单、同快照等价案例、退役阻断和无外部写回滚；
- `scripts/validate_consumer_adapters.py`：执行七个业务消费者的字段适配门，并对 CIDM、AAMO、CIG、LIFD、CAPM、MBCM、PLCO 运行真实旧脚本与 PPFC 双轨等价；
- `scripts/validate_acceptance_and_release.py`：计算七域技术兼容验收、整包回滚、L3 实质证据评审与发布状态；技术验收不要求人工签名，也不代表业务动作或生产上线获批。
- [迁移兼容账](evaluations/migration-compatibility.json) 登记当前消费者状态、同快照等价输入、退役阻断与整包回滚；`not_migrated` 不得改写成完成状态。
- [消费者适配账](evaluations/consumer-adapters.json) 登记七域源脚本、字段映射、共享输出、保留主权和禁止写回；七域 `dual_run_equivalent` 只证明共享财务字段等价，仍不等于消费者已接受或旧实现可退役。
- [消费者接受包](evaluations/consumer-acceptance.json) 以双轨等价、主权保持、禁止写回和回滚通过计算七域技术兼容验收，不收集或伪造人员签名；[回滚演练](evaluations/rollback-drill.json) 验证旧读取器、重算、失效、业务动作不变与血缘保留；[L3 评审包](evaluations/l3-review-package.json) 记录隔离的实质证据审查、开放问题和 L4 外部门。
- [历史回放模板](evaluations/historical-replay-template.json) 只接收授权、脱敏、含成熟实际结果和独立复核的案例；`scripts/validate_historical_replay.py` 计算 L4 状态，空模板必须保持 `controlled pilot`。
- [55 场景评测目录](evaluations/fixtures/evaluation-catalog.json) 登记 Golden、失败、对抗、性质、跨域和极端案例；[10% 样品 Golden 输入](evaluations/golden/mixed-batch-10pct.input.json) 与 [精确期望结果](evaluations/golden/mixed-batch-10pct.expected.json) 必须可重算一致；
- [55 场景执行映射](evaluations/fixtures/evaluation-execution-map.json) 为每个案例绑定不同的正向与反例测试；当前门禁必须实际执行 110 项绑定断言。
- [L3 全维度审计矩阵](evaluations/l3-audit-matrix.json) 独立覆盖单 Skill、跨 Skill、报告深度、场景广度、复杂场景、连续逼问、极端场景和压力测试；三份可单独审阅的 Golden 报告分别为[单域定价报告](evaluations/golden/single-skill-pricing-report.json)、[跨域复杂批次报告](evaluations/golden/multi-skill-complex-report.json)和[连续压力更新报告](evaluations/golden/continuous-pressure-report.json)。`scripts/validate_l3_audit.py` 必须验证 8 个维度、17 个审计场景和 3 种报告类型，同时保持真实案例校准延后与 L4 `controlled pilot`。
- [PPFC ERDG 适配器](../governance/erdg/adapters/pricing-profit-finance-cashflow-decision/adapter.json)：只注册经济决策类型，`external_write=false`。

## 输出最低合同

即使快速回答也必须保留：

```text
对象、范围、as_of_time、版本和状态
商业模式、目标、生命周期与核算视图
事实、假设、证据、反证、冲突和缺失
Hard gates 与动作上限
不行动、保守、推荐和压力情景
价格瀑布、利润层级、现金与库存口径
动态参数快照、来源、有效时间与未命中项
ROAS/ACOS/ROI/CAC 的注册口径和证据等级
敏感性、翻转点、最大损失和最弱假设
推荐、允许/禁止动作、成功、停止、回滚和退出
跨域 proposed 请求、补证清单和重算触发器
```

不得以“毛利率”“ROI”“ROAS”等模糊名称替代精确定义；不得把公式价格直接称为可发布价格。

## 当前实施门

运行 `python3 scripts/validate_structure_contract.py` 校验工作包 2—10 的入口和合同；运行所有 `scripts/test_*.py` 验证对账、模型、参数、物流、跨域主权、本地化、报告、连续追问、混合批次、55 场景执行、迁移兼容、消费者技术验收、回滚和历史回放门。通过可证明 L1—L3，但不证明具体业务动作已接受或 L4 已完成；重大财务判断和生产放行升级给财务/审计责任人。

短任务使用 `mktemp -d` 创建唯一临时目录，只删除本次命令返回的准确路径并验证目录已不存在；复杂可恢复任务使用 `${TMPDIR:-/tmp}/pricing-profit-finance-cashflow-decision/<task-id>/`，写入 `.task-owner.json` 后再处理。只清理归属标记与任务 ID 同时匹配的目录；清理失败必须报告准确残留路径和原因。
