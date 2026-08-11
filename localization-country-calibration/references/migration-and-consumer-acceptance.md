# 迁移与消费者接受

临时合同按 `inventory → shadow → dual_run → cutover_ready → cutover → retired` 迁移；cutover 可回滚到 dual_run。关键字段未映射、差异未解释、目标证据更弱、消费者未接受或回滚不可用时不得切换。

D01—D13 分别验证版本、哈希、血缘、未知/过期/冲突失败关闭、动作上限不提升、选择性重算和回滚。受控 fixture 接受不代表生产接受；旧读只能在接受窗口内保留，不能继续扩展第二套共享语义。
