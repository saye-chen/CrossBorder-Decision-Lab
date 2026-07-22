# CIDM 跨域集成协议

CIDM 是品类、SKU、国家、平台资本进入、追加、收缩、退出和再进入的最终主权 owner。输入卡必须含 `object_id`、生产域及运行时版本、`as_of_time`、证据/计算 ID、结论状态、置信区间、允许用途、禁止用途和到期时间。

CIDM 向 CIM 提交竞品池与需确认变化，向 VLB 提交内容最弱假设，向 CIG 提交客户价值假设，向 LIFD 提交库存/现金上限，向 PLCO 提交页面承接任务，向 AAMO 提交广告资本上限。参与域只返回本域 `proposed/validated/blocked/inconclusive` 结果，不直接改变投资档位。

CIDM 接收结果后必须按原模型重算并保留原分、建议分、接受/拒绝理由和版本。允许用途仅限声明对象与决策；禁止把竞品代理、内容评分、客户预测、页面转化或平台 ROAS直接写成市场利润或投资增量。

部分失败时保留已验证事实，受影响维度降级 `inconclusive`；不得用行业平均补洞。证据冲突不投票，按主权、证据等级、时效和不可补偿红线裁决。跨域回写必须记录冲突、责任人、成功、停止、回滚和结果回填。

## Selection Handoff Package（选品移交包）

CIDM 在选品决策完成且用户确认进入内容阶段时，可选组装 Selection Handoff Package 提交给 VLB，使 VLB 进入"战略锚定拆解模式"。

### 触发条件

以下任一条件满足时，CIDM 应主动提议生成 Handoff Package：
- 用户明确表示"开始做内容""准备拍视频""进入内容阶段"
- CIDM 完成 Decision Memo 及以上交付且结论为 Go/Conditional Go
- 用户从 CIDM 对话切换到 VLB 对话并引用同一产品

非强制：用户未要求或决策结论为 Stop/Blocked 时不生成。

### 组装逻辑

从 CIDM 已有评估中提取以下字段，不新增计算：

| Handoff Package 字段 | CIDM 来源 |
|---|---|
| `meta.confidence_level` | CIDM 整体置信度 |
| `meta.lifecycle_stage` | 用户确认的生命周期阶段 |
| `product_identity` | 决策对象基础信息 |
| `selling_points_ranked` | 七维评分中"产品差异化"维度的支撑证据 + VOC 高频卖点 |
| `target_segment` | 人群/国家校准中的目标画像 |
| `competitive_creative_gap` | 竞品内容审计（如有）或 VOC 中"用户在意但竞品没做好"的空白 |
| `entry_constraint` | 卖家画像 + 预算 + 合规快筛结论 |
| `strategic_intent` | 用户声明的内容目标；未声明时标记 `unspecified`，不得默认 conversion |

### 输出格式

完整 schema 定义见 VLB 侧 `references/selection-handoff-spec.md`。CIDM 输出时以 YAML 代码块呈现，标注 `cidm_version` 和 `assessment_date`。

### 主权边界

- Handoff Package 是 CIDM 的"建议性输入"，不约束 VLB 的拆解判断主权
- VLB 可以接受、部分接受或拒绝 Handoff Package 的锚定（如拆解发现视频证明点与选品卖点不一致）
- Handoff Package 中的 `selling_points_ranked` 不改变 CIDM 评分，仅为内容方向建议
- CIDM 不因 VLB 拆解结果自动修改 Handoff Package；更新需重新评估
