# F02 能力资产盘点、权威分工与迁移评审

> 文档编号：`F02-INVENTORY-2026-08-11-01`
>
> 状态：`review_complete`
>
> 用途：关闭 `F02-BLUEPRINT-0.1` 的 WP-00 与三个剩余 P0；本文是开发前评审证据，不是实现清单或发布证明。

## 1. 盘点方法与处置词典

盘点范围覆盖 F02 的 13 个专业消费者、F01、ERDG、PPFC 临时本地化合同和治理注册表。处置仅使用：

- `adopt`：语义和边界适合作为 F02 规范输入；
- `wrap`：保留原 owner，以 F02 标准交接包封装；
- `migrate`：临时或分散共享语义迁入 F02；
- `retain_owner`：能力必须留在专业域，F02 只验证适用性；
- `retire_after_acceptance`：双轨和回滚窗口关闭后退役旧共享入口；
- `reject`：不得迁入 F02 或不得继续作为权威能力。

文件中提及国家或本地化不等于具备正式 F02 能力；只有对象、作用域、证据、状态、转换或迁移规则明确且可验证的资产才进入迁移范围。

## 2. 逐域资产与处置矩阵

| ID | 当前资产与主要来源 | 当前价值 | 处置 | F02 边界与迁移要求 |
|---|---|---|---|---|
| D01 CIDM | `country-localization.md`、`country-routing-universal.md`、`country-calibration.md`、平台国家卡 | 国家路由、进入准备度、跨国比较、动态核验纪律 | `wrap + retain_owner` | 进入/资本姿态和国家评分留 D01；作用域、事实新鲜度、转换、可比性改读 F02；文档中的参考区间不得迁为当前事实 |
| D02 CIM | Skill 与评测中的国家/平台竞争范围 | 外部竞争事实按国家平台建档 | `wrap + retain_owner` | 竞争事实和变化归因留 D02；F02 校验目标市场、时点、locale 和跨市场可比性，不把公开代理信号升级为本地后台事实 |
| D03 PIPM | `localization-profile.schema.json`、`d04-d05-localization-professional-contracts.md`、临时迁移 Schema | 四层本地化、翻译与本地化分离、专业问题路由、lossless/lossy/unmapped | `adopt + migrate` | 四层语义和迁移纪律纳入 F02；产品适配要求仍归 D03；原 Profile 作为消费者侧对象保留，不成为第二套共享 Profile |
| D04 SPPQ | `cross-domain-migration.md` 及动态规则字段 | 供应/制造事实、辖区和规则时点、临时合同双轨 | `wrap + retain_owner` | 制造质量事实留 D04；F02 提供市场/路线作用域和动态事实外壳；D04 不得自证合法或税务正确 |
| D05 LTMA | `dynamic-rule.schema.json`、专业意见、准入 Gate、辖区/对象/时间覆盖 | 法律税务 IP 平台规则的专业来源、Claim 和准入边界 | `wrap + retain_owner` | D05 永远拥有专业含义和准入结论；F02 只消费已批准摘要、校验适用范围和新鲜度；拒绝迁移专业判断算法与法律红线主权 |
| D06 PPFC | 临时本地化合同、动态参数、迁移 Schema、确定性财务模型 | 币税单位时区/结算输入、双时间、来源指纹、参数优先级、双轨回滚 | `migrate + retain_owner + retire_after_acceptance` | 共享作用域/新鲜度/转换外壳迁 F02；价格利润现金和参数经济语义留 D06；临时合同在 13/13 接受和回滚窗关闭后退役 |
| D07 LIFD | `data-contract-and-automation.md` | 国家、仓、路线、单位、币种、税口径、时区、有效期和部分失败 | `wrap + retain_owner` | 物流路线、库存和履约能力留 D07；F02 校验国家/路线/时点和单位可比性，不选择物流方案 |
| D08 PLCO | 数据合同、平台专家卡、迁移清单 | 平台/国家/店铺/Listing/SKU/设备/页面时点和 Claim 适用范围 | `wrap + retain_owner` | 页面与转化决定留 D08；F02 统一平台站点、locale、动态规则和目标作用域；页面字段映射仍由 D08 接受 |
| D09 AAMO | 数据合同、平台规则卡和国家币税时区窗口 | 广告对象、平台归因账、成熟利润账、国家平台动态机制 | `wrap + retain_owner` | 广告预算、出价、诊断和测量留 D09；F02 校验地域/账户/币税时点；因果资格继续由 F01 判定 |
| D10 CAPM | `platform-country-routing.md`、合同/权利 Schema | 国家、平台、账号、结算、披露、权利、动态规则新鲜度 | `wrap + retain_owner` | 达人/联盟商业与权利台账留 D10；F02 统一作用域与规则新鲜度，不判断合同法律效力 |
| D11 VLB | `localization-and-compliance.md` | 语言/文化/场景适配、内容本地化层级、验证框架 | `wrap + retain_owner + reject_stale_facts` | 内容机制和创意改造留 D11；市场画像只作假设；硬编码法规/偏好/阈值不得迁为 F02 当前事实，效果验证必须路由 F01 |
| D12 MBCM | `country-calibration-contract.md`、`localization-transfer-and-unknown-routing.md`、S11 | K0—K6、T0—T4、preserve/adjust/add/remove/block、未知路由 | `adopt + wrap + retain_owner` | 迁移思想映射到 F02 四级结果；品牌/GTM/活动主权留 D12；旧 T 等级保留原值和有损映射 |
| D13 CIG | 身份、事件、授权模型和市场用途边界 | market/channel/store、event/ingest 双时间、授权按市场用途生效 | `wrap + retain_owner` | 客户身份、授权、CLV 和触达资格留 D13；F02 校验市场/locale/时点；禁止跨市场继承个人授权或触达资格 |
| F01 ECAE | 因果 handoff、外部有效性、transportability 与 CE0—CE5 | 因果 Claim、目标总体、环境适用范围和迁移证据 | `wrap + retain_owner` | CE 等级归 F01；F02 可收窄外部适用范围但不得升级 CE；目标市场效果需 F01 识别与估计 |
| ERDG | 单位币税时间校验、参数解析、证据/状态/血缘/影响闭包 | 公共结构与确定性治理 | `adopt + shared_kernel` | ERDG 保留通用 primitive；F02 拥有本地化编排和资格语义；禁止复制两个不同结果的公共转换内核 |
| 治理注册表 | foundation registry、domain registry、release/maturity | 规划/当前状态与消费者拓扑 | `adopt` | 实现期间保持 F02 `planned`；L1—L3 发布证据闭合后一次性切换 `current/controlled_pilot` |

