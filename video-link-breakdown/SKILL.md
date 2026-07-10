---
name: video-link-breakdown
description: 用中文深度拆解用户提供的视频链接，输出秒级节奏图谱、情绪曲线、脚本结构、剪辑语法、平台算法适配、内容质量加权评分、受众分层、竞争定位、变现漏斗、复刻成本、跨文化适配、A/B假设与优化建议。适用于 TikTok、YouTube Shorts、Instagram Reels、X/Twitter 视频、Bilibili、抖音、TikTok Shop、Shopee Video、Pinterest 等链接；当用户要求"拆解这个视频""分析脚本/剪辑/节奏/钩子/内容质量""复刻这个视频""改写短视频脚本""为什么这个视频能火""这个视频值不值得抄""出海/本地化分析""这个视频打法能不能用到我的产品""帮我设计 TikTok Shop 视频策略""达人矩阵怎么分配""视频带货的利润测算"或提供视频链接希望做内容策略分析或跨境电商视频商业决策时使用。
---

# Video Link Breakdown — 专业级短视频内容拆解

运行时版本：`VLB-2026.07`。

Use this skill to turn an arbitrary video link into a **strategic content teardown** at professional creator/CMO level. The goal is not just to describe what the video does, but to reverse-engineer why it works (or fails), how it fits its platform algorithm, who it targets, what it converts, and what it costs to replicate.

Prefer running the bundled preparation script first so metadata, local video, and keyframes are gathered consistently. The script downloads video only as a temporary analysis artifact by default, then deletes the original video after successful frame extraction.

## Quick Workflow

