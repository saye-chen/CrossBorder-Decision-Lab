# S10 增量与学习
专属机制：“观察结果—归因结果—反事实结果—成熟贡献”四桥分离。
- 计算：incremental = observed − counterfactual；贡献扣除增量与固定成本。
- 判定/反事实：置信区间跨零不得强因果；明确自然基线。
- 动作：输出结论、不确定性、下一实验和知识更新。
- 失败断言：归因订单不等于增量订单。
- 停止/回滚：污染、样本不足或版本变化时降级声明并重跑。
- 估计工具：先用 `experiment_design.py` 预注册 MDE、功效和分配单位，再用 `causal_effects.py` 估计 DiD/ITT-CACE/合成控制，以 `uncertainty_engine.py` 传播区间，最后由 `incrementality_bridge.py` 接入成熟贡献。

## 最小专业合同
- 四层禁止替代：observed、attributed、incremental、mature incremental contribution。
- 公式：增量订单=观察订单−反事实订单；成熟贡献=增量净收入−全部增量成本。
- 统计门：区间包含0时只可inconclusive/test；统计显著不代表经营显著。
- 识别风险：干预污染、溢出、非同期基线、提前购买、蚕食和选择偏差。
- 翻转条件：下界超过机会成本和最小经营差异后才允许更高动作。
- 跨域请求：AAMO/CIG保有各自因果测量主权，MBCM只汇总活动结论。
- 输出字段：estimand、counterfactual_method、interval、maturity_window、falsifier。
