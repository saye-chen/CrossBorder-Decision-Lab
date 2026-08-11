# D01—D13 消费者迁移、双轨与验收

## 1. 迁移对象与责任边界

F01 迁移因果识别、CE0—CE5、claim ceiling、适用范围、失效和重算合同，不迁移任何消费域的经营主权。每个消费域必须完成字段合同、双轨差异、消费者签收、回滚与重算四个闭环；受控试点闭环与生产/L4 闭环分开记账。

`integrations/consumer-migration.json` 是权威机器合同。共享字段使用冻结的 `causal_handoff_v1_full` profile；每个域另有业务字段去向、用途级最低证据、旧标签禁配表、主权、验收和回滚合同。

四类证据不得混写：

1. `fixture_non_production`：证明执行器的确定性、失败关闭和边界，不证明真实系统等价。
2. `controlled_pilot_owner_acceptance`：消费域负责人基于合同测试、fixture 差异、回滚和失败关闭证据签署，只允许非生产、非高风险的受控试点用途。
3. `production_dual_run`：同一时间冻结输入经过旧轨和 F01 轨后的实际结果证据。
4. `production_consumer_owner_acceptance`：由消费域负责人基于生产双轨差异另行签署，不得由 ECAE 生产者或实现者代签。

本地 13/13 合同测试和逐域 owner 条件接受可以关闭 WP11 的受控试点范围，但不等于生产双轨或生产接受。生产证据只进入 L4，不反向污染 L1—L3。

## 2. 用途级证据门槛

不存在一个跨域通用的“最低 CE”。最低等级必须绑定具体用途：

- 描述、背景和替代解释可以保留在 CE1—CE3，但不得改称因果或增量。
- 指定范围内的因果经营支持至少 CE4。
- 高风险资本、财务、库存、媒体、合作、活动或客户动作支持要求 CE5 和 `independent_accepted`。
- 增量经济输入必须同时带效应值、区间、适用范围、参数快照、到期时间、失效和重算触发器。
- HTE/policy use 还必须带诚实评估的 policy-value 区间和容量、成本、公平、授权等约束；分箱 uplift 不是个人因果事实。

消费域可以收窄允许用途、措辞和动作，不得拓宽 CE、claim ceiling 或 applicability，也不得删除禁止项。受控试点接受只覆盖 `requires_independent_review=false` 的合同用途。

## 3. 旧标签不等价规则

旧系统中的 `Go`、`Continue`、`qualified_causal_claim`、`causal_claim_allowed`、`incremental_eligible`、`C2/C3`、`E6/E7` 等字符串不是 F01 CE 等级。旧证据的自动上限统一为 CE0；只有重新装配完整协议、数据、识别、诊断和复现证据后，才能按 F01 重新评级，且旧轨重新审查的合同上限不超过 CE3。

重点红线：

- D06 只做经济解释，财务公式不能创造或升级 CE；没有合格回执的测算只能是显式 `noncausal_scenario`。
- D07 缺失或到期的 `incremental_contribution` 必须是 `unknown`，绝不能默认 0 后进入库存排序。
- D08 的基础二项 Wald、D09/D12 的简化 DiD/SCM/Geo、D13 的基础 Wald 和 uplift 分箱均不得继承 CE4/CE5。
- D10 的 C0—C3 是另一套本体；C2/C3 的 `incremental_eligible` 与 F01 CE4/CE5 非等价。
- D04/D05 的质量、法律、税务、IP、安全和市场准入红线始终不可被因果效果补偿。

## 4. 双轨协议

Fixture 和生产双轨都至少覆盖：正常、接近决策阈值、负效应/伤害、过期、失效触发、范围不匹配和缺字段。每次运行必须冻结 canonical object、时间、平台、国家、人群、处理版本、指标口径、代码、环境、参数、原始结果与哈希，以及看结果前登记的数值容差。

差异按 claim、grade、scope、numeric、action 五维记录：

- 语义完全一致且哈希绑定可记 `equivalent`。
- F01 缩窄措辞或动作是 `expected_restriction`，仍需消费者知情处置。
- 旧轨声称 causal/incremental、F01 新增允许动作、范围变化、空值状态变化或数值超容差均为 blocking。
- blocking 差异未关闭时禁止签收、切流或停用旧 reader。

`scripts/compare_legacy_f01.py` 负责差异记录。Fixture 只能写 `fixture_dispositioned`；实际同时间窗、同输入的生产证据才可写 `production_dispositioned`。

