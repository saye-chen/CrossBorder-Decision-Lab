# Skill 集成协议

跨域包必须声明 object_id、object_version、source/target、主权、允许用途、禁止用途、证据/计算、状态、版本、哈希和消费者响应。消费者可接受、拒绝、部分接受或要求重算。

部分失败只阻断受影响字段和动作，保留独立有效结果。证据冲突保留双方版本并升级 owner；非 owner 不得改写正式结论。D04 与 D01、D03、D05、D06、D07、D13 和 ERDG 均执行这一边界。

## 标准 envelope

跨域包至少包含：

- message_id、source_domain、target_domain；
- object_id、object_version、as_of_time；
- authority、allowed_uses、forbidden_uses；
- requested_fields、field-level provenance；
- evidence/calculation/decision lineage；
- runtime 和 contract version；
- consumer_response、accepted_fields、rejection_reasons；
- invalidated_fields、recompute_scope 和 rollback reference。

## 发送方义务

D04 发送前确认字段属于本域、版本 current、证据/计算可追溯、允许用途明确、禁止用途完整。不得把建议字段命名成目标域最终决定，也不得把 `pending` 写成 accepted。

## 消费者义务

消费者逐字段检查对象、版本、时点、权限、单位和适用性。响应：

- accepted：明确进入本域状态；
- rejected：给原因和受影响字段；
- partially_accepted：列出接受与失效字段；
- recompute_required：给所需新输入或参数；
- pending：无执行权。

## 冲突优先级

1. 主权 owner 决定优先于非 owner 推断；
2. current object/version 优先于旧版本；
3. 范围匹配证据优先于泛化证据；
4. 原始记录优先于无修订链摘要；
5. 冲突无法解决时保留双方并阻断依赖动作；
6. ERDG 校验结构，不代替业务 owner 裁决。

## 七条联动闭环

- D01：资本暴露接受/拒绝改变首单上限；
- D03：规格/CTQ 变化触发样品、工艺和批次重算；
- D05：准入拒绝阻断依赖市场动作；
- D06：现金/利润字段拒绝使 TCO/承诺相关字段失效；
- D07：只消费合格批次、产能与生产交期，不反向改写质量；
- D13：客户故障回流批次与 CAPA，补偿仍归 D13；
- ERDG：拒绝越权、错误版本、伪 L4 和外部写入。

## 部分失败示例

若 D06 仅接受采购价而拒绝账期资金成本：

- accepted_fields = purchase price；
- invalidated_fields = financing cost、cash-dependent commitment；
- recompute_scope = TCO、procurement commitment；
- preserved = MSA、process stability、batch lineage；
- 最终决定降级或阻断依赖字段，而不是删除全部 D04 分析。

## 连续追问

新消息必须关联既有 object/version。目标域后续撤回接受时，D04 生成 Revision/Rebase，使相关字段失效并检查现实动作；已经下单、生产或发运时进入恢复，不能只更新文本。
