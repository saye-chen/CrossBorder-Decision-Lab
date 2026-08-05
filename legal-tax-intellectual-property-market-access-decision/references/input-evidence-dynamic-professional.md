# 输入、证据、动态事实与专业意见

## 输入门

最小输入必须同时包含：决策问题、拟议动作、规范对象、产品事实、司法辖区/国家/平台/主体/时间、用途与用户、Claim、已有来源和请求方授权。对象、范围、用途、关键产品事实或 `as_of_time` 缺失时，最高状态为 `evidence_required`。

理想输入补充完整规格、BOM、材料/成分、能源与连接、包装、供应商/工厂、样品/批次、测试报告、证书链、标签说明、营销素材、平台通知、交易结构、税务海关资料、IP 搜索和许可链、专业意见与历史事故。

零值、未知值、未提供和不适用必须分开；缺失不得静默填零。

## 证据等级

沿用 ERDG 来源类型：`observed_public`、`authorized_first_party`、`authorized_third_party`、`official_rule`、`professional_opinion`、`benchmark`、`synthetic_fixture`、`user_assertion`。

每条证据绑定来源、来源家族、授权、对象、司法辖区、用途、获取/核验/到期时间、原始指纹、支持与反对的 Claim、限制和状态。证据状态为 `current/expired/conflicted/rejected/unavailable`。

- `synthetic_fixture` 只能用于测试；
- `benchmark` 不能证明具体对象合规；
- `user_assertion` 未核验前不能关闭 Gate；
- `observed_public` 的摘要、搜索片段和机器翻译不得替代权威原文；
- 相同来源家族的重复材料不得冒充多源独立证据。

## 动态事实

规则、平台政策、税率、认证要求和名单状态必须记录发布者、来源、规则家族、版本、司法辖区、对象/用途范围、生效、核验、到期、替代关系、刷新条件和状态。

状态为 `current/scheduled/expired/superseded/conflicted/unavailable`。当前规则必须满足：核验时间不晚于 `as_of_time`、未过期、已生效、范围匹配且不存在未解决冲突。否则不得支持 clearance。

## 专业意见

外部意见必须记录主体角色、签发者身份引用、资格或授权范围、司法辖区、对象与用途、依据、利益冲突、签发/核验/到期时间、限制、结论摘要和原始证据引用。

D05 只能记录 `received/accepted_as_bounded_evidence/rejected/expired/superseded`。接受条件包括资格范围、辖区、对象、用途、时间和依据全部匹配，利益冲突已披露并妥善处理。

接受专业意见不会自动升级 Claim，也不会把 D05 变成意见签发者。专业意见与官方规则或另一意见冲突时，保持冲突并升级复核。

## 结论上限

输入不足、证据过期、规则冲突或专业意见不适用时，输出受影响字段、阻断动作、补证清单和复核责任人。未受影响事实可以保留，但不得扩大或缩小影响范围。
