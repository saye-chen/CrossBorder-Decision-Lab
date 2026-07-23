# Repository Rules

Maintenance conventions for this repository. This file is not loaded automatically when a Skill runs. Put every runtime-critical rule in the relevant `SKILL.md`.

## 0. System-Wide Professionalism and Decision Sovereignty

Every Skill must remain decision-usable when invoked alone or jointly, across rapid answers, full reports, demos, missing data, tool failure, repeated follow-ups, and extreme scenarios. Compression may shorten presentation, not research. Degradation may lower confidence or action scope, but it may not remove the object boundary, evidence and assumptions, counterevidence, commercial constraints, risks, actions, success and stop conditions, or the decision impact of missing data.

Decision sovereignty is fixed: CIDM owns category investment, capital allocation, and final Go/No-Go; CIM owns external competitive facts, confirmed changes, and competitive attribution; VLB owns content observations, mechanisms, and transferability; CIG owns authorized customer evidence, customer state, and incremental validity; AAMO owns advertising architecture, internal budgets/bids, diagnosis, measurement, scaling, and stopping; LIFD owns logistics networks, routing, replenishment, inventory allocation, fulfillment capacity, reverse flow, incidents, and overseas-inventory disposition; PLCO owns platform, store, Listing, title, image, detail, landing-page, and conversion decisions; CAPM owns creator/affiliate diligence, commercial structures, use-specific content-rights evidence and ledgers, reconciliation, partner portfolios, renewal, and exit; MBCM owns market-level segmentation, positioning, brand architecture, GTM, Offer mechanisms, marketing campaigns, cross-channel roles, approved resource direction, brand health and marketing incident recovery. MBCM does not own capital entry, final pricing/cash, replenishment, listing edits, ad bids, creator contracts, creative production, customer-level contact or cross-domain operating posture. CAPM and MBCM do not replace qualified judgment on legal validity, tax, intellectual property, privacy or regulation. A non-owning Skill may submit a structured proposal but may not directly rewrite an owner's conclusion, score, threshold, or historical report.

Calculations that can change an investment conclusion must be deterministic. Cross-Skill adjustments follow `proposed → validated/rejected` and become effective only after the owning Skill accepts them and recomputes under its own model. Any threshold crossing requires two independent evidence fingerprints, direct target-object evidence, complete calculations, no unresolved redline, and an owner recomputation; a disclaimer cannot waive these gates.

## 1. Source of Truth

Treat this repository as the single source of truth for Skill changes. Edit here first. The local Codex installation should point to these directories with symlinks.

## 2. Skill Structure

```text
skill-name/
|-- SKILL.md          # Required Skill definition
|-- agents/           # Optional Codex UI metadata
|   `-- openai.yaml
|-- scripts/          # Optional deterministic helpers
|-- references/       # Optional supporting documentation
`-- assets/           # Optional reusable output assets
```

Keep runtime instructions inside the Skill. Do not add per-Skill README, changelog, installation guide, or other auxiliary documentation.

## 2b. Versioning

Skill frontmatter must contain only `name` and `description`, as required by the Codex Skill format. Put the runtime/model version in the `SKILL.md` body and validate it with `scripts/validate_repo.py`. Follow semantic versioning for package releases and date-based identifiers for runtime models:

- **Patch** (1.0.0 → 1.0.1): typo fixes, reference file corrections, no behavioral change.
- **Minor** (1.0.0 → 1.1.0): new scenario, new reference file, new script, or behavioral refinement that does not break existing workflows.
- **Major** (1.0.0 → 2.0.0): breaking change to scoring model, decision tiers, output structure, or input schema that would invalidate comparison with prior reports.

When bumping a major version, note the change in the commit message. Old report scores from different model versions must not be directly compared unless recalculated.

Before changing a scoring model, output contract, validator, cross-domain rule, runtime version or professional protocol, run `python3 scripts/analyze_change_impact.py <changed-paths>`. The machine-readable source of truth is `governance/change-impact-manifest.json`; every contract must map its owner, sources, consumers, validators, tests and evaluations. Unmapped contract changes block release until the manifest is updated.

