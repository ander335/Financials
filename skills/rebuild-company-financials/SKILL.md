---
name: rebuild-company-financials
description: Use when the user asks to rebuild a company financial workbook from the template, copying all historical data from the existing XLSM and adding any newer periods on top. Produces a structurally clean result based on the current template rather than an accumulated copy of an old workbook.
---

# Rebuild Company Financials

Use `$download-annual-reports`, `$extract-financial-data`, and `$excel-automation`. The existing company XLSM is a **data source only** — the output workbook is built fresh from `TEMPLATE_XLSM_PATH`. Never modify or overwrite an existing workbook.
The output workbook must conform to `docs/financial_summary_structure.md`.

## Absolute Prohibition on Python Scripts

**Never write, generate, or execute a Python script or temporary file to interact with any workbook.** All Excel operations — reading cells, writing values, inserting rows, copying data between workbooks, applying formats, scanning formulas — must be performed by calling the utility scripts from `$excel-automation` directly (e.g. `inspect_xlsm.py`, `dump_xlsm_sheet.py`, `set_workbook_cells`, `write_mapped_rows`, etc.) with the appropriate arguments. Data transfer from the source workbook to the output copy is done by reading cell values through those utilities and writing them through the same utilities — not by authoring a helper script that wraps them.

## Locate Inputs

Read `TEMPLATE_XLSM_PATH` and `STOCKS_TARGET_FOLDER` from `docs/context_variables.local.md` when present; otherwise use `docs/context_variables.md`. Locate the most recent `.xlsm` file in `STOCKS_TARGET_FOLDER/<Company>/`, excluding lock files, backups, and previously generated files for the same target year — this is the source workbook. Use an explicit source path when the user provides one.

Stop if no source workbook is found. Use `$summarize` instead when no prior company XLSM exists.

## Enumerate All Historical Periods

Inspect the source workbook to list **every** completed fiscal year row across all relevant sheets (P&L, Cash Flow). Record the earliest and latest completed fiscal years, any existing interim or TTM row, and the metric-to-column mapping on each sheet.

Read `REPORTS_FOLDER` from `docs/context_variables.local.md` when present; otherwise use `docs/context_variables.md`. List all files already present in `REPORTS_FOLDER/<Company>/` and determine which fiscal years and interim periods they cover. Compare against the source workbook's latest completed year to identify any periods not yet available in either source. Do not browse the web or the company's investor-relations page yourself at this stage.

## Prepare Financial Data for New Periods

When periods newer than the latest completed fiscal year in the source workbook are not yet present in `REPORTS_FOLDER/<Company>/`, invoke `$download-annual-reports` to collect only those missing reports. Do not invoke `$download-annual-reports` when the needed reports are already present in the folder.

Use `$extract-financial-data` to extract every new period and at least one completed fiscal year already present in the source workbook for reconciliation.

## Reconcile Overlapping Year

Compare the overlapping extracted year with the corresponding values in the source workbook and metric definitions. Stop without creating the output workbook when an unexplained mismatch, restatement, missing metric, or methodological ambiguity remains.

## Map the Template Structure

Before creating the output copy, inspect `TEMPLATE_XLSM_PATH` with the inspection tools from `$excel-automation` (`inspect_xlsm.py`, `dump_xlsm_sheet.py`). Record:

- The number of default period slots (rows) on each data sheet.
- The exact row numbers of the summary/average row, growth row, forecast rows, and all dependent sections.
- Metric column layout on each sheet.
- All helper blocks outside the primary period table: historical year columns, forecast schedules, valuation cash-flow sections, result bridges, and IRR maps.

Do not infer mappings while writing data. Complete the template map before creating the output copy.

## Create Output Copy from Template

Use PowerShell `Copy-Item -LiteralPath` on Windows or `cp --` on Unix-like systems.

Confirm the template exists and stop if the output already exists. Name the copy `<Company>_<LatestCompletedFiscalYear>.xlsm` in `STOCKS_TARGET_FOLDER/<Company>/`, where `<LatestCompletedFiscalYear>` is the newest completed fiscal year across source and any newly downloaded data. Make all workbook changes only in this copy.

## Expand Template for All Historical Years

The template contains a fixed number of period slots (typically 10). Count the total completed fiscal years to be written (all years from the source workbook plus any new annual periods). When the total exceeds the template's slot count, insert the required extra rows **before** the summary/average row on every relevant sheet, using `insert_styled_rows` with a style source row from an adjacent period row.

**openpyxl does not reliably update relative formula references in rows that move during `insert_rows`.** Row heights are handled correctly by `insert_styled_rows` (it manually shifts `row_dimensions` after insertion). Formula references are not — after inserting rows:

