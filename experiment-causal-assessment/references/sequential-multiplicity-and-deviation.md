# 序贯、多重性与偏差治理

## 序贯范式互斥

- `fixed_horizon`：按冻结样本/时间只做主分析；中途看数不得据此停止。
- `group_sequential`：预登记 looks、information fraction、alpha-spending/边界和非绑定 futility。
- `anytime_valid`：使用经验证的 e-process 或 confidence sequence，并单独报告。

三者不可混用。固定样本试验因偷看提前结束时，不得沿用固定样本 p 值。后端不可用时，返回不可执行，不以 Bonferroni 粗略模拟 group sequential。

## 假设家族 Ledger

家族键至少包括实验、primary/secondary/guardrail、指标、处理对比、总体、窗口和分析版本。fork、重跑、换窗或新增 treatment 不会自动创建“全新 alpha”。预登记 primary family 可用 Holm/Bonferroni；FDR 只用于明确探索性家族。共享对照 A/B/n 需保留相关结构，Dunnett 仅在已验证后端执行。

## 偏差登记

每个偏差记录：发现时间、协议条款、原因、是否在看结果前、影响对象、可逆性、处理、等级影响、owner。关键偏差包括：分配实现改变、样本口径改变、结果后换 primary/窗、未登记停止、坏控制、删异常、模型分叉、延迟成熟、同时活动、泄漏和 selective reporting。

## 诊断的独立否决权

- SRM：分配计数与预期不符时调查随机化、日志或入组筛选；未解决则阻断 CE5，严重时阻断 CE4。
- 护栏：达到预定伤害界限可停止，即使 primary 有利。
- 指标成熟：结果未成熟不允许用暂态数据定稿。
- 暴露/污染：assignment 与 exposure 不一致需 ITT 与不依从合同；交叉污染改变支持的 estimand。
- 多重性：未登记 family 或重复寻找显著窗口时降级。

## 结果姿态

停止、继续、扩样、重做和不行动是不同决定。扩样只能按预登记序贯/样本再估计规则进行；因为“差一点显著”临时加样是偏差。任何复核都应同时呈现原协议结果与偏差后探索结果，不能覆盖原结果。
