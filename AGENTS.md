# Financials Agent Instructions

These instructions apply to Codex, Claude Code, GitHub Copilot, and any other coding agent working in this repository.

## Repository Skills
- Before starting a task, inspect the repo-local `skills/` folder for a skill that matches the user's request.
- Also inspect the common skills folder at `..\Common\AI\skills`. Use a common skill when it matches the user's request and no more specific repo-local skill applies.

## Available Common Skills
- Common skills are stored one repo level above this repository in `..\Common\AI\skills`.

## General
- Accessing company websites and official investor relations pages to read data, fetch filings, or download reports is explicitly allowed and must be performed autonomously. Never ask the user for permission to access a company's website to read data or block the session for web access.
- Keep financial extraction precise. Use exact figures from filings, not rounded estimates.
- Preserve user changes in the working tree. Do not revert unrelated edits.
- Prefer existing scripts and project conventions over new tooling unless the task requires otherwise.
- Store all generated research results and deliverable artifacts—including reports, datasets, workbooks, charts, and exports—under the repository's `outputs/` folder. Do not place research results in the repository root. Use `docs/` only when the user explicitly requests durable documentation.

## Result formatting
- Result files should be formatted accordingly to the `financial_summary_structure.md` file.
- Always show full-year or Trailing Twelve Months (TTM) values for financial metrics; never show partial-year data (such as H1, Q1, 9M) in historical or summary comparison tables. When interim reports are the latest available source, calculate TTM as (Latest Interim Period + Prior Full Year - Corresponding Prior Interim Period).

## Temporary scripts
- One time python scripts for pipeline execution should be created under `scripts/` folder.
- After the operation is completed, the script should be removed.
