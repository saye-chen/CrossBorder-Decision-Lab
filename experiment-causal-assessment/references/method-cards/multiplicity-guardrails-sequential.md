# 方法卡：多重性、护栏与序贯

- **多重性**：Holm/Bonferroni 控制 FWER；BH 只用于明确探索性 FDR。家族跨 fork、rerun 和 window 延续；单 primary 才允许不调整。
- **护栏**：使用协议冻结的伤害方向、阈值、区间和规则。`confirmed_harm` 与 `cannot_exclude_harm` 是不同风险姿态；任一触发可独立停止。
- **固定样本**：只允许一次最终 outcome look；早期查看并据此停止破坏固定样本推断。
- **Group sequential/anytime-valid**：必须由已验证后端执行并保留 information fraction、边界/alpha spending 或 e-process/confidence sequence。
- **禁止**：混用三种范式、因“差一点显著”临时加样、让 primary 收益抵消护栏伤害、把 BH 探索结果写为确认性。
