"""
analyze_pdf.py
--------------
Extracts text from annual report PDFs in the reports/ folder and saves each
to a .txt file in the output/ folder, ready for analysis.

Usage:
    pip install pypdf
    python analyze_pdf.py
"""

import sys
from pathlib import Path

import pypdf

REPORTS_DIR = Path(__file__).parent / "reports"
OUTPUT_DIR = Path(__file__).parent / "output"


def extract_text(pdf_path: Path) -> str:
    reader = pypdf.PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def main():
    pdf_files = sorted(REPORTS_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {REPORTS_DIR}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)

    for pdf_path in pdf_files:
        print(f"Processing {pdf_path.name} ...")
        text = extract_text(pdf_path)
        out_path = OUTPUT_DIR / (pdf_path.stem + ".txt")
        out_path.write_text(text, encoding="utf-8")
        print(f"  -> {out_path} ({len(text):,} chars, {len(text.splitlines()):,} lines)")

    print("\nDone. Text files are in output/ — proceed with analysis.")


if __name__ == "__main__":
    main()
