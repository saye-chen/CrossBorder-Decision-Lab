# F01 实验与因果评估底座：开发前蓝图与联合评审文档

> 文档编号：`F01-BR-2026-08-10-01`
>
> 蓝图版本：`F01-BLUEPRINT-1.1`
>
> 状态：`implemented_controlled_pilot`
>
> 评审人：repository owner + Codex
>
> 评审结论：WP-00—WP-13 的 L1—L3 受控试点范围已经实施和验证；**真实业务双跑、外部独立复核、生产校准和任何外部写入仍由 L4 单独控制**。
>
> 后续开发规则：所有 F01 工作包、Schema、脚本、测试、迁移和发布判断必须逐条映射到本文档；未映射需求不得静默实现。实现发现蓝图缺口时必须先回写评审变更记录，再继续开发。

---

## 0. 为什么现在建设 F01

下载目录《跨境电商专业决策域后续建设方案》执行基线 v3.0 明确规定剩余顺序为：

```text
F01 实验与因果评估 → F02 本地化与国家校准 → D14 综合经营诊断与生命周期决策
```

因此，F01 必须先通过权威 L1—L3 发布门。F02 与 D14 的建设顺序不改变，但不得以其后续建设反向放宽 F01 的证据边界。

F01 的必要性不是“再增加一套实验知识”，而是把当前分散在 D01—D13 的实验、归因、增量、统计和经济判断统一成可验证的共享底座，防止：

- 未随机或无合格反事实却声称因果；
- 平台归因、前后变化或相关性被改名为净增量；
- 样本不足、污染、SRM、流失或提前停止被忽略；
- 统计显著替代经营价值；
- 不同域使用不兼容的效应、区间、窗口和结论等级；
- D14 将不可比、不可复现或互相冲突的结果直接汇总成经营动作。

## 1. 评审目标、范围与完成定义

### 1.1 本轮评审必须回答

1. F01 拥有什么共享主权，明确不拥有什么业务主权？
2. 哪些对象、状态、Schema、计算和 Gate 构成最小可发布内核？
3. 哪些设计允许输出何种结论等级，哪些情况必须降级或阻断？
4. 随机实验、准实验、干扰、异质性、序贯、多重比较和经济价值如何形成一致合同？
5. D01—D13 如何迁移、调用、接受和回滚 F01 结果？
6. L1、L2、L3 各自用什么机器证据关闭，L4 为什么仍然保留？

### 1.2 本轮范围

- 能力章程、主权与术语；
- 规范对象、版本和生命周期；
- 实验资格、指标、样本、分配、曝光、分析、结果、复现对象；
- 随机实验与第一版允许的准实验边界；
- SRM、污染、流失、缺失、干扰、提前停止和多重比较治理；
- 统计意义、经营意义、风险调整经济价值和动作上限；
- 结论等级、降级矩阵、不可补偿 Gate；
- D01—D14 交接合同、消费者接受和迁移；
- 确定性工具、评测体系、工作包和发布门；
- L4 真实回放所需的预留字段和证据链。

### 1.3 本轮明确不覆盖

- 不替各业务域决定广告、价格、产品、库存、客户、达人、营销或投资动作；
- 不把第一版扩张成通用统计软件或自动模型选择器；
- 不预置未经校准的“行业统一 MDE、样本量、显著性或利润阈值”；
- 不自动读取、写入或操纵任何外部平台；
- 不使用合成案例关闭 L4；
- 不声明 production-ready。

### 1.4 蓝图评审完成定义

本文档已依据下列条件完成项目级评审并变更为 `approved_for_implementation`：

- 所有 P0/P1 开放项均有明确结论或被 owner 明确接受为保留风险；
- 主权、术语、对象、状态、Gate、结论等级和动作上限冻结；
- 每个最小开发项均映射到 Schema、脚本、测试和消费者；
- D01—D13 现状盘点与迁移矩阵完成；
- 工作包依赖和逐包 DoD 可执行；
- 独立专业复核角色、范围和复核时点明确；
- owner 明确记录批准，不以“无异议”视为批准。

## 2. F01 章程与主权边界

### 2.1 F01 的唯一定位

F01 是共享的**实验设计与因果证据资格底座**。它负责：

- 固化实验/准实验协议；
- 验证识别条件与数据资格；
- 执行或复核获准的确定性计算；
- 生成效应、不确定性、诊断、经济解释和结论等级；
- 限制下游可使用的 Claim 与最大动作上限；
- 保存从问题、协议、样本、数据、代码到结果的复现血缘。

### 2.2 F01 拥有的共享主权

- 因果与增量 Claim 的资格判定；
- 实验协议完整性和分析计划一致性校验；
- 统计结论等级与降级原因；
- 共享估计量、诊断和不确定性输出合同；
- 跨域实验结果交接、版本和复现合同；
- 因果证据不足时的 `block_claim`、`downgrade_claim` 和 `request_redesign`。

### 2.3 F01 不拥有的主权

- 不决定业务问题是否值得做；
- 不决定最终业务 KPI、业务阈值或风险偏好；
- 不拥有领域动作的 Go/No-Go、预算、价格、库存、发布、触达或投资主权；
- 不替代 D06 计算最终现金与利润口径，但可消费其合格经济参数；
- 不替代 F02 处理国家、币税、时区、单位和动态事实校准；
- 不替代 ERDG 管理全局对象、证据、血缘、冲突和 Gate；
- 不因统计显著自动授权扩大、上线或停止业务动作。

### 2.4 双层决定合同

| 层 | Owner | 输出 | 禁止越权 |
|---|---|---|---|
| 因果证据层 | F01 | 设计是否合格、估计对象、效应区间、诊断、结论等级、最大 Claim | 不输出业务最终决定 |
| 业务决定层 | D01—D14 对应主权域 | 结合经济、风险、约束和策略作 Continue/Stop/Scale/Redesign 等决定 | 不得把低等级证据升级为因果或净增量 |

发生冲突时，F01 对因果 Claim 资格拥有否决权；业务域对自身动作拥有最终主权，但不得突破 F01 输出的 Claim 和动作上限。

## 3. 术语、认识论与结论等级

### 3.1 必须冻结的核心术语

`decision_question`、`treatment`、`control`、`assignment_unit`、`analysis_unit`、`exposure`、`estimand`、`ITT`、`TOT`、`ATE`、`ATT`、`incrementality`、`attribution`、`counterfactual`、`MDE`、`power`、`alpha`、`confidence_interval`、`SRM`、`attrition`、`interference`、`spillover`、`guardrail`、`sequential_monitoring`、`economic_value`、`external_validity`。

实现前必须为这些术语建立规范词典，包含定义、允许值、单位、误用示例和禁止替代词。

### 3.2 六级结论阶梯

| 等级 | 名称 | 最低含义 | 允许表达 | 禁止表达 |
|---|---|---|---|---|
| CE0 | `insufficient` | 数据或设计不合格 | 无法判断、需补证/重做 | 有效、增量、由动作造成 |
| CE1 | `descriptive` | 仅描述观察事实 | 观察到、发生了 | 相关、预测、归因、因果 |
| CE2 | `associational` | 存在统计关联 | 与……相关 | 导致、带来净增量 |
| CE3 | `predictive_or_attributed` | 可预测或按规则归因 | 预测值、平台归因值 | 因果效果、真实净增量 |
| CE4 | `causal_bounded` | 识别条件基本满足但有重要限制 | 在指定范围与假设下的因果效应 | 普遍有效、可无条件扩大 |
| CE5 | `causal_decision_grade` | 识别、诊断、精度、稳健性与经济解释均通过 | 可供指定业务决定使用的净增量区间 | 自动等同最终业务动作 |

`CE` 是 causal evidence 的专用前缀，避免与仓库既有 Claim、Calculation、Cycle 或各域自定义的 `C0—C4` 冲突。结论等级必须由机器规则和显式人工判断共同产生；不得由调用域自行改写或升级。CE4/CE5 均需保存估计对象、适用人群、时间、环境、版本和限制。

### 3.3 统计与经营双重判定

F01 输出必须将以下四件事分开：

1. `statistical_compatibility`：区间、p 值或后验量表达的数据兼容性；
2. `practical_materiality`：效应是否越过事前业务最小重要差异；
3. `economic_viability`：增量贡献利润减去实施、机会、风险和实验成本后是否可行；
4. `decision_readiness`：证据、经济和业务约束合并后是否足以支持指定动作。

任何一项不得替代另一项；“不显著”不自动等于无效，“显著”不自动等于值得做。

### 3.4 三层理论内核：识别、估计与决定

F01 的专家深度必须建立在三个不可混淆的层次上：

| 层 | 回答的问题 | 规范产物 | 典型失败 |
|---|---|---|---|
| Identification | 目标因果量能否由当前设计和观测分布识别？ | estimand、潜在结果/SCM、DAG、识别假设、可识别表达式 | 用更复杂模型掩盖不可识别 |
| Estimation | 在识别成立时，如何有限样本估计并量化不确定性？ | estimator、方差/随机化分布、区间、诊断、敏感性 | 估计器与分配单位、指标或样本结构不匹配 |
| Decision | 估计结果是否足以改变特定经营动作？ | 损失函数、价值区间、护栏、动作上限、信息价值 | p 值或后验概率直接等同业务 Go |

