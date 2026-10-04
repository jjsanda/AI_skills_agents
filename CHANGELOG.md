# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-29

### Added
- Runtime package `agentkit` with skill **discovery**, spec **validation**, a mock-able **agent loop** over the Anthropic Messages API, and a **diagram exporter**.
- CLI commands: `agentkit list`, `agentkit validate`, `agentkit run`, `agentkit diagrams` (all with `--help`; `run` supports `--mock`).
- Four Agent Skills (open `SKILL.md` format): `pdf-extract`, `data-profiler`, `web-research`, `code-reviewer`.
- Five subagents: `orchestrator`, `researcher`, `implementer` (preloads the `code-reviewer` skill via `skills:`), `reviewer`, `doc-writer`.
- Four Mermaid diagrams exported to SVG + PNG and embedded in the README.
- Quality tooling: ruff, mypy (strict), pytest + coverage (>=80% gate), pre-commit, a `Makefile`, and a GitHub Actions CI matrix that also renders the diagrams.

[Unreleased]: https://github.com/jjsanda/agentkit/compare/v0.1.0...HEAD [0.1.0]: https://github.com/jjsanda/agentkit/releases/tag/v0.1.0
