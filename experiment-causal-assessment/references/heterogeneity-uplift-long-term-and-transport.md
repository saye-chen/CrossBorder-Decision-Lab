# 异质性、Uplift、长期效应与迁移

## 目录

1. 目标与不可补偿边界
2. HTE estimand 与三种任务
3. 识别继承与变量时间顺序
4. Honest 数据拓扑
5. GATE、校准与排序验证
6. Policy value 与经营约束
7. 稳定性、漂移与允许措辞
8. 长期结局、删失与竞争风险
9. Surrogate 与 surrogate index
10. Transportability 与目标总体
11. F02 接口
12. 后端、证据包与失败关闭

## 1. 目标与不可补偿边界

WP-08 不回答“哪个人一定会被处理改变”，而回答四个更窄的问题：

1. 预先定义的总体分组平均效应是否不同；
2. 一个冻结的优先级分数能否在独立样本上把高效应总体排在前面；
3. 一个冻结策略相对 treat-all、treat-none 和现行策略是否增加预期价值；
4. 源环境效应能否在明确假设和支持域下迁移到指定目标环境。

以下失败不可被模型精度、显著性或经营价值补偿：

- 源因果效应本身没有合格识别；
- effect modifier 使用处理后变量、中介、碰撞点或未来信息；
- 在同一结果样本上发现分群、调参、选阈值并做最终检验；
- 把 CATE/uplift score 描述为个体真实因果效应；
- 只比较候选策略和 treat-none，不比较 treat-all 与现行策略；
- 用短期代理的正向变化替代长期因果效应；
- 把源环境等级直接继承给目标环境；
- 支持域或桥接失败后继续外推。

## 2. HTE estimand 与三种任务

二元处理下，条件平均处理效应为：

`tau(x) = E[Y(1) - Y(0) | X=x]`。

它是条件总体平均量，不是单个单位不可同时观测的 `Y_i(1)-Y_i(0)`。即使模型输出逐行分数，也只能称为条件效应预测或处理优先级分数。

### 2.1 Confirmatory GATE

对事前定义的组 `G=g`：

`GATE_g = E[Y(1)-Y(0) | G=g]`。

必须冻结：组定义、组边界、组家族、主要对比、方向、最小组样本、同时区间或多重性方法。分别给每组点区间而不检验组间差异，不能证明异质性。

### 2.2 Exploratory CATE

用于发现可能的 effect modifier、非线性结构和候选分组。输出最高通常 CE3，必须在新样本或新实验确认后才能升级。变量重要性、树分裂次数和 SHAP 不能单独证明因果异质性。

### 2.3 Ranking 与 policy learning

排序任务只要求分数 `S(X)` 将相对高效应总体排在前面，不要求逐点 CATE 数值正确。Policy learning 进一步把分数、容量、成本和约束编译为冻结决策规则 `pi(X)`。排序成功不代表策略优于 treat-all。

## 3. 识别继承与变量时间顺序

HTE 不能修复源分析的识别失败。随机试验继承随机化、暴露、干扰、不依从、缺失和指标成熟条件；观察性 HTE 继承 exchangeability、consistency、positivity、DAG 调整集、所有 nuisance 样本外预测和未测混杂敏感性。

Effect modifier 必须：

- 在处理分配或目标策略执行前可得；
- 不被处理影响；
- 在部署时按同一口径可测；
- 不通过结果、复购、退款、客服或未来行为泄漏；
- 在源与目标环境中具有可比语义。

若以处理后响应分群，目标通常变成 principal stratum、dynamic regime 或 mediation 问题，不能继续使用普通 HTE 合同。

## 4. Honest 数据拓扑

最低拓扑为：

`开发/调参 → 规则与阈值冻结 → 独立评估 → 业务决策`。

复杂任务可拆为：

`discovery → tuning → calibration → final evaluation`。

必须保存：分区规则、实体 ID、时间截断、分层方式、随机种子、fold hash、数据哈希、特征版本、模型库、超参数范围、停止规则和重复 split 方案。

以下都属于 evaluation leakage：

- 用最终评估结果选择特征、模型或 seed；
- 看 Qini 后修改分组或阈值；
- 从多个 split 中只报告最有利者；
- 用评估样本的 treatment/outcome 选择评估子集；
- 先训练全量模型，再声称其中一部分是 holdout；
- 同一实体、订单、账号、Geo 或时间周期跨分区泄漏。

Cross-fitting 解决 nuisance 过拟合，不自动等于最终策略的独立评估。最终 policy value 仍应使用未参与模型、阈值和策略选择的样本。

## 5. GATE、校准与排序验证

### 5.1 Doubly robust pseudo-outcome

以 `m_a(X)=E[Y|A=a,X]`、`e(X)=P(A=1|X)` 为 nuisance，可构造处理效应 pseudo-outcome：

`Gamma = m_1(X)-m_0(X) + A(Y-m_1(X))/e(X) - (1-A)(Y-m_0(X))/(1-e(X))`。

观察性场景的 nuisance 必须样本外；随机试验优先使用已知分配概率并核对实现概率。

