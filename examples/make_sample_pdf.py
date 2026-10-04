#!/usr/bin/env python3
"""Generate a minimal, valid sample PDF for the pdf-extract skill demo and tests.

Pure standard library: builds a minimal one-page PDF with selectable text using
the standard Helvetica font and a correct cross-reference table. Run it to
(re)create ``examples/sample.pdf``:

    python examples/make_sample_pdf.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_LINES = [
    "agentkit sample document",
    "",
    "Hello PDF. This file is generated for the pdf-extract skill.",
    "",
    "name    age    city",
    "Alice   30     Prague",
    "Bob     25     Brno",
]


def build_pdf() -> bytes:
    """Return the bytes of a minimal, valid single-page PDF with the sample text."""
    ops = ["BT", "/F1 16 Tf", "72 720 Td", "18 TL"]
    for index, line in enumerate(_LINES):
        escaped = line.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
        if index:
            ops.append("T*")
        ops.append(f"({escaped}) Tj")
    ops.append("ET")
    content = "\n".join(ops).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"

    xref_pos = len(out)
    size = len(objects) + 1
    out += f"xref\n0 {size}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += b"trailer\n" + f"<< /Size {size} /Root 1 0 R >>\n".encode()
    out += b"startxref\n" + f"{xref_pos}\n".encode() + b"%%EOF\n"
    return bytes(out)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    dest = Path(args[0]) if args else Path(__file__).resolve().parent / "sample.pdf"
    dest.write_bytes(build_pdf())
    print(f"Wrote {dest} ({dest.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