## 3. Source File Safety

- Treat user-provided files as read-only. Do not overwrite, rename, move, delete, or modify their metadata.
- Transform or analyze copies only when needed.
- Never store user data, downloaded pages, reports, or task output inside a Skill directory.

## 4. Temporary Workspaces

Create intermediate files only when the task needs them. Use one of these two modes and document the selected mode in the relevant `SKILL.md`.

### Managed mode

Use for complex, resumable, or multi-step tasks.

- Store work under `${TMPDIR:-/tmp}/<skill-name>/<YYYYMMDD-HHMMSS>-<task-slug>/`.
- Add `.task-owner.json` with the Skill name, task ID, and creation time.
- On resume, clean only directories whose marker matches the known task ID.
- Delete the task directory at completion and verify that it no longer exists.

### Ephemeral mode

Use for short, single-run tasks such as video download and frame extraction.

- Create a unique directory with `mktemp` under `${TMPDIR:-/tmp}`.
- Retain the exact path in a task-local variable and delete only that path.
- Delete the directory at completion and verify that it no longer exists.
- Do not use broad cleanup commands or guess ownership during recovery.

In both modes, report the exact remaining path and reason if cleanup fails.

## 5. Final Deliverables

- Save final deliverables to `$HOME/Downloads` unless the user specifies another directory.
- Use `<Country>_<Platform>_<CategoryOrObject>_<Scenario>_<YYYY-MM-DD>.<ext>` when the active Skill defines no more specific naming rule.
- Replace unsafe filename characters with hyphens and keep the extension intact.
- Before writing, ask the user how to handle an existing file: overwrite, version, or rename. Never choose automatically.
- Return a clickable absolute path for every delivered local file.

## 6. Local Codex Installation

Use symlinks so repository edits take effect immediately:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"

ln -sfn "$PWD/category-investment-decision" \
  "${CODEX_HOME:-$HOME/.codex}/skills/category-investment-decision"

ln -sfn "$PWD/video-link-breakdown" \
  "${CODEX_HOME:-$HOME/.codex}/skills/video-link-breakdown"

ln -sfn "$PWD/competitive-intelligence-monitoring" \
  "${CODEX_HOME:-$HOME/.codex}/skills/competitive-intelligence-monitoring"

ln -sfn "$PWD/consumer-insights-customer-growth" \
  "${CODEX_HOME:-$HOME/.codex}/skills/consumer-insights-customer-growth"

ln -sfn "$PWD/advertising-analysis-measurement-optimization" \
  "${CODEX_HOME:-$HOME/.codex}/skills/advertising-analysis-measurement-optimization"

ln -sfn "$PWD/logistics-inventory-fulfillment-decision" \
  "${CODEX_HOME:-$HOME/.codex}/skills/logistics-inventory-fulfillment-decision"

ln -sfn "$PWD/platform-store-listing-conversion" \
  "${CODEX_HOME:-$HOME/.codex}/skills/platform-store-listing-conversion"

ln -sfn "$PWD/creator-affiliate-partnership-management" \
  "${CODEX_HOME:-$HOME/.codex}/skills/creator-affiliate-partnership-management"

ln -sfn "$PWD/marketing-brand-campaign-management" \
  "${CODEX_HOME:-$HOME/.codex}/skills/marketing-brand-campaign-management"
```

Do not use `cp -r` as an update mechanism; existing destinations can retain stale files or produce nested directories.

## 7. Validation

After modifying a Skill, run validation for **every changed Skill** (not just the one you were editing):

```bash
# Validate all skills in the repo (generic — works as skills are added/removed)
for skill_dir in */; do
  [ -f "$skill_dir/SKILL.md" ] || continue
  python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" "${skill_dir%/}"
done

# Install the locked validator dependency, then run the authoritative gate.
# The full audit discovers every */scripts/test_*.py and every root test_*.py,
# excluding itself, and also runs repository and governance validators.
python3 -m pip install -r requirements-dev.txt
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_full_repository_audit.py

