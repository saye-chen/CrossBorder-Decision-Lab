# F02 本地化与国家校准底座：开发前蓝图与联合评审文档

> 文档编号：`F02-BR-2026-08-11-01`
>
> 蓝图版本：`F02-BLUEPRINT-1.0`
>
> 状态：`implemented_controlled_pilot`
>
> 评审人：repository owner + Codex
>
> 当前结论：F02 是 F01 之后、D14 之前的下一建设项；完整开发前评审已经关闭全部 P0，并形成可执行工作包、迁移矩阵和发布门。评审建议 `approved_for_implementation`，但在 repository owner 明确批准前，**尚未授权实现、发布、消费者切换或外部写入**。
>
> 变更规则：实现只能发生在本文变更为 `approved_for_implementation` 后。发现对象、主权、作用域、转换、迁移或 Gate 缺口时，必须先回写蓝图与评审记录。

---

## 0. 建设顺序与事实基线

下载目录《跨境电商专业决策域后续建设方案》给出的依赖顺序是：

```text
F01 实验与因果评估 → F02 本地化与国家校准 → D14 综合经营诊断与生命周期决策
```

评审启动时的仓库事实与该方案执行看板存在时间差：F01 已成为 `current` 并完成 L1—L3，F02 与 D14 当时仍为 `planned`。因此本轮选择 F02，不重新建设 F01，也不提前完整实施 D14；实现完成后的当前状态以基础能力注册表和发布审计为准。

F02 的任务不是新增一套“国家常识”，而是把分散在 D01—D13、PPFC 临时合同和 ERDG 公共校验中的本地化能力统一为可验证、可迁移、可失效、可回滚的共享底座。

## 1. 评审目标与完成定义

### 1.1 本轮必须回答

1. F02 拥有哪些共享资格判定权，明确不拥有哪些业务或专业主权？
2. 国家、管辖区、平台站点、主体、店铺、SKU、路线、语言和时点如何组成规范作用域？
3. 稳定 Profile、动态事实、转换参数和专业结论如何分离？
4. 币种、单位、时区、结算周期和已批准税口径如何确定性转换与复算？
5. 跨市场迁移等级如何统一，未知、过期、冲突和不可比输入如何降级？
6. 临时合同和 D01—D13 分散能力如何双轨迁移、接受与回滚？
7. L1、L2、L3 分别用什么机器证据关闭，L4 为什么继续保留？

### 1.2 本轮范围

- 章程、术语、主权和动作上限；
- 规范作用域、对象、状态和版本；
- 动态事实、双时间、来源、有效期、刷新和失效；
- 币种、税口径、单位、时区和结算周期转换合同；
- 国家×平台×品类×生命周期校准；
- 跨市场迁移等级、未知路由和差异报告；
- ERDG、F01、D01—D14 交接边界；
- 临时合同迁移、消费者接受和回滚；
- 确定性工具、评测、工作包和发布门；
- L4 真实案例校准、消费者生产双跑和独立复核预留。

### 1.3 明确不覆盖

- 不签发法律、税务、海关、认证、隐私或平台政策专业意见；
- 不决定市场进入、资本、价格、采购、库存、广告、Listing、内容、达人、客户或营销动作；
- 不把翻译质量等同于本地表达有效或消费者接受；
- 不维护“永远有效”的国家费率、税率、汇率、平台规则或文化结论；
- 不把国家平均值自动应用到平台、主体、店铺、SKU、路线或人群；
- 不自动抓取或写入外部平台；
- 不用合成案例关闭 L4；
- 不声明 production-ready。

### 1.4 评审完成定义

蓝图只有在以下条件全部满足后才能变更为 `approved_for_implementation`：

- P0 主权、对象、作用域、迁移等级、税务边界、Gate 和动作上限冻结；
- P1 动态事实、转换精度、状态、冲突、失效和回滚规则明确；
- D01—D13 分散资产盘点及 owner/consumer 迁移矩阵完成；
- 每个最小能力映射到 Schema、脚本、测试和消费者；
- 工作包依赖和逐包 DoD 可执行；
- L1—L3 机器发布证据和 L4 保留证据明确；
- repository owner 明确批准，不以“无异议”视为批准。

## 2. 章程与主权边界

### 2.1 唯一定位

