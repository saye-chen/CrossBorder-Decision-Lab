# 第一次使用：从一个经营问题开始

这套项目适合需要复算和复核经营判断的运营、财务、采购与品牌团队。目前是受控试点。先用合成样例练习，再在获得授权的环境使用脱敏数据。数据接口当前为合同定义，尚未自动连接卖家后台。

## 1. 选择任务

| 你要解决什么 | 最少准备 | 第一份结果 |
|---|---|---|
| 广告有单但不赚钱 | 同币种、同核算窗的不重叠收入/成本与广告分摊记录，订单成熟状态 | 净收入、广告前后贡献、未成熟限制与复核动作 |
| 商品值不值得小预算测 | 售价、完整变动成本、费用率、样品/素材/测试固定费、CTR/CVR 情景 | 单位贡献、保本订单/点击/曝光；市场进入仍需证据与审批 |
| 现在补不补货、补多少 | 可售和可信在途、需求分位、现金/产能/仓容上限、完整排期 | 数量、库存缺口、可售日；需求概率与真实到货须另核实 |

详细字段、错误含义和原报表映射见[资料准备](input-and-privacy.md)。

## 2. 准备运行环境

保留完整仓库，使用 Python 3.12（与 CI 一致）。在仓库根目录执行：

```bash
python3 -m venv .venv/operator
source .venv/operator/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_python_environment.py
```

如果你通过助手使用，只需让助手检查上述依赖并运行对应入口，不需要自行处理命令。下面的命令供维护者和可复现操作使用。

需要让本地助手识别 Skill 时，用已配置的 Skill 根目录作为 `--root`。例如本项目维护规则约定的 Codex 根目录：

```bash
python3 scripts/install_skills.py --root "${CODEX_HOME:-$HOME/.codex}/skills"
python3 scripts/install_skills.py --root "${CODEX_HOME:-$HOME/.codex}/skills" --check
```

也可使用 QoderWork 根目录 `~/.qoderwork/skills` 或 `~/.qoderworkcn/skills`。通过 `--skill advertising-analysis-measurement-optimization` 只安装一个入口；整个仓库仍须保留。工具只创建缺失链接，遇到已有目录或错误链接会停止并报告冲突，不覆盖既有内容。读取 Skill 时先解析链接的实际位置，以便定位相邻治理目录。单独复制 Skill 文件夹不受支持。

## 3. 先运行合成样例

三个命令分别生成新目录；已经存在时请换版本名。输出目录不能在仓库内。

```bash
python3 scripts/run_starter.py ad-profit examples/starter/ad-profit.json --output-dir "$HOME/Downloads/CBDS-ad-demo-v1"
python3 scripts/run_starter.py product-test examples/starter/product-test.json --output-dir "$HOME/Downloads/CBDS-product-demo-v1"
python3 scripts/run_starter.py replenishment examples/starter/replenishment.json --output-dir "$HOME/Downloads/CBDS-stock-demo-v1"
```

每个目录都有 `decision-card.md`（先读这个）、`result.json`（完整计算与输入/代码指纹）及 `outcome.json`（后续回填）。样例是合成的，不是成功案例，不自动登记到真实回放。

可复算预期：广告例净收入 900、广告前贡献 400、广告后贡献 200 USD；测款例单位贡献 12.5 USD、覆盖 300 USD 固定投入需 24 单、480 次点击、24,000 次曝光；补货例建议情景数量 100 件、计算可售日 2026-09-18。数值来自样例假设，不是通用阈值或当前市场建议。

每种任务还有 `-missing.json` 和 `-invalid.json`。运行后会交付明确的补数/修正卡，返回码为 2；这是预期拒绝，不是安装失败。结果不会包含伪造的利润或数量。

## 4. 换成你的任务

将样例复制到仓库外，再填写经授权的真实数据。不要改动仓库样例。将 `source_class` 改为实际来源，例如 `authorized_first_party`；填写真实但已脱敏的对象标识、市场、币种、时点和来源引用。声明为授权来源不等于工具替你验证授权。

可以这样对助手说：

> 请使用广告分析和定价财务能力，核对我提供的同周期脱敏报表。先算能复算的利润，把缺数及其影响列出来；给我一页结论、前三项检查、下一步和停止条件，不自动修改店铺。

> 请评估这款商品的小预算测试方案。先核对单位经济与保本订单，区分市场证据和假设；说明什么变化会推翻建议，并给出损失上限的确认事项。

> 请用库存与履约能力核对这个 SKU 的库存、到货和需求，比较不补货与补货情景，给出数量、时间、约束、替代方案以及需要采购和财务确认的地方。

脚本准备的是计算输入和结果，不替代这些 Skill 的竞争、准入、供货、因果或审批判断。

## 5. 确认动作、保存版本、回填

先由对应实际岗位复核，确认对象、幅度、期限、依赖及停止条件后再人工执行。把实际动作与结果填入输出的 `outcome.json`，包括未执行、失败或尚未成熟。填写前保留原文件副本；敏感源文件与案例输出始终留在授权环境，不回传仓库。

参数变化时创建新版本，并引用旧结果：

```bash
python3 scripts/run_starter.py ad-profit /absolute/path/to/revised-input.json --previous "$HOME/Downloads/CBDS-ad-demo-v1/result.json" --output-dir "$HOME/Downloads/CBDS-ad-demo-v2"
```

同一案例的新版本记录旧结果指纹，不覆盖历史；不同案例不能接成同一版本链。结果对比与非作者测试见[真实回放与使用评测](pilot-evaluation.md)。

## 常见问题

- 找不到依赖：确认已激活本项目环境，并在同一环境安装锁定依赖。
- 找不到治理文件：保留完整仓库；核对 Skill 链接实际指向，不单独复制子目录。
- 计算结果为“资料不足”：按卡片列出的字段补数；只有已确认没有发生的金额才能填 0。
- 输出存在：换用 v2 等新目录，不删除原结果。
- 没有确定性 Go/No-Go：本工具不批准业务决策；按主 Skill 的缺口清单补证。
- 需要高级因果后端：依 ECAE 后端资格和锁定环境处理；此快速入口没有安装或激活所有高级后端。

## 使用授权

本仓库保留现有 [LICENSE](../LICENSE)，本教程不新增复制或商业使用许可。外部试用者请通过 README 中的邮箱联系版权所有者，说明主体、用途、使用范围与是否涉及商业服务；先获得所需书面许可。不要在咨询中附带客户身份、凭证或未授权财务资料。
