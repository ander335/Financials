import argparse
import csv
import sys
from pathlib import Path

from inspect_xlsm import cell_parts, num_to_col, read_shared_strings, read_sheet, read_workbook
import zipfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook")
    parser.add_argument("sheet")
    parser.add_argument("--min-row", type=int, default=1)
    parser.add_argument("--max-row", type=int, default=80)
    parser.add_argument("--min-col", type=int, default=1)
    parser.add_argument("--max-col", type=int, default=30)
    args = parser.parse_args()

    with zipfile.ZipFile(Path(args.workbook)) as zf:
        shared_strings = read_shared_strings(zf)
        sheets, _ = read_workbook(zf)
        sheet = next((s for s in sheets if s["name"].lower() == args.sheet.lower()), None)
        if sheet is None:
            raise SystemExit(f"Sheet not found: {args.sheet}")
        data = read_sheet(zf, sheet["path"], shared_strings)

    writer = csv.writer(sys.stdout)
    writer.writerow(["row"] + [num_to_col(c) for c in range(args.min_col, args.max_col + 1)])
    for row in range(args.min_row, args.max_row + 1):
        values = []
        has_data = False
        for col in range(args.min_col, args.max_col + 1):
            ref = f"{num_to_col(col)}{row}"
            cell = data["cells"].get(ref)
            value = ""
            if cell:
                formula = cell.get("formula")
                raw = cell.get("value")
                value = f"={formula}" if formula else raw
                if value not in (None, ""):
                    has_data = True
            values.append(value)
        if has_data:
            writer.writerow([row] + values)


if __name__ == "__main__":
    main()
