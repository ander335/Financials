#!/usr/bin/env python
"""
verify_fx.py — Verify that converted currency CSV files are correctly calculated
from the original currency CSVs using the FX rates file.

Auto-detects the FX file and currency pair from filenames in the output directory.

Usage: python verify_fx.py [output_dir]
Default output_dir: ./output

Exits with code 0 if all values match, 1 if any mismatches are found.
"""

import csv
import glob
import os
import re
import sys


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_files(output_dir):
    """Locate FX file and original/converted CSV pairs; infer currency codes."""
    fx_files = glob.glob(os.path.join(output_dir, "fx_*_*_FY*.csv"))
    if not fx_files:
        raise FileNotFoundError(f"No FX file (fx_<FROM>_<TO>_FY<MMM>.csv) found in: {output_dir}")
    if len(fx_files) > 1:
        print(f"Multiple FX files found, using: {os.path.basename(fx_files[0])}")
    fx_file = fx_files[0]

    m = re.match(r"fx_([A-Z]+)_([A-Z]+)_FY", os.path.basename(fx_file))
    if not m:
        raise ValueError(f"Cannot parse currency codes from FX filename: {fx_file}")
    from_cur = m.group(1).lower()
    to_cur   = m.group(2).lower()

    def require(path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required file not found: {path}")
        return path

    return (
        fx_file,
        require(os.path.join(output_dir, f"profit_and_loss_{from_cur}.csv")),
        require(os.path.join(output_dir, f"cash_flow_{from_cur}.csv")),
        require(os.path.join(output_dir, f"profit_and_loss_{to_cur}.csv")),
        require(os.path.join(output_dir, f"cash_flow_{to_cur}.csv")),
        from_cur.upper(),
        to_cur.upper(),
    )


def load_fx(fx_file):
    """
    Parse the FX file.

    Returns:
        fx        — dict  {fiscal_year_int -> {"avg": float, "ye": float}}
        spot_rate — float  year_end_rate from the spot:YYYY-MM-DD row
        ttm_avg   — float  average_rate of the highest (in-progress) fiscal year
    """
    rows = load_csv(fx_file)
    fx = {}
    spot_rate = None

    for row in rows:
        fy  = row["fiscal_year"].strip()
        avg = float(row["average_rate"])
        ye  = float(row["year_end_rate"])

        if fy.startswith("spot:"):
            spot_rate = ye
        else:
            try:
                fx[int(fy)] = {"avg": avg, "ye": ye}
            except ValueError:
                pass  # skip unexpected rows

    ttm_avg = fx[max(fx)]["avg"] if fx else None
    return fx, spot_rate, ttm_avg


# Columns in profit_and_loss that use the average FX rate (income statement items)
PNL_AVG_COLS  = ["revenue", "ebit", "da"]
# Columns in profit_and_loss that use the year-end FX rate (balance sheet items)
PNL_YE_COLS   = ["total_debt", "excess_cash"]
# Columns that require no conversion
PNL_SKIP_COLS = ["diluted_shares", "year"]

# All cash flow columns use the average rate
CF_AVG_COLS   = ["cfo", "capex", "debt_payment_net", "dividends"]


def fy_number(year_str):
    """Return the 4-digit fiscal year from strings like 'FY2025'; None for 'TTM'."""
    m = re.search(r"(\d{4})", year_str)
    return int(m.group(1)) if m else None


def check(warnings, label, orig_val_str, rate, conv_val_str):
    """Compare round(orig * rate) against the value stored in the converted file."""
    try:
        orig = float(orig_val_str)
        conv = int(float(conv_val_str))
    except (ValueError, TypeError):
        warnings.append(f"  WARNING [{label}]: cannot parse values — orig={orig_val_str!r}, conv={conv_val_str!r}")
        return
    expected = round(orig * rate)
    if expected != conv:
        warnings.append(
            f"  WARNING [{label}]: {orig:,.0f} × {rate} = {expected:,}  but file has {conv:,}  (diff={conv - expected:+,})"
        )


def verify_table(name, orig_rows, conv_rows, fx, spot_rate, ttm_avg,
                 avg_cols, ye_cols, warnings):
    conv_idx = {r["year"]: r for r in conv_rows}

    for orig in orig_rows:
        yr       = orig["year"]
        is_ttm   = (yr == "TTM")
        conv     = conv_idx.get(yr)

        if conv is None:
            warnings.append(f"  WARNING [{yr}]: row missing in converted {name}")
            continue

        fy_num = fy_number(yr)

        if is_ttm:
            avg_rate = ttm_avg
            ye_rate  = spot_rate
        else:
            if fy_num not in fx:
                warnings.append(f"  WARNING [{yr}]: FY{fy_num} not found in FX file")
                continue
            avg_rate = fx[fy_num]["avg"]
            ye_rate  = fx[fy_num]["ye"]

        for col in avg_cols:
            if col in orig and col in conv:
                check(warnings, f"{yr} {col}", orig[col], avg_rate, conv[col])

        for col in ye_cols:
            if col in orig and col in conv:
                check(warnings, f"{yr} {col}", orig[col], ye_rate, conv[col])


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./output"

    fx_file, pnl_orig_path, cf_orig_path, pnl_conv_path, cf_conv_path, from_cur, to_cur = find_files(output_dir)

    print(f"FX file:        {os.path.basename(fx_file)}")
    print(f"Original P&L:   {os.path.basename(pnl_orig_path)}")
    print(f"Converted P&L:  {os.path.basename(pnl_conv_path)}")
    print(f"Original CF:    {os.path.basename(cf_orig_path)}")
    print(f"Converted CF:   {os.path.basename(cf_conv_path)}")
    print()

    fx, spot_rate, ttm_avg = load_fx(fx_file)

    warnings = []

    print(f"=== Verifying profit_and_loss_{to_cur.lower()}.csv ===")
    verify_table(
        f"profit_and_loss_{to_cur.lower()}.csv",
        load_csv(pnl_orig_path),
        load_csv(pnl_conv_path),
        fx, spot_rate, ttm_avg,
        avg_cols=PNL_AVG_COLS,
        ye_cols=PNL_YE_COLS,
        warnings=warnings,
    )

    print(f"=== Verifying cash_flow_{to_cur.lower()}.csv ===")
    verify_table(
        f"cash_flow_{to_cur.lower()}.csv",
        load_csv(cf_orig_path),
        load_csv(cf_conv_path),
        fx, spot_rate, ttm_avg,
        avg_cols=CF_AVG_COLS,
        ye_cols=[],
        warnings=warnings,
    )

    if warnings:
        print(f"\n*** {len(warnings)} MISMATCH(ES) FOUND ***")
        for w in warnings:
            print(w)
        sys.exit(1)
    else:
        print(f"\nAll values verified correctly. No mismatches found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
