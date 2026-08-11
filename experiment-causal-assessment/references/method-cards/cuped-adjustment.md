# 方法卡：CUPED 预处理协变量调整

- **目标**：在随机实验中用 treatment 前协变量降低方差，同时保持 ITT。
- **实现**：在合并样本上中心化协变量，以 pooled linear projection 估计 theta，构造 (Y-\theta'(X-\bar X))，并同时保留未调整与调整结果。
- **必要条件**：协变量时间严格早于 assignment/treatment；分析总体不因结果改变；协变量缺失方案预登记。
- **禁止**：post-treatment 中介/选择变量、结果后挑选协变量、用 CUPED 赋予非随机研究因果资格。
- **诊断**：奇异矩阵、协变量漂移、缺失不平衡、方差是否确实下降、未调整与调整方向差异。
- **边界**：当前 native 为 pooled linear CUPED，不冒充带完全交互和有限样本稳健推断的通用 ANCOVA。
