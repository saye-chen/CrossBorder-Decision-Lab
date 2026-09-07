---
name: localization-country-calibration
description: 默认用中文执行跨境国家、平台、语言、币税、单位、时区、动态事实和跨市场迁移资格校验。用于判断事实是否适用于目标国家/平台/对象/时点、不同市场数据能否比较、参数如何确定性转换、内容或机制能否迁移，以及未知、过期、冲突输入如何降级。不替代法律税务、投资、定价或其他专业域作最终决定。
---

# 本地化与国家校准底座（LCCA）

跨域统一硬门禁：国家校准报告或 handoff 交付前运行 `python3 ../governance/decision-quality/validate_domain_quality.py <report> --handoff`。

运行时版本：`LCCA-2026.07`。

ERDG contract: `ERDG-CONTRACT-2026.07`

Maturity: `controlled pilot`. L4 requires authorized real-market replay and independent review.

## 使用边界

F02 拥有本地化作用域、动态事实新鲜度、跨市场可比性、确定性转换合同和迁移等级资格；不拥有法律税务意见、市场进入、价格利润、物流、页面、广告、达人、内容、营销、客户或资本主权。

所有输入必须固定国家/管辖区、平台站点、经营对象、locale、决策时点和版本。未知、缺失、过期、冲突与不适用必须分开；不得填零或套用国家平均值。

## 路由

1. 使用 `references/charter-sovereignty-and-terminology.md` 固定问题与主权。
2. 读取[动态事实、作用域与转换](references/dynamic-facts-scope-and-conversion.md)，并使用 `scripts/validate_scope.py` 验证目标作用域。
3. 使用 `scripts/evaluate_dynamic_fact.py` 验证来源、双时间和新鲜度。
4. 需要转换时使用 `scripts/convert_quantity.py`；税口径只能消费 D05/D06 或适格专业来源批准的语义。
5. 比较市场时使用 `scripts/evaluate_comparability.py`。
6. 迁移机制、参数或表达时使用 `scripts/grade_transferability.py`。
7. 使用 `scripts/build_localization_handoff.py` 生成只读交接；下游不得提升 Claim 或动作上限。
8. 迁移和发布分别读取 `references/migration-and-consumer-acceptance.md` 与 `references/release-and-audit.md`。
9. 正式交接或状态变更必须运行 `scripts/validate_decision_contract.py`，接入 `ERDG-CONTRACT-2026.07`，并使用 `governance/erdg/adapters/localization-country-calibration/adapter.json`；失败时不得形成生效动作。

## 四级迁移

- `L4 direct_within_frozen_scope`：仅在完全相同且已冻结范围内复用。
- `L3 calibration_required`：机制可复用，目标参数或表达必须校准。
- `L2 rebuild_required`：只能迁移问题或研究结构，目标结论重建。
- `L1 prohibited`：红线或结构不兼容，禁止迁移。

`not_assessed`、`inconclusive`、`conflicted`、`expired` 是状态，不是迁移等级。

## 强制边界

- 翻译正确不等于本地化有效。
- 同语言、同平台或相邻国家不构成可迁移证据。
- 可比性不构成因果性；因果和增量 Claim 由 F01 控制。
- F02 只转换已批准税口径，不判断税务义务。
- 法律、税务、平台和安全红线不能被局部合同覆盖。
- 所有输出 `external_write=false`；真实执行仍需对应专业 owner 和用户明确授权。

## 成熟度

当前工程发布目标为 `controlled_pilot`。L4 仍需授权真实案例、真实双轨、目标市场专业复核、独立非实现者审查、实际结果和漂移再验证。

## 临时工作区

需要中间文件时使用 `mktemp -d` 创建任务专属目录，并写入 `.task-owner.json` 标记任务归属。只删除本任务创建且归属可验证的临时目录；清理后验证该目录不再存在，清理失败时报告准确路径。不得将真实客户、税务、法律、平台账户或个人数据写入 Skill 目录。

## 运营交付

当用户需要拿结果执行、转交或复盘时，读取[运营交付协议](../governance/interaction/operator-delivery.md)，按[专属成果清单](../governance/interaction/operator-deliverables.json)中本域条目交付。首屏用经营语言说明结论、理由、限制、下一步与停止条件；必要证据和计算放附录。独立解释不额外触发完整报告，正式决定保持既有专业门槛。