## 3. 单一权威能力分工

| 能力 | 语义 Owner | 计算/校验 Owner | F02 行为 | 禁止的第二权威 |
|---|---|---|---|---|
| 国家/平台进入与资本姿态 | D01 | D01 | 提供作用域、可比性和迁移上限 | F02 输出 Go/No-Go |
| 法律、税务、IP、平台准入 | D05/适格专业人 | D05 | 校验辖区、对象、时间、新鲜度并路由复核 | F02 推断税务义务或合法性 |
| 价格、利润、现金 | D06 | D06 | 转换已批准参数和口径 | F02 自建第二利润模型 |
| 物流、库存、履约 | D07 | D07 | 校验路线/地域/单位/时点 | F02 选择路线或补货 |
| 页面、广告、达人、内容、营销、客户 | D08—D13 | 对应域 | 校验 locale、市场、动态规则和迁移等级 | F02 重写专业结论 |
| 因果/增量 Claim | F01 | F01 | 判断目标环境是否仍适用并可收窄 | F02 升级 CE 或估计效果 |
| Decimal、时间解析、哈希、通用数量元数据 | ERDG | ERDG shared primitive | 复用，不分叉 | F02 复制不同舍入/解析规则 |
| 作用域交集、动态事实新鲜度、跨市场可比性和迁移等级 | F02 | F02 | 规范权威 | 任一消费者自升等级或绕过 Gate |
| 业务专用参数选择 | 对应专业域 | 对应专业域 | 先做适用性过滤，返回候选和冲突 | F02 以通用优先级替代专业选择逻辑 |

公共计算的技术归属冻结为：ERDG 提供无业务语义的 Decimal、时间、哈希、数量和版本 primitive；F02 调用这些 primitive 实现本地化作用域、转换合同、可比性和迁移资格；D05/D06 等 owner 提供专业参数与公式。相同输入在任一调用路径必须产生相同公共计算结果和哈希。

## 4. 规范状态机

### 4.1 对象状态

