# D04 SPPQ 建设说明

状态：`next_build`

运行时可用性：不可用，必须 fail closed

目标域：Supplier, Procurement, Production & Quality Decision

## 目的

D04 将承接供应商选择、采购承诺、样品批准、生产放行、批次质量放行及供应商恢复/退出
主权。当前文件只定义建设边界，不是 Skill 入口、实现骨架或部分可用声明。

## 当前禁止事项

- 不得把本文件注册为可调用 Skill。
- 不得用 PIPM、LIFD、PPFC 或 ERDG 代替 D04 作供应商、下单、量产或质量放行。
- 不得把临时 handoff、Schema 存在或合成 fixture 写成 D04 已实现。
- D04 结论缺失时，相关动作保持 `blocked` 或 `inconclusive`。

## 建设前置条件

1. 固定主权、对象、版本、货权、责任主体和外部写入边界。
2. 定义 D03规格、D05准入、D06经济、D07物流与D13质量结果的输入合同。
3. 建立供应商尽调、询报价、MOQ/产能、样品、生产、检验、偏差、CAPA、召回和退出模型。
4. 建立不可补偿红线、确定性计算、状态机、证据/计算/血缘合同和失败关闭。
5. 完成 Golden、反例、对抗、性质、容量、迁移、回滚及跨域消费者验收。
6. L1—L3通过后仍保持`controlled pilot`；L4只能由授权真实回放和独立复核关闭。

## 启用条件

只有当目录、Skill入口、注册表、ERDG适配、主权合同、测试、评测、安装、首页和
change-impact闭包同时完成，且发布校验器通过后，注册表才可从`next_build`变更为
`current`。任何单一文件或测试不得触发可用性升级。

## 当前机器边界

权威状态仍来自`governance/domain-architecture-registry.json`。运行时对D04执行请求必须
拒绝；相关测试必须持续证明planned/next_build域不能被错误执行。
