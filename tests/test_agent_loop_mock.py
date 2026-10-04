"""Tests for agentkit.agent_loop (mock path + client selection)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import pytest

from agentkit import agent_loop as al
from agentkit.discovery import load_skill

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"


def test_build_tools_for_skill_with_scripts() -> None:
    tools, mapping = al.build_tools(load_skill(SKILLS / "pdf-extract"))
    assert [t["name"] for t in tools] == ["run_extract"]
    assert "run_extract" in mapping
    assert tools[0]["input_schema"]["type"] == "object"


def test_build_tools_for_skill_without_scripts() -> None:
    tools, mapping = al.build_tools(load_skill(SKILLS / "code-reviewer"))
    assert tools == []
    assert mapping == {}


def test_run_task_executes_tool_in_mock_mode() -> None:
    result = al.run_task("do it", load_skill(SKILLS / "pdf-extract"), al.MockClient())
    assert result.tool_calls == ["run_extract"]
    assert result.final_text.startswith("[mock]")
    assert result.steps >= 2


def test_run_task_answers_immediately_without_tools() -> None:
    result = al.run_task("review this", load_skill(SKILLS / "code-reviewer"), al.MockClient())
    assert result.tool_calls == []
    assert result.steps == 1
    assert result.final_text.startswith("[mock]")


def test_run_task_uses_custom_final_text() -> None:
    result = al.run_task("x", load_skill(SKILLS / "code-reviewer"), al.MockClient("DONE"))
    assert result.final_text == "DONE"


def test_execute_tool_runs_script_help() -> None:
    _, mapping = al.build_tools(load_skill(SKILLS / "pdf-extract"))
    out = al.execute_tool("run_extract", {"args": ["--help"]}, mapping)
    assert "usage" in out.lower() or "Extract" in out


def test_execute_tool_unknown_tool() -> None:
    assert "no handler" in al.execute_tool("nope", {}, {})


def test_should_mock_explicit_flag() -> None:
    assert al.should_mock(True) is True
    assert al.should_mock(False) is False


def test_should_mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTKIT_MOCK", "yes")
    assert al.should_mock(None) is True


def test_should_mock_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTKIT_MOCK", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert al.should_mock(None) is True


def test_should_mock_with_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTKIT_MOCK", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert al.should_mock(None) is False


def test_make_client_returns_mock() -> None:
    assert isinstance(al.make_client(mock=True), al.MockClient)


def test_make_client_returns_real(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTKIT_MOCK", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    client = al.make_client(mock=False)
    assert isinstance(client, al.RealClient)


def test_real_client_create_normalizes_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

    class _Block:
        def __init__(self, data: dict[str, Any]) -> None:
            self._data = data

        def model_dump(self) -> dict[str, Any]:
            return self._data

    class _Message:
        stop_reason = "end_turn"
        content: ClassVar[list[Any]] = [_Block({"type": "text", "text": "hi"})]

    class _Messages:
        @staticmethod
        def create(**_: Any) -> _Message:
            return _Message()

    class _Stub:
        messages = _Messages()

    client = al.RealClient(model="claude-opus-4-8")
    client._client = _Stub()  # type: ignore[assignment]
    response = client.create(system="s", messages=[{"role": "user", "content": "x"}], tools=[])
    assert response["stop_reason"] == "end_turn"
    assert response["content"][0]["text"] == "hi"


def test_run_task_skips_malformed_tool_block() -> None:
    class _Malformed:
        def create(
            self, *, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
        ) -> dict[str, Any]:
            # tool_use block missing required id/name -> must be skipped, not crash
            return {"stop_reason": "tool_use", "content": [{"type": "tool_use", "input": {}}]}

    result = al.run_task("x", load_skill(SKILLS / "pdf-extract"), _Malformed())
    assert result.tool_calls == []
    assert result.steps == 1


def test_run_task_honors_time_limit() -> None:
    result = al.run_task(
        "x", load_skill(SKILLS / "pdf-extract"), al.MockClient(), time_limit_seconds=-1
    )
    assert result.steps == 0


def test_execute_tool_handles_subprocess_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _, mapping = al.build_tools(load_skill(SKILLS / "pdf-extract"))

    def boom(*_args: Any, **_kwargs: Any) -> Any:
        raise OSError("nope")

    monkeypatch.setattr(al.subprocess, "run", boom)
    out = al.execute_tool("run_extract", {"args": []}, mapping)
    assert "error running" in out


def test_real_client_create_handles_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import anthropic

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    client = al.RealClient(model="claude-opus-4-8")

    class _Messages:
        @staticmethod
        def create(**_: Any) -> Any:
            raise anthropic.AnthropicError("boom")

    class _Stub:
        messages = _Messages()

    client._client = _Stub()  # type: ignore[assignment]
    response = client.create(system="s", messages=[{"role": "user", "content": "x"}], tools=[])
    assert response["stop_reason"] == "error"
    assert "boom" in response["content"][0]["text"]


def test_resolve_max_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTKIT_MAX_TOKENS", raising=False)
    assert al._resolve_max_tokens() == al.DEFAULT_MAX_TOKENS
    monkeypatch.setenv("AGENTKIT_MAX_TOKENS", "2048")
    assert al._resolve_max_tokens() == 2048
    monkeypatch.setenv("AGENTKIT_MAX_TOKENS", "notanint")
    assert al._resolve_max_tokens() == al.DEFAULT_MAX_TOKENS
