# 科学后端选择、绑定与 parity 治理

## 三层对象不可混同

1. **candidate lock**：确认正式发行版、许可证、运行时、能力与明确不支持项；只代表“值得验证”。
2. **runtime binding**：项目运行时能以精确版本载入包，并通过冻结 I/O 合同；只代表“可以调用”。
3. **verification proof**：解析/设计真值、独立实现 parity、模拟、对抗、mutation、种子与数值容差全部通过，并由未主导实现的方法专家接受；此时 registry 才可标记 `verified`。

安装成功、能 import、单个示例通过或文档声称支持，都不能越级成为 verification proof。候选、适配器或依赖发生变化时旧 proof 自动失效。

## WP-06 选型结论

### 集群推断

- 主后端锁定 R `clubSandwich 0.7.0`，只因其直接覆盖 CR2 与 Satterthwaite/saddlepoint 小样本检验。
- Python `PyFixest 0.60.0` 仅作为 CRV3、随机化推断与 wild bootstrap 的候选组件，不得替代 CR2。
- `wildboottest 0.3.2` 当前只提供 bootstrap p 值，不提供反演区间，因此不能独立满足效果、区间、自由度与敏感性的完整交付。
- parity 至少覆盖：平衡/不平衡簇、簇大小与效果相关、少簇、高 leverage、单簇删除、零方差、奇异设计、不同 estimand 和分析权重。

### Group Sequential

- 主引擎锁定 R `gsDesign 3.10.1`；R `rpact 4.4.0` 是独立 parity oracle。
- 等价输入必须先统一单/双侧约定、Z 边界方向、information fraction、alpha 定义、spending function 参数和 futility 是否 binding，再比较数值。
- 只比较最终总 alpha 不够；逐 look 比较 efficacy/futility boundary、nominal p、累计 alpha spent 和操作特征。

### Anytime-valid

`confseq 0.0.11` 当前被拒绝绑定：正式版状态为 Alpha，最近发行时间较早，本机隔离构建失败。任何新候选必须先冻结 estimand、观测过程、可预测下注/混合规则、边界假设和有限样本支持；不能把 group-sequential 边界改名为 confidence sequence。

### Switchback

R `ri2 0.5.0` 只负责按声明的随机化程序生成分布并检验冻结统计量。ECAE 仍负责验证 allowed sequence、period、时区、washout、最大 lag、周期性、carryover、同时系统变化和 serial dependence。随机化 sharp-null p 值不能自动升级为平均效果区间。

## 2026-08-10 隔离开发验证快照

该快照是开发证据，不是 verification proof，也不改变 registry 的 `verified_count=0`：

- 在临时隔离的 R 4.6.1 环境中，从正式源精确安装 `clubSandwich 0.7.0`、`gsDesign 3.10.1`、`rpact 4.4.0` 与 `ri2 0.5.0`；项目未绑定系统级 R，临时运行时不能冒充可部署 runtime binding。
- `clubSandwich` CR2/Satterthwaite 适配器通过一个固定向量与“簇内 treatment 变化”mutation，但手工 CR2 矩阵、覆盖率/一类错误模拟、外部 parity 和独立方法评审仍未完成。
- `gsDesign` 适配器支持 efficacy-only 的 O'Brien–Fleming、Pocock、Hwang–Shih–DeCani 和用户累计花费。六个冻结向量先统一 total alpha、单/双侧和累计/增量口径，再与 `rpact` 对照；最大绝对 Z 边界差小于 `5e-7`，小于预注册开发容差 `1e-6`。`rpact` 自带 IQ 的无凭据演示子集为 110 pass、0 fail/warn/skip，但完整集共有 39065 项且需要授权凭据，所以资格状态仍是 `incomplete`。binding futility 在 beta-spending parity 完成前明确失败关闭。
- `ri2` 适配器只支持显式允许序列集合上的等概率、精确枚举、零加性 sharp null 与 period-level difference-in-means。六序列固定向量的 p 值为 `1/3`，与手工穷举完全一致；序列越界、washout 回流和枚举上限 mutation 均按专属错误拒绝。
- switchback 的 lag、周期性与 carryover 仍保留独立降级权；当前适配器只证明 sharp-null randomization p 值，没有平均效应区间，也没有在趋势、carryover 或序列相关冲击下的操作特征保证。

可复验产物分别位于 `evaluations/group-sequential-development-parity.json`、`evaluations/switchback-ri-development.json`、`evaluations/backend-probe-report.json`，复算入口为 `scripts/probe_group_sequential_parity.R`。这些高级后端不属于当前 L3 受控试点可执行面；只有 L4 外部独立复核、模拟校准、持久运行时和 proof 全部齐备后，才允许改变 registry 状态。

## WP-07 后端拆分与开发证据

WP-07 不再使用 `synthetic_counterfactual`、`rdd_iv` 或 `observational_dr` 这类合并后端。它们无法形成一对一 package/version/adapter/proof 绑定，并会掩盖以下不可互换边界：SCM 与 SDID 的优化和适用域不同，RDD 与弱 IV 的局部/依从者 estimand 不同，AIPW、TMLE 与 DML 的 nuisance、targeting 和 score 合同不同。

