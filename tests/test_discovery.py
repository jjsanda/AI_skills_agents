"""Tests for agentkit.discovery."""

from __future__ import annotations

from pathlib import Path

from agentkit.discovery import discover_skills, load_skill, parse_frontmatter

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"


def test_parse_frontmatter_basic() -> None:
    fm, body = parse_frontmatter("---\nname: demo\ndescription: d\n---\n# Title\n")
    assert fm["name"] == "demo"
    assert fm["description"] == "d"
    assert body.strip() == "# Title"


def test_parse_frontmatter_absent() -> None:
    assert parse_frontmatter("no frontmatter") == ({}, "no frontmatter")


def test_parse_frontmatter_unclosed() -> None:
    text = "---\nname: demo\n# never closes"
    assert parse_frontmatter(text) == ({}, text)


def test_parse_frontmatter_non_mapping() -> None:
    text = "---\n- just\n- a\n- list\n---\nbody"
    fm, _ = parse_frontmatter(text)
    assert fm == {}


def test_discover_finds_all_four_skills() -> None:
    names = sorted(s.name for s in discover_skills(SKILLS))
    assert names == ["code-reviewer", "data-profiler", "pdf-extract", "web-research"]


def test_load_skill_populates_fields() -> None:
    skill = load_skill(SKILLS / "pdf-extract")
    assert skill.name == "pdf-extract"
    assert skill.description
    assert "PDF" in skill.body
    assert any(p.name == "extract.py" for p in skill.scripts)


def test_load_skill_missing_skill_md(tmp_path: Path) -> None:
    skill = load_skill(tmp_path)
    assert skill.name == ""
    assert skill.frontmatter == {}
    assert skill.scripts == []
