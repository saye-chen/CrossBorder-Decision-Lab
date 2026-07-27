# ERDG 连续追问专家报告：成本变化与选择性重算

运行时：`ERDG-2026.01`；成熟度：`controlled pilot`。

## 可复算绑定

recomputation_id: `ERDG-RC-MULTITURN`
case_ids: `ERDG-M01, ERDG-M02`
input_hash: `5f2b6b0f96c7da462fa157c8ba28fd0fdebb78ae28a186754158dbf0310de7f0`
output_hash: `4cb30194c2b9113ac0cecddca8052bf0870fc869d93d6522baac0ebd8a7b02c8`

## 初始对象与当前态

对象 `SKU-D/UK/Platform/v1`。首轮报告R1使用运费Q1、退款率R1、汇率FX1，形成Decision D1 `effective`。后续四轮输入依次到达。

## Turn 2：新运费

Information Delta为 `Recalculation`。改变 `freight_cost` 和报价版本，不改变产品、订单或广告事实。影响闭包为E3→E8→现金→Decision，不重算E0—E2。

旧E3—E8标记superseded，新版本产生新输入和输出哈希。D1在复核期间不与新草稿同时effective。

## Turn 3：退款率上升

Delta为 `Recalculation`。退款影响E1及全部下游层，观察窗与原窗口不同，必须先对齐。若未对齐，只给区间，不把新退款率直接写回旧月份。

反证是上升可能由一次物流事故造成，不必永久修改默认退款参数。

## Turn 4：合规阻断

Delta为 `Revision + Gate Change`。合规参与域提交blocked Claim。即使E7仍为正，动作状态从executing转paused，Decision进入review。红线不等待新的加权评分。

## Turn 5：新汇率

Delta为 `Recalculation`，但只适用于新结算日。不得用当前汇率重写历史实际回款。预测现金更新，历史确认现金保持不变。

## Preserve / Recompute矩阵

| 模块 | Preserve | Recompute |
|---|---|---|
| 对象身份 | 是 | 否 |
| 产品事实 | 是 | 否 |
| E0—E2 | 运费轮是 | 退款轮否 |
| E3—E8 | 否 | 是 |
| 合规Gate | 新证据覆盖当前态 | 是 |
| 历史现金 | 是 | 否 |
| 预测现金 | 否 | 是 |

## 候选与动作

不行动会让旧Decision继续暴露，不能视为零风险。推荐暂停受影响动作、完成合规处理和退款窗口对齐，再按最新输入重算。不得删除R1—R4历史。

## 成功、停止和回滚

成功为每轮changed_fields、preserved、affected、hash和current唯一性一致。依赖图出现循环、旧哈希复用或两个effective即停止。回滚恢复最后可信版本和对应参数，不把新证据丢弃。

## 主权与深度保持

用户要求简短时，可以只显示当前结论、变化、动作和停止门，但底层仍完成上述研究。ERDG不替代合规或定价主权。

## L4与回填

连续重算测试证明版本和机制，不证明阈值准确。执行后的退款、现金和合规结果需进入真实回放。

退款冲突必须区分结构变化与一次事故。每轮计算保存版本、哈希和不可计算原因；对象—证据—计算—Claim—Decision—Action血缘保持追加式记录。
