# Financials Agent Instructions

These instructions apply to Codex, Claude Code, GitHub Copilot, and any other coding agent working in this repository.

## Repository Skills
- Before starting a task, inspect the repo-local `skills/` folder for a skill that matches the user's request.
- Also inspect the common skills folder at `..\Common\AI\skills`. Use a common skill when it matches the user's request and no more specific repo-local skill applies.
- When a relevant skill exists, read its `SKILL.md` and follow it.
- Skills may point to supporting documentation in `docs/`; read those files when instructed by the skill.

## Available Local Skills
- `skills/analyze-company/SKILL.md`: run the full company workflow by downloading reports, extracting financial data, and summarizing the results.
- `skills/extract-financial-data/SKILL.md`: extract financial metrics from public company reports and save structured CSV output.
- `skills/download-annual-reports/SKILL.md`: download annual reports, 10-Ks, 20-Fs, and equivalent yearly filings from official investor relations sources.
- `skills/summarize/SKILL.md`: summarize prepared financial CSV files and create a result XLSM workbook from the shared template.

## Available Common Skills
- Common skills are stored one repo level above this repository in `..\Common\AI\skills`.
- `..\Common\AI\skills\step-by-step\SKILL.md`: approval-gated workflow for AI-facing edits.

## General
- Keep financial extraction precise. Use exact figures from filings, not rounded estimates.
- Preserve user changes in the working tree. Do not revert unrelated edits.
- Prefer existing scripts and project conventions over new tooling unless the task requires otherwise.
