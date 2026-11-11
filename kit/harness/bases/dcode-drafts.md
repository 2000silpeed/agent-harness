# dcode 구현 초안 (전부 실행 검증 안 함)

> [`dcode.md`](dcode.md)의 부록이다. 본문의 "부록 A~E"가 이 파일을 가리킨다. 기준은 deepagents-code 0.2.5(수업 저장소 `Day09/deepagents/libs/code`)이고 경로·줄 번호 표기는 본문과 같다.

사본의 기반 클래스·서명·관례를 따라 쓴 초안이다. **한 번도 실행·린트·타입 검사하지 않았다.** 본문 8절 9~11번으로 확인한다. 파일 이름, 폴더 이름, 규칙 ID에 붙는 다음 행동 문구는 제안값이다.

근거로 삼은 사본의 코드: 기반 클래스와 `trace_policy`는 `memory_guard.py:34`, `:95-109`. 훅 서명과 요청 객체는 `memory_guard.py:423-450`, `agent.py:974-1010`. 요청 식별은 `git_trace.py:126-139`. 거부 메시지는 `agent.py:963-972`. 테스트의 요청 객체는 `tests/unit_tests/test_memory_guard.py:36-46`. langchain 소스는 사본에 없어 기반 클래스 자체는 읽지 못했다.

### A. 기록 미들웨어 뼈대 — `deepagents_code/run_log.py` (실행 검증 안 함)

