"""Render Mermaid ``.mmd`` sources to SVG and PNG via ``@mermaid-js/mermaid-cli``.

Uses the ``mmdc`` binary if on ``PATH``, otherwise falls back to ``npx``. A
Puppeteer config (``docs/diagrams/puppeteer-config.json``) is passed when
present so headless Chromium runs with ``--no-sandbox`` in CI/Linux. Any broken
diagram raises loudly.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

DIAGRAMS_DIR = Path("docs/diagrams")
EXPORT_DIR = DIAGRAMS_DIR / "exported"
DEFAULT_FORMATS: tuple[str, ...] = ("svg", "png")


def _mmdc_command() -> list[str]:
    """Return the base command for invoking mermaid-cli, or raise if unavailable."""
    if shutil.which("mmdc"):
        return ["mmdc"]
    if shutil.which("npx"):
        return ["npx", "-y", "-p", "@mermaid-js/mermaid-cli", "mmdc"]
    raise RuntimeError(
        "mermaid-cli not found. Install Node.js and run "
        "`npm install -g @mermaid-js/mermaid-cli`, or ensure `npx` is available."
    )


def render_diagram(
    source: Path,
    output: Path,
    *,
    puppeteer_config: Path | None = None,
    background: str = "white",
) -> Path:
    """Render a single ``.mmd`` ``source`` to ``output`` (format by extension).

    Raises ``RuntimeError`` if mermaid-cli fails or the output is not produced.

    Example:
        >>> render_diagram(
        ...     Path("docs/diagrams/00-how-it-works.mmd"), Path("out.svg")
        ... )  # doctest: +SKIP
        PosixPath('out.svg')
    """
    command = [*_mmdc_command(), "-i", str(source), "-o", str(output), "-b", background]
    if puppeteer_config and puppeteer_config.is_file():
        command += ["-p", str(puppeteer_config)]
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Failed to render {source} -> {output}:\n{proc.stdout}\n{proc.stderr}".strip()
        )
    if not output.is_file():
        raise RuntimeError(f"mermaid-cli reported success but {output} was not created")
    return output


def render_all(
    diagrams_dir: Path | str = DIAGRAMS_DIR,
    export_dir: Path | str = EXPORT_DIR,
    *,
    formats: tuple[str, ...] = DEFAULT_FORMATS,
) -> list[Path]:
    """Render every ``*.mmd`` under ``diagrams_dir`` to each format in ``formats``.

    Returns the list of written files. Raises if there are no sources or any
    diagram fails to render.

    Example:
        >>> render_all()  # doctest: +SKIP
        [PosixPath('docs/diagrams/exported/00-how-it-works.svg'), ...]
    """
    src_dir = Path(diagrams_dir)
    out_dir = Path(export_dir)
    sources = sorted(src_dir.glob("*.mmd"))
    if not sources:
        raise RuntimeError(f"No .mmd files found in {src_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    puppeteer_config = src_dir / "puppeteer-config.json"

    written: list[Path] = []
    for source in sources:
        for fmt in formats:
            output = out_dir / f"{source.stem}.{fmt}"
            render_diagram(source, output, puppeteer_config=puppeteer_config)
            written.append(output)
    return written
