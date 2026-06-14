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

## IMPORTANT: Do Not Read Source Files

**Never open or read any file under `tools/` to learn how a tool works.**
All usage information you need is in this skill. If something is unclear or a
parameter is missing from this document, **ask the user** before proceeding.
Reading source files to fill in gaps is not permitted.

## Invocation Pattern

Brick functions live in `tools/xlsm_bricks.py` and are imported in an inline
Python one-liner passed directly to `python -c`. Always run from the project
root so the import resolves:

```powershell
python -c "
import sys; sys.path.insert(0, 'tools')
from xlsm_bricks import open_workbook, save_workbook, insert_styled_rows
wb = open_workbook('e:/My Drive/Stocks/Acme/Acme_2025.xlsm')
ws = wb['P&L']
insert_styled_rows(ws, row=12, amount=2, source_row=11)
save_workbook(wb, 'e:/My Drive/Stocks/Acme/Acme_2025.xlsm')
"
```

Prefer the inline `python -c` form above. When PowerShell quoting makes an
inline call impractical (formulas containing `'` worksheet names or `$`
variables), write a minimal temporary `.py` file to `output/<Company>/`
instead — one import block and one utility call, no logic. Delete the file
immediately after the call succeeds. Never write scripts that combine
multiple utility calls or implement any workflow logic.

### PowerShell Quoting Pitfalls

When running `python -c` from PowerShell, three quoting rules apply:

**Rule 1 — No literal `"` inside the argument string.**
PowerShell strips double-quotes before Python sees them. Pass double-quote characters as `chr(34)` inside the Python code instead.

**Rule 2 — Use a single-quoted heredoc for multi-line code.**
A `@'...'@` heredoc avoids PowerShell variable expansion (`$VAR`) and quote stripping:
```powershell
python -c @'
import sys; sys.path.insert(0, "tools")
from xlsm_bricks import open_workbook, save_workbook, set_workbook_cells
wb = open_workbook("e:/My Drive/Stocks/Acme/Acme_2025.xlsm")
# ...
save_workbook(wb, "e:/My Drive/Stocks/Acme/Acme_2025.xlsm")
'@
```
The closing `'@` must start at column 0 with no leading whitespace.

**Rule 3 — No literal `'` inside a `@'...'@` heredoc.**
A single quote inside the heredoc terminates it early. For Excel cross-sheet formula references that contain worksheet names in single quotes (e.g. `='P&L'!B2`), use `chr(39)`:
```python
# Correct — no literal single quote in the heredoc
q = chr(39)
formula = "=" + q + "P&L" + q + "!B%d" % row

# Wrong — the ' before P&L closes the heredoc
formula = "='P&L'!B%d" % row  # BREAKS the heredoc
```

---

## CLI Scripts

### `tools/inspect_xlsm.py`

Prints workbook metadata: sheet names, dimensions, value/formula cell counts,
and merged ranges. Writes a summary to `output/xlsm_inspection.json`.

```
python tools/inspect_xlsm.py <workbook_path>
```

Example:
```powershell
python tools/inspect_xlsm.py "e:/My Drive/Stocks/Acme/Acme_2025.xlsm"
```

---

### `tools/dump_xlsm_sheet.py`

Prints a CSV-formatted excerpt of one worksheet. Shows cell values and
formulas. Use for structure mapping and formula review.

```
python tools/dump_xlsm_sheet.py <workbook_path> <sheet_name>
    [--min-row N] [--max-row N] [--min-col N] [--max-col N]
```

Example — dump P&L rows 1–30:
```powershell
python tools/dump_xlsm_sheet.py "e:/My Drive/Stocks/Acme/Acme_2025.xlsm" "P&L" --min-row 1 --max-row 30
```

---

### `tools/update_template_xlsm.py`

Fills a blank template with data from CSV files in a folder, populates stock
prices, inserts the company logo, and sets the current price in the Result
sheet. Use for standard summarise workflows where the template has enough
period slots.

```
python tools/update_template_xlsm.py <template_path>
    [--output OUTPUT_PATH]
    [--csv-folder CSV_FOLDER]
    [--ticker TICKER]
    [--fiscal-year-end-month N]       # default 12
    [--company COMPANY_NAME]
    [--logo-path PATH]
    [--logo-url URL]
    [--logo-output PATH]
    [--logo-anchor CELL]              # default E21
    [--logo-max-width PX]             # default 1214
    [--logo-max-height PX]            # default 221
    [--skip-logo]
    [--display-currency CODE]         # e.g. EUR; converts number formats
    [--template-currency CODE]        # default USD
```

