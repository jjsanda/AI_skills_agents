"""Tests for the web-research skill script (offline path)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "search.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("web_research_script", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manual_flow_without_key(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("WEB_RESEARCH_API_KEY", raising=False)
    module = _load()
    exit_code = module.main(["renewable energy storage 2030"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Manual research workflow" in out
    assert "renewable energy storage 2030" in out


def test_cli_help_runs() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert "Research a topic" in result.stdout
