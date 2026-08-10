# 十三域专业工程发布口径

权威范围：D01—D13 当前域。D14 为规划域，不在本发布门内，也不因本门通过而解冻。

## 1. 两类结论必须分开

| 结论 | 证明对象 | 权威入口 | 当前含义 |
|---|---|---|---|
| `controlled_pilot_engineering_ready` | L1—L3 的结构、专业机制、确定性计算、语义评测、跨域主权、连续状态、异常恢复与防篡改能力 | `scripts/validate_release_integrity.py` | 可以进行受控试点和继续仓库建设 |
| `L4 external assurance` | 授权真实案例、成熟经营结果、阈值与权重校准、独立责任人复核、适格专业签章 | 各域历史回放与独立复核合同 | 未通过；不得声称 production-ready |

工程门通过不能推出真实经营有效、法律或税务意见、生产成熟度、外部写入许可或 D14 开发授权。L4 未通过也不能被写成当前 L1—L3 工程失败。

## 2. 权威证据链

1. `governance/domain-architecture-registry.json` 决定当前域身份、主权和可用性。
2. `governance/professional-evaluation-registry.json` 为十三域评测的人工可读登记表。
3. `governance/professional-evaluation-case.schema.json` 定义统一案例字段。
4. `evaluations/professional-evaluation-index.json` 绑定每个源案例和 Golden 的 SHA-256 指纹。
5. `scripts/validate_professional_evaluation_registry.py` 验证 13 域、案例完整性、证据—主张—根因—动作关系、计算入口、主权和回滚。
6. `governance/release-mutation-contract.json` 与 `scripts/test_release_anti_cheat.py` 证明关键防线被删除或放宽时测试会失败。
7. `scripts/validate_release_integrity.py` 执行所有登记的专业和数值验证入口，计算最终工程就绪状态。

兼容路径、手填状态、Golden 文本、合成 fixture、测试数量和总分都不能单独成为权威完成证据。源目录发生变化后必须重建规范化索引，再运行总发布门；哈希不一致即失败。

当前规范化快照包含 13 域 790 个源案例、29 个去重后的专业验证入口和 12 类防篡改突变。数量只用于描述覆盖面，发布结论仍由上述权威证据链逐项计算。

## 3. D05 特别口径

`legal-tax-intellectual-property-market-access-decision/scripts/validate_completion_readiness.py` 从固定的必跑验证器和实际外部证据计算结果。它可以返回 D05 工程就绪，同时继续报告以下外部门未关闭：独立消费者 Owner 接受、适格专业签章、授权真实回放和 L4。

这一区分不降低 D05 的安全上限：D05 只签发商业 Gate、证据缺口、动作上限、Claim 使用边界和专业复核请求，不签发法律、税务、FTO、认证或实验室意见。

## 4. F01 共享底座发布口径

F01 不计入 D01—D13 业务域数量，其身份与成熟度由 `governance/foundation-capability-registry.json` 管理。`scripts/validate_f01_release.py --require-l3` 是 F01 L1—L3 的权威发布门；当前状态为 `current / controlled_pilot`，L1—L3 已关闭，非 L4 阻塞项为零。

F01 的受控试点接受只覆盖 D01—D13 合同明确列出的非生产、非高风险用途。生产快照与双跑、真实结果回放和校准、高级科学后端外部资格、非实现者独立复核均属于 L4。L4 未关闭时，生产决策、自动执行和外部写入必须保持不可用；公开方法来源、合成案例、只读预检或 Owner 授权技术复核不得被提升为生产证据。
