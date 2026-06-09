---
name: update-company-financials
description: Use when the user asks to update or refresh a company financial Excel table or workbook.
---

# Update Company Financials

Use `$download-annual-reports`, `$extract-financial-data`, and `$excel-automation`. Use the most recent company XLSM as the source and make all changes in a newly created copy. Never modify or overwrite an existing workbook.

## Locate The Source Workbook

Read `STOCKS_TARGET_FOLDER` from `docs/context_variables.local.md` when present; otherwise use `docs/context_variables.md`. Locate the company folder and select its most recent `.xlsm` file, excluding lock files, backups, and previously generated files for the same target year. Use an explicit workbook path when the user provides one.

## Determine Available Periods

Inspect the source workbook to identify its latest completed fiscal year and any existing interim row. Check the current date and the company's official investor-relations page to determine which newer annual and interim reports are available.

## Prepare Financial Data

Use `$download-annual-reports` to collect the required official reports. Use `$extract-financial-data` to extract every new period and at least one completed fiscal year already present in the source workbook.

## Reconcile Existing Data

Compare the overlapping extracted year with the corresponding workbook values and metric definitions. Stop without creating the new workbook when an unexplained mismatch, restatement, missing metric, or methodological ambiguity remains.

## Create The Output Copy

Copy the source XLSM before making changes. Name the copy `<Company>_<LatestCompletedFiscalYear>.xlsm`, even when a newer interim or TTM row is available. Stop if that output path already exists unless the user provides a different name.

## Insert New Periods

Use `insert_styled_rows` through `$excel-automation` to preserve every existing actual year. Replace a forecast placeholder with actual data when its fiscal year is completed, then insert additional annual or TTM rows before the summary and forecast sections.

## Update Growth Formulas

Calculate each long-term CAGR from the earliest retained completed fiscal year through the latest completed fiscal year. When a separate recent CAGR exists, compare approximately three- to five-year completed-period windows, select a representative window that mitigates exceptional spikes, and record the selected endpoints and rationale.

## Update Average Formulas

Adjust each ordinary non-growth average formula so its source range includes all completed annual periods. Exclude interim and TTM rows from average and CAGR formula ranges.

## Update Forecast Formulas

Keep forecasts anchored to the latest completed annual period. When interim or TTM data exists for the first forecast year, adjust that year's growth assumption so applying it to the latest annual value produces a forecast close to the interim or TTM value within the workbook's displayed precision.

## Update Dependent Formulas

Use `translate_row_formulas`, `find_formulas_referencing_rows`, and `replace_formula_references` through `$excel-automation`. Adjust downstream references so summary, forecast, and valuation formulas continue to point to their intended periods after rows are inserted.

## Verify The Workbook

Confirm overlap reconciliation, completed-year continuity, preservation of prior actual periods, and matching styles and formulas on inserted rows. Confirm average and CAGR ranges exclude interim and forecast rows, and confirm forecasts remain anchored to the latest completed annual period.

Use `scan_broken_formula_references` and `missing_years` through `$excel-automation`. Check for missing formulas, incorrect range endpoints, and unexpected external links, then save and reopen the copied XLSM with VBA preservation enabled.

## Report The Result

Report the output workbook path, inserted annual and interim periods, source reports, overlap comparison, changed formulas, selected recent-growth windows, and all judgment calls. Clearly report any periods or metrics that could not be added.
