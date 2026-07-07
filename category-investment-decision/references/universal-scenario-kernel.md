# 全场景通用内核

## 定位

本文件只在主 Skill 轻量路由表和 `selection-scenarios.md` 都无法明确判断时使用，用于兜底未被覆盖的国家、平台、商品、业务阶段或用户表达。先用通用内核识别任务，再加载具体参考文件。

不要因为场景表没有完全匹配就输出泛泛建议；必须把任务归入“决策类型 × 对象类型 × 输出格式”。

若任务包含进入、投资、上架、放量或放弃建议，默认输出仍使用完整专业报告骨架；通用内核只决定挂载模块和补数清单。用户明确要求快速、卡片、清单、月报，或任务不产生新的投资判断时，可以压缩展示，但仍要保留专业判断闭环。

## 六个通用问题

1. **这次要做什么决策？**
   Enter、Screen、Reverse、Compare、Monitor、Diagnose、Scale、Maintain、Reduce、Stop、Review。

2. **输入对象是什么？**
   Category、Product、ASIN/Link、Store、Keyword、Country、Platform、Portfolio、Experiment、Supplier、Creative、Review/VOC。

3. **哪些证据必须有？**
   需求、竞争、利润、合规、供应链、流量、VOC、国家本地化、平台规则、经营数据。

4. **哪些未知会推翻结论？**
   合规/IP/安全红线、利润压力场景、不可验证需求、供应商报价、物流尺寸、平台准入、样本不足。

5. **应该挂载哪些模块？**
   Full Report 骨架下挂载 Reverse、Matrix、Country、Platform、VOC、Keyword、Experiment、Operating、Exit 或 Checklist 模块。

6. **下一步动作是什么？**
   验证、进入、监控、修复、加码、收缩、停止、复核、补数。

## 决策类型路由

| 决策类型 | 触发语 | 默认输出骨架 | 必须回答 |
|---|---|---|---|
| Enter | 值不值得进入、能不能做 | Investment Memo | 进不进、怎么进、什么条件进 |
| Screen | 快速判断、初筛 | Compressed Investment Memo | 是否值得继续取证 |
| Reverse | 拆链接、拆 ASIN、拆竞品 | Investment Memo + Reverse Module | 可复制什么、不能复制什么 |
| Compare | 比较、选几个、排序 | Investment Memo + Matrix Module | 选谁、为什么、候补是谁 |
| Monitor | 监控、跟踪、月报 | Full Report or Monthly Report | 发生什么、是否告警、下次看什么 |
| Diagnose | 为什么不增长、哪里出问题 | Investment Memo + Diagnosis Module | 根因、修复动作、复查指标 |
| Scale | 放量、加码、扩 SKU | Investment Memo + Operating Module | 放多少、风险上限、监控指标 |
| Reduce | 收缩、降预算、清库存 | Full Report or Operating Review | 收缩哪些、释放多少资金 |
| Stop | 停止、清退、失败复盘 | Full Report or Exit Module | 为什么停、损失多少、学到什么 |
| Review | 复盘、回看实验 | Full Report or Experiment Module | 假设是否被验证或推翻 |

## 对象类型路由

| 对象 | 必查模块 |
|---|---|
| Category/Product | 五道门槛、七维评分、平台和国家 |
| ASIN/Link | 页面事实、流量代理、评论、利润、风险 |
| Store | SKU 结构、价格带、上新、流量承接、缺口 |
| Keyword | 词簇、意图、竞争、Listing/广告/内容应用 |
| Country | 消费者、法规、税务、进口、物流、语言 |
| Platform | 流量逻辑、费用、履约、准入、平台风险 |
| Portfolio | 单品评分、预算、负荷、集中度、协同 |
| Experiment | 事先门槛、样本、指标、异常、评分回写 |
| Supplier | 报价、MOQ、交期、质检、备选、合规资料 |
| Creative | 钩子、素材角度、达人适配、疲劳和转化 |

## 输出骨架选择

| 输出格式 | 适用情况 |
|---|---|
| Full Report | 完整投决、投委会、深度研究 |
| Compressed Investment Memo | 用户明确要求快速判断、卡片或单点决策，仍保留门槛、评分、利润/风险假设、关键证据和 Go/Stop |
| Matrix Module | 多国家、多平台、多候选比较，默认挂载到 Full Report |
| Monthly Report | 竞品、店铺、老品周期监控且不产生新投资判断 |
| Experiment Module | 测款设计或实验复盘，默认挂载到 Full Report |
| Operating Module | 上市后放量、稳态、衰退，默认挂载到 Full Report |
| Exit Module | 失败复盘、停止、清退，默认挂载到 Full Report |
| Checklist | 补数、合规、供应链或上架准备 |

## 兜底规则

- 未知国家：读取 `country-routing-universal.md`，按当前官方来源核验，不凭内置经验断言。
- 未知平台：读取 `platform-routing-universal.md`，先归类平台流量逻辑，再决定证据和利润口径。
- 未知品类：先做风险分类，再决定是否需要合规/IP/安全人工复核。
- 数据不足：输出可执行补数清单；不得为了完整报告编造精确数字。
- 多场景叠加：以最终商业决策为主场景，其他模块作为附录或补充表。