机器学习、贝叶斯模型、回归或大样本只能改善 Estimation；它们不能自行创造 Identification，也不能取代业务域的 Decision 主权。

### 3.5 双表示因果模型

每个 CE4/CE5 候选分析必须同时具备：

1. **潜在结果表示**：定义 `Y_i(a)`、目标总体、处理版本、estimand 和分配/选择机制；
2. **结构因果表示**：至少提供变量角色和 DAG/SCM 邻接合同，标记 treatment、outcome、pre-treatment confounder、mediator、collider、instrument、selection、proxy 和 unobserved；
3. **一致性映射**：说明 DAG 的调整集或识别路径如何对应到潜在结果假设和实际字段；
4. **不可识别报告**：若存在无法关闭的后门、选择偏差、未测混杂或处理版本不一致，必须输出 `not_identified`，不得自动挑选一组控制变量继续回归。

基础识别假设包括：consistency、well-defined treatment、exchangeability/randomization、positivity/overlap、no informative interference 或显式 interference model、correct time zero、no post-treatment adjustment、无选择性结果观测。每项必须是独立机器字段，不允许用一个 `assumptions_passed=true` 概括。

### 3.6 Estimand 注册表

F01 不接受只有“提升率”的分析。协议必须从以下估计对象中显式选择并绑定尺度：

| 家族 | 最小 estimand | 关键限定 |
|---|---|---|
| 随机实验 | SATE、PATE、ITT | 分配总体、样本总体和目标总体分开 |
| 不依从 | CACE/LATE、TOT | 工具相关性、排除限制、单调性；不得冒充 ATE |
| 观察性处理 | ATE、ATT、ATC | exchangeability、positivity、目标总体 |
| 异质性 | GATE/CATE、policy value | 子组/特征事前性、honesty、overlap；不声称个人真实效应 |
| 集群/网络 | cluster-average、individual-average、direct/spillover/total effect | 分配权重与暴露映射决定含义 |
| 时间设计 | period-average、event-time ATT、cumulative effect | time zero、anticipation、carryover、权重 |
| 连续/剂量 | dose-response、local derivative、policy contrast | treatment support、generalized positivity |
| 中介/机制 | total、controlled direct、natural/interventional indirect | 需要更强的跨世界或中介识别假设；默认不用于 v1 决策 Claim |
| 迁移 | TATE/PATE in target environment | transport set、effect modifier、目标总体权重和支持重叠 |

绝对差、相对差、风险比、赔率比、对数尺度和金额尺度不可互换。非塌缩 estimand（例如 odds ratio）不得当作风险差解释；平均效应不得自动外推为每个对象的效果。

## 4. 规范对象模型

### 4.1 核心对象

| 对象 | 目的 | 必含内容 |
|---|---|---|
| `causal_question` | 固化业务问题与反事实 | 对象、人群、动作、对照、结果、窗口、目标 Claim、业务 owner |
| `experiment_protocol` | 事前登记 | 假设、estimand、设计、分配单位、样本、指标、分析、停止、多重比较、偏差处理 |
| `metric_contract` | 固化口径 | 主/护栏/诊断/经济指标、公式、单位、方向、成熟窗口、来源、缺失规则 |
| `population_snapshot` | 固化资格总体 | 纳入/排除、时间、版本、去重、覆盖、基线、分层变量 |
| `assignment_record` | 保存分配 | 单位、组别、算法、随机种子或可复核证明、时间、分层/集群 |
| `exposure_record` | 区分分配与真实曝光 | 曝光资格、实际曝光、污染、交叉、依从、时间 |
| `analysis_plan` | 锁定估计方法 | 主估计量、协变量、缺失、异常、序贯、稳健性、异质性 |
| `analysis_dataset_manifest` | 锁定分析数据 | 数据指纹、字段、过滤、转换、快照、权限、隐私、质量结果 |
| `causal_analysis_result` | 承载估计与诊断 | estimand、点估计、区间、方向、诊断、敏感性、限制、等级 |
| `economic_interpretation` | 转成经营价值 | 增量量、贡献利润、实施/机会/风险成本、净价值区间、参数来源 |
| `causal_handoff` | 供各域消费 | 当前结果、Claim 上限、允许/阻断动作、依赖、版本、失效条件 |
| `reproducibility_bundle` | 复算与审计 | 协议、样本、数据、代码、环境、参数、哈希、结果和偏差 |
| `deviation_record` | 记录偏离 | 偏离类型、发生时间、原因、影响、批准者、降级和补救 |

### 4.2 通用字段

所有对象至少含：`schema_version`、`object_id`、`object_version`、`status`、`as_of_time`、`owner`、`created_at`、`updated_at`、`source_refs`、`lineage_refs`、`jurisdiction_refs`、`parameter_refs`、`assumption_refs`、`limitations`、`content_hash`。

禁止用空字符串、0、默认显著或默认无影响替代未知；未知、缺失、不适用、未观察和冲突必须可区分。

## 5. 生命周期与状态机

```text
draft
  → preregistered
  → eligibility_checked
  → approved_to_launch
  → running
  → monitoring
  → analysis_locked
  → analyzed
  → reviewed
  → handed_off
  → replayed / superseded / invalidated
```

允许的旁路状态：`blocked`、`redesign_required`、`stopped_for_harm`、`stopped_for_futility`、`stopped_for_success`、`cancelled`、`data_failed`、`inconclusive`。

状态转移必须记录：前状态、后状态、触发条件、证据、执行者、时间、版本、允许动作、阻断动作和回滚目标。禁止：

- 未 `preregistered` 直接启动；
- 未通过资格 Gate 进入 `approved_to_launch`；
- 运行中静默修改主指标、样本、估计量或停止规则；
- 未锁定数据和分析计划就发布结果；
- 已 `invalidated` 的结果继续被下游消费；
- 新版本覆盖旧结果而不保留历史和影响闭包。

## 6. 实验资格与设计路由

### 6.1 资格 Gate

每个 Gate 输出 `pass / conditional / fail / not_assessed`，并区分可补偿与不可补偿。

| Gate | 核心问题 | fail 时动作 |
|---|---|---|
| Q1 决策可行动性 | 结果是否会改变一个真实决定？ | 停止实验或重写问题 |
| Q2 可操纵性 | treatment 是否可定义、可执行、可撤回？ | 禁止因果实验 Claim |
| Q3 反事实 | 对照是否代表合格反事实？ | 改设计或降级 |
| Q4 分配与识别 | 随机化/准实验识别条件是否成立？ | 阻断 CE4/CE5 |
| Q5 SUTVA/干扰 | 单位间影响是否可忽略或已建模？ | 改为集群/网络设计或降级 |
| Q6 可观测性 | 分配、曝光、结果、时间是否可对齐？ | 修复埋点，不得启动/出结论 |
| Q7 功效与精度 | 样本、方差、MDE、流失是否可接受？ | 延长、扩大、重设 MDE 或承认不确定 |
| Q8 安全与伦理 | 护栏、隐私、公平、伤害和停止是否充分？ | 不可补偿阻断 |
| Q9 可执行性 | 库存、流量、平台规则和运营能力是否支持？ | 延期或重设计 |
| Q10 经济合理性 | 信息价值是否高于实验成本和风险？ | 不做或缩小实验 |

### 6.2 设计路由顺序

1. 优先判断能否做个体随机 A/B；
2. 存在污染或共享环境时评估分层/集群随机；
3. 资源动态分配需求不能自动使用多臂赌博机替代因果实验；
4. 强时间/地区外溢时评估 switchback、geo 或集群设计；
5. 无法随机时，先判断是否存在自然实验或明确分配机制；
6. 准实验只能按识别假设选择，不得按“哪个结果显著”反向选择；
7. 所有设计均不合格时，输出 CE0—CE3 和补证方案，不强行产生因果结论。

### 6.3 第一版设计边界

方法能力使用三档，不用“文档提到过”冒充支持：

- `native_executable`：仓库内确定性实现，可离线复算；
- `verified_backend`：通过固定版本科学计算后端执行，保存环境锁、输入输出、诊断和 parity fixture；
- `protocol_only`：只提供资格、设计、数据和外部执行/复核合同，不产生数值因果结论。

第一版 L3 发布范围冻结如下：

