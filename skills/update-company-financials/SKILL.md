---
name: update-company-financials
description: Use when the user asks to update or refresh a company financial Excel table or workbook.
---

# Update Company Financials

Use `$download-annual-reports`, `$extract-financial-data`, and `$excel-automation`. Use the most recent company XLSM as the source and make all changes in a newly created copy. Never modify or overwrite an existing workbook.
Result file should be formatted accordingly to the `financial_summary_structure.md` file.

## Locate The Source Workbook

Read `STOCKS_TARGET_FOLDER` from `docs/context_variables.local.md` when present; otherwise use `docs/context_variables.md`. Locate the company folder and select its most recent `.xlsm` file, excluding lock files, backups, and previously generated files for the same target year. Use an explicit workbook path when the user provides one.

## Determine Available Periods

Inspect the source workbook to identify its latest completed fiscal year and any existing interim row. Check the current date and the company's official investor-relations page to determine which newer annual and interim reports are available.

## Map The Workbook

Before editing, record each relevant worksheet's actual-period rows,
interim/TTM row, summary rows, forecast rows, metric columns, and dependent
valuation or result sections.

Identify the row that supplies styles and formulas for each inserted row.
Record formulas that reference the insertion area using
`find_formulas_referencing_rows`.

Map helper blocks outside the primary period table, including historical year
columns, forecast year columns, valuation cash-flow schedules, result bridges,
and IRR maps. Record their row and column meanings before insertion because
Excel may shift formulas into valid-looking self-references.

Do not infer mappings while writing data. Complete and review the worksheet map
before creating the output copy.

## Prepare Financial Data

Use `$download-annual-reports` to collect the required official reports. Use `$extract-financial-data` to extract every new period and at least one completed fiscal year already present in the source workbook.

## Reconcile Existing Data

Compare the overlapping extracted year with the corresponding workbook values and metric definitions. Stop without creating the new workbook when an unexplained mismatch, restatement, missing metric, or methodological ambiguity remains.

## Prepare The Update Specification

Create explicit records for every new annual and interim/TTM period. Create
worksheet mappings for metric values, repeated formulas, isolated formulas,
and cells that must be cleared.

Record the completed annual endpoint, recent-growth window, first forecast
year, forecast anchor row, and every dependent section requiring adjustment.

Keep this specification in agent working context or structured output data. Do
not create a company-specific Python update script.

## Create The Output Copy

Use PowerShell `Copy-Item -LiteralPath` on Windows or `cp --` on Unix-like
systems. Do not create a Python tool or script for copying.

Confirm the source exists and stop if the output already exists. Name the copy
`<Company>_<LatestCompletedFiscalYear>.xlsm`, even when a newer interim or TTM
row is available. Make all workbook changes only in this copy.

## Insert New Periods

Use `insert_styled_rows` through `$excel-automation` to preserve every existing actual year. Replace a forecast placeholder with actual data when its fiscal year is completed, then insert additional annual or TTM rows before the summary and forecast sections.

## Populate New Periods

Use `write_mapped_rows` to write reconciled annual and interim metric records
into the inserted rows. Supply the worksheet, starting row, and explicit
metric-to-column mapping.

Use `write_formulas` for formulas repeated across contiguous period rows. Use
`set_workbook_cells` for isolated values, formulas, and exceptions across
worksheets. Review the changes returned by `set_workbook_cells`.

Do not create company-specific row-population functions. The agent must derive
each mapping and formula from the inspected workbook structure.

## Apply The Update

Perform workbook changes in this order:

1. Insert and style all required period rows.
2. Populate reconciled metric values.
3. Translate repeated row formulas.
4. Apply isolated cell updates and clear obsolete cells.
5. Update averages, CAGRs, forecasts, and valuation sections.
6. Repair dependent references using the explicit reviewed mapping.
7. Scan for circular references and repair every detected dependency cycle.

Do not save intermediate structural changes over the source workbook.

## Update Growth Formulas

Calculate each long-term CAGR from the earliest retained completed fiscal year through the latest completed fiscal year. When a separate recent CAGR exists, compare approximately three- to five-year completed-period windows, select a representative window that mitigates exceptional spikes, and record the selected endpoints and rationale.

## Update Average Formulas

Adjust each ordinary non-growth average formula so its source range includes all completed annual periods. Exclude interim and TTM rows from average and CAGR formula ranges.

## Update Forecast Formulas

Keep forecasts anchored to the latest completed annual period. When interim or TTM data exists for the first forecast year, adjust that year's growth assumption so applying it to the latest annual value produces a forecast close to the interim or TTM value within the workbook's displayed precision.

## Update Dependent Formulas

Use the existing formula tools through `$excel-automation`; do not create a
company-specific formula-update utility.

1. Use `translate_row_formulas` when copying formulas from an existing period
   row to a newly inserted row. Review the translated formulas before
   continuing.
2. Use `find_formulas_referencing_rows` after determining the insertion range
   and again after inserting rows. Search every dependent worksheet, including
   summary, forecast, result, valuation, and IRR sheets.
3. Classify each returned reference by its intended meaning. Decide whether it
   should continue pointing to the same historical period, move with the
   inserted content, expand through the latest completed annual period, or
   exclude an interim/TTM row.
4. Build an explicit old-reference to new-reference mapping for references that
   did not retain their intended meaning.
5. Apply that mapping with `replace_formula_references`. Review every returned
   old and new formula before saving.
6. Re-run `find_formulas_referencing_rows` and inspect the affected cells
   directly. A formula without `#REF!` can still point to the wrong period or
   column, so broken-reference scanning alone is insufficient.
7. Inspect formulas in helper rows and columns adjacent to the insertion area.
   Specifically check for direct self-references such as `A20=A20-1`, shifted
   year sequences, formulas moved under the wrong header, and result or
   valuation formulas that now use the wrong input column.

Do not apply a blanket row-offset replacement. Formula changes must preserve
the semantic purpose of each historical, summary, forecast, and valuation
reference.

## Verify The Workbook

Confirm overlap reconciliation, completed-year continuity, and preservation of
every prior actual period. Use `compare_cell_styles` on representative cells
from each inserted row and its source row.

Inspect average and CAGR formulas to confirm their endpoints include completed
annual periods and exclude interim, TTM, and forecast rows. Inspect forecast,
result, valuation, and IRR cells directly to confirm their semantic period and
column references remain correct.

Use `scan_broken_formula_references`, `missing_years`, and
`list_external_links` through `$excel-automation`. Also run
`scan_circular_formula_references` across every worksheet. Check for missing
formulas and incorrect range endpoints.

The circular-reference result must be empty. When a cycle is found:

1. Inspect every formula cell returned for the cycle.
2. Restore the intended helper sequence, cross-sheet link, or valuation bridge
   from the pre-insertion workbook map.
3. Do not enable iterative calculation or suppress Excel's warning.
4. Re-run `scan_circular_formula_references` until it returns no cycles.

Directly inspect representative helper blocks after the repair, including year
sequences, forecast schedules, result cash-flow columns, valuation outputs, and
IRR endpoints. Confirm each formula remains under the correct semantic header.

Run these validations before saving and again after reopening the copied XLSM
with VBA preservation enabled. Do not deliver or copy the workbook to its final
destination unless both circular-reference scans return empty. Stop and report
any unexpected external link, broken reference, circular dependency, missing
completed year, or VBA loss.

## Report The Result

Report the output workbook path, inserted annual and interim periods, source
reports, overlap comparison, changed formulas, selected recent-growth windows,
and all judgment calls. State that circular-reference validation passed and
report the number of cycles found and repaired. Clearly report any periods or
metrics that could not be added.
