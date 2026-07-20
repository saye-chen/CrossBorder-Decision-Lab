# 输入、证据与 Hard Gates

## 目录

1. Diagnostic bundle
2. Evidence ledger
3. Claims
4. Gates
5. 数据质量

## Diagnostic bundle

至少包括 scope、object tree、page snapshots、product truth、approved offer、inventory/fulfillment、traffic/funnel、customer/VOC、external competition、platform rules、experiments、incidents、cross-domain handoffs。每项带来源、时间、对象、版本、权限和缺失原因。

对象主键不得只用标题。规范键组合平台、站点、商家/店铺、目录/Listing、SKU/变体、Offer、页面层和版本。比较前确认同对象、同定义、同设备/流量、同窗口。

## Evidence ledger

每条记录 `evidence_id/source_type/source_uri_or_record/object_id/page_version/observed_at/retrieved_at/fingerprint/claim_scope/allowed_uses/forbidden_uses/expiry/conflicts`。证据层：E0无证；E1公开/代理；E2授权快照；E3可复算经营数据；E4合格实验；E5成熟利润/实际结果。

同一指纹、转述或派生不得伪装独立证据。缺失与零值分开。代理量不写成后台量，相关不写成因果。

## Claims

Claims 分 observed、authorized、derived、inferred、causal。每条必须有支持、反证、适用范围、置信度和禁止用途。`causal` 至少需要 E4；经营价值再接 E5。冲突不静默平均，保留双方并降低动作上限。

## Gates

G1身份权利、G2产品真实、G3平台合规、G4 Offer/利润、G5库存履约、G6测量版本。状态仅 `pass/conditional/fail/unknown`。输出阻断原因、所需补证、允许动作和复核owner。`fail` 阻断依赖动作；`unknown` 不得升级为pass。

## 数据质量

校验有限值、非负计数、币种、税口径、时区、窗口、去重、分子分母、版本传播和缺货截尾。Q3允许具体动作；Q2给条件方案；Q1只筛查/验证；Q0只给阻断和补数。任何精确平台限制绑定平台/站点/页面/设备/证据日期。