```python
"""Record the tool calls of a thread as JSON lines.

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

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from pathlib import Path

    from langgraph.prebuilt.tool_node import ToolCallRequest
    from langgraph.types import Command

logger = logging.getLogger(__name__)

_UNKNOWN = "unknown"
"""Value used when the run metadata carries no thread or turn id."""


def run_ids(request: ToolCallRequest) -> tuple[str, str]:
    """Read the thread and turn ids the client put in the run metadata.

    Args:
        request: The tool call being processed.

    Returns:
        `(thread_id, turn_id)`, each `"unknown"` when absent.
    """
    runtime = getattr(request, "runtime", None)
    config = getattr(runtime, "config", None) or {}
    metadata = config.get("metadata") or {}
    thread, turn = metadata.get("thread_id"), metadata.get("turn_id")
    return (
        thread if isinstance(thread, str) and thread else _UNKNOWN,
        turn if isinstance(turn, str) and turn else _UNKNOWN,
    )


class RunLogMiddleware(AgentMiddleware):
    """Append one JSON line per tool call to `<log_dir>/<thread_id>.jsonl`.

    A write failure is logged and never fails the tool call.
    """

    trace_policy = TracePolicy(process_inputs=omit_payload)
    """Omit hook inputs from traces by default; set a `TracePolicy` to override."""

    def __init__(self, log_dir: Path, *, agent: str = "main") -> None:
        """Initialize the recorder.

        Args:
            log_dir: Workspace-scoped directory passed in by the graph builder.
            agent: Role name written to every event.
        """
        super().__init__()
        self._log_dir = log_dir
        self._agent = agent

    def _record(
        self,
        request: ToolCallRequest,
        result: ToolMessage | Command[Any] | None,
        error: BaseException | None,
        started: float,
    ) -> None:
        """Append the record for one finished tool call."""
        thread, turn = run_ids(request)
        kind, status, error_type, exit_code = "tool_call", "ok", None, None
        if error is not None:
            status, error_type = "error", type(error).__name__
        elif isinstance(result, ToolMessage):
            artifact = result.artifact if isinstance(result.artifact, dict) else {}
            code = artifact.get("exit_code")
            if isinstance(code, int) and not isinstance(code, bool):
                exit_code = code
            if "gate_rule" in artifact:
                # A gate block is the gate working, not an error.
                kind, status = "gate_block", "blocked"
                error_type = artifact["gate_rule"]
            elif exit_code not in {None, 0}:
                # `execute` reports a failed command as a successful tool call.
                status, error_type = "error", "exit_nonzero"
            elif result.status == "error":
                status, error_type = "error", "tool_error"
        event = {
            "ts": datetime.now(UTC).isoformat(timespec="milliseconds"),
            "session_id": thread,
            "request_id": turn,
            "agent": self._agent,
            "type": kind,
            "name": request.tool_call["name"],
            "tool_call_id": request.tool_call["id"],
            "status": status,
            "error_type": error_type,
            "exit_code": exit_code,
            "duration_ms": int((time.perf_counter() - started) * 1000),
        }
        stem = "".join(ch for ch in thread if ch.isalnum() or ch in "-_")
        path = self._log_dir / f"{stem or _UNKNOWN}.jsonl"
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
- 이벤트 필드는 `../reference/trace.md` 2절의 이름을 따랐다. 빠진 것: `seq`(요청 안 순번. 인스턴스가 여럿일 수 있으니 파일 잠금이나 줄 번호로 정한다), `phase`(호출 시점의 계획 상태에서 계산하는 순수 함수를 따로 둔다), `request_start`·`request_end`·`llm_call` 이벤트(`before_agent`·`after_agent`·`wrap_model_call`. 본문 3절의 fork 주의를 지킨다).
- 결과가 `ToolMessage`가 아니라 `Command`로 올 수 있다. 그 안의 메시지에서 상태를 읽는 예가 `hooks/server_middleware.py:1460-1482`다. 초안은 `Command`를 `ok`로만 적는다.
- 파일 키를 `thread_id`로 둔 이유: 승인 전후로 실행이 나뉘면 `turn_id`가 달라진다. 한 대화의 줄을 한 파일에 모으고 `request_id`로 가른다.
- 린트에 걸릴 수 있는 곳 〔추정〕: `except Exception … raise`, `getattr` 결과의 타입, 한 줄에 여러 값을 대입한 곳. 걸리면 사본의 같은 패턴(`memory_guard.py`, `git_trace.py`)에 맞춘다.

### A2. 계획 게이트 뼈대 — `deepagents_code/plan_gate.py` (실행 검증 안 함)

규격은 `../reference/plan-gate.md` 5~6절이다. 계획은 `design/plans/<plan_id>.md`, 승인 기록은 `design/approvals/<plan_id>.json`이고 승인 기록은 사람이 돌리는 승인 명령만 쓴다.

```python
"""Block file-changing tool calls that no approved plan covers.

The gate trusts only the approval record written by the human-run approve
command. A `status: approved` line in a plan file is not evidence on its own.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from typing import TYPE_CHECKING, Any

import yaml
from langchain.agents.middleware.types import AgentMiddleware, TracePolicy, omit_payload
from langchain_core.messages import ToolMessage

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from pathlib import Path

    from langgraph.prebuilt.tool_node import ToolCallRequest
    from langgraph.types import Command

logger = logging.getLogger(__name__)

GATED_TOOLS: frozenset[str] = frozenset(
    {"write_file", "edit_file", "delete", "execute"}
)
"""Tool names the gate inspects; every other tool passes through."""

PROTECTED: tuple[str, ...] = (
    "design/approvals",
    ".deepagents/runs",
    ".deepagents/memory",
)
"""Workspace-relative paths no tool call may change, even when a plan lists them."""

NEXT_STEPS: dict[str, str] = {
    "plan.approved_required": "Write a plan under design/plans and ask for approval.",
    "plan.multiple_approved": "Ask the user to leave exactly one approved plan.",
    "plan.approval_record_missing": "Ask the user to run the approve command.",
    "plan.approval_stale": "The plan changed; get the new version approved.",
    "scope.outside_plan": "Raise the plan version, add the file, get it approved.",
    "scope.outside_workspace": "Change files inside the workspace only.",
    "protected_path": "This path is protected; do not look for another way in.",
    "reviewer.read_only": "The reviewer reads only; return findings instead.",
    "gate.failure": "The gate could not decide; report this to the user.",
}
"""What the model is told to do next, keyed by rule id."""

_TARGETS_HEADING = "## 수정 대상"


def body_sha256(plan_text: str) -> str:
    """Hash a plan body the way the approve command does.

    Args:
        plan_text: Full text of the plan file, front matter included.

    Returns:
        SHA-256 hex digest of the body with trailing spaces and outer blank
        lines removed.
    """
    body = plan_text.split("---", 2)[-1]
    lines = [line.rstrip() for line in body.strip("\n").splitlines()]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def plan_targets(plan_text: str) -> list[str]:
    """List the first cell of every row in the targets table.

    Args:
        plan_text: Full text of the plan file.

    Returns:
        Workspace-relative paths as written, optionally ending in `/*` or `/**`.
    """
    targets: list[str] = []
    in_section = False
    for line in plan_text.splitlines():
        if line.startswith("## "):
            in_section = line.strip() == _TARGETS_HEADING
        elif in_section and line.lstrip().startswith("|"):
            cell = line.strip().strip("|").split("|")[0].strip().strip("`")
            if cell and cell != "경로" and not set(cell) <= {"-", ":"}:
                targets.append(cell)
    return targets


def _covers(target: str, rel: str) -> bool:
    """Tell whether one plan target covers a workspace-relative path."""
    if target.endswith("/**"):
        return rel.startswith(target[:-2])
    if target.endswith("/*"):
        return rel.startswith(target[:-1]) and "/" not in rel[len(target) - 1 :]
    return rel == target


def approved_targets(root: Path) -> tuple[str | None, list[str]]:
    """Find the single approved plan and return its targets.

    Args:
        root: Resolved workspace directory.

    Returns:
        `(rule_id, targets)`. `rule_id` is `None` when exactly one plan is
        approved and its approval record matches; otherwise it names the rule
        that blocks code changes and `targets` is empty.
    """
    approved: list[tuple[str, Any, str]] = []
    for path in sorted((root / "design" / "plans").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta = yaml.safe_load(text.split("---", 2)[1])
        if meta["status"] == "approved":
            approved.append((path.stem, meta, text))
    if not approved:
        return "plan.approved_required", []
    if len(approved) > 1:
        return "plan.multiple_approved", []
    plan_id, meta, text = approved[0]
    record_path = root / "design" / "approvals" / f"{plan_id}.json"
    if not record_path.is_file():
        return "plan.approval_record_missing", []
    record = json.loads(record_path.read_text(encoding="utf-8"))
    same = (
        record["plan_id"] == plan_id == meta["plan_id"]
        and record["version"] == meta["version"]
        and record["plan_sha256"] == body_sha256(text)
    )
    return (None, plan_targets(text)) if same else ("plan.approval_stale", [])


def check_call(workspace: Path, tool: str, args: dict[str, Any]) -> str | None:
    """Decide one gated tool call.

    Args:
        workspace: Directory the agent works in.
        tool: Native tool name, one of `GATED_TOOLS`.
        args: Tool-call arguments.

    Returns:
        The id of the rule that blocks the call, or `None` when it may run.
    """
    root = workspace.resolve()
    if tool == "execute":
        command = str(args.get("command", "")).casefold()
        if any(path in command for path in PROTECTED):
            return "protected_path"
        return approved_targets(root)[0]
    raw = args.get("file_path")
    if not isinstance(raw, str) or not raw:
        return "gate.failure"
    target = (root / raw).resolve()
    if not target.is_relative_to(root):
        return "scope.outside_workspace"
    rel = target.relative_to(root).as_posix()
    folded = rel.casefold()
    if any(folded == path or folded.startswith(f"{path}/") for path in PROTECTED):
        return "protected_path"
    if rel.startswith("design/") and rel.endswith(".md") and tool != "delete":
        return None
    rule, targets = approved_targets(root)
    if rule is not None:
        return rule
    return None if any(_covers(item, rel) for item in targets) else "scope.outside_plan"


class PlanGateMiddleware(AgentMiddleware):
    """Reject write, edit, delete, and shell calls no approved plan covers."""

    trace_policy = TracePolicy(process_inputs=omit_payload)
    """Omit hook inputs from traces by default; set a `TracePolicy` to override."""

    def __init__(self, workspace: Path | None, *, read_only: bool = False) -> None:
        """Initialize the gate.

        Args:
            workspace: Directory the agent works in. `None` blocks every gated
                call because the gate cannot locate plans.
            read_only: Block every gated call; used for the plan reviewer.
        """
        super().__init__()
        self._workspace = workspace
        self._read_only = read_only

    def _rejection(self, request: ToolCallRequest) -> ToolMessage | None:
        """Return the error result for a blocked call, or `None` to let it run."""
        name = request.tool_call["name"]
        try:
            if self._read_only:
                rule: str | None = "reviewer.read_only"
            elif self._workspace is None:
                rule = "gate.failure"
            else:
                args = request.tool_call.get("args") or {}
                rule = check_call(self._workspace, name, args)
        except Exception:
            # Any failure to decide blocks the call (fail closed).
            logger.exception("Plan gate failed; blocking %s", name)
            rule = "gate.failure"
        if rule is None:
            return None
        return ToolMessage(
            content=f"[{rule}] {NEXT_STEPS[rule]}",
            name=name,
            tool_call_id=request.tool_call["id"],
            artifact={"gate_rule": rule},
            status="error",
        )

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command[Any]]],
    ) -> ToolMessage | Command[Any]:
        """Block the call when the approved plan does not cover it.

        Args:
            request: The tool call being processed.
            handler: The next handler in the middleware chain.

        Returns:
            The tool result, or an error `ToolMessage` naming the blocking rule.
        """
        if request.tool_call["name"] not in GATED_TOOLS:
            return await handler(request)
        rejection = await asyncio.to_thread(self._rejection, request)
        if rejection is not None:
            return rejection
        return await handler(request)
```

- 동기 `wrap_tool_call`도 같은 모양으로 만든다(`asyncio.to_thread` 없이 `self._rejection(request)`).
- 판정 순서는 규격 6절과 같다: 보호 경로 → 작업 폴더 밖 → 계획·설계 문서(`design/` 아래 마크다운) 통과 → 승인된 계획이 정확히 하나, 승인 기록의 `plan_id`·`version`·본문 해시 일치, 경로가 수정 대상 안. 형식이 깨진 계획 파일, 읽기 실패, 키 누락은 예외가 되어 `gate.failure`로 막힌다.
- 초안이 하지 않는 것: 계획 형식 검사(규격 2절. 같은 모듈의 순수 함수로 더하고 승인 명령이 다시 부른다), 시간 제한(`asyncio.wait_for`로 감싸고 초과도 차단), 디렉터리 삭제의 범위 판정, 수정 대상 칸의 경로 정규화 검사(절대 경로·`..`·중간 와일드카드 거부), 계획 상태 변경 이벤트.
- `execute`는 대상 경로를 알 수 없다. 초안은 "보호 경로 문자열이 명령에 있으면 차단, 승인된 계획이 없으면 차단"만 한다. 범위는 끝난 뒤 `git diff --name-only <base_commit>`으로 본다(본문 4절).
- 승인 명령(`scripts/approve_plan.py`, 제안값)이 할 일: 형식 검사를 다시 돌린다 → 게이트가 읽을 수정 대상과 위험 표시를 화면에 보여 준다 → 확인을 받아 `{"plan_id", "version", "plan_sha256", "reviewer_verdict", "approved_by", "approved_at"}`을 쓴다. 같은 `version`에서 본문만 바뀐 재승인과 `version`이 뒤로 가는 승인은 거절한다. 터미널이 아니면 거절한다(방지턱일 뿐이다). `body_sha256`은 이 모듈의 것을 가져다 쓴다.
- `ToolMessage`의 `artifact`에 규칙 ID를 넣어 기록 미들웨어가 `gate_block`으로 남기게 했다. `artifact`가 바깥 미들웨어에서 다르게 쓰이는지는 〔미확인〕이다.
- 린트에 걸릴 수 있는 곳 〔추정〕: `except Exception`(로그를 남기므로 통과할 것으로 본다), `meta["status"]`의 타입, 한글이 든 문자열 상수의 모호한 문자 규칙.

### B. 설치 명령과 넣는 자리 (실행 검증 안 함)

제출용 복사본을 만들고 해설 줄을 지운다. 해설 줄은 전부 `# [해설]`로 시작하는 독립된 줄이다.

```bash
cp -R <수업 저장소>/Day09/deepagents/libs/code <제출 저장소>/libs/code && cd <제출 저장소>/libs/code
grep -rlZ '# \[해설\]' deepagents_code | xargs -0 sed -i.bak '/^[[:space:]]*# \[해설\]/d' && find deepagents_code -name '*.bak' -delete
grep -rc '# \[해설\]' deepagents_code | grep -v ':0$'      # 아무것도 안 나와야 한다
uv venv --python 3.14 .venv                                # 제출 저장소 안에 둔다(.gitignore)
uv pip install --no-sources --python .venv/bin/python -e ".[openrouter]" --group test
```

- 수업 저장소 안에서 돌릴 때는 두 `uv` 명령에 `--no-config`를 붙인다(본문 2절). 저장소 기록에 있는 것은 임시 가상환경에 `--no-sources -e . --group test`를 넣은 조합까지다 〔저장소 실행 기록〕 `Day09/TEST_MAP.md`. extra를 더한 조합은 〔추정〕이다.
- README에는 평가자가 그대로 따라 할 설치 스크립트(위 마지막 두 줄)와 실행 스크립트(`DEEPAGENTS_HOME`을 정하고 `.venv/bin/dcode`를 부른다. 본보기 `Day09/scripts/dcode`)를 적는다.

`agent.py`의 메인 목록: `agent_middleware: list[AgentMiddleware[Any, Any]] = [git_trace, ConfigurableModelMiddleware(...), EmptyTruncatedReplyMiddleware()]` 리터럴(`:3191-3204`) 바로 뒤, `if not interactive:`(`:3205`) 앞.

```python
    # Record tool calls for monitoring. Installed only when the builder knows
    # the workspace directory; the process directory is never consulted.
    if effective_cwd is not None:
        from deepagents_code.run_log import RunLogMiddleware

        agent_middleware.append(
            RunLogMiddleware(Path(effective_cwd) / ".deepagents" / "runs")
        )
    # Inside the recorder so every block is recorded. Without a workspace the
    # gate blocks all gated calls instead of guessing a directory.
    from deepagents_code.plan_gate import PlanGateMiddleware

    agent_middleware.append(PlanGateMiddleware(effective_cwd))
```

서브에이전트: `_subagent_cli_middleware`(`:2989`)에 이름 인자를 하나 더하고, `middleware.append(CodeModelRetryMiddleware(max_retries=model_retries))`(`:3022`) 뒤에 새 인스턴스를 넣는다. 호출하는 두 곳(`:3148`, `:3178`) 중 파일 정의 서브에이전트 쪽에서 `agent_name=subagent_meta["name"]`을 넘긴다.

```python
    def _subagent_cli_middleware(
        *,
        has_explicit_model: bool,
        agent_name: str = "general-purpose",
    ) -> list[AgentMiddleware[Any, Any]]:
        ...
        middleware.append(CodeModelRetryMiddleware(max_retries=model_retries))
        if effective_cwd is not None:
            from deepagents_code.run_log import RunLogMiddleware

            middleware.append(
                RunLogMiddleware(
                    Path(effective_cwd) / ".deepagents" / "runs", agent=agent_name
                )
            )
        from deepagents_code.plan_gate import PlanGateMiddleware

        middleware.append(
            PlanGateMiddleware(effective_cwd, read_only=agent_name == "plan-reviewer")
        )
```

- 기본값(fork)의 `general-purpose`에는 부모 목록이 이름 기준으로 합쳐진다 〔저장소 실행 기록〕. 같은 이름의 두 인스턴스 중 어느 쪽이 남는지는 〔미확인〕이라, 그 경로의 `agent` 값이 `main`으로 찍힐 수 있다. 판정과 파일 위치는 두 인스턴스가 같으므로 차단과 기록 자체는 달라지지 않는다 〔추정〕.
- 이 삽입은 `Path.cwd()`가 든 기존 문장(`:3032`)을 건드리지 않는다. cwd 검사의 허용 목록 항목은 그 문장의 요약값에 묶여 있다(`scripts/check_process_cwd.py:36-56`) 〔코드〕.
- 설치를 증명하는 테스트는 `tests/unit_tests/test_agent.py:3413`, `:3458` 부근의 방식을 따른다: `create_deep_agent`를 가짜로 바꾸고 `kwargs["middleware"]`와 `kwargs["subagents"]`의 `middleware`에 두 클래스가 있는지 본다.

### C. 단위 테스트 (실행 검증 안 함)

`tests/unit_tests/test_run_log.py`

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
    text = (log_dir / "unknown.jsonl").read_text(encoding="utf-8")
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
    assert (event["status"], event["error_type"]) == ("error", "exit_nonzero")
    assert event["exit_code"] == 1


async def test_async_call_is_recorded(tmp_path: Path) -> None:
    """The async wrapper writes the same record as the sync path."""
    middleware = RunLogMiddleware(tmp_path / "runs")

    async def handler(_request: ToolCallRequest) -> ToolMessage:  # noqa: RUF029
        return ToolMessage(content="ok", name="ls", tool_call_id="call-1")

    await middleware.awrap_tool_call(_request("ls"), handler)

    (event,) = _events(tmp_path / "runs")
    assert (event["name"], event["status"], event["exit_code"]) == ("ls", "ok", None)
```

`tests/unit_tests/test_plan_gate.py`

```python
"""Tests for the plan gate."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest

