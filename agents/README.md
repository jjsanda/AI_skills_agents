# Subagents

Each file here is a [Claude Code subagent](https://code.claude.com/docs/en/sub-agents):
Markdown with YAML frontmatter (`name`, `description`, optional `tools`, `model`,
and `skills`) whose body is the system prompt. Tools are kept least-privilege.

| Agent | Role | Tools | Preloaded skill |
|---|---|---|---|
| [`orchestrator`](orchestrator.md) | Plans a task and delegates | `Read, Grep, Glob` | none |
| [`researcher`](researcher.md) | Read-only research; returns a sourced brief | `Read, Grep, Glob, WebSearch, WebFetch` | `web-research` |
| [`implementer`](implementer.md) | Writes code and self-reviews | `Read, Write, Edit, Bash, Glob, Grep` | `code-reviewer` |
| [`reviewer`](reviewer.md) | Read-only review (Critical/Warning/Suggestion) | `Read, Grep, Glob` | none |
| [`doc-writer`](doc-writer.md) | Writes and maintains docs | `Read, Write, Edit, Glob, Grep, WebFetch` | none |

`researcher` and `implementer` preload a skill through the `skills:` frontmatter
field, so the full skill content is injected into the subagent's context at
startup.

## Install into Claude Code

Subagents are discovered from `.claude/agents/`. Symlink them (and the skills)
into place:

```bash
make claude-install
```
