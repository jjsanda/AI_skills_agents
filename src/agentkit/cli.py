"""The ``agentkit`` command-line interface (built with Typer).

Commands:
    agentkit list                 List discovered skills.
    agentkit validate             Validate every SKILL.md (non-zero exit on failure).
    agentkit run "<task>"         Run the demo agent loop (use --mock to force offline).
    agentkit diagrams             Render Mermaid diagrams to SVG + PNG.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from agentkit import __version__
from agentkit.agent_loop import MockClient, make_client, run_task
from agentkit.diagrams import render_all
from agentkit.discovery import discover_skills
from agentkit.validation import validate_all

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Discover, validate, and run AI Agent Skills.",
)

SkillsDir = Annotated[Path, typer.Option("--skills-dir", help="Directory containing skills.")]

# Truncate descriptions in the `list` table so each skill stays on one row.
_LIST_DESC_WIDTH = 80


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"agentkit {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """agentkit: discover, validate, and run AI Agent Skills and subagents."""


@app.command("list")
def list_skills(skills_dir: SkillsDir = Path("skills")) -> None:
    """List discovered skills and their descriptions."""
    skills = discover_skills(skills_dir)
    if not skills:
        typer.echo(f"No skills found in {skills_dir}/.")
        return
    width = max(len(s.name) for s in skills)
    typer.echo(f"{'SKILL'.ljust(width)}  DESCRIPTION")
    typer.echo(f"{'-' * width}  {'-' * 11}")
    for skill in skills:
        desc = skill.description
        if len(desc) > _LIST_DESC_WIDTH:
            desc = desc[: _LIST_DESC_WIDTH - 1] + "…"  # reserve one column for the ellipsis
        typer.echo(f"{skill.name.ljust(width)}  {desc}")


@app.command()
def validate(skills_dir: SkillsDir = Path("skills")) -> None:
    """Validate every SKILL.md against the agentskills.io spec."""
    skills = discover_skills(skills_dir)
    if not skills:
        typer.echo(f"No skills found in {skills_dir}/.", err=True)
        raise typer.Exit(1)
    violations = validate_all(skills)
    if violations:
        for violation in violations:
            typer.echo(f"✗ {violation}", err=True)
        typer.echo(f"\n{len(violations)} violation(s) across {len(skills)} skill(s).", err=True)
        raise typer.Exit(1)
    typer.echo(f"✓ All {len(skills)} skill(s) valid.")


@app.command()
def run(
    task: Annotated[str, typer.Argument(help="The task for the agent to complete.")],
    skill: Annotated[str | None, typer.Option("--skill", help="Name of the skill to load.")] = None,
    mock: Annotated[
        bool, typer.Option("--mock", help="Force deterministic offline mock mode.")
    ] = False,
    skills_dir: SkillsDir = Path("skills"),
) -> None:
    """Run a demo agent loop that loads a skill and completes the task."""
    skills = discover_skills(skills_dir)
    if not skills:
        typer.echo(f"No skills found in {skills_dir}/.", err=True)
        raise typer.Exit(1)

    if skill is not None:
        chosen = next((s for s in skills if s.name == skill), None)
        if chosen is None:
            available = ", ".join(s.name for s in skills)
            typer.echo(f"Unknown skill '{skill}'. Available: {available}", err=True)
            raise typer.Exit(1)
    else:
        chosen = next((s for s in skills if s.scripts), skills[0])

    client = make_client(mock=True if mock else None)
    mode = "mock" if isinstance(client, MockClient) else "real"
    typer.echo(f"> Skill: {chosen.name}  |  Mode: {mode}")
    result = run_task(task, chosen, client)
    if result.tool_calls:
        typer.echo(f"> Tools called: {', '.join(result.tool_calls)} ({result.steps} step(s))")
    typer.echo(f"\n{result.final_text}")


@app.command()
def diagrams(
    diagrams_dir: Annotated[
        Path, typer.Option("--diagrams-dir", help="Directory of .mmd sources.")
    ] = Path("docs/diagrams"),
) -> None:
    """Render every Mermaid diagram to SVG and PNG."""
    written = render_all(diagrams_dir)
    typer.echo(f"✓ Rendered {len(written)} file(s) into {Path(diagrams_dir) / 'exported'}/")
    for path in written:
        typer.echo(f"  {path}")


if __name__ == "__main__":  # pragma: no cover
    app()
