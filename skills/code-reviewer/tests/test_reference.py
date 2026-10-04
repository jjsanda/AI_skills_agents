"""Structural tests for the code-reviewer skill (no executable script)."""

from __future__ import annotations

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]


def test_skill_md_exists() -> None:
    assert (SKILL_DIR / "SKILL.md").is_file()


def test_checklist_covers_all_categories() -> None:
    text = (SKILL_DIR / "references" / "checklist.md").read_text(encoding="utf-8")
    for category in ["Correctness", "Security", "Tests", "Readability", "Performance"]:
        assert category in text, f"checklist missing category: {category}"


def test_skill_documents_severity_levels() -> None:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    for severity in ["Critical", "Warning", "Suggestion"]:
        assert severity in text, f"SKILL.md missing severity: {severity}"