| 方法族 | v1 能力档 | 必须实现或验证的内容 | 最大 Claim |
|---|---|---|---|
| 两组 A/B | native | 二元、连续、计数、比例/ratio；绝对与相对效应；不等分配 | CE5 |
| A/B/n | native | 共享对照、比较家族、Holm/Bonferroni；Dunnett 走 backend | CE5 |
| 分层/区组随机 | native | 分层分配、权重、strata fixed effects、分层稳健区间 | CE5 |
| CUPED/ANCOVA | native | 仅 treatment 前协变量、theta 估计、方差缩减、交互项稳健调整 | CE5 |
| 集群随机 | verified_backend | ICC/设计效应、cluster-weighted estimand、CR2/自由度修正、随机化推断备选 | CE5 |
| 固定样本 | native | superiority、non-inferiority、equivalence；MDE/precision assurance | CE5 |
| Group sequential | verified_backend | 预登记 looks、information fraction、O'Brien-Fleming/Pocock 或 alpha-spending、边界复算 | CE5 |
| Anytime-valid | verified_backend | e-process/confidence sequence；与固定样本报告分离 | CE5 |
| Switchback | verified_backend | 周期分块、washout/burn-in、carryover order、periodicity、serial dependence、随机化推断 | CE4/CE5 |
| Geo/cluster holdout | verified_backend | 匹配/分层、spillover、pre-fit、cluster inference、随机化分布 | CE4/CE5 |
| 2×2 DiD | native | ATT、共同冲击、anticipation、pre-period 说明、稳健/安慰剂合同 | CE4 |
| 多期/错峰 DiD | verified_backend | group-time ATT、动态效应、never/not-yet-treated、同时区间；禁止朴素 TWFE | CE4/CE5 |
| Synthetic control/SDID | verified_backend | donor 资格、正则/权重、pre-fit、placebo、leave-one-out、时间 placebo、不确定性 | CE4 |
| RDD | verified_backend | sharp/fuzzy、局部线性、带宽、偏差修正、密度/协变量连续、donut/placebo | CE4/CE5 |
| IV | verified_backend | ITT、first stage、弱工具、排除限制/单调性、LATE 边界 | CE4 |
| 观察性 AIPW/TMLE/DML | verified_backend | DAG 调整集、overlap、cross-fitting、orthogonal score、双重稳健、敏感性 | CE4 |
| Matching/weighting | verified_backend | balance、overlap、estimand-compatible weights、trimming、隐藏偏差敏感性 | CE4 |
| HTE/uplift | verified_backend | honest split/cross-fit、DR/R learner 或 causal forest、GATE、policy value、AUUC/Qini holdout | CE4 |
| 网络干扰 | protocol_only | exposure mapping、assignment probabilities、direct/spillover estimand、外部合格分析 | CE4 |
| 纵向/动态处理 | protocol_only | time-varying confounding、g-formula/IPW/MSM/TMLE、策略 estimand | CE4 |
| 中介分析 | protocol_only | 明确 direct/indirect estimand 和强识别假设；不接受简单逐步回归 | CE4 |
| Proximal causal | research_only | treatment/outcome proxies、completeness、bridge function 与外部复核 | CE4 |
| Bayesian hierarchical | protocol_only | prior、likelihood、loss、posterior predictive、simulation calibration、敏感性 | 不独立决定等级 |
| Bandit/off-policy | protocol_only | 记录 propensity、regret 目标与推断目标分离、IPS/DR policy value | CE4 |
| MMM/BSTS/media response | domain_owned | F01 只验证设计与 Claim；模型和预算主权仍属 D09/D12 | 依 F01 Grade |

其中 `protocol_only` 与 `research_only` 不计入 v1 executable 覆盖率。任何方法升级必须新增方法卡、依赖决策记录、独立 Oracle、模拟覆盖率测试、真实/半合成回放和版本变更。

## 7. 指标、样本与分析合同

### 7.1 指标合同

每个实验必须事前冻结：

- 一个主要决策指标或明确的多主要指标校正规则；
- 护栏指标及不可补偿停止阈值；
- 诊断指标（分配、曝光、漏斗、数据质量）；
- 经济指标及与 D06 的口径连接；
- 短期、成熟和长期观察窗口；
- 指标方向、分母、去重、缺失、异常、延迟和重算规则；
- 指标版本改变时的兼容、重基线和失效规则。

### 7.2 样本设计

样本计划至少保存：基线率/均值、方差、MDE、alpha、power、组间比例、单/双侧、流失、依从、聚类相关、设计效应、多重比较、计划中期查看、最小运行时长和成熟等待期。

任何样本量输出必须同时给出公式版本、参数来源、适用分布、舍入规则、敏感性区间和不能保证的事项。禁止只输出一个无上下文样本数。

### 7.3 默认分析原则

- 随机实验主分析默认 ITT；TOT/依从性分析只能作为明确标注的补充，并说明额外假设；
- 报告绝对效应、相对效应、区间和基线，避免只报百分比提升；
- 协变量和 CUPED 必须事前指定或标记为探索性，且协变量不得受 treatment 影响；
- 缺失、流失、异常值和删样必须按事前规则处理并给出敏感性；
- 子组结果默认探索性，除非事前登记且完成交互检验与多重比较治理；
- 不允许根据显著性选择指标、窗口、分群、模型或停止时点。

### 7.4 指标统计模型

| 指标类型 | 规范估计 | 强制诊断 | 禁止捷径 |
|---|---|---|---|
| Binary | 风险差为默认，同时可报风险比；小样本走精确/稳健方法 | 极端基线、零事件、成熟窗 | 无条件 Wald 区间 |
| Continuous | 均值差/协变量调整；重尾时预登记稳健估计或 bootstrap | 尾部、异常、方差异质 | 事后 winsorize 直到显著 |
| Count | 单位时间/暴露率或总量 estimand；Poisson/负二项仅在后端诊断合格时 | 暴露时长、过度离散、零膨胀 | 把事件当独立用户 |
| Ratio | 明确 ratio-of-sums 或 mean-of-ratios；delta/linearization、cluster bootstrap 或后端稳健区间 | 分母接近零、分子分母协方差、随机化单位 | 把聚合比率当普通均值 |
| Quantile | 预登记分位点，bootstrap/随机化推断 | mass point、稀疏尾部、同时区间 | 用均值方差公式套分位数 |
| Time-to-event | 生存/累计发生 estimand、右删失与 competing risk 合同 | 非比例风险、删失机制、成熟度 | 未成熟样本填 0 |
| Repeated measures | 以分配单位聚合或使用合格纵向模型 | intake、窗口、单位内相关、carryover | 每行事件当独立样本 |

累计窗口与固定暴露后窗口估计的对象不同，必须在协议中选择；运行时长变化导致 estimand 变化时，不得继续把不同快照当同一指标。

### 7.5 协变量调整与方差降低

- CUPED：`Y_adj = Y - theta(X - E[X])`，`X` 必须在 treatment 前确定且不受实验资格/触发影响；
- ANCOVA：默认包含 treatment、中心化基线协变量及 treatment×covariate 交互，使用与分配设计相容的稳健方差；
- 高维调整：必须 sample splitting/cross-fitting，报告未调整主估计与调整估计的方向、区间、方差缩减和覆盖率验证；
- 协变量选择只允许事前规则或与 treatment label 隔离的流程；
- 方差缩减不能改变 estimand、修复 SRM、弥补无 overlap 或制造因果识别。

### 7.6 功效、精度与最小重要差异

F01 不把 `alpha=.05`、`power=.8` 当作全局默认真理。样本设计必须由错误成本、业务最小重要差异、可用单位、运行成本、护栏风险和决策时限共同生成。支持：

- superiority、non-inferiority、equivalence 三类问题；
- 基于 MDE 的设计与基于目标区间宽度的 precision assurance；
- 二元、连续、ratio、cluster、repeated-period 和预计流失/污染修正；
- baseline/variance/ICC 不确定时的情景样本区间；
- 小样本集群不可用增加集群内事件数无条件补偿；
- 观察到的 post-hoc power 不作为结果解释。

### 7.7 缺失、流失与不依从

缺失必须区分分配缺失、曝光缺失、结果缺失、退款/成熟缺失和协变量缺失。分析最少包含 complete-case 风险、IPW/多重插补适用条件、best/worst-case 或 tipping-point 敏感性；MNAR 不能被 MAR 模型“解决”。

不依从主报告 ITT。Per-protocol/as-treated 默认只作描述。CACE/LATE 只有随机 assignment 可作有效 instrument，且 relevance、exclusion、independence、monotonicity 与 first-stage 均有依据时才允许；弱 first stage 必须阻断确定 Claim。

## 8. 序贯、多重比较、数据质量与偏差治理

### 8.1 序贯治理

协议必须明确属于：固定样本、group sequential、alpha spending 或其他经批准设计。若未登记序贯规则，中途窥视不得触发“胜出”停止；由此产生的结果必须降级并记录偏差。

提前停止分为：伤害、无效、成功、外部不可执行和数据失败。每类必须有独立阈值、责任人和下游动作；“成功停止”不能只由未校正 p 值触发。

### 8.2 多重比较

必须登记比较家族、主要/次要/探索性层级、校正方法和 Claim 上限。新增指标、分群、窗口或变体必须增加比较族或降级为探索性，不能静默保留原 alpha。

### 8.3 不可忽略诊断

- SRM；
- A/A 与分配复现；
- 分配前协变量平衡；
- 曝光错配、交叉和 non-compliance；
- 重复单位、机器人、欺诈和身份拼接；
- 流失、缺失和延迟成熟；
- novelty、seasonality、carryover；
- 并发实验和共同干预；
- 库存、价格、履约、页面或追踪事故；
- 数据版本、回填和泄漏。

### 8.4 降级不可被业务结果补偿

