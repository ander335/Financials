# XLSM Automation Instructions

Use these instructions when an AI agent needs to copy data from CSV files into an Excel `.xlsm` valuation template, check formatting, or build projections.

## Goal

Keep workbook edits deterministic and auditable. The AI should reason about the workbook layout, then use Python bricks from `tools/xlsm_bricks.py` to make controlled changes.

Do not paste data manually. Do not edit `.xlsm` files as ZIP/XML unless a Python Excel library cannot perform the required operation.

## Main Files

- `tools/xlsm_bricks.py`: reusable workbook operations.
- `tools/update_template_xlsm.py`: current example workflow for this template.
- `tools/inspect_xlsm.py`: workbook structure inspection.
- `tools/dump_xlsm_sheet.py`: sheet range dump for understanding formulas and formatting.
- `output/profit_and_loss.csv`: P&L and balance-sheet metrics.
- `output/cash_flow.csv`: cash-flow metrics.
- `output/*_stock_data.csv`: monthly price data.

## Standard Workflow

1. Inspect the template before editing:
   ```powershell
   python .\tools\inspect_xlsm.py "path\to\template.xlsm"
   python .\tools\dump_xlsm_sheet.py "path\to\template.xlsm" "P&L" --min-row 1 --max-row 40 --min-col 1 --max-col 18
   python .\tools\dump_xlsm_sheet.py "path\to\template.xlsm" "Cash flow" --min-row 1 --max-row 40 --min-col 1 --max-col 13
   ```

2. Identify three types of cells:
   - CSV input cells: write values from CSV files.
   - Formula cells: write or preserve Excel formulas.
   - Model assumption cells: write only when the user explicitly instructs it.

3. Build the import workflow with `tools/xlsm_bricks.py`.

4. Copy formatting from nearby correct rows or columns after writing values.

5. Validate key number formats before saving.

6. Save with `save_workbook(...)`, which also asks Excel to recalculate on open and validates that `openpyxl` can reopen the saved file.

## Bricks Available

Use these helpers from `tools/xlsm_bricks.py`:

- `open_workbook(path, keep_vba=True)`
- `save_workbook(wb, output_path, validate=True, keep_vba=True)`
- `read_csv_rows(path)`
- `detect_single_file(folder, pattern)`
- `parse_number(value)`
- `parse_year(value)`
- `parse_iso_date(value)`
- `latest_number(rows, sort_column, value_column)`
- `write_columnar_rows(ws, rows, start_row, columns, limit=None)`
- `write_mapped_rows(ws, rows, start_row, mapping, limit=None)`
- `write_formulas(ws, formulas_by_col, start_row, row_count)`
- `write_two_column_series(...)`
- `clear_range(ws, cell_range)`
- `clear_columns(ws, columns, start_row, end_row)`
- `copy_cell_style(source, target)`
- `copy_row_styles(ws, source_row, target_row, first_col, last_col)`
- `copy_range_styles(ws, source_range, target_start_cell)`
- `format_column_rows(ws, column, start_row, row_count, number_format)`
- `collect_formats(ws, cell_refs)`
- `assert_same_number_format(ws, source_ref, target_refs)`

## Mapping Pattern

Prefer explicit mappings from CSV columns to Excel columns:

```python
write_columnar_rows(
    ws,
    rows,
    start_row=2,
    limit=11,
    columns=[
        ("A", ("Year", parse_year)),
        ("B", ("Revenue", parse_number)),
        ("C", ("EBIT", parse_number)),
    ],
)
```

Then add formulas separately:

```python
write_formulas(
    ws,
    start_row=2,
    row_count=11,
    formulas_by_col={
        "F": lambda row: f"=C{row}+D{row}+E{row}",
        "G": lambda row: None if row == 2 else f"=(F{row}-F{row - 1})/F{row - 1}",
    },
)
```

## Formatting Rules

Formatting must be copied or asserted deliberately.

For a TTM row or newly added historical row, copy the style from the nearest complete historical row:

```python
copy_row_styles(ws, source_row=11, target_row=12, first_col=1, last_col=13)
```

Then validate important formats:

```python
assert_same_number_format(ws, "B11", ["B12", "C12", "D12", "E12", "F12", "G12"])
assert_same_number_format(ws, "L11", ["L12", "M12"])
```

When a row mixes currency, percentages, and share counts, validate each group against a known-good source cell.

## Projection Rules

Projection logic should be written as Excel formulas unless the user specifically asks Python to calculate fixed projection values.

Before writing projections:

1. Locate the projection block with `dump_xlsm_sheet.py`.
2. Identify the first forecast year and the final explicit forecast year.
3. Determine which cells are assumptions, such as growth rates or terminal multiples.
4. Write formulas into forecast output cells.
5. Leave user assumptions untouched unless instructed.
6. Copy styles from the previous forecast row or nearest complete row.
7. Validate percentage columns and currency columns separately.

## Safety Rules

- Always write to a new output workbook unless the user explicitly asks to overwrite the template.
- Use `keep_vba=True` for `.xlsm` workbooks.
- Preserve formulas unless the workflow intentionally replaces them.
- Preserve styles by copying from known-good cells.
- Run a saved-file reopen check through `save_workbook`.
- If Microsoft Excel reports corruption, stop using that output file and regenerate from the original template with `openpyxl`.

## Current Template Notes

For `Template_2025.xlsm`, the current known import areas are:

- `P&L!A2:P12`: historical and TTM P&L/valuation inputs.
- `Cash flow!A2:M12`: historical and TTM cash-flow inputs.
- `P&L!U18:V1000`: monthly date and close price history.
- `P&L!V15`: fiscal year-end month number.
- `Result!C2`: current share price.

Current workflow command:

```powershell
python .\tools\update_template_xlsm.py "e:\My Drive\Stocks\AbbVie\Template_2025.xlsm" --output .\output\filled_Template_2025_openpyxl.xlsm --fiscal-year-end-month 12
```
