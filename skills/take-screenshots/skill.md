---
name: take-screenshots
description: Use when the user asks to take or capture screenshots of an Excel workbook.
---

# Take Screenshots

Capture PNG screenshots of sheets in an `.xlsm` workbook using `tools/xlsm_screenshot.py`.

## Locate The Workbook

Read `STOCKS_TARGET_FOLDER` from `docs/context_variables.local.md` when present; otherwise use `docs/context_variables.md`. Find the company folder and select the most recent `.xlsm` file, excluding lock files (`~$`). Use an explicit path if the user provides one.

## Determine Output Folder

Output goes to `output/<CompanyName>/screenshots/` under the project root. Create it if it does not exist.

## Run The Script

```bash
python tools/xlsm_screenshot.py "<workbook_path>" "<project_root>/output/<CompanyName>/screenshots" [sheet1 sheet2 ...]
```

Capture all sheets unless the user specifies otherwise.

## Report

List each saved PNG path when done.
