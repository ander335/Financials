# Data Sources and Evidence Hierarchy

## Source-selection framework

Sources were prioritized in this order:

1. U.S. government or central-bank data for Treasury yields and federal debt.
2. The ETF issuer for portfolio characteristics and distributions.
3. A specialist ETF database only as a secondary cross-check.
4. The user-supplied image only as a visual reference; no numerical observations were extracted from it.

All rates are stored in the workbooks as decimal numbers and formatted as percentages.

## Treasury yields

| Use | Series or page | Provider | Workbook treatment |
|---|---|---|---|
| Latest 20Y and 30Y CMT observations | [Daily Treasury par yield curve rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026) | U.S. Department of the Treasury | The 2026-08-27 observations, 5.18% and 5.19%, were appended because the FRED bulk file then ended on 2026-08-26. |
| Daily 20Y history | [DGS20](https://fred.stlouisfed.org/series/DGS20) | Federal Reserve Bank of St. Louis; underlying Federal Reserve H.15 release | Primary scenario driver. |
| Daily 30Y history | [DGS30](https://fred.stlouisfed.org/series/DGS30) | Federal Reserve Bank of St. Louis; underlying Federal Reserve H.15 release | Context and chart comparison, not the scenario driver. |

The 30-year workbook uses 7,504 daily 20Y observations from 1996-08-27 through 2026-08-27. The 20-year workbook uses 5,004 observations from the first available business-day observation on 2006-08-28 through 2026-08-27; its nominal start date is 2006-08-27.

## 30Y-series anomaly treatment

The official 30Y constant-maturity series has a historical gap. In the workbook, 2002-02-19 through 2006-02-08 is explicitly labeled `Theoretical proxy`; official DGS30 observations resume on 2006-02-09.

This treatment prevents missing values from being plotted as zero, which had caused the vertical chart spikes seen in an earlier version. The proxy is retained only to provide chart continuity and is not used to set the mid-case or best-case targets. It must not be described as an official 30Y CMT observation.

The 20-year-history chart starts in August 2006, after the official 30Y series resumed, so that chart does not include the discontinued interval.

## ETF data

| Use | Source | Role |
|---|---|---|
| Yield to maturity, effective duration, maturity, coupon, trailing distribution yield, TER, benchmark, and distribution frequency | [iShares product page](https://www.ishares.com/uk/individual/en/products/272124/ishares-usd-treasury-bond-20-yr-ucits-etf?siteEntryPassthrough=true&switchLocale=y) | Primary ETF source. The modeled distribution yield is 4.88%. |
| Dividend-yield cross-check | [justETF profile for IE00BSKRJZ44](https://www.justetf.com/en/etf-profile.html?isin=IE00BSKRJZ44) | Secondary cross-check only. Its 4.83% figure is not used in model cash flows. |

The issuer snapshot is preferred because duration and portfolio characteristics must refer to the actual ETF rather than to a generic long-bond index.

## Gross federal debt to GDP

Gross federal debt as a percentage of GDP comes from [FRED series GFDEGDQ188S](https://fred.stlouisfed.org/series/GFDEGDQ188S), sourced from the U.S. Office of Management and Budget and distributed by the Federal Reserve Bank of St. Louis.

The series is quarterly and seasonally adjusted. For monthly chart alignment, the latest reported quarterly value is carried forward until the next official release. This affects only chart presentation; it does not create new quarterly observations or interpolate the economic series.

## Data-quality controls

The workbooks include a `Sources & Checks` sheet that reconciles:

- current Treasury yields against the official snapshot;
- historical means, percentiles, and observation counts against independent calculations;
- duration-based price gains against the scenario formula;
- all six scenario XIRRs against an independent dated-cash-flow solution.

The final model status is `OK` only when every high-severity check passes.
