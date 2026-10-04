---
name: pdf-extract
description: Pull text and tables out of PDFs into clean Markdown or CSV. Handy for statements, invoices, reports, scanned documents, or any PDF whose contents you need downstream; it flags image-only PDFs instead of returning empty text.
license: Apache-2.0
compatibility: Requires Python 3.11+ and the pdfplumber package (install agentkit with the `skills` extra).
---

# PDF Extract

Turn a PDF into clean, structured text you can use downstream.

## Usage

The bundled script prints extracted text as Markdown by default:

```bash
python scripts/extract.py path/to/file.pdf
```

Extract tables to CSV instead:

```bash
python scripts/extract.py path/to/file.pdf --format csv --output tables.csv
```

Run `python scripts/extract.py --help` for all options. Two common cases:

- "Extract the text from this PDF and summarize it": run with the default
  `--format md`, then summarize the Markdown.
- "Pull the tables out of this bank statement into a spreadsheet": run with
  `--format csv --output statement.csv`.

## When to use

Whenever a task involves reading a PDF: extracting body text, pulling tables
into CSV, or converting a report into Markdown for summarization.

## Notes

- Prefer the bundled script over re-deriving extraction logic. It is
  deterministic, tested, and side-effect-free: it only reads the input file and
  makes no network calls.
- Text extraction uses `pdfplumber` (built on `pdfminer.six`). Table detection
  needs ruled lines to be reliable; see `references/notes.md` for caveats.
- Scanned or image-only PDFs have no embedded text. Say so and note that OCR
  would be required instead of returning empty output silently.