F02 是共享的**本地化适用性、跨市场可比性和动态事实范围资格底座**。它负责固化作用域、验证事实是否适用于目标对象和时点、执行获准的确定性转换、评估跨市场迁移上限，并向各业务域交付限制和失效条件。

### 2.2 F02 拥有的共享主权

- 本地化作用域完整性与适用性资格；
- 跨市场对象、指标和参数的可比性资格；
- 动态事实的来源、时点、有效期、适用范围和冲突状态；
- 币种、单位、时区、结算周期和**已批准税口径**的转换合同；
- 跨市场迁移等级与最大可复用范围；
- 不合格输入的 `block`、`downgrade`、`request_refresh`、`request_rebuild`；
- 统一交接、版本、失效、影响闭包和迁移合同。

### 2.3 F02 不拥有的主权

- D05 拥有商业市场准入 Gate、Claim 边界和适格专业复核路由；F02 不判断法律或纳税义务；
- D06 拥有最终价格、利润、现金和税费经济影响；F02 只转换获准口径与参数；
- D01 拥有国家/平台进入与资本姿态；
- D03—D13 各自保留产品、供应、履约、页面、广告、达人、内容、营销和客户主权；
- F01 拥有因果与增量 Claim 资格；F02 只判断外部适用范围和可迁移性；
- ERDG 保留全局对象、证据、状态、血缘、参数和确定性公共计算治理；
- F02 不授权任何外部写入。

### 2.4 三层决定合同

| 层 | Owner | 输出 | 禁止越权 |
|---|---|---|---|
| 专业事实/决定层 | D01—D13 | 专业事实、参数、约束和最终决定 | 不得自行提升跨市场适用范围 |
| 本地化资格层 | F02 | 适用作用域、可比性、转换、迁移等级、失效和动作上限 | 不得重写专业结论或签发专业意见 |
| 全局治理层 | ERDG | 对象、证据、状态、参数、血缘、冲突和 Gate | 不得替代 F02 或专业域作业务判断 |

专业域决定“这个值或结论在本域代表什么”；F02 决定“它是否可在目标市场、平台、对象和时点使用，以及必须如何转换”；ERDG 决定“结构和血缘是否合格”。

## 3. 第一轮 P0 架构决定

### 3.1 P0-01：迁移采用四级结果，信息不足独立建状态

正式 `transferability_grade` 冻结为四级：

| 等级 | 名称 | 含义 | 动作上限 |
|---|---|---|---|
| L4 | `direct_within_frozen_scope` | 在完全相同且已冻结的作用域、版本和证据窗口内可直接复用 | 仅在原批准动作上限内复用 |
| L3 | `calibration_required` | 机制可能复用，但参数、表达、阈值或执行条件必须在目标市场校准 | 受控测试或补证后决定 |
| L2 | `rebuild_required` | 只能迁移问题、对象或研究框架；目标市场结论必须重建 | 分析与重新研究 |
| L1 | `prohibited` | 存在红线、结构不兼容或不可接受风险，禁止迁移 | 阻断 |

`not_assessed`、`inconclusive`、`conflicted` 和 `expired` 是评估状态，不是第五个迁移等级。没有证据时不得默认 L1，也不得默认 L3/L4。

现有 MBCM T0—T4 的迁移采用显式映射：T0→L1，T1→L2，T2/T3→L3，T4→L4；映射必须保留原等级、差异和有损说明，不静默改写历史。

### 3.2 P0-02：税口径转换与税务判断严格分离

F02 可以：

- 保存来自 D05、D06 或适格专业来源的税口径引用；
- 验证口径、币种、精度、时点、作用域和来源是否完整；
- 在已批准公式和参数下转换税含/税不含金额；
- 标记税口径冲突、过期、缺失或不可比；
- 请求 D05/D06 或适格专业人员补证和重算。

F02 不可以：

- 判断注册、申报、代扣代缴、常设机构、税收居民或海关义务；
- 根据国家默认税率推断具体交易税务处理；
- 用确定性计算结果替代法律或税务意见；
- 在专业来源缺失时选择“最可能”的税口径；
- 允许合同、店铺或 SKU 覆盖绕过法律红线。

