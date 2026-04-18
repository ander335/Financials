"""
fx_rates.py — Download annual average and year-end exchange rates.

Source: Frankfurter API (api.frankfurter.dev) — free, no API key required.
Data backed by ECB and other central banks.

Usage:
    python fx_rates.py FROM TO [--years N] [--year-end MONTH] [--spot-date DATE]

Arguments:
    FROM              Base currency ISO code (e.g. JPY)
    TO                Quote currency ISO code (e.g. USD)
    --years N         Number of fiscal years to retrieve (default: 12)
    --year-end M      Fiscal year-end month, 1-12 (default: 12 = December)
    --spot-date DATE  Extra spot rate for a specific date (YYYY-MM-DD), e.g. Q3 balance sheet date.
                      Looks up the rate on that date (or the nearest preceding trading day).
                      Appended to the output CSV as a separate row with fiscal_year="spot".

Examples:
    python fx_rates.py JPY USD
    python fx_rates.py JPY USD --year-end 3                        # March year-end (Toyota, Sony…)
    python fx_rates.py JPY USD --year-end 3 --spot-date 2025-12-31 # + Q3 balance sheet rate
    python fx_rates.py GBP USD --year-end 6                        # June year-end
    python fx_rates.py EUR JPY --years 15

Output:
    output/fx_FROM_TO[_FYMMM].csv  with columns: fiscal_year, period, average_rate, year_end_rate
    fiscal_year = calendar year in which the fiscal year ends
    year_end_rate = rate on the last available trading day of the fiscal year
    spot row: fiscal_year="spot:<DATE>", period=DATE, average_rate=N/A (0), year_end_rate=spot rate
"""

import argparse
import calendar
import csv
import json
import sys
import urllib.request
import urllib.error
from datetime import date

MONTH_ABBR = {
    1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN",
    7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC",
}


def fiscal_periods(first_fy: int, last_fy: int, year_end_month: int) -> list[tuple[int, str, str, str]]:
    """
    Return a list of (fiscal_year_label, period_str, start_date, end_date).
    fiscal_year_label: calendar year in which the FY ends.
    """
    periods = []
    for fy in range(first_fy, last_fy + 1):
        if year_end_month == 12:
            start = f"{fy}-01-01"
            end = f"{fy}-12-31"
            period_str = str(fy)
        else:
            start_month = year_end_month + 1
            start_year = fy - 1
            last_day = calendar.monthrange(fy, year_end_month)[1]
            start = f"{start_year}-{start_month:02d}-01"
            end = f"{fy}-{year_end_month:02d}-{last_day:02d}"
            period_str = f"{start_year}-{MONTH_ABBR[start_month]} / {fy}-{MONTH_ABBR[year_end_month]}"
        periods.append((fy, period_str, start, end))
    return periods


