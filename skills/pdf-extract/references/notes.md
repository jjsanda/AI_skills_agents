# pdf-extract — reference notes

Deep detail loaded on demand (kept out of `SKILL.md` per progressive disclosure).

## Library choice

- `pdfplumber` (https://github.com/jsvine/pdfplumber) wraps `pdfminer.six` and
  exposes both text and table extraction with a clean API. It is pure-Python and
  has no system dependencies, which keeps the skill portable.

## Table detection caveats

- `page.extract_tables()` detects tables from **ruled lines** by default. PDFs
  that lay tables out with whitespace alignment (no drawn borders) often yield
  no tables. For those, fall back to text extraction and parse columns by
  position, or pass custom `table_settings` (e.g. `"vertical_strategy": "text"`).
- Multi-page tables are returned as separate tables (one per page); stitch them
  together downstream if needed.

## Scanned PDFs

- If `extract_text()` returns empty strings for every page, the PDF is almost
  certainly image-only (scanned). Text extraction cannot help there — OCR
  (e.g. Tesseract) is required. Surface this clearly instead of returning "".

## Determinism & safety

- The script reads only the input file and writes only to the chosen output. It
  makes no network calls and runs no shell commands — safe to audit and run in
  CI.
