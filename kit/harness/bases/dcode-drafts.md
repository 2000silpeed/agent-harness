# dcode 구현 초안 (전부 실행 검증 안 함)

> [`dcode.md`](dcode.md)의 부록이다. 본문의 "부록 A~D"가 이 파일을 가리킨다.

저장소의 기반 클래스·서명·관례를 따라 쓴 초안이다. **한 번도 실행·린트·타입 검사하지 않았다.** 8절 7~9번으로 확인한다.

### A. 미들웨어 뼈대 — `libs/code/deepagents_code/run_log.py` (실행 검증 안 함)

```python
"""Record every tool call of a thread as JSON lines.

One agent server hosts several workspaces, so the log directory is passed in by
the graph builder instead of being derived from the process working directory.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from langchain.agents.middleware.types import AgentMiddleware, TracePolicy, omit_payload
from langchain_core.messages import ToolMessage
from langgraph.errors import GraphBubbleUp

from deepagents_code._cli_context import CLIContextSchema

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from pathlib import Path

    from langgraph.prebuilt.tool_node import ToolCallRequest
    from langgraph.types import Command

logger = logging.getLogger(__name__)

_UNKNOWN_THREAD = "unknown-thread"
"""File stem used when the run context carries no thread id."""


class RunLogMiddleware(AgentMiddleware):
    """Append one JSON line per tool call to `<log_dir>/<thread_id>.jsonl`.

    A write failure is logged and never fails the tool call.
    """

    trace_policy = TracePolicy(process_inputs=omit_payload)
    """Omit hook inputs from traces by default; set a `TracePolicy` to override."""

    def __init__(self, log_dir: Path) -> None:
        """Initialize the recorder.

        Args:
            log_dir: Workspace-scoped directory passed in by the graph builder.
        """
        super().__init__()
        self._log_dir = log_dir

    def _record(
        self,
        request: ToolCallRequest,
        result: ToolMessage | Command[Any] | None,
        error: BaseException | None,
        started: float,
    ) -> None:
        """Append the record for one finished tool call."""
        runtime = getattr(request, "runtime", None)
        context = CLIContextSchema.from_payload(getattr(runtime, "context", None))
        thread = (context.thread_id if context is not None else None) or ""
        stem = "".join(ch for ch in thread if ch.isalnum() or ch in "-_")
        status = "error" if error is not None else "ok"
        exit_code: int | None = None
        if isinstance(result, ToolMessage):
            artifact = result.artifact
            code = artifact.get("exit_code") if isinstance(artifact, dict) else None
            if isinstance(code, int) and not isinstance(code, bool):
                exit_code = code
            # `execute` reports a failed command as a successful tool call.
            if result.status == "error" or exit_code not in {None, 0}:
                status = "error"
        event = {
            "ts": datetime.now(UTC).isoformat(),
            "kind": "tool_call",
            "tool": request.tool_call["name"],
            "tool_call_id": request.tool_call["id"],
            "status": status,
            "exit_code": exit_code,
            "error": type(error).__name__ if error is not None else None,
            "duration_ms": int((time.perf_counter() - started) * 1000),
        }
        path = self._log_dir / f"{stem or _UNKNOWN_THREAD}.jsonl"
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError:
            logger.warning("Could not append run log %s", path, exc_info=True)

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command[Any]]],
    ) -> ToolMessage | Command[Any]:
        """Run the tool and record its outcome without blocking the event loop.

        Args:
            request: The tool call being processed.
            handler: The next handler in the middleware chain.

        Returns:
            The tool result, unchanged.
        """
        started = time.perf_counter()
        try:
            result = await handler(request)
        except GraphBubbleUp:
            # An interrupt is control flow; the call runs again on resume.
            raise
        except Exception as exc:
            await asyncio.to_thread(self._record, request, None, exc, started)
            raise
        await asyncio.to_thread(self._record, request, result, None, started)
        return result
```

- **동기 `wrap_tool_call`도 반드시 만든다.** 위와 같은 모양에서 `async`/`await`를 빼고 `asyncio.to_thread(self._record, …)`를 `self._record(…)`로 바꾼다(`handler`의 타입은 `Callable[[ToolCallRequest], ToolMessage | Command[Any]]`). 부록 C의 첫 테스트가 이 메서드를 부른다.
- 게이트는 `handler`를 부르지 않고 거부를 돌려준다: `return ToolMessage(content="Edit blocked: the plan is not approved yet.", name=request.tool_call["name"], tool_call_id=request.tool_call["id"], status="error")`.
- 린트에 걸릴 수 있는 곳 〔추정〕: `except Exception … raise`, `result.artifact`의 타입 좁히기, docstring 구역. 걸리면 저장소의 같은 패턴(`memory_guard.py`, `model_retry.py`)에 맞춘다.