git diff --check
git status --short
```

> **Note:** `quick_validate.py` is provided by the Codex/QoderWork runtime at `${CODEX_HOME}/skills/.system/skill-creator/`. It is not part of this repository. If the script is missing, check that your local Codex installation is up to date.

Also verify that:

- every local link from `SKILL.md` resolves;
- `agents/openai.yaml` still represents the Skill accurately;
- README file inventories match the repository (update README if files were added, removed, or renamed);
- no caches, downloads, screenshots, or test artifacts remain.

## 8. Git Workflow

Review the exact changed files before staging. Do not use broad staging when unrelated user changes are present.

```bash
git add <changed-files>
git commit -m "Describe the Skill change"
git push origin main
```

## 9. Adding a Skill

1. Use `skill-creator` to initialize and validate the Skill.
2. Keep the Skill self-contained and add only required resources.
3. Add `agents/openai.yaml` with accurate UI metadata.
4. Add the Skill to both language sections of `README.md` (description + file inventory table).
5. Add its symlink command to section 6 and any Skill-specific validation/test command to section 7.
6. If the new Skill references or integrates with an existing Skill, document the relationship in section 10.

## 10. Cross-Skill Dependencies

Skills in this repository are **independent and self-contained by default**. Do not design implicit data flows or call chains between Skills unless explicitly documented here.

### Current relationships

**video-link-breakdown → category-investment-decision (optional, unidirectional)**

When the user provides a CIDM report or explicitly requests it, `video-link-breakdown` can:
- **Read** CIDM's "content propagation" dimension score, wedge, and weakest assumption as analysis input.
- **Write back** video analysis conclusions to CIDM dimensions:
  - Product-video fit and replication evidence → CIDM "content propagation"
  - Unit economics and creator/material cost → CIDM "profit margin"
  - Product/content compliance quick-screen → CIDM "risk controllability"
  - New video evidence → CIDM wedge, validation plan or opportunity window

Rules: integration is opt-in, never auto-triggered; video analysis conclusions take priority over CIDM optimism; write-backs are "suggested adjustments" for the user to accept or reject.

**category-investment-decision → video-link-breakdown (optional, user-confirmed).** When content propagation is a key weakness or weakest assumption and the user supplies a video or requests tactic validation, CIDM may suggest the video Skill. It may consume the output only when the user explicitly requests integration. Write-back must record the original CIDM version/date, affected dimension, original and suggested score, reason, evidence/assumption IDs, and whether a gate must be reassessed. Never silently overwrite a historical report.

**competitive-intelligence-monitoring ↔ category-investment-decision (optional, user-confirmed).** CIM may consume CIDM's target market, own SKU, initial competitor links, wedge, gates, and weakest assumptions to initialize a monitored competitor pool. CIM sends confirmed intelligence event cards back when a new entrant, concentration shift, sustained price move, VOC gap, or competitive change may affect entry, scaling, or exit. CIDM owns gate and score reassessment. Both sides retain model version, event/evidence IDs, original conclusion, suggested adjustment, confidence, and gate impact; neither silently overwrites history.

**competitive-intelligence-monitoring ↔ video-link-breakdown (optional, user-confirmed).** CIM routes a confirmed creative or advertising change, before/after snapshots, product identity, and associated performance signals to VLB. VLB returns observed content mechanisms, transferability, test hypotheses, and stop conditions. CIM owns timeline and competitive-impact tracking; VLB owns video-level analysis. A creative score is not proof of sales or competitive advantage.

**consumer-insights-customer-growth ↔ category-investment-decision (optional, user-confirmed).** CIDM provides market, product, audience, wedge, repeat-purchase, and LTV hypotheses. CIG returns authorized customer evidence, retention, returns, contribution-profit CLV, and hypothesis/experiment results. CIDM owns capital decisions; CIG owns customer evidence and incremental-effect validity. Write-back retains both model versions, data date, original conclusion/score, evidence or experiment IDs, suggested adjustment, confidence interval, and gate impact.

**consumer-insights-customer-growth ↔ competitive-intelligence-monitoring (optional, user-confirmed).** CIM provides external competitor feedback, service, price, creative, and opportunity-window events. CIG tests whether the same issue appears among authorized first-party customers and quantifies affected segments, lifecycle states, and economic outcomes. CIM owns external change; CIG owns internal customer impact. Do not person-match public competitor audiences to first-party customers.

**consumer-insights-customer-growth ↔ video-link-breakdown (optional, user-confirmed).** CIG provides de-identified audiences, lifecycle states, jobs, frictions, language, and content hypotheses. VLB returns content mechanisms, transferability, production plans, and test variants. VLB owns content analysis; only CIG experiments or credible quasi-experiments may claim incremental retention or profit. No historical report is silently overwritten and neither Skill executes contact automatically.

**advertising-analysis-measurement-optimization ↔ category-investment-decision (optional, user-confirmed).** AAMO returns advertising feasibility, measured CAC range, mature marginal profit, budget capacity, scaling and stop signals. CIDM alone owns category entry and capital-allocation decisions; advertising efficiency cannot silently change an investment conclusion.

**advertising-analysis-measurement-optimization ↔ competitive-intelligence-monitoring (optional, user-confirmed).** CIM supplies confirmed competitor advertising events and snapshots; AAMO tests their relevance to the user's advertising system and owns only advertising actions. A competitor signal is neither a verified auction mechanism nor proof that copying it will work.

**advertising-analysis-measurement-optimization ↔ video-link-breakdown (optional, user-confirmed).** VLB supplies observed content mechanisms, transferability and creative test variants; AAMO owns paid delivery, advertising-internal budget and scaling. Paid performance does not prove a content mechanism, and a strong video score does not authorize budget.

**advertising-analysis-measurement-optimization ↔ consumer-insights-customer-growth (optional, user-confirmed).** CIG supplies authorized customer value, lifecycle and credible incrementality evidence; AAMO supplies exposure, cost and platform-attributed outcomes. AAMO does not execute customer contact, and platform attribution cannot replace CIG's causal standard.

**logistics-inventory-fulfillment-decision ↔ all business-domain Skills (optional, user-confirmed).** LIFD owns logistics networks, routes, replenishment, inventory allocation, fulfillment capacity, reverse logistics, incidents, and overseas-inventory disposition. It accepts supply constraints from D04, compliance gates from D05, cash/profit constraints from D06, channel plans from PLCO, demand scenarios from AAMO/D12, and returns/experience evidence from D13; it returns structured `proposed` capacity, inventory, route, recovery, and stop signals. It never changes capital, procurement, legal, price, advertising, listing, promotion, or customer-action conclusions directly.

**creator-affiliate-partnership-management ↔ CIDM/CIM/VLB/CIG/AAMO/LIFD/PLCO (optional, user-confirmed).** CAPM owns creator/affiliate diligence, commercial structures, commissions, delivery acceptance, content-use rights, affiliate reconciliation, partner portfolios, renewal and exit. It may receive capital boundaries from CIDM, competitive events from CIM, content mechanisms from VLB, de-identified customer evidence from CIG, paid-measurement results from AAMO, fulfillment capacity from LIFD and page breakpoints from PLCO. CAPM only sends versioned `proposed` business/rights/partner messages; each receiving Skill retains its own sovereignty. CAPM must still produce a bounded standalone result when any participant is unavailable, and only AAMO may activate paid media decisions.

### Rules for new cross-skill references

- The integrating Skill must contain the reference in its own `SKILL.md`; the referenced Skill does not need to know about its caller.
- Cross-skill references must be **optional** — each Skill must function correctly without the other.
- Document every cross-skill reference in this section, including direction (one-way / mutual), trigger condition (user-initiated / automatic), and data flow (what is read / written back).

## 11. Deprecating or Removing a Skill

1. Update this file: remove the Skill's symlink command from section 6, test command from section 7, and cross-skill references from section 10.
2. Update `README.md`: remove the Skill's entry from both language sections.
3. Remove the symlink in `${CODEX_HOME}/skills/`: `rm "${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>"`.
4. Commit the removal with a clear message explaining why.
5. Keep the directory in the repo for one commit cycle if other Skills or external workflows may still reference it; then delete.

---

# 仓库规则

本文件用于维护本仓库，不会在 Skill 执行时自动加载。所有运行时必须遵守的规则都应写入对应的 `SKILL.md`。

## 0. 系统级专业性与决策主权

所有 Skill 在单独调用、任意联合调用、快速交付、完整报告、demo、压测、缺数据、工具失败和极端场景下，都必须保持本域专业研究和决策可用性。压缩只作用于展示，不作用于研究；降级只作用于结论强度，不得删除对象边界、证据与假设、反例、商业约束、风险、动作、成功/停止条件和缺失数据影响。

决策主权固定为：CIDM 拥有品类投资、资本配置和最终 Go/No-Go 主权；CIM 拥有外部竞争事实、变化确认与竞争归因主权；VLB 拥有视频观察、内容机制与迁移性主权；CIG 拥有授权客户证据、客户状态与增量有效性主权；AAMO 拥有广告架构、广告内部预算/出价、广告诊断/测量和放量/停投主权；LIFD 拥有物流网络、路线、补货、库存配置、履约能力、逆向、异常恢复和海外库存处置主权；PLCO 拥有平台、店铺、Listing、标题、图片、详情、落地页和转化承接主权；CAPM 拥有达人/联盟尽调、商务结构、用途级内容权利证据与台账、联盟对账、伙伴组合、续约和退出主权。CAPM 不替代适格主体对合同法律效力、税务、知识产权或监管合规的最终判断。非主权 Skill 只能提交结构化建议，不得直接改变主权 Skill 的正式结论、评分、门槛或历史报告。

所有会改变投资结论的计算使用确定性脚本；跨 Skill 调整使用 `proposed → validated/rejected` 状态，只有主权 Skill 接受并按原模型重算后才能生效。任何跨档位变化必须有两个独立证据指纹、目标对象直接证据、完整计算、无未解决红线和主权 Skill重算。违反任一条件即阻断交付，不允许用自然语言免责声明绕过。

## 1. 唯一真实来源

将本仓库作为 Skill 变更的唯一真实来源。先在这里修改；本地 Codex 安装目录通过软链接指向本仓库。

## 2. Skill 目录结构

```text
skill-name/
|-- SKILL.md          # 必需：Skill 定义
|-- agents/           # 可选：Codex 界面元数据
|   `-- openai.yaml
|-- scripts/          # 可选：确定性辅助脚本
|-- references/       # 可选：支持文档
`-- assets/           # 可选：可复用交付资产
```

运行规则写入 Skill 本身。不要在单个 Skill 内添加 README、更新日志、安装指南等辅助文档。

## 2b. 版本管理

Skill 前置元数据必须按 Codex Skill 格式只包含 `name` 和 `description`。运行时/模型版本写在 `SKILL.md` 正文中，并由 `scripts/validate_repo.py` 强制校验。发布版本遵循语义化版本，运行时模型使用日期型标识：

- **补丁版本**（1.0.0 → 1.0.1）：修正错别字、参考文件勘误，无行为变更。
- **次版本**（1.0.0 → 1.1.0）：新增场景、参考文件、脚本，或不破坏现有工作流的行为调整。
- **主版本**（1.0.0 → 2.0.0）：评分模型、决策档位、输出结构或输入格式的破坏性变更，导致旧报告分数不可直接比较。

主版本升级时需在 commit message 中注明变更。不同模型版本的报告分数不可直接对比，除非按同一版本重算。

修改评分模型、输出合同、校验器、跨域规则、运行时版本或专业协议前，运行 `python3 scripts/analyze_change_impact.py <变更路径>`。机器可读的唯一来源为 `governance/change-impact-manifest.json`；每个合同必须映射 owner、权威来源、消费者、校验器、测试和评估。合同类变更未映射时阻断发布，先更新影响清单。

## 3. 源文件安全

- 将用户提供的文件视为只读，不覆盖、重命名、移动、删除或修改元数据。
- 只有任务需要时才使用副本进行转换或分析。
- 不把用户数据、下载页面、业务报告或任务交付物存入 Skill 目录。

## 4. 临时工作目录

只有任务需要中间文件时才创建临时目录。每个 Skill 在 `SKILL.md` 中明确使用以下哪一种模式。

### 受管模式

适用于复杂、可恢复或多步骤任务。

- 路径使用 `${TMPDIR:-/tmp}/<skill-name>/<YYYYMMDD-HHMMSS>-<task-slug>/`。
- 创建 `.task-owner.json`，记录 Skill 名称、任务 ID 和创建时间。
- 恢复任务时，只清理标记与已知任务 ID 完全匹配的目录。
- 完成后删除任务目录，并验证目录不再存在。

### 短生命周期模式

适用于视频下载、抽帧等单次短任务。

- 使用 `mktemp` 在 `${TMPDIR:-/tmp}` 下创建唯一目录。
- 在当前任务变量中保存精确路径，只删除该路径。
- 完成后删除目录，并验证目录不再存在。
- 禁止宽泛清理；恢复时无法确认归属的目录不得删除。

两种模式下，若清理失败，都必须报告准确的残留路径和原因。

## 5. 最终交付物

- 用户未指定目录时，保存到 `$HOME/Downloads`。
- 当前 Skill 没有更具体规则时，使用 `<国家>_<平台>_<品类或对象>_<场景>_<YYYY-MM-DD>.<扩展名>`。
- 将不安全字符替换为连字符，并保持扩展名完整。
- 写入前检查同名文件；必须让用户选择覆盖、版本号或改名，不得擅自决定。
- 最终回复提供可点击的绝对路径。

## 6. 本地 Codex 安装

统一使用软链接，让仓库修改即时生效：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"

ln -sfn "$PWD/category-investment-decision" \
  "${CODEX_HOME:-$HOME/.codex}/skills/category-investment-decision"

ln -sfn "$PWD/video-link-breakdown" \
  "${CODEX_HOME:-$HOME/.codex}/skills/video-link-breakdown"

ln -sfn "$PWD/competitive-intelligence-monitoring" \
  "${CODEX_HOME:-$HOME/.codex}/skills/competitive-intelligence-monitoring"

ln -sfn "$PWD/consumer-insights-customer-growth" \
  "${CODEX_HOME:-$HOME/.codex}/skills/consumer-insights-customer-growth"

ln -sfn "$PWD/advertising-analysis-measurement-optimization" \
  "${CODEX_HOME:-$HOME/.codex}/skills/advertising-analysis-measurement-optimization"

ln -sfn "$PWD/logistics-inventory-fulfillment-decision" \
  "${CODEX_HOME:-$HOME/.codex}/skills/logistics-inventory-fulfillment-decision"

ln -sfn "$PWD/platform-store-listing-conversion" \
  "${CODEX_HOME:-$HOME/.codex}/skills/platform-store-listing-conversion"

ln -sfn "$PWD/creator-affiliate-partnership-management" \
  "${CODEX_HOME:-$HOME/.codex}/skills/creator-affiliate-partnership-management"
```

