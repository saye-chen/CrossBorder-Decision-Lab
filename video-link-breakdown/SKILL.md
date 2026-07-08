---
name: video-link-breakdown
description: 用中文深度拆解用户提供的视频链接，输出秒级节奏图谱、情绪曲线、脚本结构、剪辑语法、平台算法适配、内容质量加权评分、受众分层、竞争定位、变现漏斗、复刻成本、跨文化适配、A/B假设与优化建议。适用于 TikTok、YouTube Shorts、Instagram Reels、X/Twitter 视频、Bilibili、抖音等链接；当用户要求“拆解这个视频”“分析脚本/剪辑/节奏/钩子/内容质量”“复刻这个视频”“改写短视频脚本”“为什么这个视频能火”“这个视频值不值得抄”“出海/本地化分析”或提供视频链接希望做内容策略分析时使用。
---

# Video Link Breakdown — 专业级短视频内容拆解

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

## Core Principle: Observed vs. Inferred

Always separate what was **observed** (from frames, audio, on-screen text, metadata) from what is **inferred** (psychology, algorithmic behavior, business model, audience intent). If inference is critical to the conclusion, label it explicitly.

If there is no transcript or audio transcription, state that script analysis is based on visual structure, title, on-screen text, and editing flow. Do not fabricate dialogue.

## Output Framework: 十二维度拆解

Respond in the user's language. Be direct and practical. Favor reusable patterns over vague praise. Use the following structure unless the user asks for a different format.

---

### 一、基础信息与元数据

- **平台**：TikTok / 抖音 / YouTube Shorts / Instagram Reels / Bilibili / 其他
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

| 维度 | 抖音/TikTok | YouTube Shorts | Bilibili | Instagram Reels |
|---|---|---|---|---|
| **核心指标** | 完播率>互动率>转发 | 观看时长>回关率>互动 | 弹幕密度>收藏>三连 | 停留时长>分享>保存 |
| **最佳时长** | 15-60s，黄金7s | 30-60s，允许更长 | 1-5min，可深度 | 15-30s，快节奏 |
| **Hook偏好** | 视觉冲击/强冲突 | 问题前置/悬念 | 梗/文化共鸣 | 美学冲击/生活方式 |
| **互动设计** | 评论区造梗 | 订阅引导 | 弹幕互动 | 标签挑战 |
| **音乐策略** | 热门BGM跟拍 | 原创/无版权优先 | 原声/鬼畜改编 | 趋势音乐 |

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

### 十、内容质量加权评分

摒弃平均打分。引入 **品类权重** 和 **目标导向权重**。

**第一步：判定内容类型**
从以下类型中选择最接近的一个：
- 带货转化型（电商、直播切片、好物推荐）
- 知识干货型（教程、科普、行业洞察）
- 情绪共鸣型（剧情、Vlog、情感、励志）
- 娱乐搞笑型（段子、鬼畜、挑战、Reaction）
- 人设建设型（日常、价值观输出、生活方式）

**第二步：应用权重矩阵**

| 评分维度 | 带货转化型 | 知识干货型 | 情绪共鸣型 | 娱乐搞笑型 | 人设建设型 |
|---|---|---|---|---|---|
| Hook 强度 | 20% | 15% | 20% | 25% | 15% |
| 节奏把控 | 15% | 15% | 20% | 20% | 15% |
| 信息/情绪密度 | 10% | 25% | 20% | 15% | 10% |
| 说服力/可信度 | 25% | 20% | 15% | 5% | 15% |
| 原创性 | 10% | 15% | 15% | 20% | 20% |
| 复刻价值 | 15% | 5% | 5% | 10% | 15% |
| 转化/留存强度 | 5% | 5% | 5% | 5% | 10% |

**第三步：逐项评分（1-10）并计算加权总分**

每一项评分需附带 **一句话依据**，拒绝无解释的分数。

**第四步：给出雷达图描述**
用文字描述该视频在七个维度上的形状（如"Hook极强但说服力弱"的漏斗型，或"全面平庸"的圆形）。

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

**出海/本地化分析**
- 增加文化适配度评估：梗、幽默、音乐、色彩、身体语言、社会议题的跨文化风险
- 目标市场的平台偏好（如东南亚重 TikTok，拉美重 Instagram，日本重 YouTube/TikTok）
- 本地化成本：翻译、重新配音、换演员、调整场景

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

## Link Handling

Use `yt-dlp` through the script for supported platforms. The script can install missing Python packages into the user site when allowed by the environment. It records failures in `summary.json`; do not keep retrying the same failing method.

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

## Quality Gate: 交付前自检

在输出最终分析前，快速检查：

- [ ] 我是否区分了 observed 和 inferred？
- [ ] 秒级节奏图谱是否至少拆到了前 15 秒？
- [ ] 情绪曲线是否有明确的峰值和低谷标注？
- [ ] 平台分析是否具体到算法指标，而非泛泛而谈？
- [ ] 受众分层是否超越了 demographics，进入了消费场景和决策类型？
- [ ] 评分是否有权重依据和一句话解释？
- [ ] 复刻模板是否包含了执行成本和风险提示？
- [ ] 优化建议是否使用了假设-验证格式，而非简单结论？
- [ ] 全文是否有至少一个 "如果改 X，预计会如何" 的具体预测？

Keep the teardown grounded in the actual video. If only metadata is available, give a limited analysis and state exactly what artifact would unlock a full teardown.