### 5.2 BLP 与 calibration

在独立评估样本上，用 doubly robust 结果对冻结 CATE 分数做 best linear predictor。正斜率是分数捕捉方向性异质性的证据之一，但不充分：还要检查区间、模型校准、支持域和重复 split 稳定性。

Calibration 比较预测 CATE 分组均值与独立 GATE。负 calibration 指标、斜率方向错误或跨 split 反转时，不允许因为某个 nominal p-value 显著而宣称成功。

### 5.3 TOC、AUTOC、Qini 与 RATE

对冻结优先级分数 `S(X)`，TOC 比较前 `q` 比例总体的平均效应与全体平均效应。AUTOC/RATE 对 TOC 加权积分；Qini 更强调给定处理比例下的累计增量。

必须满足：

- priorities 在 evaluation forest 或最终评估样本之外构造；
- 曲线、积分、标准误和统一带使用同一冻结定义；
- 方向预先规定，负 Qini 不能因为 p-value 小而改写为“存在正异质性”；
- 探索多个分数、模型或结局时进入同一 hypothesis family；
- AUUC/Qini 的软件定义、归一化和基线必须记录，跨实现不能只比较名称。

EconML `DRTester` 提供 BLP、calibration、Qini 和 TOC；GRF `rank_average_treatment_effect` 明确要求优先级分数独立于 evaluation forest。两者作为 differential parity 时需冻结同一 DGP、分区、estimand 和积分网格。

## 6. Policy value 与经营约束

二元策略 `pi(X) in {0,1}` 的价值为 `V(pi)=E[Y(pi(X))]`。相对 treat-none 的增量可由 `E[pi(X) Gamma]` 估计；候选与基准 `pi_0` 的差为 `E[(pi(X)-pi_0(X)) Gamma]`。

最低基准：

- `treat_none`；
- `treat_all`；
- `current_policy`；
- 若适用，随机容量策略或简单透明规则。

策略阈值、tie-break、容量、资格、频控、成本、禁止人群和 fallback 必须在最终评估前冻结。不得在 evaluation outcome 上选择“最佳 top-k”。

Policy value 输出至少包括：

- 每个策略的价值与区间；
- 候选相对每个基准的成对差与区间；
- 处理比例、容量利用和未覆盖总体；
- 贡献利润/成本参数版本，但经济计算不升级因果等级；
- 受保护或高风险群体的精度、伤害和未知；
- 策略复杂度、可执行性、漂移和回滚条件。

候选策略只有在注册的业务重要差异和统计区间同时满足时才可交给 owner 考虑。若所有人的效应均为正，优秀的 CATE 排序仍可能输给 treat-all；若处理有成本，则须在同一单位上重算净 policy value。

## 7. 稳定性、漂移与允许措辞

必须检查：

- repeated split/seed 下 GATE、BLP、RATE、policy value 的分布；
- 特征集合、nuisance library、森林或 learner 的合理替代规格；
- 小组样本、重叠和极端 propensity；
- treatment version、渠道、国家、平台、价格、内容和供给变化；
- 训练到部署的 covariate、modifier 和 calibration drift；
- 容量变化和成本变化下策略排序是否反转。

允许措辞示例：

- “冻结优先级分数在独立评估样本上显示正向排序能力”；
- “预定义 GATE 家族在同时区间下存在差异”；
- “候选策略在指定容量、成本和总体内优于已登记基准”。

禁止措辞示例：

- “模型找到了会被改变的个人”；
- “高 uplift 用户一定会购买”；
- “某变量导致了异质性”，除非另有识别；
- “模型显著，所以应该个性化投放”。

## 8. 长期结局、删失与竞争风险

长期效应首先定义 outcome、time zero、horizon、处理策略和 estimand。不得只写“长期价值”。常见量包括指定时间点风险差、累计发生率差、restricted mean survival time 差和指定窗口累计贡献。

必须区分：

- outcome 尚未成熟；
- administrative censoring；
- loss to follow-up；
- informative censoring；
- competing event；
- treatment switching 或动态处理；
- 重复购买、退款和复活等多状态过程。

简单删掉未成熟用户会造成 cohort/immortal-time 偏差。把竞争事件当普通独立删失也可能改变 estimand。报告中必须冻结风险集、成熟窗口、删失权重、竞争风险定义和敏感性。

动态处理和时间变化混杂路由到 longitudinal g-method `protocol_only`，例如 marginal structural model、parametric g-formula 或 longitudinal TMLE；普通时变回归不能获得 CE4。

## 9. Surrogate 与 surrogate index

短期代理只有在明确的干预族、总体、测量和长期结局下才有意义。高相关、预测准确或处理显著改变 surrogate 都不等于长期因果效应被识别。

两样本 surrogate index 至少需要：

- 实验样本观察处理与短期 surrogates；
- outcome 样本观察相同 surrogates 与长期 outcome；
- surrogacy：给定 surrogates 后长期 outcome 与处理独立；
- comparability：给定 surrogates 后实验样本和 outcome 样本的长期 outcome 机制可比；
- 一致的 treatment family、总体、测量、时间和支持域；
- cross-fitted surrogate model 与冻结特征库；
- 历史 treatment-family 验证、失败案例和违反假设的偏差敏感性。

