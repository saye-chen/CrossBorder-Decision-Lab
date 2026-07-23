---
name: marketing-brand-campaign-management
description: 默认用中文执行专家级跨境市场营销、品牌与活动经营决策。覆盖市场级人群细分、定位、品牌架构、GTM与再上市、Offer机制、营销日历、广告/达人/内容/CRM/PR渠道编排、获批资源包内方向配置、品牌健康、活动成熟增量、跨国家平台迁移、营销事故与品牌恢复、收缩清仓和退出；当用户要求制定或评估上市营销、品牌定位、促销活动、渠道组合、营销预算方向，判断活动是否真正增量，或处理营销危机时使用。可单独工作并与CIDM、CIM、LIFD、PLCO、AAMO、CAPM、VLB、CIG联动；不替代资本投资、产品、合规、最终定价现金、补货、页面、广告内部执行、达人商务、内容制作、客户级触达或跨域总诊断主权。
---

# MBCM 市场营销、品牌与活动经营

运行时版本：`MBCM-2026.01`。

成熟度：`controlled pilot`；授权真实历史回放门通过前不得声明`production ready`。

## 专业性与决策可用性硬约束

所有任务先读取[professional-depth-governance.md](references/professional-depth-governance.md)。只允许压缩展示，不得降低研究标准。始终固定对象、国家/平台、生命周期、版本和`as_of_time`；分离事实、计算、估计、推断、决策与未知；分离观察、归因、增量和成熟增量；先执行G0—G8，再比较方案。

动态平台规则、国家法律、促销资格、价格展示、节日窗口、渠道能力和数据可见性必须在任务执行时核验当前官方或授权证据。无法刷新时降级，不得编造精确阈值。

## 跨域边界与双向数据交换

MBCM最终决定：

- 市场级人群选择、定位、价值主张和品牌架构；
- 已获批准经营对象的GTM、再上市和阶段性营销姿态；
- Offer机制、营销活动组合、日历和跨渠道角色编排；
- D06批准资源包内的跨目标、跨活动、跨渠道方向配置；
- 品牌资产验证路径、活动成熟增量复盘；
- 单域营销事故的传播隔离、品牌恢复、收缩与退出传播。

不得替代：

- CIDM的品类/SKU/国家/平台资本进入、加码、收缩和退出；
- 产品域的产品定义，D05/专业人员的法律合规，D06的价格、利润、现金和总预算；
- LIFD的补货、库存与履约，PLCO的页面优化，AAMO的广告内部预算/出价/投放；
- CAPM的达人筛选、报价、合同、佣金和权利，VLB的脚本/素材，CIG的个人客户资格、触达、补偿和不触达；
- D14的跨域经营总诊断。

跨域只输出`proposed/validated/blocked/inconclusive/stale/withdrawn/superseded`，保留来源结论、运行时、证据、允许/禁止用途。读取[skill-integration-protocol.md](references/skill-integration-protocol.md)。

## 十层工作流

1. 建立决策合同：对象、Q01—Q13、主意图、市场、生命周期、版本、目标、责任和可逆性。
2. 判定最小可分析/可决策输入、DQ0—DQ3、授权、时间和口径。
3. 执行G0数据授权、G1法律准入、G2承诺、G3经济、G4容量、G5执行、G6测量、G7客户品牌、G8生命周期。
4. 按十层根因检查测量、版本、市场、人群、产品承诺、Offer经济、渠道、承接、内部执行和外部事件。
5. 生成不行动、修复、测试、重配、放量、收缩、暂停、停止或升级候选。
6. 实际运行适用确定性脚本；金额、守恒、边际、容量和状态不得心算。
7. 先淘汰Gate失败方案，再比较增量经济、品牌/客户影响、风险、可逆性、学习价值和机会成本。
8. 将DQ/C证据等级映射为动作上限；`proceed`不等于`scale`。
9. 输出动作对象、幅度、依赖、责任、成功、护栏、暂停、停止、回滚和重决策。
10. 保存决策版本、监控成熟结果，变化时只重跑受影响闭包。

## 场景路由