税务输入至少区分 `tax_basis`、`tax_type`、`jurisdiction_ref`、`transaction_role`、`responsible_party_ref`、`professional_source_ref`、`effective_window` 和 `decision_time`。未能冻结这些字段时，最高 `analysis_only`，涉及执行则阻断。

### 3.3 P0-03：先求适用性交集，再解析参数优先级

作用域解析分为两个不可混淆的步骤。

**第一步：适用性交集。** 法律管辖区、销售国家、履约目的地、平台站点、经营主体、店铺、产品/SKU、路线、客户/语言、生命周期和决策时点共同决定一个事实是否适用。任一不可补偿红线不匹配即阻断，不能由更具体的商业合同覆盖。

**第二步：参数优先级。** 仅在候选均已通过适用性、批准、有效期和证据 Gate 后，按更具体的作用域选择：

```text
global
  < jurisdiction/country
  < platform_site/channel
  < legal_entity/account/store
  < category/product/SKU
  < fulfillment_route/settlement_account/customer_segment
  < approved_contractual_override
```

若两个候选在不同维度各自更具体、无法形成唯一偏序，返回 `SCOPE_CONFLICT_UNRESOLVED`，不得以数组顺序、更新时间或最高数值静默决胜。全局不可放宽红线永远优先于局部覆盖。

## 4. 规范术语与对象模型

### 4.1 必须冻结的术语

`source_market`、`target_market`、`jurisdiction`、`country`、`platform`、`platform_site`、`channel`、`legal_entity`、`store`、`product`、`sku`、`fulfillment_route`、`settlement_account`、`locale`、`language`、`currency`、`unit`、`time_zone`、`tax_basis`、`dynamic_fact`、`valid_time`、`record_time`、`decision_time`、`calibration`、`comparability`、`transferability`、`translation`、`local_expression`。

`translation_complete` 不得推导 `localization_complete`；`localization_complete` 不得推导消费者接受或经营有效；国家一致不得推导平台、主体、SKU、路线或时点一致。

### 4.2 核心对象

| 对象 | 目的 | 最小内容 |
|---|---|---|
| `localization_scope` | 固化目标对象和适用边界 | 国家、管辖区、平台站点、主体、店铺、SKU、路线、locale、生命周期、决策时点 |
| `market_profile` | 保存相对稳定背景 | 语言、文化、商业、支付、运营、服务、季节和版本 |
| `dynamic_fact_record` | 保存会变化的事实 | 值、单位、来源、业务有效时间、记录时间、到期、刷新、作用域、冲突、指纹 |
| `conversion_contract` | 冻结转换语义 | 输入/输出单位、币种、税口径、时区、精度、舍入、公式、参数引用 |
| `calibration_record` | 固化局部参数适用性 | 国家×平台×品类×生命周期、样本、方法、区间、置信度、漂移条件 |
| `comparability_assessment` | 判断对象是否可比较 | 对齐字段、差异、转换、残余不可比性、结论上限 |
| `transferability_assessment` | 判断跨市场迁移上限 | 来源/目标作用域、四级结果、机制/参数/表达差异、补证和禁止项 |
| `localization_handoff` | 供各域消费 | 当前结论、适用范围、转换结果、限制、动作上限、失效和请求 |
| `migration_record` | 管理临时/分散能力迁移 | 字段映射、损失、同输入双轨、差异、接受、切换、回滚 |
| `reproducibility_bundle` | 复算和审计 | 输入、证据、参数、代码、环境、版本、哈希、结果和偏差 |

### 4.3 通用字段

所有规范对象至少包含：`schema_version`、`object_id`、`object_version`、`status`、`owner`、`as_of_time`、`decision_time`、`created_at`、`updated_at`、`scope_ref`、`source_refs`、`evidence_refs`、`parameter_refs`、`lineage_refs`、`limitations`、`content_hash`、`external_write=false`。

未知、缺失、不适用、未观察、过期和冲突必须分开表达；不得用空字符串、0、国家默认值或最近一条记录代替。

## 5. 动态事实与时间治理

### 5.1 双时间最低合同

每条动态事实至少保存：

- `valid_from` / `valid_until`：事实在业务世界中的适用时间；
- `recorded_at` / `superseded_at`：系统何时知道和替换该事实；
- `verified_at`：最后核验时间；
- `decision_time`：本次决定使用事实的时点；
- `source_published_at`：来源发布或更新时点（可得时）；
- `refresh_triggers`：到期、来源更新、阈值漂移、合同变化、政策变化或人工复核。

