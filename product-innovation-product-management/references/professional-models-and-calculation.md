# 专业模型、参数、校准与压力计算

## 1. 共同计算合同

八类模型只回答 D03 自有的产品判断，不替代 D06 价格利润现金、D04 供应商和量产质量、D05 法律准入、D07 库存履约或其他业务域最终决定。

所有数值必须使用十进制字符串。比例输入通常位于 `[0,1]`；数量和权重不得为负；单位必须显式声明。禁止把缺失、不可得、不适用、尚未观察、拒绝提供、无效和观测零值统一转成 `0`。

参数来源按以下优先级选择：

1. 当前对象、国家、平台和版本的授权实测；
2. 同一产品族的可比历史数据；
3. 经Owner批准且仍在有效期内的业务参数；
4. 明确标为benchmark的外部或跨域参数；
5. 仅用于敏感性分析的假设。

每个参数必须保留 `owner`、`approved_by`、`scope`、`valid_from`、`valid_to` 和 `source`。缺少元数据的权重不得用于路线图排序。任何经济参数只可作为D06返回值消费，D03不得自行发明。

## 2. unmet_need：未满足需求强度

输入：

- `importance = I ∈ [0,1]`；
- `satisfaction = S ∈ [0,1]`；
- `support_weight = W_s ≥ 0`；
- `conflict_weight = W_c ≥ 0`。

公式：

```text
unmet_score = I × (1 − S)
evidence_consistency = W_s / (W_s + W_c)
```

当总证据权重为零时，一致性为零而不是一。`evidence_consistency < 0.5` 时只能返回 `inconclusive`。未满足分高不等于市场可进入，也不等于值得投资；CIDM仍拥有资本进入权。

压力：

- T0：高重要度、高一致性、低满意度；
- T1：重要度或满意度位于区间边缘；
- T2：支持与反证接近，结论不稳定；
- T3：代理指标与直接VOC冲突；
- T4：关键安全、合规或现金门失败，分数不得补偿。

校准检查：同一量表、相同样本框和相同场景下，重要度上升不得降低未满足分；满意度上升不得提高未满足分。跨国家量表未经测量等价性验证不得直接排序。

## 3. opportunity_interval：机会区间

输入必须满足：

```text
0 ≤ low ≤ base ≤ high
width = high − low
```

low/base/high必须来自同一对象、口径、期间和单位。该模型不计算市场规模，而是校验跨域或研究输入的区间一致性并保留不确定性。禁止用base替代完整区间，也禁止把区间宽度误作置信区间，除非上游明确提供统计含义。

压力：

- T0：窄区间且来源一致；
- T1：区间较宽但不会改变MVP设计；
- T2：低位与高位会导向不同产品定义；
- T3：不同来源区间不重叠；
- T4：单位、期间或对象版本不一致，阻断。

校准以真实结果对区间覆盖率、偏向性和宽度进行回填；连续低估或高估必须触发来源降级。

## 4. constraint_feasibility：规格与功能约束

对每个规格 `j`：

```text
min_j ≤ value_j ≤ max_j
unit_j is present
```

同时检查功能互斥集合和依赖边：

```text
selected(A) ∧ mutually_exclusive(A,B) ∧ selected(B) → blocked
selected(A) ∧ depends_on(A,B) ∧ ¬selected(B) → blocked
```

所有违反项必须逐项输出，禁止用平均通过率掩盖关键尾部失败。安全关键规格、法规相关规格、不可逆制造规格和客户承诺规格属于非补偿门。

压力：

- T0：全部规格位于稳定区间；
- T1：接近工程边界但仍有验证余量；
- T2：多个约束共同收窄可行域；
- T3：功能依赖、互斥或国家版本冲突；
- T4：尾部分位、红线规格或单位失败，直接阻断。

## 5. mvp_coverage：MVP关键假设覆盖

只计算标为 `critical=true` 的假设：

```text
covered_i = coverage_i ≥ threshold_i
critical_coverage = covered critical assumptions / all critical assumptions
```

没有关键假设时覆盖率为零并阻断，而不是视为100%。任何关键假设未达阈值时MVP不得标为可推进。coverage代表验证设计覆盖，不代表假设已被真实世界证实。

关键假设至少分为：用户任务、问题强度、方案可理解、方案可用、关键规格可实现、交付可行、Claim可支持和经济边界可接受。对应主权域未接受时必须保留pending。

## 6. variant_portfolio：变体净增量

公式：