Example:
```powershell
python tools/update_template_xlsm.py "e:/My Drive/Stocks/AbbVie/Template_2025.xlsm" `
    --output "e:/My Drive/Stocks/Acme/Acme_2025.xlsm" `
    --csv-folder "output/Acme" `
    --ticker ACME `
    --fiscal-year-end-month 12
```

---

## Brick Functions (imported from `tools/xlsm_bricks.py`)

### Workbook Open / Save

#### `open_workbook(path, keep_vba=True) → Workbook`

Opens an `.xlsm` file with openpyxl. Always pass `keep_vba=True` unless
working with a plain `.xlsx`.

```python
wb = open_workbook('e:/My Drive/Stocks/Acme/Acme_2025.xlsm')
```

#### `save_workbook(wb, output_path, validate=True, keep_vba=True) → Path`

Saves the workbook and sets `recalculate_on_open`. When `validate=True`
(default) re-opens the saved file in read-only mode to confirm it is not
corrupted.

```python
save_workbook(wb, 'e:/My Drive/Stocks/Acme/Acme_2025.xlsm')
```

---

### Row Insertion

#### `insert_styled_rows(ws, row, amount=1, source_row=None, first_col=1, last_col=None)`

Inserts `amount` blank rows immediately before `row` on worksheet `ws`.
Copies cell styles, number formats, and row height from `source_row` (an
existing row near the insertion point). Correctly shifts `row_dimensions`
after insertion (openpyxl does not do this automatically).

**Does not populate values or formulas** — call `set_workbook_cells` or
`write_mapped_rows` afterward.

```python
# Insert 2 rows before row 12, styled like row 11
insert_styled_rows(ws, row=12, amount=2, source_row=11)
```

---

### Row Style Copy

#### `copy_row_styles(ws, source_row, target_row, first_col, last_col)`

Copies cell style from every cell in `source_row` to the matching cell in
`target_row`, column by column within `[first_col, last_col]`.

```python
copy_row_styles(ws, source_row=11, target_row=12, first_col=1, last_col=16)
```

---

### Style Validation

#### `compare_cell_styles(ws, source_ref, target_refs) → list[dict]`

Compares the style of `source_ref` against each cell in `target_refs`.
Returns a list of dicts `{cell, expected_style_id, actual_style_id}` for
cells whose style differs from the source. An empty list means all styles
match.

- `source_ref`: cell address string, e.g. `"B11"`
- `target_refs`: list of cell address strings, e.g. `["B12", "C12"]`

```python
mismatches = compare_cell_styles(ws, "B11", ["B12", "C12", "D12"])
```

---

### Formula Translation

#### `translate_row_formulas(ws, source_row, target_row, first_col=1, last_col=None) → dict`

Copies every formula from `source_row` to `target_row`, adjusting relative
row references to the new row number. Returns `{col_letter: translated_formula}`
for every cell that had a formula. Review the returned formulas before saving.

```python
translated = translate_row_formulas(ws, source_row=11, target_row=13)
# inspect translated before writing
```

---

### Formula Reference Search

#### `find_formulas_referencing_rows(wb, min_row, max_row, ref_sheet=None, search_sheets=None) → list[dict]`

Finds every formula cell in `wb` whose A1 references intersect the row range
`[min_row, max_row]`. Optionally restrict to references pointing to
`ref_sheet` and/or restrict which worksheets are searched via `search_sheets`
(list of sheet name strings).

Returns a list of dicts:
`{sheet, cell, formula, matched_reference}`

```python
hits = find_formulas_referencing_rows(wb, min_row=12, max_row=13)
hits = find_formulas_referencing_rows(wb, min_row=12, max_row=13,
                                      ref_sheet="P&L",
                                      search_sheets=["Cash flow", "Result"])
```

---

### Formula Reference Replacement

#### `replace_formula_references(wb, replacements, sheets=None) → list[dict]`

Replaces formula references across worksheets according to `replacements`, a
dict mapping old reference strings to new reference strings. Optionally
restrict to `sheets` (list of sheet name strings).

Returns a list of dicts `{sheet, cell, old_formula, new_formula}` for every
changed cell. **Review this list before saving.**

