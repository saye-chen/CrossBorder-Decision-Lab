# Amazon营销操作卡

## 适用对象

Amazon Marketplace的Coupon、Deal、Prime/会员价格、Subscribe & Save、品牌推广、站内广告、Amazon Attribution与站外引流组合。具体名称、资格、费用、展示和可叠加规则属于动态事实，执行时必须核验Seller Central或官方页面。

## 店铺与品牌层级路由

每个活动先建立 Amazon `store_profile_id`，锁定 Seller ID/法定主体、Marketplace site、Seller Central 3P 或 Vendor Central 1P、卖家角色、FBA/MFN/Vendor 履约、库存所有权、目录所有权、品牌授权和 Ads Profile。Brand Registry、Brand Store、A+ 属于品牌资产层，不等于卖家账户；同一 ASIN 也不等于同一卖家 Offer。没有画像和证据指纹时，只输出条件方案，不给跨店铺迁移、放量或归因结论。

活动比较必须按 `店铺账户 × 站点 × Offer × ASIN/variation × 履约方式 × 价格版本` 分桶。品牌 Owner、授权经销商、Vendor 1P 和 Amazon Business 叠加层分别核算价格控制、佣金/采购成本、库存责任、活动资格、广告归因和成熟贡献；不得用品牌店铺内容、Vendor 条款或 FBA 配送承诺替代其他 Offer 的事实。

运营节奏也必须分开：日内处理资格、价格、库存、Offer 和活动异常；每日核对活动展示、费用、库存、配送、广告和退款成熟；每周复盘拉前、蚕食、成熟贡献和恢复窗；每月复核品牌资产、B2B 结构、站点组合和退出成本。品牌 Owner、授权经销商、Vendor 1P 的主指标集合不同，不能以一个“促销销售额/转化率”日报代替全部经营过程。

## Offer载体必须分开

- Coupon：记录资格、预算、费用、领取/核销口径、展示位置和叠加关系。
- Lightning/短期Deal：记录活动窗口、价格历史约束、库存承诺、费用和Deal后恢复窗。
- 7-Day或长期Deal：单独评估较长折扣暴露对参考价、拉前和恢复的影响。
- Subscribe & Save：区分平台/卖家折扣、订阅留存、取消和长期贡献。
- Prime/会员专享：明确资格人群，不把会员选择效应当活动增量。

不得把不同载体的归因订单合并成一个“促销订单”后直接比较。

## 证据与数据

- ASIN、variation、seller、marketplace、Offer版本和价格历史；
- Deal资格与费用快照；
- Business Reports、广告、Attribution和品牌分析的时间窗；
- 库存、Buy Box/Featured Offer、配送承诺和页面版本；
- 成熟退款、退货、平台费和订阅留存。

## 专属识别风险

- Featured Offer变化、自然排名和库存会同时影响活动结果；
- 品牌词广告可能截取自然需求；
- Deal前等待和Deal后透支造成窗口搬移；
- 会员人群与非会员不可直接比较；
- 不同ASIN/variation之间存在蚕食。

## 操作决策

1. 由PLCO确认页面与Offer展示承接。
2. 由LIFD确认活动及恢复窗库存。
3. 使用历史价格—订单估计弹性；弱证据只做折扣网格情景。
4. 用ASIN/地域/时间holdout或合成控制估计增量。
5. 扣除Deal/Coupon费用、广告、退款、履约、拉前和蚕食。
6. 成熟增量下界和客户/品牌护栏通过后才允许扩大。

## 停止条件

资格或费用变化、库存风险、Featured Offer丢失、页面版本变化、参考价风险、成熟贡献为负或实验污染时停止/重算。
