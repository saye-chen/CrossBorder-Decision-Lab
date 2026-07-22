# CIDM → VLB 选品移交包消费协议

定义 VLB 如何消费 CIDM 输出的 Selection Handoff Package（选品移交包），进入"战略锚定拆解模式"。

## 目录

- [触发条件](#触发条件)
- [Handoff Package Schema](#handoff-package-schema)
- [消费规则](#消费规则)
- [Golden 样例](#golden-样例)
- [与飞轮的关系](#与飞轮的关系)

## 触发条件

- **非必须**：VLB 可以在没有 Handoff Package 的情况下独立运行（纯拆解模式）
- **有 Handoff Package 时**：VLB 进入"战略锚定拆解模式"，输出带战略对齐判断
- **低置信/早期阶段**：Handoff Package 的 `confidence_level = low` 或 `lifecycle_stage = LC-1/LC-2` 时，VLB 输出附加"选品决策本身待验证"提示，Brief Seed 标记为探索性（`usage: "hypothesis_only"`）

## Handoff Package Schema

```yaml
selection_handoff_package:
  meta:
    cidm_version: string           # CIDM 评估版本（如 CIDM-2026.14）
    assessment_date: string
    confidence_level: enum [high, medium, low]
    lifecycle_stage: enum [LC-1, LC-2, LC-3, LC-4, LC-5, LC-6]

  product_identity:
    name: string
    listing_url: string
    category_path: string          # 如 Home & Kitchen > Storage > Closet Organizers
    price_band: string             # 如 $15-25
    key_variants: [string]

  selling_points_ranked:           # 按差异化程度排序
    - point: string
      differentiation: enum [unique, rare, common]
      evidence: string
    # 至少 2 个，最多 5 个

  target_segment:
    primary_persona: string
    demographics:
      age_range: string
      gender_skew: string
      income_level: string
    psychographics: string
    content_consumption: string    # 内容消费偏好

  competitive_creative_gap:
    what_competitors_do: [string]
    what_users_want: [string]
    gap_opportunity: string
    source_evidence: string

  entry_constraint:
    budget_level: enum [micro, small, medium, large]
    production_capability: enum [self_shot, outsource, ai_generate, mixed]
    platform_compliance_notes: [string]
    timeline: string

  strategic_intent:
    content_role: enum [awareness, conversion, retargeting, brand_building, unspecified]
    funnel_position: string
    success_metric: string
```

## 消费规则

VLB 接收到 Handoff Package 后，按以下规则锚定拆解方向：

### 规则 1：拆解方向锚定

`selling_points_ranked` 中 `differentiation = unique/rare` 的卖点，成为拆解时的核心锚点。拆解时重点关注：
- 该视频是否有效传达了差异化卖点？
- 传达方式是否匹配目标人群的 `content_consumption` 偏好？
- 如果视频未触及差异化卖点，在报告中标注"战略错位"并建议调整方向。

### 规则 2：空白点验证

`competitive_creative_gap.gap_opportunity` 成为拆解时的验证假设：
- "这条视频是否在填补该空白？"
- "填补效果如何？（用户互动/评论反馈是否验证了需求）"
- 如果视频确实在填补空白且效果正向，Brief Seed 中标注 `gap_validated: true`。

### 规则 3：Brief Seed 约束传递

- Brief Seed Layer 1 的 `primary_proof_point` 必须对应 `selling_points_ranked` 中 differentiation 最高的卖点
- 如果拆解发现视频的证明点与选品卖点不一致，Brief Seed 中保留视频实际证明点，但在 meta 中标注 `handoff_aligned: false` 并附说明
- Layer 3 的 `talent_requirement.type` 受 `entry_constraint.production_capability` 约束
- Layer 3 的 `ai_generation_notes` 受 `entry_constraint.budget_level` 约束（micro/small 预算不推荐高端模型）

### 规则 4：执行约束继承

- `entry_constraint.platform_compliance_notes` 直接传递到 Brief Seed Layer 2 的 `compliance_risk` 评估
- `strategic_intent.content_role` 影响 Brief Seed 的转化节点设计：
  - awareness → 弱化 CTA，强化记忆点
  - conversion → 强化 CTA + 紧迫感
  - retargeting → 强化社会证明 + 限时
  - brand_building → 弱化产品，强化价值观/情感
  - unspecified → 不预设 CTA 强度，先确认内容目标；未确认前只输出可逆的多方案假设

### 规则 5：置信度传递

- Handoff Package `confidence_level = high` + `lifecycle_stage >= LC-3` → 正常拆解
- Handoff Package `confidence_level = medium` 或 `lifecycle_stage = LC-2` → 拆解报告附加"选品决策中等置信，创意方案建议小批量验证"
- Handoff Package `confidence_level = low` 或 `lifecycle_stage = LC-1` → Brief Seed 强制 `usage: "hypothesis_only"`，拆解报告附加"选品决策待验证，本拆解仅供探索参考"

## Golden 样例

### 输入：Handoff Package（收纳品类）

```yaml
selection_handoff_package:
  meta:
    cidm_version: "CIDM-2026.14"
    assessment_date: "2026-07-15"
    confidence_level: high
    lifecycle_stage: LC-3

  product_identity:
    name: "免打孔磁吸刀架"
    listing_url: "https://www.amazon.com/dp/B0XXXXX"
    category_path: "Home & Kitchen > Storage & Organization > Kitchen Storage > Knife Racks"
    price_band: "$12-18"
    key_variants: ["黑色", "白色", "木纹"]

  selling_points_ranked:
    - point: "磁吸力 3x 竞品，可吸住陶瓷刀"
      differentiation: unique
      evidence: "专利磁铁排列，用户评价高频提及'终于能吸住陶瓷刀了'"
    - point: "免打孔安装，租房友好"
      differentiation: rare
      evidence: "竞品 80% 需打孔，VOC 中'租房不能打孔'出现频率 top3"
    - point: "304 不锈钢面板，防锈"
      differentiation: common
      evidence: "行业标配，非差异化但需提及"

  target_segment:
    primary_persona: "25-35 岁租房/新居年轻女性，注重厨房颜值和收纳效率"
    demographics:
      age_range: "25-35"
      gender_skew: "女性 70%"
      income_level: "中等"
    psychographics: "追求'小而美'生活质感，愿意为设计感付溢价，反感廉价塑料感"
    content_consumption: "偏好 15-30 秒快节奏改造/收纳视频，喜欢 before/after 对比，反感硬广口播"

  competitive_creative_gap:
    what_competitors_do: ["棚拍产品旋转展示", "功能参数罗列", "打折促销口播"]
    what_users_want: ["真实厨房场景安装过程", "陶瓷刀/重型刀吸附测试", "改造前后对比"]
    gap_opportunity: "用真实厨房场景 + 极限吸附测试填补'性能可视化'空白"
    source_evidence: "Amazon 评论 VOC 分析 + TikTok 同品类 top50 视频内容审计"

  entry_constraint:
    budget_level: small
    production_capability: self_shot
    platform_compliance_notes: ["不得声称'永不掉落'（绝对化用语）", "承重数据需标注测试条件"]
    timeline: "2 周内首条素材上线"

  strategic_intent:
    content_role: conversion
    funnel_position: "中漏斗（已认知品类，需说服选择本品）"
    success_metric: "CTR > 3% 且加购率 > 8%"
```

### 输出：VLB 战略锚定拆解（摘要）

拆解一条同品类爆款视频后，VLB 输出：

**战略对齐判断：**
> 本条视频证明点为"免打孔安装便捷性"，对应 Handoff Package selling_points_ranked #2（rare）。未触及 #1 差异化卖点"磁吸力吸陶瓷刀"。建议：下一条 Brief Seed 将 primary_proof_point 调整为"陶瓷刀吸附测试"，填补竞品内容空白。

**Brief Seed（handoff_aligned: true）：**
- Layer 1 primary_proof_point: "磁吸力可吸住陶瓷刀（竞品做不到）"
- Layer 1 evidence_format: live_test（真实厨房场景，陶瓷刀+菜刀+剪刀连续吸附）
- Layer 2 archetype: "极限测试型"（匹配 gap_opportunity "性能可视化"）
- Layer 2 compliance_risk: low（标注测试条件即可）
- Layer 3 talent_requirement: real_person + self_shot（受 production_capability 约束）
- Layer 3 ai_generation_notes: null（自拍方案，无需 AI 生成）

## 与飞轮的关系

本协议是"双环飞轮"中"选品环 → 内容环"的显式数据桥：
- CIDM 选品决策完成 → 用户确认进入内容阶段 → CIDM 组装 Handoff Package → VLB 消费
- VLB 拆解 + Brief Seed → D10 生产 → 发布 → 数据回流 → D10→CIDM 经济性回传 → CIDM 校准选品模型

与 D10 执行文档中已定义的 "D10→CIDM 组合经济性" 回传 schema 形成双向闭环。
