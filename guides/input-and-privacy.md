# 资料准备与脱敏

先保存原文件只读副本。密码、API Key、Cookie、客户姓名、电话、邮箱、地址和不必要的身份信息不进入输入。订单/SKU 用一致的映射 ID，跨表连接必须保留相同映射；映射表留在授权环境。

利润分析需要真实计算口径。经授权使用的价格、成本、币种、税口径、退款与数量不能任意删除或替换成失真数字。若必须按比例脱敏，应所有相关金额一致转换并明确标注，不能用转换后的金额直接下真实经营决定。下表为通用映射规则，不宣称任何平台当前导出列名或费用制度。

## 共用字段

`case_id` 案例 ID；`object_id` 对象；`country/platform/currency` 市场/平台/币种；`as_of_time` 带时区的业务截点；`source_class` 实际来源；`source_ref` 可回查的脱敏文件或来源 ID；`data` 计算数据。样例使用 `synthetic_fixture`；用户估计用 `user_assertion`；经授权自有报表用 `authorized_first_party`。

## 广告利润：原始账单映射

| 输入字段 | 从哪里取得 | 核对要点 |
|---|---|---|
| order_id/currency/maturity | 订单或不重叠核算单元、币种、结算状态 | 主键唯一；未成熟写 immature；不得默认为成熟 |
| gross_revenue | 毛收入 | 与折扣、税、退款口径一致，不能把已扣金额重复扣 |
| discount/refund/chargeback/tax | 优惠、退款、拒付、代收税 | 缺失留空触发补数；已确认无发生才填 0 |
| cogs/fulfillment/platform_fee/service_cost | 商品、履约、平台、可变服务成本 | 统一核算窗；固定分摊与可变成本不得混淆 |
| ad_spend | 广告账单或可核对分摊 | 汇总与原账单守恒；没有归因的花费也不能消失 |

同一订单跨广告平台重复归因不能重复计入；真实数据若无法唯一分摊，先单独处理不重叠账本而非伪造订单对应。混币种先由财务确认转换依据。样例只演示已映射结果，连接器尚未自动导入后台报表。

## 商品测款：情景而非市场事实

| 字段组 | 必须填写 | 来源/解释 |
|---|---|---|
| price | 售价 | 明确币种和税基 |
| fixed_costs | samples/creative/test_ads | 样品、创意、计划测试广告固定投入；不能再计入变动成本 |
| variable_costs | product/logistics/packaging/other | 每件变动成本；保留已确认的 0 |
| rates | platform_commission/creator_commission/payment/return_loss | 0 到 1 的比例；本简化模型以售价为基数，仅适合相同基数场景 |
| funnel | ctr/cvr | 0 到 1；注明来自后台还是假设；未知则无法反推流量 |

费率基数不同、税务或退款结构复杂时路由 PPFC 原有模型；不要硬塞进简化逆漏斗。保本不等于值得进入，竞争、合规、供应、资本仍需验证。

## 补货：可信库存和排期

| 字段组 | 含义 | 缺失处理 |
|---|---|---|
| expected_protection_demand/target_demand_quantile | 保护期需求均值与目标分位 | 没有已批准的需求估计，先分析需求，不编服务水平 |
| target_inventory_position/current_inventory_position/opening_available | 目标库存位、当前库存位、期初可售 | 已锁定、隔离和不可信在途不能当可售 |
| case_pack/moq | 箱规与最小起订 | 整箱和最低采购不能违反现金容量 |
| supplier_capacity/cash_capacity_units/warehouse_capacity_units/lifecycle_cap/shelf_life_cap | 供给、现金、仓容、生命周期、保质期数量上限 | 缺失不当作无限能力 |
| order_date 与 8 个 *_days | 下单、确认、生产、质检、始发、干线、清关、入仓、上架 | 单位整数天；情景日期不是承诺；缺失不当 0 天 |
| timeline | 每期 eligible_arrival/demand/reservation/expected_loss/protection_floor | 时间线应按期有序；仅计可信到货，已在途与本轮采购避免重复 |

库存位定义与时间线由计划人员核对。这一快速入口不从几个历史点自动猜需求分布，也不产生未经验证的缺货概率。

## 提交前四项核对

1. 同一对象、同一业务窗口、同一单位与币种。
2. 缺失、不适用、明确为零分别处理；不适用字段在该简化模型中需确认可填 0，否则改用专业模型。
3. 汇总与来源对账，记录差额与原因；未平账部分不得升级为确定结果。
4. 保留来源引用、假设、数据截点和授权范围，报告不含凭证与个人身份。