### B. 넣는 자리 — `libs/code/deepagents_code/agent.py` (실행 검증 안 함)

메인 목록: `agent_middleware: list[AgentMiddleware[Any, Any]] = [ConfigurableModelMiddleware(...)]` 리터럴 바로 뒤, `if not interactive:` 앞.

```python
    # Record tool calls for monitoring. Installed only when the builder knows
    # the workspace directory; the process directory is never consulted.
    if effective_cwd is not None:
        from deepagents_code.run_log import RunLogMiddleware

        agent_middleware.append(
            RunLogMiddleware(Path(effective_cwd) / ".deepagents" / "runs")
        )
```

서브에이전트: `_subagent_cli_middleware()` 안의 `middleware.append(CodeModelRetryMiddleware(max_retries=model_retries))` 뒤에 같은 블록을 `middleware.append(...)`로 넣는다(새 인스턴스. `effective_cwd`는 바깥 함수의 변수라 보인다). 게이트 미들웨어도 같은 두 곳에 넣는다.

### C. 단위 테스트 — `libs/code/tests/unit_tests/test_run_log.py` (실행 검증 안 함)

```python
"""Tests for the run-log middleware."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest

from deepagents_code.run_log import RunLogMiddleware

if TYPE_CHECKING:
    from pathlib import Path


def _request(tool_name: str = "execute") -> ToolCallRequest:
    return ToolCallRequest(
        runtime=cast("Any", None),
        tool_call={"id": "call-1", "name": tool_name, "args": {}},
        state={},
        tool=None,
    )


def _events(log_dir: Path) -> list[dict[str, Any]]:
    text = (log_dir / "unknown-thread.jsonl").read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines()]


def test_failed_command_is_recorded_as_error(tmp_path: Path) -> None:
    """A non-zero exit code is an error even though the tool call succeeded."""
    middleware = RunLogMiddleware(tmp_path / "runs")

    def handler(_request: ToolCallRequest) -> ToolMessage:
        return ToolMessage(
            content="[Command failed with exit code 1]",
            name="execute",
            tool_call_id="call-1",
            artifact={"exit_code": 1},
            status="success",
        )

    middleware.wrap_tool_call(_request(), handler)

    (event,) = _events(tmp_path / "runs")
    assert event["status"] == "error"
    assert event["exit_code"] == 1


async def test_async_call_is_recorded(tmp_path: Path) -> None:
    """The async wrapper writes the same record as the sync path."""
    middleware = RunLogMiddleware(tmp_path / "runs")

    async def handler(_request: ToolCallRequest) -> ToolMessage:  # noqa: RUF029
        return ToolMessage(content="ok", name="ls", tool_call_id="call-1")

    await middleware.awrap_tool_call(_request("ls"), handler)

    (event,) = _events(tmp_path / "runs")
    assert (event["tool"], event["status"], event["exit_code"]) == ("ls", "ok", None)
```

### D. `hooks.json` 예 — `{프로젝트 루트}/.deepagents/hooks.json` (실행 검증 안 함)

```json
{"hooks": {
  "PreToolUse": [{"matcher": "Write|Edit|delete", "hooks": [
    {"type": "command", "command": "python3 .deepagents/hooks/plan_gate.py", "timeout": 10}]}],
  "UserPromptSubmit": [{"hooks": [
    {"type": "command", "command": "python3 .deepagents/hooks/inject_memory.py", "timeout": 10}]}]
}}
```

- `Write|Edit|delete`는 정확히 그 세 이름과 일치한다. 셸까지 보려면 `Bash`를 더한다. `UserPromptSubmit`에는 `matcher`를 쓰지 않는다. `type`은 `"command"`만 된다(`hooks/models/config.py:20-78`).
- 스크립트는 stdin으로 JSON을 받는다: 공통 `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `PreToolUse`는 `tool_name`, `tool_input`(`Write`·`Edit`은 `file_path`), `tool_use_id`(`hooks/models/wire.py:205-306`).
- `plan_gate.py`의 규칙: 승인됐으면 출력 없이 종료 0, 아니면 이유를 stderr에 쓰고 **종료 2**. `main()` 전체를 `try`로 감싸 어떤 예외에서도 종료 2로 끝낸다(종료 1이면 편집이 통과한다).
- `inject_memory.py`는 종료 0으로 끝내고 stdout에 일반 텍스트를 쓴다. 그 텍스트가 사용자 메시지 앞의 추가 컨텍스트가 된다.
- 훅 경로는 빠른 시험용이다. 제출물의 게이트와 기록은 3절 권고대로 미들웨어로 만든다.
