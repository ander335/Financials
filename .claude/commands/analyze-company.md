Analyze annual reports found in the `reports/` subfolder of this project.

Follow the process in CLAUDE.md:
1. List all files in the `reports/` folder and identify the company (ticker, name, fiscal year end) from the filenames or document contents
2. Read the most recent finantial report and locate the consolidated statements according to the `CLAUDE.md` file.
   - Familiarize with their exact naming and structure since they will appear similar way in older reports.
2. For each annual report found, extract the following according to `CLAUDE.md` file:
   - Revenue (Income Statement)
   - EBIT / Operating Income (Income Statement)
   - Depreciation & Amortization (Cash Flow Statement)
   - Any significant one-off adjustments
   - Total debt
   - Excess cash (Balance Sheet)
   - Diluted shares outstanding
5. Output a markdown table using the columns defined in CLAUDE.md
6. Note any data gaps, restatements, or fiscal year changes

Be precise with numbers — use the exact figures from filings, not rounded estimates. Flag any line items that required judgment calls.

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
2. Run: `python analyze_pdf.py`
3. Text files appear in `output/` — then run `/analyze-company` for analysis