正向收入、显著 p 值、漂亮 ROAS、管理层偏好或下游一致意见，都不能补偿随机化失败、无反事实、严重污染、数据不可复现、未成熟结果或不可接受伤害。

### 8.5 多重性与试验组合治理

多重性至少分为四层：

1. 单实验多变体/多主指标：优先 FWER，使用 Holm、closed testing、共享对照校正或经验证 Dunnett；
2. 大量探索性指标/异质性发现：允许 FDR，但不能把 FDR 结果改写为验证性主结论；
3. 连续进入的实验组合：若启用 online FDR，必须注册假设到达顺序、依赖假设、alpha wealth 和异步完成规则；
4. 数据驱动选择后推断：选择过程与确认过程分离；无法分离时使用有效 post-selection inference 或降级。

实验被分叉、重跑、延长、换窗口、换分群或换模型时，必须继承同一 hypothesis family 或明确登记新家族，禁止通过改实验 ID 重置错误预算。

### 8.6 序贯方法不可混用

- 固定样本 p 值只能在预定分析点解释；
- group sequential 使用事前 information fraction 与边界；
- alpha-spending 必须保存 spending function 和实际 look；
- anytime-valid 使用 e-value/e-process 或 confidence sequence，并保存 time-uniform 语义；
- Bayesian monitoring 必须用预先验证的 prior、likelihood、decision loss 和 stopping simulation，不得把 posterior probability 当 frequentist error guarantee；
- futility 可非约束或约束，但属性必须事前登记；安全停止可以越过 efficacy 计划，不能反向证明 treatment 有害的精确因果量。

同一结果不得从不同框架中挑最有利的显著/可信表达。报告必须指明推断框架和保证对象。

## 9. 准实验、干扰与外部有效性

### 9.1 准实验统一要求

每个准实验必须显式记录：分配机制、识别假设、时间零点、处理组与对照组构造、anticipation、同期冲击、spillover、预趋势、安慰剂/伪检验、敏感性、估计对象和外推范围。

DiD 至少要求：

- 处理前趋势和足够的前期窗口；
- 不把“前趋势不显著”单独当作平行趋势已证明；
- 处理时点错开时不得默认使用会产生错误权重的简单双向固定效应；
- 同期政策、价格、库存、渠道和季节冲击进入混杂审查；
- 动态效应、anticipation 和 spillover 有显式诊断；
- 不满足关键识别条件时最高 CE3。

### 9.2 干扰治理

实验协议必须定义干扰图或最小干扰说明。店铺、家庭、达人、地区、渠道、库存池、竞价环境和社交传播均可能形成 spillover。必要时改变随机单位、采用集群/网络设计、估计直接与间接效应，或降低 Claim。

### 9.3 异质性与迁移

国家、平台、品类、生命周期、人群和时间差异只能用于：

- 事前指定的 effect modification；
- 有多重比较控制的探索；
- 形成下一轮验证假设。

一个环境中的 CE5 结果迁移到另一环境时默认降级，除非 F02 适用性、关键机制、总体差异和再验证证据均满足。F01 不自行宣布跨国、跨平台或跨生命周期普遍有效。

### 9.4 现代 DiD 合同

- 单一同时处理、两组两期可使用 2×2 ATT；
- 多期或错峰处理必须使用 group-time ATT 或等价异质性稳健估计，明确 never-treated 与 not-yet-treated 对照；
- 禁止默认用传统 TWFE event study 汇总错峰且异质的处理效应；
- 动态 effect 按 event time 输出，并提供 simultaneous bands，不用单个 lead 不显著证明平行趋势；
- 显式处理 anticipation、treatment reversal、continuous dose、composition change、spillover 与 time-varying covariates；
- conditioning 只能使用明确的 pre-treatment covariates，禁止加入被 treatment 影响的 bad controls；
- 结果至少包含 group-time effect、聚合权重、pre-trend/placebo、对照构造和敏感性。

### 9.5 Synthetic control 与 SDID 合同

供体池必须在看 post-treatment outcome 前冻结，并排除污染、结构断裂和不可比口径。输出：unit/time weights、effective donor count、weight concentration、pre-RMSPE、post gap、placebo rank、leave-one-out、time placebo、in-space placebo 和不确定性。拟合优秀不等于识别成立；供体污染、单一权重支配、短 pre-period 或 placebo 不异常时最高 CE3。

SDID 可在 latent factor 结构下作为 DiD 与 synthetic control 的稳健组合候选，但必须由 verified backend 执行，不能用现有简单非负权重求解器改名实现。

### 9.6 RDD、IV 与观察性因果

- RDD：固定 cutoff 和 running variable；局部线性、数据驱动带宽、robust bias correction、密度操纵、协变量连续、带宽/多项式敏感性、donut/placebo；只外推 cutoff 附近；
- IV：明确 instrument、first stage、reduced form、2SLS/LIML 选择、弱工具诊断和 exclusion/monotonicity；结果是 LATE/CACE，不是全体 ATE；
- 观察性研究先写 target trial：资格、策略、分配、time zero、随访、结果、estimand、分析；
- AIPW/TMLE/DML 需要 DAG 支持的调整集、overlap、cross-fitting、out-of-fold nuisance prediction、orthogonal score 和 influence-function 区间；
- 倾向分数只用于设计/加权/双重稳健组成，不把高 propensity matching 当因果证明；
- 每个观察性 CE4 必须提交未测混杂敏感性、negative control 或 placebo、trimming 影响和替代模型；无敏感性最高 CE3。

### 9.7 HTE、Uplift 与策略价值

HTE 分为 confirmatory GATE、exploratory CATE 和 policy learning：

- GATE 必须事前登记子组、交互检验和同时区间；
- CATE 使用 honest splitting/cross-fitting；DR/R learner、causal forest 等模型必须报告 overlap、校准、稳定性和 out-of-sample policy value；
- Uplift 使用 AUUC/Qini、分位增量差异和 cost-sensitive policy value，普通 AUC 不合格；
- 多模型选择必须嵌套验证，禁止在同一 holdout 上反复挑模；
- 个体分数只表示条件效应估计/排序及不确定性，不声明不可观测的“此人的真实因果效果”；
- 公平、隐私、资格、频控和不触达是策略的硬约束，不得被正 uplift 补偿。

### 9.8 长期效应、Surrogate 与动态处理

短期指标不能自动替代长期贡献。Surrogate index 只有在历史长短期数据、surrogacy/transport 假设、out-of-sample 校准和失败边界均有证据时用于早期估计；否则只标为 mechanism/leading indicator。novelty、learning、fatigue、carryover、cookie/identity decay、survivorship 与退款成熟必须进入长期结果合同。

时间变化处理、重复触达和策略序列涉及 time-varying confounding 时，普通回归/分层不合格；必须路由 g-formula、marginal structural model、sequential DR/TMLE 或外部合格分析，v1 保持 protocol_only。

### 9.9 Transportability 与外部有效性

迁移必须固定 source population、target population、selection mechanism、effect modifiers、support overlap 和目标尺度。至少输出 covariate-shift、overlap 和 effect-modification 风险。允许重加权/transport estimator 的前提是关键 effect modifier 已观测且目标总体有支持；否则提供界限、敏感性或要求目标环境再实验。F02 负责环境口径，F01 负责迁移识别与等级，两者缺一不可。

## 10. 经济解释与动作上限

### 10.1 经济价值合同

至少输出：

```text
incremental_quantity_interval
× qualified_contribution_per_unit
− implementation_cost
− experiment_cost
− opportunity_cost
− expected_risk_cost
= risk_adjusted_net_value_interval
```

所有金额必须引用 D06/F02/ERDG 的币种、税费、时间、单位、参数版本和情景。缺失关键经济参数时，可以输出统计结果，但经济结论必须为 `not_assessed` 或 `inconclusive`。

### 10.2 结果姿态

F01 可输出的证据姿态仅限：

- `evidence_supports_consideration`；
- `evidence_does_not_support`；
- `inconclusive_collect_more`；
- `redesign_required`；
- `stop_for_harm`；
- `result_invalidated`。

F01 不直接输出 `launch`、`scale_budget`、`change_price`、`replenish`、`contact_customer` 或 `invest`。对应业务域必须结合自身 Gate 作最终决定。

## 11. 强制 Gate 与降级矩阵

### 11.1 不可补偿阻断

以下任一成立，禁止 CE4/CE5：

- 无合格反事实或识别策略；
- 分配机制无法复核；
- 未事前登记主要指标和停止规则却声称验证性结论；
- 严重 SRM、污染、流失或数据血缘断裂未解释；
- 结果窗口未成熟；
- 选择性删样、挑指标、挑窗口、挑子组或按结果改模型；
- 多重比较未治理；
- 准实验关键识别假设不成立；
- 护栏出现不可接受伤害；
- 无法复算或结果版本冲突未解决。

### 11.2 最低降级规则

