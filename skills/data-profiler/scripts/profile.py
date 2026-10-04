#!/usr/bin/env python3
"""Profile a CSV into a Markdown data-quality report and an optional PNG chart.

Examples:
    python profile.py data.csv                      # Markdown report to stdout
    python profile.py data.csv --chart profile.png  # + null-rate bar chart

Heavy dependencies (``pandas``, ``matplotlib``) are imported lazily so that
``--help`` works without the ``skills`` extra installed.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only
    import pandas as pd


def build_markdown(df: pd.DataFrame, name: str) -> str:
    """Build a deterministic Markdown data-quality report for ``df``.

    Example:
        >>> import pandas as pd  # doctest: +SKIP
        >>> build_markdown(pd.read_csv("examples/sample.csv"), "sample.csv")  # doctest: +SKIP
        '# Data Quality Report: sample.csv\\n...'
    """
    rows = len(df)
    cols = len(df.columns)
    lines = [
        f"# Data Quality Report: {name}",
        "",
        f"- Rows: {rows}",
        f"- Columns: {cols}",
        "",
        "## Columns",
        "",
        "| column | dtype | non-null | null rate | unique | top value |",
        "|---|---|---|---|---|---|",
    ]
    for column in df.columns:
        series = df[column]
        non_null = int(series.notna().sum())
        null_rate = float(series.isna().mean())
        unique = int(series.nunique(dropna=True))
        present = series.dropna()
        top = present.value_counts().index[0] if not present.empty else ""
        lines.append(
            f"| {column} | {series.dtype} | {non_null} | {null_rate:.0%} | {unique} | {top} |"
        )
    return "\n".join(lines) + "\n"


def build_chart(df: pd.DataFrame, out_path: Path | str) -> None:
    """Write a null-rate-by-column bar chart (PNG) to ``out_path``."""
    import matplotlib

    matplotlib.use("Agg")  # headless backend; no display needed
    import matplotlib.pyplot as plt

    null_rates = df.isna().mean().sort_values(ascending=False)
    figure, axes = plt.subplots(figsize=(6, 4))
    axes.bar([str(c) for c in null_rates.index], list(null_rates.to_numpy()), color="#4C72B0")
    axes.set_ylim(0, 1)
    axes.set_ylabel("null rate")
    axes.set_title("Null rate by column")
    axes.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(out_path, dpi=100)
    plt.close(figure)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Profile a CSV into a Markdown data-quality report and an optional chart.",
    )
    parser.add_argument("csv", type=Path, help="Path to the input CSV file")
    parser.add_argument(
        "-o", "--output", type=Path, help="Write the Markdown report here instead of stdout"
    )
    parser.add_argument("--chart", type=Path, help="Write a PNG null-rate chart to this path")
    args = parser.parse_args(argv)

    if not args.csv.is_file():
        parser.error(f"no such file: {args.csv}")

    import pandas as pd

    # pandas ships no type stubs, so this stays loosely typed (Any).
    frame: Any = pd.read_csv(args.csv)
    report = build_markdown(frame, args.csv.name)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(report)

    if args.chart:
        build_chart(frame, args.chart)
        print(f"Wrote {args.chart}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
