# Financials — Annual Report Analysis

# General
- Extract key financial metrics from public company annual reports (10-K, 20-F or equivalent) at least for the last 10 years and compile them into a structured table.
- Reports are normally presented in sequence every 2 years (2025, 2023, etc.). `Consolidated Balance sheet` is normally disclosed for 2 years in the report. Other statements, might be disclosed for 3 years. Consider only latest 2.

# Financial report structure
- The following statements normally appear together in the financial report
- `Consolidated Statement of Comprehensive Income` does not contain significant information and can be skipped from analysis.

## Consolidated Balance sheet
### Total debt. Consists of:
- Includes short term debt, current portion of long term debt (Current/short term liabilities section)
- Long term debt and capital leases (Long term liabilities)

### Excess cash. Consists of:
- Short term investments only. Cash and cash equivalents shouldn't be considered here (Current/short term assets section)


## Consolidated Income statement
### Revenue
- It should be total revenue from different business segments and services.
### Operating income (EBIT)
- Total revenue - total operation costs. It shouldn't include interest income/expense nor provision for income tax.


## Consolidated statement of cash flow
### Depreciation and Amortization
- They can be split into 2 different rows, in that case sum it up.

### Cash flow from operations
### Capex
- Normally appears as `Purchases of property, plant and equipment` (Cash flow from investing activities). Negative number.
### Debt payment
- It should include principal payment of debt - proceeds, repayments, issuance, etc. for both short term debt and long term debt.
### Dividends paid
- Dividends paid to the shareholders. Negative number.

## Other information
### Shares outstanding (shares in issue)
- Normally appears as `Diluted weighted-average number of common shares outstanding`
- It can be either found in `Consolidated Income statement`
- Or in a separate report section `Earnings per share`. Can also appear as `Loss per share` in case there is no profit for the company.
- Or it can be a separate table that displays shares outstanding over years.
- Report the number in millions.