| 情况 | 最高等级 | 必须附加动作 |
|---|---:|---|
| 平台归因，无反事实 | CE3 | 标注 attributed，设计增量验证 |
| 前后对比，无同期对照 | CE2 | 排查趋势、季节与共同干预 |
| 随机化合格但样本精度不足 | CE4 或更低 | 报宽区间，不得宣称无效 |
| 事后子组显著 | CE2/CE3 | 标为探索性，独立验证 |
| 未登记的中途停止 | CE2/CE3 | 重算或重做实验 |
| DiD 识别条件部分满足 | CE3/CE4 | 明示假设与敏感性，不得普遍外推 |
| 统计通过但经济参数缺失 | 因果等级可保留 | 经济与动作 readiness 为 not_assessed |
| 护栏伤害超过硬阈值 | 证据可保留 | 动作上限强制 stop_for_harm |

## 12. 确定性工具与实现上限

第一版拟建工具必须小而可审计，每个工具有输入 Schema、输出 Schema、公式/算法卡、边界条件、错误合同、Golden、性质测试、模拟覆盖率和反例：

| 组 | 工具 | 责任 |
|---|---|---|
| Protocol | `validate_causal_question.py` | estimand、DAG/潜在结果、time zero、总体与 Claim 合法性 |
| Protocol | `validate_experiment_protocol.py` | 指标、分配、停止、多重性、偏差与资格 Q1—Q10 |
| Design | `calculate_sample_size.py` | 二元/连续/ratio/cluster 的 superiority、NI、equivalence 与情景范围 |
| Design | `calculate_mde_precision.py` | MDE 与目标区间宽度双向设计 |
| Design | `generate_randomization.py` | 可复核 seed、hash、分层/区组/集群分配；不接真实外部执行 |
| Trust | `validate_randomization.py` | SRM、A/A、分配复现、基线平衡、重复单位 |
| Trust | `validate_exposure_outcome.py` | eligibility→assignment→exposure→outcome→maturity 守恒 |
| Metric | `evaluate_metric_effect.py` | binary/continuous/count/ratio/quantile 路由和效应尺度 |
| Metric | `apply_covariate_adjustment.py` | CUPED/ANCOVA，输出未调整与调整 parity |
| RCT | `evaluate_randomized_effect.py` | ITT、分层、共享对照 A/B/n、有限总体/稳健推断 |
| Cluster | `evaluate_cluster_effect.py` | cluster-weighted estimand、CR2/df 或随机化推断后端 |
| Sequential | `evaluate_sequential_result.py` | 固定、group sequential、alpha spending、confidence sequence 严格分路 |
| Multiplicity | `adjust_multiplicity.py` | Holm/Bonferroni/BH/后端 Dunnett 与 hypothesis family ledger |
| Safety | `evaluate_guardrails.py` | non-inferiority/伤害区间、停止姿态、不可补偿红线 |
| Switchback | `evaluate_switchback.py` | period assignment、carryover、washout、periodicity、随机化推断 |
| Quasi | `evaluate_did.py` | 2×2 与 group-time ATT 后端、动态效应和 simultaneous bands |
| Quasi | `evaluate_synthetic_counterfactual.py` | SCM/SDID、placebo、leave-one-out、pre-fit 和不确定性 |
| Quasi | `evaluate_rdd_iv.py` | RDD/IV verified backend 适配与完整诊断 |
| Observational | `evaluate_doubly_robust_effect.py` | AIPW/TMLE/DML 路由、cross-fit、overlap、influence function |
| HTE | `evaluate_heterogeneous_effect.py` | GATE/CATE、honest split、校准、AUUC/Qini/policy value |
| Sensitivity | `evaluate_sensitivity.py` | hidden confounding、attrition、trimming、specification curve 的合格子集 |
| Economics | `calculate_incremental_economics.py` | 效应分布连接 D06/F02 合格参数与风险调整净价值 |
| Grade | `grade_causal_claim.py` | 根据 Gate、诊断、偏差、复现和经济状态生成 CE0—CE5 |
| Handoff | `build_causal_handoff.py` | 统一交接、过期、失效、重算和动作上限 |
| Reproduce | `validate_reproducibility_bundle.py` | 协议、数据、代码、环境、参数、随机种子和结果血缘 |

### 12.1 科学计算后端政策

仓库当前开发依赖只有 PyYAML 与 jsonschema。F01 不允许为了“零依赖”手写高风险高级推断，也不允许无约束引入大型运行时。实现采用双层策略：

1. `native_core`：仅实现容易独立验证的代数、Schema、状态、分配、基础效应、CUPED、固定样本和简单 2×2 DiD；
2. `scientific_backend`：集群稳健推断、sequential、现代 DiD、SCM/SDID、RDD、IV、DML/TMLE/HTE 使用固定版本、固定平台的成熟库或经过独立复核的实现。

引入后端前必须提交 ADR：库/版本/许可证、方法对应、平台支持、数值稳定、随机种子、线程与浮点确定性、序列化、漏洞更新、替代/回滚和 Oracle parity。运行时不可用时必须返回 `backend_unavailable`，不得自动退化为错误的简化估计器。

### 12.2 数值与随机性合同

- 拒绝 bool-as-number、NaN、Infinity、溢出、非法概率、零/近零分母和未对齐数组；
- 明确浮点容差、求解收敛、最大迭代、条件数和权重退化；
- 随机算法保存 PRNG 家族、seed、版本和抽样索引哈希；
- bootstrap/permutation/Monte Carlo 输出 Monte Carlo error 与有效重复数；
- 同输入、版本、环境和 seed 必须可重现；
- 解析/计算失败不得写入部分正常结果；部分方法失败时保留已验证模块但总 Claim 降级。

禁止第一版工具：自动挑选“最佳”模型、自动 p-hacking、用正态近似覆盖不适用的小样本、将无穷/NaN 静默改为 0、在错误输入上返回看似正常的结果、以默认值替代缺失关键设计参数。

## 13. Schema 与目录蓝图

正式目录名冻结为 `experiment-causal-assessment`，runtime prefix 冻结为 `ECAE`。目录在 WP-01 后、WP-02 开始时创建：

```text
experiment-causal-assessment/
├── SKILL.md
├── references/
│   ├── charter-sovereignty-and-terminology.md
│   ├── identification-estimands-and-causal-graphs.md
│   ├── experiment-eligibility-and-design-routing.md
│   ├── metrics-sample-and-analysis-contract.md
│   ├── sequential-multiplicity-and-deviation.md
│   ├── randomized-cluster-switchback-and-interference.md
│   ├── quasi-experiments-and-observational-causality.md
│   ├── heterogeneity-uplift-long-term-and-transport.md
│   ├── economics-claim-grading-and-handoff.md
│   ├── data-lineage-reproducibility-and-replay.md
│   ├── method-cards/
│   ├── professional-depth-governance.md
│   └── output-protocols/professional-report-delivery.md
├── schemas/
├── scripts/
├── backends/
├── tests/
├── evaluations/
│   ├── golden/
│   ├── adversarial/
│   ├── failure/
│   ├── property/
│   └── cross-domain/
├── integrations/
└── agents/openai.yaml
```

第一版至少需要独立 Schema：causal-question、causal-graph、estimand、protocol、metric、population、assignment、exposure、analysis-plan、hypothesis-family、dataset-manifest、diagnostic-result、analysis-result、sensitivity-result、economic-interpretation、deviation、handoff、reproducibility-bundle。

F01/F02 是共享底座，不插入仅允许 D01—D14 的 `domain-architecture-registry.json`。WP-01 必须新增共享底座注册合同，明确 foundation id、runtime、availability、provides/requires、消费者、Claim 权限、external write=false 和发布门；D01—D14 继续保留业务域身份与主权。

根目录 `SKILL.md` 可在实施期创建但 availability 必须保持 `next_build`；只有 L1—L3 全部通过后才能按发布策略改为 `current`。目录存在、示例运行或局部脚本通过都不构成 current 证据。

### 13.1 逻辑组件架构

```text
Question/Protocol Registry
        ↓
Eligibility + Identification Engine
        ↓
Design/Assignment + Metric Compiler
        ↓
Data Trust + Exposure/Maturity Reconciliation
        ↓
Estimator Router ── native_core / scientific_backend / protocol_only
        ↓
Diagnostics + Sensitivity + Reproducibility
        ↓
CE Grade + Economics Bridge + Claim/Action Ceiling
        ↓
D01—D14 Handoff / Invalidation / Recompute
```

每层产生版本化对象，下层不能绕过上层 Gate。Estimator Router 只接受 protocol 锁定的方法，不能根据输出效果自动换模型。

### 13.2 数据工程最小合同

F01 不建设通用数据仓库，但必须定义以下逻辑表/事件：assignment、eligibility、exposure、outcome、metric fact、maturity adjustment、experiment change、analysis snapshot。所有事件需支持 event time、ingestion time、source version、dedupe key、late-arrival policy、deletion/consent state 和 backfill revision。

必须验证守恒：eligible ≥ assigned；exposed 是 assigned 的合格子集或给出明确跨组污染；结果按 analysis unit 唯一聚合；订单/收入与退款成熟版本可重算；触发分析不能基于 treatment 后变量选择样本而不改变 estimand。

### 13.3 非功能要求

