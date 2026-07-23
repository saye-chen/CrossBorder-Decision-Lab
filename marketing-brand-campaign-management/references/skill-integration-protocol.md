# Skill联动协议

每个包必须显式声明`allowed_uses`（允许用途）与`forbidden_uses`（禁止用途）；缺失任一字段时不得执行下游动作。

## 交付包

`packet_id/packet_version/source_domain/source_runtime/target_domain/object/scope/question/original_conclusion/status/evidence/data_quality/calculations/constraints/uncertainty/allowed_uses/forbidden_uses/request/action/lineage`必填。状态为`validated/proposed/blocked/inconclusive/stale/conflicted/withdrawn/superseded`。

接收时核验来源运行时、对象/国家/版本/时间、状态、有效期、用途、新版/撤回和关键缺失。拒绝使用必须保留原结论和原因，不得改写。

## 双向主权

- CIDM→MBCM：资本边界；MBCM→CIDM：GTM和品牌投资候选。
- CIM→MBCM：竞争事实；MBCM→CIM：监控问题。
- LIFD↔MBCM：容量与需求情景/清仓路径。
- PLCO↔MBCM：页面承接与营销任务。
- AAMO↔MBCM：广告可行/边际与渠道方向。
- CAPM↔MBCM：达人商务可行包与渠道任务。
- VLB↔MBCM：内容机制与传播目标。
- CIG↔MBCM：客户证据/资格与市场级策略。
- D03—D06/D14/F01—F03使用共享合同桩，未安装标`unavailable`。

## 部分失败与冲突

参与域失败只撤回依赖该输入的主张；共同身份、法律、财务、容量或授权红线扩大阻断。超时不默认通过。对象/口径不可比先由所有者对齐，跨域经营取舍交D14，资本交CIDM。不得投票或平均置信度。

## 回写

回传使用/拒绝的包、MBCM新增判断、待确认动作、最终动作上限和实际结果应回给谁。上游撤回触发影响分析、暂停/回滚/保守运行和新决策版本。

## 幂等

同一`packet_id+packet_version+target_domain`重复接收不得生成重复动作。外部执行不属于本协议；只输出具名请求和待批准状态。
