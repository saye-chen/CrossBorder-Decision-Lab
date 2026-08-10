# 方法卡：随机实验 ITT

- **目标量**：冻结总体中 assignment policy 的 ITT；不是按实际曝光的效果。
- **识别**：分配概率已知且实现一致；一致性；无未建模干扰；结果采集不因 treatment 差异缺失。
- **实现**：连续/计数用组均值差与 Welch 方差的正态近似；二元风险差用 Newcombe hybrid score 区间、零假设 score 检验；ratio-of-totals 用单位级 influence-function delta method；A/B/n 输出共享对照的未调整对比，须另接 hypothesis-family ledger。
- **单位**：输入必须是一行一个随机化/分析单位。重复事件需先按单位聚合；ratio 输入保留每单位分子、分母。
- **诊断**：assignment proof、SRM、曝光/交叉、成熟、缺失/流失、污染、干扰、多重性。
- **边界**：正态/Delta 近似的有限样本充足性由协议与独立方法复核；脚本不自行设全行业样本阈值。
- **CE 上限**：所有 Gate、诊断、精度、复现、经济和独立复核通过时 CE5。
- **失败**：非 ITT、非有限数、样本不足、无对照、非法二元/计数/ratio、未调整多臂结果不得作为最终 primary。