| 维度 | 开发要求 |
|---|---|
| Determinism | 同输入/版本/seed/环境同输出；非确定后端必须记录容差与差异 |
| Auditability | 每个 Claim 回指 protocol、数据指纹、方法卡、代码和诊断 |
| Idempotency | 重复验证/交接不产生重复状态或不同结果 |
| Failure isolation | 单个 estimator/back-end 失败不污染其他方法；总等级 fail closed |
| Compatibility | Schema 使用 semver；破坏性升级有适配、双轨、差异和回滚 |
| Security/privacy | 最小字段、去识别、目的限制、授权/删除传播、日志脱敏、无外部写入 |
| Performance | 大样本允许流式聚合；不得以抽样加速静默改变 estimand |
| Observability | 方法、版本、耗时、失败、降级、重算、失效和消费者拒绝可追踪 |
| Portability | macOS/Linux 与仓库支持的 Python 版本验证；平台差异进入发布证据 |

## 14. 跨域消费者与迁移合同

### 14.1 已核验现状与迁移处置

本轮已对全仓 265 个含实验、因果、增量、归因、MDE、SRM、护栏、Uplift 等关键词的文件做静态盘点，并重点复核主要实现。结论如下：

| 域 | 已有能力/接口 | 已核验问题 | F01 处置 |
|---|---|---|---|
| D01 CIDM | `evaluate_experiment.py` 的漏斗计数、经营 Gate、Continue/Iterate/Stop | 不是反事实实验估计器，缺 assignment/exposure/uncertainty | 保留业务测款决定；接收 F01 handoff，不迁入因果内核 |
| D02 CIM | 变化、替代解释、竞争归因 | 多为观察归因，不应升级 causal | 作为证据/共同冲击/negative-control 提供者 |
| D03 PIPM | 已明确“F01 建成前因果 Claim 必须阻断” | 临时阻断待正式合同替换 | 接收 validation evidence，保留产品路线图主权 |
| D04 SPPQ | 样品、质量、生产和抽样对象 | 工程/质量检验不自动等于市场因果实验 | 可消费实验设计；保留供应与质量放行主权 |
| D05 LTMA | 动态规则、Claim、合规 Gate | 不应由因果证据覆盖法律/安全 Gate | 仅提供不可补偿约束与实验合规资格 |
| D06 PPFC | 贡献利润、现金、币税与实际经济结果 | 不负责因果识别 | 作为 economic parameter owner；接收效应分布做价值重算 |
| D07 LIFD | 使用增量贡献做分配、回收实际履约结果 | 增量输入资格未统一 | 只接受带 CE Grade/有效期的增量；库存动作仍属 D07 |
| D08 PLCO | 二元两组 Wald 区间、成熟与护栏 | 无 SRM、序贯、多重性、协变量、ratio/cluster；动作过早基于基础区间 | 现脚本降为 legacy adapter；新实验走 F01，D08 决定页面动作 |
| D09 AAMO | 两组 ITT、MDE、cluster ITT、简单 DiD/SCM、adstock-Hill | 两套重叠入口；DiD/SCM/cluster 推断过度简化；SCM 缺 placebo inference | 基础/高级因果迁入 F01；media response、广告架构和预算仍属 D09 |
| D10 CAPM | G6 测量 Gate、`causal_evidence_level` | 现代码把未定义的 `C2/C3` 直接视作 incremental eligible | P0 迁移：改用 CE Grade 显式映射，旧标签不得自动等价 |
| D11 VLB | 创意变体、内容观察与信号归因 | 内容机制评分不证明销量或增量 | 提供变体和机制假设；实验结论由 F01，创意主权保留 D11 |
| D12 MBCM | MDE、DiD、ITT/CACE、SCM、Geo match、bootstrap/Monte Carlo | 与 D09 重复；部分公式为简化实现；`causal_claim_allowed` 把区间与利润过度合并 | 统计内核迁 F01；品牌、GTM、Offer、活动与资源方向仍属 D12 |
| D13 CIG | 二元 Wald、SRM z、护栏、Uplift 分箱/AUUC 概念 | 明确承认当前仅基础计算；Wald/简单分箱不足以支持复杂实验与 HTE | RCT/HTE 估计迁 F01；客户证据、授权、CRM 与不触达主权仍属 D13 |

`governance/shared-statistical-primitives.md` 当前规定 D09/D12 各保留一套本地公式并做 parity。F01 current 后，统计原语**合同 owner** 转为 F01；业务结论 owner 不变。迁移期保留旧实现 parity，所有消费者验收完成后才能决定 retire，不直接删除。

### 14.2 已确认的 P0/P1 技术债

| ID | 等级 | 技术债 | 开发处置 |
|---|---|---|---|
| TD-01 | P0 | 因果等级标签在不同域含义冲突 | 新增 CE0—CE5；旧标签逐域显式映射，不做字符串推断 |
| TD-02 | P0 | 平台归因、经营前后差与增量仍有混写入口 | Claim validator 词汇/字段/动作三重阻断 |
| TD-03 | P0 | 现有 DiD 对多期、错峰、异质处理不成立 | 简单实现只保留 2×2；现代 DiD 走 verified backend |
| TD-04 | P0 | 合成控制缺 placebo、leave-one-out 和有效不确定性 | 旧脚本不得输出 CE4；重建 SCM/SDID adapter |
| TD-05 | P1 | 二元 Wald 在极端基线/小样本下覆盖不足 | 指标路由改用稳健/精确/后端方法，Wald 仅合格大样本 |
| TD-06 | P1 | cluster 只对 cluster mean 做正态区间，少集群风险未处理 | CR2/df、randomization inference、wild cluster 或降级 |
| TD-07 | P1 | ratio、重复事件与随机化单位错位 | metric compiler + delta/linearization/cluster bootstrap |
| TD-08 | P1 | 无统一 hypothesis family 和序贯账本 | multiplicity/sequential ledger 成为协议必需对象 |
| TD-09 | P1 | Uplift 排序评估缺少完整 policy-value 与模型校准 | honest/cross-fit HTE backend + holdout policy evaluation |
| TD-10 | P1 | F01/F02 无共享底座注册平面 | WP-01 新建 foundation registry，不污染 D01—D14 域注册表 |

### 14.3 消费者盘点范围

必须逐一盘点 D01—D13 现有：

- 因果/增量等级字段；
- 实验 Schema 和脚本；
- MDE、样本、区间、护栏、停止和经济公式；
- attributed/incremental 的命名；
- 各自 Gate、报告模板和测试断言；
- 与 shared statistical primitives 的重复或冲突；
- F01 建成前的临时阻断语句。

### 14.4 迁移原则

- F01 统一“因果资格与共享统计合同”，业务域保留业务问题和最终动作；
- 不直接删除旧字段，先建立字段级映射、双读/双写或适配器、差异报告和回滚；
- 每个消费者必须显式声明接受的 F01 schema/version、最小等级、失效处理和禁止升级；
- 不兼容消费者阻断迁移，不以“主流程能跑”替代消费者验收；
- 同一公式的多个实现必须有 parity fixture；语义不同的公式不得为了复用强行合并；
- F01 发布前，现有域不得被描述为已完成统一迁移。

### 14.5 统一交接最小字段

`question_ref`、`protocol_ref`、`estimand`、`design_family`、`population_scope`、`time_scope`、`effect_absolute`、`effect_relative`、`uncertainty`、`diagnostics`、`causal_grade`、`claim_ceiling`、`economic_status`、`allowed_evidence_postures`、`blocked_claims`、`limitations`、`valid_until`、`invalidation_triggers`、`recompute_triggers`、`reproducibility_ref`。

## 15. 评测与独立发布门

### 15.1 测试分类

- **Golden**：正常、边界、零效应、负效应、护栏伤害、经济不可行；
- **Failure**：缺字段、非法状态、非有限数、单位错误、样本不足、数据未成熟；
- **Adversarial**：p-hacking、挑窗口、挑子组、伪随机、平台归因冒充增量、显著冒充价值；
- **Property**：交换组别符号翻转、样本增大区间不应无故变宽、单位缩放一致、哈希稳定、重复运行幂等；
- **Mutation**：删除 Gate、反转护栏、放宽等级、忽略 SRM、静默默认值后测试必须失败；
- **Cross-domain**：D01—D13 接受、拒绝、降级、冲突、过期、回滚和重算；
- **Multi-turn/rebase**：连续追问只保留唯一当前结果，同时保留完整历史与影响闭包；
- **Extreme**：极小/极大样本、极端基线、零方差、稀有事件、严重不平衡、集群退化、全量流失。

### 15.1.1 每个 executable 方法的最低证据包

每张方法卡至少绑定：

- 1 个可手算或解析解 Golden；
- 1 个零效应、1 个正效应、1 个负效应 DGP；
- 2 个边界、2 个非法输入、2 个识别失败、2 个对抗案例；
- 3 个与方法相关的 metamorphic/property tests；
- 1 组与独立成熟实现的 differential/parity fixtures；
- 覆盖率、I 类错误、功效/精度、偏差和 RMSE 的模拟报告；
- 1 个“数值结果漂亮但必须降级”的反例；
- 1 个跨域接受与 1 个消费者拒绝案例；
- 方法实现或 Gate 被 mutation 后必然失败的测试。