晚到数据不得覆盖历史决策快照；更正必须生成新版本、影响闭包和选择性重算。

### 5.2 来源与冲突

来源记录至少包含发布者、来源类型、引用位置、原文 locale、采集方式、授权边界、核验者、证据等级和内容指纹。多个来源冲突时必须保留双方，按专业 owner、直接性、目标对象匹配度、时点和可复核性升级处理；不得用多数票或最新时间自动裁决专业冲突。

### 5.3 失效规则

以下任一情况必须失效或降级：

- 决策时点超出有效窗口；
- 来源撤回、内容变化或指纹漂移；
- 目标作用域变化；
- 专业 owner 撤销、替换或限制原结论；
- 转换参数、汇率、税口径、平台费率或结算日历变化；
- 新证据形成未解决冲突；
- 下游对象版本或依赖发生变化。

## 6. 转换与可比性合同

### 6.1 确定性要求

- 金额使用十进制定点语义，不以二进制浮点作为权威财务值；
- 汇率必须声明 base/quote、rate、来源、时间、精度和反向转换规则；
- 单位转换必须使用明确维度、单位版本、精度和舍入模式；
- 时区使用 IANA 标识，必须处理 DST、日期边界和本地结算截止；
- 税含/税不含转换只消费已批准税口径与公式；
- 所有转换输出保存输入哈希、参数哈希、公式版本、舍入残差和结果哈希；
- 不可逆或有损转换必须明确标记，不得声称原值可完全恢复。

### 6.2 可比性结果

`comparability_status` 冻结为：`comparable`、`comparable_after_conversion`、`partially_comparable`、`not_comparable`、`not_assessed`、`conflicted`、`expired`。

可比性只说明口径与作用域是否允许比较，不说明差异由何种动作造成；因果解释必须交给 F01。

## 7. 强制 Gate 与动作上限

### 7.1 Gate

| Gate | 核心问题 | fail 动作 |
|---|---|---|
| LQ1 `SCOPE_COMPLETE` | 目标对象、市场、平台、主体和时点是否完整？ | 补齐或阻断 |
| LQ2 `SOURCE_QUALIFIED` | 来源、授权、直接性和指纹是否合格？ | 降级/补证 |
| LQ3 `DYNAMIC_FACT_FRESH` | 动态事实是否在有效窗口内？ | 刷新/失效 |
| LQ4 `PROFESSIONAL_BOUNDARY` | 是否需要 D05/D06 或其他 owner 判断？ | 路由专业复核 |
| LQ5 `CONVERSION_REPRODUCIBLE` | 参数、公式、精度和舍入是否可复算？ | 阻断转换 |
| LQ6 `COMPARABILITY` | 作用域、口径和时间能否比较？ | 降级/阻断比较 |
| LQ7 `TRANSFERABILITY` | 机制、参数、表达和执行条件能否迁移？ | 校准/重建/禁止 |
| LQ8 `CONFLICT_RESOLVED` | 来源、作用域、owner 或参数冲突是否解决？ | 阻断确定结论 |
| LQ9 `CONSUMER_ACCEPTED` | 下游是否接受版本、差异和动作上限？ | 不得切换 |
| LQ10 `ROLLBACK_READY` | 旧读、重算和回滚是否真实可用？ | 不得切换 |

### 7.2 不可补偿阻断

- 法律、税务、平台政策或安全红线冲突；
- 未知目标国家/管辖区却输出确定执行结论；
- 过期事实冒充当前事实；
- 税、币种、单位或时间不可复算；
- 不可比较输入被强制合并；
- 单一市场结果无证据复制到另一市场；
- 翻译正确替代消费者接受或经营有效；
- 迁移差异未解释即切换；
- 任何外部写入被启用。

### 7.3 动作上限

| 状态 | 最大动作上限 |
|---|---|
| `not_assessed / expired / conflicted / blocked` | `analysis_only` 或补证，不得执行 |
| `L2 rebuild_required` | 重新研究和设计 |
| `L3 calibration_required` | 受控测试，仍需业务 owner 批准 |
| `L4 direct_within_frozen_scope` | 不超过来源决定原有动作上限 |

