# 对象、生命周期与状态模型

## 目录

1. 主权与建模原则
2. 核心对象
3. 身份、范围与版本
4. 生命周期
5. 状态机
6. 动态参数双时间
7. 关系与守恒
8. 失败、重算与审计

## 1. 主权与建模原则

D06/PPFC 拥有价格、统一经济口径、贡献利润、财务边界和现金承受力结论。它消费其他业务域的事实与候选动作，不取得资本、物流、广告、页面、达人、营销、客户、法律税务或外部执行主权。

对象模型遵守：

- 事实、假设、场景和结论分离；
- 业务对象、规则和决策分别版本化；
- 业务有效时间与系统记录时间分离；
- 聚合必须保留子对象、权重、覆盖率、缺失率和守恒；
- 历史版本只追加或替代，不原地改写；
- 未对齐范围、时间、单位、币税和版本的结果不可直接比较。

## 2. 核心对象

| 对象 | 身份 | 最小职责 |
|---|---|---|
| Economic Subject | `subject_id + subject_type + version` | SKU、订单、批次、活动、客户、国家平台组合等经济边界 |
| Price Architecture | `price_architecture_id + market_scope + version` | MSRP、标价、成交价、渠道价、会员价和区域价 |
| Pricing Route | `pricing_route_id + business_model + objective + version` | 六维路由及主/辅定价模型选择 |
| Offer Candidate | `offer_id + channel + window + version` | 折扣、券、满减、赠品、套装或促销候选 |
| Cost Component | `component_id + cost_class + basis + version` | 产品、物流、平台、支付、税、营销、售后等成本 |
| Economic Ledger | `ledger_id + subject_id + basis + version` | 收入、成本、贡献和利润的权威经济账 |
| Cash Event | `cash_event_id + event_at + currency + version` | 流入、流出、结算、押金、退款和回款 |
| Scenario | `scenario_id + assumption_set + version` | 不行动、保守、推荐、压力和退出 |
| Financial Constraint | `constraint_id + owner + scope + version` | 预算、损失、现金、回收期和风险边界 |
| Decision | `decision_id + decision_type + version` | 价格、促销、预算、现金和风险结论 |
| Inventory Batch | `batch_id + sku + inbound_version` | 采购、样品、可售、预留、损耗和退出数量 |
| Unique Order | `order_id + order_line_id + state_version` | 唯一收入、数量、退款、履约和库存扣减 |
| Touchpoint Event | `event_id + order_id + occurred_at` | 广告、达人、视频、直播、货架等接触 |
| Channel Claim | `claim_id + order_id + method_version` | 渠道归因主张，不等于财务收入 |
| Sample Deployment | `sample_id + batch_id + creator_id + state_version` | 样品发出、签收、发布、授权、回收和结果 |
| Dynamic Parameter | `parameter_id + semantic_code + version` | 金额、费率、税率、汇率、概率、阈值和数量 |
| Rate/Tariff Rule | `rule_id + rule_type + scope + version` | 平台支付费率和物流计费规则 |
| Resolution Context | `context_id + dimensions_hash` | 规则解析所需完整业务上下文 |
| Parameter Snapshot | `snapshot_id + decision_id + content_hash` | 决策时点已解析参数包 |
| Refresh Event | `refresh_event_id + source_id + observed_at` | 到期、来源变化、替代和越阈事件 |
| Parameter Override | `override_id + target_id + approved_version` | 有范围、理由、审批、期限和回滚的覆盖 |

## 3. 身份、范围与版本

Economic Subject 必须声明：

- 对象类型、对象 ID、版本、父子关系；
- 国家、平台、店铺、渠道、生命周期和业务时间；
- SKU/变体、批次、订单、活动或客户范围；
- 币种、税口径、单位系统和数量基准；
- 数据来源、证据 IDs、内容指纹和记录时间；
- 前一版本、替代版本和退役原因。

聚合对象不得把不同层级的平均值当作子层级事实。版本改变必须生成新身份；只有完成口径桥或在同一版本下重算后才能比较。