测试数量只是最低覆盖，不是质量证明；重复模板、改 ID 或同一 DGP 换数字不算独立案例。

### 15.1.2 模拟验收规则

设模拟重复数为 `R`，名义覆盖率/错误率为 `p`，Monte Carlo 标准误为 `sqrt(p(1-p)/R)`。覆盖率与 I 类错误验收带不得靠肉眼或固定“差 1%”判断，而使用预登记的 Monte Carlo band，默认 `max(0.005, 3×MCSE)`；若尾部精度不足必须增加 R。

- 固定样本：零效应下 I 类错误受控；备择下功效与设计值相容；
- sequential/anytime：在所有 look/path 上验证整体错误保证，不只验证终点；
- interval：多种基线、方差、偏斜、样本、分配比和 cluster DGP 下验证覆盖；
- DiD/SCM/RDD/IV：假设成立时覆盖/偏差合格，假设破坏时诊断或等级必须失败；
- DML/TMLE/HTE：cross-fit 泄漏、overlap 退化、模型错设、异质性为零与强异质性均覆盖；
- multiplicity：完整 family 下验证 FWER/FDR，不以单个假设通过代替；
- sensitivity：隐藏偏差增强时结论强度应单调不升；
- economics：单位、币种、税、时间缩放与风险传播保持守恒。

### 15.1.3 独立 Oracle 与反作弊

实现者编写的测试不能单独作为 Oracle。L3 受控试点至少需要三类相互独立的证据：解析/设计型真值、外部成熟软件数值 parity、基于公开一手论文或官方包文档的 owner 授权技术审查。发布门必须注入以下 mutation：删除识别 Gate、把 CE3 升 CE5、忽略 SRM、改换 estimand、去除 multiplicity、忽略 carryover、允许 bad control、删敏感性、让过期结果继续消费、把 backend failure 改为 native fallback；每项都必须使相应测试失败。未完成完整操作特征和外部方法复核的高级后端不得进入 L3 可执行面，只能保持安装但失败关闭。

### 15.2 L1 Structure 发布门

- 目录、入口、引用、版本、路由和注册信息完整；
- 无死链、孤儿文件、临时产物、秘密或不必要本机路径；
- 所有专业文件被入口直接或条件路由；
- 结构验证、引用验证和仓库级治理验证通过；
- 尚未满足 L2/L3 时不得声明完整可用。

### 15.3 L2 Contract 发布门

- 所有核心 Schema 可机器验证；
- 状态转移、Gate、降级、幂等、版本、失效和回滚可测试；
- 缺失、冲突、过期、部分失败和非有限数 fail closed；
- 结果变更触发影响闭包与选择性重算；
- 业务域不能升级 Claim 或突破动作上限；
- D01—D13 消费者矩阵、字段映射、差异报告和验收齐全。

### 15.4 L3 Expert 发布门

- 第一版所有 executable 方法都有确定性实现、公式依据、适用条件和诊断；
- 正常、边界、失败、对抗、性质、mutation、极端和跨域测试通过；
- 每个设计至少一个 Golden 与一个看似合理但必须拒绝的反例；
- 输出完整覆盖证据、反证、估计对象、区间、偏差、限制、经济、不行动、成功、停止、回滚和失效；
- 公开一手方法来源、独立软件 parity 与 owner 授权技术审查完成，且关键异议有处置记录；
- 全仓发布门无新增失败，既有失败不得被归因给 F01 后静默接受。

### 15.5 L4 保留门

L4 只能由授权真实案例关闭，至少需要：原始证据指纹、事前协议、分配与曝光、代码和环境、参数快照、结果、真实经营后果、偏差/事故、独立非实现者复核、版本对照、漂移检查和可复算证明。生产消费者双跑/签收以及受控试点未释放的高级科学后端外部资格也归入此门。合成测试、公开方法来源、示例报告或内部自评都不能关闭 L4。

## 16. 实施工作包与逐包 DoD

| WP | 工作包 | 依赖 | 完成定义 |
|---|---|---|---|
| WP-00 | 全仓现状与冲突盘点 | 无 | D01—D13 文件/字段/公式/脚本/测试/owner 清单及冲突分级完成 |
| WP-01 | 章程、术语、主权和注册蓝图 | WP-00 | 词典、双层主权、禁止结论和 F01/F02/ERDG 边界冻结 |
| WP-02 | 对象、Schema、版本与状态 | WP-01 | 核心 Schema、示例、反例和状态验证器通过 |
| WP-03 | 识别、estimand、资格、指标与样本 | WP-02 | 双表示模型、Q1—Q10、指标编译、MDE/precision 和协议验证通过 |
| WP-04 | 随机实验 native core | WP-03 | A/B/n、指标族、分层、CUPED/ANCOVA、固定样本与随机化诊断通过 |
| WP-05 | 序贯、护栏、多重性和偏差 | WP-03/04 | fixed/group/anytime 分路、alpha/FDR ledger、护栏和 deviation 可测试 |
| WP-06 | 集群、Geo、Switchback 与干扰 | WP-03—05 | cluster estimand、CR2/RI、carryover、washout、spillover 与后端 parity 通过 |
| WP-07 | 现代准实验与观察性因果 | WP-03/05 | 2×2/错峰 DiD、SCM/SDID、RDD/IV、AIPW/TMLE/DML 与敏感性按能力档交付 |
| WP-08 | HTE、长期效应与迁移 | WP-04/07 | GATE/CATE/policy value、surrogate、transport 与 F02 接口通过 |
| WP-09 | 经济解释、等级和交接 | WP-04—08 | 经济区间、CE0—CE5、动作上限和 handoff 通过 |
| WP-10 | 复现、血缘、重算与回滚 | WP-02—09 | bundle、哈希、影响闭包、失效和 replay 通过 |
| WP-11 | 跨域迁移与消费者验收 | WP-00/09/10 | D01—D13 映射、本地双轨、差异、回滚和受控试点 acceptance 完成；生产 acceptance 由 L4 管理 |
| WP-12 | 专业评测与方法资格 | WP-03—11 | 全测试族、模拟覆盖、外部软件 Oracle、公开一手方法审查、mutation、异议和修复闭环完成 |
| WP-13 | L1—L3 发布与 L4 准备 | WP-01—12 | 仓库发布门通过，状态仅为 controlled pilot；只准备 L4 模板，不关闭 L4 |

每个 WP 开始前必须有输入清单，结束时必须提交：变更范围、需求映射、Schema/代码/文档、测试证据、未决项、风险、回滚点、消费者影响和下一包准入结论。

### 16.1 开发控制与需求追踪

- 本文每个 MUST/禁止项分配稳定 requirement id，生成 requirement→WP→artifact→test→release-evidence 矩阵；
- 一个 PR 只关闭明确工作包范围，不允许顺手扩大 estimator 或 Claim；
- 方法实现 PR 必须附 method card、公式/伪代码、依赖、数值风险、fixture 和失败边界；
- Schema PR 必须附合法/非法样例、兼容性、迁移和回滚；
- 每个 WP 结束运行局部门与全仓回归；全仓既有失败先归因，不得改测试降低门槛；
- 破坏性修改 estimand、Grade、动作上限、Gate、Schema 或后端时回到蓝图变更评审；
- 开发完成不等于发布：只有 WP-13 的权威发布证据可修改 maturity/current 状态。

### 16.2 关键路径

```text
WP-00 → WP-01 → WP-02 → WP-03 → WP-04 → WP-05
                                  ├──────→ WP-06 ─┐
                                  └──────→ WP-07 ─┼→ WP-08 → WP-09 → WP-10 → WP-11 → WP-12 → WP-13
```

WP-06 与 WP-07 可在 WP-05 合同冻结后并行，但当前任务执行是否并行不改变验收和证据边界。WP-11 的受控试点接受必须逐消费者绑定合同哈希并由 owner 授权；生产接受必须在真实双跑后另行逐消费者签署，不能由生产者自测替代。

## 17. 评审决定与关闭记录

本轮不遗留需要下一轮蓝图讨论的内部 P0/P1。外部人员、真实数据和 L4 属于后续发布依赖，不构成蓝图未完成。