不要使用 `cp -r` 更新 Skill；目标已存在时可能保留旧文件或产生嵌套目录。

## 7. 校验

每次修改 Skill 后，对**所有变更的 Skill** 运行校验（不仅限于你正在编辑的那个）：

```bash
# 通用校验：遍历仓库中所有含 SKILL.md 的子目录
for skill_dir in */; do
  [ -f "$skill_dir/SKILL.md" ] || continue
  python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" "${skill_dir%/}"
done

# 安装锁定的校验依赖，再运行唯一权威发布门。
# 全仓审计会自动发现每个 */scripts/test_*.py 和根目录 scripts/test_*.py
#（排除自身），并执行仓库与治理校验器，避免新增 Skill 后漏列测试。
python3 -m pip install -r requirements-dev.txt
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_full_repository_audit.py

git diff --check
git status --short
```

> **说明：** `quick_validate.py` 由 Codex/QoderWork 运行时提供，位于 `${CODEX_HOME}/skills/.system/skill-creator/`，不属于本仓库。如脚本缺失，请检查本地 Codex 安装是否完整。

同时检查：

- `SKILL.md` 中的本地链接全部存在；
- `agents/openai.yaml` 与 Skill 实际能力一致；
- README 文件清单与仓库一致（新增、删除或重命名文件后必须同步更新 README）；
- 没有残留缓存、下载文件、截图或测试产物。

