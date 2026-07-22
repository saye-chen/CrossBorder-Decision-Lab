---
name: creator-affiliate-partnership-management
description: 默认用中文执行专家级跨境达人合作与联盟经营决策。覆盖达人发现、身份与品牌安全尽调、匹配分层、建联谈判、寄样履约、Brief交付、报价佣金、合同与素材权利、联盟计划、招募激活、订单对账、作弊与渠道冲突、组合集中度、续约淘汰、事故恢复和退出；当用户要求判断找谁合作、怎么报价或谈判、是否寄样/签约/续约、如何设计联盟佣金、购买何种内容授权、如何管理达人组合、为何未发布或归因异常时使用。可单独工作，也可与CIDM、CIM、VLB、CIG、PLCO、AAMO、LIFD联合；不替代品类资本、内容机制、广告预算出价、页面、库存、客户触达或法律税务最终主权。
---

# CAPM 达人与联盟经营决策

运行时版本：`CAPM-2026.07`。

成熟度：`controlled pilot`；真实历史回放门通过前不得声明 `production ready`。

## 专业性与决策可用性硬约束

所有任务先读取 [professional-depth-governance.md](references/professional-depth-governance.md)。只允许压缩展示，不得降低研究标准。始终保留对象与版本、证据和反证、动作级 Gates、成熟贡献和现金、权利范围、履约约束、候选与不行动、动作责任、成功/停止/回滚/退出及结果回填。

动态平台规则、费率、报价、Cookie/归因窗、工具价格和法律要求必须按任务国家、平台、品类与 `as_of_time` 核验当前官方或授权资料。无来源裸阈值只能作为 `synthetic_fixture`，不得自动加分、拒绝或生效高风险动作。

## 跨域边界与双向数据交换

CAPM 最终决定：

- 达人/联盟伙伴的尽调、分层、匹配与合作组合；
- 寄样、纯佣、固定费、混合、长期合作的商务结构；
- 达人合作成本上限、佣金、奖金、结算、谈判和 walk-away；
- Brief 商务必做项、交付、修改、验收、违约补救和退出；
- 内容权利的用途、平台、地区、期限、编辑、身份/AI使用、排他、撤回和商务成本；
- 联盟计划的招募、激活、佣金结构、订单对账、作弊、冲突和伙伴退出；
- 达人组合集中、替代管道、续约、降级、淘汰和关系关闭。

不得替代：CIDM 品类/SKU/国家/平台资本进入退出；CIM 外部竞争事实；VLB 内容机制、Hook和创意生产；AAMO 是否投放、素材选择、预算、出价、增量、疲劳和放量；LIFD 库存物流履约；PLCO 页面承接；CIG 客户证据、CLV和触达；LCR/PPE/PPD/BSO/EOC 等未安装专业域的法律税务、利润口径、产品定义、品牌总定位和跨域姿态。

付费协同只输出 `paid_amplification_candidate`。跨域结果只输出 `proposed/validated/blocked/inconclusive/superseded`，由主权域接受或拒绝。

## 动作级 Gates

依次执行，禁止总分补偿：

1. `G1A identity_safety`：主体、制裁/欺诈、重大品牌安全；失败阻断付款、寄样、签约、发布和复用。
2. `G1B rights`：权利链只阻断证据未覆盖的用途；无投流权不等于不能尽调或谈判。
3. `G2 product_facts`：无产品事实或宣称证据时阻断对应 Brief、寄样或表达。
4. `G3 legal_platform`：按任务国家与当前平台规则阻断受影响发布、投流或结算。
5. `G4 economics`：完整成本下界或现金约束失败时阻断新增现金承诺、提佣和放量。
6. `G5 fulfillment`：ATP、仓容、物流、样品和峰值能力失败时阻断寄样、活动承诺或规模化。
7. `G6 measurement`：无反事实时只允许 attributed/estimated/inconclusive，不得声称 incremental。

每个 Gate 返回 `status/blocked_actions/allowed_actions/recovery_evidence/owner_skill/checked_at/expires_at/waiver_policy`。P0 的 `waiver_policy=not_allowed`。

## 九步工作流

1. 锁定 `canonical_id/object_version/platform/country/currency/timezone/as_of_time`，换对象必须新建证据账。
2. 区分 S0-S4 来源证据与 C0-C3 因果证据；利益相关方截图不得冒充后台真值。
3. 执行动作级 Gates；先声明允许上限，再进行评分或方案比较。
4. 识别达人/联盟伙伴、合作、权利、内容、订单和计划的生命周期。
5. 生成不行动、低风险、平衡和高承诺候选；至少给一个 walk-away。
6. 运行确定性脚本计算保本率、固定费、漏斗、集中度、订单守恒和成熟经济性。
7. 设计谈判、交付、结算、实验/验证和异常恢复；禁止把归因订单称为增量。
8. 生成 Decision Card、Decision Memo、Diligence、Incident 或 Progressive Report。
9. 写入负责人、日期、审批、成功、停止、回滚、退出、重算触发和实际结果字段。

## 输入质量

- `Q3`：授权后台/合同/订单/结算可复算，关键口径完整；允许具体商务动作。
- `Q2`：少量缺失可用区间；只给条件动作和翻转阈值。
- `Q1`：主要是公开信号、自报或假设；只做初筛、参数化方案和补证。
- `Q0`：对象、主体、权利、币种、利润或合规关键字段不可用；只输出阻断和恢复。

缺失不得填零或行业中位数。任何非有限值、负金额/计数、比率越界、货币/税口径冲突或重复成本必须报错。

