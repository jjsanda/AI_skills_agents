.DEFAULT_GOAL := help
PY ?= python3
VENV := .venv
BIN := $(VENV)/bin

.PHONY: help install lint format type test diagrams claude-install all clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Create venv and install agentkit with dev + skills extras (uses uv if available)
	@if command -v uv >/dev/null 2>&1; then \
		echo "==> creating environment with uv"; \
		uv venv $(VENV) --clear; \
		uv pip install --python $(BIN)/python -e ".[dev,skills]"; \
	else \
		echo "==> creating environment with python venv"; \
		$(PY) -m venv $(VENV); \
		$(BIN)/python -m pip install --upgrade pip; \
		$(BIN)/pip install -e ".[dev,skills]"; \
	fi

lint:  ## Lint and check formatting (ruff)
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .

format:  ## Auto-fix lint issues and format (ruff)
	$(BIN)/ruff check --fix .
	$(BIN)/ruff format .

type:  ## Type-check the runtime package (mypy --strict)
	$(BIN)/mypy

test:  ## Run all tests with coverage gate (>=80% on agentkit)
	$(BIN)/pytest --cov=agentkit --cov-report=term-missing --cov-fail-under=80

diagrams:  ## Render every Mermaid diagram to SVG + PNG
	$(BIN)/agentkit diagrams

claude-install:  ## Symlink skills/ and agents/ into .claude/ so Claude Code can discover them
	mkdir -p .claude/skills .claude/agents
	@for d in skills/*/; do ln -sfn "$$(pwd)/$$d" ".claude/skills/$$(basename $$d)"; done
	@for f in agents/*.md; do ln -sfn "$$(pwd)/$$f" ".claude/agents/$$(basename $$f)"; done
	@echo "Linked skills/ -> .claude/skills/ and agents/ -> .claude/agents/"

all: lint type test diagrams  ## Run the full local quality gate (lint + type + test + diagrams)

clean:  ## Remove caches and build artifacts
	rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml htmlcov build dist src/*.egg-info
