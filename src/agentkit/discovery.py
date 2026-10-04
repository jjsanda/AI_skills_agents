"""Find and parse ``SKILL.md`` files into :class:`~agentkit.models.Skill` objects."""

from __future__ import annotations

from pathlib import Path

import yaml

from agentkit.models import Skill


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Split a document's leading YAML frontmatter from its Markdown body.

    Frontmatter is the block between an opening ``---`` line at the very start
    of the file and the next ``---`` line. Returns ``(frontmatter, body)``;
    if there is no valid frontmatter block, returns ``({}, text)``.

    Example:
        >>> fm, body = parse_frontmatter("---\\nname: demo\\n---\\n# Title\\n")
        >>> fm["name"], body.strip()
        ('demo', '# Title')
        >>> parse_frontmatter("no frontmatter here")
        ({}, 'no frontmatter here')
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    closing: int | None = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing = i
            break
    if closing is None:
        return {}, text

    raw = "\n".join(lines[1:closing])
    body = "\n".join(lines[closing + 1 :])
    loaded = yaml.safe_load(raw) or {}
    if not isinstance(loaded, dict):
        return {}, text
    frontmatter: dict[str, object] = {str(k): v for k, v in loaded.items()}
    return frontmatter, body


def load_skill(skill_dir: Path | str) -> Skill:
    """Load a single skill from its directory.

    Example:
        >>> load_skill("skills/pdf-extract").name  # doctest: +SKIP
        'pdf-extract'
    """
    path = Path(skill_dir)
    skill_md = path / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else ""
    frontmatter, body = parse_frontmatter(text)
    name = str(frontmatter.get("name", "")).strip()
    description = str(frontmatter.get("description", "")).strip()
    return Skill(
        name=name,
        description=description,
        path=path,
        frontmatter=frontmatter,
        body=body,
    )


def discover_skills(skills_dir: Path | str = "skills") -> list[Skill]:
    """Discover every skill under ``skills_dir`` (one folder per ``SKILL.md``).

    Example:
        >>> sorted(s.name for s in discover_skills("skills"))  # doctest: +SKIP
        ['code-reviewer', 'data-profiler', 'pdf-extract', 'web-research']
    """
    root = Path(skills_dir)
    return [load_skill(p.parent) for p in sorted(root.glob("*/SKILL.md"))]