from deepagents_code.plan_gate import PlanGateMiddleware, body_sha256

if TYPE_CHECKING:
    from pathlib import Path

_PLAN = """---
plan_id: p1
version: 1
status: {status}
---
## 수정 대상
| 경로 | 종류 | 이유 |
|---|---|---|
| src/a.py | 수정 | test |
"""


def _blocked_rule(workspace: Path, file_path: str) -> str | None:
    """Run one `edit_file` call through the gate and return the blocking rule."""
    request = ToolCallRequest(
        runtime=cast("Any", None),
        tool_call={"id": "c1", "name": "edit_file", "args": {"file_path": file_path}},
        state={},
        tool=None,
    )

    def handler(_request: ToolCallRequest) -> ToolMessage:
        return ToolMessage(content="ok", name="edit_file", tool_call_id="c1")

    result = PlanGateMiddleware(workspace).wrap_tool_call(request, handler)
    artifact: Any = result.artifact if isinstance(result, ToolMessage) else None
    return artifact["gate_rule"] if artifact else None


def _write_plan(workspace: Path, status: str) -> str:
    plans = workspace / "design" / "plans"
    plans.mkdir(parents=True)
    text = _PLAN.format(status=status)
    (plans / "p1.md").write_text(text, encoding="utf-8")
    return text


