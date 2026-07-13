# Uplift 与净增量价值

四类客户：可说服者（因动作改变）、自然购买者（有无动作都购买）、无动于衷者、反感者（动作使结果变差）。高响应概率不等于高 Uplift。

`τ(x)=E[Y(1)-Y(0)|X=x]`。只使用有可靠处理分配、资格和暴露日志的实验/可信准实验训练双模型、T/X/R-Learner 或因果森林。用 Qini、AUUC、分位数增量差异、时间外和重要人群稳定性验收，不用普通 AUC 代替。

`NIV(i,a)=uplift(i,a)×ContributionMargin(i,a)-Incentive-ContactCost-FatigueCost-RiskCost`。只有 `NIV>0` 且通过资格规则的动作进入候选；否则输出“不触达”和原因。优惠额是动作的一部分，不应在模型后统一发放。
