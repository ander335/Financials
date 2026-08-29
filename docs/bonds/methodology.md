# Analysis Framework and Methodology

## 1. Historical-window framework

The model has two versions so the effect of history selection can be evaluated explicitly:

- the 30-year version uses daily 20Y CMT observations from 1996-08-27 through 2026-08-27;
- the 20-year version uses daily observations from 2006-08-28 through 2026-08-27.

For each version, two historical targets are calculated from the 20Y CMT series:

- **Mid-case:** arithmetic mean of all valid daily observations in the selected window.
- **Best-case:** inclusive 25th percentile of the same observations.

This is a mean-reversion scenario framework. It does not estimate the probability or timing of either target.

## 2. Duration-based ETF price sensitivity

The ETF price effect is estimated with the first-order effective-duration approximation:

```text
Yield change = target 20Y yield - current 20Y yield
Estimated ETF price change = -effective duration × yield change
Terminal ETF value = initial investment × (1 + estimated ETF price change)
```

The effective duration is 14.86. Yield changes are decimal changes, so a decline from 5.18% to 4.13% is approximately `-0.0105`, not `-1.05`.

For example, the 30-year-history mid-case is approximately:

```text
-14.86 × (4.1298% - 5.18%) = 15.61%
```

The duration estimate is lower than a simple “yield decline multiplied by remaining maturity” intuition because effective duration already represents the portfolio's first-order percentage sensitivity. It excludes convexity, which would normally add positive curvature when yields fall.

## 3. Income framework

The model uses the issuer's 4.88% trailing distribution yield and assumes:

- two equal cash distributions per year;
- distributions are calculated on the initial USD 10,000 investment;
- distributions remain constant;
- cash is not reinvested.

The semiannual modeled distribution is therefore:

```text
USD 10,000 × 4.88% ÷ 2 = USD 244
```

This convention isolates cash income from price appreciation. It is deliberately simpler than forecasting future ETF distributions as portfolio yields and holdings change.

## 4. Return framework

For each 3-, 5-, and 10-year horizon, the dated cash-flow stream contains:

1. the initial USD 10,000 outflow;
2. semiannual USD 244 cash distributions;
3. terminal sale proceeds equal to the duration-adjusted ETF value.

Annualized return is calculated with `XIRR`, using the actual cash-flow dates. Dividends and terminal value are not double-counted.

The workbook also presents:

```text
Total distributions = initial investment × distribution yield × years
Total profit = price gain in USD + total distributions
Total return = total profit ÷ initial investment
```

Total return is a cumulative, non-annualized figure. XIRR is the annualized result and is the better metric for comparing holding periods.

## 5. Debt-to-GDP chart framework

Treasury yields use the chart's left axis. Gross federal debt/GDP is shown against a labeled right-hand scale of 0%–160%.

The workbook implements the right-side display by scaling debt/GDP to the 0%–8% yield-axis range:

```text
Chart value = gross debt/GDP × 5%
```

Thus 160% debt/GDP maps to 8% on the plotted scale. The right-hand labels translate the plotted value back to the economic debt/GDP ratio. This is a visualization device only; debt/GDP does not enter the ETF return calculation.

Quarterly debt observations are carried forward between official releases to align them with monthly yield points.

## 6. Model-control framework

The workbook uses four layers of control:

- **Source controls:** current yields and ETF metrics are tied to dated source records.
- **Statistical controls:** means, inclusive percentiles, and counts are independently recalculated.
- **Valuation controls:** duration-based price gains are independently reconciled.
- **Cash-flow controls:** each XIRR is compared with an independent numerical solution.

Formula-error scans check for `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, and `#N/A`. The workbooks are also rendered sheet by sheet for visual review of charts, labels, and table layout.

## 7. Interpretation and limitations

The main limitations are:

- first-order duration ignores convexity;
- parallel yield sensitivity is used even though the curve can change shape;
- ETF duration, holdings, and distributions are held constant;
- no roll-down, portfolio turnover, taxes, FX, fees beyond the observed fund metrics, trading costs, or bid-ask spreads are modeled;
- the selected historical window materially affects the target yield and result;
- reaching a target earlier or later changes realized XIRR;
- market prices can deviate from NAV and from the simplified duration estimate.

Results should therefore be read as internally consistent sensitivities under stated assumptions, not as expected returns.