## 8. Git 工作流

暂存前检查具体变更文件。存在无关用户改动时，不使用宽泛暂存命令。

```bash
git add <变更文件>
git commit -m "说明 Skill 变更"
git push origin main
```

## 9. 新增 Skill

1. 使用 `skill-creator` 初始化并校验 Skill。
2. 保持 Skill 自包含，只添加必要资源。
3. 添加与能力一致的 `agents/openai.yaml`。
4. 在 `README.md` 中英文部分都登记该 Skill（描述 + 文件清单表）。
5. 在本文件第 6 节加入软链接命令，第 7 节加入该 Skill 专属的校验/测试命令。
6. 若新 Skill 引用或对接了已有 Skill，在第 10 节记录该关系。

## 10. 跨 Skill 依赖

本仓库的 Skill 默认**独立自包含**。不要设计隐式数据流或调用链，除非在此处显式记录。

### 当前关系

**video-link-breakdown → category-investment-decision（可选、单向）**

当用户主动提供 CIDM 报告或明确要求对接时，`video-link-breakdown` 可以：
- **读取** CIDM 的"内容传播"维度评分、切入楔子和最弱假设，作为视频分析起点。
- **回写**视频分析结论到 CIDM 维度：
  - 产品-视频匹配与复刻证据 → CIDM "内容传播"维度
  - 单位经济与达人/素材成本 → CIDM "利润空间"维度
  - 产品/内容合规快筛 → CIDM "风险可控性"维度
  - 新视频证据 → CIDM 切入楔子、验证计划或机会窗口

