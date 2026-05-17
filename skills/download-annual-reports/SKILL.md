---
name: download-annual-reports
description: Download annual reports, 10-Ks, 20-Fs, and equivalent yearly filings from a public company's investor relations, annual reports, SEC filings, or results web page. Use when the user asks to collect, download, get, save, or prepare company annual report files.
---

# Download Annual Reports

Use this skill to find and save public company annual reports before financial analysis.

## Required Reading
1. Read `docs/context_variables.md` first, then read
   `docs/context_variables.local.md` when present and prefer its
   `REPORTS_FOLDER` as the destination folder for downloaded reports.

## Inputs
- Company name, ticker, or investor relations URL from the user.
- If the user provides only a company name or ticker, find the official investor relations page before downloading.
- Download reports into a company-named subfolder under `REPORTS_FOLDER`, such as `REPORTS_FOLDER\<Company-Name>\`.

## Source Rules
- Use only the company's official investor relations website.
- Do not use regulator pages, third-party mirrors, search-result document caches, or financial data aggregators as report sources.
- If the investor relations website does not provide the requested annual reports, stop and tell the user what was available there.

## Workflow

### Step 1: Resolve Investor Relations Source And Destination
- Identify the company name to use for the destination subfolder.
- Create or use `REPORTS_FOLDER\<Company-Name>\`.
- Locate the company's official investor relations website.
- Use only report links found on that investor relations website.

### Step 2: Select Reports
- Always prefer Form 10-K or Form 20-F files when they are available on the investor relations website.
- If a Form 10-K or Form 20-F is available for a fiscal year, download that filing and do not download the annual report for the same fiscal year.
- Use annual reports, integrated reports, yearly results, or annual filings only when no Form 10-K or Form 20-F is available for that fiscal year.
- Prefer PDF files when both PDF and web versions are available.
- Download annual source files in two-year steps for all report types because each annual report normally covers at least two years of financial information. For example, starting from 2025, download 2025, 2023, 2021, and continue backward until at least 10 years are covered when available.
- Always prefer Form 10-Q for the most recent interim period when it is available on the investor relations website.
- If Form 10-Q is not available, download the most recent quarterly, half-year, or interim report when available on the investor relations website.

### Step 3: Download And Name Files
- Save each report into `REPORTS_FOLDER\<Company-Name>\`.
- Use stable filenames that include company name or ticker, fiscal year, and report type when known.
- Preserve the original file extension.
- Do not overwrite an existing file unless it is clearly the same report; otherwise add a short distinguishing suffix.

### Step 4: Verify And Report
- List the downloaded files with their fiscal years and source URLs.
- Note any expected years that were not available on the investor relations website.
- State the destination folder path.
- Do not begin financial extraction unless the user asks for analysis next.