def test_edit_without_a_plan_is_blocked(tmp_path: Path) -> None:
    """Code cannot change before any plan is approved."""
    assert _blocked_rule(tmp_path, "src/a.py") == "plan.approved_required"


def test_status_line_alone_is_not_an_approval(tmp_path: Path) -> None:
    """Writing `status: approved` into the plan does not open the gate."""
    _write_plan(tmp_path, "approved")
    assert _blocked_rule(tmp_path, "src/a.py") == "plan.approval_record_missing"


def test_approved_plan_opens_only_its_targets(tmp_path: Path) -> None:
    """A matching approval record lets listed files through and nothing else."""
    text = _write_plan(tmp_path, "approved")
    approvals = tmp_path / "design" / "approvals"
    approvals.mkdir()
    record = {"plan_id": "p1", "version": 1, "plan_sha256": body_sha256(text)}
    (approvals / "p1.json").write_text(json.dumps(record), encoding="utf-8")

    assert _blocked_rule(tmp_path, "src/a.py") is None
    assert _blocked_rule(tmp_path, "src/b.py") == "scope.outside_plan"
    assert _blocked_rule(tmp_path, "design/approvals/p1.json") == "protected_path"
```

- 더할 시험은 `../reference/plan-gate.md` 9절의 목록(PG-01~PG-14)에서 고른다: 승인 뒤 계획 본문 수정(`plan.approval_stale`), 승인된 계획이 둘, 깨진 계획 파일(`gate.failure`), `..`와 심볼릭 링크, 서브에이전트 경로.

### D. `hooks.json` 예 — `{프로젝트 루트}/.deepagents/hooks.json` (실행 검증 안 함)

```json
{"hooks": {
  "PreToolUse": [{"matcher": "Write|Edit|delete", "hooks": [
    {"type": "command", "command": "python3 .deepagents/hooks/plan_gate.py", "timeout": 10}]}],
  "UserPromptSubmit": [{"hooks": [
    {"type": "command", "command": "python3 .deepagents/hooks/inject_memory.py", "timeout": 10}]}]
}}
```

- 매처는 공개 이름이다. 셸까지 보려면 `Bash`를 더한다. `UserPromptSubmit`에는 `matcher`를 쓰지 않는다. `type`은 `"command"`만 되고 `async: true`는 거부된다(`hooks/models/config.py:20-48`) 〔코드〕.
- 스크립트는 stdin으로 JSON을 받는다: 공통 `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `PreToolUse`는 `tool_name`, `tool_input`(`Write`·`Edit`은 `file_path`), `tool_use_id`(`hooks/models/wire.py:200-317`) 〔코드〕.
- `plan_gate.py`의 규칙: 승인됐으면 출력 없이 종료 0, 아니면 이유를 stderr에 쓰고 **종료 2**. `main()` 전체를 `try`로 감싸 어떤 예외에서도 종료 2로 끝낸다(종료 1이면 편집이 통과한다).
- `inject_memory.py`는 종료 0으로 끝내고 stdout에 일반 텍스트를 쓴다. 그 텍스트가 사용자 메시지 앞의 추가 컨텍스트가 된다.
- `-n`에서는 `--trust-project-hooks`를 붙여야 이 파일이 로드된다. 훅 경로는 빠른 시험용이다. 제출물의 게이트와 기록은 본문 3절 권고대로 미들웨어로 만든다.