当前锁定：`did 2.5.1`、`Synth 1.1-10`、固定 commit 的 `synthdid 0.0.9`、`rdrobust 2.0.0`、`ivmodels 0.10.0`、`AIPW 0.6.9.3` 和 `DoubleML 0.11.3`。`tmle 2.1.1` 被审阅但未绑定，因为当前 F01 合同要求所有进入 score 的 nuisance prediction 都是 out-of-fold，而该候选所审 API 不能满足完整要求。

隔离 Python 3.9.6 开发环境已精确安装并运行 `rdrobust 2.0.0` 与 `ivmodels 0.10.0`：

- RDD 固定 sanity vector 的结构断点为 3，robust bias-corrected 估计约 3.011，95% 区间覆盖 3；这是适配器形状和数值不变量检查，不是独立 parity。
- 强 first-stage IV 向量的 LIML 估计约 1.977，AR/CLR 置信集覆盖结构值 2。
- 弱 first-stage 向量的 rank-test p 值约 0.45；AR 与 CLR 都返回 `[-inf, inf]`，证明适配器保留非识别而不伪造有限 Wald 精度。

上述临时 probe 已由锁定的持久开发环境取代：CPython 3.12.13 与 R 4.5.3 的精确依赖、synthdid 源码 revision 和 12 个适配器哈希均已冻结，错峰 DiD、SCM、SDID、AIPW、DoubleML 及其余已选适配器的统一固定向量全部通过。registry 因外部 parity、预注册完整模拟网格和方法专家复核尚未完成，保持零 verified；已执行候选标记为 `installed_unverified`。详细冻结计划与开发结果见 `evaluations/wp07-parity-plan.json`、`evaluations/wp07-backend-development.json` 和 `evaluations/persistent-backend-development-qualification.json`。

## WP-08 HTE、Policy Value、Surrogate 与 Transport

HTE 主候选锁定 Python `econml 0.16.0`，组合使用 honest `CausalForestDML` 和 `DRTester`。选择依据不是逐点预测精度，而是它同时暴露 honest tree splitting、cross-fitted nuisance、独立样本 BLP、calibration、Qini 与 AUTOC。R `grf 2.6.1` 被锁定为独立 parity oracle，因其 `rank_average_treatment_effect` 明确要求 priorities 独立于 evaluation forest，并提供 RATE/Qini 推断。两者不能因都使用森林而被视为同一 oracle。

隔离 Python 3.9.6 开发环境精确安装 `econml 0.16.0`，实际执行两个冻结向量：

- 两组真实 GATE 为 1 和 3 时，独立评估样本估计约 1.112 与 3.226，BLP 斜率约 1.133、calibration R² 约 0.794、Qini 约 0.258、AUTOC 约 0.674。冻结的正向异质性门通过。
- 同一向量中，候选策略相对 treat-all 的值差约 -0.588，95% 区间约 `[-0.741,-0.436]`。因此策略门失败；“异质性可排序”没有被升级为“个性化策略值得采用”。
- 常数真实效果为 2 的反例中，两组 GATE 接近，calibration R² 为负，BLP、Qini 与 AUTOC 的方向不支持正向排序。即使某些 nominal p-value 很小，冻结门仍输出 `heterogeneity_supported=false`，防止把负排序或过拟合写成异质性成功。

适配器不输出逐行 CATE，只输出总体 GATE、校准、排序、policy value 和分布摘要。Policy threshold、primary baseline、最低校准/排序下界和最低策略改进必须在 evaluation outcomes 之前冻结。任何业务动作仍需容量、成本、公平、部署漂移和业务 owner 决定。

Surrogate 和 transport 当前不绑定自制估计后端：前者只验证 surrogacy、comparability、treatment family、成熟、删失/竞争风险、失败案例和 surrogate paradox；后者只验证目标 estimand、selection/effect modifiers、支持域、sampling-score cross-fit、权重 ESS/支配、桥接和 F02 applicability。两者通过只代表有资格进入外部合格估计，不直接授予目标因果等级。

开发证据与预注册验证计划见 `evaluations/wp08-backend-development.json` 和 `evaluations/wp08-parity-plan.json`。EconML 主适配器与 GRF 开发 oracle 已在锁定的持久运行时完成统一固定向量执行；这不构成独立 parity。外部 differential parity、预注册覆盖率与 I 类错误网格、backend-output mutations、surrogate/transport 外部 fixtures 和独立专家复核完成前，`hte_uplift` 保持 `installed_unverified`，不得执行生产因果动作。

## 失败关闭顺序

执行前依次检查：registry schema → candidate lock 一致 → `status=verified` → proof 完整且未过期 → 运行时存在 → 精确版本一致 → adapter 存在 → 输入合同 → 数值与诊断。任一步失败都返回专属错误码；禁止改用 iid SE、固定样本 p 值、普通 bootstrap 或未验证自制算法。

## Proof 最低要求

proof 必须绑定 backend、candidate、package/version、environment、adapter、contract、seed，以及五类证据。外部 parity 必须是实现独立的 oracle；同一包的两个 API 或同一代码的包装层不算独立实现。有效期届满、依赖升级、平台/编译器变化、容差变化、关键异常或适配器修改都会触发重新验证。