```text
net_incremental_demand
  = incremental_demand
  − cannibalized_demand
  − complexity_demand_equivalent

cannibalization_rate
  = cannibalized_demand / incremental_demand
```

增量需求为零时蚕食率返回null，禁止除零或伪造0%。`net_incremental_demand ≤ 0` 时拒绝该变体建议。复杂度等价需求必须由可审计的产能、库存、页面、服务或运营约束换算；缺少来源时只能做情景参数。

压力包括需求下修、蚕食上修、MOQ/库存碎片、页面变体混淆、国家版本分裂和退出残值。D03只判断产品组合逻辑；最终利润、库存量和页面动作分别由D06、LIFD和PLCO决定。

## 7. packaging_impact：包装体积、保护与代理

公式：

```text
volume_cm3 = length_cm × width_cm × height_cm
dimensional_weight_kg = volume_cm3 / dimensional_divisor_cm3_per_kg
```

尺寸和除数必须严格大于零。除数必须带承运商、渠道、国家、有效期和来源；过期除数不得继续使用。保护评分低于最低保护要求时增加`packaging_protection`硬门。

体积重只是物流代理，不是实际计费结果；最终分段计费、附加费和路线属于LIFD/D06。体验评分不能补偿跌落、防潮、密封、危险品或标签红线。

压力至少覆盖：尺寸取整、峰值包装公差、运输跌落尾部、退货再包装、承运商除数变化和保护/体积冲突。

## 8. roadmap_priority：路线图排序

对候选项 `c` 和获批权重 `w_k`：

```text
Σw_k = 1
priority_score_c = Σ(score_c,k × w_k)
```

排序稳定规则：按分数降序，再按候选ID稳定排序。第一、第二名同分时返回`inconclusive`，不得伪造唯一最优。权重变化导致第一名变化时必须报告敏感性，而不是沿用旧结论。

权重建议维度可包括用户价值、证据强度、战略适配、学习价值、可逆性和跨域可行性，但具体权重必须由Owner批准。财务价值只能消费D06结果。

压力层覆盖权重扰动、评分区间、关键依赖失败、资源容量下降和时间窗口变化。应报告至少保守、基准和压力三种排序。

## 9. traceability：需求到验证的追踪

合法链路：

```text
Requirement → Specification → Verification
Specification → Claim → Verification
```

每个Requirement至少连接一个Specification；每个Specification必须反向指向Requirement并连接Verification；每个Claim必须连接存在的Specification和Verification。任一孤立节点都会阻断设计冻结。

Claim的存在不代表可发布。证据等级、允许用途、国家平台、语言、媒介和有效期仍由Claim合同与D05/PLCO/VLB接受控制。

压力覆盖孤立节点、跨版本链接、验证撤回、Claim升级、规格漂移和旧报告仍引用失效验证。

## 10. 非补偿门与状态

安全、法律准入、现金、关键规格、证据完整性、对象版本和外部授权失败时，任何得分都不得放行。

- `proposed`：D03机制可形成受控建议；
- `inconclusive`：证据冲突、参数不稳定或关键跨域结论未回；
- `rejected`：候选在D03自有逻辑内不值得继续；
- `blocked`：红线、合同、版本或不可补偿约束失败；
- `validated`：仅限D03自有事实且满足相应验证合同，不代表其他域接受。

## 11. 校准与漂移

真实结果回填至少记录输入快照哈希、模型版本、参数版本、建议、实际动作、实际结果、失败/退出、残余暴露和复核人。校准不允许用未来参数改写历史。

触发重新校准：

- 连续三个同类案例方向性偏差；
- 区间覆盖率显著恶化；
- 国家、平台、品类或生命周期迁移；
- 规格、承运商、法规或成本合同版本变化；
- 关键反例导致既有阈值失效。

没有授权成熟真实回放时，这些模型只能保持`controlled pilot`，自动化性质测试不能替代L4证据。

## 12. 专家检查清单

1. 对象、国家、平台、版本和双时态是否冻结？
2. 输入是事实、Owner参数、benchmark还是假设？
3. 公式、单位、范围和缺失语义是否可复算？
4. 是否存在平均通过但关键尾部失败？
5. 是否把代理指标误作直接事实或因果证据？
6. 非补偿门是否可能被总分覆盖？
7. 模型输出是否越权替代D04/D05/D06等结论？
8. 参数变化是否会翻转推荐？
9. 停止、回滚、退出和重接受条件是否明确？
10. 是否保留了结果回填、校准和漂移触发？
