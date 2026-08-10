# CrossBorder Decision Lab

[English](README.en.md) · [十三个专业 Skill](#skill-快速定位) · [F01 与 ERDG](#统一决策基础设施) · [系统结构](#系统结构) · [使用方式](#如何使用) · [维护规则](RULES.md)

> 面向跨境商业的专业决策基础设施，把依赖个人经验的经营判断转化为有证据、有模型、有边界、有动作、有停止规则、可持续积累的决策资产。

当前统一发布列车：`2026.07`；目标架构：`CBDS-ARCH-2026.07`；共享合同：`ERDG-CONTRACT-2026.07`。

CrossBorder Decision Lab 服务于跨境电商经营者、品牌团队、投资决策者与专业服务团队。它不是一组通用提示词，而是把品类投资、竞争情报、产品、供应采购生产质量、定价财务、履约、页面、广告、达人、内容、营销品牌与客户增长连接成可独立运行、跨域协同和持续进化的专业决策系统。

系统当前包含十三个已完成 L1—L3 专家级仓库建设的专业决策域、ERDG（Economic, Risk & Decision Governance）治理底座，以及当前可用的 F01 实验与因果评估共享底座。D05/LTMA 覆盖商业市场准入 Gate、动作上限、Claim 使用边界、适格专业复核路由、动态规则、事故恢复和临时合同迁移；它不签发法律、税务、FTO、认证或实验室意见。系统成熟度保持 `controlled_pilot`；L4 尚未关闭，任何真实生产决策、高风险用途或外部写入均不可用。

CIDM现包含受治理的`OSL-v1`机会信号层：以clean-room方式把外部研究启发归并为八类确定性候选信号，覆盖多源字段质量、五类组合剧本、有效供给/VOC、CIDM→PLCO Proof交接、部分失败DAG、R0–R4恢复、独立Oracle和13项源码mutation。该信号层只扩大候选池，不能直接改变七维评分、资本姿态或跨域主权；授权20例盲选回放、20人非实现者理解测试和前向校准仍未完成，因此不构成生产成熟度声明。

### OSL-v1 机会信号结构

```mermaid
flowchart TB
    subgraph IN["① 证据接入"]
      direction LR
      RAW["外部研究<br/>原始证据"] --> ADP["Evidence Adapter<br/>字段归一 · 时效 · 来源家族 · 血缘"]
      ADP --> CON["信号合同<br/>对象 · 时间窗 · 反证 · 替代解释"]
    end
    subgraph CORE["② 信号计算"]
      direction LR
      MOD["8 类<br/>确定性模型"] <--> ORA["独立 Oracle<br/>状态与指标双算"]
      ORA --> SIG["12 类<br/>规范信号"]
    end
    subgraph DEC["③ 决策治理"]
      direction LR
      PLAY["5 类组合剧本<br/>Required · Supporting<br/>Counter · Veto"] --> GATE["CIDM 五道门槛<br/>七维评分"]
      GATE --> CARD["Rapid Decision Card<br/>进入 · 小测 · 观察 · 不进入"]
    end
    subgraph REC["④ 失效恢复"]
      direction LR
      DRIFT["证据失效<br/>字段漂移 · 口径变化"] --> FREEZE["冻结受影响动作"]
      FREEZE --> RECOMPUTE["影响闭合 · 逐域重算<br/>生成新有效决策"]
    end
    CON --> MOD
    SIG --> PLAY
    CARD --> HAND["受控跨域交接<br/>PPFC · SPPQ · LIFD · PLCO"]
    GATE -->|触发红线 / Veto| BLOCK["Blocked<br/>不可被高分补偿"]
    CARD -.证据失效.-> DRIFT
    RECOMPUTE -.重新进入证据接入.-> RAW
    EXT["外部门仍关闭<br/>20例盲选回放 · 20人非实现者测试 · 前向校准"] -.限制成熟度.-> CARD
    classDef evidence fill:#e8f1ff,stroke:#3269a8,color:#17324d
    classDef signal fill:#eaf7f0,stroke:#31845c,color:#153b2a
    classDef decision fill:#fff4d8,stroke:#a87716,color:#4d3810
    classDef recovery fill:#f3ecff,stroke:#7652a8,color:#34234d
    classDef stop fill:#ffe9e7,stroke:#b84a42,color:#541e1a
    class RAW,ADP,CON evidence
    class MOD,ORA,SIG signal
    class PLAY,GATE,CARD,HAND decision
    class DRIFT,FREEZE,RECOMPUTE recovery
    class BLOCK,EXT stop
```

这张图展示的是“候选发现如何受治理”，不是另一套投资评分器。机会信号必须经过证据接入、合同校验、确定性模型与独立双算，再进入组合剧本和 CIDM 原有门槛；任何红线、否决条件或证据失效都优先阻断并触发恢复。信号层无权直接批准投资、备货、页面或广告动作。

## 系统价值与长期壁垒

大模型会持续变强，单次生成内容的成本也会持续下降。真正具有长期价值的不是某一个模型，而是建立在模型之上的专业决策基础设施。

CrossBorder Decision Lab 将跨境经营中分散、隐性的个人经验，转化为可以复用和持续积累的系统能力：

- 把模糊问题拆成明确的决策对象、约束、证据、反事实和责任边界；
- 把“感觉可行”转化为可复算的经济模型、实验方案和行动门槛；
- 把单点分析连接成品类、竞争、内容、客户、广告、供应链、页面、渠道与品牌的协同决策；
- 把成功、失败、异常、停止和退出都纳入同一套经营闭环；
- 把每次使用沉淀为可追溯的判断、动作、结果、修正和业务基准。

系统价值与长期壁垒是同一件事：系统解决的问题越重要，进入真实经营流程越深，积累的决策资产越多，后续决策就越准确、越高效，也越难被简单复制。

```text
专业决策框架与数学模型
            ↓
进入真实跨境经营工作流
            ↓
沉淀“问题—证据—判断—动作—结果”
            ↓
形成国家、平台、品类与生命周期业务基准
            ↓
持续校准模型、门槛、反例与决策路径
            ↓
提升决策质量、协作效率与经营确定性
            ↓
形成数据资产、工作流、专业治理与组织信任壁垒
```

### 为什么它不容易被更强的通用模型替代

通用模型可以理解材料、生成方案和辅助推理，但不会天然拥有一套企业长期积累的：

1. 决策对象和专业主权边界；
2. 历史判断、版本变化与责任链；
3. 国家、平台、品类、价格带和生命周期基准；
4. 成功、失败、异常、停止和退出案例；
5. 业务动作与后续经营结果之间的连续反馈；
6. 跨团队共同使用的证据、计算和审批语言。

模型是可以升级和替换的推理引擎；CrossBorder Decision Lab 保留的是模型之上的专业方法、经营上下文、计算工具、协作协议和持续复利的决策资产。

### 面向长期使用的复利机制

每一次实际使用都会增加系统的长期价值：

- 新问题扩展专业场景覆盖；
- 新证据丰富国家、平台和品类基准；
- 新动作补充经营策略与执行边界；
- 新结果修正参数、门槛和反事实；
- 新失败转化为反例、压力测试和阻断条件；
- 新协作沉淀为可追溯、可复用的组织工作流。

这使系统从“能够回答专业问题”，逐步发展为“能够持续管理专业决策”。

## 系统结构

### D01—D14 目标架构

```mermaid
flowchart TB
    U["经营问题 · 事件 · 新证据"] --> D14["D14 跨域协同姿态与决策编排<br/>规划中"]
    D14 --> D01["D01 CIDM<br/>资本与组合决策"]
    D14 --> D02["D02 CIM<br/>竞争事实"]
    D14 --> D03["D03 PIPM<br/>产品定义"]
    D14 --> D05["D05 LTMA<br/>合规与市场准入"]
    D14 --> D06["D06 PPFC<br/>定价、利润与现金"]
    D01 --> D03 --> D04["D04 SPPQ<br/>供应采购生产质量"] --> D07["D07 LIFD<br/>物流、库存与履约"]
    D07 --> D12["D12 MBCM<br/>营销、品牌与活动"]
    D12 --> D11["D11 VLB<br/>内容创意"]
    D12 --> D10["D10 CAPM<br/>达人联盟"]
    D11 --> D08["D08 PLCO<br/>平台与转化"]
    D11 --> D09["D09 AAMO<br/>广告测量"]
    D10 --> D08
    D10 --> D09
    D08 --> D13["D13 CIG<br/>客户、体验与增长"]
    D09 --> D13
    D02 -.事实与持续监测.-> D01
    D05 -.准入与持续合规.-> D04
    D06 -.经济与现金边界.-> D04
    D13 --> O["动作、客户与经营结果"]
    O --> D06 --> D01 --> D14
    O -.质量、竞争、规则与客户反馈.-> D02
    O -.质量、竞争、规则与客户反馈.-> D04
    O -.质量、竞争、规则与客户反馈.-> D05
    E["ERDG 治理控制面<br/>对象 · 证据 · 计算 · 经济 · 风险 · 状态 · 参数 · 血缘"] -.治理.-> D14
    F["F01 实验与因果评估<br/>协议 · 估计量 · CE0—CE5 · 诊断 · 复现"] -.因果与增量 Claim 资格.-> D01
    F -.因果与增量 Claim 资格.-> D06
    F -.因果与增量 Claim 资格.-> D12
    O -.授权结果回放与校准.-> F
    E -.合同与发布治理.-> F
    E -.合同与红线校验.-> D01
    E -.合同与红线校验.-> D04
    E -.合同与红线校验.-> D12
    O -.回放与参数校准.-> E
    classDef planned stroke-dasharray:6 5
    class D14 planned
```

图中十三域与 F01 为当前可运行能力；D14 为规划域，注册表和校验器禁止其提前进入执行。各专业域继续保留最终专业主权；F01 只裁定实验设计、因果/增量 Claim 资格与证据等级，不作业务最终决定；D14 只负责编排、冲突升级，以及在各 owner 已批准结论和资源边界内合成协同姿态与安排顺序，不裁决专业结论、不批准资本、不拥有外部写入。ERDG 只做中立治理与确定性计算，不替代任何专业域作出业务结论。

### D01—D14 连续决策闭环

```mermaid
sequenceDiagram
    actor U as 用户/经营事件
    participant D14 as D14 编排（规划）
    participant D02 as D02 CIM
    participant D13 as D13 CIG
    participant D01 as D01 CIDM
    participant D03 as D03 PIPM
    participant D04 as D04 SPPQ
    participant D05 as D05 LTMA 合规与市场准入
    participant D06 as D06 PPFC
    participant D07 as D07 LIFD
    participant M as D12/D11/D10/D08/D09 市场域
    participant E as ERDG
    U->>D14: 问题、事件或新证据
    par 事实与约束
      D14->>D02: 竞争事实
      D14->>D13: 客户证据
      D14->>D06: 经济与现金边界
      D14->>D05: 合规与准入
    end
    D14->>E: Gate G0 证据资格
    E-->>D14: 通过 / 降级 / 阻断
    D14->>D01: 资本姿态
    D01-->>D14: 预算、停止与退出边界
    D14->>D03: 产品定义
    D03-->>D14: Product Definition Packet
    par 产品落地
      D14->>D04: 供应、样品、产能与质量
      D14->>D06: 产品经济重算
      D14->>D05: 产品正式准入
    end
    D14->>E: Gate G2 产品—供应—经济—准入
    E-->>D14: 通过 / 部分接受 / 阻断
    D04->>D07: 合格批次、产能与交期
    D07-->>D14: ATP/CTP、履约与逆向计划
    D14->>M: 定位、内容、达人、页面与广告并行协作
    M-->>D13: 转化、获客、服务与伙伴结果
    D13-->>D14: Outcome Packet
    par 经营复盘
      D14->>D06: 实际经济重算
      D14->>D02: 竞争变化复盘
      D14->>D04: 质量与供应恢复
      D14->>D05: 持续合规复盘
    end
    D14->>E: Gate G5 血缘闭合与选择性重算
    E-->>D14: child cycle 与影响闭包
    D14->>D01: 实际经营结果
    D01-->>D14: 追加 / 维持 / 收缩 / 退出
    D14-->>U: 新的当前有效经营姿态
```

连续时序只展示跨阶段主链；市场域组中的五个 Skill 仍各自拥有主权，并通过标准 Packet 交接。完整 D01—D14 注册表位于 [`governance/domain-architecture-registry.json`](governance/domain-architecture-registry.json)。全系统统一使用 v2 交接与 Decision Cycle；旧 v1 运行主链已经退役。

## Skill 快速定位

按“需要做什么决策”选择主 Skill。每个 Skill 的平台覆盖、专业模型、执行流程、输入输出和失败边界，请进入对应目录查看。

| Skill | Runtime | 主要解决的问题 | 专业入口 |
|---|---|---|---|
| **CIDM** | `CIDM-2026.07` + `OSL-v1` | 什么值得进入、投资、测试、放量、收缩或退出？外部信号只生成受治理候选。 | [品类投资决策](category-investment-decision/SKILL.md) |
| **CIM** | `CIM-2026.07` | 竞品是谁、发生了什么变化、为什么重要、如何响应？ | [竞品情报监控](competitive-intelligence-monitoring/SKILL.md) |
| **VLB** | `VLB-2026.07` | 内容为什么有效、能否迁移、如何生产、测试和规模化？ | [内容创意与传播](video-link-breakdown/SKILL.md) |
| **CIG** | `CIG-2026.07` | 客户是谁、需求和阻力是什么、什么是真增量、如何增长？ | [消费者洞察与客户增长](consumer-insights-customer-growth/SKILL.md) |
| **AAMO** | `AAMO-2026.07` | 广告能否投、问题在哪里、真实增量多少、如何配置和停止？ | [广告分析、测量与优化](advertising-analysis-measurement-optimization/SKILL.md) |
| **LIFD** | `LIFD-2026.07` | 走什么路线和仓、何时补货、库存怎么分、如何履约和退出？ | [物流、库存与履约](logistics-inventory-fulfillment-decision/SKILL.md) |
| **PLCO** | `PLCO-2026.07` | 店铺和页面能否承接，标题、主图、详情或落地页具体怎么改？ | [平台、店铺与转化](platform-store-listing-conversion/SKILL.md) |
| **CAPM** | `CAPM-2026.07` | 找谁合作、如何报价、寄样、签约、购买权利、经营联盟和退出？ | [达人与联盟经营](creator-affiliate-partnership-management/SKILL.md) |
| **MBCM** | `MBCM-2026.07` | 如何分层、定位、上市、建设品牌、组织活动和编排营销资源？ | [营销、品牌与活动](marketing-brand-campaign-management/SKILL.md) |
| **PPFC** | `PPFC-2026.07` | 售价、利润、贡献、保本指标、财务约束和现金风险应该如何计算与调整？ | [定价、利润、财务与现金流](pricing-profit-finance-cashflow-decision/SKILL.md) |
| **PIPM** | `PIPM-2026.07` | 产品机会如何转化为可验证的产品定义、规格、MVP和路线图？ | [产品创新与产品管理](product-innovation-product-management/SKILL.md) |
| **SPPQ** | `SPPQ-2026.07` | 供应商是否可信、采购能否承诺、生产和批次是否可以放行、事故如何恢复？ | [供应商、采购、生产与质量](supplier-procurement-production-quality-decision/SKILL.md) |
| **LTMA** | `LTMA-2026.07` | 当前证据下能否继续商业准备，哪些动作须阻断、补证或交适格专业主体复核？ | [法律、税务、IP 与市场准入](legal-tax-intellectual-property-market-access-decision/SKILL.md) |

共享底座不拥有业务最终决策主权：

| Foundation | Runtime | 主要解决的问题 | 专业入口 |
|---|---|---|---|
| **F01 / ECAE** | `ECAE` · `controlled_pilot` | 实验是否可执行、因果量是否可识别、结果可声称到什么等级、何时必须降级或重做？ | [实验与因果评估](experiment-causal-assessment/SKILL.md) |

## 统一决策基础设施

十三个专业域通过 [`ERDG-CONTRACT-2026.07`](governance/erdg/ERDG.md) 共享一套底层决策原则，并通过 [F01 实验与因果评估](experiment-causal-assessment/SKILL.md) 统一实验协议、估计量、CE0—CE5 证据等级、诊断、复现和因果 Claim 上限。ERDG 负责结构安全、确定性公共计算和跨域合同校验；F01 负责因果证据资格；各 Skill 继续拥有专业模型、阈值与最终业务决策。

模型交互前由 [`Prompt Intake Guard`](governance/interaction/interaction-governance.md) 把请求路由为回答、补数、研究、计算或阻断；ERDG 通过后的 Decision Packet 才能编译为面向运营的 Operator Playbook。动态平台知识使用带来源、证据等级、复核日和失效条件的 [平台知识卡](governance/platform-knowledge/platform-knowledge-contract.md)；外部数据按 [Connector 合同](governance/connectors/connector-governance.md) 接入，当前均为只读合同，不授权外部写入。

1. **证据与反证**：观察、用户输入、授权数据、外部基准、推断和假设分开记录。
2. **数学与守恒**：利润、增量、容量、组合和风险通过可复算模型计算。
3. **专业主权**：资本、广告、客户、页面、履约、内容、伙伴和品牌结论不互相越权。
4. **版本与血缘**：对象、证据、计算、结论和动作均保留版本与来源。
5. **连续追问**：新信息只重算受影响部分，不静默覆盖历史判断。
6. **动作闭环**：每个结论绑定责任人、资源、观察窗、成功条件、停止和回滚。
7. **失败治理**：缺失、冲突、污染、异常、事故、收缩和退出均有明确处理路径。
8. **长期校准**：随着持续使用，逐步形成适配国家、平台、品类和生命周期的经营基准。

## 当前能力

当前版本已经形成十三个可独立运行、可跨域联动的专业决策 Skill，并完成：

- 专业场景与生命周期覆盖；
- 确定性经济模型与统计估计工具；
- 单 Skill、跨 Skill 和连续追问执行；
- 极端组合、冲突、缺失、失败和压力测试；
- 证据、计算、结论、动作和版本血缘；
- 专业主权、风险红线、停止、回滚与退出治理；
- 仓库级自动化校验和发布门禁。

十三域专业工程门以 [`governance/professional-engineering-release.md`](governance/professional-engineering-release.md) 为统一口径。当前发布快照将 13 个域的 790 个源案例、Golden、语义验证器和数值复算入口绑定到带指纹的规范化索引，执行 29 个专业验证入口，并用 12 类防篡改突变证明关键守卫不能被静默删除或放宽。F01 已完成 L1—L3、163 项测试、23 种方法的来源绑定与 13/13 消费者受控试点接受；其 91 个只读预检案例没有生产证据声明。运行 `python3 scripts/validate_release_integrity.py` 和 `python3 scripts/validate_f01_release.py --require-l3` 复算发布状态。L4 的生产双跑、真实结果校准、高级后端外部资格和非实现者独立复核单独管理；工程门通过不等于 production-ready，也不会授权外部写入或解冻规划中的 D14。

系统不依赖固定的大模型供应商。模型可以持续升级，专业决策合同、计算工具、业务基准和历史资产保持连续。

## 如何使用

### 1. 直接描述决策问题

例如：

- “这个品类是否值得进入美国 Amazon？”
- “竞品最近为什么突然增长？”
- “这条视频为什么有效，适不适合我的产品？”
- “这批客户为什么没有复购？”
- “广告有订单但没有利润，应该怎么处理？”
- “现在应该补多少库存、走哪个仓？”
- “这个 Listing 的主图和详情页具体怎么改？”
- “这个达人值不值得寄样和签约？”
- “新品应该如何定位、上市和组织营销活动？”
- “不同平台费率和陆海空运成本变化后，售价、利润和保本 ROAS 应该是多少？”

### 2. 由主 Skill 完成专业判断

主 Skill 固定对象、证据、约束和决策目标，调用相应模型并输出行动、成功条件、停止规则和需要承接的其他专业域。

### 3. 按需进行跨 Skill 联动

复杂问题可以由多个 Skill 交换经过版本化的证据和约束，但最终结论仍由拥有该决策主权的 Skill 给出。

### 4. 持续回填与校准

实际动作和经营结果回填后，系统更新业务基准、参数、反例和下一阶段决策。

## 仓库导航

| 位置 | 内容 |
|---|---|
| 十三个专业 Skill 目录 | 各专业域的入口、工作流、模型、参考资料和测试 |
| [`evaluations/`](evaluations/) | 单 Skill、跨 Skill、连续追问、对抗与极端场景 |
| [`governance/`](governance/) | 主权、成熟度、变更影响与共享治理合同 |
| [`governance/erdg/`](governance/erdg/ERDG.md) | ERDG 经济、风险、证据、状态、参数、血缘与跨域决策治理底座 |
| [`experiment-causal-assessment/`](experiment-causal-assessment/SKILL.md) | F01 实验设计、因果资格、证据分级、诊断、复现、消费者接受与 L4 预留门 |
| [`governance/foundation-capability-registry.json`](governance/foundation-capability-registry.json) | F01/F02 共享底座身份、能力、消费者、主权和成熟度 |
| [`governance/interaction/`](governance/interaction/interaction-governance.md) | Prompt Intake Guard 与 Decision Packet → Operator Playbook 编译控制 |
| [`governance/platform-knowledge/`](governance/platform-knowledge/platform-knowledge-contract.md) | PLCO、AAMO、LIFD 的版本化平台知识卡与失效门 |
| [`governance/connectors/`](governance/connectors/connector-governance.md) | SP-API、Seller Central、广告与 ERP 的只读证据接口和 Action Gateway |
| [`scripts/`](scripts/) | 全仓校验、质量评分、集成与发布门禁 |
| [`.github/workflows/expert-release.yml`](.github/workflows/expert-release.yml) | 自动化发布质量门 |
| [`requirements-dev.txt`](requirements-dev.txt) | 本地与自动化校验使用的锁定依赖 |
| [`RULES.md`](RULES.md) | 仓库维护、版本、测试和发布规则 |

## 质量与安全边界

- 动态平台规则、法规、价格和市场事实在执行时按日期核验。
- 平台归因、相关性、预测和因果增量保持严格区分。
- L4 未关闭前，真实生产决策、高风险用途、自动执行和外部写入必须失败关闭；合成或只读预检不得冒充生产证据。
- 财务结论区分事实、用户输入、外部基准和情景假设。
- 法律、税务、知识产权和监管事项保留适格专业主权。
- 系统不支持虚假互动、欺骗性宣传、侵权、刷评或规避平台规则。
- 内容迁移聚焦可转移机制和测试逻辑，不复制受保护表达。

## Copyright

Copyright © 2026 Miles Chen. All rights reserved.

CrossBorder Decision Lab / 出海决策实验室及其原创决策框架、评分模型、工作流、文档和代码受版权保护。未经版权所有者事先书面许可，不得复制、修改、分发、转授权、销售、商业使用或基于本仓库内容制作衍生作品。详见 [LICENSE](LICENSE)。
