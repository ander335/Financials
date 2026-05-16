import argparse
from pathlib import Path

from download_company_logo import download_bytes, download_company_logo, normalize_to_transparent_png
from xlsm_bricks import (
    add_scaled_png,
    apply_currency_number_formats,
    assert_same_number_format,
    clear_columns,
    copy_row_styles,
    detect_single_file,
    latest_number,
    open_workbook,
    parse_iso_date,
    parse_number,
    parse_year,
    populate_result_prices,
    read_csv_rows,
    save_workbook,
    write_columnar_rows,
    write_formulas,
    write_two_column_series,
)


def detect_price_file(csv_folder, ticker):
    if ticker:
        return Path(csv_folder) / f"{ticker}_stock_data.csv"
    return detect_single_file(csv_folder, "*_stock_data.csv")


def avg_year_price_formula(row):
    if row == 12:
        return "=Result!C2"
    return (
        f'=AVERAGEIFS($V:$V, $U:$U, ">" & DATE($A{row} - IF($V$15 <= 10, 1, 0), '
        f'MOD($V$15 + 1, 12), 1), $U:$U, "<=" & DATE($A{row} + '
        f'IF(MOD($V$15, 12) = 0, 1, 0), MOD($V$15 + 1, 12), 1), $V:$V, "<>")'
    )


def populate_p_and_l(ws, rows):
    written = write_columnar_rows(
        ws,
        rows,
        start_row=2,
        limit=11,
        columns=[
            ("A", ("Year", parse_year)),
            ("B", ("Revenue", parse_number)),
            ("C", ("EBIT", parse_number)),
            ("D", ("D&A", parse_number)),
            ("H", ("Total debt", parse_number)),
            ("I", ("Excess cash", parse_number)),
            ("O", ("Diluted shares", parse_number)),
        ],
    )
    for row in range(2, 2 + written):
        ws[f"E{row}"] = None
    write_formulas(
        ws,
        start_row=2,
        row_count=written,
        formulas_by_col={
            "F": lambda row: f"=C{row}+D{row}+E{row}",
            "G": lambda row: None if row == 2 else f"=(F{row}-F{row - 1})/F{row - 1}",
            "J": lambda row: f"=O{row}*P{row}",
            "K": lambda row: f"=J{row}+H{row}-I{row}",
            "L": lambda row: f"=K{row}/F{row}",
            "M": lambda row: f"=H{row}/F{row}",
            "P": avg_year_price_formula,
        },
    )
    copy_row_styles(ws, source_row=11, target_row=12, first_col=1, last_col=16)
    return written


def populate_cash_flow(ws, rows):
    written = write_columnar_rows(
        ws,
        rows,
        start_row=2,
        limit=11,
        columns=[
            ("A", ("Year", parse_year)),
            ("B", ("Cash flow from operations", parse_number)),
            ("C", ("Capex", parse_number)),
            ("D", ("Debt payment (net)", parse_number)),
            ("G", ("Dividends", parse_number)),
        ],
    )
    write_formulas(
        ws,
        start_row=2,
        row_count=written,
        formulas_by_col={
            "F": lambda row: f"=B{row}+C{row}+D{row}+E{row}",
            "H": lambda row: f"=-G{row}/F{row}",
            "I": lambda row: f"='P&L'!O{row}",
            "J": lambda row: f"=F{row}/I{row}",
            "K": lambda row: f"='P&L'!P{row}",
            "L": lambda row: f"=J{row}/K{row}",
            "M": lambda row: f"=-G{row}/I{row}/K{row}",
        },
    )
    copy_row_styles(ws, source_row=11, target_row=12, first_col=1, last_col=13)
    return written


def populate_prices(ws, rows):
    clear_columns(ws, columns=["U", "V"], start_row=18, end_row=1000)
    written = write_two_column_series(
        ws,
        rows,
        start_row=18,
        first_col="U",
        second_col="V",
        first_spec=("Date", parse_iso_date),
        second_spec=("Close", parse_number),
    )
    for row in range(18, 18 + written):
        ws[f"U{row}"].number_format = "m/d/yyyy"
    return written


