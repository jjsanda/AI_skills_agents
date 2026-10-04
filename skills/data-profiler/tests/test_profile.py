"""Tests for the data-profiler skill script."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = SKILL_DIR / "scripts" / "profile.py"
SAMPLE_CSV = REPO_ROOT / "examples" / "sample.csv"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("data_profiler_script", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_markdown_report_has_expected_fields() -> None:
    module = _load()
    import pandas as pd

    frame = pd.read_csv(SAMPLE_CSV)
    report = module.build_markdown(frame, "sample.csv")
    assert "# Data Quality Report: sample.csv" in report
    assert "Rows: 5" in report
    assert "null rate" in report.lower()
    assert "name" in report


def test_chart_is_created(tmp_path: Path) -> None:
    module = _load()
    import pandas as pd

    frame = pd.read_csv(SAMPLE_CSV)
    out = tmp_path / "chart.png"
    module.build_chart(frame, out)
    assert out.is_file()
    assert out.stat().st_size > 0


def test_cli_help_runs_without_heavy_deps() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert "Profile a CSV" in result.stdout
