# 输入与批量数据规范

## 目录

- 通用字段、单品与链接
- 多候选与国家比较
- 店铺、老品与 VOC 数据
- 测款实验与数据质量

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

`id,name,country,platform,category,url,variant,price,currency,score,confidence,dimension_confidence,investment,operational_load,cash_cycle_days,supplier,redline,notes`

- `score` 必须来自同一版本基础模型；未评分时留空，先逐项评分。
- `confidence` 使用 `high/medium/low`，表示整体置信度。
- `dimension_confidence` 可填 JSON 或短文本摘要，记录七维中的确定/中等/不确定短板；缺失时必须在报告中单独补评。
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

## VOC 与竞品数据

CSV、JSON 数组或 JSONL 每条记录推荐使用：

| 字段 | 必需 | 说明 |
|---|---:|---|
| `text` | 是 | 原始评论、问答或反馈 |
| `source` | 否 | Amazon、Reddit、support、survey 等 |
| `competitor` | 否 | 品牌、产品或替代方案 |
| `rating` / `date` | 否 | 0-5 评分和原文日期 |
| `sentiment` | 否 | `positive/neutral/negative/mixed` |
| `themes` | 否 | 多标签，CSV 用 `|`，JSON 可用数组 |
| `verified` / `url` | 否 | 已购/交易信号与原文地址 |

`scripts/analyze_voc.py` 只做去重、数据质量、分布和已编码主题聚合，不自动发明标签。

## 测款实验

`scripts/evaluate_experiment.py` 输入示例：

```json
{
  "experiment": "US landing-page test v1",
  "currency": "USD",
  "spend": 300,
  "revenue": 180,
  "counts": {
    "impressions": 12000,
    "clicks": 360,
    "landing_visits": 330,
    "leads": 42,
    "add_to_cart": 20,
    "checkout_started": 10,
    "purchases": 4,
    "refunds": 0
  },
  "minimums": {"landing_visits": 300},
  "gates": [
    {"metric": "lead_rate", "operator": ">=", "threshold": 0.10, "kind": "primary"},
    {"metric": "refund_rate", "operator": "<=", "threshold": 0.10, "kind": "redline"}
  ]
}
```

率使用 0-1 小数；事先门槛必须来自当前实验的历史基线、同期对照或明确商业约束，不使用无来源的统一健康线。

## 数据质量

- 每个数字尽量附 `source`、`period_start`、`period_end` 和 `retrieved_at`。
- 百分比明确使用小数或百分数，不能混用；币种和含税口径必须统一。
- 空值保留为空，不填 0；0 表示已观察到真实零值。
- 重复候选按平台＋国家＋商品 ID＋变体去重，父子变体不得混成同一价格记录。
