"""
analyze_pdf.py
--------------
Extracts text from annual report PDFs in the reports/ folder and saves each
to a .txt file in the output/ folder, ready for analysis.

Usage:
    pip install pypdf
    python tools/analyze_pdf.py --folder "reports/"                          # convert all PDFs
    python tools/analyze_pdf.py --folder "reports/" report1.pdf report2.pdf  # convert specific files
    python tools/analyze_pdf.py --folder "reports/Apple" --output "output/Apple"
"""

import argparse
import sys
from pathlib import Path

import pypdf

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "output"


def extract_text(pdf_path: Path) -> str:
    reader = pypdf.PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def main():
    parser = argparse.ArgumentParser(description="Extract text from annual report PDFs.")
    parser.add_argument("--folder", required=True, help="Path to the folder containing PDF reports.")
    parser.add_argument("--output", default=str(OUTPUT_DIR), help="Path to the folder where extracted text files should be saved.")
    parser.add_argument("files", nargs="*", help="Specific PDF filenames to convert (optional).")
    args = parser.parse_args()

    reports_dir = Path(args.folder)
    if not reports_dir.is_dir():
        print(f"Folder not found: {reports_dir}")
        sys.exit(1)
    output_dir = Path(args.output)

    if args.files:
        pdf_files = []
        for name in args.files:
            p = reports_dir / name
            if not p.exists():
                print(f"File not found: {p}")
                sys.exit(1)
            pdf_files.append(p)
    else:
        pdf_files = sorted(reports_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {reports_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in pdf_files:
        print(f"Processing {pdf_path.name} ...")
        text = extract_text(pdf_path)
        out_path = output_dir / (pdf_path.stem + ".txt")
        out_path.write_text(text, encoding="utf-8")
        print(f"  -> {out_path} ({len(text):,} chars, {len(text.splitlines()):,} lines)")

    print(f"\nDone. Text files are in {output_dir} - proceed with analysis.")


if __name__ == "__main__":
    main()
