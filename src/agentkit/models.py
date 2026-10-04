"""Typed data structures shared across the runtime."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Skill:
    """A discovered Agent Skill: a folder containing a ``SKILL.md``.

    Attributes:
        name: The ``name`` from the YAML frontmatter (should equal the folder).
        description: The ``description`` from the frontmatter.
        path: Path to the skill directory.
        frontmatter: All parsed frontmatter keys/values.
        body: The Markdown body after the frontmatter.

    Example:
        >>> from pathlib import Path
        >>> s = Skill(
        ...     name="demo",
        ...     description="Does X. Use when Y.",
        ...     path=Path("skills/demo"),
        ...     frontmatter={"name": "demo"},
        ...     body="# Demo",
        ... )
        >>> s.name
        'demo'
        >>> s.skill_md.as_posix()
        'skills/demo/SKILL.md'
    """

    name: str
    description: str
    path: Path
    frontmatter: dict[str, object]
    body: str

    @property
    def skill_md(self) -> Path:
        """Path to this skill's ``SKILL.md`` file."""
        return self.path / "SKILL.md"

    @property
    def scripts(self) -> list[Path]:
        """All ``*.py`` scripts bundled under ``scripts/`` (sorted)."""
        scripts_dir = self.path / "scripts"
        return sorted(scripts_dir.glob("*.py")) if scripts_dir.is_dir() else []


@dataclass(frozen=True)
class Violation:
    """A single spec-compliance problem found in a skill.

    Example:
        >>> v = Violation(skill="bad", field="name", message="must be lowercase")
        >>> str(v)
        'bad: [name] must be lowercase'
    """

    skill: str
    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.skill}: [{self.field}] {self.message}"