规则：对接为用户主动触发，不自动执行；视频分析结论优先于 CIDM 乐观判断；回写以"建议调整"形式呈现，由用户决定是否采纳。

**category-investment-decision → video-link-breakdown（可选、用户确认）。** 当内容传播是关键短板或最弱假设，且用户提供视频或要求验证打法时，CIDM 可建议启用视频 Skill；只有用户明确要求对接时才读取输出。回写必须记录原 CIDM 版本/日期、受影响维度、原分与建议分、变化理由、证据/假设编号，以及是否需要重判门槛；不得静默覆盖历史报告。

**competitive-intelligence-monitoring ↔ category-investment-decision（可选、用户确认）。** CIM 可读取 CIDM 的目标市场、自有 SKU、初始竞品链接、切入楔子、门槛和最弱假设来初始化监控池；新进入者、集中度、持续价格、VOC 缺口或竞争变化可以情报事件卡回传。CIDM 负责门槛与评分重判；双方保留版本、事件/证据 ID、原结论、建议调整、置信度和门槛影响，不静默覆盖历史。

**competitive-intelligence-monitoring ↔ video-link-breakdown（可选、用户确认）。** CIM 向 VLB 提供已确认的素材/广告变化、前后快照、产品一致性和关联效果信号；VLB 回传内容观测、机制、迁移性、测试假设和停止条件。CIM 负责时间线和竞争影响，VLB 负责视频级分析；内容高分不等于销量或竞争优势事实。

