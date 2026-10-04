"""A minimal, tool-using agent loop with a real and a mock backend.

The loop loads a skill's instructions into the system prompt and exposes the
skill's bundled scripts as tools, then runs the standard Anthropic Messages API
tool-use loop: send messages, and while the model asks to use a tool, execute it
and feed the result back, until the model stops.

NOTE: Model ids and API details change over time. The default model id and the
request shape here reflect the Anthropic Messages API at time of writing;
consult the official docs (https://docs.claude.com) and keep the model
configurable via the ``AGENTKIT_MODEL`` environment variable.

Real mode uses the official ``anthropic`` SDK and reads ``ANTHROPIC_API_KEY``
from the environment (never hardcode keys). Mock mode is deterministic, needs no
network or key, and is the default whenever no key is present.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

from agentkit.models import Skill

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pathlib import Path

logger = logging.getLogger("agentkit.agent_loop")

DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_TOKENS = 4096
_TOOL_TIMEOUT_SECONDS = 30  # generous for the bundled scripts; revisit if a skill needs longer
_MAX_TOOL_OUTPUT = 2000  # cap tool results so a chatty script can't blow the context budget

# Wire-format aliases (Anthropic Messages API shapes are plain JSON dicts).
Message = dict[str, Any]
ToolDef = dict[str, Any]
Response = dict[str, Any]


class LLMClient(Protocol):
    """A minimal client interface the loop depends on (real or mock)."""

    def create(self, *, system: str, messages: list[Message], tools: list[ToolDef]) -> Response:
        """Return ``{"stop_reason": str, "content": [block, ...]}``."""
        ...


@dataclass
class LoopResult:
    """The outcome of :func:`run_task`."""

    final_text: str
    tool_calls: list[str] = field(default_factory=list)
    steps: int = 0


def build_tools(skill: Skill) -> tuple[list[ToolDef], dict[str, Path]]:
    """Build one tool definition per bundled script in ``skill``.

    Returns the list of tool definitions (for the API) and a mapping from tool
    name to the script path (for execution).

    Example:
        >>> from pathlib import Path
        >>> from agentkit.models import Skill
        >>> s = Skill("demo", "d", Path("skills/demo"), {}, "")
        >>> build_tools(s)
        ([], {})
    """
    tools: list[ToolDef] = []
    mapping: dict[str, Path] = {}
    for script in skill.scripts:
        tool_name = f"run_{script.stem}".replace("-", "_")
        tools.append(
            {
                "name": tool_name,
                "description": (
                    f"Run the `{script.name}` script from the '{skill.name}' skill. "
                    f"{skill.description}"
                )[:1000],  # Anthropic caps tool descriptions near 1024 chars; stay under it
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Command-line arguments to pass to the script.",
                        }
                    },
                    "required": [],
                },
            }
        )
        mapping[tool_name] = script
    return tools, mapping


def execute_tool(name: str, tool_input: dict[str, Any], mapping: dict[str, Path]) -> str:
    """Execute a skill script tool and return its (truncated) output.

    Example:
        >>> execute_tool("missing", {}, {})
        "(no handler registered for tool 'missing')"
    """
    script = mapping.get(name)
    if script is None:
        return f"(no handler registered for tool '{name}')"
    raw_args = tool_input.get("args") or []
    args = [str(a) for a in raw_args] if isinstance(raw_args, list) else [str(raw_args)]
    logger.debug("execute_tool: running %s with args=%s", script.name, args)
    try:
        proc = subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True,
            text=True,
            timeout=_TOOL_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        logger.warning("execute_tool: %s failed: %s", script.name, exc)
        return f"(error running {script.name}: {exc})"
    combined = (proc.stdout + proc.stderr).strip()
    # TODO: truncate on a line boundary so multi-line output stays readable
    return combined[:_MAX_TOOL_OUTPUT] or f"(no output; exit code {proc.returncode})"


def run_task(
    task: str,
    skill: Skill,
    client: LLMClient,
    *,
    max_steps: int = 6,
    time_limit_seconds: float | None = None,
) -> LoopResult:
    """Run the demo agent loop for ``task`` using ``skill`` and ``client``.

    ``max_steps`` caps the number of model turns; ``time_limit_seconds``, if set,
    adds a wall-clock guard so a slow loop can't run unbounded.

    Example:
        >>> from pathlib import Path
        >>> from agentkit.models import Skill
        >>> s = Skill("demo", "Demo skill.", Path("skills/demo"), {}, "Body.")
        >>> result = run_task("say hi", s, MockClient())
        >>> result.final_text.startswith("[mock]")
        True
    """
    system = f"You have loaded the '{skill.name}' skill. Follow its instructions:\n\n{skill.body}"
    tools, mapping = build_tools(skill)
    messages: list[Message] = [{"role": "user", "content": task}]
    tool_calls: list[str] = []
    final_text = ""
    steps = 0
    started = time.monotonic()

    for _ in range(max_steps):
        if time_limit_seconds is not None and (time.monotonic() - started) > time_limit_seconds:
            logger.warning(
                "run_task: time limit %.1fs reached after %d step(s)", time_limit_seconds, steps
            )
            break
        steps += 1
        response = client.create(system=system.strip(), messages=messages, tools=tools)
        logger.debug("run_task: step %d stop_reason=%s", steps, response.get("stop_reason"))
        assistant_blocks: list[dict[str, Any]] = []
        tool_results: list[dict[str, Any]] = []

        for block in response.get("content", []):
            block_type = block.get("type")
            if block_type == "text":
                text = block.get("text", "")
                assistant_blocks.append({"type": "text", "text": text})
                if text:
                    final_text = text
            elif block_type == "tool_use":
                tool_name = block.get("name")
                tool_id = block.get("id")
                if not tool_name or not tool_id:
                    logger.warning("run_task: skipping malformed tool_use block: %r", block)
                    continue
                tool_input = block.get("input", {})
                assistant_blocks.append(
                    {"type": "tool_use", "id": tool_id, "name": tool_name, "input": tool_input}
                )
                tool_calls.append(tool_name)
                output = execute_tool(tool_name, tool_input, mapping)
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": tool_id, "content": output}
                )

        if assistant_blocks:
            messages.append({"role": "assistant", "content": assistant_blocks})
        if response.get("stop_reason") != "tool_use" or not tool_results:
            break
        messages.append({"role": "user", "content": tool_results})

    logger.debug("run_task: finished in %d step(s), %d tool call(s)", steps, len(tool_calls))
    return LoopResult(final_text=final_text.strip(), tool_calls=tool_calls, steps=steps)


class MockClient:
    """A fake client for offline runs and tests (no network, no key).

    On the first turn it asks to use the first available tool (with
    ``args=["--help"]``); after a tool result comes back it returns a final
    text answer. With no tools, it answers immediately.
    """

    def __init__(self, final_text: str | None = None) -> None:
        self._final_text = final_text

    def create(self, *, system: str, messages: list[Message], tools: list[ToolDef]) -> Response:
        already_used_tool = any(
            isinstance(m.get("content"), list)
            and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in m["content"])
            for m in messages
        )
        if already_used_tool or not tools:
            text = self._final_text or self._derive_text(messages)
            return {"stop_reason": "end_turn", "content": [{"type": "text", "text": text}]}

        tool = tools[0]
        return {
            "stop_reason": "tool_use",
            "content": [
                {"type": "text", "text": f"Loading the skill and running `{tool['name']}`."},
                {
                    "type": "tool_use",
                    "id": "toolu_mock_0001",
                    "name": tool["name"],
                    "input": self._mock_input(tool),
                },
            ],
        }

    @staticmethod
    def _mock_input(tool: ToolDef) -> dict[str, Any]:
        properties = tool.get("input_schema", {}).get("properties", {})
        return {"args": ["--help"]} if "args" in properties else {}

    @staticmethod
    def _derive_text(messages: list[Message]) -> str:
        first = messages[0].get("content", "") if messages else ""
        if isinstance(first, list):
            first = " ".join(b.get("text", "") for b in first if isinstance(b, dict))
        return f"[mock] Completed task: {first}".strip()


class RealClient:
    """Wraps the official ``anthropic`` SDK for the Messages API tool loop."""

    def __init__(self, model: str, max_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        import anthropic  # imported lazily so mock mode needs no SDK setup

        self._client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens

    def create(self, *, system: str, messages: list[Message], tools: list[ToolDef]) -> Response:
        import anthropic

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        if system:
            kwargs["system"] = system
        # TODO: no retry/backoff yet; a transient 429/5xx surfaces as a one-shot error
        try:
            message = self._client.messages.create(**kwargs)
        except anthropic.AnthropicError as exc:
            logger.error("Anthropic API call failed: %s", exc)
            return {
                "stop_reason": "error",
                "content": [{"type": "text", "text": f"[error] Anthropic API call failed: {exc}"}],
            }
        return {
            "stop_reason": message.stop_reason,
            "content": [block.model_dump() for block in message.content],
        }


def should_mock(flag: bool | None = None) -> bool:
    """Decide whether to use mock mode.

    Precedence: explicit ``flag`` > ``AGENTKIT_MOCK`` env > absence of
    ``ANTHROPIC_API_KEY`` (no key => mock).

    Example:
        >>> should_mock(True)
        True
    """
    if flag is not None:
        return flag
    if os.environ.get("AGENTKIT_MOCK", "").strip().lower() in {"1", "true", "yes"}:
        return True
    return not os.environ.get("ANTHROPIC_API_KEY")


def _resolve_max_tokens() -> int:
    raw = os.environ.get("AGENTKIT_MAX_TOKENS")
    return int(raw) if raw and raw.isdigit() else DEFAULT_MAX_TOKENS


def make_client(*, mock: bool | None = None, model: str | None = None) -> LLMClient:
    """Construct a :class:`MockClient` or :class:`RealClient` per :func:`should_mock`.

    Example:
        >>> isinstance(make_client(mock=True), MockClient)
        True
    """
    if should_mock(mock):
        return MockClient()
    resolved_model = model or os.environ.get("AGENTKIT_MODEL", DEFAULT_MODEL)
    return RealClient(model=resolved_model, max_tokens=_resolve_max_tokens())