## 5. 消费者侧验收

消费者负责人使用 `consumer-acceptance.schema.json` 签署接受、条件接受或拒绝。记录必须显式声明 `acceptance_scope`，并绑定 migration ID、域 ID、合同版本、精确合同哈希、证据、允许用途、条件、审阅人与有效期。

验收成立需同时满足：

1. reviewer role 与该域 `Dxx_consumer_owner` 完全一致；
2. reviewer 独立于 ECAE 生产实现，`producer_self_acceptance=false`；
3. 接受用途是合同用途子集，不可现场创造新用途；
4. 条件接受有明确条件，拒绝不携带 accepted uses；
5. 合同、schema、claim、适用范围或关键依赖变化时重新签收。

`controlled_pilot_non_production` 必须保持 `production_evidence_claimed=false`；`production` 则必须引用真实双轨、生产差异和生产回滚证据。`scripts/validate_consumer_acceptance.py` 只验证签收真实性和合同绑定，不代表业务动作已经批准。

截至 `2026-08-10`，Miles Chen 以 repository owner 指令授权 D01—D13 的受控试点条件接受。13 份记录均绑定精确合同哈希，只接受无需独立复核的普通用途。非生产双轨预检覆盖 91 个强制案例，差异阻断为 0、失败关闭语义异常为 0，13 次模拟回滚均通过。

因此 `wp11_controlled_pilot_complete=true`。同时 `production_dual_run_completed=false`、`l4_production_acceptance_complete=false`、`independent_owner_accepted=false`；fixture、公开方法或 owner 的非生产接受都没有被提升为生产证据，也不授权任何定价、现金、库存、广告、页面、客户触达、发布、付款、签约或其他自动业务动作。

## 6. 消费运行时决策

`scripts/evaluate_consumer_handoff.py` 的状态语义：

- `accept`：合同、范围、时效、等级、payload、review 和消费者签收均通过；仍需业务 owner 决定。
- `hold_pending_consumer_acceptance`：技术合同合格但当前 scope 尚未签收，只能保留描述性上下文。
- `degrade`：等级、claim ceiling 或独立审阅不足，降为合同 fallback，不得使用因果措辞。
- `reject`：消费者、schema、范围、用途、动作或必需 payload 不合格。
- `request_recompute`：过期、旧状态、失效或重算触发器命中；立即停止静默消费。

运行时输出永远保持 `business_owner_decision_required=true` 和 `external_write=false`。

## 7. 回滚、失效与重算

回滚不是恢复旧因果结论，而是恢复旧 reader 的描述性只读能力：

1. F01 handoff 标为 stale，不再供因果或增量用途消费。
2. 增量值编码为 `unknown`，不得沿用旧值或填 0。
3. 旧轨输出只能使用 descriptive/attributed/inconclusive 措辞。
4. 阻断该域合同列出的高风险动作，创建 recompute request。
5. D04/D05 回到 `consumer_sovereignty_only`，继续由专业红线控制。
6. 同一 domain、contract version 和 reason 的回滚必须幂等。

合同变更、到期、数据更正、处理版本、指标、成本参数或适用范围变化都触发影响闭包、重新计算和必要的重新签收。

## 8. 关闭标准

WP11 的 L1—L3 受控试点范围要求：

- 域级合同、映射、用途、主权和禁止写回清单通过；
- fixture 双轨、差异、失败关闭和回滚演练通过；
- 每个域有绑定精确合同哈希的 `controlled_pilot_non_production` 接受或条件接受；
- 高风险用途仍由独立复核门阻断，外部写入保持 false。

该范围现已关闭。以下条件单独属于 L4 生产接受门：

- 生产双轨完成且有可重放证据；
- 所有 blocking/expected 差异均由消费域处置；
- 每个消费域基于生产证据另行签署 production acceptance 或条件 acceptance；
- 生产环境回滚演练通过；
- 所有 L4 production completion gate 由证据自动推导为 true。

任何生产消费者拒绝或仍 pending，L4 生产接受保持未通过。生产执行使用 [D01—D13 消费者生产验收操作手册](consumer-production-acceptance-operator-runbook.md)、`integrations/consumer-production-acceptance-plan.json` 和 `scripts/evaluate_consumer_production_run.py`；这些产物只负责协调、比较和留证，不创建 owner 签名或生产业务动作。
