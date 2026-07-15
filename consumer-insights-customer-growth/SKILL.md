---
name: consumer-insights-customer-growth
description: 默认用中文执行跨境电商消费者洞察与客户增长分析。用于经授权的订单、浏览、内容互动、使用、客服、评价、退货、问卷和触达数据的客户身份/事件/授权建模、数据质量与收入守恒、VOC 证据工程、人群×场景×任务×阻力洞察、RFM 与行为分群、客户生命周期、Cohort 留存、贡献利润 CLV、CAC 回收、复购/流失/购买时机、推荐与下一最佳动作、频控和疲劳、A/B 实验、准实验、Uplift、净增量价值、预算/渠道/权益优化、模型回测/漂移/隐私/公平性治理；当用户要求了解客户、计算留存或 CLV、预测复购/流失、评估促销是否产生增量、选择客户动作、优化触达或审计增长模型时使用。不用于仅凭公开市场/竞品数据完成品类准入，不替代视频内容机制拆解，也不自动执行 CRM 或触达动作。
---

# 消费者洞察与客户增长

运行时版本：`CIG-2026.08`。

## 专业性与决策可用性硬约束

无论单 Skill、联合 Skill、快速洞察、正式报告、demo、压测、样本不足、授权受限或极端场景，都只允许压缩展示，不允许降低数据、行为、价值、增量和决策研究标准。每次交付至少保留：分析对象与授权边界、事实/描述/预测/因果/决策层级、证据与假设、反例与替代解释、经济约束、隐私与公平风险、动作或不触达、成功/护栏/停止条件、缺失数据及其决策影响。门槛失败时降低分析层级，不删除决定性模块，也不把预测、相关性或未曝光人群写成增量事实。

本 Skill 对授权客户证据、客户状态和增量有效性拥有主权；不拥有外部竞争、视频机制或品类投资主权。联合调用时只交换去识别、带版本、对象、证据/实验 ID、允许/禁止用途、区间/置信度和验证状态的结果卡。任何投资评分、门槛或档位调整必须由 CIDM 接受并重算；其他 Skill 缺席或失败不降低本域报告专业性，只改变可下结论的强度。

## 目标与边界

把经授权的客户证据转化为可证伪洞察、动态客户状态、带不确定性的价值/风险估计和可审计的增量动作。所有输出必须标记为事实、描述、预测、因果或决策层；预测准确不能证明动作有效。

- 负责：身份/事件/授权、客户证据、分群与生命周期、CLV、复购/流失、实验、Uplift、下一最佳动作和治理。
- 不负责：品类准入、外部竞品监控、视频逐镜头拆解、客服工单执行、广告/CRM 操作或自动发送消息/优惠券。
- 不将账号、邮箱、设备或地址无条件视为同一人；不使用未授权数据触达；不用敏感属性进行不透明排斥、差别定价或不公平权益。

## 工作区与数据安全

将用户数据视为只读源。复杂任务使用 `${TMPDIR:-/tmp}/consumer-insights-customer-growth/<YYYYMMDD-HHMMSS>-<task-slug>/`，写入 `.task-owner.json`；仅删除本任务目录。最小化读取字段，对直接标识符做哈希/代理化；最终输出不暴露不必要的个人数据。删除、触达、权益发放和外部系统写入均需要用户明确授权。

## 任务路由

