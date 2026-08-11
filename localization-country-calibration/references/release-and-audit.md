# 发布与审计

L1 检查结构、路由、注册和失败关闭；L2 检查 Schema、状态、转换、迁移、消费者和回滚；L3 检查 Golden、失败、对抗、极端、性质、跨域、突变和独立受控评审。L4 不使用合成案例关闭。

任何发布判断必须由 `scripts/validate_f02_release.py --require-l3` 复算。发布证据不授权外部写入，`production_ready` 恒为 false，真实市场结果和独立外部复核保持 L4。
