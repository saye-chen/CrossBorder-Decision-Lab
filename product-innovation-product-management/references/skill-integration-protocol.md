# Skill 集成协议

## 主权

D03拥有产品机会转产品任务、产品定义、MVP、需求、规格、变体、包装、验证范围、路线图、迭代和停产建议。CIDM拥有资本进入；D04拥有供应商、制造和量产质量；D05拥有法律准入；D06拥有价格利润现金；LIFD拥有库存履约；其余域保留页面、广告、伙伴、营销、内容和客户动作主权。

## 输入与输出卡

跨域输入至少包含contract、message_id、idempotency_key、object_id、object_version、country、platform、as_of_time、recorded_at、evidence_ids、parameter_snapshot、allowed_uses、forbidden_uses、sender_sovereignty、requested_owner和`external_write=false`。

D03输出产品事实、产品定义、规格、变体、包装、版本变化、Claim候选、影响集合和验证请求。输出必须标记状态、允许用途、禁止用途、证据血缘、缺失项、重接受触发和旧读兼容。

## 禁止回写、版本与部分失败

消费者可以接受、拒绝、部分接受、请求证据或请求重算，但不得改写D03规范产品事实。D03不得改写消费者的投资、制造、准入、价格、库存、页面、广告、伙伴或营销决定。

对象版本不一致时阻断；相同幂等键和输入哈希返回同一结果，相同键不同输入阻断。新版本不能静默覆盖旧版本。

一个消费者失败不得污染其他消费者已验证结果；失败节点及其下游进入blocked/expired/reaccept，未受影响节点保留。禁止多数投票覆盖安全关键或主权域拒绝。

## 冲突与反向消费

事实冲突按对象、来源、有效期和证据等级裁决；主权冲突按Owner裁决；合同版本冲突走双读和回滚。无法裁决时保持`inconclusive`。

D03消费CIM竞品事实、CIG VOC、VLB内容机制或其他域输出时，也必须通过对应消费者合同。当前没有正式反向adapter的路径只能作为显式输入证据，不能作为自动权威数据源。
