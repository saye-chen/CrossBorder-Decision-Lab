# 输入与批量数据规范

## 通用字段

所有任务尽量提供：`task_id`、`scenario`、`country`、`platform`、`product_scope`、`currency`、`tax_basis`、`evidence_cutoff`、`seller_constraints`。缺失字段允许为空，但必须在报告中列为假设或数据缺口。

## 单品与链接

| 字段 | 必填 | 说明 |
|---|---|---|
| `product_name` | 是 | 品类或商品短名称 |
| `country` | 是 | 具体销售国家 |
| `platform` | 否 | 未提供时可推断 |
| `url` / `product_id` | 链接反查必填其一 | 规范链接、ASIN 或商品 ID |
| `variant` | 否 | 尺寸、颜色、数量、型号 |
| `price` / `currency` | 否 | 当前成交口径 |
| `seller_data` | 否 | 搜索量、销量、广告、退货等一手数据 |
| `constraints` | 否 | 预算、MOQ、交期、认证、重量等 |

## 多候选表格

CSV/Excel 建议字段：

`id,name,country,platform,category,url,variant,price,currency,score,confidence,investment,operational_load,cash_cycle_days,supplier,redline,notes`

- `score` 必须来自同一版本基础模型；未评分时留空，先逐项评分。
- `confidence` 使用 `high/medium/low`。
- `investment` 使用统一币种，包含启动阶段预计现金投入。
- `operational_load` 使用同一团队定义的相对尺度。
- `redline` 仅使用 `true/false`，并在 `notes` 写原因。

组合脚本 JSON 使用 [portfolio-decision.md](portfolio-decision.md) 的结构。不要把缺失投资额自动视为 0。

## 国家比较

```json
{
  "product_name": "产品",
  "candidate_countries": ["US", "JP", "DE"],
  "platforms": {"US": ["Amazon"], "JP": ["Amazon"], "DE": ["Amazon"]},
  "fulfillment": "cross_border_or_local",
  "base_currency": "USD",
  "product_spec": "same_spec_for_comparison",
  "known_costs": {},
  "constraints": {}
}
```

欧洲、东南亚等区域必须转换成具体国家后再进入比较表。

## 店铺补品与老品扩展

店铺数据至少包含：SKU、类目、价格、流量词、曝光、点击、订单、净贡献、退货、库存和关联购买。老品扩展另需原品基准期、变体、素材、供应商、MOQ、毛利和销售蚕食观察。

## 数据质量

- 每个数字尽量附 `source`、`period_start`、`period_end` 和 `retrieved_at`。
- 百分比明确使用小数或百分数，不能混用；币种和含税口径必须统一。
- 空值保留为空，不填 0；0 表示已观察到真实零值。
- 重复候选按平台＋国家＋商品 ID＋变体去重，父子变体不得混成同一价格记录。
