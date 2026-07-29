# 主权、对象与供应网络

六类主权决定必须绑定唯一对象、版本、owner、证据、计算、限制、成功、停止、回滚和结果回填。D04 不得改写资本、产品、合规、价格现金、物流库存或客户关系结论。

规范对象包括 Supplier、Facility、Supply Network Node、Product Specification、BOM、RFQ/Quote、Tooling、Sample、Production Order、Production Batch、Inspection Lot、Deviation/Concession、Nonconformance、CAPA/8D、Engineering Change 和 Release Decision。

供应网络穿透签约方、收款方、开票方、实际工厂、分包商、关键物料、专用模具、关键设备和地区。双源共享关键节点时不得视为独立冗余。模糊匹配只产生候选关联，不能自动合并主体、工厂、批次或报告。

数量守恒：

`投入 = 合格 + 不合格 + 返工中 + 报废 + 在制 + 已解释差异`

规格、BOM、材料、工艺、设备、工厂、分包、包装或检验方法变化必须生成 Engineering Change，声明影响、重新验证、生效批次、旧批处置和回滚。

## 六类主权与对象

| 决定 | 主对象 | D04 最终拥有 | 不拥有 |
|---|---|---|---|
| supplier_selection | Supplier + Facility + Network | 制造与质量能力、主备结构、分配上限 | 资本进入、法律准入 |
| procurement_commitment | Quote + BOM + Production Order | 采购条件、数量与供应承诺是否可接受 | 实际签约、付款、公司现金批准 |
| sample_approval | Sample + Specification | 样品证明范围、条件和重新验证 | 产品规格意图 |
| production_release | Process + Production Order | 试产/爬坡/量产放行及暴露上限 | 外部执行生产 |
| batch_quality_release | Production Batch + Inspection Lot | 放行、隔离、返工、报废或拒绝 | 法定召回和客户补偿 |
| supplier_recovery_exit | Incident + CAPA + Supplier | 遏制、恢复、切换、暂停或退出 | 资本/库存/客户最终处置 |

## 主键与版本

- Supplier：法定主体标识 + 司法辖区；不可靠时使用 provisional ID。
- Facility：主体 + 物理场所 + 制造活动；同地址多主体不得合并。
- Supply Network Node：节点类型 + 主体/场所 + 生效时间。
- Quote：supplier + RFQ + quote version + validity window。
- BOM：product specification version + BOM version + effective scope。
- Sample：sample ID + facility + sample type + specification/BOM version。
- Production Batch：facility + work order/batch number + production window。
- Inspection Lot：batch set + sampling plan + inspection event。
- Decision：decision type + object ID + decision version。

模糊匹配只建立 `candidate_link`。主体、工厂、批次或报告合并必须保存匹配证据、置信度、冲突和人工/owner 接受。

## 供应网络图

节点至少包括签约方、收款方、开票方、工厂、分包商、关键材料源、模具、关键设备、实验室和物流交接方；边记录控制、制造、供货、付款、检验、共享和替代关系。

冗余按真实故障域判断：

- 两个品牌名共享工厂：工厂层单点；
- 两个工厂共享关键材料：材料层单点；
- 不同地区共享专用模具：模具层单点；
- 多供应商共享实际控制人：治理层相关；
- 备供未经验证：不是可用冗余。

## 变更影响闭包

Engineering Change 必须列出：

1. 旧/新对象与版本；
2. 变更原因和提出者；
3. 受影响的规格、BOM、样品、工艺、批次和报告；
4. 安全、性能、合规、成本、交期、库存与客户影响；
5. 重新打样、首件、试产、可靠性和准入范围；
6. 各 owner 的接受、拒绝或部分接受；
7. 旧批最后允许点、新批生效点和防混批；
8. 回滚对象、窗口、现实动作和处置责任。

## 职责分离

商务谈判、工程确认、检验执行、质量放行、偏差批准和付款执行应分离。下列情况必须拒绝：

- 采购负责人单独批准自己谈判批次的质量让步；
- 供应商或利益关联方作为唯一验收者；
- 非 D04 owner 改写放行结论；
- 同一人既修改原始读数又批准报告；
- 以紧急为由取消证据、追溯或事后复核。
