# Financials Agent Instructions

These instructions apply to Codex, Claude Code, GitHub Copilot, and any other coding agent working in this repository.

## Repository Skills
- Before starting a task, inspect the repo-local `skills/` folder for a skill that matches the user's request.
- Also inspect the common skills folder at `..\Common\AI\skills`. Use a common skill when it matches the user's request and no more specific repo-local skill applies.


## Available Common Skills
- Common skills are stored one repo level above this repository in `..\Common\AI\skills`.

## General
- Keep financial extraction precise. Use exact figures from filings, not rounded estimates.
- Preserve user changes in the working tree. Do not revert unrelated edits.
- Prefer existing scripts and project conventions over new tooling unless the task requires otherwise.

## Result formatting
- Result files should be formatted accordingly to the `financial_summary_structure.md` file.