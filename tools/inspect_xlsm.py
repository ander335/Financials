import argparse
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def col_to_num(col):
    total = 0
    for ch in col:
        total = total * 26 + ord(ch.upper()) - 64
    return total


def num_to_col(num):
    out = ""
    while num:
        num, rem = divmod(num - 1, 26)
        out = chr(65 + rem) + out
    return out


def cell_parts(ref):
    match = re.match(r"([A-Z]+)([0-9]+)", ref)
    if not match:
        return None, None
    return col_to_num(match.group(1)), int(match.group(2))


def load_xml(zf, name):
    return ET.fromstring(zf.read(name))


def text_of(node):
    if node is None:
        return None
    return "".join(node.itertext())


def read_shared_strings(zf):
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = load_xml(zf, "xl/sharedStrings.xml")
    return [text_of(si) for si in root.findall("main:si", NS)]


def read_workbook(zf):
    workbook = load_xml(zf, "xl/workbook.xml")
    rels = load_xml(zf, "xl/_rels/workbook.xml.rels")
    rel_by_id = {}
    for rel in rels:
        rel_by_id[rel.attrib["Id"]] = rel.attrib["Target"]

    sheets = []
    for sheet in workbook.findall("main:sheets/main:sheet", NS):
        rid = sheet.attrib[f"{{{NS['rel']}}}id"]
        target = rel_by_id[rid]
        if not target.startswith("/"):
            target = "xl/" + target
        else:
            target = target.lstrip("/")
        sheets.append(
            {
                "name": sheet.attrib["name"],
                "sheet_id": sheet.attrib["sheetId"],
                "state": sheet.attrib.get("state", "visible"),
                "path": target,
            }
        )

    names = []
    for defined_name in workbook.findall("main:definedNames/main:definedName", NS):
        names.append(
            {
                "name": defined_name.attrib.get("name"),
                "local_sheet_id": defined_name.attrib.get("localSheetId"),
                "hidden": defined_name.attrib.get("hidden"),
                "text": text_of(defined_name),
            }
        )
    return sheets, names


def read_sheet(zf, sheet_path, shared_strings):
    root = load_xml(zf, sheet_path)
    dimension = root.find("main:dimension", NS)
    merged = [m.attrib["ref"] for m in root.findall("main:mergeCells/main:mergeCell", NS)]
    cells = {}
    formulas = {}
    for c in root.findall(".//main:sheetData/main:row/main:c", NS):
        ref = c.attrib["r"]
        formula = text_of(c.find("main:f", NS))
        value = text_of(c.find("main:v", NS))
        inline = text_of(c.find("main:is", NS))
        typ = c.attrib.get("t")
        if typ == "s" and value is not None:
            try:
                value = shared_strings[int(value)]
            except (ValueError, IndexError):
                pass
        elif typ == "inlineStr":
            value = inline
        if formula is not None:
            formulas[ref] = formula
        if value not in (None, "") or formula is not None:
            cells[ref] = {"value": value, "formula": formula, "type": typ}
    return {
        "dimension": dimension.attrib.get("ref") if dimension is not None else None,
        "merged": merged,
        "cells": cells,
        "formulas": formulas,
    }


def find_label_context(cells, labels):
    by_row = defaultdict(dict)
    for ref, data in cells.items():
        col, row = cell_parts(ref)
        if col and row:
            by_row[row][col] = data

    hits = []
    for row, cols in by_row.items():
        for col, data in cols.items():
            value = data.get("value")
            if value is None:
                continue
            value_text = str(value).strip()
            normalized = value_text.lower()
            if any(label in normalized for label in labels):
                context = []
                for ctx_col in range(max(1, col - 3), col + 8):
                    ref = f"{num_to_col(ctx_col)}{row}"
                    item = cells.get(ref)
                    if item:
                        context.append({"cell": ref, "value": item.get("value"), "formula": item.get("formula")})
                hits.append({"label_cell": f"{num_to_col(col)}{row}", "label": value_text, "row_context": context})
    return hits


def summarize_sheet(sheet, sheet_data):
    cells = sheet_data["cells"]
    values = [ref for ref, data in cells.items() if data.get("value") not in (None, "")]
    formulas = list(sheet_data["formulas"].keys())
    return {
        "name": sheet["name"],
        "state": sheet["state"],
        "dimension": sheet_data["dimension"],
        "non_empty_cells": len(cells),
        "value_cells": len(values),
        "formula_cells": len(formulas),
        "merged_ranges": sheet_data["merged"][:20],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook")
    parser.add_argument("--json-output", default="output/xlsm_inspection.json")
    args = parser.parse_args()

    workbook_path = Path(args.workbook)
    labels = [
        "revenue",
        "ebit",
        "depre",
        "amort",
        "ebitda",
        "debt",
        "cash",
        "share",
        "price",
        "date",
        "close",
        "fiscal",
        "year",
        "capex",
        "dividend",
        "cash flow",
    ]

    with zipfile.ZipFile(workbook_path) as zf:
        shared_strings = read_shared_strings(zf)
        sheets, names = read_workbook(zf)
        report = {
            "workbook": str(workbook_path),
            "has_vba": "xl/vbaProject.bin" in zf.namelist(),
            "sheets": [],
            "defined_names": names,
            "label_hits": {},
        }
        for sheet in sheets:
            data = read_sheet(zf, sheet["path"], shared_strings)
            report["sheets"].append(summarize_sheet(sheet, data))
            hits = find_label_context(data["cells"], labels)
            if hits:
                report["label_hits"][sheet["name"]] = hits[:200]

    output_path = Path(args.json_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Workbook: {workbook_path}")
    print(f"Has VBA: {report['has_vba']}")
    print("Sheets:")
    for sheet in report["sheets"]:
        print(
            f"- {sheet['name']} [{sheet['state']}], "
            f"dimension={sheet['dimension']}, "
            f"values={sheet['value_cells']}, formulas={sheet['formula_cells']}"
        )
    print(f"Defined names: {len(names)}")
    print(f"Label-hit sheets: {', '.join(report['label_hits']) or 'none'}")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
