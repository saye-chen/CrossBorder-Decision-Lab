# AAMO 跨 Skill 集成协议

## 共享包

每个输入/输出包必须包含 `packet_id/source_skill/source_runtime/target_skill/object_id/object_version/as_of_time/status/evidence_ids/calculation_ids/allowed_uses/forbidden_uses/expiry/recompute_trigger`。状态仅允许 `proposed/validated/blocked/inconclusive/stale/withdrawn/superseded`；来源更新不得静默覆盖已批准版本。

`allowed_uses/forbidden_uses` 分别是允许用途与禁止用途；接收方必须逐项执行，不能仅保存字段。

## 双向主权

| 对接域 | AAMO 可消费 | AAMO 可返回 | 禁止越权 |
|---|---|---|---|
| CIDM | 资本姿态、现金/利润/库存红线 | 广告可行性、成熟/边际经济、预算上限 | 改写进入/退出 |
| CIM | 已确认竞争事件、时间窗、证据 | 广告内部响应与待验证假设 | 把可见广告当竞品花费 |
| VLB | 素材机制、变体、权利和成本 | 付费交付结果、素材测试请求 | 以付费胜出证明内容机制 |
| CIG | 授权人群、CLV、频控、不触达 | 广告人群交付和增量请求 | 执行客户触达 |
| LIFD | ATP/CTP、配送、容量和降级线 | 广告消耗需求和节奏 | 修改补货/库存 |
| PLCO | 页面版本、断点、实验和承接能力 | 流量、查询/人群、素材承诺 | 修改页面或用评分替代增量 |
| CAPM | 达人权利、归因边界、合作对象 | 付费授权需求和交付结果 | 改价、签约、佣金 |
| MBCM | 市场姿态、Offer机制、渠道角色 | 广告内部预算/出价与测量结论 | 改写品牌/活动总战略 |

## 接受、冲突与部分失败

接收方先验证身份、版本、证据截止、币税时区、主权和允许用途，再显式 `validated/rejected`。`proposed` 不得自动生效。冲突依次按不可补偿红线、主权、对象版本、证据等级、时效和可复算性裁决，不多数投票。

参与域失败时保留未受污染的本域事实，只把依赖主张降级。例如 LIFD 不可用只阻断库存约束下的放量，不能抹掉已验证的追踪故障；PLCO 不可用时页面根因保持 `inconclusive`，不能自动归因广告。

## 结果回填

任何跨域动作回填 `accepted_version/applied_at/actual_scope/actual_spend/actual_delivery/mature_profit/incremental_result/guardrail_result/deviation/superseded_packet_ids/next_recompute_trigger`。来源撤回、版本变化或证据过期时，接收方只重算受影响闭包并撤销失效动作。