Surrogate paradox 指处理改善 surrogate、surrogate 与 outcome 正相关，但处理仍伤害长期 outcome。系统因此强制：

- `surrogate_endpoint_only` 最高 CE3；
- 有利 surrogate effect 不能决定长期 effect 的符号；
- 注册直接作用路径、未测共同原因和违反 surrogacy 的 tipping point；
- 保留失败干预、失败国家/平台和机制改变案例；
- 新 treatment version 或新机制默认重新验证。

若长期 outcome 已直接成熟，应优先估计直接长期 estimand，而不是继续用 proxy 获得更漂亮的精度。

## 10. Transportability 与目标总体

设 `S=1` 表示源试验/研究样本，`S=0` 表示目标总体。Transport estimand 必须写为指定目标总体中的 `E[Y(1)-Y(0)|S=0]` 或其他明确尺度。

最低识别假设：

1. 源设计内部有效；
2. consistency 与 treatment version 可比；
3. outcome 测量和 time zero 可比；
4. 给定完整 effect modifiers `Z` 后，处理效应与 selection 可交换；
5. 目标 `Z` 支持域在源样本中有正概率；
6. sampling score、outcome model 或 doubly robust transport 的 nuisance 合格；
7. 未发生破坏机制的并发政策、时间或平台变化。

若源样本是目标总体子集，通常称 generalizability 并使用 inverse probability of sampling weights；源与目标不重叠时，常使用 inverse odds of sampling weights。两者不可只因名称相似而互换。

权重诊断至少报告：

`ESS = (sum w)^2 / sum(w^2)`、最大归一化权重、上尾权重质量、截断前后估计、effect modifier 平衡、源/目标未覆盖单元和 estimand 变化。

阈值必须由协议和精度需求冻结，不设置跨行业万能数字。若重叠不足，可将目标改为明确的 restricted target，但不能静默把它仍称原总体。

源 CE5 不自动成为目标 CE5。Transport 本身最高通常 CE4；目标环境 CE5 需要目标本地的直接决策级证据。未完成桥接时最高 CE3。

## 11. F02 接口

跨国家、平台、币种或时间的效应交给业务域之前，必须绑定 F02 applicability：

- country、platform、channel、seller/account tier；
- treatment version、offer、price、creative、fulfillment promise；
- population inclusion/exclusion 与 lifecycle；
- currency、tax、timezone、unit、metric definition；
- source/target baseline risk 与 effect modifiers；
- 支持域、桥接实验、局部 holdout 和持续校准；
- 有效期、漂移阈值、recompute 与 rollback。

F02 未通过时，F01 只交付源环境证据和迁移缺口，不替目标环境给业务动作。

## 12. 后端、证据包与失败关闭

### 12.1 当前后端拓扑

- `hte_uplift`：EconML 0.16.0 为开发主候选；GRF 2.6.1 为独立 parity oracle。
- 长期动态处理：`protocol_only`。
- Surrogate：协议与证据门，不在当前仓库自制估计器。
- Transport：协议、支持域与 F02 门；外部合格估计后才可评定目标证据。

开发适配器只输出总体 GATE、BLP、calibration、Qini、AUTOC、policy value 和分布摘要，不输出逐行 CATE。

### 12.2 L3 前最低证据

HTE 至少完成：

- 零、稀疏、弥散、阈值、平滑、符号反转异质性 DGP；
- GATE 同时覆盖、BLP/RATE/Qini I 类错误和功效；
- policy value 覆盖与 treat-all/treat-none/current 成对反例；
- EconML/GRF differential parity；
- overlap、cross-fit leakage、split instability、容量、成本、公平和漂移；
- 删除 honest split、改阈值、挑 seed、输出个体效应等 mutation。

Surrogate 与 transport 至少完成解析/闭式两层总体真值、假设破坏、paradox、支持域失败、权重支配、estimand shift、桥接失败和 F02 拒绝案例。

### 12.3 当前发布边界

临时安装、固定向量和本地测试只构成 development evidence。只有持久运行时、精确锁、外部 parity、预注册模拟、backend-output mutation、证据有效期和独立因果专家复核全部闭环，registry 才可改为 `verified`。否则必须返回 `BACKEND_UNAVAILABLE`，不得回退到简单 uplift bins、相关分群或预测模型。

主要官方依据：

- EconML CausalForestDML：https://www.pywhy.org/EconML/_autosummary/econml.dml.CausalForestDML.html
- EconML DRTester：https://www.pywhy.org/EconML/_autosummary/econml.validate.DRTester.html
- GRF causal forest：https://grf-labs.github.io/grf/reference/causal_forest.html
- GRF RATE：https://grf-labs.github.io/grf/reference/rank_average_treatment_effect.html
- Surrogate index：https://www.nber.org/papers/w26463
- Trial transport inverse-odds weighting：https://academic.oup.com/aje/article/186/8/1010/3848983
