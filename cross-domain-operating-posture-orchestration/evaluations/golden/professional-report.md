# D14 COPO 专业评测 Golden

## 经营姿态合成

当前有效姿态仅由各专业 owner 已批准结论、有效证据版本和已批准资源包合成。D14 不裁决专业结论，不批准资本，也不把总分用于覆盖红线。

## 依赖编排

每个动作保留 owner、前置依赖、成功条件、停止条件和回滚。required owner 缺失、回执过期、哈希错误或不可补偿门失败时，姿态保持阻断或不确定。

## 冲突升级

专业冲突进入 owner 升级队列；D14 只描述冲突、影响范围和待决事项，不通过平均、投票或静默覆盖解决冲突。

## 主权边界

D01-D13、F01/F02 与 ERDG 的主权保持不变。所有外部动作维持 proposed 或 owner_approval_pending；L4 未关闭前禁止 production-ready 和 external write 声明。
