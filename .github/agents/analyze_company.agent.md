---
name: analyze_company
description: Analyzes annual reports found in the reports/ folder and extracts key financial metrics into structured CSV tables.
argument-hint: Company name or ticker to analyze (optional — agent will detect from reports).
tools: ['read', 'execute', 'edit', 'todo']
---

# Analyze annual reports found in the reports folder.
- REPORTS_FOLDER=`C:\Users\user\Downloads\`

# General
- Be precise with numbers — use the exact figures from filings, not rounded estimates. Flag any line items that required judgment calls.

# Steps
## Read `CLAUDE.md` file in the project root for context

## List all files in the `REPORTS_FOLDER` folder
   - List files in the `./output/`, for the `.pdf`, `.htm`, `.html`, and `.txt` reports that are not yet converted to text use `analyze_pdf.py`. Convert only the files that are not yet present in the `output/` folder, provide them as the script arguments.
   - Do not analyze reports at this stage.
   - Triage the reports by their name. There could be annual reports and 1 quarter report (optional).
   - Analyze how much financial data is presented. Example:
      - For reports 2025, 2021, ..., 2015 total available period will be 12 years (2025 - 2015 + 2)
      - This value can be referenced as `AVAILABLE_PERIOD`

## Read only the most recent financial report
   - Extract company name and ticker, primary listing exchange, main reporting currency.
   - Locate the consolidated statements according to the `CLAUDE.md` file. Familiarize with their exact naming and structure since they will appear in a similar way in older reports.
   - Find how and where `Shares outstanding (shares in issue)` is reported for this company. Use the same pattern to find this information in the other reports.
   - For `Debt payment` analyze the debt structure, what debt the company has and how movements are reported. Use the same pattern in the other reports.

## Extract historical prices data
   - Run `historical_prices.py` with the company ticker and the number of years `AVAILABLE_PERIOD` + 1 as arguments.
   - Example: `python historical_prices.py AAPL 13` (where 13 = `AVAILABLE_PERIOD` years of data + 1 for margin)
   - **Important**: The script outputs the `Currency: <currency>`, compare it with the reporting currency. If it's not the same, warn the user about it.
   - **ADR check**: If the listing exchange is not the company's home exchange (e.g. a Japanese company listed on NYSE, or a European company listed on NYSE/NASDAQ), the ticker likely represents an ADR. In that case:
     - Determine the ADR ratio (number of ordinary shares per ADR) from the company's ADR prospectus or investor relations page.
     - Cross-check: take the most recent year-end share price from the price data, multiply by (shares_outstanding ÷ ADR_ratio), and compare the implied market cap against a known reference (e.g. reported market cap, or cross-check with the home-exchange share price × full share count). The ratio is correct when the implied market caps align.
     - **⚠ WARNING**: Display a warning to the user stating the ADR ratio found and that diluted shares will be divided by that ratio in all output files.
     - Store the ADR ratio as `ADR_RATIO` and divide all `diluted_shares` values by `ADR_RATIO` before saving to CSV.

## User confirmation (Required). Important to request the approval before reading other reports
   - Show all the consolidated statements from the most recent report to the user as tables.
   - Show the extracted financial data from the most recent report.
   - Provide comments how the data was extracted for this company.
   - Ask for approval to proceed with the other reports.

## Read other reports. Aggregate info in the following format according to the `CLAUDE.md` file:
   - Output data that is marked as `###` three sharps under `# Financial report structure` structure.
   - Rows should represent years, columns - metrics.
   - The most recent year should appear on the bottom.

## Aggregate latest quarter report (Optional, if the report was found)
   - Add corresponding year to the result table. Mark the year with `TTM` in the table.
   - Apply the following rules:
   - `Shares outstanding` should be taken from the quarter report.
   - All balance sheet data should be taken from the quarter report.
   - For the `Consolidated Income statement` and `Consolidated statement of cash flow` use the TTM approach to get the numbers that can be compared with the previous year:
      - Locate statements that include the most fiscal data. Example:
         - For Q3 report - Look for `Nine Months Ended`
         - For Q2 or interim report - Look for `Six Months Ended` or `Half-year Ended`
         - If in Q2 or Q3 reports only the corresponding period is reported, warn user about it. In this case all available quarter reports need to be provided.
      - Calculate `the difference` with the same period previous year. Example:
         - Revenue Nine Months Ended Dec 31, 2025 - 13,031.7
         - Revenue Nine Months Ended Dec 31, 2024 - 11,651.2
         - Calculate `the difference` +1380.5 = (13,031.7 - 11,651.2)
      - Result value is the previous financial year value with `the difference` applied.

## Note any data gaps, restatements, or fiscal year changes

## Save financial data
   - Save result table into 2 `.csv` files into the `output/` folder.
   - First one - profit_and_loss.csv with Revenue, EBIT, D&A, Total debt, Excess cash, Diluted shares.
   - Second one - cash_flow.csv with Cash flow from operations, Capex, Debt payment (net), Dividends.

## Currency conversion (Optional — only when reporting currency ≠ price currency)
   If a mismatch was detected between the reporting currency and the stock price currency (e.g. JPY reports but USD prices):
   - Run `python fx_rates.py FROM TO --year-end MONTH` using the company's fiscal year-end month.
     - Add `--spot-date YYYY-MM-DD` if a TTM row exists, where the date is the quarter-end balance sheet date (e.g. `--spot-date 2025-12-31` for a Q3 March-year-end company).
     - Example: `python fx_rates.py JPY USD --year-end 3 --spot-date 2025-12-31`
   - Use the resulting `output/fx_FROM_TO_FY<MMM>.csv` (columns: `average_rate`, `year_end_rate`) as follows:
     - **Income statement & cash flow items** (Revenue, EBIT, D&A, CFO, Capex, Debt payment, Dividends): multiply by the **average_rate** for the matching fiscal year.
     - **Balance sheet items** (Total debt, Excess cash): multiply by the **year_end_rate** for the matching fiscal year.
     - **TTM balance sheet**: use the spot rate returned by `--spot-date` (the quarter-end date rate).
     - **TTM income/CF**: use the average rate of the current in-progress fiscal year (the row marked with `*` in the FX table).
     - **Shares outstanding**: no conversion needed (unit count, not monetary).
   - Rename the original files to `profit_and_loss_<original_currency_lowercase>.csv` and `cash_flow_<original_currency_lowercase>.csv`.
   - Save two additional converted files: `profit_and_loss_<target_currency_lowercase>.csv` and `cash_flow_<target_currency_lowercase>.csv`.
   - All converted monetary values should be rounded to the nearest whole number (same unit as original, e.g. millions).
   - Run `python verify_fx.py` to verify the converted files are correct. Fix any reported mismatches before proceeding.

---

## How to use analyze_pdf.py

`analyze_pdf.py` extracts text from PDFs and saves it to `output/` as `.txt` files.
GitHub Copilot then reads those files and performs the analysis.

**Run**
1. Place annual report PDFs in the `REPORTS_FOLDER` folder
2. Run with `--folder` pointing to `REPORTS_FOLDER` to convert all PDFs, or pass specific filenames to convert only those:
   - `python analyze_pdf.py --folder "REPORTS_FOLDER"`
   - `python analyze_pdf.py --folder "REPORTS_FOLDER" report1.pdf report2.pdf`
3. Running the script takes about 1-2 minutes. Wait for it to finish. Do not run any other python commands while it's running.