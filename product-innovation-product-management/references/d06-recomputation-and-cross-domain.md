# D06 重算与跨域合同

## 版本策略

- 保留 `PPFC-XDOMAIN-2026.07` 原件，历史消息继续由 D06 v1 校验器读取。
- D03 与 D06 新消息使用 `PIPM-XDOMAIN-2026.07`；它是增加 D03、字段级回执和重算影响集的兼容扩展，不覆盖旧合同。
- 消费方按 `contract` 路由。未知版本、对象版本、币种、税基或有效时间不一致时失败关闭，不做静默转换。

## 消息闭环

1. D03 发送 `product_change` 或 `recompute_request`，状态只能是 `proposed`。
2. D06 返回 `economic_constraint`、`recompute_result` 或逐 Claim `acceptance`。
3. 接收方必须逐 Claim 标记 `accepted/rejected/blocked`；部分接受只使被拒 Claim 及其下游失效。
4. `idempotency_key` 与 `message_id` 共同防止重试产生第二份业务效果。
5. 所有消息保持 `external_write=false`，跨域结论不得替接收域自我验证。

## 选择性重算

依赖图使用“输入字段 -> 派生字段”。变更字段的传递闭包为 `recompute_fields`；未进入闭包的既有结论保留在 `preserved_fields`。缺失依赖或出现循环时 `blocked`。币种、税基、国家、平台、对象版本和业务有效时间是身份边界，任一不匹配都不得合并。

典型 D03 -> D06 触发字段包括 `target_unit_cost`、`packaging_dimensions`、`variant_mix`、`warranty_policy`；D06 回传的 `price_floor`、`contribution_margin`、`cash_peak` 和 `payback_period` 仍由 D06 主权确认。