| 模式 | 必读 | 默认交付 |
|---|---|---|
| 消费者洞察 | [voc-evidence-engineering.md](references/voc-evidence-engineering.md)、[multilingual-research-and-voc-governance.md](references/multilingual-research-and-voc-governance.md)、[consumer-insight-protocol.md](references/consumer-insight-protocol.md) | Consumer Insight Card |
| 数据建模/审计 | [identity-event-consent-model.md](references/identity-event-consent-model.md)、[identity-purpose-and-deletion-governance.md](references/identity-purpose-and-deletion-governance.md)、[data-quality-and-revenue-reconciliation.md](references/data-quality-and-revenue-reconciliation.md) | 数据门槛与异常清单 |
| 分群/生命周期 | [segmentation-and-lifecycle.md](references/segmentation-and-lifecycle.md)、[cohort-retention.md](references/cohort-retention.md)、[customer-journey-value-and-sequential-effects.md](references/customer-journey-value-and-sequential-effects.md) | 动态状态、迁移、旅程与动作边界 |
| CLV/CAC | [clv-and-payback.md](references/clv-and-payback.md)、[customer-journey-value-and-sequential-effects.md](references/customer-journey-value-and-sequential-effects.md) | 贡献利润价值分解、CLV 区间和回收期 |
| 复购/流失/时机 | [repurchase-churn-and-timing.md](references/repurchase-churn-and-timing.md) | 风险、时间窗和可行动性 |
| 推荐/下一动作 | [recommendation-and-next-best-action.md](references/recommendation-and-next-best-action.md)、[policy-uncertainty-and-strategy-governance.md](references/policy-uncertainty-and-strategy-governance.md)、[privacy-fairness-and-contact-policy.md](references/privacy-fairness-and-contact-policy.md) | 风险调整动作、不触达、资格/频控与净价值 |
| 增长实验 | [experimentation-and-causal-inference.md](references/experimentation-and-causal-inference.md)、[customer-journey-value-and-sequential-effects.md](references/customer-journey-value-and-sequential-effects.md) | 单次/连续效应区间、护栏与 Go/Iterate/Stop |
| Uplift/资源配置 | [uplift-and-incremental-value.md](references/uplift-and-incremental-value.md)、[budget-channel-and-benefit-optimization.md](references/budget-channel-and-benefit-optimization.md)、[policy-uncertainty-and-strategy-governance.md](references/policy-uncertainty-and-strategy-governance.md) | 风险调整净增量价值排序和未入选原因 |
| 模型治理 | [model-monitoring-and-governance.md](references/model-monitoring-and-governance.md)、[policy-uncertainty-and-strategy-governance.md](references/policy-uncertainty-and-strategy-governance.md) | 模型与策略继续、重训、降级、回滚或停用 |

所有任务都读 [professional-depth-governance.md](references/professional-depth-governance.md)、[analysis-contract-and-evidence-ledger.md](references/analysis-contract-and-evidence-ledger.md)、[privacy-fairness-and-contact-policy.md](references/privacy-fairness-and-contact-policy.md) 和 [output-protocols.md](references/output-protocols.md)。专业深度协议保证简报、卡片和快速分析只压缩展示，不降低数据、行为、价值、增量和决策研究深度。需要与 CIDM、CIM 或 VLB 对接时读 [skill-integration-protocol.md](references/skill-integration-protocol.md)。
涉及结构化数据、外部执行、周期任务、删除传播或自动化流水线时必须读 [data-contract-and-automation.md](references/data-contract-and-automation.md)。

## 核心流程

1. **定义决策和截点**：明确人群、市场、商品、行为/结果、预测或实验窗口，锁定业务时间截点。
2. **检查授权与身份**：分开身份图谱与授权用途矩阵，先过退订、撤回、删除和保留期；确定账号/个人/家庭分析粒度、匹配置信度和可逆关系。
3. **验证事件与财务口径**：去重、业务时间/入库时间、迟到数据、订单/支付/退款守恒和币种口径。
4. **选择分析层级**：事实 → 描述 → 预测 → 因果 → 决策；不越级表达。
5. **构建可比样本**：披露来源、分子/分母、时间窗、选择偏差、右删失、缺失和实验暴露。
6. **分析与校准**：使用与数据成熟度匹配的规则/统计模型；处理跨语言/来源偏差、旅程状态、价值分解和连续动作；输出区间、校准、时间外回测和反例。
7. **计算净增量价值**：只有可信实验/准实验数据才估计 Uplift；扣除权益、渠道、疲劳、服务和风险成本。
8. **应用资格与护栏**：按增量效应下界或保守分位数决策；授权、退订、频控、投诉、库存、市场、预算、公平性和人工审批优先于模型分数。
9. **输出与回收**：给出动作或“不触达”、理由、成本上限、成功/护栏/停止条件；回写真实暴露、成本和长期结果。