```python
changes = replace_formula_references(
    wb,
    replacements={"F11": "F13", "O11": "O13"},
    sheets=["P&L", "Cash flow"],
)
```

---

### Explicit Cell Updates

#### `set_workbook_cells(wb, updates) → list[dict]`

Writes values or formulas to explicit cells across one or more worksheets.
`updates` is `{sheet_name: {cell_ref: value}}` where `value` is a number,
string, date, or formula string starting with `=`.

Returns a list of dicts `{sheet, cell, old_value, new_value}` for every
written cell. **Review this list before saving.**

```python
changes = set_workbook_cells(wb, {
    "P&L": {
        "A12": 2024,
        "B12": 20444,
        "F12": "=C12+D12+E12",
    },
    "Result": {"C2": 45.20},
})
```

---

### Data Population

#### `write_mapped_rows(ws, rows, start_row, mapping, limit=None)`

Writes rows from a list of dicts (e.g. from `read_csv_rows`) into a
worksheet starting at `start_row`. `mapping` is an ordered list of
`(col_letter, (csv_header, parser_fn))` tuples. `parser_fn` is typically
`parse_number`, `parse_year`, or `parse_iso_date`. Stops after `limit` rows
if provided.

```python
from xlsm_bricks import write_mapped_rows, parse_number, parse_year, read_csv_rows
rows = read_csv_rows('output/Acme/profit_and_loss.csv')
write_mapped_rows(ws, rows, start_row=2, mapping=[
    ("A", ("Year",    parse_year)),
    ("B", ("Revenue", parse_number)),
    ("C", ("EBIT",    parse_number)),
])
```

#### `write_columnar_rows(ws, rows, start_row, columns, limit=None) → int`

Like `write_mapped_rows` but uses `columns` — an ordered list of
`(col_letter, (csv_header, parser_fn))` tuples. Returns the number of rows
written.

```python
written = write_columnar_rows(ws, rows, start_row=2, limit=11, columns=[
    ("A", ("Year",         parse_year)),
    ("B", ("Revenue",      parse_number)),
    ("C", ("EBIT",         parse_number)),
    ("D", ("D&A",          parse_number)),
    ("H", ("Total debt",   parse_number)),
    ("I", ("Excess cash",  parse_number)),
    ("O", ("Diluted shares", parse_number)),
])
```

#### `write_formulas(ws, formulas_by_col, start_row, row_count)`

Writes repeated formulas across `row_count` consecutive rows starting at
`start_row`. `formulas_by_col` is `{col_letter: callable(row) → str|None}`
where the callable receives the current row number and returns the formula
string (or `None` to leave the cell empty).

```python
write_formulas(ws, start_row=2, row_count=12, formulas_by_col={
    "F": lambda row: f"=C{row}+D{row}+E{row}",
    "G": lambda row: None if row == 2 else f"=(F{row}-F{row-1})/F{row-1}",
    "J": lambda row: f"=O{row}*P{row}",
})
```

#### `write_two_column_series(ws, rows, start_row, first_col, second_col, first_spec, second_spec, limit=None) → int`

Writes a two-column series (e.g. date + close) from CSV rows into a
worksheet. `first_spec` and `second_spec` are `(csv_header, parser_fn)`
tuples. Returns the number of rows written.

```python
from xlsm_bricks import write_two_column_series, parse_iso_date, parse_number
written = write_two_column_series(
    ws, price_rows, start_row=18,
    first_col="U", second_col="V",
    first_spec=("Date", parse_iso_date),
    second_spec=("Close", parse_number),
)
```

---

### CSV Helpers

#### `read_csv_rows(path) → list[dict]`

Reads a CSV file and returns a list of row dicts keyed by header name.
Handles UTF-8 BOM automatically.

```python
rows = read_csv_rows('output/Acme/profit_and_loss.csv')
```

#### `latest_number(rows, sort_column, value_column) → float|int|None`

Returns the numeric value in `value_column` from the row with the highest
value in `sort_column`. Useful for finding the most recent stock price.

```python
current_price = latest_number(price_rows, sort_column="Date", value_column="Close")
```

---

### Prices and Logo

#### `populate_result_prices(ws, current_price, current_cell="C2", price_cells=("K2","L2","M2","N2","O2"), step=None) → list`