```text
draft
  → evidence_pending
  → qualified
  → calibrated
  → accepted_for_controlled_use
  → handed_off
  → superseded / expired / invalidated / retired
```

旁路状态：`blocked`、`conflicted`、`inconclusive`、`refresh_required`、`rebuild_required`、`rollback_required`。

禁止转移：

- `draft/evidence_pending → handed_off`；
- `expired/conflicted/invalidated → accepted_for_controlled_use`；
- 未通过消费者接受进入 `cutover`；
- 新版本覆盖旧版本而没有 supersedes、影响闭包和历史快照；
- 回滚后继续把目标合同标为当前权威。

### 4.2 迁移状态

```text
inventory → shadow → dual_run → cutover_ready → cutover → retired
                                    ↘ blocked
                         cutover → rolled_back → dual_run
```

`cutover_ready` 要求字段映射、差异、13/13 消费者接受、回滚演练和证据哈希全部通过。`retired` 只能在回滚窗口关闭且 owner 明确接受后进入。

## 5. 规范错误码

| 类别 | 错误码 | 含义与强制动作 |
|---|---|---|
| 作用域 | `SCOPE_INCOMPLETE` | 缺少必要目标维度；补齐前不得确定判断 |
| 作用域 | `SCOPE_NOT_APPLICABLE` | 事实不适用于目标对象或时点；拒绝使用 |
| 作用域 | `SCOPE_CONFLICT_UNRESOLVED` | 多维候选无法形成唯一偏序；交 owner 处理 |
| 证据 | `SOURCE_UNQUALIFIED` | 来源/授权/直接性不足；降级或补证 |
| 证据 | `SOURCE_FINGERPRINT_DRIFT` | 来源内容变化；失效并重核 |
| 时间 | `DYNAMIC_FACT_EXPIRED` | 决策时点超出有效期；刷新 |
| 时间 | `VALID_RECORD_TIME_INCONSISTENT` | 业务时间和记录时间矛盾；阻断当前化 |
| 转换 | `CURRENCY_PAIR_MISMATCH` | 汇率方向或币对不匹配；阻断计算 |
| 转换 | `UNIT_DIMENSION_MISMATCH` | 不同物理维度不可转换；阻断 |
| 转换 | `TIMEZONE_UNRESOLVED` | IANA 时区或 DST/截止不明确；阻断时间聚合 |
| 转换 | `ROUNDING_POLICY_MISSING` | 权威金额缺精度或舍入规则；阻断 |
| 税务 | `TAX_BASIS_UNAPPROVED` | 税口径没有 owner/专业来源；只允许补证 |
| 税务 | `PROFESSIONAL_REVIEW_REQUIRED` | 涉及专业判断；路由 D05/适格人员 |
| 比较 | `COMPARABILITY_NOT_ESTABLISHED` | 口径/作用域不能对齐；禁止聚合或排名 |
| 迁移 | `TRANSFER_NOT_ASSESSED` | 信息不足；不得默认迁移等级 |
| 迁移 | `TRANSFER_REBUILD_REQUIRED` | 只可迁移问题/结构；目标结论重建 |
| 迁移 | `TRANSFER_PROHIBITED` | 红线或结构不兼容；阻断 |
| 冲突 | `OWNER_CONFLICT_UNRESOLVED` | 专业 owner 结论冲突；F02 不裁决内容 |
| 消费者 | `CONSUMER_ACCEPTANCE_MISSING` | 未接受；不得切换 |
| 回滚 | `BLOCKED_ROLLBACK_UNRESOLVED` | 找不到唯一有效回退；阻断动作 |
| 越权 | `ACTION_CEILING_EXCEEDED` | 下游动作超过来源/F02 上限；拒绝 handoff |
| 外部 | `EXTERNAL_WRITE_FORBIDDEN` | F02 写操作恒定禁止 |

错误码必须稳定、机器可断言并携带 object/scope/evidence/version refs；不得只输出自由文本。

## 6. 消费者验收矩阵

每个 D01—D13 消费者都必须通过以下共同断言：

