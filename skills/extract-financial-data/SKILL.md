---
name: extract-financial-data
description: Extract precise financial metrics from public company annual reports, 10-Ks, 20-Fs, equivalent filings, or interim reports and save structured CSV output.
---

# Extract Financial Data

Use this skill when extracting financial metrics from public company annual reports, 10-Ks, 20-Fs, equivalent filings, or interim reports.

## Inputs
- Use `REPORTS_FOLDER` from `docs/context_variables.local.md` when present;
  otherwise use `docs/context_variables.md`.
- Reports for analysis must be stored in a company-specific subfolder of `REPORTS_FOLDER`.
- Name the reports subfolder like the company being analyzed, for example `REPORTS_FOLDER/Apple` or `REPORTS_FOLDER/Novo Nordisk`.
- Save all generated output in a company-specific subfolder of `./output/` named like the company being analyzed, for example `./output/Apple/` or `./output/Novo Nordisk/`.
- The company name or ticker may be provided by the user. If not provided, detect it from the reports and use that company name for the input and output subfolders.

## Required Reading
1. Read `docs/context_variables.md` first for shared workflow variable examples,
   then read `docs/context_variables.local.md` when present and prefer those
   local values.
2. Read `docs/financial_report_structure.md` for statement descriptions and metric definitions.

## General Rules
- Analyze only reports that already exist in `COMPANY_REPORTS_FOLDER` unless the user explicitly asks to download or collect reports.
- Do not browse the web, search investor relations pages, or invoke the `download-annual-reports` skill during analysis merely because a company name was provided.
- If no company-specific reports folder exists, or if the existing folder does not contain analyzable reports, stop and tell the user what is missing. Ask whether they want reports downloaded as a separate step.
- Extract key financial metrics from public company annual reports for at least the last 10 years when enough reports are available.
- Reports are normally presented in sequence every 2 years, such as 2025, 2023, etc.
- The `Consolidated Balance Sheet` is normally disclosed for 2 years in each report. Other statements may be disclosed for 3 years. Consider only the latest 2 years from each report.
- Be precise with numbers. Use the exact figures from filings, not rounded estimates. Flag any line items that required judgment calls.
- Report all monetary values in millions of the relevant currency, such as USD millions or EUR millions.
- If source statements are presented in thousands, divide monetary figures by 1,000 and preserve precision with decimals rather than rounding away filing detail.
- Shares outstanding should also be reported in millions.

## Workflow

### Step 1: Inventory Reports
- Determine `COMPANY_REPORTS_FOLDER`, the company-specific subfolder inside `REPORTS_FOLDER`.
- Determine `COMPANY_OUTPUT_FOLDER`, the company-specific subfolder inside `./output/`.
- First inspect the existing `COMPANY_REPORTS_FOLDER`. Treat downloaded files in this folder as the source of truth for the analysis.
- Do not look for additional reports online during this step. Missing years should be noted as data gaps, not silently sourced from the web.
- List all files in `COMPANY_REPORTS_FOLDER`.
- List files in `COMPANY_OUTPUT_FOLDER`.
- For `.pdf`, `.htm`, `.html`, and `.txt` reports that are not yet converted to text, use `tools/analyze_pdf.py`.
- Convert only files that are not already present in `COMPANY_OUTPUT_FOLDER`; provide those files as script arguments.
- Do not analyze reports during this inventory step.
- Triage reports by filename. There may be annual reports and one optional quarter report.
- Determine how much financial data is available.
- Example: for reports 2025, 2021, ..., 2015, the total available period is 12 years (`2025 - 2015 + 2`).
- Reference this value as `AVAILABLE_PERIOD`.

### Step 2: Read Only the Most Recent Financial Report
- Extract company name and ticker, primary listing exchange, and main reporting currency.
- Locate the consolidated statements according to `docs/financial_report_structure.md`.
- Learn their exact naming and structure because older reports should use similar wording.
- Find how and where shares outstanding are reported for this company. Use the same pattern in the other reports.
- For debt payment, analyze the company's debt structure and how debt movements are reported. Use the same pattern in the other reports.

### Step 3: Extract Historical Prices
- Run `tools/historical_prices.py` with the company ticker, `AVAILABLE_PERIOD + 1`, and `--output COMPANY_OUTPUT_FOLDER` as arguments.
- Example: `python tools/historical_prices.py AAPL 13 --output "COMPANY_OUTPUT_FOLDER"`, where 13 means `AVAILABLE_PERIOD` years of data plus 1 year for margin.
- The script outputs `Currency: <currency>`. Compare this with the reporting currency. If they differ, warn the user.

### Step 4: ADR Check
- If the listing exchange is not the company's home exchange, such as a Japanese company listed on NYSE or a European company listed on NYSE/NASDAQ, the ticker likely represents an ADR.
- Determine the ADR ratio, meaning the number of ordinary shares per ADR, from the company's ADR prospectus or investor relations page.
- Cross-check the ratio by taking the most recent year-end share price from the price data, multiplying it by `shares_outstanding / ADR_RATIO`, and comparing the implied market cap against a known reference such as reported market cap or home-exchange share price times full share count.
- The ratio is correct when the implied market caps align.
- Warn the user with the ADR ratio found and state that diluted shares will be divided by that ratio in all output files.
- Store the ADR ratio as `ADR_RATIO` and divide all `diluted_shares` values by `ADR_RATIO` before saving CSV files.