F02 的任何通过结果都不自动授权业务动作。

## 8. 跨域接口与消费者迁移

### 8.1 与 F01

F01 输出因果效果及其原始适用环境；F02 判断目标环境是否处于相同作用域或需要校准、重建。F02 不得提升 CE 等级；外部适用性不足时可以进一步限制 Claim 和动作上限。

### 8.2 与 D05、D06 和 ERDG

- D05 提供准入、Claim、专业复核和动态规则边界；
- D06 提供价格、利润、现金及获准税费经济语义；
- F02 提供目标作用域、事实新鲜度、转换和跨市场适用性；
- ERDG 提供统一对象、证据、参数、状态、血缘和确定性公共校验。

同一能力不得形成第二权威实现。ERDG 现有单位/币税/时间校验应扩展或由 F02 调用，不复制成语义分叉的平行内核。

### 8.3 临时合同迁移

`F02-temporary-localization-contract-v1` 采用：

```text
inventory → shadow → dual_run → cutover_ready → cutover
                                           ↘ rolled_back
                         legacy readable → retired after acceptance window
```

每个字段必须记录来源字段、目标字段、转换、损失等级、关键性、owner 和验证方法。双轨必须使用相同输入快照，并比较作用域、币种、税口径、单位、时区、结算、动态规则、状态、动作上限和结果哈希。

目标证据更弱、关键字段不等价、差异未解释、消费者未接受或回滚不可用时，不得切换。

### 8.4 D01—D13 消费者接受

每个消费者必须独立证明：

- 能生成和读取版本化 `localization_handoff`；
- 仍保留自身专业主权；
- 不会提升来源 Claim、迁移等级或动作上限；
- 未知、过期、冲突和部分失败能够失败关闭；
- 同输入双轨差异可解释；
- 回滚后可恢复旧读和选择性重算；
- 接受仅限 `controlled_pilot`，不代表生产批准。

## 9. Schema、工具与目录蓝图

正式实施时建议建立 `localization-country-calibration/`，但在发布前不得创建可调用根 `SKILL.md`。最小 Schema：

- `localization-scope.schema.json`
- `market-profile.schema.json`
- `dynamic-fact-record.schema.json`
- `conversion-contract.schema.json`
- `calibration-record.schema.json`
- `comparability-assessment.schema.json`
- `transferability-assessment.schema.json`
- `localization-handoff.schema.json`
- `migration-record.schema.json`
- `consumer-acceptance.schema.json`
- `reproducibility-bundle.schema.json`

最小确定性工具：作用域校验、动态事实新鲜度、参数解析、币种/单位/时间转换、税口径转换、可比性评估、迁移评级、交接构建、影响闭包、双轨差异、消费者接受和回滚验证。

## 10. 评测与发布门

### 10.1 测试分类

- Schema 正常、边界、失败和附加字段拒绝；
- 作用域交集、偏序冲突和不可放宽红线；
- 时点边界、DST、跨日、过期、晚到和追溯更正；
- Decimal、汇率方向、舍入、单位维度和税口径复算；
- 未知市场、未知平台、未知 locale 和未知主体；
- 来源冲突、owner 冲突和动态事实漂移；
- 四级迁移 Golden 与反例；
- 临时合同字段映射、双轨、差异、切换和回滚；
- D01—D13 消费者契约、对抗和越权测试；
- 多国、多平台、多币种和部分失败跨域压力测试；
- 变形、性质、突变和证据包防篡改测试。

### 10.2 L1 Structure

- 目录、入口、引用、版本、路由和注册表完整；
- 规划期失败关闭，发布前不暴露可调用入口；
- 无死链、临时产物、秘密和不必要本机路径；
- 所有专业文件可由入口直接或条件路由。

### 10.3 L2 Contract

- 对象、作用域、证据、时间、转换、状态、版本、迁移和动作 Schema 可验证；
- 未知、缺失、过期、冲突、部分失败和幂等可测试；
- 输入变化触发正确影响闭包和选择性重算；
- 越权、不可比、无效状态和血缘污染被阻断；
- 临时合同双轨迁移和回滚通过；
- D01—D13 消费者合同全部接受。

### 10.4 L3 Expert

