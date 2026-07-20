# 35项审计整改核销矩阵

> 口径：`fixed` 表示仓库实现与自动门已修复；`controlled external gate` 表示代码和验收器已完备，但真实授权数据不能由仓库伪造。行数只作异常信号，最终以语义与可执行测试为准。

| # | 状态 | 整改与证据 |
|---:|---|---|
| 1 | fixed | D09十个平台卡分别增加竞价/交付、优化反馈、归因差异、特有失败和反事实；`test_professional_depth.py`逐卡检查。 |
| 2 | fixed | D09增量、经济预算和九层诊断均增加文件名绑定的专属机制、公式/判定、失效和动作；独立门禁止用通用附录替代。 |
| 3 | fixed | CIG核心reference逐文件增加独有模型：Cohort右删失、ITT、状态迁移、NIV、VOC一致性、CLV等，不再只靠同一协议扩行。 |
| 4 | fixed | CIM逐文件增加独有基线、MAD阈值、三快照、代理边界、归因信号数和机会窗口判定。 |
| 5 | fixed | D07全部11个reference分别增加补货、路由、分配、仓容、逆向、追踪、CTS、事故等专属计算和失败动作。 |
| 6 | fixed | D08全部9个reference分别增加Gates、具体优化、实验、平台校准、事故迁移等专属内核；独立测试检查内核唯一性。 |
| 7 | fixed | D09 reference总量增至1133行并由语义门校验；均值不再作为唯一成熟度判断。 |
| 8 | fixed | D07四个标准治理文件齐备并由统一治理验证器检查。 |
| 9 | fixed | D08四个标准治理文件齐备并由统一治理验证器检查。 |
| 10 | fixed | D09补齐专业深度、集成、数据自动化和标准路径报告协议。 |
| 11 | fixed | CIDM补齐集成协议、数据合同和标准路径报告协议。 |
| 12 | fixed | VLB补齐集成、报告和数据自动化协议。 |
| 13 | fixed | 新增`governance/required-skill-governance.md`与`validate_governance_baseline.py`，定义四个必需模块、语义门和L1—L4成熟度。 |
| 14 | fixed | D07新增显式“跨域边界与双向数据交换”，覆盖CIDM/CIM/VLB/CIG/D08/D09。 |
| 15 | fixed | D08新增显式双向协议、结果卡、部分失败和禁止反向改写主权。 |
| 16 | fixed | D09新增独立跨域边界节并路由标准集成协议。 |
| 17 | fixed | CIG新增与CIDM/CIM/VLB/D07/D08/D09的统一双向协议。 |
| 18 | fixed | D07/D08新增同名“专业性与决策可用性硬约束”，保留原Gates作为域级实现。 |
| 19 | fixed | 七域统一显式“入口与交付层级”，均定义Card/Memo/Diligence。 |
| 20 | fixed | D09入口按渐进加载保持精炼，并新增十平台“交付机制—归因经济—首要失败”路由表；详细知识留在逐平台reference。 |
| 21 | fixed | D09四个数量脚本分别增至130/116/101/82行；增加风险预算、成熟/曝光/护栏、边际下界和订单成熟重述。 |
| 22 | fixed | D09 `test_models.py`增至12个正常/边界/失败测试，覆盖组上限、最低预算、风险、成熟、护栏、重复档位和负成本。 |
| 23 | fixed | CIG保留小型原子计算器并新增域级`evaluate_growth_decision.py`组合身份、授权、质量、因果成熟、NIV和不触达；两个测试套件覆盖正常与失败。 |
| 24 | fixed | CIM新增域级`evaluate_competitive_decision.py`和第二个独立测试文件，覆盖三快照、混对象、代理、反证、窗口关闭和部分失败。 |
| 25 | fixed | D09 5行委托器替换为域级校验器，在共享内核上增加四轴、成熟状态、三本账、数量动作、增量和Scale/Stop约束。 |
| 26 | fixed | 7份single-skill Golden分别加入本域独立原始输入、推理链和翻转条件，不再只共享同一评测附录。 |
| 27 | fixed | 新增10个语义不同的`cross-skill-executable-fixtures.json`场景，逐个给对象、数值输入、证据冲突、中间状态、计算和禁止结论。 |
| 28 | fixed | adversarial扩展至7类；其中5类新增可执行JSON fixture与校验器，逐项实际触发造假、越权、版本、数字血缘和部分失败Guard。 |
| 29 | controlled external gate | D07历史回放schema与校验器一致并实际阻断0<3；无授权真实cases，因此不得称L4关闭。 |
| 30 | controlled external gate | D08新增32行真实回放schema、三例门和禁止合成替代；未获授权真实案例，因此诚实保持controlled pilot。 |
| 31 | fixed | `.gitignore`补齐Python缓存、环境、构建、测试缓存、日志和临时文件。 |
| 32 | fixed | change-impact manifest新增七域治理、CIM、CIG和D08合同；共享decision-contract-core消费者补入D08，D09标准治理消费者闭包同步。 |
| 33 | fixed | D08升级为`D08-2026.07`并在SKILL/README/Goldens/测试同步；成熟度单独保持controlled pilot，不用版本号冒充production。 |
| 34 | fixed | D07知识层由11个操作协议实质补强，总reference达770行，与脚本广度建立对象/机制/约束/失败映射。 |
| 35 | fixed | D09版本不再单独作为成熟度证据；审计报告更正为L1/L2历史结果，内容、模型和独立深度门已同步补强。 |

## 验收命令

```text
python3 scripts/validate_governance_baseline.py
python3 scripts/test_professional_depth.py
python3 scripts/test_full_repository_audit.py
python3 scripts/validate_repo.py
```

## 唯一未能由代码关闭的外部条件

D08三个授权真实历史回放仍未提供。仓库已把输入schema、证据哈希、版本可比性、并发变化和独立复核要求固化；任何人试图用Golden或合成fixture替代都会失败。该项不影响L1—L3整改验收，但继续阻断L4 Production。
