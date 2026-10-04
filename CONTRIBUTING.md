# Contributing to agentkit

Thanks for taking a look. Contributions are welcome; the sections below cover local setup and the checks that CI runs.

## Development setup

```bash
make install          # create .venv and install agentkit with dev + skills extras
source .venv/bin/activate
pre-commit install    # optional: run lint/type/validate hooks on each commit
```

## The quality gate

Everything CI checks is reproducible locally with one command:

```bash
make all              # ruff (lint + format) -> mypy (strict) -> pytest (cov >=80%) -> render diagrams
```

Individual targets: `make lint`, `make type`, `make test`, `make diagrams`, `make format`.

## Adding a new skill

A skill is a folder under `skills/` with a `SKILL.md` (see [the spec](https://agentskills.io/specification)). The folder name **must match** the `name:` in the frontmatter.

```text
skills/my-skill/
├── SKILL.md           # required: YAML frontmatter + Markdown instructions
├── scripts/           # optional: executable, --help-able, side-effect-free code
├── references/        # optional: deep detail loaded on demand
└── tests/             # a test proving the script works
```

Then validate it:

```bash
agentkit validate     # exits non-zero if any SKILL.md breaks the spec
```

`agentkit validate` enforces: lowercase/hyphen `name` (<=64 chars, matches the folder), a non-empty `description` (<=1024 chars) that says *what* the skill does and *when* to use it, and no `<`/`>` or reserved words in the metadata.

## Adding a subagent

Subagents live in `agents/` as Markdown files with YAML frontmatter (`name`, `description`, optional `tools`/`model`/`skills`). Keep `tools` least-privilege. Run `make claude-install` to symlink `skills/` and `agents/` into `.claude/` for use inside Claude Code.

## Pull requests

- Keep changes focused; add a test for any new behavior.
- Make sure `make all` is green.
- Update `CHANGELOG.md` under `[Unreleased]`.