- 动态事实、作用域、转换和迁移结论由适格方法或确定性模型支持；
- 正常、边界、失败、对抗、极端、性质和跨域测试齐全；
- 每个独立场景有 Golden 和反例；
- 报告包含原文、转换、差异、反证、未知、动作上限、刷新、停止和回滚；
- 独立专业复核检查税务、法律、语言文化、数据时间和跨市场迁移边界；
- 不能用合成通过声称真实市场有效。

### 10.5 L4 保留门

L4 至少需要授权真实市场案例、原始来源指纹、目标市场专业复核、真实双轨、消费者接受、转换误差、实际结果、偏差、事故、独立非实现者复核、版本对照和漂移再验证。本轮不得关闭。

## 11. 实施工作包与逐包 DoD

| WP | 工作包 | 完成定义 |
|---|---|---|
| WP-00 | 资产盘点 | D01—D13、PPFC 临时合同、ERDG 能力逐项登记 owner、对象、公式、状态、测试和迁移处置 |
| WP-01 | 章程与术语 | 主权矩阵、术语表、误用和禁止推导机器可检查 |
| WP-02 | 对象与作用域 | 规范对象、作用域交集、偏序和冲突测试通过 |
| WP-03 | 动态事实 | 双时间、来源、有效期、刷新、失效和更正链通过 |
| WP-04 | 转换内核 | 币、单位、时区、结算和获准税口径确定性复算通过 |
| WP-05 | 校准与迁移 | 四级迁移、校准记录、未知路由和跨市场反例通过 |
| WP-06 | Gate 与动作上限 | 不可补偿 Gate、降级、部分失败和越权突变被阻断 |
| WP-07 | 交接与 ERDG/F01 | 统一 handoff、Claim 不升级、影响闭包和版本失效通过 |
| WP-08 | 临时合同迁移 | 全字段映射、同输入双轨、差异、切换和回滚工具通过 |
| WP-09 | 消费者适配 | D01—D13 独立适配、接受、失败关闭和回滚通过 |
| WP-10 | 专家评测 | Golden、失败、对抗、极端、性质、跨域和突变证据齐全 |
| WP-11 | 发布审计 | L1—L3 机器门、证据包和注册表状态一致，L4 保持开放 |

关键路径：`WP-00 → WP-01 → WP-02 → WP-03/WP-04 → WP-05/WP-06 → WP-07 → WP-08 → WP-09 → WP-10 → WP-11`。

## 12. 评审关闭项与实现期控制项

### 12.1 已冻结 P0

- P0-01：四级迁移结果，未评估/冲突/过期独立建状态；
- P0-02：F02 只转换已批准税口径，不判断税务义务；
- P0-03：先求适用性交集，再解析参数优先级；红线不可被局部覆盖。

### 12.2 已关闭 P0

| 优先级 | 原开放项 | 关闭结论与证据 |
|---|---|---|
| P0 | D01—D13 分散资产与 owner/consumer 迁移矩阵 | 已在 `f02-capability-inventory-and-migration-review.md` 逐域冻结 `adopt/wrap/migrate/retain_owner/retire/reject` |
| P0 | 正式对象、状态机和错误代码 | 10 个对象在本文冻结；对象/迁移状态机和 22 个稳定错误码在资产评审中冻结 |
| P0 | ERDG 与 F02 转换内核的单一权威归属 | ERDG 拥有无业务语义 primitive；F02 拥有本地化资格与转换编排；专业域拥有参数和业务语义 |

### 12.3 实现期必须关闭的 P1

| P1 | 冻结方向 | 必须由何种证据关闭 |
|---|---|---|
| locale、语言变体、书写系统、数字/日期格式和翻译血缘 | 使用 BCP 47/Unicode CLDR 兼容标识；原文、译文、审校和版本分离 | WP-01/02 Schema、Golden 与反例 |
| 汇率三角转换、反向转换、舍入残差和历史重算 | Decimal；直接币对优先；三角路径显式且保留每段来源；不静默回写历史 | WP-04 性质、变形和独立复算测试 |
| 文化/消费者接受证据和 F01 触发 | Profile 只存假设/观察；效果与增量必须进入 F01；本地专业审校不等于经营效果 | WP-05/07 联合合同及消费者测试 |
| 动态事实刷新期限 | 由来源、owner、事实类别和风险决定，不提供无证据全局默认有效期 | WP-03 refresh policy 与过期对抗测试 |
| 高频市场校准卡 | v1 只交付空模板与已验证实例格式，不内置声称当前的国家事实 | WP-05 模板、无默认值测试和发布审计 |

