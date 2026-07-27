# PLCO 数据合同与自动化

## 规范对象与版本

平台、国家、店铺、Listing、SKU/变体、Offer、页面层、槽位、设备、流量、事件和实验使用稳定 `object_id`。页面快照保存 `page_version_id/parent_version_id/effective_at/collected_at/as_of_time/source/fingerprint/current_status`，任一对象只能有一个当前版本。缺失使用 `unknown`，不得填零值。

证据记录 `evidence_id/access_level/claim_ids/allowed_uses/forbidden_uses/expires_at`；计算记录 `calculation_id/model_version/input_ids/input_hash/output_hash/window/units/currency/assumptions`。页面事实、后台授权、脚本派生、推断和因果结论分开。

## 守恒与校验

- 曝光≥点击≥有效到达，加购、结账和购买按事件定义及去重规则对账；不同漏斗不得硬拼。
- Claim 必须绑定产品事实、证据、权利、适用国家/平台、版本和过期日。
- Offer、库存、配送、页面显示和实验版本必须可追溯到各自主权来源。
- 非有限值、负计数、分子大于分母、币种/时区/窗口冲突、循环血缘和多个当前版本必须失败。

## 部分失败

抓取、后台、发布传播或实验读取返回 `complete/partial/inconclusive/failed`、成功槽位、失败槽位、数据截止和重试条件。页面抓取失败不得抹掉后台事实；后台失败不得把公开页面当授权配置；失败事件和设备分区不得补零。

自动化只生成 `proposed` 候选稿、图片 Brief、模块方案、排序或回滚包。输出必须附页面版本、依赖、禁止 Claim、审批、成功、停止、回滚和过期条件。

## 外部写入

发布、覆盖、合并、拆分、删除、改价、改 Offer、变体和页面替换必须明确授权，先保存前值与资源指纹，限定精确对象，使用幂等键并核验传播。部分成功时按槽位/站点恢复，不得整批盲重试。评论操纵、非法合并和越权改价始终禁止。