- 对象、生命周期、状态和Q01—Q13：读[object-lifecycle-and-state-model.md](references/object-lifecycle-and-state-model.md)与[scenario-tree-and-decision-types.md](references/scenario-tree-and-decision-types.md)。
- 输入、DQ、证据和动态刷新：读[input-data-quality-and-evidence.md](references/input-data-quality-and-evidence.md)。
- Gates、候选和冲突：读[decision-gates-and-conflict-resolution.md](references/decision-gates-and-conflict-resolution.md)。
- 细分、定位、品牌架构：读[segmentation-positioning-and-brand.md](references/segmentation-positioning-and-brand.md)。
- GTM与上市准备：读[gtm-readiness-and-launch.md](references/gtm-readiness-and-launch.md)。
- Offer、活动与日历：读[offer-campaign-and-calendar.md](references/offer-campaign-and-calendar.md)。
- 渠道和资源方向：读[channel-orchestration-and-resource-direction.md](references/channel-orchestration-and-resource-direction.md)。
- 品牌健康、增量与学习：读[brand-health-incrementality-and-learning.md](references/brand-health-incrementality-and-learning.md)。
- 实验设计、MDE、DiD、合成控制、ITT/CACE与不确定性：读[measurement-design-and-causal-estimation.md](references/measurement-design-and-causal-estimation.md)。
- Offer弹性、疲劳、adstock、饱和、交互与pacing：读[offer-demand-and-channel-response.md](references/offer-demand-and-channel-response.md)。
- 品牌价值桥、溢价、聚合CLV/CAC与回收：读[brand-customer-economics.md](references/brand-customer-economics.md)。
- 季节、竞争干扰、事故损失与恢复曲线：读[seasonality-competition-and-incident-quantification.md](references/seasonality-competition-and-incident-quantification.md)。
- 事故、恢复、收缩和退出：读[incident-recovery-reduction-and-exit.md](references/incident-recovery-reduction-and-exit.md)。
- 国家、平台、品类、模式和未知路由：读[localization-transfer-and-unknown-routing.md](references/localization-transfer-and-unknown-routing.md)及对应子卡。
- 平台路由：[平台原型](references/platforms/archetypes.md)、[未知平台](references/platforms/unknown-platform-routing.md)。
- 操作级平台卡：[Amazon](references/platforms/amazon-marketing-operations.md)、[TikTok Shop](references/platforms/tiktok-shop-marketing-operations.md)、[Shopee](references/platforms/shopee-marketing-operations.md)。
- 国家、品类与经营模式校准：[国家合同](references/countries/country-calibration-contract.md)、[品类原型](references/categories/category-archetypes.md)、[模式控制卡](references/operating-modes/operating-mode-control-cards.md)。

需要模块级深挖时，分别读取：[S01](references/modules/s01-segmentation.md)、[S02](references/modules/s02-positioning.md)、[S03](references/modules/s03-brand-architecture.md)、[S04](references/modules/s04-gtm.md)、[S05](references/modules/s05-offer.md)、[S06](references/modules/s06-campaign-calendar.md)、[S07](references/modules/s07-channel.md)、[S08](references/modules/s08-resource.md)、[S09](references/modules/s09-brand-health.md)、[S10](references/modules/s10-incrementality.md)、[S11](references/modules/s11-localization.md)、[S12](references/modules/s12-incident.md)、[S13](references/modules/s13-exit.md)。
- 对象、血缘、权限与外部写入：读[data-contract-and-automation.md](references/data-contract-and-automation.md)。
- 报告类型和最低合同：读[professional-report-delivery.md](references/output-protocols/professional-report-delivery.md)。

只加载当前任务所需reference。复杂全链路可组合加载，但不得覆盖相邻域主权。

## 确定性工具

估计类工具必须先报告识别假设、诊断和区间，再进入决策；弱拟合不得因输出数字而升级证据。

