# 品牌价值与聚合客户经济

## 品牌价值桥

品牌代理指标必须经过以下量化链路：

`代理变化 → 行为变化 → 增量需求 → 价格/留存效应 → 成熟贡献`

每一箭头单独估计并报告区间，不允许把搜索增长直接乘平均客单价。

## Adstock与衰减

品牌代理或投资使用几何adstock表示延迟和残留：

`Stock_t = Input_t + decay × Stock_(t-1)`

半衰期：

`half_life = log(0.5) / log(decay)`

使用`brand_value_bridge.py`估计adstock后的代理—经营结果斜率、标准误和拟合度。缺少同期控制变量时只作可证伪情景。

## 价格溢价

品牌溢价至少使用匹配商品：

`premium_i = brand_price_i / matched_generic_price_i - 1`

匹配需控制规格、评分、履约、卖家、促销、库存和页面质量。未匹配价差不能归因于品牌。更强设计应使用面板固定效应、hedonic regression或受控价格实验。

## 搜索到收入

区分品牌搜索量、搜索点击、合格访问、成熟订单与增量订单。每层使用同时间窗和版本，报告自然趋势、媒体覆盖、分销扩张和竞争事件。最终只使用增量订单和成熟贡献进入估值。

## 聚合客户经济

CIG保有个人客户身份、CLV模型和触达主权；MBCM只消费聚合cohort包：

- cohort_id与获取活动版本；
- acquired_customers；
- acquisition_cost；
- 分期retention rate；
- 每活跃客户贡献；
-观察窗、成熟度和授权用途。

简化cohort CLV：

`CLV = Σ retention_t × contribution_per_active_t / (1+r)^t`

`CAC = acquisition_cost / acquired_customers`

累计折现贡献首次达到CAC的期间为payback，并与`maximum_payback_periods`比较。使用`aggregate_customer_economics.py`计算CLV/CAC和回收期。

## 模型升级

- 交易频次与流失：CIG可提供BG/NBD或Pareto/NBD输出。
- 金额：CIG可提供Gamma-Gamma或分层贡献模型输出。
- MBCM不得自行拼接个人身份或据此触达，只比较聚合获客质量。
- 新客数量高但CLV/CAC低、回收期超限或退货投诉恶化时，活动不得因首单ROAS高而放量。

## 品牌投资情景

`brand_investment_scenarios.py`只负责折现与损失边界；现金流来源必须来自上述价值桥、聚合客户经济或明确外部估计，并保留模型版本、区间与替代解释。