这些 P1 已有不可更改的方向，但具体字段、算法和测试必须在对应工作包关闭；任何一项未关闭都阻断 L2/L3，不能降为普通 backlog。

## 13. 需求追踪与完整评审结论

### 13.1 需求到实现证据追踪

| 需求族 | 规范对象 | 预期工具 | 必测证据 | 工作包 |
|---|---|---|---|---|
| 章程与主权 | 所有对象通用字段 | sovereignty/entry validator | 越权与第二权威突变 | WP-01 |
| 目标作用域 | localization_scope | scope validator/resolver | 交集、偏序、冲突、红线 | WP-02 |
| 稳定市场背景 | market_profile | profile validator | translation≠localization、unknown | WP-02/05 |
| 动态事实 | dynamic_fact_record | freshness/conflict/invalidation | 双时间、过期、漂移、晚到 | WP-03 |
| 转换 | conversion_contract | currency/unit/time/tax-basis converters | Decimal、DST、维度、舍入、复算 | WP-04 |
| 校准 | calibration_record | calibration validator | 适用范围、样本、漂移、无默认值 | WP-05 |
| 可比性 | comparability_assessment | comparability evaluator | 转换前后、部分可比、禁止聚合 | WP-05 |
| 跨市场迁移 | transferability_assessment | transfer grader | L1—L4 Golden、状态分离、不得升级 | WP-05/06 |
| Gate 与动作 | localization_handoff | handoff builder/validator | 不可补偿阻断、动作上限 | WP-06/07 |
| 影响与失效 | handoff/reproducibility bundle | invalidation closure | 选择性重算、历史不覆盖 | WP-03/07 |
| 临时合同迁移 | migration_record | mapper/diff/cutover/rollback | 同输入双轨、差异、回滚 | WP-08 |
| 消费者接受 | consumer acceptance | domain adapters | 13/13 独立接受与附加断言 | WP-09 |
| 发布完整性 | reproducibility_bundle | release validator | Golden/失败/对抗/性质/突变/哈希 | WP-10/11 |

每项需求必须至少有一个规范对象、一个可执行验证入口和一个失败案例。只有文档、只有 Schema 或只有 happy-path 脚本均不能关闭工作包。

### 13.2 独立评审角色

L3 至少需要与实现者分离的复核视角覆盖：

- 数据/时间与确定性转换；
- 法律税务专业边界；
- 语言、文化与消费者接受边界；
- 跨市场迁移、外部有效性和 F01 接口；
- ERDG 血缘、状态、影响闭包和发布完整性。

仓库 owner 可以接受工程发布，但不能用 owner 接受替代需适格专业人员签发的法律、税务或其他专业事实。

### 13.3 当前评审结论

F02 开发前完整评审已经完成：主权、对象、作用域、动态事实、转换边界、四级迁移、状态、错误码、Gate、消费者、迁移、回滚、测试和 L1—L4 发布门均已形成可执行约束；WP-00 资产盘点及三个剩余 P0 已由 `f02-capability-inventory-and-migration-review.md` 关闭。

评审结论为：**建议批准进入 WP-01—WP-11 实现**。在 owner 明确批准前仍保持 `review_complete_pending_owner_approval`；批准后只取得受控实现授权，不取得发布、L4、production-ready、消费者生产切换或外部写入授权。

## 14. 联合评审记录

| 日期 | 参与者 | 结论 | 授权上限 |
|---|---|---|---|
| 2026-08-11 | repository owner + Codex | 确认 F02 为下一建设项并继续评审 | 开始蓝图与 P0 评审，不授权实现 |
| 2026-08-11 | Codex | 冻结 P0-01—P0-03，形成蓝图 0.1 | 仅允许继续 WP-00 盘点与迁移设计 |
| 2026-08-11 | Codex | 完成 WP-00、关闭剩余 P0、形成蓝图 1.0 | 建议进入实现，等待 owner 明确批准 |
| 2026-08-11 | repository owner | 明确批准按蓝图和审计方案实现 | 授权 WP-01—WP-11 受控实现；不授权 L4、生产切换或外部写入 |