## 必要输出

1. 决策问题、对象、市场/渠道/商品、业务截点、观察/预测/实验窗口和允许使用的数据目的。
2. 身份粒度、匹配置信度、授权/退订/删除状态、最小字段和不可使用数据。
3. 数据来源、样本分子分母、缺失、迟到、右删失、币种、收入守恒和质量降级项。
4. 事实、描述、预测、因果和决策层级，以及 Evidence / Assumption / Model / Decision Ledger 回指。
5. 洞察、状态、CLV、风险或增量效应的区间、校准、反例、最弱假设和适用边界。
6. 动作或“不触达”、未入选原因、成本/预算/容量上限、资格、频控、公平性和人工审批点。
7. 主要、机制、护栏和长期指标，成功/停止条件、真实曝光、成本和结果回收要求。

## 脚本路由

- `validate_customer_events.py`：检查事件必填字段、时间、授权和订单/退款异常。
- `build_rfm_segments.py`：从已去重交易数据构建可解释 RFM 与规则型生命周期。
- `analyze_cohort_retention.py`：计算首购 Cohort 的可比留存/复购矩阵。
- `calculate_clv.py`：用贡献利润和情景参数计算历史/情景 CLV 与回收期。
- `evaluate_growth_experiment.py`：计算两组增量效应、区间、经济价值和护栏。
- `rank_next_best_actions.py`：对用户已给定的 Uplift、贡献利润、成本和资格排序，不自行预测 Uplift。
- `build_growth_report.py`：将结构化结果生成可复核的增长建议卡。
- `reconcile_customer_revenue.py`：核对有效支付、折扣、退款、税费和贡献利润账本。
- `audit_voc_labels.py`：按语言/市场审计双标一致性、Kappa 和低置信覆盖。
- `analyze_lifecycle_transitions.py`：计算客户状态迁移次数和概率。
- `evaluate_uplift_ranking.py`：在可靠随机分配和真实曝光数据上评估 Uplift 排序。
- `evaluate_growth_governance.py`：汇总概率误差、预测漂移和群体选择/结果差异，供治理复核。

脚本只处理用户提供或经授权读取的数据，不自动匹配真实身份、不自动训练高风险模型、不编造 Uplift、不写外部系统。现有实验脚本是二元两组基础 ITT 计算器；集群、连续指标、CUPED、多重比较、准实验和长期效应必须按实验协议另行分析。

## 质量门槛

- 比例同时报告分子、分母、来源、窗口和区间；无可识别抽样概率时只称“样本内”。
- 分群必须有进入/退出条件、刷新周期、稳定性和动作差异；不生成永久人格标签。
- CLV 使用贡献利润，处理退款、权益、服务、CAC、时间和不确定性；销售额不是 CLV。
- CLV 必须区分 CAC 前客户价值与 CAC 后净 CLV；LTV/CAC 的分子不重复扣除 CAC。
- 流失/复购定义必须有时间窗，处理右删失和概率校准；高风险不等于可挽回。
- 实验事先定义实验单位、主要/护栏指标、最小可检测效应、窗口和停止规则；不只看 p 值。
- 客户级 Uplift 只能表述为条件处理效应排序或区间，不冒充不可观测的个人真实因果效应；没有可信增量证据时只输出待实验候选动作。
- 触达前通过授权、退订、频控、敏感事件、投诉、库存、预算和市场规则；“不触达”是正式动作。
- 不同运行时版本的分群、CLV、风险或 Uplift 结果不直接比较，除非用同口径重算。
- 跨语言主题必须保留原文、词典版本和语义/场景/经营含义对齐；不可识别抽样概率时不外推总体发生率。
- 连续动作、跨渠道或家庭/店铺干扰不得用单次独立处理假设解释；必须调整实验单位或降级因果结论。
- 策略与模型分别治理；模型指标稳定不能证明频控、权益和下一动作策略仍产生长期净增量价值。
- 授权、身份、事件、收入、实验分配或真实曝光的关键门槛失败时，必须降级分析层级，不让模型吸收数据异常。
