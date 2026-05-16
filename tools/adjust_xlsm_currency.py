import argparse

from xlsm_bricks import apply_currency_number_formats, open_workbook, save_workbook


def repair_malformed_currency_formats(wb):
    repairs = []
    replacements = {
        "[\u20ac\u00a3-809]": "[$\u00a3-809]",
        "[\u20ac\u20bd-419]": "[$\u20bd-419]",
        "[\u20ac\u00a5-804]": "[$\u00a5-804]",
        "[\u20ac\u20ac-2]": '"\u20ac"',
        "[$\u20ac-2]": '"\u20ac"',
    }
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                old_format = cell.number_format
                new_format = old_format
                for bad, good in replacements.items():
                    new_format = new_format.replace(bad, good)
                if new_format != old_format:
                    cell.number_format = new_format
                    repairs.append(
                        {
                            "sheet": ws.title,
                            "cell": cell.coordinate,
                            "old_format": old_format,
                            "new_format": new_format,
                        }
                    )
    return repairs


def main():
    parser = argparse.ArgumentParser(description="Change only currency tokens in XLSM number formats.")
    parser.add_argument("workbook", help="Workbook to update.")
    parser.add_argument("target_currency", help="Target currency code, such as EUR.")
    parser.add_argument("--source-currency", default="USD", help="Currency format to replace. Defaults to USD.")
    parser.add_argument("--output", default=None, help="Optional output workbook. Defaults to updating in place.")
    parser.add_argument("--sheet", action="append", dest="sheets", help="Sheet to update. Can be passed multiple times.")
    parser.add_argument("--audit", action="store_true", help="List matching formats without saving changes.")
    parser.add_argument("--repair-malformed", action="store_true", help="Repair malformed currency format tokens from earlier conversions.")
    args = parser.parse_args()

    wb = open_workbook(args.workbook, keep_vba=True)
    repairs = repair_malformed_currency_formats(wb) if args.repair_malformed else []
    changes = apply_currency_number_formats(
        wb,
        target_currency=args.target_currency,
        source_currency=args.source_currency,
        sheets=args.sheets,
    )

    print(f"Workbook: {args.workbook}")
    print(f"Source currency: {args.source_currency.upper()}")
    print(f"Target currency: {args.target_currency.upper()}")
    if args.repair_malformed:
        print(f"Malformed currency formats repaired: {len(repairs)}")
    print(f"Currency formats matched: {len(changes)}")
    printed = repairs + changes
    for change in printed[:50]:
        print(
            f"{change['sheet']}!{change['cell']}: "
            f"{ascii(change['old_format'])} -> {ascii(change['new_format'])}"
        )
    if len(printed) > 50:
        print(f"... {len(printed) - 50} more")

    if args.audit:
        wb.close()
        print("Audit only; workbook not saved.")
        return

    output_path = args.output or args.workbook
    saved_path = save_workbook(wb, output_path, validate=True, keep_vba=True)
    print(f"Saved: {saved_path}")


if __name__ == "__main__":
    main()
