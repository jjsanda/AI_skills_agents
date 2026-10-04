#!/usr/bin/env python3
"""Extract text and tables from a PDF into Markdown or CSV.

Examples:
    python extract.py input.pdf                       # Markdown text to stdout
    python extract.py input.pdf --format csv -o t.csv # tables as CSV to a file

The heavy dependency (``pdfplumber``) is imported lazily inside the functions so
that ``--help`` works even when the ``skills`` extra is not installed.
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path


def extract_text(pdf_path: Path | str) -> str:
    """Return all page text from ``pdf_path`` as Markdown (one section per page).

    Example:
        >>> extract_text("examples/sample.pdf")  # doctest: +SKIP
        '## Page 1\\n\\nHello PDF...'
    """
    import pdfplumber

    parts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            parts.append(f"## Page {index}\n\n{text}".rstrip())
    return "\n\n".join(parts).strip() + "\n"


def extract_tables(pdf_path: Path | str) -> list[list[list[str | None]]]:
    """Return every detected table as a list of rows of cells."""
    import pdfplumber

    tables: list[list[list[str | None]]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables.extend(page.extract_tables())
    return tables


def tables_to_csv(tables: list[list[list[str | None]]]) -> str:
    """Serialize extracted tables to CSV (blank line between tables)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    for index, table in enumerate(tables):
        if index:
            writer.writerow([])
        for row in table:
            writer.writerow(["" if cell is None else cell for cell in row])
    return buffer.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract text or tables from a PDF into Markdown or CSV.",
    )
    parser.add_argument("pdf", type=Path, help="Path to the input PDF file")
    parser.add_argument(
        "--format",
        choices=["md", "csv"],
        default="md",
        help="Output format: 'md' for page text (default), 'csv' for tables",
    )
    parser.add_argument("-o", "--output", type=Path, help="Write to this file instead of stdout")
    args = parser.parse_args(argv)

    if not args.pdf.is_file():
        parser.error(f"no such file: {args.pdf}")

    if args.format == "md":
        output = extract_text(args.pdf)
    else:
        output = tables_to_csv(extract_tables(args.pdf))

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
