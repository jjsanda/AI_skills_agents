"""Tests for agentkit.diagrams (mermaid-cli is mocked out)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest

from agentkit import diagrams as dg


def test_mmdc_command_prefers_mmdc(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        dg.shutil, "which", lambda name: "/usr/bin/mmdc" if name == "mmdc" else None
    )
    assert dg._mmdc_command() == ["mmdc"]


def test_mmdc_command_npx_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dg.shutil, "which", lambda name: "/usr/bin/npx" if name == "npx" else None)
    assert dg._mmdc_command()[0] == "npx"


def test_mmdc_command_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dg.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError):
        dg._mmdc_command()


def test_render_all_no_sources(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError):
        dg.render_all(tmp_path, tmp_path / "out")


def test_render_diagram_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "a.mmd"
    source.write_text("graph TD; A-->B")
    output = tmp_path / "a.svg"
    monkeypatch.setattr(dg.shutil, "which", lambda name: "/x/mmdc" if name == "mmdc" else None)

    def fake_run(cmd: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        output.write_text("<svg/>")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(dg.subprocess, "run", fake_run)
    assert dg.render_diagram(source, output) == output
    assert output.is_file()


def test_render_diagram_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "a.mmd"
    source.write_text("nonsense")
    output = tmp_path / "a.svg"
    monkeypatch.setattr(dg.shutil, "which", lambda name: "/x/mmdc" if name == "mmdc" else None)
    monkeypatch.setattr(
        dg.subprocess,
        "run",
        lambda cmd, **_: subprocess.CompletedProcess(cmd, 1, "", "boom"),
    )
    with pytest.raises(RuntimeError, match="Failed to render"):
        dg.render_diagram(source, output)


def test_render_all_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "a.mmd").write_text("graph TD; A-->B")
    out_dir = tmp_path / "exported"

    def fake_render(source: Path, output: Path, **_: Any) -> Path:
        output.write_text("x")
        return output

    monkeypatch.setattr(dg, "render_diagram", fake_render)
    written = dg.render_all(tmp_path, out_dir, formats=("svg", "png"))
    assert len(written) == 2
    assert {p.suffix for p in written} == {".svg", ".png"}