**consumer-insights-customer-growth ↔ category-investment-decision（可选、用户确认）。** CIDM 提供市场、商品、人群、切入楔子、复购与 LTV 假设；CIG 回传授权客户证据、留存、退货、贡献利润 CLV 和假设/实验结果。CIDM 负责资本决策，CIG 负责客户证据与增量效果有效性。回写保留双方版本、数据日期、原结论/评分、证据/实验 ID、建议调整、区间和门槛影响。

**consumer-insights-customer-growth ↔ competitive-intelligence-monitoring（可选、用户确认）。** CIM 提供外部竞品反馈、服务、价格、内容和机会窗口事件；CIG 检查相同问题是否出现在经授权的我方客户中，并量化受影响人群、生命周期和经济结果。CIM 负责外部变化，CIG 负责内部客户影响；不将公开竞品受众与我方客户做个人匹配。

**consumer-insights-customer-growth ↔ video-link-breakdown（可选、用户确认）。** CIG 提供已去识别人群、生命周期、任务、阻力、语言和内容假设；VLB 回传内容机制、迁移性、生产方案和测试变体。VLB 负责内容分析，只有 CIG 的实验或可信准实验可声称增量留存/利润。不静默覆盖历史，不自动执行触达。

**advertising-analysis-measurement-optimization ↔ category-investment-decision（可选、用户确认）。** AAMO 回传广告可行性、测量后的 CAC 区间、成熟边际利润、预算容量、放量与停止信号；只有 CIDM 拥有品类准入和资本配置主权，广告效率不得静默改变投资结论。

