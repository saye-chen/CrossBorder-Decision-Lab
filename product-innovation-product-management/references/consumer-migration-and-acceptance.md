# 消费者迁移、接受与回滚

## 1. 权威切换原则

D03产品事实必须依次经过：

```text
inventory
  → shadow
  → dual_read
  → automated_contract_accepted
  → independent_owner_accepted
  → authoritative
```

禁止跳级、倒签或由发送方代替消费者接受。自动合同通过不等于独立Owner接受；独立Owner接受也不自动证明L4 Production。任一阶段失败时保持`authoritative=false`，旧读继续有效。

## 2. 六阶段进入与退出条件

### inventory

进入：D03规范字段和候选消费者已识别。

必须完成：

- 列出每个消费者读取的旧字段、来源和重复逻辑；
- 标记required、optional、ignored和forbidden；
- 明确保留主权和禁止回写；
- 识别旧读路径、消费者测试和退休候选。

退出：消费者、字段、来源、测试和旧读库存完整。此阶段禁止发送新合同到业务执行路径。

### shadow

进入：inventory完整，adapter Schema和validator可运行。

允许：新合同只在影子路径读取同一对象快照并生成审计结果。

禁止：影响消费者结论、写回D03、触发外部动作或关闭旧读。

退出：规定样本范围内无Schema、对象、版本、单位、双时态或血缘错误；错误必须保留，不得从分母删除。

### dual_read

进入：shadow通过且双轨对象、期间和参数快照冻结。

旧读与新读必须使用同一`object_id`、`object_version`、业务有效时间、记录截止时间和允许用途。每个结果分类为equivalent、expected_change、error或incomparable。

退出：全部差异已分类，error为零，incomparable均阻断，expected_change均有Owner、原因、影响和接受条件。禁止用总体平均差异掩盖安全关键字段错误。

### automated_contract_accepted

进入：消费者本地adapter、validator和test实际运行。

最低测试：

- 有效消息接受；
- 缺少required字段阻断；
- forbidden字段和禁止回写阻断；
- 合同或对象版本错配阻断；
- 外部执行请求阻断；
- 部分失败保留未受影响结果；
- 旧读仍可用；
- acceptance绑定adapter和测试结果哈希。

退出：中央账本仅汇总消费者本域证据路径和哈希，不直接手写true。

### independent_owner_accepted

进入：自动接受通过，证据索引冻结。

消费者Owner必须复核字段语义、业务用途、禁止用途、主权、版本、部分失败、旧读和重接受触发，并留下身份、独立性、利益冲突、结论、发现、时间和证据哈希。

退出：所有required消费者完成签署；任何拒绝、P0/P1或证据漂移阻断。发送方、自评或自动测试不能代签。

### authoritative

进入：全部独立Owner接受、回滚演练通过、旧读关闭计划获批。

允许：D03规范产品事实成为约定字段的权威来源。

仍然禁止：越权替代消费者业务结论、外部写入或将L3签署解释成L4。

退出或撤回：对象/合同版本变化、关键证据撤回、消费者拒绝、漂移、事故或回滚触发时，退回dual_read或automated_contract_accepted，具体取决于影响范围。

## 3. 消费者adapter合同

每个消费者本域目录必须拥有：

```text
integrations/product-innovation-product-management/
  adapter.json
  acceptance.json
  validate_adapter.py
  test_adapter.py
```

adapter至少声明runtime、contract、adapter_version、required/optional/ignored/forbidden、field_mapping、mapping_classification、retained_sovereignty、forbidden_writeback、allowed_uses、forbidden_uses、blocked_actions、preserved_results、reaccept_triggers、legacy_reader和`external_write=false`。

对象、版本、国家平台、单位、双时态或血缘不一致时不得静默转换。安全关键、Claim、身份和版本字段必须lossless。

## 4. 接受状态机

消费者对每个消息只能返回：

- `accepted`：合同和用途均满足；
- `partially_accepted`：明确列出保留结果、失败字段和受阻动作；
- `rejected`：列出拒绝码和影响范围；
- `evidence_requested`：列出缺失证据及其Owner；
- `recompute_requested`：列出变化字段、参数快照和期望版本。

部分接受不得被中央账本改写为整体成功；一个消费者失败不得污染其他消费者已验证结果。

## 5. 双轨差异

### equivalent

对象、字段语义、单位、版本和结果相同，可继续。

### expected_change

新合同按批准规则产生差异。必须记录原因、Owner、影响、有效期、消费者接受和回滚条件。

### error

Schema、计算、路由、版本、单位、血缘或实现错误。必须阻断，不允许归入expected_change。

### incomparable

对象、期间、参数、版本或业务口径无法对齐。必须阻断并请求修正，禁止选择对迁移最有利的结果。

## 6. 重接受触发

以下变化必须使相关消费者接受过期：

- object_version、contract_version或adapter_version变化；
- evidence过期、撤回或等级变化；
- Claim文本、允许用途、国家、平台、语言或媒介变化；
- 规格、材料、包装、变体或生命周期变化；
- 字段映射、单位、双时态或主权变化；
- 消费者runtime升级或旧读关闭。

选择性重接受只作用于影响闭包内消费者；不得无理由污染未受影响消费者。

## 7. 回滚

回滚单元至少包括contract、routing、Schema、validator、catalog和evaluation。触发条件：

- 消费者拒绝或本域测试失败；
- 新旧结果出现error或未解释incomparable；
- adapter/acceptance哈希漂移；
- 旧读失败；
- 权威切换后出现关键事故、版本污染或主权越界。

回滚必须：

1. 停止新合同影响业务结论；
2. 恢复全部发布单元的冻结哈希；
3. 验证旧读可用；
4. 将新合同消息保留为只读审计证据；
5. 报告已执行动作的补偿和残余暴露；
6. 保持`external_write=false`。

RTO、RPO和切换窗口必须由实际运行Owner批准；没有真实运行数据时不得编造固定承诺。

## 8. 旧读退休

旧读只有在以下条件全部满足后才可关闭：

- 所有required消费者独立接受；
- 规定观察窗口无未解释差异；
- 回滚演练验证可恢复；
- 权威切换和退休计划获批；
- 没有待处理P0/P1；
- 关闭后仍保留历史重放能力。

关闭旧读是独立决策事件，不能因为代码中存在新adapter而自动发生。

## 9. 审计证据

迁移账本必须可复算地连接：

```text
source
→ consumer
→ adapter hash
→ local validator/test
→ dual-run result
→ acceptance hash
→ independent signoff
→ authoritative transition
→ rollback evidence
```

任何静态true、缺失本域测试、失效哈希或自我签署均不能关闭迁移门。
