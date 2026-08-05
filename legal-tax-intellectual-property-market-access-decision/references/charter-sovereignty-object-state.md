# 章程、双层主权、对象与状态

## 章程与主权

D05 管理商业市场准入 Gate、动作上限、Claim 使用边界、适格专业复核路由和合规恢复。法律解释、最终税务处理、FTO、正式认证、实验室结果及其他需要执业资格或法定授权的结论由适格专业主体保留。

## 规范对象

一个决定由 `subject_ref + product_ref + scope_ref + use_ref` 唯一限定：

- `subject_ref`：经营对象 ID、类型和版本；
- `product_ref`：产品 ID/版本，可选 SKU、BOM、包装、样品或批次版本；
- `scope_ref`：司法辖区、ISO 国家、平台、销售模式、主体角色和业务时间；
- `use_ref`：预期用途、可预见误用、用户年龄范围和接触场景。

对象或版本不同不得静默合并。一个市场、平台、主体、用途或时间窗的结论不得扩展到另一个范围。

## 生命周期

`sense → define → qualify → launch → learn → recover → exit`

## 状态

| 状态 | 含义 | 动作上限 |
|---|---|---|
| `intake` | 已登记，最小输入未通过 | 只补充输入 |
| `screening` | 初筛中 | 只准备可逆材料 |
| `evidence_required` | 关键证据缺失 | 补证，不执行依赖动作 |
| `professional_review` | 等待适格专业复核 | 保持受影响动作冻结 |
| `conditionally_cleared` | 条件、对象和时间受限 | 仅执行列明可逆动作 |
| `cleared_for_named_use` | 具名用途商业 Gate 通过 | 不超过列明范围 |
| `blocked` | 红线或关键缺口 | 停止依赖动作 |
| `suspended` | 既有结论因变化或事故冻结 | 停止并进入影响闭包 |
| `remediation` | 整改和重新验证中 | 仅执行整改动作 |
| `withdrawn` | 主动撤回 | 不再继续 |
| `expired` | 依赖证据或意见过期 | 重新核验 |
| `superseded` | 被新版本替代 | 只读历史 |
| `closed` | 退出完成 | 只读历史与回放 |

## 转换不变量

- `cleared_for_named_use` 必须经过 `conditionally_cleared` 或完整复核路径，不得从 `intake/screening` 直达。
- `blocked/suspended/expired` 不得直接进入 cleared 状态；必须先进入 `remediation` 或重新 `professional_review`。
- 任何产品、范围、用途、规则或专业意见版本变化都生成新决定版本。
- 历史决定不可删除；`superseded` 指向替代版本。
- 当前暂存实现禁止产生 `cleared_for_named_use`。
