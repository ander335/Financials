---
name: excel-automation
description: Inspect, copy, populate, validate, and repair Excel .xlsm workbooks using the repository tools in ./tools. Use when the user asks to inspect workbook structure, dump sheet ranges, preserve VBA while editing templates, copy CSV data into a workbook, apply formulas or formatting, validate saved XLSM files, or correct workbook automation issues.
---

# Excel Automation

Use this skill for controlled `.xlsm` workbook inspection and updates in this repository.

Use only the existing Python tools under `./tools/` for workbook inspection, copying, population, validation, and correction. Preserve VBA, formulas, styles, and workbook structure unless the user explicitly asks to change them.

## Tool Map

- `tools/inspect_xlsm.py`: inspect workbook metadata, sheets, dimensions, merged cells, formulas, and used ranges.
- `tools/dump_xlsm_sheet.py`: print a selected sheet range for mapping, formula review, and formatting checks.
- `tools/xlsm_bricks.py`: import reusable workbook operations in repository automation scripts.
- `tools/update_template_xlsm.py`: use as the current template-population workflow example.

## Logo Insertion

- Use the existing `tools/xlsm_bricks.py` `add_scaled_png` helper to insert transparent PNG logos into `.xlsm` workbooks.
- Get the target worksheet, anchor cell, and maximum logo dimensions from the calling skill or workflow context.

## Currency Formatting

- Use `tools/adjust_xlsm_currency.py` to audit or update currency display formats in an existing `.xlsm` workbook.
- Currency-format changes must only update number-format currency tokens; preserve values, formulas, decimal places, negative formats, percentages, shares, and workbook structure.
