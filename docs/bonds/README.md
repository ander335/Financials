# Long-Term U.S. Treasury ETF Analysis

## Purpose

This folder documents the long-duration U.S. Treasury ETF scenario analysis built for ISIN `IE00BSKRJZ44` (iShares $ Treasury Bond 20+yr UCITS ETF). The model evaluates potential cash returns if the 20-year U.S. Treasury constant-maturity yield moves from its current level toward a historical reference level.

The analysis is a scenario framework, not a price forecast or investment recommendation.

## Workbook versions

| Workbook | Historical window used for scenario statistics | Main chart window |
|---|---:|---:|
| `Long_Treasury_ETF_IRR_Analysis_with_Debt_GDP.xlsx` | Trailing 30 years | August 1996–August 2026 |
| `Long_Treasury_ETF_IRR_Analysis_20Y_History_with_Debt_GDP.xlsx` | Trailing 20 years | August 2006–August 2026 |

Both workbooks are stored under `outputs/01a046b9-7252-7120-80a4-284d914650b5/`. The 20-year workbook is an additional file; it does not replace the 30-year version.

## Snapshot assumptions

| Input | Value | Date or treatment |
|---|---:|---|
| Current 20Y Treasury CMT | 5.18% | 2026-08-27 |
| Current 30Y Treasury CMT | 5.19% | 2026-08-27 |
| ETF trailing distribution yield | 4.88% | iShares snapshot, 2026-08-21 |
| ETF effective duration | 14.86 | iShares snapshot |
| Initial investment | USD 10,000 | Model assumption |
| Distribution frequency | Semiannual | Cash distributions are not reinvested |
| Holding periods | 3, 5, and 10 years | Terminal sale at each horizon |

## Historical targets and scenario results

| History window | 20Y CMT mean | 20Y CMT 25th percentile | Mid-case price gain | Best-case price gain |
|---|---:|---:|---:|---:|
| 30 years | 4.1298% | 2.8075% | 15.61% | 35.26% |
| 20 years | 3.3840% | 2.5500% | 26.69% | 39.08% |

The lower 20-year-history mean produces a larger modeled yield decline and therefore a larger duration-based price gain than the 30-year-history mean.

For the 20-year-history workbook, annualized XIRRs are:

| Case | 3 years | 5 years | 10 years |
|---|---:|---:|---:|
| Mid-case | 12.86% | 9.41% | 6.90% |
| Best-case | 16.18% | 11.25% | 7.70% |

## Documentation map

- [Data sources](data_sources.md) explains source selection, dates, and anomaly treatment.
- [Methodology](methodology.md) explains the scenario, valuation, income, XIRR, chart, and validation frameworks.
- [Shared Node setup](node_setup.md) explains the computer-level runtime installed outside the repository and how to reproduce or update it.

## Important limitations

The model excludes convexity, yield-curve roll-down, portfolio turnover, changing distributions, taxes, foreign-exchange effects, transaction costs, and bid-ask spreads. The ETF does not hold a single 20-year bond, so its realized NAV response can differ from the first-order duration estimate.
