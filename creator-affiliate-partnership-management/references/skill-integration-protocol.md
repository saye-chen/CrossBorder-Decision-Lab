# CAPM 跨 Skill 集成协议

每个 claim 必须显式列出允许用途、禁止用途、对象版本和有效期；接收方不得把“可用于尽调”扩大为“可用于付款、投流或法律认定”。

## 目录

1. 统一信封
2. 双向主权
3. 部分失败与冲突
4. 状态机
5. 专属决策内核

## 统一信封

每条消息必须包含：`contract_id/contract_version/message_id/correlation_id/causation_id/supersedes_message_id`，真实 sender/receiver Skill 与运行时，对象 ID/类型/版本，平台/国家/币种/时区/`as_of_time`，`status`，S/C证据等级，claim/evidence/calculation IDs，允许/禁止用途，阻断动作，接收确认，input/output/schema SHA-256，有效期和重算触发。

状态只允许 `proposed/validated/blocked/inconclusive/superseded`。缺证据不得 `validated`；接收方不可用不得 `accepted`；过期消息不得继续生效。

## 双向主权

- CIDM：接收达人端口成熟经济、集中和风险；只有 CIDM 改资本姿态。
- CIM：发送已确认外部竞争事件和明确代理字段；CAPM 不把估计报价/预算写成事实。
- VLB：拥有内容机制、Hook、迁移和生产；CAPM发送交付、权利和观察证据。
- AAMO：拥有是否投、素材、预算、出价、增量、疲劳、放量；CAPM只发付费使用权商务候选。
- LIFD：拥有ATP、库存、物流、峰值能力；CAPM只发带货需求区间和事件计划。
- PLCO：拥有页面/店铺/Listing承接；CAPM只调整承诺、链接和商务验收。
- CIG：拥有客户证据、CLV、触达和客户因果；CAPM发送去识别承诺上下文。

未安装 LCR/PPE/PPD/BSO/EOC 时标记 `unavailable`，CAPM输出缺口与人工升级，不代作法律税务、利润、产品、品牌或跨域最终结论。

## 部分失败与冲突

单个参与域超时、拒绝或不可用，不污染其他已验证结果。逐参与域记录 `accepted/rejected/unavailable/timed_out`。Schema不兼容返回 `blocked:schema_incompatible`，不得丢字段继续。

冲突优先级：法律/安全/权利/欺诈 > 履约能力 > 成熟利润与现金 > 因果证据 > CAPM商务匹配 > 内容/广告代理 > GMV/播放/偏好。Hard Gate 不多数投票，也不以高分覆盖。

重试沿用 `correlation_id`，生成新 `message_id` 并引用 `causation_id`。同一 idempotency key 的付款、寄样、结算、下架、举报或处罚最多执行一次。

## 状态机

`proposed → validated|blocked|inconclusive → superseded`。只有主权 owner 可把其字段从 proposed 改为 validated。对象版本、合同、权利、退款成熟、平台规则或证据撤回时，沿依赖闭包重算。

连续报告保留 parent、changed_fields、new_evidence、affected_claims/calculations、preserved_constraints、superseded/current actions 和 next trigger。

## skill-integration-protocol 专属决策内核

机制：以主权字段级 merge 而非报告级覆盖联合结果。每个 claim 带 owner 和用途；编排层只组合，不改写主权。

计算/判定：验证版本兼容、允许/禁止用途不重叠、接收确认、哈希、过期、因果标签和动作幂等；任何失败返回可定位错误码。

反事实：删除 AAMO 后，CAPM仍能完成权利商务判断但不得生成广告动作；删除LIFD后仍能谈判但不得承诺峰值销量；将VLB高分加入不得覆盖G1B。

失效模式：虚构运行时、空证据validated、部分失败被忽略、旧消息复活、重复动作、跨对象混合、接收方静默覆盖。

动作：拒绝消息、降级、请求schema negotiation、保留双方claim、路由owner、重试或退出。成功/停止/回滚均写入消息状态。

机器入口：`scripts/validate_cross_skill_handoff.py`；Schema 位于 `schemas/cross_skill_envelope.schema.json`。
