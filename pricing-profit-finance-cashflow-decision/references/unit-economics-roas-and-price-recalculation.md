# 单位经济、价格重算与保本指标

## 价格场景

每个候选价独立执行：

`Price → 收入基数 → 折扣/税/退款 → 各费率与条件费用 → 成本层级 → 贡献 → 保本指标`

禁止沿用基准价计算的比例费用、最低收费或总成本。不同基数费率分别计算；互斥计划不得全部叠加。

## 利润桥

- Gross Profit = 净确认收入 − Product COGS
- Contribution 1 = Gross Profit − 履约 − 平台/支付费 − 预期退货
- Contribution 2 = Contribution 1 − 变动营销 − 变动服务
- Contribution 3 = Contribution 2 − 可避免期间成本
- Operating Profit = Contribution 3 − 分摊经营费用

未售库存不能同时作为全额 COGS 和期末库存价值。现金贡献由日期现金事件计算，不等于利润。

## 指标注册

- `ROAS_ATTR_GROSS = AttributedGrossRevenue / AdSpend`
- `ROAS_ATTR_NET = AttributedNetRevenue / AdSpend`
- `ROAS_INCREMENTAL_REVENUE = IncrementalNetRevenue / AdSpend`
- `ROAS_INCREMENTAL_CONTRIBUTION = IncrementalContributionBeforeAd / AdSpend`
- `ACOS_ATTR_GROSS = AdSpend / AttributedGrossRevenue`
- `MER_GROSS = TotalGrossRevenue / TotalMarketingSpend`
- `MARKETING_ROI_INCREMENTAL = (IncrementalContributionBeforeMarketing - MarketingSpend) / MarketingSpend`
- `PROJECT_ROI = ProjectNetProfit / ProjectInvestedCash`
- `PROFIT_ON_COST = Profit / TotalCost`
- `PROFIT_MARGIN = Profit / RecognizedNetRevenue`

收入/营销支出是 MER，不是 ROI；广告支出/收入是 ACOS，不是 ROAS。归因不得升级为增量。

## F01 合格因果效应接入

D06 只通过消费者侧 `ecae_financial_receipt` 接收增量效应。回执必须绑定 D06 合同、F01 handoff 内容哈希、CE4/CE5、适用范围、有效期、消费者负责人接受记录，以及带独立内容哈希的经济参数快照。缺失、过期、待签、低等级、范围不符或被篡改时，增量输入保持 `unknown`，不得填零或沿用旧值。

`effect_estimate`、`effect_interval`、裸 `incremental_contribution`、`ROAS_ATTR_*` 等旧字段均不能绕过回执进入增量经济测算。没有合格因果回执时，只允许使用明确标记为 `noncausal_scenario` 的敏感性情景；该情景不得输出增量 ROI 或因果措辞。

D06 对合格效应执行 Decimal 区间经济重算并保留价格、利润阈值、现金姿态和财务约束主权。F01 只确认因果证据资格，不签发价格、现金、付款或任何外部动作。

## 保本传导

`PreAdContribution = NetRevenue - AllAvoidableCostsExceptAd`

`BreakEvenACOS = PreAdContribution / RevenueBasis`

`BreakEvenROAS = RevenueBasis / PreAdContribution`

`AllowableAdSpend = PreAdContribution - RequiredProfit - RiskBuffer`

`TargetROAS = RevenueBasis / AllowableAdSpend`

前广告贡献或可承受广告费小于等于零时，不存在有限保本 ROAS，必须阻断。价格、退款、费率、佣金或履约成本变化时全部重算。