Writes `current_price` to `current_cell` and computes a five-value price
sensitivity band (two below, current, two above) into `price_cells`. Returns
the five price values written.

```python
band = populate_result_prices(wb["Result"], current_price=45.20)
```

#### `add_scaled_png(ws, image_path, anchor_cell="E21", max_width=1214, max_height=221, replace_from_row=18) → (width, height)`

Inserts a PNG image into `ws` anchored at `anchor_cell`, scaled to fit
within `max_width × max_height` pixels. Removes any existing image anchored
at or below `replace_from_row` first. Returns the inserted image dimensions.

```python
w, h = add_scaled_png(wb["Result"], "output/Acme/company_logo.png")
```

---

### Currency Formatting

#### `apply_currency_number_formats(wb, target_currency, source_currency="USD", sheets=None) → list[dict]`

Replaces currency tokens in number formats across worksheets, e.g. `$` → `€`.
Only touches number-format strings; does not modify values or formulas.
Returns a list of changed cells.

```python
changes = apply_currency_number_formats(wb, target_currency="EUR")
```

---

### Metric Reconciliation

#### `compare_metric_records(expected, actual, tolerances=None, fields=None) → list[dict]`

Compares two metric dicts field by field. `tolerances` is an optional
`{field: abs_tolerance}` dict. `fields` restricts which keys are compared.
Returns a list of mismatch dicts `{field, expected, actual, diff}`. An empty
list means all compared fields reconcile.

```python
mismatches = compare_metric_records(
    expected={"Revenue": 20502, "EBIT": 11547},
    actual={"Revenue": 20502, "EBIT": 11547},
    tolerances={"Revenue": 1},
)
```

---

### Validation

#### `scan_broken_formula_references(wb, sheets=None) → list[dict]`

Returns a list of dicts `{sheet, cell, formula}` for every cell containing
`#REF!`. `sheets` limits which worksheets are scanned.

```python
broken = scan_broken_formula_references(wb, sheets=["P&L", "Cash flow", "Result"])
```

#### `scan_circular_formula_references(wb, sheets=None, max_range_cells=10000) → list`

Detects direct self-references and indirect dependency cycles. Returns a list
of cycle descriptions. An empty list means no cycles were found. Run after
every structural change.

```python
cycles = scan_circular_formula_references(wb)
```

#### `missing_years(years) → list[int]`

Accepts an iterable of integer years and returns a sorted list of any gaps.

```python
gaps = missing_years([2014, 2015, 2017, 2018])  # → [2016]
```

Pass a list of integer year values — not a worksheet object. Extract year values first:
```python
years = [ws.cell(row=r, column=1).value for r in range(2, 15)
         if isinstance(ws.cell(row=r, column=1).value, int)]
gaps = missing_years(years)
```

#### `list_external_links(wb) → list[dict]`

Returns a list of dicts describing each external workbook relationship
(index and file-link metadata). Does not modify the workbook.

```python
links = list_external_links(wb)
```

---

### Period Row Classification

#### `classify_period_rows(ws, min_row, max_row, classifiers) → list[dict]`

Classifies each row in `[min_row, max_row]` using `classifiers`, an ordered
list of `(category_name, predicate_fn)` pairs where `predicate_fn(ws, row)`
returns `True` when the row belongs to that category. Returns a list of dicts
`{row, category}`. The first matching predicate wins; unmatched rows get
category `"unknown"`.

```python
from xlsm_bricks import classify_period_rows
def is_data(ws, row): return isinstance(ws.cell(row, 1).value, int)
def is_summary(ws, row): return ws.cell(row, 1).value is None and ws.cell(row, 2).value is not None
classified = classify_period_rows(ws, min_row=2, max_row=20, classifiers=[
    ("data", is_data),
    ("summary", is_summary),
])
```

---

### Utility Parsers

These are used as `parser_fn` arguments in mapping/column helpers:

| Function | Input | Output |
|---|---|---|
| `parse_number(value)` | `"20,502"` | `20502` (int) or float |
| `parse_year(value)` | `"2024 TTM"` | `2024` (int) |
| `parse_iso_date(value)` | `"2024-12-01"` | `datetime.date` |

#### `clear_columns(ws, columns, start_row, end_row)`

Clears all cell values in the specified column letters between `start_row`
and `end_row` (inclusive).

```python
clear_columns(ws, columns=["U", "V"], start_row=18, end_row=1000)
```
