# 素材来源信号与归因修正

VLB 拆解前的前置信号标注协议。三项信号决定创意有效性判断的归因置信度，防止把投流预算或 AI 新奇感的贡献错误归功于创意结构。

## 信号字段定义

### production_source

| 取值 | 定义 | 检测启发式 |
|---|---|---|
| `human_shot` | 真人实拍（达人自拍、棚拍、街拍） | 自然人体动态、真实环境纹理、无 AI 伪影 |
| `ai_generated` | 主体画面由 AI 模型生成（Sora/Kling/Seedance 等） | 手指/文字/物理规律异常、平台 AI 标注、元数据标记 |
| `hybrid` | AI 生成 + 真人混剪，或 AI 辅助后期（换脸/换背景） | 部分帧真实部分帧异常、局部 AI 伪影 |
| `unknown` | 现有证据无法判定制作来源 | 缺少可验证标签、元数据或足够画面证据 |

无法判断时标记为 `unknown`，不得为了完整而猜测 `hybrid`。平台 AI 标签可作为一项可见证据，但标签规则、适用市场和生效时间必须按任务时点核验；无标签不证明非 AI 生成。

### traffic_source

| 取值 | 定义 | 检测启发式 |
|---|---|---|
| `organic` | 自然推荐流量为主 | 无 Ad 标签、播放量与粉丝量比值合理、传播曲线呈自然扩散 |
| `paid` | 明确投流放大（Spark Ads / In-Feed Ads） | 视频带 "Sponsored"/"Ad" 标签、评论区有"广告"反馈 |
| `mixed` | 自然起量后追加投流 | 早期自然增长曲线 + 后期突然加速、创作者自述 |
| `unknown` | 无法判断 | 以上信号均不可用 |

播放/粉丝比、分享、评论和传播曲线只能作为任务内辅助信号，不设置跨平台固定阈值，也不能单独确认 `paid`。无广告标签、授权后台或可验证投放记录时，保持 `unknown`。

### commerce_binding

| 取值 | 定义 | 检测启发式 |
|---|---|---|
| `shoppable` | 视频挂车（TikTok Shop 商品链接） | 左下角商品卡片/购物袋图标、评论区置顶购买链接 |
| `non_shoppable` | 纯内容/品牌向，无直接购买入口 | 无商品卡片、无购买引导 |

## 归因修正规则

| traffic_source | production_source | 创意有效性置信度 | 修正说明 |
|---|---|---|---|
| organic | human_shot | 中高 | 排除了已知付费投放，但仍需考虑账号基线、分发和外部事件 |
| organic | ai_generated | 中 | 需分离画面新奇性、账号基线与创意结构贡献 |
| organic | hybrid | 中高 | 同上，需判断 AI 部分是核心吸引力还是辅助 |
| paid | any | 待验证 | 播放量含预算贡献，创意判断降级为"假设"而非"结论" |
| mixed | any | 中 | 自然起量阶段有效，投流放大效果未分离 |
| unknown | any | 中 | 流量来源未确认，判断含不确定性 |

## 报告措辞模板

拆解报告结论段必须包含归因前提声明。按置信度选择措辞：

**高置信（organic + human_shot）：**
> 本条视频观察为自然流量真人实拍，已知付费投放影响较低。创意结构与表现相关，但仍不等于已证明因果；需通过同账号对照或实验验证。

**中高置信（organic + ai_generated/hybrid）：**
> 本条视频为自然流量但使用 AI 生成/辅助画面。创意结构可作为候选机制，但当前无法分离画面新奇性、账号基线和创意结构的贡献。建议在可比条件下复测。

**待验证（paid + any）：**
> 本条视频 traffic_source = paid（{具体标记}），创意结构分析有效但播放量不可直接归因于创意本身。以下创意有效性判断为假设，需在 organic 条件下复测验证。

**中置信（mixed / unknown）：**
> 本条视频流量来源为 {mixed/unknown}，创意有效性判断含不确定性。自然起量阶段的创意信号可参考，投流放大效果未分离。

## 与 Brief Seed 的联动

`vlb_confidence` 字段直接继承归因修正结果，`usage` 由 `vlb_confidence` 决定：

| 归因置信度 | 条件 | vlb_confidence | usage |
|---|---|---|---|
| 中高 | organic + human_shot | medium | validate_before_scale |
| 中 | organic + ai_generated/hybrid | medium | validate_before_scale |
| 中 | mixed / unknown + any | medium | validate_before_scale |
| 待验证 | paid + any | low | hypothesis_only |

Handoff Package 约束：当 CIDM 选品移交包 `confidence_level = low` 或 `lifecycle_stage = LC-1/LC-2` 时，usage 强制降级为 `hypothesis_only`（即使 vlb_confidence = medium）。选品决策本身的不确定性叠加到内容生产决策上。

D10 消费 Brief Seed 时，`hypothesis_only` 必须设计 A/B 验证而非直接量产；`validate_before_scale` 可小批量测试但不可全量铺开；`production_ready` 正常量产。

## 与 D10 发布预检的闭环

D10 Publish Pre-flight Checklist 的 `brief_fidelity` 检查项引用 Brief Seed Layer 1 和 Layer 2 作为对照基准。如果某创意结构连续 3 次因合规问题被限流/下架，VLB 在后续拆解中标记该母题为"高合规风险"，Brief Seed Layer 2 附加 `compliance_risk: high` 警告。
