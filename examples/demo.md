# Demo walkthrough

A short tour of `agentkit`. Everything here runs offline; no API key is needed,
because the agent loop falls back to mock mode when no key is set.

## 1. Install

```bash
make install
source .venv/bin/activate
```

## 2. List the skills

```bash
agentkit list
```

This prints a table of the four skills with their descriptions.

## 3. Validate them

```bash
agentkit validate
```

`validate` checks each skill against the
[agentskills.io](https://agentskills.io/specification) naming and description
rules and exits non-zero if any skill breaks them.

## 4. Run the agent loop (offline)

```bash
agentkit run "Extract the text from the sample PDF" --skill pdf-extract --mock
```

```text
> Skill: pdf-extract  |  Mode: mock
> Tools called: run_extract (2 step(s))

[mock] Completed task: Extract the text from the sample PDF
```

In mock mode the loop loads the skill, exposes its script as a tool, calls it,
and returns. With `ANTHROPIC_API_KEY` set (and without `--mock`), the same loop
runs against the real Anthropic Messages API.

## 5. Run a skill script directly

```bash
python skills/pdf-extract/scripts/extract.py examples/sample.pdf
python skills/data-profiler/scripts/profile.py examples/sample.csv --chart /tmp/profile.png
```

## 6. Regenerate the diagrams

```bash
agentkit diagrams
```

This writes SVG and PNG files into `docs/diagrams/exported/`.
