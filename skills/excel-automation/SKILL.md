---
name: excel-automation
description: Inspect, populate, validate, and repair Excel .xlsm workbooks using the repository tools in ./tools. Use when the user asks to inspect workbook structure, dump sheet ranges, preserve VBA while editing templates, copy CSV data into a workbook, apply formulas or formatting, validate saved XLSM files, or correct workbook automation issues.
---

# Excel Automation

Use this skill for controlled `.xlsm` workbook inspection and updates in this repository.

Use the existing Python tools under `./tools/` for workbook inspection,
population, validation, and correction. Use native shell commands for file
copying when required by the calling workflow. Preserve VBA, formulas, styles,
and workbook structure unless the user explicitly asks to change them.

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

## Row Insertion

- Use `insert_styled_rows` to insert caller-specified worksheet rows and copy cell styles, number formats, and row height from a caller-selected source row.
- Supply all row positions, counts, and column boundaries from the calling workflow.
- This brick does not decide where rows belong or populate their values and formulas.

## Style Validation

- Use `compare_cell_styles` to compare one source cell's style with caller-selected target cells.
- The function returns cells whose style IDs differ, including expected and actual style IDs.
- It does not modify styles or decide which cells should match.

## Formula Translation

- Use `translate_row_formulas` to copy formulas from a caller-selected source row to a target row with relative references translated to the target coordinates.
- Supply the source row, target row, and column boundaries from the calling workflow.

## Formula Reference Search

- Use `find_formulas_referencing_rows` to find workbook formulas whose A1-style references intersect a caller-supplied row range.
- Optionally restrict the referenced sheet and the worksheets searched.
- The result includes each formula cell, its formula, and the matching parsed reference.

## Formula Reference Replacement

- Use `replace_formula_references` to replace caller-supplied formula references across selected worksheets.
- Pass an exact mapping of old references to new references.
- Review the returned old and new formulas before saving the workbook.

## Explicit Cell Updates

- Use `set_workbook_cells` to apply caller-supplied values and formulas to explicit cells across multiple worksheets.
- Pass updates as `{sheet_name: {cell_reference: value}}`.
- Review the returned sheet, cell, old value, and new value records before saving.
- The caller must decide every target cell and value; this tool does not map metrics, periods, or formulas.

## Metric Reconciliation

- Use `compare_metric_records` to compare caller-supplied metric dictionaries.
- Supply optional fields and absolute tolerances by metric.
- An empty result means the compared fields reconcile; otherwise the result lists each mismatch.

## Formula And Year Validation

- Use `scan_broken_formula_references` to list formula cells containing `#REF!`.
- Use `scan_circular_formula_references` to detect direct self-references and
  indirect dependency cycles between formula cells.
- A clean `scan_broken_formula_references` result does not prove that formulas
  are cycle-free. Run both checks after structural row or column changes.
- Use `missing_years` to identify gaps in a caller-supplied collection of completed fiscal years.

## External Link Validation

- Use `list_external_links` to list external workbook relationships without modifying them.
- The function returns each relationship's index and file-link metadata.

## Period Row Classification

- Use `classify_period_rows` to classify rows within caller-supplied boundaries.
- Supply ordered category names and classifier functions for actual, interim, summary, forecast, or other row types.
