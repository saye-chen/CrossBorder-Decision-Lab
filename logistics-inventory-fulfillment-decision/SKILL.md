---
name: logistics-inventory-fulfillment-decision
description: 默认用中文执行专家级跨境物流、库存与履约决策。覆盖采购放行至可售库存、头程/干线/清关/入仓尾程、海外仓与平台仓、多级仓网路由、需求预测、ATP/CTP、补货与安全库存、多平台库存保护、仓内吞吐、订单尾程、退货退供、特殊货物、追踪召回、物流合同与费用、异常恢复、清仓和海外库存退出；当用户要求判断走什么路线或仓、何时补货补多少、库存如何分配、为什么缺货积压或履约失败、退货和尾货如何处理时使用。不替代供应商采购、法律税务、公司级资金、定价促销、广告、Listing或客户补偿主权。
---

# 物流、库存与履约决策

运行时版本：`LIFD-2026.04`。

## 专业性与决策可用性硬约束

所有模式先读取 [professional-depth-governance.md](references/professional-depth-governance.md)。只允许压缩展示，不得省略对象/版本、数据质量、红线、数量守恒、证据与反对证据、候选与不行动、尾部情景、动作、成功、停止、回滚、退出和结果回填。

## 入口与交付层级

- Decision Card：单路线、补货、ATP、容量或异常。
- Decision Memo：仓网、库存配置、履约恢复或海外库存退出。
- Logistics Diligence：多国多仓、重大资本、召回或连续性设计。

正式交付读取 [professional-report-delivery.md](references/output-protocols/professional-report-delivery.md)。

## 临时工作区与源文件

用户源文件只读，不覆盖、改名、移动或删除。复杂、可恢复任务使用 managed 模式：`${TMPDIR:-/tmp}/logistics-inventory-fulfillment-decision/<YYYYMMDD-HHMMSS>-<task-slug>/`，写入包含 Skill、任务 ID 和创建时间的 `.task-owner.json`；短任务使用 `mktemp -d`。后台导出、路线报价、库存快照、计算中间件和截图只放本任务目录。结束时只删除归属标记与任务 ID 完全匹配的目录并验证不存在；清理失败时报告准确残留路径与原因。

## 跨域边界与双向数据交换

与 CIDM、CIM、VLB、CIG、PLCO、AAMO 的输入卡、允许/禁止用途、部分失败和冲突裁决读取 [skill-integration-protocol.md](references/skill-integration-protocol.md)。LIFD 只拥有物流库存履约主权；结构化接口读取 [data-contract-and-automation.md](references/data-contract-and-automation.md)。

## 与品类投资决策 Skill 的边界

当物流网络、仓容、库存或履约成本影响品类进入、追加投资或退出判断时，路由 `category-investment-decision`。本 Skill 向 CIDM 提交物流可行性、总相关成本、容量上限、服务水平、退出/清仓成本和下行情景；CIDM 回传资本姿态和利润/现金红线。本 Skill 拥有物流库存履约主权，CIDM 拥有资本进入/退出主权；LIFD 不得直接改变投资结论，CIDM 不得反向修改补货、路线或库存分配。CIDM 缺失或失败时仍完成物流诊断，资本可行性标记 `inconclusive`。

## 与广告分析 Skill 的边界

当广告放量涉及库存可售量、配送承诺或仓容时，本 Skill 向 `advertising-analysis-measurement-optimization` 提供 ATP/CTP、可履约数量、承诺上限、批次衔接和降级条件；AAMO 据此约束广告消耗上限和放量节奏。本 Skill 拥有库存履约主权，AAMO 拥有广告预算/出价主权；广告消耗不得超出可履约容量，AAMO 不得反向修改补货或库存结论。AAMO 不可用时仍完成物流诊断，广告协同标记 `inconclusive`。

## 与平台店铺Listing转化 Skill 的边界

本 Skill 保留 ATP/CTP、库存分配、配送承诺、退货和容量主权。页面库存、配送、预售、退换或可购买显示需要诊断/修复时，向 `platform-store-listing-conversion` 提供对象、时点、合格可售量、承诺上限、证据 ID 和允许用途；PLCO 只能据此限制或修复页面承诺。本 Skill 拥有库存履约主权，PLCO 拥有页面承接主权；PLCO 不得反向修改补货、路线或库存结论。PLCO 不可用时仍完成物流诊断，页面承诺标记 `inconclusive`。

