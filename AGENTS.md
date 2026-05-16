# Financials Agent Instructions

These instructions apply to Codex, Claude Code, GitHub Copilot, and any other coding agent working in this repository.

## Repository Skills
- Before starting a task, inspect the repo-local `skills/` folder for a skill that matches the user's request.
- When a relevant skill exists, read its `SKILL.md` and follow it.
- Skills may point to supporting documentation in `docs/`; read those files when instructed by the skill.

## Available Local Skills
- `skills/analyze-company/SKILL.md`: extract financial metrics from public company reports and save structured CSV output.

## General
- Keep financial extraction precise. Use exact figures from filings, not rounded estimates.
- Preserve user changes in the working tree. Do not revert unrelated edits.
- Prefer existing scripts and project conventions over new tooling unless the task requires otherwise.
