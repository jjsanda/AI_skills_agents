"""Tests for the pdf-extract skill script."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = SKILL_DIR / "scripts" / "extract.py"
SAMPLE_PDF = REPO_ROOT / "examples" / "sample.pdf"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("pdf_extract_script", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extract_text_contains_sample_text() -> None:
    module = _load()
    text = module.extract_text(SAMPLE_PDF)
    assert "Hello PDF" in text


def test_extract_markdown_via_main(capsys) -> None:  # type: ignore[no-untyped-def]
    module = _load()
    exit_code = module.main([str(SAMPLE_PDF)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "## Page 1" in captured.out
    assert "Hello PDF" in captured.out


def test_cli_help_runs_without_heavy_deps() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert "Extract" in result.stdout
