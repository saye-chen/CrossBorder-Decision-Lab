# Miles-Chen Codex Skills

Personal Codex skills for ecommerce research, content analysis, and repeatable AI workflows.

## Skills

### Category Investment Decision

Creates structured ecommerce category-entry decision reports with scoring, risk analysis, platform recommendations, and operating plans.

Path: `category-investment-decision/`

### Video Link Breakdown

Analyzes short-form video links into script structure, editing techniques, content quality, reusable templates, and improvement suggestions.

Path: `video-link-breakdown/`

## Repository Workflow

Use this repository as the source of truth for local skill changes.

## Workspace Hygiene

After each skill modification, new skill creation, report generation, script run, or analysis task, clean up temporary files created during the work. Keep only intentional source changes and final deliverables.

Temporary files include scratch folders, caches, downloaded source media, extracted raw pages, one-off screenshots, intermediate exports, test artifacts, and disposable calculation files. If a task needs persistent evidence or reusable assets, store them deliberately in the relevant skill folder and document why they are kept.

Before finishing, check the workspace for unintended generated files. If cleanup cannot be completed, report the remaining files and the reason.

Conversation context and model reasoning state cannot be physically deleted from the workspace, but no local files should be kept merely to preserve intermediate thinking.

```bash
git add .
git commit -m "Update skills"
git push
```

## Structure

Each skill lives in its own folder and includes a required `SKILL.md`. UI-facing metadata, when present, lives in `agents/openai.yaml`.
