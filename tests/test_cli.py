"""Tests for the agentkit CLI (via Typer's CliRunner)."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

import agentkit.cli as cli_mod
from agentkit.cli import app

REPO = Path(__file__).resolve().parents[1]
SKILLS = str(REPO / "skills")

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "agentkit" in result.output


def test_list_skills() -> None:
    result = runner.invoke(app, ["list", "--skills-dir", SKILLS])
    assert result.exit_code == 0
    assert "pdf-extract" in result.output
    assert "data-profiler" in result.output


def test_list_empty(tmp_path: Path) -> None:
    result = runner.invoke(app, ["list", "--skills-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No skills" in result.output


def test_validate_ok() -> None:
    result = runner.invoke(app, ["validate", "--skills-dir", SKILLS])
    assert result.exit_code == 0
    assert "valid" in result.output


def test_validate_empty_dir(tmp_path: Path) -> None:
    result = runner.invoke(app, ["validate", "--skills-dir", str(tmp_path)])
    assert result.exit_code == 1


def test_validate_bad_skill(tmp_path: Path) -> None:
    bad = tmp_path / "BadSkill"
    bad.mkdir()
    (bad / "SKILL.md").write_text(
        "---\nname: BadSkill\ndescription: x\n---\nbody\n", encoding="utf-8"
    )
    result = runner.invoke(app, ["validate", "--skills-dir", str(tmp_path)])
    assert result.exit_code == 1
    assert "✗" in result.output


def test_run_mock() -> None:
    result = runner.invoke(app, ["run", "do a thing", "--mock", "--skills-dir", SKILLS])
    assert result.exit_code == 0
    assert "Mode: mock" in result.output


def test_run_explicit_skill() -> None:
    result = runner.invoke(
        app, ["run", "x", "--skill", "web-research", "--mock", "--skills-dir", SKILLS]
    )
    assert result.exit_code == 0
    assert "web-research" in result.output


def test_run_unknown_skill() -> None:
    result = runner.invoke(app, ["run", "x", "--skill", "nope", "--mock", "--skills-dir", SKILLS])
    assert result.exit_code == 1
    assert "Unknown skill" in result.output


def test_run_no_skills(tmp_path: Path) -> None:
    result = runner.invoke(app, ["run", "x", "--mock", "--skills-dir", str(tmp_path)])
    assert result.exit_code == 1


def test_diagrams(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_mod, "render_all", lambda _: [Path("a.svg"), Path("a.png")])
    result = runner.invoke(app, ["diagrams"])
    assert result.exit_code == 0
    assert "Rendered 2" in result.output
