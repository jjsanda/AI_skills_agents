---
name: web-research
description: Turn a research question into a concise, cited brief by framing it, gathering independent sources, scoring them, triangulating, then synthesizing. Reach for it on research, investigation, fact-checking, or background-gathering tasks where the sourcing has to hold up.
license: Apache-2.0
---

# Web Research

A method for turning a question into a brief where every claim carries a citation.
It is mostly procedure, not code: the value is in how you gather and weigh sources.

## When to use

Use when a task is "research X", "what's the latest on Y", "fact-check this
claim", or "give me a sourced summary of Z".

## Workflow

1. **Frame the question.** Restate it precisely and note what a good answer needs
   (scope, time range, region).
2. **Gather diverse sources.** Aim for several independent sources, not three
   copies of the same wire story.
3. **Evaluate each source.** Score credibility using
   `references/source-quality.md` (authority, evidence, recency, independence).
4. **Triangulate.** Treat a claim as established only when at least two
   independent, credible sources agree, and flag disagreements explicitly.
5. **Synthesize** into the output template below, citing every claim.

## Output template

```markdown
# <Topic>

## Summary
<3-5 sentences answering the question directly.>

## Key findings
- <finding> [source: <url>, <date>, <credibility: high/med/low>]

## Open questions / disagreements
- <where sources conflict or evidence is thin>

## Sources
1. <title>, <url> (<publisher>, <date>)
```

## Optional helper script

`scripts/search.py` prints this workflow by default. If a `WEB_RESEARCH_API_KEY`
environment variable is set, it performs a real web search over HTTPS
(Brave-compatible API). It only touches the network when a key is provided.

```bash
python scripts/search.py "your question"            # prints the manual workflow
WEB_RESEARCH_API_KEY=... python scripts/search.py "your question"   # live search
```

## Guidelines

- Prefer primary sources over commentary, and recent over stale for fast-moving
  topics.
- Never present a single-source claim as established fact.
- Keep the brief tight: the template, not an essay.