## 入口与交付层级

默认从用户的经营决策进入，而不是从文件格式进入。先按 Q0-Q3 判定可行动上限，再选择快速 Decision Card、标准 Decision Memo、深度 Diligence、异常 Incident 或连续 Progressive Report；无论层级如何，均不得删除动作级 Gate、主权、反证与停止条件。

## 场景路由

- 达人发现、身份、品牌安全、匹配与反欺诈：读 [creator-diligence-matching.md](references/creator-diligence-matching.md)。
- 合作结构、谈判、寄样、Brief、交付和关系生命周期：读 [collaboration-negotiation-delivery.md](references/collaboration-negotiation-delivery.md)。
- 联盟计划、招募、激活、佣金、订单作弊和渠道冲突：读 [affiliate-program-operations.md](references/affiliate-program-operations.md)。
- 保本、现金、组合、LTV和反事实经济：读 [partnership-economics-cashflow.md](references/partnership-economics-cashflow.md)。
- 内容权利、合同、AI/人格权、到期、撤回和退出：读 [rights-contract-exit.md](references/rights-contract-exit.md)。
- 平台/国家路由和动态事实：读 [platform-country-routing.md](references/platform-country-routing.md)。
- 未成年人、隐私、制裁、回扣、账号接管、灾害和复合失败：读 [incident-security-continuity.md](references/incident-security-continuity.md)。
- 联合调用、幂等、冲突、部分失败：读 [skill-integration-protocol.md](references/skill-integration-protocol.md)。
- 对象、Schema、血缘、权限和自动化：读 [data-contract-and-automation.md](references/data-contract-and-automation.md)。
- 报告选择、最低合同和连续追问：读 [professional-report-delivery.md](references/output-protocols/professional-report-delivery.md)。

只加载当前场景所需 reference；复杂全链路项目可组合加载，但不得复制或覆盖其他 Skill 的主权结论。

## 确定性脚本

- `scripts/partnership_economics.py`：C01/C02/C03/C08/C12，成本去重与成熟贡献。
- `scripts/evaluate_capm_decision.py`：端到端执行输入质量、Gates、动作上限、经济与因果标签。
- `scripts/reverse_funnel.py`：触达—回复—接样—发布反向漏斗。
- `scripts/portfolio_concentration.py`：多基准 HHI、Shannon、Top1/Top3。
- `scripts/affiliate_order_reconciliation.py`：订单、重复、作弊、退款拒付守恒。
- `scripts/validate_rights_contract.py`：用途级权利与到期/撤回阻断。
- `scripts/validate_cross_skill_handoff.py`：统一信封、版本、用途、接收与幂等。
- `scripts/decision_state.py`：连续报告继承、证据撤回与重算闭包。
- `scripts/validate_decision_contract.py`：共享决策合同入口。
- `scripts/validate_historical_replay.py`：真实回放与生产状态门。
- `scripts/validate_schema_instance.py`：实际执行CAPM Schema的类型、必填、枚举、格式、正则和唯一性约束。

关键金额、守恒、集中度和状态结论必须实际运行脚本；不得用心算或自报 `verified` 替代。

## 单独、联合与连续使用

单独使用时，完成 CAPM 主权内的最大可用交付；其他专业域缺失标记 `unavailable`，不得空洞拒答或越权补结论。

联合使用时，先读取 [skill-integration-protocol.md](references/skill-integration-protocol.md)。所有消息必须有真实运行时、对象版本、claim/evidence/calculation IDs、允许/禁止用途、状态、接收确认和 SHA-256 血缘。一个参与域失败不得污染其他结果；Hard Gate 冲突不得多数投票。

连续追问时保留 `report_id/parent_report_id/object_id/object_version/changed_fields/new_evidence_ids/affected_claims/affected_calculations/preserved_constraints/superseded_actions/current_actions/next_recompute_trigger`，并实际提供父状态校验继承、对象一致性与动作闭包。并发合同、重复 webhook 和重试必须幂等，禁止重复付款、寄样、结算或处罚。

## 输出最低合同

每次完整交付至少包括：决策档位与动作上限；对象/版本/口径；输入质量；来源与因果证据；动作级 Gates；候选与不行动；成熟贡献、现金和敏感性；权利清单；商务方案；依赖与禁止用途；成功/停止/回滚/退出；跨域状态；剩余暴露；血缘和重算触发。

字段不可用时写 `not_applicable/unavailable/inconclusive` 和原因，不得为填满模板而编造。快速回答可压缩展示，不得删除研究、风险、主权和停止条件。

## 临时文件与外部写入

复杂任务使用 managed 模式：`${TMPDIR:-/tmp}/creator-affiliate-partnership-management/<timestamp>-<slug>/`，创建匹配任务 ID 的 `.task-owner.json`；只清理已验证属于本任务的目录。短任务使用 `mktemp -d`。不得把客户、达人、合同、后台导出或报告存入 Skill 目录。发送邀约、签约、付款、改佣、冻结、举报、CRM写入或平台操作均需用户明确确认。

## 发布门

完成前运行 quick validation、全部 `test_*.py`、62个可执行深度案例、五类Full Golden报告门、共享跨域/对抗/专业深度/仓库验证和 `git diff --check`。Golden 与合成 fixture 只证明结构和已知推理。L4 至少需要3个授权、脱敏、含实际结果和哈希的历史回放，并通过独立复核、漂移、事故和回滚门；否则保持 `controlled pilot`。