### Step 5: Continue With Remaining Reports
- After analyzing the most recent report, use the extracted company-specific patterns to process the remaining reports.
- Continue directly to historical aggregation unless required inputs are missing or the extracted statements are too ambiguous to proceed safely.

### Step 6: Read Other Reports
- Aggregate information according to `docs/financial_report_structure.md`.
- Output data marked with `###` headings under `# Financial report structure`.
- Rows should represent years; columns should represent metrics.
- The most recent year should appear on the bottom.

### Step 7: Aggregate Latest Quarter Report, If Present
- Add the corresponding year to the result table and mark the year with `TTM`.
- Use shares outstanding from the quarter report.
- Use all balance sheet data from the quarter report.
- For the `Consolidated Income Statement` and `Consolidated Statement of Cash Flow`, use a TTM approach so the numbers can be compared with the previous year.
- Locate statements that include the most fiscal data.
- For a Q3 report, look for `Nine Months Ended`.
- For a Q2 or interim report, look for `Six Months Ended` or `Half-year Ended`.
- If Q2 or Q3 reports include only the corresponding quarter period, warn the user. In that case, all available quarter reports need to be provided.
- Calculate the difference versus the same period in the previous year.
- Example: `Revenue Nine Months Ended Dec 31, 2025 = 13,031.7` and `Revenue Nine Months Ended Dec 31, 2024 = 11,651.2`, so the difference is `+1,380.5`.
- The TTM value is the previous financial year value plus the difference.

### Step 8: Note Issues
- Note any data gaps, restatements, or fiscal year changes.

### Step 9: Save Financial Data
- Save result tables into 2 `.csv` files in `COMPANY_OUTPUT_FOLDER`.
- Save monetary values in millions of the reporting currency. Keep share counts in millions.
- Save `profit_and_loss.csv` with:
  - Revenue
  - EBIT
  - D&A
  - Total debt
  - Excess cash
  - Diluted shares
- Save `cash_flow.csv` with:
  - Cash flow from operations
  - Capex
  - Debt payment (net)
  - Dividends

### Step 10: Currency Conversion, If Needed
Use this only when reporting currency differs from price currency.

- Run `python tools/fx_rates.py FROM TO --year-end MONTH --output "COMPANY_OUTPUT_FOLDER"` using the company's fiscal year-end month.
- Add `--spot-date YYYY-MM-DD` if a TTM row exists, where the date is the quarter-end balance sheet date.
- Example: `python tools/fx_rates.py JPY USD --year-end 3 --spot-date 2025-12-31 --output "COMPANY_OUTPUT_FOLDER"`.
- Use the resulting `COMPANY_OUTPUT_FOLDER/fx_FROM_TO_FY<MMM>.csv`, with columns `average_rate` and `year_end_rate`.
- Income statement and cash flow items use `average_rate`: Revenue, EBIT, D&A, CFO, Capex, Debt payment, Dividends.
- Balance sheet items use `year_end_rate`: Total debt, Excess cash.
- TTM balance sheet uses the spot rate returned by `--spot-date`.
- TTM income statement and cash flow values use the average rate of the current in-progress fiscal year, marked with `*` in the FX table.
- Shares outstanding require no conversion because they are unit counts, not monetary values.
- Rename original files to `profit_and_loss_<original_currency_lowercase>.csv` and `cash_flow_<original_currency_lowercase>.csv`.
- Save converted files as `profit_and_loss_<target_currency_lowercase>.csv` and `cash_flow_<target_currency_lowercase>.csv`.
- Round all converted monetary values to the nearest whole number in the same unit as the original, such as millions.
- Run `python tools/verify_fx.py "COMPANY_OUTPUT_FOLDER"` to verify the converted files. Fix any reported mismatches before proceeding.

## How To Use `tools/analyze_pdf.py`

`tools/analyze_pdf.py` extracts text from PDFs and saves it as `.txt` files. Agents should save and read those text files from `COMPANY_OUTPUT_FOLDER`.

1. Place annual report PDFs in the company-specific subfolder inside `REPORTS_FOLDER`.
2. Run with `--folder` pointing to `COMPANY_REPORTS_FOLDER` and `--output` pointing to `COMPANY_OUTPUT_FOLDER` to convert all PDFs, or pass specific filenames to convert only those:
   - `python tools/analyze_pdf.py --folder "COMPANY_REPORTS_FOLDER" --output "COMPANY_OUTPUT_FOLDER"`
   - `python tools/analyze_pdf.py --folder "COMPANY_REPORTS_FOLDER" --output "COMPANY_OUTPUT_FOLDER" report1.pdf report2.pdf`
3. Running the script takes about 1-2 minutes. Wait for it to finish. Do not run any other Python commands while it is running.
