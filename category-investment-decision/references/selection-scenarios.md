# 选品场景路由

## 路由原则

本文件只在主 Skill 的轻量路由表无法明确判断，或多场景冲突会改变输出骨架时读取。先用“决策类型 × 对象类型 × 输出格式”识别任务，再选择参考文件和报告模板。场景路由只决定取证重点、补充指标和附表，不修改五道门槛、七维评分及决策阈值。

商品链接反查、多候选组合、国家本地化、平台适配、关键词策略是横向模块，可以叠加到任何主场景。

一旦确定主场景和横向模块，就停止继续读取其他路由文件，直接进入对应专业参考文件。不要为了确认同一场景反复读取 `scene-output-protocols.md` 和 `universal-scenario-kernel.md`。

当用户表达不在本文件列举范围内，读取 `universal-scenario-kernel.md` 兜底；不要因为场景未列出就输出泛泛建议。

## 一、决策类型

| 决策类型 | 典型触发 | 默认输出骨架 | 关键问题 |
|---|---|---|---|
| Enter | 值不值得进入、能不能做 | Investment Memo | 是否进入、怎么进入、什么条件停止 |
| Screen | 快速判断、初筛、粗看 | Compressed Investment Memo | 是否值得继续取证 |
| Reverse | 拆链接、拆 ASIN、拆竞品 | Investment Memo + Reverse Module | 可复制什么、不能复制什么、风险在哪 |
| Compare | 比较、排序、预算选几个 | Investment Memo + Matrix | 选谁、为什么、候补是谁 |
| Monitor | 监控、跟踪、月报 | Full Report or Monthly Report | 发生什么、是否告警、下次看什么 |
| Diagnose | 为什么不增长、问题在哪 | Investment Memo + Diagnosis Module | 根因、修复动作、复查指标 |
| Scale | 放量、加码、扩 SKU | Investment Memo + Operating Module | 放多少、风险上限、监控指标 |
| Maintain | 稳态巡检、维持 | Full Report or Operating Review | 是否稳定、是否需要优化 |
| Reduce | 收缩、降预算、清库存 | Full Report or Operating Review | 收缩哪些、释放多少资金 |
| Stop | 停止、清退、失败复盘 | Full Report or Exit Memo | 为什么停、损失多少、学到什么 |
| Review | 复盘、实验回看 | Full Report or Experiment Review | 假设是否被验证或推翻 |

## 二、对象类型

| 对象类型 | 必查证据 | 横向模块 |
|---|---|---|
| Category / Product | 需求、竞争、利润、供应、风险、机会 | 国家、平台、关键词、VOC |
| ASIN / Link | 页面事实、价格、评论、流量代理、风险 | 竞品、VOC、利润 |
| Store | SKU 结构、价格带、上新、流量承接、缺口 | 店铺补品、监控 |
| Keyword | 词簇、意图、竞争、CPC/代理、Listing 应用 | 关键词策略 |
| Country / Region | 消费者、法规、税务、进口、物流、语言 | 国家本地化 |
| Platform | 流量逻辑、费用、履约、准入、平台风险 | 平台适配 |
| Portfolio | 单品评分、预算、负荷、集中度、协同 | 组合决策 |
| Experiment | 事先门槛、样本、指标、异常、评分回写 | 测款复盘 |
| Supplier | 报价、MOQ、交期、质检、备选、合规资料 | 供应链 |
| Creative / Content | 钩子、素材、达人、转化、疲劳 | 内容传播 |
| Review / VOC | 样本、痛点、反例、服务风险、切入楔子 | VOC 情报 |

## 三、输出格式

