"""Enforce the open Agent Skills (``SKILL.md``) specification in code.

Rules are taken from the spec at https://agentskills.io/specification and the
Anthropic Agent Skills docs
(https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview):

- ``name``: required; <= 64 chars; lowercase letters/digits and single hyphens
  only (no leading/trailing/consecutive hyphens); must equal the skill's folder
  name; must not contain ``<``/``>`` (XML tags) or the reserved words
  ``anthropic``/``claude``.
- ``description``: required; non-empty; <= 1024 chars; must not contain ``<``/``>``.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from agentkit.models import Skill, Violation

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_MAX_LENGTH = 64
DESCRIPTION_MAX_LENGTH = 1024
RESERVED_WORDS = ("anthropic", "claude")
FORBIDDEN_CHARS = ("<", ">")

# NOTE: the spec also defines license/compatibility/allowed-tools metadata;
# we only enforce name + description today.


def validate_skill(skill: Skill) -> list[Violation]:
    """Return every spec violation for a single skill (empty list == valid).

    Example:
        >>> from pathlib import Path
        >>> from agentkit.models import Skill
        >>> bad = Skill(
        ...     name="Bad_Name",
        ...     description="ok",
        ...     path=Path("nowhere/Bad_Name"),
        ...     frontmatter={"name": "Bad_Name"},
        ...     body="",
        ... )
        >>> sorted({v.field for v in validate_skill(bad)})
        ['SKILL.md', 'name']
    """
    violations: list[Violation] = []
    name = skill.name
    skill_id = name or skill.path.name

    if not name:
        violations.append(Violation(skill_id, "name", "missing required `name` field"))
    else:
        if len(name) > NAME_MAX_LENGTH:
            violations.append(Violation(skill_id, "name", f"exceeds {NAME_MAX_LENGTH} characters"))
        if not NAME_PATTERN.match(name):
            violations.append(
                Violation(
                    skill_id,
                    "name",
                    "must be lowercase letters/digits with single hyphens "
                    "(no leading, trailing, or consecutive hyphens)",
                )
            )
        if any(ch in name for ch in FORBIDDEN_CHARS):
            violations.append(Violation(skill_id, "name", "must not contain '<' or '>'"))
        if any(word in name.lower() for word in RESERVED_WORDS):
            violations.append(
                Violation(skill_id, "name", "must not contain reserved words 'anthropic'/'claude'")
            )
        if name != skill.path.name:
            violations.append(
                Violation(skill_id, "name", f"must match folder name '{skill.path.name}'")
            )

    description = skill.description
    if not description:
        violations.append(
            Violation(skill_id, "description", "missing or empty required `description` field")
        )
    else:
        if len(description) > DESCRIPTION_MAX_LENGTH:
            violations.append(
                Violation(skill_id, "description", f"exceeds {DESCRIPTION_MAX_LENGTH} characters")
            )
        if any(ch in description for ch in FORBIDDEN_CHARS):
            violations.append(Violation(skill_id, "description", "must not contain '<' or '>'"))

    if not skill.skill_md.is_file():
        violations.append(Violation(skill_id, "SKILL.md", "missing SKILL.md file"))

    return violations


def validate_all(skills: Iterable[Skill]) -> list[Violation]:
    """Validate many skills and return the combined list of violations.

    Example:
        >>> validate_all([])
        []
    """
    violations: list[Violation] = []
    for skill in skills:
        violations.extend(validate_skill(skill))
    return violations
