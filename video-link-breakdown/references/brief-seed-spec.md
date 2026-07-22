# Production-Ready Brief Seed 规格

VLB 拆解的结构化生产摘要输出协议。Brief Seed 是完整拆解报告的"可执行摘要"，面向 D10 达人 Brief 编写、AI 视频生成工具（CreatOK/Kling/Sora 等）和内部生产团队直接消费。

## 目录

- [输出规则](#输出规则)
- [完整 Schema](#完整-schema)
- [约束传递规则](#约束传递规则)
- [Golden 样例](#golden-样例)
- [与 D10 的接口](#与-d10-的接口)
- [与 AI 生成工具的接口](#与-ai-生成工具的接口)

## 输出规则

- Decision Memo 及以上交付层级必须同时输出完整报告 + Brief Seed
- Decision Card 可选输出（用户要求时）
- Brief Seed 可独立于完整报告被 D10 消费（D10 不需要读完整报告就能启动 Brief 编写）
- 存在 CIDM Selection Handoff Package 时，Brief Seed 必须与选品卖点对齐

## 完整 Schema

```yaml
production_ready_brief_seed:
  meta:
    source_video_id: string        # 来源视频 ID
    source_video_url: string       # 来源视频 URL
    vlb_confidence: enum [high, medium, low]  # 继承归因修正后的置信度
    usage: enum [production_ready, validate_before_scale, hypothesis_only]
    platform: string               # 目标平台
    category: string               # 品类
    handoff_aligned: boolean       # 是否与 CIDM 选品移交包对齐（无移交包时为 null）

  layer_1_product_proof:           # 第一层：产品证明点（What to prove）
    primary_proof_point: string    # 核心证明点（一句话）
    secondary_proof_points:        # 辅助证明点（0-2个）
      - string
    evidence_format:               # 证据呈现形式
      type: enum [live_test, comparison, data_overlay, scenario_immersion, testimonial, unboxing]
      detail: string               # 具体怎么呈现（如"左右分屏对比使用前后"）
    proof_duration_ratio: number   # 证明段占全片时长比例（0-1）

  layer_2_creative_blueprint:      # 第二层：创意方案（How to tell）
    archetype: string              # 创意母题类型（对应 VLB 母题分类体系）
    compliance_risk: enum [low, medium, high]  # 合规风险标记（默认 low）
    narrative_structure:
      hook:
        type: enum [question, shock, pain_point, curiosity_gap, direct_callout, trend_ride]
        content: string            # hook 具体内容描述
        duration_sec: number       # hook 时长
      development:
        pattern: enum [linear_escalation, problem_solution, before_after, listicle, story_arc]
        beats:                     # 展开节拍（按时间顺序）
          - timestamp: string      # 时间点或时间段
            content: string        # 该节拍内容
            function: string       # 叙事功能（如"建立痛点""展示转化""社会证明"）
      conversion_node:
        type: enum [cta_verbal, cta_text, product_reveal, urgency_trigger, social_proof_cascade]
        timing: string             # 出现时间点
        content: string
    rhythm_template:
      total_duration_sec: number
      cut_frequency: string        # 切镜频率（如"前3秒每0.5秒一切，中段每2秒一切"）
      info_density: enum [high, medium, low]
      energy_curve: string         # 能量曲线描述（如"高开→平稳→尾部再拉升"）

  layer_3_execution_params:        # 第三层：执行参数（How to shoot/generate）
    camera_language:
      shots: [string]              # 镜头类型列表
      movement: string             # 运镜方式（固定/手持/滑轨/无人机）
      angle: string                # 机位角度
    lighting_tone: string          # 光线基调
    talent_requirement:
      type: enum [real_person, ai_avatar, product_only, mixed]
      persona: string              # 人物设定
    audio:
      music_style: string
      voiceover: enum [none, ai_tts, real_voice, trending_sound]
      sound_effects: [string]
    text_overlay:
      strategy: enum [minimal, key_points, full_subtitle]
      style: string
    ai_generation_notes:           # 若使用 AI 生成
      recommended_model: string    # 建议模型
      prompt_skeleton: string      # 可直接使用的 prompt 骨架
      limitations: string          # 已知限制
```

## 约束传递规则

三层之间是约束传递关系，下层不得违反上层约束：

### Layer 1 → Layer 2 约束

| 证明点类型 | 适配母题 | 不适配母题 |
|---|---|---|
| 功能性能证明（防水/耐用/速度） | live_test, before_after, comparison | listicle, story_arc |
| 场景适配证明（收纳/穿搭/烹饪） | scenario_immersion, before_after | data_overlay |
| 社会证明（口碑/销量/权威） | testimonial, social_proof_cascade | live_test |
| 情感/身份认同 | story_arc, scenario_immersion | data_overlay, comparison |
| 性价比/数据 | data_overlay, comparison, listicle | story_arc |

### Layer 2 → Layer 3 约束

| 叙事结构 | 镜头约束 | 演员约束 |
|---|---|---|
| before_after | 需分屏/对比镜头，固定机位优先 | 需真人或产品出镜 |
| live_test | 手持跟拍 + 特写切换 | 需真人操作 |
| story_arc | 多场景多机位 | 需真人表演 |
| listicle | 快节奏切换，每 item 独立镜头 | product_only 可行 |
| data_overlay | 屏幕录制/动画 + 画外音 | product_only 或 ai_avatar |

### 选品移交包约束（如存在）

- Brief Seed Layer 1 的 `primary_proof_point` 必须对应 Handoff Package `selling_points_ranked` 中 differentiation = unique/rare 的卖点
- Layer 3 的 `talent_requirement.type` 受 `entry_constraint.production_capability` 约束
- Layer 3 的 `ai_generation_notes` 受 `entry_constraint.budget_level` 约束

## Golden 样例

### 样例 A：human_shot / organic / shoppable（中高置信，需验证后放量）

```yaml
production_ready_brief_seed:
  meta:
    source_video_id: "7382946510293847"
    source_video_url: "https://www.tiktok.com/@creator/video/7382946510293847"
    vlb_confidence: medium
    usage: validate_before_scale
    platform: TikTok
    category: Home & Kitchen > Storage
    handoff_aligned: true

  layer_1_product_proof:
    primary_proof_point: "免打孔安装，承重 15kg 不掉落"
    secondary_proof_points:
      - "适配多种墙面材质（瓷砖/乳胶漆/木板）"
    evidence_format:
      type: live_test
      detail: "安装后挂 15kg 桶装水，静置 24 小时，镜头记录无位移"
    proof_duration_ratio: 0.45

  layer_2_creative_blueprint:
    archetype: "极限测试型"
    compliance_risk: low
    narrative_structure:
      hook:
        type: shock
        content: "手举 15kg 桶装水悬在挂钩上方，松手"
        duration_sec: 2
      development:
        pattern: linear_escalation
        beats:
          - timestamp: "0-2s"
            content: "松手瞬间，水桶悬停"
            function: "视觉冲击建立悬念"
          - timestamp: "2-8s"
            content: "展示安装过程（免打孔，按压 30 秒）"
            function: "降低使用门槛感知"
          - timestamp: "8-15s"
            content: "切换三种墙面材质重复测试"
            function: "扩展适用场景"
          - timestamp: "15-20s"
            content: "24 小时后回访，水桶仍在"
            function: "时间维度证明持久性"
      conversion_node:
        type: product_reveal
        timing: "18s"
        content: "展示产品包装 + 价格对比（vs 打孔安装人工费）"
    rhythm_template:
      total_duration_sec: 22
      cut_frequency: "前 2 秒单镜头不切（保持悬念），中段每 2-3 秒一切"
      info_density: medium
      energy_curve: "高开（冲击）→ 平稳（安装）→ 递进（多材质）→ 尾部确认"

  layer_3_execution_params:
    camera_language:
      shots: ["中景人物+产品", "特写挂钩受力", "特写墙面材质切换", "延时摄影24h"]
      movement: "固定机位为主，安装段手持跟拍"
      angle: "平视 + 低角度仰拍（强化承重感）"
    lighting_tone: "自然光，居家环境"
    talent_requirement:
      type: real_person
      persona: "25-35 岁女性，居家装扮，邻家感，非专业模特"
    audio:
      music_style: "轻快电子，低音量背景"
      voiceover: real_voice
      sound_effects: ["松手瞬间的'咚'声", "按压安装的'咔嗒'声"]
    text_overlay:
      strategy: key_points
      style: "白色无衬体，左下角，承重数字放大加粗"
    ai_generation_notes:
      recommended_model: null
      prompt_skeleton: null
      limitations: "本条为真人实拍方案，AI 生成难以还原真实物理承重效果"
```

### 样例 B：ai_generated / paid / shoppable（待验证）

```yaml
production_ready_brief_seed:
  meta:
    source_video_id: "7391028374651029"
    source_video_url: "https://www.tiktok.com/@brand/video/7391028374651029"
    vlb_confidence: low
    usage: hypothesis_only
    platform: TikTok
    category: Beauty > Skincare > Serum
    handoff_aligned: true

  layer_1_product_proof:
    primary_proof_point: "7 天可见肤色均匀度提升"
    secondary_proof_points:
      - "成分安全性（无酒精/香精）"
    evidence_format:
      type: before_after
      detail: "AI 生成面部特写，左右分屏 Day1 vs Day7 肤色对比"
    proof_duration_ratio: 0.5

  layer_2_creative_blueprint:
    archetype: "变形记型"
    compliance_risk: medium  # before_after 在部分市场有功效声明风险
    narrative_structure:
      hook:
        type: pain_point
        content: "AI 生成面部暗沉特写，文字'肤色不均困扰你多久了？'"
        duration_sec: 3
      development:
        pattern: before_after
        beats:
          - timestamp: "0-3s"
            content: "痛点展示（肤色不均）"
            function: "建立共鸣"
          - timestamp: "3-8s"
            content: "产品使用过程（滴管→涂抹→吸收）"
            function: "展示使用仪式感"
          - timestamp: "8-15s"
            content: "Day1→Day7 渐变动画"
            function: "可视化效果"
          - timestamp: "15-18s"
            content: "成分表特写 + 无添加标注"
            function: "安全背书"
      conversion_node:
        type: urgency_trigger
        timing: "16s"
        content: "限时折扣倒计时 + 购物车引导"
    rhythm_template:
      total_duration_sec: 20
      cut_frequency: "每 1.5-2 秒一切，快节奏"
      info_density: high
      energy_curve: "低起（痛点）→ 渐升（使用）→ 高潮（效果）→ 急收（CTA）"

  layer_3_execution_params:
    camera_language:
      shots: ["AI 生成面部特写", "产品微距", "分屏对比", "成分表动画"]
      movement: "固定 + 缓慢推进"
      angle: "正面平视（面部）+ 45度俯拍（产品）"
    lighting_tone: "柔光，偏暖，护肤品质感"
    talent_requirement:
      type: ai_avatar
      persona: "AI 生成 20-30 岁亚洲女性面部，自然肤质，非完美"
    audio:
      music_style: "舒缓钢琴 + 轻电子"
      voiceover: ai_tts
      sound_effects: ["滴管滴水声", "涂抹时的轻柔音效"]
    text_overlay:
      strategy: key_points
      style: "细体白色，居中下方，Day 标注用金色"
    ai_generation_notes:
      recommended_model: "Seedance 2 / Kling 3（面部一致性好）"
      prompt_skeleton: "Close-up of Asian woman face, natural skin texture, soft warm lighting, split screen Day1 dull vs Day7 even tone, slow zoom, skincare serum application sequence..."
      limitations: "AI 面部在连续帧中可能出现皮肤纹理闪烁；before_after 对比需后期合成而非单次生成"
```

### 样例 C：hybrid / mixed / non_shoppable（中置信）

```yaml
production_ready_brief_seed:
  meta:
    source_video_id: "7385612093847561"
    source_video_url: "https://www.tiktok.com/@techreviewer/video/7385612093847561"
    vlb_confidence: medium
    usage: validate_before_scale
    platform: TikTok
    category: Technology > Audio > Earbuds
    handoff_aligned: null  # 无选品移交包

  layer_1_product_proof:
    primary_proof_point: "降噪效果在真实嘈杂环境中的表现"
    secondary_proof_points:
      - "佩戴舒适度（长时间不压耳）"
    evidence_format:
      type: scenario_immersion
      detail: "地铁/咖啡厅/街道三场景实拍 + AI 生成声波可视化叠加"
    proof_duration_ratio: 0.6

  layer_2_creative_blueprint:
    archetype: "沉浸体验型"
    compliance_risk: low
    narrative_structure:
      hook:
        type: curiosity_gap
        content: "地铁轰鸣声中突然静音——'世界安静了'"
        duration_sec: 2.5
      development:
        pattern: linear_escalation
        beats:
          - timestamp: "0-2.5s"
            content: "地铁噪音 → 戴上耳机 → 瞬间安静"
            function: "感官对比制造冲击"
          - timestamp: "2.5-10s"
            content: "三场景切换（地铁→咖啡厅→街道），每场景展示降噪"
            function: "多场景验证通用性"
          - timestamp: "10-16s"
            content: "摘下耳机，展示 4 小时佩戴无压痕"
            function: "舒适度证明"
          - timestamp: "16-20s"
            content: "AI 声波可视化：环境噪音 vs 降噪后对比"
            function: "数据化呈现"
      conversion_node:
        type: cta_text
        timing: "19s"
        content: "文字'链接在主页' + 产品名"
    rhythm_template:
      total_duration_sec: 22
      cut_frequency: "前 2.5 秒不切（沉浸），中段每 3 秒一切"
      info_density: medium
      energy_curve: "冲击（静音）→ 平稳（多场景）→ 收尾（数据）"

  layer_3_execution_params:
    camera_language:
      shots: ["真人中景佩戴", "特写耳机入耳", "环境全景", "AI 声波动画叠加"]
      movement: "手持跟拍（真实感）+ 固定特写"
      angle: "平视 + 侧面 45 度"
    lighting_tone: "自然光，城市环境光"
    talent_requirement:
      type: mixed
      persona: "真人 20-30 岁男性，通勤装扮 + AI 生成声波可视化层"
    audio:
      music_style: "无背景音乐，纯环境音切换（降噪开/关对比）"
      voiceover: real_voice
      sound_effects: ["地铁轰鸣", "咖啡厅嘈杂", "降噪启动的'嗡'声"]
    text_overlay:
      strategy: minimal
      style: "仅场景标注（'地铁''咖啡厅''街道'），白色小字"
    ai_generation_notes:
      recommended_model: "Kling 3（声波动画部分）"
      prompt_skeleton: "Abstract sound wave visualization, noise waveform chaotic red → noise-cancelled smooth blue, overlay on real footage, minimal style..."
      limitations: "声波动画为后期叠加，非视频主体；真人部分必须实拍以保证可信度"
```

## 与 D10 的接口

D10 Brief 编写时消费 Brief Seed 的路径：

1. 读取 `meta.usage`：`hypothesis_only` → 必须设计 A/B 变体；`validate_before_scale` → 小批量测试；`production_ready` → 可直接量产
2. Layer 1 → D10 Brief 的"核心信息"和"产品证明要求"
3. Layer 2 → D10 Brief 的"创意方向"和"叙事结构要求"
4. Layer 3 → D10 Brief 的"执行规格"和"技术参数要求"
5. `meta.vlb_confidence` → D10 Brief 验收卡的"来源置信度"字段

D10 Brief 验收卡新增检查项：
- "Brief Seed Layer 1 证明点是否在成品视频中被清晰呈现（非一笔带过）"
- "Brief Seed Layer 2 的 hook 类型和转化节点是否在成品中被保留"
- 如有偏离，需标注原因并评估是否影响核心逻辑

## 与 AI 生成工具的接口

Layer 3 的 `ai_generation_notes.prompt_skeleton` 可直接作为以下工具的输入 prompt：
- CreatOK Video Generator / Video Cloning
- Kling 3 / Seedance 2 / Sora 2
- 其他文生视频模型

使用时注意：
- `prompt_skeleton` 是骨架而非完整 prompt，需根据具体模型的 prompt 格式补充细节
- `limitations` 字段标注了该场景下 AI 生成的已知限制，生产前必须评估
- 如果 `talent_requirement.type = real_person`，则 AI 生成仅适用于辅助层（动画/叠加/背景），主体必须实拍
