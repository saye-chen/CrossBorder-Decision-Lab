# Repository Rules

Maintenance conventions for this repository. This file is not loaded automatically when a Skill runs. Put every runtime-critical rule in the relevant `SKILL.md`.

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

# Run skill-specific test suites (only for skills that ship them)
[ -f category-investment-decision/scripts/test_models.py ] && \
  python3 category-investment-decision/scripts/test_models.py

[ -f video-link-breakdown/scripts/test_prepare_video_link.py ] && \
  python3 video-link-breakdown/scripts/test_prepare_video_link.py

python3 scripts/validate_repo.py

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

# 运行 Skill 专属测试套件（仅对提供了测试的 Skill）
[ -f category-investment-decision/scripts/test_models.py ] && \
  python3 category-investment-decision/scripts/test_models.py

[ -f video-link-breakdown/scripts/test_prepare_video_link.py ] && \
  python3 video-link-breakdown/scripts/test_prepare_video_link.py

python3 scripts/validate_repo.py

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
