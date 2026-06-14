---
name: analyze-company
description: Use when the user asks to analyze a company, provides only a company name or ticker, or gives company-identifying information without another explicit task. Shouldn't be triggered on financials rebuild request.
---

# Analyze Company

Use this skill as the entry point for company analysis requests. Trigger it when the user asks to analyze a company, or when the user provides only a company name, ticker, or other company-identifying information without additional instructions.

## Workflow

Run these skills in order:

1. `$download-annual-reports`
2. `$extract-financial-data`
3. `$summarize`

Do not skip a skill unless the user explicitly says the required output from that skill already exists.