def fetch_daily_rates(from_ccy: str, to_ccy: str, fetch_start: str, fetch_end: str) -> dict:
    url = (
        f"https://api.frankfurter.dev/v1/{fetch_start}..{fetch_end}"
        f"?base={from_ccy}&symbols={to_ccy}"
    )
    print(f"Fetching: {url}")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; fx-rates-script/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def aggregate(daily_data: dict, to_ccy: str, periods: list) -> list[dict]:
    # Flat dict: date_str -> rate
    rates: dict[str, float] = {
        d: v[to_ccy] for d, v in daily_data["rates"].items()
    }
    today_str = date.today().isoformat()
    rows = []

    for fy, period_str, start, end in periods:
        effective_end = min(end, today_str)
        period_rates = {d: r for d, r in rates.items() if start <= d <= effective_end}

        if not period_rates:
            continue

        avg = sum(period_rates.values()) / len(period_rates)
        last_date = max(period_rates)
        year_end_rate = period_rates[last_date]
        partial = effective_end < end  # FY not yet complete

        rows.append({
            "fiscal_year": f"{fy}*" if partial else str(fy),
            "period": period_str,
            "average_rate": round(avg, 6),
            "year_end_rate": round(year_end_rate, 6),
        })

    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Download annual FX rates (average + year-end) for a currency pair."
    )
    parser.add_argument("from_ccy", metavar="FROM", help="Base currency (e.g. JPY)")
    parser.add_argument("to_ccy", metavar="TO", help="Quote currency (e.g. USD)")
    parser.add_argument("--years", type=int, default=12, help="Number of fiscal years (default: 12)")
    parser.add_argument(
        "--year-end", type=int, default=12, dest="year_end", metavar="MONTH",
        help="Fiscal year-end month 1-12 (default: 12 = December)"
    )
    parser.add_argument(
        "--spot-date", dest="spot_date", metavar="DATE", default=None,
        help="Extra spot rate for a specific date YYYY-MM-DD (e.g. Q3 balance sheet date)"
    )
    args = parser.parse_args()

    from_ccy = args.from_ccy.upper()
    to_ccy = args.to_ccy.upper()
    year_end = args.year_end
    years = args.years
    spot_date = args.spot_date

    if not 1 <= year_end <= 12:
        print("Error: --year-end must be between 1 and 12", file=sys.stderr)
        sys.exit(1)

    today = date.today()

    # Determine last complete (or in-progress) fiscal year
    # A FY ending in month M of year Y is complete once today > last day of M/Y
    last_complete_fy = today.year if today.month > year_end else today.year - 1
    # Include the partial current FY if it has started
    last_fy = today.year if today.month > year_end else today.year

    first_fy = last_complete_fy - years + 1  # gives `years` complete FYs

    periods = fiscal_periods(first_fy, last_fy, year_end)

    # Fetch start: beginning of the first fiscal period
    fetch_start = periods[0][2]  # start date of first period
    # If a spot date is requested and it's earlier than the first FY start, extend fetch range
    if spot_date and spot_date < fetch_start:
        fetch_start = spot_date
    fetch_end = today.isoformat()

    year_end_label = MONTH_ABBR[year_end]
    print(f"Currency pair : {from_ccy}/{to_ccy}")
    print(f"Fiscal year end: {year_end_label} ({year_end:02d})")
    print(f"Fiscal years  : FY{first_fy} to FY{last_fy}")

    data = fetch_daily_rates(from_ccy, to_ccy, fetch_start, fetch_end)
    rows = aggregate(data, to_ccy, periods)

    # Spot-date lookup: find the rate on or before the requested date
    spot_row = None
    if spot_date:
        all_rates: dict[str, float] = {
            d: v[to_ccy] for d, v in data["rates"].items()
        }
        candidates = sorted(d for d in all_rates if d <= spot_date)
        if candidates:
            actual_date = candidates[-1]
            spot_rate = all_rates[actual_date]
            note = f" (nearest trading day: {actual_date})" if actual_date != spot_date else ""
            spot_row = {
                "fiscal_year": f"spot:{spot_date}",
                "period": actual_date,
                "average_rate": 0,
                "year_end_rate": round(spot_rate, 6),
            }
            print(f"\nSpot rate on {spot_date}{note}: {spot_rate:.6f}")
        else:
            print(f"\nWarning: no rate data available on or before {spot_date}", file=sys.stderr)

    suffix = f"_FY{year_end_label}" if year_end != 12 else ""
    output_path = f"output/fx_{from_ccy}_{to_ccy}{suffix}.csv"

    all_rows = rows + ([spot_row] if spot_row else [])
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fiscal_year", "period", "average_rate", "year_end_rate"])
        writer.writeheader()
        writer.writerows(all_rows)

    # Console table
    print(f"\n{from_ccy}/{to_ccy} — Fiscal year ending {year_end_label}")
    print(f"{'FY':<6}  {'Period':<30}  {'Avg Rate':>12}  {'Year-End':>12}")
    print("-" * 68)
    for r in rows:
        print(f"{r['fiscal_year']:<6}  {r['period']:<30}  {r['average_rate']:>12.6f}  {r['year_end_rate']:>12.6f}")

    if any(r["fiscal_year"].endswith("*") for r in rows):
        print("  * partial fiscal year (in progress)")

    print(f"\nSaved -> {output_path}")
    print(f"Rows  : {len(rows)}")


if __name__ == "__main__":
    main()
