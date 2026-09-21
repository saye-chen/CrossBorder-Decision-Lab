# Amazon 店铺经营模型与路由

版本：`PLCO-AMAZON-STORE-2026.07`；运行时：`PLCO-2026.07`；状态：`controlled_pilot`。

机器可校验的中央合同见 [amazon-store-operating-models.json](amazon-store-operating-models.json)；店铺画像建立后，运营节奏和指标读取 [Amazon 运营流程与指标合同](amazon-operating-workflows-and-metrics.json) 及 [说明](amazon-operating-workflows-and-metrics.md)。本文件把 Amazon 的“店铺”拆成卖家账户、品牌资产层、站点和卖家 Offer，避免把同一 ASIN 下不同卖家、不同履约方式或不同法律主体混为一谈。

## 使用门槛

Amazon 专项报告先建立 `store_profile`，再进入 Listing、Offer、广告、库存或组合判断。至少锁定：

- 卖家账户、Seller ID、法律主体和 Seller of Record；
- Marketplace 站点、语言、税务范围和证据截止时间；
- 3P Seller Central、1P Vendor Central 或 Amazon Business 经营程序；
- 品牌商、授权经销商、Vendor 或服务运营者身份；
- FBA、MFN/FBM、Vendor Fulfilled 或混合履约；
- 库存所有权、目录控制权、品牌授权和账户健康状态；
- Ads Profile、Brand Store/A+ 等权限与对应证据。

缺少关键字段时使用 `unknown`，不填默认值。`unknown` 只能产生补证、条件诊断或冻结放量的建议，不能生成外部执行动作。

## G1—G6 与执行边界

G1 身份、G2 站点/程序、G3 品牌与目录权利、G4 Offer/库存/履约、G5 证据新鲜度、G6 测量与归因必须逐项记录 `pass / fail / unknown`。任一 `fail` 阻断，任一 `unknown` 只允许条件诊断和补证。

具体方案必须写明对象、字段/槽位、负责人、前置证据、审批、上线顺序、成功条件、停止条件和回滚版本。每个主根因都要有反事实验证，例如固定站点和履约后只切换 Offer 或 Ads Profile；不能用一次前后变化或账户平均值证明因果。

## 基础经营档案

### 3P 品牌商 + FBA

重点是品牌权限、目录控制、FBA 单位经济、可售库存、Featured Offer、广告与页面承接。不能继承 Vendor 1P 条款、经销商的价格和 Buy Box 假设，或 FBM 配送承诺。

### 3P 品牌商 + MFN/FBM

重点是自有履约容量、配送承诺、退货责任、库存真实性和 Offer 可购买性。不能直接套用 FBA 费用、时效和库存状态。

### 3P 授权经销商 + FBA/MFN

重点是品牌授权、真实货权、商品一致性、采购成本、价格政策、Featured Offer 竞争和授权撤回风险。经销商不能把品牌商的 Brand Store/A+ 权限或品牌增量结论当作自己的权限和证据。

### 1P Vendor Central

单独评估采购订单、批发价格、供货能力、零售内容权、扣款/索赔、库存责任和渠道冲突。Vendor 结论不能与 Seller Central 的卖家利润或 Offer 控制权混算。

## 叠加层

- **Amazon Business**：作为 B2B 商业叠加层，单独核算企业价格、阶梯价、MOQ、发票/税务和企业需求，不把消费者转化率直接当作 B2B 证据。
- **Brand Registry / Brand Store**：作为品牌资产层，不是独立 Seller Account。必须同时核验品牌授权、目录控制和具体卖家 Offer。
- **多账户/多品牌/多站点组合**：必须核验法律主体、经营目的、授权、库存、价格、数据隔离、账户关联和关闭迁移方案；不提供规避关联、重复铺货或处罚绕过路径。

## 报告路由

1. `store_identity_and_permissions`：确认账户、主体、程序、权限和健康状态；
2. `catalog_rights_and_brand_authority`：确认目录、品牌、素材和内容控制；
3. `listing_parent_child_and_offer_integrity`：区分 ASIN、Parent/Child、SKU 和卖家 Offer；
4. `featured_offer_and_buyability`：核对价格、库存、配送、可购买性和卖家归属；
5. `fulfillment_inventory_and_returns`：按 FBA、MFN 或 Vendor 单独核算；
6. `advertising_profile_and_attribution`：按 Ads Profile、站点、推广 ASIN、购买 ASIN 和归因窗对账；
7. `portfolio_cannibalization_migration_and_exit`：处理多店、迁移、蚕食、冲突和退出。

## 继承与禁止

可复用的产品事实也必须在新站点、新 Offer 和新履约模式下重验。评论、评分、广告归因、Featured Offer、索引、配送承诺和店铺权限不跨对象静默继承。FBA 与 MFN 的履约承诺、Vendor 与 3P 的经济口径、品牌资产与卖家 Offer 的权限边界均为不可直接继承项。

## 交付状态

没有授权后台、当前规则、库存/履约或账户权限证据时，报告最高只能是 `controlled pilot / conditional`。中央合同不授权发布、改价、改 Offer、合并 Listing 或调整广告；所有动作仍必须通过 ERDG、责任域和人工审批。

异常时先冻结传播并恢复最近验证通过的页面、Offer、库存和归因版本；回滚必须记录影响闭包、剩余暴露和责任人。

## amazon-store-operating-models 专属决策内核

| 维度 | Amazon 专项要求 |
|---|---|
| 核心机制 | 以 Seller Account、品牌资产、Marketplace site 和卖家 Offer 四层身份路由，基础 archetype 与 overlay 分离。 |
| 计算或判定 | 只有画像、对象、时间和证据指纹闭合后，才可比较广告、库存、履约、页面和组合经济。 |
| 主要失效 | 把 ASIN 当店铺、把 Brand Store 当账户、把 FBA 承诺套给 MFN、把 Vendor 口径套给 3P，或跨 Profile 归因。 |
| 决策动作 | 先过 G1—G6；缺字段补证，冲突阻断，条件状态只做可逆试验；所有跨域交接保留对象和权限边界。 |
