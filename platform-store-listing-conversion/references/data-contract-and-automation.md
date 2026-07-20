# D08 数据合同与自动化

规范键为 `store × listing × sku/variant × offer × page_layer × device × traffic × page_version_id × as_of_time`。页面快照、产品事实、Offer、库存和漏斗分别保留来源；缺失、零值、不可见和 not_applicable 分开。

脚本校验对象身份、版本、证据指纹、漏斗守恒、变体关系和单一 Current 版本，保存输入/输出哈希。重跑幂等，不静默覆盖旧页面或报告。

抓取、后台或实验失败返回可用层和 `partial/inconclusive`，不猜测隐藏字段。外部写入、发布、合并、删除、改价或页面替换必须明确授权；默认只生成候选。动作含成功、停止、回滚和结果回填。

规范合同还必须提供 object_id。
