---
name: summarize
description: Summarize prepared financial CSV files from a company-specific ./output/<Company>/ folder and create a result XLSM workbook from the shared template. Use when the user asks to summarize prepared statements, fill the valuation template, create a result workbook, or generate a company XLSM from existing output CSV files.
---

# Summarize

Use this skill when a company-specific folder already exists under `./output/` with prepared financial CSV files.

This skill must not read annual reports, PDFs, filing text, or web sources. It summarizes and transfers the prepared statement data from `./output/<Company>/` into the XLSM template defined by `TEMPLATE_XLSM_PATH` in `docs/context_variables.md`.

## Required Skill

Use `$excel-automation` for all workbook inspection, copying, population, validation, and correction. Do not manipulate `.xlsm` files outside the tools allowed by that skill.

## Inputs

- Read `docs/context_variables.md` first.
- Use `TEMPLATE_XLSM_PATH` as the source workbook template.
- Use `STOCKS_TARGET_FOLDER` as the root folder for result workbooks.
- Determine `COMPANY_OUTPUT_FOLDER` as `./output/<Company>/`.
- Require `profit_and_loss.csv`, `cash_flow.csv`, and one `*_stock_data.csv` file in `COMPANY_OUTPUT_FOLDER`.
- If the company name is not provided, infer it only when exactly one company subfolder exists under `./output/`; otherwise ask the user to choose the company.

## Output Workbook

- Create `STOCKS_TARGET_FOLDER/<Company>/` when it does not exist.
- Copy the template workbook into that folder before editing it.
- Name the copied result workbook `<Company>_<Year>.xlsm`.
- Use the latest fiscal year from `profit_and_loss.csv` for `<Year>`; if the latest row is marked `TTM`, use the numeric year part.
- Never overwrite an existing workbook unless the user explicitly approves it.

## Workflow

### Step 1: Verify Prepared Output
- Locate `COMPANY_OUTPUT_FOLDER`.
- Require `profit_and_loss.csv`, `cash_flow.csv`, and exactly one `*_stock_data.csv` file.
- Stop if any required CSV file is missing, empty, or ambiguous.
- Determine the latest year from `profit_and_loss.csv`.

### Step 2: Prepare Result Workbook
- Read `TEMPLATE_XLSM_PATH` and `STOCKS_TARGET_FOLDER`.
- Create `STOCKS_TARGET_FOLDER/<Company>/`.
- Set the result workbook path to `STOCKS_TARGET_FOLDER/<Company>/<Company>_<Year>.xlsm`.
- Use the same `<Year>` as the template workbook filename when the template name contains a year, such as
  `Template_2025.xlsm` -> `<Company>_2025.xlsm`, even if the prepared CSV files include a later TTM or interim row.

### Step 3: Download Company Logo
- Download the company's logo as a PNG with a transparent background.
- Save the normalized logo PNG in `COMPANY_OUTPUT_FOLDER` as `company_logo.png`.
- Prefer the automated Wikimedia Commons lookup in `tools/download_company_logo.py`; if automatic lookup is ambiguous or fails, use a direct logo URL and normalize it through the same tool workflow.

### Step 4: Develop Mapping, Populate, Insert Logo, And Validate
- Use `$excel-automation` to inspect the template and read the prepared CSV files.
- Develop the mapping schema from the template structure and the financial data available in `COMPANY_OUTPUT_FOLDER`.
- Populate the result workbook from the prepared CSV files according to that mapping schema.
- Set the `Result` sheet current price cell to the latest current price from the stock data.
- Populate the right-side price sensitivity values on the `Result` sheet around the current price: two rounded prices below the current price, the current price, and two rounded prices above the current price, using a reasonable rounded step for the stock's price level.
  Example: if the current price is `$47`, use `$30`, `$40`, `$47`, `$55`, and `$65`.
- Insert the transparent PNG logo on the `Result` sheet at `E21`, scaled to fit within `1214 x 221`, using `$excel-automation` for the workbook operation.
- Preserve formulas, formatting, VBA, workbook structure, and assumptions unless the user explicitly asks for a change.
- Report the workbook display currency applied by the population workflow.
- Report the final workbook path.
