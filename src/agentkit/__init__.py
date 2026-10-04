"""agentkit: discover, validate, and run AI Agent Skills and subagents.

A small runtime around the open SKILL.md format (https://agentskills.io) with a
mock-able agent loop over the Anthropic Messages API. The package is split into
modules for discovery, validation, the agent loop, diagram export, and the CLI.
"""

from __future__ import annotations

from agentkit.models import Skill, Violation

__version__ = "0.1.0"

__all__ = ["Skill", "Violation", "__version__"]
