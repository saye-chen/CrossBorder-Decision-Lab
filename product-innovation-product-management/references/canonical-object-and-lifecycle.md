# 规范对象与生命周期

## 对象树

`enterprise → brand → product_family → product → market_product → sku_variant → sample_batch`

稳定身份与可变版本分离。每个版本记录 `valid_from`、可选 `valid_to`、`as_of_time`、`recorded_at`、属性哈希和被替代版本。D03 对象映射 ERDG canonical object；向 D06 交接时映射 product、sku 或 batch economic subject。

## PLC 生命周期

| 阶段 | 含义 | 动作上限 |
|---|---|---|
| PLC0 | 机会登记 | 取证 |
| PLC1 | 发现 | 产品假设 |
| PLC2 | 概念 | 概念筛选 |
| PLC3 | 定义 | 产品定义 |
| PLC4 | MVP | 受控原型验证 |
| PLC5 | 样品 | 样品迭代 |
| PLC6 | 试产 | 量产放行请求 |
| PLC7 | 上市版本 | 受控版本变更 |
| PLC8 | 衰退停产 | 收缩、替代或归档 |

字段固定为 `product_lifecycle_stage`。成熟度另存 `maturity_l1/l2/l3/l4`，不得从产品阶段推导。
