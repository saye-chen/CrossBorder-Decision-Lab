# 数据合同与自动化

## 对象、字段与缺失

所有机器合同至少绑定`object_id`、`object_version`、`as_of_time`、`recorded_at`、scope、runtime、input_hash和external_write。金额、数量、重量、尺寸、比例和时间必须带单位、币种、时区或口径。

允许的缺失语义为`missing`、`unavailable`、`not_applicable`、`not_yet_observed`、`withheld`、`invalid`和`observed_zero`。只有`observed_zero`可参与零值计算；其他状态必须阻断、降级或请求证据。

## 精度、双时态与幂等

数值使用十进制字符串，禁止二进制浮点进入权威计算。单位换算保留原值、原单位、目标值、目标单位、规则版本和来源。

`as_of_time`表示业务有效时间，`recorded_at`表示系统获知时间。迟到事件追加到历史，不能回写过去。对象、参数、合同和运行时版本分别记录。

相同idempotency_key和输入哈希返回同一结果；相同key、不同输入阻断。批量输入按对象和版本去重，禁止重复累计。

## 血缘、权限、外部写入与失败

报告可追溯到输入、证据、Claim、计算、跨域回执、决策、动作和消费者接受。Golden必须记录案例自有fixture、专业引擎、实际输出、mutation输出和哈希。

自动化只做读取、计算、验证和受控文件产物。`external_write`必须为false；真实平台、供应商、客户、广告、库存或资金动作需要主权域和显式授权。

Schema错误、版本错配、过期证据、未知单位、缺失关键字段、哈希漂移、循环依赖、消费者拒绝和工具部分失败均fail closed。未受影响节点可保留，但必须报告残余暴露。
