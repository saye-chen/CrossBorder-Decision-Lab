# 身份、事件与授权

## 分析主键

| 层级 | 含义 | 用途 |
|---|---|---|
| Account | 单平台/店铺账号 | 平台内行为 |
| Person | 经授权且可合理归并的个人 | 生命周期与触达 |
| Household | 共享购买决策的家庭/组织 | 避免重复获客/权益 |

确定性规则优先，概率匹配仅形成带置信度的候选边。低于业务审定阈值不合并。保留原账号与合并记录，使错误合并可逆。

## 标准事件

```text
event_id / event_time / ingest_time / customer_key / anonymous_key
market / channel / store / session / event_type / object_type / object_id
quantity / amount / currency / consent_state / source / data_quality_flag
```

事件域包括认知、考虑、交易、履约、使用、服务、反馈和触达。状态快照、训练和实验必须按 `event_time` 重建；迟到数据追加修订版本，不静默改写历史。

## 授权门槛

对每个用途记录授权范围、市场、渠道、取得/撤回时间和保留期。分析可用不等于可触达；撤回、退订、删除和敏感事件优先于模型分数。
