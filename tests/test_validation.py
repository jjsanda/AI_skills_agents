"""Tests for agentkit.validation (the spec-compliance rules)."""

from __future__ import annotations

from pathlib import Path

from agentkit.discovery import discover_skills
from agentkit.models import Skill
from agentkit.validation import validate_all, validate_skill

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"


def _skill(name: str, description: str = "ok", folder: str | None = None) -> Skill:
    folder = folder or name or "x"
    return Skill(
        name=name,
        description=description,
        path=Path("nowhere") / folder,
        frontmatter={"name": name},
        body="",
    )


def test_all_real_skills_are_valid() -> None:
    assert validate_all(discover_skills(SKILLS)) == []


def test_missing_name() -> None:
    fields = [v.field for v in validate_skill(_skill("", folder="foo"))]
    assert "name" in fields


def test_bad_name_pattern() -> None:
    messages = [v.message for v in validate_skill(_skill("Bad_Name"))]
    assert any("lowercase" in m for m in messages)


def test_consecutive_hyphens() -> None:
    messages = [v.message for v in validate_skill(_skill("a--b"))]
    assert any("hyphen" in m for m in messages)


def test_reserved_word_rejected() -> None:
    messages = [v.message for v in validate_skill(_skill("claude-helper"))]
    assert any("reserved" in m for m in messages)


def test_name_must_match_folder() -> None:
    messages = [v.message for v in validate_skill(_skill("foo", folder="bar"))]
    assert any("match folder" in m for m in messages)


def test_name_too_long() -> None:
    messages = [v.message for v in validate_skill(_skill("a" * 65))]
    assert any("64" in m for m in messages)


def test_description_required() -> None:
    fields = [v.field for v in validate_skill(_skill("ok-name", description=""))]
    assert "description" in fields


def test_description_too_long() -> None:
    messages = [v.message for v in validate_skill(_skill("ok-name", description="x" * 1025))]
    assert any("1024" in m for m in messages)


def test_forbidden_chars_in_description() -> None:
    messages = [v.message for v in validate_skill(_skill("ok-name", description="has <tag>"))]
    assert any("'<' or '>'" in m for m in messages)


def test_forbidden_chars_in_name() -> None:
    messages = [v.message for v in validate_skill(_skill("a<b", folder="a<b"))]
    assert any("'<' or '>'" in m for m in messages)


def test_validate_all_aggregates() -> None:
    violations = validate_all([_skill("Bad_Name"), _skill("ok-name", description="")])
    assert len(violations) >= 2