## 目标与主权

把需求、供应、资金、渠道和客户承诺转化为可复算、可执行、可停止、可回滚的物流库存动作。

本 Skill 最终决定：

- 物流网络、运输路线、仓配服务商专业方案；
- 服务水平、安全库存、再订货点、补货量和批次衔接；
- 国家、仓库、平台之间的库存配置、保护和调拨；
- 可履约数量、承诺日期、仓内/尾程能力和降级条件；
- 退货、退供、库存异常、履约异常和海外库存处置路径。

不得替代：D01资本进入/退出，D03产品定义，D04供应商/采购/生产/质量，D05法规税务及法律结论，D06公司级资金和定价，PLCO渠道与Listing，AAMO广告动作，D12促销品牌，D13客户补偿与关系动作。需要广告协同时路由 `advertising-analysis-measurement-optimization`；缺少成熟证据时结论保持 `inconclusive`。跨域动作只提交 `proposed`，由主权域 `validated/rejected`。

## 不可补偿红线

任一命中即阻断相关动作：

- 禁运、危险、安全、召回、证件或清关红线未解决；
- 库存、货权、批次或主数据不可对账；
- 峰值现金超限或下行情景负贡献仍要求无条件扩量；
- 关键路线、仓容、吞吐或尾程无可信能力且无备选；
- 需求证据不足却要求不可逆大额补货；
- P90/P95交期无法覆盖承诺且无降级方案；
- 推断、报价、平均值或外部基准被冒充真实经营事实；
- 关键计算不可复算或违反数量守恒；
- 非主权域要求直接改采购、价格、广告、活动或客户动作。

## 九层工作流

严格依次执行，不从单一指标直接跳到动作：

1. **对象与时点**：锁定SKU、批次、国家、渠道、仓、路线、时间窗和版本。
2. **数据有效性**：统一单位、币种、税口径、时区、状态和更新时间。
3. **Hard gates**：检查合规、安全、货权、现金、利润、能力和守恒。
4. **状态识别**：识别生命周期、库存、订单、在途和履约状态。
5. **根因分层**：区分需求、供应、运输、清关、仓内、尾程、系统和策略。
6. **候选生成**：至少生成当前、不行动和两个可行替代方案。
7. **确定性比较**：计算总相关成本、服务、现金、风险、尾部和恢复。
8. **动作设计**：明确对象、数量、时间、责任域、上限和依赖。
9. **闭环**：定义成功、停止、回滚、升级、退出和实际结果回填。

## 输入质量路由

- `Q3`：粒度一致、关键成本完整、库存可对账、交期有分布；允许具体数量和动作。
- `Q2`：少量缺失可由区间覆盖；只给条件方案和翻转阈值。
- `Q1`：主要依赖用户假设、报价或外部基准；只做筛查和验证设计。
- `Q0`：对象、单位、货权、库存、合规或关键成本不可用；只输出阻断和补数清单。

缺失值不得填零；点估计不足时改用区间；销量受缺货截尾时不得直接当真实需求；平均交期不得替代尾部分位数。

## 场景路由与必读文件

- 网络、运输、包装、多仓、尾程：读 [network-transport-packaging.md](references/network-transport-packaging.md)。
- 预测、补货、ATP/CTP、批次衔接：读 [forecasting-replenishment.md](references/forecasting-replenishment.md)。
- 多平台分配、库存健康、策略分层：读 [inventory-allocation-health.md](references/inventory-allocation-health.md)。
- 仓内作业、供需平衡、吞吐：读 [warehouse-operations-capacity.md](references/warehouse-operations-capacity.md)。
- 订单履约、退货、退供、海外库存退出：读 [fulfillment-reverse-logistics.md](references/fulfillment-reverse-logistics.md)。
- 特殊货物、主数据、追踪和召回：读 [special-cargo-traceability.md](references/special-cargo-traceability.md)。
- 合同、账单、Cost-to-Serve和完美订单：读 [contracts-cost-to-serve.md](references/contracts-cost-to-serve.md)。
- 异常、安全、欺诈和业务连续性：读 [incident-security-continuity.md](references/incident-security-continuity.md)。
- 平台、国家、品类和履约模式：读 [platform-country-calibration.md](references/platform-country-calibration.md)。
- 跨域交接和输出格式：读 [decision-contracts-and-output.md](references/decision-contracts-and-output.md)。
- 连续追问、报告继承、对象当前态与增量重算：读 [report-lineage-and-progressive-rebase.md](references/report-lineage-and-progressive-rebase.md)。