def validate_key_formats(wb):
    cf = wb["Cash flow"]
    assert_same_number_format(cf, "B11", ["B12", "C12", "D12", "E12", "F12", "G12"])
    assert_same_number_format(cf, "L11", ["L12", "M12"])
    pl = wb["P&L"]
    assert_same_number_format(pl, "B11", ["B12", "C12", "D12", "F12", "H12", "I12", "J12", "K12"])


def resolve_logo_path(args, csv_folder):
    if args.skip_logo:
        return None, None

    if args.logo_path:
        return Path(args.logo_path), "local file"

    company = args.company or csv_folder.name
    output_path = Path(args.logo_output) if args.logo_output else csv_folder / "company_logo.png"

    if args.logo_url:
        raw = download_bytes(args.logo_url)
        return normalize_to_transparent_png(raw, output_path), args.logo_url

    logo_path, title, source_url = download_company_logo(company, output_path)
    return logo_path, f"{title} ({source_url})"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template")
    parser.add_argument("--output", default="output/filled_Template_2025.xlsm")
    parser.add_argument("--csv-folder", default="output")
    parser.add_argument("--ticker", default=None)
    parser.add_argument("--fiscal-year-end-month", type=int, default=12)
    parser.add_argument("--company", default=None)
    parser.add_argument("--logo-path", default=None)
    parser.add_argument("--logo-url", default=None)
    parser.add_argument("--logo-output", default=None)
    parser.add_argument("--logo-anchor", default="E21")
    parser.add_argument("--logo-max-width", type=int, default=1214)
    parser.add_argument("--logo-max-height", type=int, default=221)
    parser.add_argument("--skip-logo", action="store_true")
    parser.add_argument("--display-currency", default=None)
    parser.add_argument("--template-currency", default="USD")
    args = parser.parse_args()

    csv_folder = Path(args.csv_folder)
    pl_rows = read_csv_rows(csv_folder / "profit_and_loss.csv")
    cf_rows = read_csv_rows(csv_folder / "cash_flow.csv")
    price_path = detect_price_file(csv_folder, args.ticker)
    price_rows = read_csv_rows(price_path)

    wb = open_workbook(args.template, keep_vba=True)
    pl_written = populate_p_and_l(wb["P&L"], pl_rows)
    cf_written = populate_cash_flow(wb["Cash flow"], cf_rows)
    prices_written = populate_prices(wb["P&L"], price_rows)
    wb["P&L"]["V15"] = args.fiscal_year_end_month
    current_price = latest_number(price_rows, "Date", "Close")
    price_band = populate_result_prices(wb["Result"], current_price)
    logo_path, logo_source = resolve_logo_path(args, csv_folder)
    logo_size = None
    if logo_path:
        logo_size = add_scaled_png(
            wb["Result"],
            logo_path,
            anchor_cell=args.logo_anchor,
            max_width=args.logo_max_width,
            max_height=args.logo_max_height,
        )
    currency_changes = []
    if args.display_currency:
        currency_changes = apply_currency_number_formats(
            wb,
            target_currency=args.display_currency,
            source_currency=args.template_currency,
        )
    validate_key_formats(wb)
    output_path = save_workbook(wb, args.output, validate=True, keep_vba=True)

    print(f"Template: {args.template}")
    print(f"Output: {output_path}")
    print(f"P&L rows written: {pl_written}")
    print(f"Cash-flow rows written: {cf_written}")
    print(f"Price rows written: {prices_written} from {price_path}")
    print(f"Fiscal year-end month: {args.fiscal_year_end_month}")
    print(f"Current price set in Result!C2: {current_price}")
    print(f"Price sensitivity values set in Result!K2:O2: {', '.join(str(value) for value in price_band)}")
    if logo_path:
        print(f"Logo inserted in Result!{args.logo_anchor}: {logo_path} ({logo_size[0]}x{logo_size[1]})")
        print(f"Logo source: {logo_source}")
    else:
        print("Logo insertion skipped.")
    if args.display_currency:
        print(
            f"Currency display formats changed from {args.template_currency.upper()} "
            f"to {args.display_currency.upper()}: {len(currency_changes)} cells"
        )


if __name__ == "__main__":
    main()
