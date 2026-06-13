# Excel file structure
- Describes the result `.xlsm` files formatting and rules.

## Sheets

- The workbook has three primary sheets: **P&L**, **Cash flow**, and **Result**. ROE and IRR map are secondary and not subject to these formatting rules unless explicitly noted.

## General rules

### Formatting
- All cells in a given metric column use the same number format, currency symbol, decimal places, alignment, color, and font across all data, summary, and forecast rows.
- Percentage metrics (growth rates, CAGRs, margins, yields) are formatted as percentage throughout — not as raw decimals.
- Label text for summary rows (e.g., "Yeild:", "Stock Price:") must appear in exactly one column. Duplicate labels in adjacent columns are not permitted.

### Years column
- If TTM or interim data is available, its row label must show only the year number — no "TTM" or period suffix — and must be aligned and formatted identically to the annual rows.

### Row structure (per data sheet)

Rows appear in this fixed order:

1. **Data rows** — one row per completed fiscal year, oldest to newest. All completed fiscal years must be contiguous with no gaps.
2. **TTM/interim row** (if present) — immediately after the last completed annual row.
3. **Blank row** — one blank row after the TTM/interim row (or after the last annual row if no TTM exists).
4. **Summary row** — one row combining long-term CAGR and average depending on the metric (see below). Spans from the earliest to the latest completed fiscal year. Interim and TTM rows are excluded from this range.
5. **Recent CAGR row** (optional) — one row showing a shorter-period CAGR, typically a 3–5 year window ending at the latest completed fiscal year. Excludes the TTM/interim row. When exceptional values would distort the window, choose an endpoint that mitigates the spike.
6. **Blank row** — one blank row after the summary/CAGR rows, before any forecast or valuation section.

### Summary row: CAGR vs. average
The summary row uses **long-term CAGR** for metrics where the growth rate over time is the meaningful measure:
- P&L: Revenue, EBIT, EBITDA, D&A, Debt, Market Cap, Share count
- Cash flow: CFO, CAPEX, Distributed Cash, FCFE, FCFE/share

The summary row uses **average** for metrics where the long-term level or ratio is more meaningful than its growth rate:
- P&L: EV/EBITDA multiple, Debt/EBITDA
- Cash flow: DC/FCF ratio, FCFE Yield, Div Yield, EV/Equity

### Forecast section
- Forecasts are anchored to the latest completed annual period, not to the TTM row.
- When a TTM or interim value is available for the first forecast year, that year's growth assumption is calibrated so the forecast is consistent with the TTM/interim value.
- The year column and the primary metric column form a chain: each row's values reference the row immediately above. No row may hardcode an absolute year or base value that bypasses this chain.
- The year sequence across forecast rows must be contiguous.
- The first forecast row is the exception to the chain rule: its primary metric cell references the last completed annual period's metric value (×(1+growth_rate)), and its year cell hardcodes the first forecast year. All subsequent rows reference the row immediately above.
- Growth column: the first forecast row uses a TTM-calibrated value (hardcoded to keep the forecast consistent with the TTM period). The second and all subsequent forecast rows use the long-term CAGR reference. The growth column must never chain from the first row — doing so would propagate the TTM adjustment spike into subsequent years.

### Workbook conformance
- The output workbook must contain no circular formula references.

## P&L
