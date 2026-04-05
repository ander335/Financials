Analyze annual reports found in the `reports/` subfolder of this project.

Follow the process in CLAUDE.md:
1. List all files in the `reports/` folder and identify the company (ticker, name, fiscal year end) from the filenames or document contents
2. Read the most recent financial report and locate the consolidated statements according to the `CLAUDE.md` file.
   - Familiarize with their exact naming and structure since they will appear in a similar way in older reports.
   - Find how and where `Shares outstanding (shares in issue)` is reported for this company. Use the same pattern to find this information in the other reports.
   - For `Debt payment` analyze the debt structure, what debt the company has and how movements are reported. Use the same pattern in the other reports.
3. Before proceeding with the other reports:
   - Show all the consolidated statements form the most recent report to the user as tables.
   - Show the extracted finantial data from the most recent report.
   - Provide comments how the data was extraced for this comany.
   - Ask for approval to proceed with the other reports.
4. For each annual report found, extract the following according to `CLAUDE.md` file:
   - Output data that is marked as `###` three sharps under `# Financial report structure` structure.
   - Rows should represent years, columns - metcirs.
   - The most recent year should appear on the bottom.
5. Note any data gaps, restatements, or fiscal year changes

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
