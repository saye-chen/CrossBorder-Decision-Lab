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

## 保本传导

`PreAdContribution = NetRevenue - AllAvoidableCostsExceptAd`

`BreakEvenACOS = PreAdContribution / RevenueBasis`

`BreakEvenROAS = RevenueBasis / PreAdContribution`

`AllowableAdSpend = PreAdContribution - RequiredProfit - RiskBuffer`

`TargetROAS = RevenueBasis / AllowableAdSpend`

前广告贡献或可承受广告费小于等于零时，不存在有限保本 ROAS，必须阻断。价格、退款、费率、佣金或履约成本变化时全部重算。