1. 接受唯一版本化 `localization_handoff`，验证 schema、content hash 和 lineage；
2. 只读取与自身业务用途相关字段，不取得 F02 或其他域主权；
3. 不升级 `comparability_status`、`transferability_grade`、专业 Claim 或 `action_ceiling`；
4. 对 unknown、expired、conflicted、partial 和 invalidated 失败关闭；
5. 同输入临时/正式双轨保留 source/target 结果、字段差异和解释；
6. 输入、参数、作用域或 owner 结论变化时触发选择性重算；
7. 回滚恢复旧读和旧 current state，不只回滚代码；
8. 外部写入保持 false；
9. 合成 fixture 接受只证明受控兼容，不证明生产效果；
10. 每域至少具备 Golden、失败、越权、过期、冲突和回滚案例。

各域附加断言：

| 域 | 附加验收断言 |
|---|---|
| D01 | 不因可比性通过自动改变国家评分、Gate 或资本姿态 |
| D02 | 不把跨市场相似信号写成目标市场已确认竞争事实 |
| D03 | 翻译完成不升级产品本地化或专业准入状态 |
| D04 | 制造通用性不推导目标市场合法或可生产放行 |
| D05 | F02 转换结果不替代专业意见、准入 Gate 或 Claim 边界 |
| D06 | F02 不改写价格、利润、现金或税务经济语义；必须由 D06 重算 |
| D07 | 单位/路线可比不授权补货、调拨或履约承诺 |
| D08 | locale/规则通过不授权页面发布或 Claim 使用 |
| D09 | 平台归因和跨市场表现不升级净增量，CE 继续由 F01 控制 |
| D10 | 国家平台匹配不证明合同、披露、权利或结算合法有效 |
| D11 | 内容机制可迁移不证明效果量可迁移；目标效果走 F01 |
| D12 | 品牌机制迁移不授权活动、资源或市场总姿态 |
| D13 | 市场相同不继承个人身份、授权、敏感数据或触达资格 |

## 7. 迁移映射与退役决定

### 7.1 PPFC 临时合同

| 临时字段 | F02 目标对象 | 迁移等级 | 处置 |
|---|---|---|---|
| `country_code/platform_id` | `localization_scope` | explainable | 扩展 jurisdiction/platform_site/entity/store/route 等维度；原值保留 |
| `currency_code/fx` | `conversion_contract + dynamic_fact_record` | lossless after normalization | 来源字符串升级结构化来源；无法补齐指纹则不得 current |
| `tax` | `conversion_contract + professional_source_ref` | material | 旧字段不足以证明税务语义；只迁为待专业确认输入 |
| `unit_system` | `conversion_contract` | explainable | 总体单位系统不能替代字段级单位；需逐数量迁移 |
| `time_zone` | `localization_scope/conversion_contract` | lossless if IANA | 非 IANA 或 DST 不明则阻断 |
| `settlement_calendar` | `dynamic_fact_record/conversion_contract` | explainable | 补 calendar timezone、business-day rule、holiday source |
| `dynamic_rule` | `dynamic_fact_record` | explainable/material | 补发布者、作用域、双时间、证据指纹和冲突状态 |
| `localization_status` | F02 object state | explainable | 显式状态映射，不把 validated 迁成专业批准 |
| `evidence_grade/action_ceiling` | `localization_handoff` | lossless ceiling | 只能保持或收窄 |
| `validity/lineage` | 各规范对象 | explainable | runtime 从 PPFC 改 LCCA，同时保留 source runtime lineage |
| `external_write` | 所有对象 | lossless | 必须恒为 false |

### 7.2 退役纪律

- `F02-temporary-localization-contract-v1` 在 cutover 前继续可读，但不得扩展成第二套新语义；
- D06 可继续拥有内部财务参数对象，不再拥有共享 F02 合同入口；
- 各域硬编码市场画像、费率、法规、阈值和偏好不得迁入权威动态事实库；
- 旧 T0—T4、本地化层级和准备度保留为 owner 历史字段，通过显式 adapter 映射；
- 没有 13/13 接受、实际回滚演练和 owner 接受记录，不得声明 retired。

## 8. 评审关闭结论

WP-00 的开发前盘点已完成。三个剩余 P0 结论如下：

1. D01—D13 的资产、owner、消费者和迁移处置已逐域冻结；
2. 正式对象状态机与稳定错误码已冻结到评审级；实现时 Schema 不得改变语义；
3. ERDG/F02/专业域的单一权威函数分工已冻结：ERDG primitive、F02 本地化资格与转换编排、专业域业务语义。

仍需在实现阶段以 Schema、脚本和测试证明这些决定，但不存在阻止进入实现的未决 P0。P1 必须按工作包关闭，不得被“后续优化”无限延期。