1. Dump every affected section with `dump_xlsm_sheet.py` and inspect each formula manually.
2. Rewrite every forecast row formula explicitly using `set_workbook_cells`, deriving each cell reference from the new row numbers. Never carry over shifted formulas from the insert operation.
3. Rewrite every valuation row formula the same way.
4. Run `find_formulas_referencing_rows` across all sheets (including cross-sheet references from Result and IRR map) to catch stale references in other sheets that openpyxl also did not update automatically.

Cross-sheet formula references (e.g., Result sheet referencing Cash flow rows, IRR map referencing P&L rows) are **never** updated automatically by openpyxl's `insert_rows` — they must be corrected with `replace_formula_references` or `set_workbook_cells` after every structural row change.

## Prepare The Rebuild Specification

Create explicit records for every period to be written (all historical years from the source workbook, then any new periods). For each period record:

- The target sheet and row in the output copy.
- An explicit metric-to-column mapping.
- Whether the row value is read from the source XLSM or from a freshly extracted CSV.

Record the completed annual endpoint, first forecast year, forecast anchor row, and every dependent section requiring adjustment after population. Keep this specification in agent working context.

## Populate All Historical Data

For every historical year present in the source workbook, read the metric values directly from the source workbook cells (using `dump_xlsm_sheet.py` or cell inspection via `$excel-automation`). Write them into the output copy oldest→newest using `write_mapped_rows` or `set_workbook_cells`.

For new periods not present in the source workbook, write from the freshly extracted CSV data.

Use `write_formulas` for formulas that repeat across contiguous period rows. Use `set_workbook_cells` for isolated values, formulas, and exceptions across worksheets. Review every change returned by `set_workbook_cells`.

Derive each mapping from the inspected workbook structure.

## Add TTM/Interim Row

If a newer interim or TTM period exists (either carried over from the source workbook or from a newly downloaded report), insert it after the last completed annual row using `insert_styled_rows` + `write_mapped_rows`. Format the row label per `financial_summary_structure.md`.

## Populate Prices, Logo, Price Sensitivity

Follow the same steps as the `$summarize` skill and `tools/update_template_xlsm.py`:

- Stock prices (date and close) → relevant sheet rows.
- Current price → `Result!C2`.
- Price sensitivity band → `Result!K2:O2` via `populate_result_prices` (two rounded prices below, current price, two above).
- Company logo → `add_scaled_png` at `Result!E21`, scaled to fit within 1214 × 221.
- Apply display currency via `apply_currency_number_formats` if the company reports in a non-USD currency.

## Apply The Rebuild

Perform workbook changes in this order:

1. Expand template rows on all relevant sheets.
2. Populate all historical period values (oldest to newest).
3. Populate new periods.
4. Write repeated row formulas.
5. Apply isolated cell updates.
6. Add TTM/interim row if present.
7. Populate prices, logo, and price sensitivity.
8. Update averages, CAGRs, forecasts, and valuation sections.
9. Repair dependent formula references.
10. Scan for circular references and repair every detected dependency cycle.

## Update Summary Row Formulas

Apply CAGR or average per metric and CAGR window as specified in `financial_summary_structure.md`.

## Update Forecast Formulas

Follow the forecast chain structure and growth column rules in `financial_summary_structure.md`. After any row insertion, rewrite the entire forecast section — every row from the first forecast year through the last — using `set_workbook_cells`. Construct each formula from the final row numbers. Never assume openpyxl preserved the chain correctly.

For each forecast row `r` (first forecast row `r0` through last `r_last`):
- Year: `N{r} = "=N{r-1}+1"` (except first row: `N{r0} = first_forecast_year`)
- EBITDA: `O{r} = "=O{r-1}*(1+P{r})"` (except first row: `O{r0} = "=F{last_completed}*(1+P{r0})"`)
- Shares: `R{r} = "=R{r-1}*(1+S{r})"` (except first row: `R{r0} = "=O{last_completed}*(1+S{r0})"`)

Verify the year sequence is contiguous and the EBITDA chain has no gaps before saving.

## Update Dependent Formulas

Use the existing formula tools through `$excel-automation`.

1. Use `translate_row_formulas` when copying formulas from an existing period row to a newly inserted row. Review the translated formulas before continuing.
2. Use `find_formulas_referencing_rows` after determining the expansion range and again after inserting rows. Search every dependent worksheet, including summary, forecast, result, valuation, and IRR sheets.
3. Classify each returned reference by its intended meaning. Decide whether it should continue pointing to the same historical period, expand through the latest completed annual period, or exclude an interim/TTM row.
4. Build an explicit old-reference to new-reference mapping for references that did not retain their intended meaning.
5. Apply that mapping with `replace_formula_references`. Review every returned old and new formula before saving.
6. Re-run `find_formulas_referencing_rows` and inspect the affected cells directly. A formula without `#REF!` can still point to the wrong period or column.
7. Inspect formulas in helper rows and columns adjacent to the expansion area. Specifically check for direct self-references such as `A20=A20-1`, shifted year sequences, formulas moved under the wrong header, and result or valuation formulas that now use the wrong input column.