只读取当前任务需要的reference；复杂全链路项目可组合读取，但不得重复同一主权结论。

## 确定性脚本

关键数量和经济结论必须运行脚本，不得心算：

- `scripts/logistics_economics.py`：落地、履约、尾程和总相关成本；
- `scripts/inventory_ledger.py`：库存位置、在途折扣和数量守恒；
- `scripts/replenishment.py`：安全库存、ROP、约束补货和投影衔接；
- `scripts/demand_forecast.py`：移动预测、经验误差区间、偏差与WAPE；
- `scripts/lead_time_service.py`：交期P50/P75/P90/P95与承诺概率；
- `scripts/network_routing.py`：候选路线过滤与风险调整比较；
- `scripts/multi_warehouse_flow.py`：多仓—目的地容量约束流量分配与缺口；
- `scripts/inventory_allocation.py`：多平台保护、共享池和边际分配；
- `scripts/order_capacity.py`：ATP、CTP、供需缺口和仓内吞吐；
- `scripts/warehouse_capacity.py`：收货至承运商提货的分阶段瓶颈与队列；
- `scripts/reverse_exit.py`：退货净回收、继续持有和海外库存退出；
- `scripts/cost_to_serve.py`：对象级成本、合同净成本和完美订单；
- `scripts/traceability_recall.py`：追踪谱系与召回未解决数量。
- `scripts/validate_decision_contract.py`：通过仓库共享内核阻断不完整、越权或不可追溯输出。
- `scripts/decision_state.py`：对象当前态、报告血缘、证据过期和增量重算完整性。
- `scripts/validate_historical_replay.py`：阻止未完成授权历史回放时宣称生产就绪。

脚本输入失败、非有限数、负数量、单位冲突或不可行约束必须返回错误，不得静默修复。

## 决策纪律

- 先过红线，再做比较；不可补偿条件不得用加权总分抵消。
- 需求、交期、成本、损失和回收值优先使用区间、分位数或情景。
- 区分平均效率与边际效率；新增一单位库存、运力或仓容必须仍有正边际价值。
- 不行动不是零成本，计入仓储、资金、价值衰减、缺货和机会成本。
- 所有“最优”至少给低成本、平衡、高服务/高韧性Pareto候选及未选原因。
- 动态平台、国家、承运商、费率、税费和特殊货物规则必须执行时核验当前官方或授权资料。

## 输出最低合同

任何完整决策必须包含：

```text
决策对象与as_of_time
生命周期与当前状态
输入质量、事实、假设、推断和证据ID
Hard gates与阻断项
主根因、反对证据和最弱假设
候选方案与不行动基线
确定性计算、区间、敏感性和翻转阈值
推荐动作：对象、数量、时间、责任域、上限
成功指标、停止、回滚、升级和退出条件
跨域proposed事项与补证需求
模型版本、数据日期和实际结果回填字段
```

快速回答可以压缩展示，不得删除研究、边界、风险和停止条件。

## 失败与海外库存退出

失败时依次评估：冻结新增暴露、核验货权/批次/可售性、自然销售、受控降价、组合包、转平台/国家/仓、折扣/B2B/批发、合格清算商或尾货买方、退供应商/返工/拆件、跨境退运、捐赠/回收/合规销毁。

召回、禁售或安全风险货物不得进入降价或尾货渠道。货代作为运输商与作为库存买方必须分离；买方主体、货权、付款、税务、品牌去标、产品责任和最终流向不清即阻断。

## 专家级交付门

缺少下列任一项，不得标记为完整决策：数据质量、hard gates、替代方案、不行动基线、可复算计算、敏感性、反对证据、下行情景、责任与时间、成功/停止/回滚/退出、跨域确认、实际结果回填。

不得把Golden Case或合成fixture当成真实效果证明。正式生产发布前至少回放3个经授权、已脱敏、具有实际结果和证据哈希的历史案例；未满足时只允许`controlled pilot`，不得标记`production ready`。