1. Resolve the installed skill directory and create a unique temporary task folder:

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/video-link-breakdown"
TASK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/video-link-breakdown.XXXXXX")"
python3 "$SKILL_DIR/scripts/prepare_video_link.py" "<video-url>" --out "$TASK_DIR"
```

2. Read `$TASK_DIR/summary.json`.
3. If `$TASK_DIR/contact_sheet.jpg` exists, inspect it with the image viewer before analyzing.
4. Expect the downloaded source video to be deleted after frames are extracted. Use `--keep-video` only when the user explicitly wants a local archive.
5. If downloaded video exists but no frames were extracted, try an alternate local media tool only if needed.
6. If the script reports `needs_user_input`, ask only for the missing artifact: uploaded video file, transcript/subtitles, screenshots, or a platform-accessible mirror.
7. After delivering the analysis, remove `$TASK_DIR` and verify it no longer exists. If cleanup fails, report the remaining path and reason.

Do not modify the user's Python environment by default. If dependencies are missing, report the explicit install command; use `--install-missing` only after the user authorizes environment changes.

## Core Principle: Observed vs. Inferred

Always separate what was **observed** (from frames, audio, on-screen text, metadata) from what is **inferred** (psychology, algorithmic behavior, business model, audience intent). If inference is critical to the conclusion, label it explicitly.

If there is no transcript or audio transcription, state that script analysis is based on visual structure, title, on-screen text, and editing flow. Do not fabricate dialogue.

Maintain an evidence ledger for decision-relevant claims:

- `O` — observed directly in frames, audio, subtitles, or on-screen text;
- `M` — visible metadata, account data, or platform analytics;
- `U` — user-provided product, cost, audience, or operating data;
- `B` — external benchmark with market, category, source, and date;
- `I` — inference that still requires validation.

Retention, audience, algorithm, and ROI claims must cite one of these identifiers. Never present `I` or a generic `B` as observed performance.

## Scenario Routing

Choose one primary route before analysis. Routes change emphasis and presentation, not evidence standards.

| User goal | Primary route | Required emphasis |
|---|---|---|
| Break down one video | Single-video teardown | observed beats, rhythm, persuasion, reusable pattern |
| Compare videos | Competitive comparison | normalized comparison matrix, common baseline, winner by objective |
| Diagnose an account | Account diagnosis | recent 10-20 posts, content roles, stage, distribution and conversion trend |
| Decide whether a video can sell | Commerce decision | commercial gates, unit economics, content-to-commerce bridge, Go/Iterate/Stop |
| Rewrite a script | Script optimization | evidence-backed failure point, revised beat sheet, A/B plan |
| Build a creator/material system | Scale system | template variance, creator tiers, cost, fatigue and stop rules |

For very short videos or incomplete evidence, merge adjacent dimensions into a concise complete report. Do not invent missing sections or mechanically repeat “unknown.” Cross-border commerce reports retain all decision components but may consolidate the 16 headings.

## Output Framework: 十二维度拆解

Respond in the user's language. Be direct and practical. Favor reusable patterns over vague praise. Use the following structure unless the user asks for a different format.

---

### 一、基础信息与元数据

- **平台**：TikTok / 抖音 / YouTube Shorts / Instagram Reels / Bilibili / TikTok Shop / Shopee Video / Pinterest / 其他
- **创作者**：账号名、粉丝量级（若可见）、账号定位标签
- **标题/描述/话题标签**：原文及策略解读
- **时长与画幅**：精确到秒，竖屏/横屏/比例
- **可见互动数据**：点赞、评论、转发、收藏、播放量（注明数据抓取时间点）
- **音乐/音效**：原声、热门BGM、音效使用方式
- **发布时间**：若可见，分析时段选择逻辑

### 二、战略诊断（一句话+三段论）

用一句话概括视频的核心策略，再用三段论展开：
1. **它想达到什么目标？**（曝光、涨粉、带货、引流私域、建立人设、引发讨论）
2. **它选择的核心冲突/欲望是什么？**（好奇、恐惧、共鸣、嫉妒、愤怒、爽感）
3. **它的差异化锚点在哪？**（与同类内容相比，凭什么被记住）

### 三、秒级节奏图谱与注意力审计

这是拆解的核心。将视频按 **3-5 秒为一个时间单位**（短视频）或 **5-10 秒为一个时间单位**（中视频）进行切片：

| 时间段 | 画面内容 | 信息密度 | 情绪值 | 注意力风险 | 功能定位 |
|---|---|---|---|---|---|
| 0-3s | ... | 高/中/低 | 峰值/上升/平稳/下降 | 低/中/高 | Hook |
| ... | ... | ... | ... | ... | ... |

**信息密度**：单位时间内传递的新信息量。高密度适合知识/干货，低密度适合情绪/氛围。
**情绪值**：-5 到 +5，标注情绪类型（好奇、紧张、爽、感动、愤怒、幽默）。
**注意力风险**：该时段导致用户划走的概率估计。风险高 = 节奏拖沓、信息重复、情绪断档。
**功能定位**：Hook / 铺垫 / 证明 / 转折 / 高潮 / Payoff / CTA

画出一条 **情绪曲线**（Emotion Arc），标注：
- 峰值点（情绪最高点，通常对应完播节点）
- 低谷点（是否有不必要的情绪回落导致掉人）
- 钩子留存率预测（前3秒、前5秒、前8秒分别能留住多少百分比观众）

### 四、脚本结构拆解（Beat-by-Beat）

拆解每一个叙事节拍：

| 节拍 | 时间 | 内容 | 叙事功能 | 心理学机制 |
|---|---|---|---|---|
| Hook | 0-3s | ... | 打断用户滑动 | 好奇心缺口 / 认知冲突 |
| Setup | ... | ... | 建立情境/问题 | 共鸣/代入 |
| Proof 1 | ... | ... | 第一个证据/故事推进 | 可信度累积 |
| Turn | ... | ... | 转折/反预期 | 惊喜/情绪翻转 |
| Proof 2 | ... | ... | 强化论证 | 社会认同/数据 |
| Payoff | ... | ... | 释放价值/给出答案 | 多巴胺释放 |
| CTA | ... | ... | 引导下一步 | 损失厌恶/稀缺性 |

对每个节拍回答：
- 如果这个节拍被删除，视频会不会塌？
- 这个节拍是否可以前置/后置来提升留存？

### 五、剪辑语法与视听语言拆解

超越 checklist，进入视觉语法分析：

**1. 镜头序列与衔接**
- **匹配剪辑**：动作匹配、图形匹配、视线匹配、色彩匹配——这些匹配创造了什么语义关联？
- **运动连贯性**：摄像机运动方向是否保持了空间逻辑？有没有故意打破连贯性制造跳跃感？
- **景别变化**：远景→特写（强调细节）、特写→远景（释放情绪）的节奏模式。
- **轴线与越轴**：是否利用越轴制造混乱/紧张？

**2. 声画关系**
- **J-cut / L-cut**：声音先入或画面先入如何影响信息接收节奏？
- **对位/平行**：画面和声音是同步解释，还是对位制造反讽/张力？
- **ASMR/环境音**：哪些声音设计增强了沉浸感？

**3. 字幕与信息层**
- 字幕是 decorative（装饰性）还是 informational（信息性）？
- 关键信息是否被高亮（变色、放大、动画）？
- 多信息层并行时（画面+字幕+贴图+音效），认知负荷是否过载？

**4. 视觉焦点与引导**
- 第一眼会落在哪里？（热区预测）
- 视线如何在画面内移动？（Z型、F型、螺旋型）
- 产品/人物的 framing 是否符合平台审美（抖音重怼脸，YouTube Shorts 重场景）？

### 六、平台算法适配度分析

不同平台有不同的"算法心智"，同一个视频在不同平台的命运完全不同。

| 维度 | 抖音/TikTok | YouTube Shorts | Bilibili | Instagram Reels | TikTok Shop | Shopee Video | Pinterest Video |
|---|---|---|---|---|---|---|---|
| **分析指标候选** | 完播、观看时长、互动、分享 | 观看时长、划走率、回访、互动 | 观看时长、弹幕、收藏、三连 | 停留、分享、保存、互动 | GPM、商品点击、CVR、退货 | 商品点击、CVR、店铺关注 | 保存、外链点击、站外转化 |
| **时长测试起点** | 15-60s，按账号基线分层 | 20-60s，并测试更长叙事 | 按内容深度分层测试 | 10-45s，按目标测试 | 15-60s，按类目与客单测试 | 20-90s，按演示复杂度测试 | 6-30s，测试循环与保存 |
| **Hook偏好** | 视觉冲击/强冲突 | 问题前置/悬念 | 梗/文化共鸣 | 美学冲击/生活方式 | 痛点前置+产品效果对比+价格锚定 | 价格优势+使用效果+本地化信任 | 美学灵感+场景化+DIY感 |
| **互动设计** | 评论区造梗 | 订阅引导 | 弹幕互动 | 标签挑战 | 购物车引导+评论区答疑+达人信任背书 | 店铺关注+优惠券领取+聊天引导 | 板块保存+链接点击+站外引流 |
| **音乐策略** | 热门BGM跟拍 | 原创/无版权优先 | 原声/鬼畜改编 | 趋势音乐 | 原声解说+轻BGM（不抢产品信息） | 本地热门音乐+原声解说 | 氛围感音乐+ASMR |
| **电商功能** | 小黄车（内容电商） | 购物标签（发展中） | 无直接电商 | 购物标签 | 原生电商闭环（TikTok Shop 内完成交易） | 原生电商闭环（Shopee 内完成交易） | 外链引流（跳转独立站/电商） |

**TikTok 与 TikTok Shop 的关键区别：**

TikTok 内容分发与 TikTok Shop 商业分发的目标信号不同，但具体权重不可假定为固定公开公式。内容分析重点观察观看与互动信号；电商分析同时观察 GPM、商品点击、转化、退货和履约。同一个视频可能高互动低转化，反之亦然。

平台矩阵只是待验证的分析起点。优先使用目标国家、品类、账号阶段和最近 30-90 天后台数据；没有后台数据时标记为 `B` 或 `I`，记录证据日期，不使用“黄金时长”或固定算法权重作为事实。

分析时必须区分用户的目标平台是 TikTok（品牌曝光/涨粉）还是 TikTok Shop（带货转化），两者的内容策略有本质差异：

- TikTok 内容策略：娱乐性>信息量>产品露出。产品是内容的配角。
- TikTok Shop 内容策略：痛点精准>证据充分>CTA清晰>娱乐性。产品是内容的主角。

不要把 TikTok 的爆款视频直接当作 TikTok Shop 的标杆来分析。

**分析该视频对其主平台的适配度**：
- 它的时长是否符合该平台的最佳区间？
- 它的 hook 机制是否匹配该平台的用户滑动习惯？
- 它的互动设计（评论引导、投票、CTA）是否利用了该平台的算法加权？
- 如果搬到另一个平台，需要改什么？

### 七、受众分层与匹配度

不要只说"面向年轻人"。拆解三层受众：

**1. 核心受众（Core）**
-  demographics：年龄、性别、地域、消费能力
-  psychographics：价值观、痛点、渴望、恐惧
-  内容消费习惯：在什么场景下看？通勤？睡前？摸鱼？

**2. 扩散受众（Reach）**
-  非核心人群为什么会被算法推荐到？
-  视频中有哪些"破圈元素"？（普世情感、猎奇、争议）

**3. 决策类型匹配**
-  **冲动型决策**（低价快消、情绪价值）：视频是否制造了"现在就要"的紧迫感？
-  **理性型决策**（高客单价、知识付费）：视频是否建立了足够的信任和证据链？
-  **该视频实际服务的是哪种决策类型？是否错配？**

### 八、竞争格局与品类定位

**1. 品类坐标**
- 该视频属于什么内容赛道？（如：美妆教程/好物测评/剧情/知识科普/情感共鸣/带货切片）
- 该赛道目前是红海还是蓝海？同质化程度如何？

**2. 定位判断**
- **定义者**：开创了一个新的内容格式或叙事范式
- **跟风者**：在已有模板上做了微创新
- **搬运者**：纯模仿，无明显差异化
- **该视频属于哪一类？**

**3. 差异化分析**
- 与赛道 Top 10 的共性是什么？（必须满足的基准线）
- 与赛道 Top 10 的差异是什么？（它的护城河或独特卖点）
- 这种差异化是可持续的，还是一次性的？

### 九、变现漏斗与转化路径

每个视频都是商业系统的一环。拆解：

**1. 商业目标识别**
- 直接带货（挂车、小黄车、橱窗）
- 引流私域（主页链接、评论区引导、私信话术）
- 品牌曝光（软植入、口播、场景露出）
- 人设建设（为后续变现铺信任）
- 纯流量玩法（为其他视频或直播间导流）

**2. 转化漏斗审计**
- **曝光→播放**：封面/标题/前3秒的吸引力
- **播放→完播**：节奏和情绪的把控
- **完播→互动**：评论、点赞、转发的触发点设计
- **互动→转化**：CTA 的清晰度、紧迫感和信任基础
- **转化→复购/留存**：是否有引导关注、加入粉丝群、进入私域的路径？

**3. 承接页匹配度**
- 用户点击主页后，看到的内容是否和视频承诺一致？
- 评论区是否被运营（置顶评论、小号互动、答疑）？
- 私域入口（微信、社群、独立站）是否顺畅？

**4. 电商衔接审计（跨境电商模式专用）**

当视频用于电商带货时，内容漏斗和电商漏斗之间有一个关键的衔接层。很多视频在内容漏斗上表现优秀（高完播、高互动），但在电商漏斗上断裂——用户看完视频觉得"好看"但没有"想买"。

衔接层检查：
- 产品在视频中出现的时间占比是否足够？（低于 20% 通常不够建立购买意向，除非是软植入人设型）
- 产品的核心卖点是否被清晰传达？（不是"提到了产品"，而是"传达了一个明确的购买理由"）
- 价格锚定是否到位？（用户看完视频后是否知道大概价格区间？是否建立了"值这个价"的认知？）
- CTA 到商品的跳转路径是否顺畅？（挂车位置、评论区链接、主页入口——用户从"想买"到"能买"之间有几步？）
- 视频承诺与产品实际体验是否一致？（不一致 → 高退货率 → 放量等于放大亏损）

若衔接层断裂，在结论中明确指出"内容漏斗有效但电商衔接断裂"，并给出修复建议。

### 十、内容质量加权评分

摒弃平均打分。引入 **品类权重** 和 **目标导向权重**。

**第一步：判定内容类型**
从以下类型中选择最接近的一个：
- 带货转化型（电商、直播切片、好物推荐）
- 知识干货型（教程、科普、行业洞察）
- 情绪共鸣型（剧情、Vlog、情感、励志）
- 娱乐搞笑型（段子、鬼畜、挑战、Reaction）
- 人设建设型（日常、价值观输出、生活方式）
- 电商短视频型（TikTok Shop 带货、Shopee Video 商品展示、产品种草）——当视频的核心目标是直接驱动电商成交而非内容涨粉时选择此项

**第二步：应用权重矩阵**

| 评分维度 | 带货转化型 | 知识干货型 | 情绪共鸣型 | 娱乐搞笑型 | 人设建设型 | 电商短视频型 |
|---|---|---|---|---|---|---|
| Hook 强度 | 20% | 15% | 20% | 25% | 15% | 15% |
| 节奏把控 | 15% | 15% | 20% | 20% | 15% | 10% |
| 信息/情绪密度 | 10% | 25% | 20% | 15% | 10% | 10% |
| 说服力/可信度 | 25% | 20% | 15% | 5% | 15% | 25% |
| 原创性 | 10% | 15% | 15% | 20% | 20% | 5% |
| 复刻价值 | 15% | 5% | 5% | 10% | 15% | 10% |
| 转化/留存强度 | 5% | 5% | 5% | 5% | 10% | 20% |
| 产品-视频匹配 | — | — | — | — | — | 5% |

电商短视频型的特点：说服力权重最高（25%），转化/留存次之（20%），原创性权重最低（5%）——电商带货不需要为原创而原创，需要可验证的商业有效性。产品-视频匹配作为额外维度（5%）只在跨境电商模式下启用。

**第三步：逐项评分（1-10）并计算加权总分**

每一项评分需附带 **一句话依据**，拒绝无解释的分数。

**第四步：给出雷达图描述**
用文字描述该视频在所选评分维度上的形状（如"Hook 极强但说服力弱"的漏斗型，或"全面平庸"的圆形）。跨境电商模式使用包含产品-视频匹配的八维口径。

### 十一、可复刻模板与执行成本

**1. 节拍公式**
用填空题的方式输出可复刻结构：

```
[时长]秒 [类型]视频
Beat 1 (0-3s): [动作] + [冲突/悬念] → 目的：Hook
Beat 2 (3-Xs): [情境建立] → 目的：代入
Beat 3 (Xs-Ys): [证明/转折] → 目的：信任/惊喜
Beat 4 (Ys-Zs): [价值释放] → 目的：Payoff
Beat 5 (Zs-结尾): [CTA] → 目的：转化
```

**2. 执行成本评估**

| 成本项 | 等级 | 说明 |
|---|---|---|
| 设备要求 | 手机/微单/专业设备 | ... |
| 场景要求 | 室内/室外/特定场地 | ... |
| 演员/出镜 | 本人/他人/专业演员 | ... |
| 后期复杂度 | 剪映级/PR级/AE级 | ... |
| 制作周期 | 1小时/半天/1天/更长 | ... |
| 预估最低预算 | 0元/100元/1000元/更高 | ... |

**3. 复刻风险提示**
- 哪些元素是 "通用可抄" 的？（结构、节奏、剪辑手法）
- 哪些元素是 "不可复制" 的？（创作者个人魅力、特定时机、平台流量扶持）
- 如果今天复刻，预期效果会打几折？为什么？

### 十二、A/B假设与优化建议

超越"这里应该改"的结论式建议，进入 **假设-验证** 思维。

对每一个优化建议，使用以下格式：

```
【假设】如果将 [当前元素] 改为 [替代方案]
【预期影响】预计 [指标] 会 [上升/下降] [幅度]
【Trade-off】代价是 [失去什么]
【验证方式】可以通过 [小规模测试/评论区调研/对标账号对比] 验证
```

至少提供 3 个 A/B 假设，覆盖：
1. **开头优化**：Hook 的替代方案（视觉/听觉/文案）
2. **中段优化**：节奏、信息密度或情绪曲线的调整
3. **结尾优化**：CTA、转化路径或互动设计

如果适用，提供 **一版重写的脚本或分镜**，标注每一处改动的原因。

---

## Special Modes: 特殊场景变体

当用户提出以下特定需求时，在十二维度框架基础上做侧重调整：

**跨境电商模式**

当用户的目标是跨境卖家的视频商业决策（"这个视频值不值得抄""这个打法能不能用到我的产品""帮我设计出海视频策略"）时，启用跨境电商模式。该模式在十二维度框架基础上增加四个商业维度（第十三至第十六维度），并将本地化分析作为核心模块。

启用条件（满足任一即启用）：
- 用户提到跨境电商、出海、TikTok Shop、Shopee、Amazon、带货、挂车、小黄车
- 用户的目标是判断视频的商业可行性而非纯内容学习
- 用户提供了产品信息或要求分析产品与视频的匹配度
- 用户要求比较不同国家/市场的视频策略

跨境电商模式下的完整输出结构：
1. 十二维度内容拆解（完整覆盖；短视频或证据不足时可合并相邻标题）
2. 第十三维度：产品-视频匹配度与商业可行性
3. 第十四维度：电商转化漏斗与单位经济
4. 第十五维度：跨境本地化与合规
5. 第十六维度：规模化生产与达人矩阵适配
6. 商业决策结论：Go / Iterate / Stop + 执行方案

若用户只要求内容学习（"拆解这个爆款视频的手法"），不启用跨境电商模式，使用标准十二维度。

**账号诊断模式**
- 结合该账号最近 10-20 条视频的数据趋势
- 判断该视频在账号内容矩阵中的角色（引流款/信任款/转化款/日常款）
- 账号所处成长阶段（起号期/涨粉期/变现期/守成期）与视频策略是否匹配

**竞品对标模式**
- 用户同时提供 2-3 个同类视频时，增加对比矩阵
- 对比维度：节奏、信息量、情绪、制作成本、互动数据、变现效率

**纯音频/播客型视频**
- 弱化视觉语法部分，强化听觉叙事分析（声音设计、语速变化、停顿艺术、音乐情绪）

---

## 跨境电商模式：额外维度

以下四个维度在跨境电商模式下追加在标准十二维度之后。非跨境电商模式下不输出。

### 十三、产品-视频匹配度与商业可行性

内容质量高不等于商业价值高。本维度判断视频打法与目标产品之间的匹配度，以及该打法背后的商业模型是否成立。

**1. 产品-视频匹配评估**

| 匹配维度 | 判断问题 | 评分标准（1-10） |
|---|---|---|
| 品类适配 | 视频的内容格式是否适合展示该产品？（演示型产品适合前后对比，体验型产品适合真人使用，标品适合参数对比） | 1-3: 格式与品类严重错配；5-7: 基本适配但无亮点；8-10: 格式天然适合该品类 |
| 价格带适配 | 视频建立的信任深度是否匹配产品价格？（$10 产品靠视觉冲击即可，$100+ 产品需要完整证据链） | 1-3: 信任深度严重不足；5-7: 基本匹配；8-10: 信任建设充分且有余 |
| 人群适配 | 视频吸引的受众是否与产品目标人群重合？ | 1-3: 受众严重错位；5-7: 部分重合；8-10: 高度重合 |
| 卖点覆盖 | 视频是否覆盖了产品的核心卖点？是否遗漏了关键购买理由？ | 1-3: 核心卖点未覆盖；5-7: 覆盖了主要卖点；8-10: 覆盖完整且有差异化表达 |
| 竞争差异 | 该视频打法能否在同类产品中形成差异化？还是竞品也在用同样的手法？ | 1-3: 完全同质化；5-7: 有一定差异；8-10: 打法本身构成竞争壁垒 |

**2. 商业可行性快筛**

在分析视频之前或同时，对视频推广的产品做快速商业可行性判断：

| 快筛项 | 判断 | 不通过的后果 |
|---|---|---|
| 产品利润 | 售价扣除产品成本、物流、平台佣金、广告费后是否有正净利？ | 利润倒挂 → 视频再好也不值得做 |
| 合规/IP | 产品在该目标市场是否有合规障碍（认证、标签、宣称限制、专利风险）？ | 合规红线 → 不能做 |
| 供应链 | 如果视频起量，供应链能否在 2-4 周内响应放量需求？ | 供应跟不上 → 起量即断货 |
| 退货风险 | 产品退货率是否在可控范围？差评是否集中在产品本质缺陷？ | 退货率过高 → 放量等于放大亏损 |

快筛不通过的项目在结论中单列为"商业否决项"，不因内容质量高而忽略。若用户未提供产品信息，将快筛结果标记为"未核验"并列出需要用户补充的信息。

### 十四、电商转化漏斗与单位经济

标准框架的变现漏斗（第九维度）只覆盖到"互动→转化"的内容层。跨境电商需要延伸到"点击商品→加购→下单→签收→不退货"的电商层，并计算单位经济。

**1. 电商转化漏斗**

| 漏斗阶段 | 关键指标 | 该视频的影响因素 | 判断 |
|---|---|---|---|
| 曝光→播放 | 3 秒播放率 | Hook 强度、封面、标题 | 从节奏图谱直接得出 |
| 播放→完播 | 完播率 | 节奏、情绪曲线、信息密度 | 从节奏图谱直接得出 |
| 完播→商品点击 | 商品点击率 | CTA 清晰度、产品露出方式、价格锚定 | 评估视频中产品出现的时机、时长和引导强度 |
| 商品点击→加购 | 加购率 | Listing 质量、价格竞争力、评论基础 | 视频外因素，标注为"需配合 Listing 评估" |
| 加购→下单 | 下单转化率 | 价格、优惠券、运费、紧迫感 | 视频外因素，标注为"需配合促销策略评估" |
| 下单→签收 | 签收率 | 物流时效、包装质量 | 视频外因素 |
| 签收→不退货 | 退货率 | 产品是否符合视频承诺、预期管理 | 评估视频是否过度承诺或误导 |

重点分析前三个阶段（视频直接影响的阶段），后四个阶段标注为"视频外因素"并给出配合建议。

**2. 单位经济快算**

当用户提供了产品成本和售价信息时，计算：

| 指标 | 公式 | 判断标准 |
|---|---|---|
| 单件贡献利润 | 售价 - 产品 - 包装 - 物流 - 佣金 - 支付费 - 退货准备金 | 必须为正 |
| 可承受最高 CPA | 单件贡献利润 - 售价 × 目标净利润率 | 视频推广的单次获客成本不得高于此值 |
| 可承受最高广告费率 | 单件贡献利润 ÷ 售价 | 即盈亏平衡 ACOS |
| 最低日均订单量 | 视频制作+推广固定成本 ÷ (单件贡献利润 × 30 天) | 放量可持续的最低订单量 |

若用户未提供成本数据，使用行业区间假设（标注为假设），并列出推翻变量。

**3. 视频投资回报情景**

只有漏斗输入和成本输入足够时才计算 ROI；否则输出反推门槛，不用内容评分直接推导利润率。优先复用 CIDM 的 `profit_model.py` 与 `reverse_funnel.py` 口径，分别报告 ROI 和净利润率：

| 场景 | 必填假设 | 输出 |
|---|---|---|
| 压力 | 曝光、CTR、CVR、签收、退货、单位贡献、素材/达人/投流成本 | 订单、收入、净利、ROI、净利润率 |
| 基准 | 同上，采用已验证基线或明确的 `U/B` 假设 | 订单、收入、净利、ROI、净利润率 |
| 乐观 | 同上，并明确自然流量或转化改善来自哪项假设 | 订单、收入、净利、ROI、净利润率 |

`ROI =（归因收入或归因贡献利润 - 内容与推广投入）÷ 内容与推广投入`，必须声明采用哪一种分子口径。净利润率单独按 `净利 ÷ 收入` 计算。不把视频 ROI、产品 ROI 和净利润率混为同一指标。

### 十五、跨境本地化与合规

跨境电商视频不是翻译+换演员。不同市场的购买动机、信任建立方式、合规边界和审美偏好存在系统性差异。

**1. 目标市场适配矩阵**

对用户指定的目标市场（或默认分析美国、东南亚、日本三个核心市场），按以下维度评估：

| 适配维度 | 美国 | 东南亚（印尼/泰国/越南） | 日本 | 中东（沙特/阿联酋） | 拉美（巴西/墨西哥） |
|---|---|---|---|---|---|
| 购买动机 | 功能+性价比+评价 | 价格+社交证明+达人信任 | 品质+细节+品牌故事 | 品牌+身份表达+社交认同 | 价格+功能演示+分期付款 |
| 信任建立 | 真实评测+数据+对比 | 达人背书+评论区氛围 | 精致制作+专业感+细节 | 品牌授权+本地认证+阿语内容 | 真人出镜+使用效果+社交证明 |
| Hook 偏好 | 强冲突/问题前置/反预期 | 价格锚定/效果对比/猎奇 | 美学冲击/仪式感/安静感 | 奢华感/身份标签/家庭场景 | 高能量/色彩丰富/音乐驱动 |
| 时长偏好 | 15-60s（TikTok）/ 30-60s（Shorts） | 15-30s（节奏更快） | 30-90s（允许更慢节奏） | 15-30s | 15-30s |
| 音乐/音效 | 热门 BGM 或原声 | 本地热门音乐/节奏感强 | 轻音乐/ASMR/安静 | 阿语音乐/避免敏感内容 | 拉丁节奏/热门 BGM |
| 禁忌/敏感点 | 虚假宣称/FDA/FTC/儿童保护 | 宗教敏感/王室相关/价格欺诈 | 过度承诺/粗糙制作/虚假成分 | 女性形象/酒精/猪肉相关/宗教 | 政治敏感/种族/过度 P 图 |
| 平台偏好 | TikTok + Amazon + TikTok Shop | TikTok + Shopee + Lazada | YouTube + TikTok + Amazon JP | TikTok + Noon | Instagram + TikTok + Mercado Libre |

对于每个目标市场，回答：
1. 该视频的核心打法在该市场是否成立？
2. 需要调整哪些元素？（语言、演员、场景、音乐、卖点顺序、价格锚定）
3. 调整的预估成本和周期。
4. 是否存在不可调整的硬障碍？（文化禁忌、合规红线）

**2. 合规快筛**

针对视频推广的产品和视频内容本身，做两层合规快筛：

第一层——产品合规：
- 目标市场是否有该品类的准入要求（认证、注册、标签）？
- 视频中展示的产品是否符合目标市场的标签/宣称要求？
- 是否存在专利或商标风险？

第二层——内容合规：
- 视频中的宣称是否违反目标市场的广告法规（如美国 FTC 披露要求、欧盟 UCPD、日本景品表示法）？
- 视频中是否有文化敏感内容（宗教、种族、性别、政治）？
- 达人合作是否需要标注广告关系（如 FTC #ad 要求）？

合规快筛不通过的项目标记为"合规否决"，不因内容质量高或市场潜力大而忽略。标注需要哪种专业人士复核（律师、检测机构、本地化团队）。

**3. 本地化成本评估**

| 本地化层级 | 内容 | 预估成本 | 适用场景 |
|---|---|---|---|
| L1 语言适配 | 翻译字幕/配音 + 保留原画面 | 低（翻译/配音费） | 产品通用、无文化特定元素 |
| L2 文化适配 | L1 + 调整卖点顺序、价格锚定、音乐、文字 | 中（本地化团队+重新剪辑） | 产品通用但购买动机因市场而异 |
| L3 全面重制 | 重新拍摄 + 本地演员 + 本地场景 + 本地脚本 | 高（拍摄制作费） | 产品需要本地信任背书或文化适配度高 |

给出建议的本地化层级和理由。不要把 L3 作为默认选项——很多产品在 L1 或 L2 就足够。

### 十六、规模化生产与达人矩阵适配

跨境卖家通常不是做一条视频，而是做一个视频体系：一个产品 50-100 条视频，分发给 20-30 个达人，覆盖多个市场和平台。本维度判断该视频打法是否可规模化，以及如何设计达人矩阵。

**1. 可规模化评估**

| 评估维度 | 判断问题 | 可规模化信号 | 不可规模化信号 |
|---|---|---|---|
| 脚本模板化 | 该视频的脚本结构能否抽象成可复用的模板？ | Beat 结构清晰、可替换产品/场景/演员 | 高度依赖特定创作者的即兴发挥或个人魅力 |
| 制作标准化 | 拍摄和后期能否标准化到不同团队执行？ | 镜头语言简单、不依赖特殊设备或技术 | 需要专业设备、特殊技能或特定创作者的风格 |
| 素材可替换性 | 画面素材能否在不同市场/达人之间替换？ | 产品镜头通用、场景可替换、演员可替换 | 画面与特定创作者强绑定 |
| 内容疲劳抗性 | 同一打法能否支撑 50+ 条视频而不让观众审美疲劳？ | 多变体空间大（不同场景/演员/角度） | 打法单一，超过 10 条就会重复 |

**2. 达人矩阵设计**

基于该视频的打法，设计达人分发矩阵：

| 达人层级 | 粉丝量级 | 合作方式 | 内容要求 | 预估数量 | 预算分配 |
|---|---|---|---|---|---|
| 头部达人 | >100 万 | 品牌合作/定制内容 | 高质量定制，建立品牌背书 | 1-3 个 | 30-40% |
| 腰部达人 | 10-100 万 | 寄样+佣金/小额合作费 | 按模板执行+个人风格微调 | 5-10 个 | 30-40% |
| 尾部达人/KOC | <10 万 | 纯寄样+佣金 | 按模板执行，量大覆盖 | 20-50 个 | 20-30% |

每个层级给出：
1. 该层级达人的筛选标准（品类匹配度、粉丝画像、历史带货数据）
2. 脚本模板（基于该视频的 Beat 结构，标注哪些节拍可替换、哪些必须保留）
3. 预估单达人成本和预期产出
4. 传播分布预期：是否可能避免"单达人集中"风险（使用传播熵简化口径：单达人贡献 >60% 订单 = 单点集中，放量风险高）

**3. 素材生命周期管理**

| 阶段 | 时间 | 信号 | 动作 |
|---|---|---|---|
| 测试期 | 第 1-2 周 | 小批量发布 5-10 条变体 | 观察 3 秒播放率和商品点击率，筛选有效变体 |
| 放量期 | 第 3-6 周 | 有效变体数据稳定 | 扩大达人分发，追加投流预算 |
| 疲劳期 | 第 7-12 周 | 播放率或点击率开始下滑 | 更新素材变体（换场景/演员/Hook），保持 Beat 结构不变 |
| 衰退期 | 第 13 周+ | 数据持续下滑，更新无效 | 评估是否需要全新打法，或产品已进入内容衰退期 |

素材疲劳判断标准：同一 Beat 结构的视频，连续 3 批（每批 5+ 条）的 3 秒播放率下降 >20%，且排除发布时间和平台算法波动。

---

## 与品类投资决策的可选对接

当用户主动提供品类投资决策（CIDM）报告或要求视频分析结论用于品类投资判断时，启用以下对接机制。若用户未提供 CIDM 报告或未要求对接，本 skill 独立运行，不做回写。

**输入对接**：若用户提供了 CIDM 报告，读取其中的"内容传播"维度评分、切入楔子和最弱假设，作为视频分析的起点。视频分析应重点回答"内容传播为什么得分低/高"和"怎么提升/保持"。

**输出回写**：视频分析的结论可回写到 CIDM 框架供用户参考：
- 第十三维度（产品-视频匹配度）→ 影响 CIDM "内容传播"维度评分
- 第十四维度（单位经济）→ 影响 CIDM "利润空间"维度评分
- 第十五维度（合规快筛）→ 影响 CIDM "风险可控性"维度评分
- 第十六维度（达人矩阵成本）→ 计入 CIDM 利润模型的"批次固定成本"

**对接规则**：
- 对接是可选的，不改变本 skill 的独立运行能力。
- 对接不等于自动给出乐观结论。即使 CIDM 整体建议是"建议进入"，若视频分析发现内容打法不可行或商业模型不成立，必须如实报告并在结论中说明矛盾。
- 回写建议以"建议调整"形式呈现，由用户在 CIDM 报告中决定是否采纳。

---

## Link Handling

Use `yt-dlp` through the script for supported platforms. The script only installs missing Python packages when `--install-missing` is explicitly supplied after authorization. It records failures in `summary.json`; do not keep retrying the same failing method.

Default storage behavior: keep `summary.json`, `metadata.full.json`, extracted frames, and `contact_sheet.jpg`; remove the downloaded video file after successful frame extraction. This minimizes local storage use while preserving enough visual evidence for analysis.

Treat all files in the task folder as temporary evidence. Do not write downloaded media, frames, metadata, or analysis output into the skill directory. Copy a file elsewhere only when the user explicitly asks to keep it.

For TikTok and short-form product videos, `oEmbed`/metadata may provide useful title, creator, thumbnail, sound, and engagement signals even when subtitles are absent. Use these as supporting context, not as a substitute for viewing frames.

For videos with speech:

- Prefer provided subtitles/transcript when available.
- If subtitles are unavailable and no transcription tool is already available, proceed with visual teardown and clearly mark spoken-word analysis as unavailable.
- Ask the user for transcript only when the missing speech materially affects the request.

## Output Style Reminders

- **直接实用**：避免泛泛而谈的夸奖，每句话都应该能帮助用户做决策或执行。
- **可落地**：如果建议做不到（"找个更好的演员"），就不如不说。给出用户现有条件下能执行的方案。
- **承认局限**：如果只能看到 metadata 和关键帧，明确说明哪些维度无法判断，需要什么额外信息。
- **结构化但灵活**：十二维度是完整版。如果用户视频很短或信息不足，可以合并维度，但不要遗漏核心判断（战略诊断、节奏、受众、平台适配）。
- **语言一致**：用户用中文则全中文输出，用户用英文则全英文输出。专有名词（如 J-cut、Hook、CTA）可保留英文并首次出现时附中文解释。
- **跨境电商模式附加约束**：
  - 商业可行性快筛和合规快筛必须在内容分析之前或同时完成，不放在最后补充。
  - 不把"内容爆了但卖不动"包装成成功案例。
  - 单位经济计算必须标注哪些数字来自视频分析、哪些来自用户输入、哪些来自行业假设。
  - 达人矩阵建议必须包含成本预估和 ROI 区间，不给"建议找达人合作"这种空话。
  - 本地化建议必须具体到"改什么、怎么改、预估成本"，不给"建议本地化"这种结论。

## Quality Gate: 交付前自检

在输出最终分析前，快速检查：

- [ ] 我是否区分了 observed 和 inferred？
- [ ] 是否记录 `VLB-2026.07`、证据截止时间、目标国家/平台及分析路线？
- [ ] 决策相关结论是否回指 `O/M/U/B/I` 证据编号？
- [ ] 秒级节奏图谱是否至少拆到了前 15 秒？
- [ ] 情绪曲线是否有明确的峰值和低谷标注？
- [ ] 平台分析是否具体到算法指标，而非泛泛而谈？
- [ ] 受众分层是否超越了 demographics，进入了消费场景和决策类型？
- [ ] 评分是否有权重依据和一句话解释？
- [ ] 复刻模板是否包含了执行成本和风险提示？
- [ ] 优化建议是否使用了假设-验证格式，而非简单结论？
- [ ] 全文是否有至少一个 "如果改 X，预计会如何" 的具体预测？

跨境电商模式附加自检（仅跨境电商模式启用时检查）：

- [ ] 商业可行性快筛是否完成？利润、合规、供应链、退货四项是否都已判断？
- [ ] 电商转化漏斗是否覆盖了"完播→商品点击→加购→下单"的衔接层？
- [ ] 单位经济快算是否完成？可承受最高 CPA 和盈亏平衡 ACOS 是否已给出？
- [ ] ROI 与净利润率是否分别计算，且漏斗、成本和归因口径完整？
- [ ] 目标市场的本地化适配是否具体到元素级别（不是"建议本地化"）？
- [ ] 合规快筛是否覆盖了产品合规和内容合规两层？
- [ ] 达人矩阵是否包含了层级分配、脚本模板、成本预估和传播分布预期？
- [ ] 素材生命周期是否给出了疲劳判断标准和更新策略？
- [ ] 与 CIDM 的对接是否完成（若用户提供了 CIDM 报告）？

Keep the teardown grounded in the actual video. If only metadata is available, give a limited analysis and state exactly what artifact would unlock a full teardown.
