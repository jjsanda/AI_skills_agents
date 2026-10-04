"""Run the docstring usage examples as real tests."""

from __future__ import annotations

import doctest
from types import ModuleType

import pytest

from agentkit import agent_loop, discovery, models, validation


@pytest.mark.parametrize("module", [models, discovery, validation, agent_loop])
def test_module_doctests(module: ModuleType) -> None:
    results = doctest.testmod(module, verbose=False)
    assert results.failed == 0, f"{module.__name__}: {results.failed} doctest failure(s)"
