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

## 模块执行协议

### 对象与页面版本

- 固定平台、国家、店铺、Listing、SKU/变体、Offer、页面层、设备、流量和 page_version。
- 比较必须同对象、同定义、同窗口；缺失、零值、不可见和 not_applicable 分开。
- 保存页面快照、产品事实、授权Offer、ATP、规则和测量配置的证据指纹。

### 机制与诊断

- 依次检查可发现、可理解、可信、可选择、可购买、可履约和可测量。
- 分开标题/索引、首图/图组、详情、Offer、变体、购物车/结账与跨层一致性。
- 漏斗变化先检查流量组合、设备、价格、库存、配送和追踪版本，再解释页面机制。
- 每个主根因至少给一个替代解释和能区分两者的验证。

### 证据与约束

- G1—G6 任一 fail 不得被页面评分补偿；unknown 也不得写成 pass。
- observed/authorized/derived/inferred/causal 分层；竞品页面和单次前后变化不证明因果。
- 任何卖点、参数、认证、效果和比较声明必须回指产品事实与权利。
- 具体方案含候选文案或逐槽 Brief，不用“优化图片/提升转化”替代执行内容。

### 反事实与实验

- 比较不改版、保守修复、核心推荐和探索方案，说明依赖与禁止项。
- 实验固定单位、版本、主要指标、护栏、MDE/区间、观察窗和停止规则。
- 检查新奇效应、流量污染、并发改价/库存、跨设备和回归均值。
- 无合格实验时只称描述变化或待验证机制，不声称页面增量。

### 动作与恢复

- 动作写明页面层、字段/槽位、责任人、审批、上线顺序和传播确认。
- 给成功、停止、回滚版本、剩余暴露和实际结果回填。
- 覆盖、抑制、非法合并、身份错配或后台部分成功时先恢复对象一致性。
- 外部依赖失败时保留可验证页面事实，相关层 inconclusive，不猜隐藏字段。
- 跨域只交接证据与页面结论，不反向改变投资、库存、广告、内容或客户主权。

## input-evidence-and-gates 专属决策内核

| 维度 | 本模块要求 |
|---|---|
| 核心机制 | 产品事实、权利、规则、Offer、ATP和测量版本先于页面优化 |
| 计算或判定 | G1-G6逐门输出pass/conditional/fail/unknown和动作上限 |
| 主要失效 | unknown写pass、竞品页面当产品事实、缺失填零 |
| 决策动作 | 失败门阻断依赖改版并列补证与owner |

本节必须由该模块自己的证据和失败测试验证，不得用通用附录或其他reference代替。