## 4. 生命周期

| 阶段 | 含义 | 最高动作 |
|---|---|---|
| L0 Intake | 明确对象、问题、时点和最小输入 | 取证清单 |
| L1 Hypothesis | 显式假设形成初步区间 | `proposed` |
| L2 Reconciled | 收入、成本、数量、币税和时间对齐 | 候选比较 |
| L3 Modeled | 确定性计算、敏感性和压力完成 | 推荐或阻断 |
| L4 Validated | 主权输入、规则和参数已验证 | 提交业务域接受 |
| L5 Accepted | 业务域或 CIDM 接受约束 | 人工执行准备 |
| L6 Observed | 执行结果和偏差回收 | 再计算判断 |
| L7 Recalibrated | 参数或模型经审查调整 | 发布新版本 |
| L8 Retired | 过期、替代或退出 | 仅历史重放 |

L4 生命周期名称不等于系统成熟度 L4 Production。后者仍需授权真实历史回放和独立复核。

## 5. 状态机

正常路径：

`draft → proposed → validated → accepted → executed → observed → closed`

允许旁路：

- 任一前置阶段 → `inconclusive`：证据或能力不足；
- 任一非终态 → `blocked`：不可补偿门失败；
- `proposed/validated` → `rejected`：主权方拒绝；
- `validated/accepted` → `expired`：动态事实、规则或依赖过期；
- `accepted/executed/observed` → `rolled_back`：达到回滚条件；
- `closed/expired/rolled_back` → `retired`：不再作为当前结论。

恢复规则：

- `inconclusive → proposed` 需要新增证据或可用能力；
- `blocked → proposed` 需要红线解除证据和全依赖重算；
- `expired → proposed` 需要刷新、参数快照和重算；
- `rejected → proposed` 需要新版本候选；
- `rolled_back → proposed` 需要新对象版本或新场景。

禁止：

- `draft/proposed → executed`；
- `blocked → accepted/executed`；
- `expired → validated/accepted`；
- `closed/retired → executed`；
- 状态改变但无事件、责任人、时间、原因和前后版本。

## 6. 动态参数双时间

每条动态规则同时记录：

- `valid_from/valid_to`：业务事实上何时适用；
- `recorded_at/superseded_at`：系统何时知道、批准、纠正或替代。

当前计算按目标业务时间和当前已批准知识解析。历史审计使用决策时点快照，回答“当时为什么这样算”；追溯纠错使用新规则形成差异桥，不覆盖原快照。

人工覆盖是独立对象，必须绑定目标、原值、新值、范围、理由、审批、有效期和回滚。覆盖到期后重新解析当时有效的一般规则。

## 7. 关系与守恒

- 一个 Decision 绑定一个主 Economic Subject，可引用多个候选 Scenario；
- 每个 Scenario 绑定独立 Parameter Snapshot；
- 一个参数快照包含所有解析成功、缺失、过期和冲突项；
- Unique Order 是收入、退款、履约和库存扣减的去重锚点；
- Channel Claim 可多于一个，但不得增加 Unique Order 或权威收入；
- Inventory Batch 的样品、测试、预留、可售、已售、退货、损耗和期末数量必须守恒；
- Economic Ledger 与 Cash Event 分开：利润确认不等于现金收付；
- Cost Component 必须声明性质、行为、决策相关性、确认方式和分摊基数。

## 8. 失败、重算与审计

参数、规格、价格、退款、库存、费率、汇率、税、路线或模型版本变化时：

1. 记录 Refresh Event；
2. 解析受影响对象与时间窗；
3. 将依赖结论置为 `expired`；
4. 创建新 Parameter Snapshot；
5. 只重算依赖闭包；
6. 输出旧新差异和翻转项；
7. 要求相关主权域重新接受；
8. 保留原对象、原快照、原结论和回滚关系。

审计记录至少包含对象版本、状态事件、参数快照、证据指纹、计算哈希、决策责任、允许/禁止用途和实际结果回填位置。