**advertising-analysis-measurement-optimization ↔ competitive-intelligence-monitoring（可选、用户确认）。** CIM 提供已确认的竞品广告事件与快照；AAMO 判断其对我方广告系统的相关性并只拥有广告动作主权。竞品信号不等于已验证的竞价机制，也不证明复制有效。

**advertising-analysis-measurement-optimization ↔ video-link-breakdown（可选、用户确认）。** VLB 提供内容机制、迁移性和创意测试变体；AAMO 负责付费交付、广告内部预算与放量。付费效果不能证明内容机制，视频高分也不自动授权预算。

**advertising-analysis-measurement-optimization ↔ consumer-insights-customer-growth（可选、用户确认）。** CIG 提供授权客户价值、生命周期和可信增量证据；AAMO 提供曝光、成本和平台归因结果。AAMO 不执行客户触达，平台归因不能替代 CIG 的因果标准。

**logistics-inventory-fulfillment-decision ↔ 所有业务主域 Skill（可选、用户确认）。** LIFD 拥有物流网络、路线、补货、库存配置、履约能力、逆向、异常和海外库存处置主权；接收 D04 供应约束、D05 合规门、D06 现金利润边界、PLCO 渠道计划、AAMO/D12 需求情景和 D13 退货体验证据，并只回传结构化 `proposed` 容量、库存、路线、回收和停止信号。LIFD 不直接改变资本、采购、法律、价格、广告、Listing、促销或客户动作结论。

**creator-affiliate-partnership-management ↔ CIDM/CIM/VLB/CIG/AAMO/LIFD/PLCO（可选、用户确认）。** CAPM拥有达人/联盟尽调、商务结构、佣金、交付验收、内容使用权、联盟对账、伙伴组合、续约和退出主权；可读取CIDM资本边界、CIM竞争事件、VLB内容机制、CIG去识别客户证据、AAMO付费测量、LIFD履约容量和PLCO页面断点。CAPM只发送带版本的`proposed`商务/权利/伙伴消息，各接收Skill保留自身主权；任何参与域不可用时CAPM仍须给出受限的独立结果，且只有AAMO能生效付费媒体决策。

### 新增跨 Skill 引用的规则

- 引用方 Skill 必须在其 `SKILL.md` 中写明引用关系；被引用方无需知晓调用者。
- 跨 Skill 引用必须是**可选的**——每个 Skill 必须能在不依赖其他 Skill 的情况下独立运行。
- 所有跨 Skill 引用必须在本节记录，包括方向（单向/双向）、触发条件（用户发起/自动）和数据流（读取什么/回写什么）。

## 11. 废弃与移除 Skill

1. 更新本文件：从第 6 节删除软链接命令、从第 7 节删除测试命令、从第 10 节删除跨 Skill 引用。
2. 更新 `README.md`：从中英文两部分中移除该 Skill 的条目。
3. 删除本地软链接：`rm "${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>"`。
4. 提交移除操作，commit message 中说明原因。
5. 若有其他 Skill 或外部工作流可能仍在引用该目录，保留一个 commit 周期后再删除目录。
