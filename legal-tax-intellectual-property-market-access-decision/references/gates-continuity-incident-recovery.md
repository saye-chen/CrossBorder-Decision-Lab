# Gate、连续决策、事故与恢复

## Gate 顺序

1. G0：对象、授权、证据资格、范围和时间可用；
2. 分类与适用规则：保留未排除的合理候选；
3. 红线：法律禁止、安全、授权、伪证、制裁、明确专业否定等不可补偿；
4. 覆盖：规则、证书、Claim、专业意见和平台文件与对象逐维匹配；
5. 方案：比较不行动、补证、限制继续、整改、暂停和退出；
6. Gate：输出最窄对象范围和最高动作上限；
7. 连续状态：绑定成功、停止、回滚、复核、有效期和结果回填。

Gate 状态为 `continue_reversible_preparation/continue_with_conditions/evidence_required/professional_review/blocked/suspended/remediation/exit_required`。暂存开发期禁止输出任何等价“正式准入通过”状态。

## 不可补偿红线

明确禁售/禁运、重大安全风险、关键证书伪造或不适用、无授权使用受保护资产、法定主体或许可缺失、明确制裁/执法阻断、适格专业意见明确否定、无法控制的重大召回风险。红线存在时收入、利润、流量和战略价值不能抬高 Gate。

## 动作上限

动作等级从低到高：`collect_evidence → reversible_preparation → limited_internal_test → external_commercial_action`。D05 暂存开发期最高只能建议 `reversible_preparation`；外部动作始终需要责任人授权和正式发布状态。

## 连续决策

每次变化记录变更字段、旧/新版本、直接依赖、受影响 Claim/决定/动作和保留结果。只使依赖闭包失效；不扩大到无依赖对象，也不保留已失效动作。

新版本不得覆盖历史；当前有效决定必须唯一。不同对象、范围或合同版本的结果不得直接比较。

## 事故与恢复

事故链：`detected → triaged → contained → investigation → remediation → professional_recheck → recovery_review → recovered/exit`。

检测后先冻结受影响动作，再确认传播范围。恢复必须具备根因、影响闭包、整改证据、必要复测/专业复核、消费者接受和回滚方案。恢复生成新决定版本，不删除旧阻断。

无法确认影响范围、关键来源不可用、伪证嫌疑未排除或专业复核未完成时保持冻结。通知、下架、召回和申报只生成动作请求，不自动执行。
