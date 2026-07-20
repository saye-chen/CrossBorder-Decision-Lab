# 异常、迁移与血缘

## 状态机

页面状态至少包括 draft、submitted、live、limited、suppressed、unavailable、retired；动作状态 proposed、approved、executing、partially_applied、verified、failed、rolled_back、closed。非法跃迁、无审批执行、部分成功写完成均阻断。

## 异常处理

建立 incident_id、对象/版本、开始时间、发现信号、影响范围、根因层、Gate、已成功/失败子动作、止损、重试/回滚、传播确认、剩余暴露、owner和关闭证据。区分页面覆盖、索引、图片错序、详情不渲染、变体断裂、Offer/库存不同步、权限/审核、API部分失败、站点延迟和平台事故。

恢复不等于提交成功；必须核验前台/后台、设备/站点、可购买性、索引、变体、Offer、库存和事件数据。超时后保持 `partially_applied` 或 `inconclusive`。

## 迁移与合并

分类可继承事实、需重验事实、禁止继承资产、待专业复核权利。不同产品不得为继承评论/流量非法合并。跨站/跨平台不继承当前规则、索引、评论资格和实验结论。

## 血缘与退出

页面、报告、证据、动作、实验和回滚形成有向无环图；同一对象仅一个current版本。回滚创建新事件，不能删除历史。退出冻结新增承诺，处理页面、素材权利、评论/QA、库存履约、客户责任和侵权监控，保存最终指纹与未解决责任。