Do not apply a blanket row-offset replacement. Formula changes must preserve the semantic purpose of each historical, summary, forecast, and valuation reference.

## Verify The Workbook

Confirm every historical year from the source workbook is present and matches the source values. Confirm all completed years are contiguous with no gaps.

Use `scan_broken_formula_references`, `missing_years`, and `list_external_links` through `$excel-automation`. Also run `scan_circular_formula_references` across every worksheet.

The circular-reference scan must confirm conformance with `financial_summary_structure.md` (zero cycles, no iterative-calculation workaround). When a cycle is found:

1. Inspect every formula cell returned for the cycle.
2. Restore the intended helper sequence, cross-sheet link, or valuation bridge from the pre-rebuild template map.
3. Do not enable iterative calculation or suppress Excel's warning.
4. Re-run `scan_circular_formula_references` until it returns no cycles.

Also confirm the output conforms to `financial_summary_structure.md`: row order, blank rows, label formatting, CAGR vs. average assignment, and percentage number formats.

Run these validations before saving and again after reopening the output XLSM with VBA preservation enabled. Do not deliver or copy the workbook to its final destination unless both circular-reference scans return empty. Stop and report any unexpected external link, broken reference, circular dependency, missing completed year, or VBA loss.

## Sheet Scope

By default, all rebuild, verification, and format-fix work applies only to the **P&L**, **Cash flow**, and **Result** sheets. Do not inspect, update, or repair the ROE or IRR map sheets unless the user explicitly asks for it.

## Visual Verification

After all programmatic checks pass, invoke `$take-screenshots` on the output workbook, targeting the **P&L**, **Cash flow**, and **Result** sheets only.

Once the screenshots are saved, read `docs/financial_summary_structure.md` and inspect every screenshot against each rule. Work through each sheet in turn and check:

1. **Row order** — Data rows (oldest→newest) → TTM/interim row (if present) → blank row → summary row → optional recent-CAGR row → blank row → forecast/valuation section. Any deviation is a violation.
2. **Blank rows** — Exactly one blank row separates the data/TTM block from the summary block, and exactly one blank row separates the summary block from the forecast section. Extra or missing blank rows are violations.
3. **TTM/interim label** — If a TTM or interim row is present, its year label must show only the year number with no suffix. A label like "2024 TTM" or "Q3 2024" is a violation.
4. **Summary row formula type** — For each metric, confirm the cell uses CAGR (for growth metrics: Revenue, EBIT, EBITDA, D&A, Debt, Market Cap, Share count; CFO, CAPEX, Distributed Cash, FCFE, FCFE/share) or average (for ratio/level metrics: EV/EBITDA, Debt/EBITDA, DC/FCF, FCFE Yield, Div Yield, EV/Equity). A mismatched formula type is a violation.
5. **Number formats** — Percentage columns (growth rates, margins, yields, CAGRs) must display as percentages, not raw decimals. A cell showing "0.12" where "12%" is expected is a violation.
6. **Label duplication** — Summary row labels (e.g., "Yield:", "Stock Price:") must appear in exactly one column. A label repeated in an adjacent column is a violation.
7. **Forecast chain** — Verify visually that the first forecast year hardcodes a year value and that subsequent rows increment by one. Any visible gap or non-sequential year is a violation.
8. **Contiguous annual rows** — All completed fiscal years must appear with no gap rows between them. A missing year or unexpected blank between annual rows is a violation.

For every violation found:
- State the sheet, row, and column where the violation occurs.
- Quote the exact rule from `docs/financial_summary_structure.md` that is broken.
- Apply the fix using the appropriate tool from `$excel-automation` (format correction via `set_workbook_cells` or `apply_currency_number_formats`, row reorder via `insert_styled_rows` / row deletion, label correction via `set_workbook_cells`).
- Re-run `$take-screenshots` on the affected sheet after fixing to confirm the violation is resolved.

Do not proceed to **Report The Result** until all screenshots are free of violations.

## Report The Result

Report the output workbook path, all historical years written, any new periods added, the source reports used, overlap comparison, changed formulas, selected recent-growth windows, and all judgment calls. State that circular-reference validation passed and report the number of cycles found and repaired. Clearly report any periods or metrics that could not be added.
