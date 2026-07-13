# 推荐与下一最佳动作

优化目标为净增量贡献和长期体验，而非点击或订单总量：

`Utility(i,a)=IncrementalProbability(i,a)×ContributionMargin(i,a)-Incentive-Cost-Fatigue-Risk`。

动作包括内容、提醒、商品推荐、服务修复、权益和“不触达”。共购 Lift、矩阵分解、相似人群和时间到事件模型只产生候选推荐，不证明增量。

对每个候选依次检查：授权/退订 → 敏感事件/投诉 → 跨渠道频控 → 市场与渠道可达 → 库存/兼容性 → 权益预算 → 实验资格 → 公平性/人工审批。规则优先于分数。

对第 n 次触达，`MV=IncrementalMargin-SendCost-FatigueCost`；`MV≤0` 停止。频控必须跨邮件、短信、站内信、广告和客服统一计算。
