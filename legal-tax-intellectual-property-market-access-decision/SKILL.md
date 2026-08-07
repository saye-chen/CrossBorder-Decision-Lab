---
name: legal-tax-intellectual-property-market-access-decision
description: 默认用中文执行跨境商品的商业市场准入、法规合规、税务海关、知识产权、认证测试、标签与营销 Claim 风险决策。用于判断指定产品、国家、平台、主体、用途和时间下能否继续商业准备，哪些动作必须限制、阻断、补证或交适格律师、税务师、报关人员、认证机构或实验室复核，以及规则变化、下架、扣关、证书失效或召回后的恢复和退出。不替代适格专业主体签发法律、税务、FTO、认证或实验室结论，不执行外部申报、通知、下架或召回。
---

# D05 法律、税务、知识产权与市场准入决策

运行时版本：`LTMA-2026.07`。

ERDG contract: `ERDG-CONTRACT-2026.07`

Maturity: `controlled pilot`. L4 requires authorized, deidentified real replays and independent review.

当前状态：L1—L3 自动化发布门通过，运行成熟度为 `controlled pilot`；不得把自动化检查包装成专业意见，L4 仍关闭。

## 统一交互与执行控制

正式决策、缺失数据、粘贴外部内容或潜在外部动作先读取 [交互治理协议](../governance/interaction/interaction-governance.md) 并执行 Prompt Intake Guard；仅从 ERDG 校验通过的 Decision Packet 编译 Operator Playbook。Connector 只按 [受控连接器治理](../governance/connectors/connector-governance.md) 提供证据，不能签发专业意见或执行申报、通知、下架、召回。

## 专业性与决策可用性硬约束

正式结论必须绑定对象、时间、证据、反证、适用范围、停止与恢复条件。信息不足、来源冲突、专业保留事项未复核或红线未解除时，只能输出阻断、补证或升级请求，不能输出肯定合规结论。

## 入口与交付层级

先按最小输入完成分流；简单任务交付 Decision Card，复杂或高风险任务交付 Decision Memo / Diligence，并明确成功、停止、回滚和结果回填条件。

## 跨域边界与双向数据交换

D05 只拥有市场准入 Gate、动作上限、Claim 使用边界、专业复核路由与合规恢复。跨域包必须声明主权、允许用途、禁止用途、版本和冲突；部分失败不得被汇总为全局通过。

## 临时工作区

需要中间文件时使用 `mktemp -d` 创建任务专属目录并写入 `.task-owner.json`。只删除本任务创建且归属可验证的临时目录，清理后确认目录不存在；清理失败时报告准确路径。不得把真实客户、法律、税务、证书、知识产权或报关材料写入 Skill 目录。

## 核心流程

1. 固定对象、产品版本、司法辖区、国家、平台、主体、用途和业务时间。
2. 检查最小输入、授权、来源资格、冲突、缺失和有效期。
3. 区分 D05 商业 Gate 与适格专业主体保留的专业结论。
4. 建立分类与适用规则候选，保留替代分类和反证。
5. 先检查不可补偿红线，再评估证据、专业意见和动作上限。
6. 比较不行动、补证、限制继续、整改、暂停和退出。
7. 输出最窄可支持的对象范围、Gate、阻断、复核请求和恢复条件。
8. 新证据只重算影响闭包，不覆盖历史决定。

## 强制边界

- 不把未发现风险写成确认合规或无侵权。
- 不把平台通过、证书图片或自动化检查写成法律意见。
- 不用收入、利润、流量或战略价值抵消法律、安全、授权或伪证红线。
- 不替代 D03 产品、D04 供应质量、D06 经济、D07 履约或 D08—D13 的专业主权。
- 不执行外部写入；只生成具名责任人的动作请求。

## 按需读取

- 开始任何判断前读取 `references/charter-sovereignty-object-state.md`。
- 涉及对象、身份或状态验证时使用 `scripts/validate_object_state.py`。
- 涉及输入、证据、动态规则或专业意见时读取 `references/input-evidence-dynamic-professional.md`，并使用 `scripts/validate_input_evidence.py`。
- 接受独立专业复核前使用 `schemas/qualified-professional-signoff.schema.json` 与 `scripts/validate_professional_signoff.py`；模板或未签署记录必须阻断。
- 涉及分类、认证、测试、标签或 Claim 时读取 `references/classification-certification-claims.md`。
- 涉及 IP、税务海关或平台准入时读取 `references/ip-tax-customs-platform.md`。
- 使用 `scripts/evaluate_professional_domains.py` 计算覆盖和升级路由；不得把其结果表述为专业意见。
- 形成 Gate、处理新证据或事故时读取 `references/gates-continuity-incident-recovery.md`，并使用 `scripts/decision_engine.py`。
- 涉及跨域交接、消费者响应或临时合同迁移时读取 `references/cross-domain-migration.md`，并使用 `scripts/validate_integration_migration.py`。
- D03、D04、D08 消费合同还必须运行 `scripts/validate_consumer_acceptance.py`；机器合同通过不等于独立域 Owner 签署，Owner 为 pending 时阻断外部签署与 L4，不得伪装成独立接受。
- 所有任务遵守 `references/professional-depth-governance.md`、`references/skill-integration-protocol.md` 和 `references/data-contract-and-automation.md`。
- 处理机密、个人或潜在特权材料前读取 `references/confidential-material-governance.md`。
- 交付报告时读取 `references/output-protocols/professional-report-delivery.md`，并用 `schemas/professional-report.schema.json` 验证。
- 发布前运行 `scripts/validate_release_candidate.py` 和全部 `test_*.py`。
- 判断 D05 专业工程门是否完成必须运行 `scripts/validate_completion_readiness.py`；非零退出表示工程证据未闭合。零退出只代表 `controlled_pilot_engineering_ready`，不代表 L4、生产成熟度、适格专业签章或 D14 开发授权。
- L4 只能使用 `schemas/authorized-replay.schema.json` 记录的授权、脱敏、非合成且独立复核通过的案例，并运行 `scripts/validate_l4_replays.py`；少于 3 例或缺少跨辖区/主题覆盖时保持关闭。
- 正式决策、跨域交接和状态变更必须运行 `scripts/validate_decision_contract.py`，接入 `ERDG-CONTRACT-2026.07`，并使用 `governance/erdg/adapters/legal-tax-intellectual-property-market-access-decision/adapter.json` 声明 D05 主权；失败时不得形成生效动作。

## 当前结论上限

可以对真实任务输出商业 Gate、证据缺口、动作上限和专业复核请求；不得签发法律、税务、FTO、认证或实验室意见。没有授权真实回放和独立复核前，不得声称生产成熟度。
