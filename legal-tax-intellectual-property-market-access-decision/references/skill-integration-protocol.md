# Skill 集成协议

每个交接必须写明允许用途和禁止用途；任一参与域部分失败时，整体不得被包装成全量通过。

使用 ERDG v2 handoff 和 Decision Cycle。D05 接收 D01、D03、D04、D06—D13 的事实与约束，输出 `compliance_gate`、`market_access_decision`、`claim_boundary`、`professional_review_request`、`professional_opinion_receipt` 和 `compliance_recovery`。

每个 Packet 必含对象版本、决策问题、来源/目标主权、允许/禁止用途、Gate、影响闭包、血缘和消费者响应请求。D05 不转移其他域主权；ERDG 只校验结构。

消费者回传 `accepted/rejected/partially_accepted/pending`。非 pending 必须写入 Current Decision State；部分接受隔离字段并选择性重算。对象、时间、口径、证据、模型或主权冲突未解决时保持 `inconclusive/blocked`。

旧合同迁移逐字段标记 loss class，同快照双轨比较。安全关键字段非 lossless、消费者拒绝、动作上限升高或旧读不可用时回滚。