- `campaign_economics.py`：成熟活动贡献和情景。
- `offer_economics.py`：Offer全成本、非增量核销和保本增量率。
- `incrementality_bridge.py`：观察/归因/增量/成熟增量经济桥。
- `experiment_design.py`：MDE、power、聚类设计效应、集群数与周期。
- `causal_effects.py`：DiD、平行趋势、ITT/CACE与合成控制。
- `uncertainty_engine.py`：固定seed Bootstrap与蒙特卡洛区间传播。
- `offer_response_optimization.py`：价格弹性、疲劳修正和非线性折扣优化。
- `channel_response.py`：adstock、Hill饱和、渠道交互和pacing。
- `channel_curve_estimation.py`：从聚合历史网格估计adstock/Hill响应参数。
- `aggregate_customer_economics.py`：聚合cohort CLV、CAC和回收期。
- `brand_value_bridge.py`：品牌代理到经营结果、衰减和匹配溢价。
- `seasonality_competition.py`：季节指数、节后透支、竞争压力和SOV姿态。
- `incident_recovery_quantification.py`：受控损失、恢复半衰期和修复增量NPV。
- `pull_forward_cannibalization.py`：提前购买、SKU蚕食与渠道抢单。
- `resource_portfolio.py`：资源约束、边际阶梯和集中度。
- `brand_investment_scenarios.py`：品牌投资可证伪情景。
- `capacity_stress.py`：需求组成、峰值容量和活动上限。
- `risk_and_sensitivity.py`：最大损失、敏感性和翻转点。
- `clearance_exit_economics.py`：继续/修复/清仓/退出净回收。
- `validate_units_currency_time.py`：单位、币种、币税、时区和成熟窗守恒。
- `evaluate_marketing_decision.py`：端到端DQ、Gates、动作上限和主权。
- `decision_state.py`：连续追问、版本撤回和重算闭包。
- `validate_handoff_packet.py`、`validate_decision_contract.py`、`validate_evidence_claims.py`：合同入口。
- `validate_incident.py`：事故对象、版本、分级、止血与责任校验。
- `validate_historical_replay.py`：L4外部证据门。

## 单独、联合与连续使用

单独使用时完成MBCM主权内的最大闭环；参与域缺失标记`unavailable`并提出精确请求，不空洞拒答、不伪造结论。

联合使用时验证`packet_id/source_domain/source_runtime/object/version/status/evidence/calculations/allowed_uses/forbidden_uses`。参与域失败只污染受影响主张；共同红线例外。不得多数投票。

连续追问时保留`decision_id/parent_decision_id/object_version/changed_fields/new_evidence_ids/affected_claims/affected_calculations/preserved_constraints/superseded_actions/current_actions/next_recompute_trigger`。每轮说明变化、影响和未变项。

## 入口与交付层级

按风险选择快速Decision Card、专业Memo、完整Diligence或机器handoff包。每次交付至少保留：结论与动作上限；对象/版本/口径；DQ与证据；Gates；候选与不行动；适用计算；参与域状态；成功/护栏/暂停/停止/回滚/退出；允许/禁止用途；血缘和重算触发。

字段不可用时写`unknown/not_applicable/unavailable/inconclusive`及原因，不得填0或行业均值。

## 外部动作

本Skill只形成决策和具名请求。发布活动、改价、投放、签达人、改页面、发CRM、补货、公开危机响应或删除内容均需用户明确授权和相应主权域/责任人确认。

## 临时文件与清理

复杂任务使用`${TMPDIR:-/tmp}/marketing-brand-campaign-management/<timestamp>-<slug>/`并创建匹配任务ID的`.task-owner.json`；短任务使用`mktemp -d`。只清理已验证属于当前任务的临时目录，并确认目录已不存在；清理失败必须报告。客户、财务、平台导出和真实报告不得写入Skill目录。

## 发布门

完成前运行skill quick validation、全部`test_*.py`、120个差异场景及coverage manifest、10类Golden、数学Oracle/性质/变异、多轮连续性、单Skill、真实八Skill包、主权、事故、对抗和全仓回归。自动化通过只称L3 automated gate；L4至少需要3个授权、脱敏、成熟且含实际结果/哈希的异质历史回放，覆盖失败或退出并独立复核，否则保持`controlled pilot`。