### E. 가짜 모델 설정 — `<DEEPAGENTS_HOME>/config.toml` (실행 검증 안 함)

모델 호출 없이 도구 호출 경로를 시험할 때 쓴다. 수업 저장소의 `Day09/scripts/trace_dcode.sh:38-52`가 같은 키로 돈다 〔저장소 실행 기록〕.

```toml
[models]
default = "itest:fake"                # 받은 문장을 되돌려주는 모델

[models.providers.itest]
class_path = "deepagents_code._testing_models:DeterministicIntegrationChatModel"
models = ["fake"]

[models.providers.itool]              # 요청문의 표지를 보고 도구 호출을 만드는 모델
class_path = "deepagents_code._testing_models:ToolCallingIntegrationChatModel"
models = ["fake"]
```

- 표지(`_testing_models.py:38-40`) 〔코드〕: `DCA_TEST_WRITE_FILE=<절대경로>`는 메인 에이전트의 `write_file` 호출을, `DCA_TEST_DELEGATE_WRITE=<절대경로>`는 `task` 위임을 만든다. 위임받은 쪽이 실제로 파일을 쓰는 것은 `DEEPAGENTS_CODE_FORKED_SUBAGENTS=0`일 때뿐이다 〔저장소 실행 기록〕.
- 실행 예: `<dcode> -n "DCA_TEST_WRITE_FILE=$PWD/a.py" -M itool:fake --no-tracing --no-mcp < /dev/null`. `HOME`도 임시 폴더로 바꾸면 사용자 쪽 스킬·설정이 섞이지 않는다.
- 이 모델은 `execute`를 부르지 않는다 〔문서〕 `Day09/TRACE_WALKTHROUGH.md` 5절. 셸 경로와 실제 계획 흐름은 실제 모델로 본다.
