# Skills

Each folder here is an [Agent Skill](https://agentskills.io/specification): a
`SKILL.md` (YAML frontmatter plus Markdown instructions) with optional `scripts/`,
`references/`, and `tests/`. They use the open `SKILL.md` format, so they work
across Claude Code, the Claude API, and other agents that understand it.

| Skill | What it does | When to use |
|---|---|---|
| [`pdf-extract`](pdf-extract/) | Extracts text and tables from a PDF to Markdown or CSV | Working with PDFs, statements, reports, or pulling out tables |
| [`data-profiler`](data-profiler/) | Profiles a CSV into a Markdown data-quality report and a chart | Sizing up a dataset (nulls, dtypes, cardinality) before analysis |
| [`web-research`](web-research/) | A method for producing a sourced research brief | Researching or fact-checking a topic with cited sources |
| [`code-reviewer`](code-reviewer/) | A review checklist with Critical/Warning/Suggestion output | Reviewing a diff, or self-checking before handoff |

Validate every skill against the spec:

```bash
agentkit validate
```

Install them into Claude Code:

```bash
make claude-install
```