| ID | 等级 | 决定 | 状态 | 后续约束 |
|---|---|---|---|---|
| F01-R-01 | P0 | 正式目录 `experiment-causal-assessment`，runtime `ECAE` | closed | 改名属于破坏性变更 |
| F01-R-02 | P0 | 采用 CE0—CE5；旧 `C*` 标签逐域显式映射 | closed | 禁止字符串自动映射或默认升级 |
| F01-R-03 | P0 | 采用第 6.3 节三档能力和完整 v1 范围 | closed | 未过方法发布包不得升级 executable |
| F01-R-04 | P0 | L3 采用解析真值、外部成熟软件 parity 和 owner 授权公开方法审查；独立非实现者专业复核保留至高风险个案与 L4 | closed | 不足证据的高级后端不得进入受控试点可执行面 |
| F01-R-05 | P1 | frequentist/design-based 为 v1 核心；Bayesian 为 protocol_only | closed | Bayesian 升级需 calibration 和独立错误/决策验证 |
| F01-R-06 | P1 | 固定样本 native；group sequential 与 anytime-valid verified backend | closed | 三种语义严格分路，不得混用 |
| F01-R-07 | P1 | 按 D01—D13 逐消费者双轨迁移 | closed | 无统一截止日期；以 acceptance 完成决定 retire |
| F01-R-08 | P1 | F01 current 后成为共享统计合同 owner | closed | 领域保留业务结论；迁移完成前保留 parity |
| F01-R-09 | P1 | 不设全行业 CE4/CE5 数值阈值 | closed | 机器门验证识别/协议/诊断；精度和价值阈值由问题协议与业务 owner 提供 |
| F01-R-10 | P1 | F01 校验隐私/公平/伦理/伤害合同，业务域和 owner 批准真实实验 | closed | 安全/授权失败不可补偿 |
| F01-R-11 | P2 | F02 完成前保留原币种/税/时区/单位，不自动合并或迁移 | closed | 跨环境结果默认降级并阻断 D14 合并 |
| F01-R-12 | P2 | L4 只预留合同，不在本轮绑定真实数据源 | closed_as_L4_dependency | 真实授权、最小化和留存在 WP-13 后单独审批 |

### 17.1 L4 独立专业复核资格

L4 或高风险 CE5 个案的独立复核者至少满足：有因果推断/实验设计的可验证专业背景；能复核随机化、集群/序贯、现代 DiD/SCM、观察性双重稳健和 HTE 中至少三个族；未主导待复核实现；披露利益冲突；对范围内方法和个案签署 accepted/conditional/rejected 及理由。单纯代码审查、模型跑通或通用数据科学经验不能替代该外部复核。

## 18. 最终评审结论

### 18.1 通过内容

- 建设顺序、章程、共享主权和双层决定合同通过；
- 双表示因果模型、estimand 注册、CE0—CE5 与不可补偿 Gate 通过；
- RCT、cluster、sequential、anytime、switchback、现代 DiD、SCM/SDID、RDD/IV、DML/TMLE、HTE、长期和 transport 方法边界通过；
- native/verified backend/protocol-only 分层通过；
- 25 个工具职责、20 类 Schema/对象、逻辑组件、数据工程和非功能要求通过；
- D01—D13 现状处置、10 项 P0/P1 技术债和双轨迁移合同通过；
- 模拟覆盖、独立 Oracle、differential parity、mutation 和跨域消费者验收通过；
- WP-00—WP-13 关键路径、DoD、回滚和发布证据链通过。

### 18.2 实施授权上限

F01 现可进入 WP-00，并按依赖进入后续工作包。授权不包含：

- 跳过盘点/Schema/方法卡直接写高级模型；
- 把旧 AAMO/MBCM/CIG/PLCO 脚本改名后视为 F01 完成；
- 在消费者验收前删除旧字段或实现；
- 在 WP-12 方法资格证据关闭前声明 L3 Expert，或把未释放高级后端写成可执行；
- 在 WP-13 发布门前设置 current；
- 用合成/模拟案例关闭 L4；
- 对真实平台执行外部写入或自动经营动作。

### 18.3 成熟度边界

本评审通过的是**项目开发蓝图**，不是 F01 实现或发布。未来 L1—L3 全部通过的最高表述仍为 `controlled_pilot_engineering_ready`；production-ready、真实经营有效和跨市场普遍有效均需 L4 外部保证。

## 19. 方法论证据登记

以下原始论文/作者页面用于冻结本蓝图的方法方向；实现阶段必须为每张方法卡补充精确公式、版本和适用条件，不能只引用本表：

| 主题 | 主要证据 | 对 F01 的约束 |
|---|---|---|
| 随机实验协变量调整 | [Lin, Agnostic Notes on Regression Adjustments](https://www.stat.berkeley.edu/~winston/agnostic.pdf) | ANCOVA 使用 treatment interaction 与设计相容稳健推断 |
| CUPED | [Deng et al., Improving Sensitivity with Pre-Experiment Data](https://citeseerx.ist.psu.edu/document?doi=049ba16a73e4493c0d62db369e4f9a1c4820cbb2&repid=rep1&type=pdf) | 只用 treatment 前协变量，方差降低不改变识别 |
| Ratio/delta | [Deng et al., Applying the Delta Method in Metric Analytics](https://www.microsoft.com/en-us/research/publication/applying-the-delta-method-in-metric-analytics-a-practical-guide-with-novel-ideas/) | ratio 指标必须处理分子分母协方差与聚合层级 |
| SRM | [Fabijan et al., Diagnosing Sample Ratio Mismatch](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/) | SRM 是数据可信度 Gate，不能忽略后继续 Claim |
| Anytime-valid | [Howard et al., Time-uniform Confidence Sequences](https://arxiv.org/abs/1810.08240) | 中途查看需 time-uniform 保证，不能套固定样本区间 |
| 多期/错峰 DiD | [Callaway & Sant'Anna, DiD with Multiple Time Periods](https://arxiv.org/abs/1803.09015) | 使用 group-time ATT 与异质性稳健聚合 |
| Continuous DiD | [Callaway, Goodman-Bacon & Sant'Anna](https://www.nber.org/papers/w32117) | 连续处理效应解释需额外选择/剂量假设 |
| Synthetic DiD | [Arkhangelsky et al., Synthetic Difference in Differences](https://arxiv.org/abs/1812.09970) | SDID 不得由简单 SCM 改名实现 |
| Switchback | [Bojinov, Simchi-Levi & Zhao, Design and Analysis of Switchback Experiments](https://arxiv.org/abs/2009.00148) | 设计与推断必须处理 carryover order |
| Switchback 前沿 | [Zeng et al., Sequentially-Rerandomized Switchback Experiments](https://arxiv.org/abs/2604.02489) | 作为 research watchlist，不在无独立复核时升级 v1 |
| 一般干扰 | [Aronow & Samii, Average Causal Effects Under General Interference](https://isps.yale.edu/research/publications/isps18-01) | assignment、exposure mapping 与 direct/spillover estimand 必须联动 |
| DML | [Chernozhukov et al., Double/Debiased ML](https://academic.oup.com/ectj/article/21/1/C1/5056401) | orthogonal score、cross-fitting、overlap 和 nuisance 诊断 |
| TMLE | [van der Laan & Rubin, Targeted Maximum Likelihood Learning](https://ideas.repec.org/a/bpj/ijbist/v2y2006i1n11.html) | 双重稳健不等于任一模型任意错误仍有效 |
| HTE/causal forest | [Athey, Tibshirani & Wager, Generalized Random Forests](https://gsbpreserve.stanford.edu/view/42785) | honesty、样本外评估和有效区间 |
| Target trial | [Hernán & Robins, Using Big Data to Emulate a Target Trial](https://pmc.ncbi.nlm.nih.gov/articles/PMC4832051/) | 观察性因果先对齐资格、time zero、策略、随访与 estimand |
| RDD | [Calonico, Cattaneo & Titiunik, Robust RD Intervals](https://onlinelibrary.wiley.com/doi/abs/10.3982/ECTA11757) | 局部估计需带宽、偏差修正和 cutoff 诊断 |
| Surrogate/长期 | [Athey et al., The Surrogate Index](https://www.nber.org/papers/w26463) | 只有 surrogacy 与迁移假设成立才能替代长期结果 |
| Transport | [Ung, VanderWeele & Dahabreh, Trial Transportability](https://arxiv.org/abs/2407.14703) | source/target、参与效应和 effect modifier 显式化 |
| 未测混杂前沿 | [Tchetgen Tchetgen et al., Proximal Causal Learning](https://arxiv.org/abs/2009.10982) | 仅 research_only；需要 proxy/completeness/bridge 专门合同 |

来源登记不是“采用所有模型”的授权。方法能力仍以第 6.3 节和实际发布证据为准。

## 20. 联合评审与批准记录

| 轮次 | 日期 | 评审范围 | 决定 | 保留边界 | 文档版本 | 责任人 |
|---:|---|---|---|---|---|---|
| 0 | 2026-08-10 | 初始蓝图 | 建立草案 | 12 项待决定 | DRAFT-0.1 | repository owner + Codex |
| 1 | 2026-08-10 | 全仓盘点、理论/方法、工程、迁移、评测、发布 | `approved_for_implementation` | 独立复核与 L4 作为发布依赖 | 1.0 | repository owner + Codex |
| 2 | 2026-08-10 | 受控试点方法资格、13 域接受与生产边界拆分 | `implemented_controlled_pilot` | 真实双跑、外部独立复核、高级后端资格和生产校准保留 L4 | 1.1 | repository owner authorization + Codex technical review |

批准依据：repository owner 明确要求本次完成深度、先进性、专家级和项目开发级评审；本文已关闭内部 P0/P1，冻结能力档、关键路径和授权上限。

当前结论：`F01-BLUEPRINT-1.1 implemented_controlled_pilot`

后续每轮评审必须追加记录，不得覆盖历史。破坏性改变主权、对象、estimand、公式/推断语义、CE Grade、接口、依赖后端或动作上限时，必须提高蓝图版本并重新评审影响闭包。
