# Analyze annual reports found in the `reports/` subfolder of this project.

# General
- Be precise with numbers — use the exact figures from filings, not rounded estimates. Flag any line items that required judgment calls.

# Steps
## Read `CLAUDE.md` file for context

## List all files in the `reports/` folder
   - List files in the `output/`, for the `.pdf` reports that are not yet converted to text use `analyze_pdf.py`. Convert only the files that are not yeat present in the `output/` folder, provide them as the script arguments.
   - Do not analyze reports at this stage.
   - Triage the reports by their name. There could be annual reports and 1 quater report (optional).
   - Ananlyze how much financial data is presented. Example:
      - For reports 2025, 2021, ..., 2015 total available period will be 12 years (2025 - 2015 + 2)
      - This value can be rederenced as `AVAILABLE_PERIOD`

## Read only the most recent financial report
   - Extract company name and ticker, primary listing exchange, main reporting currency.
   - Locate the consolidated statements according to the `CLAUDE.md` file. Familiarize with their exact naming and structure since they will appear in a similar way in older reports.
   - Find how and where `Shares outstanding (shares in issue)` is reported for this company. Use the same pattern to find this information in the other reports.
   - For `Debt payment` analyze the debt structure, what debt the company has and how movements are reported. Use the same pattern in the other reports.

## User confirmation (Required). Important to request the approval before reading other reports
   - Show all the consolidated statements form the most recent report to the user as tables.
   - Show the extracted finantial data from the most recent report.
   - Provide comments how the data was extraced for this comany.
   - Ask for approval to proceed with the other reports.

## Read other reports. Aggregate info in the following format according to the `CLAUDE.md` file:
   - Output data that is marked as `###` three sharps under `# Financial report structure` structure.
   - Rows should represent years, columns - metcirs.
   - The most recent year should appear on the bottom.

## Aggregate latest quater report (Optional, if the report was found)
   - Add corresponding year to the result table. Mark the year with `TTM` in the table.
   - Apply the following rules: 
   - `Shares outstanding` should be taken from the quater report.
   - All balance sheet data should be taken from the quater report.
   - For the `Consolidated Income statement` and `Consolidated statement of cash flow` use the TTM approach to get the numbers that can be compared with the previous year:
      - Locate statements that include the most fiscal data. Example:
         - For 3Q report - Look for `Nine Months Ended`
         - For 2Q or interim report - Look for `Fix Months Ended` or `Half-year Ended`
      - Calculate `the difference` with the same period previous year. Example:
         - Revenue Nine Months Ended Dec 31, 2025 - 13,031.7
         - Revenue Nine Months Ended Dec 31, 2024 - 11,651.2
         - Calculate `the difference` +1380.5 = (13,031.7 - 11,651.2)
      - Result value is the previous financial year value with `the difference` applied.

## Note any data gaps, restatements, or fiscal year changes

## Save financial data
   - Save result table into 2 `.csv` files into the `output/` folder.
   - First one - profit_and_loss.csv with Revenue, EBIT, D&A, Total debt, Excess cash, Diluted shares.
   - First one - cash_flow.csv with Cash flow from operations, Capex, Debt payment (net).

## Extract historical prices data
   - Run `historical_prices.py` with the company ticker and the number of years `AVAILABLE_PERIOD` + 1 as arguments.
   - Example: `python historical_prices.py AAPL 13` (where 13 = `AVAILABLE_PERIOD` years of data + 1 for margin)
   - **Important**: The script outputs the `Currency: <currency>`, compare it with the reporting currency. If it's not the same, warn the user about it.

---

## How to use analyze_pdf.py

`analyze_pdf.py` extracts text from PDFs and saves it to `output/` as `.txt` files.
Claude Code then reads those files and performs the analysis.

**Setup (one-time)**
```bash
pip install pypdf
```

**Run**
1. Place annual report PDFs in the `reports/` folder
2. Run: `python analyze_pdf.py` to convert all PDFs, or pass specific filenames to convert only those:
   - `python analyze_pdf.py report1.pdf report2.pdf`
