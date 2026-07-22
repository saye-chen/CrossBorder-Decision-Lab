# CAPM 数据合同与自动化

所有对象必须携带稳定的 `object_id`（或可无损映射的 `canonical_id`）与 `object_version`；跨域传递不得仅用达人昵称、短链或展示名充当主键。

每条动态事实记录 `as_of_time`、来源和过期日。任何外部写入（付款、寄样、改佣、冻结、发送或平台操作）必须在幂等键、权限校验和用户明确确认后执行。

## 目录

1. 对象和字段
2. 数据语义
3. 血缘与权限
4. 自动化安全
5. 专属决策内核

## 对象和字段

核心对象：`creator_candidate`、`affiliate_partner`、`partnership`、`content_asset`、`rights_record`、`affiliate_order`、`affiliate_program`、`decision_report`。每个对象使用稳定 canonical ID、版本、创建/更新时间、来源系统和状态；平台账号是别名，不是主键。

货币使用 `{amount,currency,tax_inclusive,fx_rate_id}`；比率声明分母；时间使用 ISO-8601 与 IANA 时区；国家使用 ISO 3166-1 alpha-2。零值与缺失不同。金额、计数、概率不得非有限；比率通常在[0,1]。

权利记录逐项列 platform/use/territory/start/end/edit/identity/AI/exclusivity/revocation。订单记录区分 raw、duplicate、fraud、refund/chargeback、mature_valid，不允许一单进入多个排除桶。

## 数据语义

每个字段标记 observed/authorized/derived/inferred/causal 和 S/C等级。`attributed` 不能改名 `incremental`。成熟由退款、拒付、结算和归因窗决定，不用固定三个月。

动态阈值包含 `threshold_id/value/unit/source_evidence_id/platform/country/category/cohort/valid_from/expires_at/approved_by/fallback_if_expired`。缺失或过期时返回 `threshold_unverified`。

## 血缘与权限

对规范化 JSON 使用稳定排序和 SHA-256；保存 input/output/schema hash、脚本版本和 calculation ID。验证器实际重算，不信任 `verified=true`。

只读取用户授权的数据。客户上下文去识别并最小化；年龄、隐私、受益所有人、付款和身份字段按最小权限。撤回或删除请求沿原件—衍生内容—报告—导出闭包处理，保留合法审计记录而不扩散PII。

## 自动化安全

发现、评分、提醒、报告草拟可自动；发送邀约、签约、付款、改佣、冻结、举报、删除、CRM写入和平台发布必须用户确认及审计日志。高风险拒绝不能只由模型分数触发。

managed临时目录必须有 `.task-owner.json`；只删除匹配任务ID的目录。不得把用户数据或运行输出写进Skill目录。

## data-contract-and-automation 专属决策内核

机制：对象版本图连接证据、计算、权利、合同、动作和报告；字段变化只重算受影响闭包。

计算/判定：Schema校验、范围/枚举/日期顺序、low≤mid≤high、订单守恒、币种/税口径、哈希、幂等和权限。

反事实：重复证据不增信；顺序变化不改组合计算；币种、税或退货计提基数改变而未重算则失败；删除同意/年龄/权利字段不得通过高风险动作。

失效模式：昵称作主键、null填0、跨币种相加、时间窗错位、双扣退款/COGS、哈希自报、重复webhook、对象串线、过期规则继续用。

动作：拒绝、隔离、降级、补证、重算、人工审批或受控退出。输出具体JSON path和错误码。

机器入口：`schemas/*.schema.json`、`scripts/decision_state.py`、`scripts/validate_cross_skill_handoff.py` 与 `scripts/test_capm.py`。
