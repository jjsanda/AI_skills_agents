---
name: data-profiler
description: Hand it a CSV (or any delimited table) and get back a Markdown data-quality report plus a null-rate chart — row and column counts, dtypes, null rates, cardinality, and top values — handy for sizing up a dataset before analysis or cleaning.
license: Apache-2.0
compatibility: Requires Python 3.11+ with pandas and matplotlib (install agentkit with the `skills` extra).
---

# Data Profiler

A quick quality snapshot of a tabular dataset before you commit to analyzing it.

## Usage

Print a Markdown report to stdout and save a null-rate chart:

```bash
python scripts/profile.py data.csv --chart profile.png
```

Write the report to a file as well:

```bash
python scripts/profile.py data.csv --output report.md --chart profile.png
```

Run `python scripts/profile.py --help` for all options.

## What the report contains

For each column: dtype, non-null count, null rate, unique count, and the most
frequent value. The chart is a null-rate bar chart across columns.

## When to use

Reach for this when handed a CSV (or any delimited table) and you need a
data-quality snapshot before modeling or cleaning: how many rows and columns
there are, which columns have missing values, their types, cardinality, and
common values.

## Notes

- Output is deterministic for a fixed input, so it is safe to assert on in tests
  and to diff across dataset versions.
- The script reads only the input CSV and writes only the report and chart you
  ask for. It makes no network calls.