| 输出格式 | 使用场景 | 必须包含 |
|---|---|---|
| Investment Memo | 完整投决与所有正式场景 | 决策页、门槛、评分、利润、风险、行动、Evidence/Assumption Ledger |
| Compressed Investment Memo | 快速初筛 | 结论、门槛速判、粗评分、利润/风险假设、关键证据、Go/Stop |
| Reverse Module | 链接/ASIN 拆解 | 页面事实、可复制项、不可复制项、风险、评分 |
| Matrix Module | 多候选/多国家/多平台 | 横向表、排序、进入顺序、淘汰原因 |
| Monthly Report | 竞品/店铺/老品监控 | 范围、变化、告警、动作、下次检查 |
| Experiment Module | 测款设计/复盘 | 假设、指标、样本、Go/Iterate/Stop |
| Operating Module | 上市后经营 | KPI、告警、根因、Scale/Maintain/Review/Reduce/Stop |
| Exit Module | 退出复盘 | 初始假设、实际表现、损失、学习、下次规则 |
| Checklist | 补数/合规/上架准备 | 待确认项、责任角色、截止条件 |

## 常见场景映射

| 用户场景 | 决策类型 | 对象类型 | 输出格式 |
|---|---|---|---|
| 品类进入 | Enter | Category/Product | Investment Memo |
| 快速初筛 | Screen | Product/Category | Compressed Investment Memo |
| 商品链接反查 | Reverse | ASIN/Link | Investment Memo + Reverse Module |
| 多候选组合 | Compare | Portfolio | Investment Memo + Matrix Module |
| 国家比较 | Compare | Country/Region | Investment Memo + Country Matrix |
| 平台适配 | Compare / Enter | Platform | Investment Memo + Platform Fit |
| VOC/竞品情报 | Review | Review/VOC + Competitor | Investment Memo + Intelligence Module |
| 关键词策略 | Review | Keyword | Investment Memo + Keyword Module |
| 竞品监控月报 | Monitor | ASIN/Store | Full Report or Monthly Report |
| 店铺补品 | Diagnose / Enter | Store/Product | Investment Memo + SKU Gap Matrix |
| 老品延展 | Scale | Product | Investment Memo + Operating Module |
| 老品诊断 | Diagnose | Product | Investment Memo + Diagnosis Module |
| 测款设计 | Review | Experiment | Investment Memo + Experiment Module |
| 测款复盘 | Review | Experiment | Full Report or Experiment Review |
| 上市后巡检 | Maintain / Scale / Reduce | Product | Full Report or Operating Review |
| 退出复盘 | Stop / Review | Product/Experiment | Full Report or Exit Memo |
| 季节选品 | Enter / Screen | Product/Category | Investment Memo / Compressed Investment Memo |
| 趋势爆品 | Screen / Enter | Product/Category | Compressed Investment Memo / Investment Memo |
| 榜单反查 | Reverse / Screen | Category/ASIN | Investment Memo + Reverse Module |

## 使用要求

- 多场景冲突时，以最终商业决策确定主场景；其他模块作为横向附表。
- 国家或区域相关任务必须落到具体国家；区域只用于选择候选国家。
- 平台未覆盖时先判断平台类型，不套用 Amazon、TikTok 或 Temu 逻辑。
- 监控、月报、复盘和诊断默认挂载到完整报告骨架；若用户明确要求月报/卡片或未产生新的投资判断，可以压缩 STEP1-STEP8 展示，但仍要保留专业判断闭环。只有触发投资判断变化时才重新评分。
- 链接反查页面不可访问时，使用用户提供的截图、导出或页面文本；不得凭 ASIN 猜测页面事实。
- VOC/竞品必须披露原始与去重样本量、来源偏差和反例；样本内频率不外推为市场比例。
- 多候选决策先按同一证据截止日和基础模型分别评分，再做资源约束组合。
- 测款验证事先定义主假设、主指标、最小样本、红线和迭代上限；实验结果回写原评分版本。

## 批量机会记录

用户要求批量候选、机会池、CSV/Excel 或持续复盘时，增加以下字段；单品报告不强制展示：

- 基础：商品方向、类目、平台、国家、价格带、来源场景、来源链接。
- 判断：总分、七维原始分、风险等级、整体/维度置信度、推荐动作、切入楔子。
- 审计：数据日期、评分模型版本、人工复核、复核结论、放弃原因。
- 验证：批次、曝光、CTR、CVR、订单、净利、退货、周转、测款结论。

建议状态：`待评估 -> 待验证 -> 测试中 -> 已验证 / 已放弃 -> 放量 / 清退`。不要把“已分析”等同于“已验证”。
