# R7. `kit/harness/bases/dcode.md` 정적 검증 (dcode 0.1.69)

> **검증 방식.** 읽기만 했다. 수업 스냅샷(`/home/user/hyunjunjeon/sds_ax_advanced_2026/Day08/dcode-analysis/`)의 코드·문서를 읽고, 공식 문서 1쪽(`docs.langchain.com/oss/deepagents/code/cli-reference`)과 GitHub 커밋 페이지 1쪽을 확인했다. **빌드·설치·린트·테스트·실행은 하나도 하지 않았다.** "린트에 걸린다/통과한다", "이렇게 출력된다"는 전부 코드와 설정을 읽고 낸 추정이다.
> **줄 번호.** 모두 스냅샷의 한국어 해설 주석판 기준이다(원본과 다르다). 경로는 `libs/code/` 기준이고, SDK는 `libs/deepagents/`로 적었다.
> **판정 표기.** 코드로 확인 / 문서로만 확인 / 틀림 / 미확인. "코드로 확인"도 실행해 본 것은 아니다.

---

## 0. 가장 중요한 정정 10개

| # | dcode.md의 내용 | 실제 (근거) | 영향 |
|---|---|---|---|
| 1 | S1 "`dcode -n`과 `--rubric`, 종료 코드로 자동 실행" | **채점 결과는 종료 코드에 반영되지 않는다.** `-n`의 종료 코드는 0(성공·훅이 멈춤) / 1(오류) / 124(`--max-turns`·`--timeout` 초과) / 130(Ctrl-C) / 2(사용법 오류)뿐이다. 채점 결과는 콘솔 문구로만 나온다 (`deepagents_code/client/non_interactive.py:1118-1163`, `:3153-3181`, `main.py:6665`) | 평가 스크립트가 종료 코드만 보면 "기준 미충족"도 통과로 센다. 문구를 읽거나 자체 기록 파일을 봐야 한다 |
| 2 | 4-3 "재시도는 `model_attempt` 이벤트가 원천" | 재시도 신호는 **`model_retry`** 이벤트다. `model_attempt`는 시도의 시작/완료 경계다. 둘 다 서버가 **클라이언트로 보내는 스트림 이벤트**라서 다른 미들웨어가 받아 볼 수 없다 (`model_retry.py:969-1010`, `:1014-1038`, `:1174-1190`) | 기록 미들웨어가 재시도 수를 세려면 직접 모델 호출을 감싸서 세야 한다(§2.5) |
| 3 | 출발 소스 "주석판은 린트에 걸릴 수 있다(확인 필요)" | **거의 확실히 걸린다(추정).** `# [해설]` 주석 4,179줄 중 1,752줄이 88자를 넘는다(한글은 폭 2라 실제 위반은 더 많다). `line-length` 설정이 없어 기본 88이다 (`pyproject.toml:243-285`) | 제출용 저장소는 **원본(커밋 `1d3232c`)에서 시작**하고 주석판은 읽기용으로만 쓴다 |
| 4 | `make bootstrap` | `uv sync --group test` 뒤에 **git 최상위에 pre-commit 훅을 설치**한다(`Makefile:8`, `:101-104`). 스냅샷의 `deepagents/`에는 `.git`·`.github`가 없다(수업 저장소에 파일로 들어 있음). 수업 저장소 안에서 돌리면 수업 저장소에 훅을 깔려고 한다 | `uv sync --group test`를 기본으로 쓴다. `make check`는 `.github/scripts`가 없어 스냅샷에서는 끝까지 못 간다(`Makefile:106-117`) |
| 5 | OpenRouter "정확한 명령은 문서에 없다" | 맞다. 문서의 `dcode --install openrouter`는 **소스(editable) 설치에서 거부된다**(`update_check.py:3996-4003`). extra 이름은 `openrouter`(`pyproject.toml:129`), lock에도 있다(`uv.lock:1158-1160`) | `uv sync --group test --extra openrouter` 한 줄로 해야 한다(실행 미확인). `uv sync`를 extra 없이 다시 돌리면 빠진다 |
| 6 | S5 "서브에이전트의 도구 호출에도 게이트가 걸리는가" (질문으로만 있음) | 코드로 답이 나온다. **파일로 정의한 서브에이전트는 메인 `agent_middleware`를 물려받지 않는다.** `_subagent_cli_middleware()` 목록만 받는다(`agent.py:2885-2944`, SDK `graph.py:726-735`). `general-purpose`만 fork 모드라 부모 미들웨어를 물려받는다(`agent.py:3056-3057`) | 게이트·기록 미들웨어는 **두 곳**(메인 목록 + `_subagent_cli_middleware`)에 넣어야 한다 |
| 7 | 훅 "종료 코드 2가 차단이다" | 이벤트마다 뜻이 다르다. `PreToolUse`는 거부, `UserPromptSubmit`은 프롬프트 차단, `PostToolUse`는 피드백, `Stop`은 계속 진행. **2가 아닌 0 이외 코드와 시간 초과는 차단이 아니고 진단만 남는다(열림)** (`hooks/capabilities.py:100-246`, `hooks/runner.py:157-176`) | 게이트 스크립트가 예외로 죽으면(종료 1) 도구가 그대로 실행된다. 스크립트는 오류 때도 2로 끝내야 한다 |
| 8 | (없음) | 헤드리스에서 **훅 왕복(인터럽트)이 turn으로 세어진다.** 기본 한도 50, 넘으면 종료 124 (`non_interactive.py:174`, `:2412-2440`). `PreToolUse` 핸들러가 하나라도 있으면 매처와 무관하게 서버가 왕복한다(`hooks/server_middleware.py:898-899`) | 훅으로 게이트를 만들면 `--max-turns`를 넉넉히 줘야 한다. 미들웨어 게이트는 이 비용이 없다 |
| 9 | (없음) | `execute`는 실패해도 **`status="success"`** 로 돌아온다. 종료 코드는 `artifact["exit_code"]`와 본문 끝 `[Command failed with exit code N]`에 있다(SDK `middleware/filesystem.py:2922-2941`, `:3047-3053`) | "테스트 실패"를 `status`로 판정하면 놓친다 |
| 10 | 함정 7 "실행한 폴더의 `AGENTS.md`…도 읽는다" | 기준은 실행 폴더가 아니라 **`.git`이 있는 상위 폴더(프로젝트 루트)** 다(`_git.py:136-160`, `project_utils.py:76-98`). `.git`이 없으면 프로젝트 메모리·스킬·서브에이전트가 **로드되지 않는다** | 시연 폴더는 `git init`된 별도 폴더여야 한다. dcode 모노레포 안에서 실행하면 모노레포의 `AGENTS.md`·`.agents/skills`·`.mcp.json`이 섞인다 |

---

## 1. CLI 플래그 (argparse, `deepagents_code/main.py`)

typer가 아니라 argparse다. 정의는 `parse_args()` 안에 있다.

| 플래그 | 정의 위치 | 형식·기본값 | 비고 |
|---|---|---|---|
| `-n`, `--non-interactive TEXT` | `main.py:2768-2775` | `dest=non_interactive_message` | 파이프 stdin도 같은 경로. `--stdin`(`:2867-2871`) |
| `-S`, `--shell-allow-list LIST` | `main.py:2936-2944` | 쉼표 목록, `recommended`, `all` | 환경 변수 `DEEPAGENTS_CODE_SHELL_ALLOW_LIST`(`_env_vars.py:615`). `-n`과 대화형 모두 적용 |
| `--rubric TEXT\|@PATH` | `main.py:2831-2840` | `@`로 시작하면 항상 파일. 12,000자 제한(`goal_state_limits.py:29`) | 경로는 프로세스 cwd 기준, `~` 지원(`main.py:1645-1661`). 빈 값·읽기 실패는 종료 2(`:6598-6604`) |
| `--rubric-model MODEL` | `main.py:2841-2847` | 기본은 메인 모델 | |
| `--rubric-max-iterations N` | `main.py:2848-2855` | 1 이상. 기본 3(`reliable_rubric.py:166`) | 줘야만 콘솔에 반복 번호가 나온다(`non_interactive.py:3144`) |
| `-a`, `--agent NAME` | `main.py:2652-2663` | 없으면 `[agents].default` → `[agents].recent` → `agent`(`_constants.py:13`) | |
| `--max-turns N` | `main.py:2801-2809` | 1 이상. 없으면 내부 기본 50 | 초과 시 **124**(`non_interactive.py:3159-3168`) |
| `--timeout SECONDS` | `main.py:2811-2820` | 1 이상 | 초과 시 **124**(`main.py:6654-6665`) |
| `--trust-project-hooks` | `main.py:2962-2967` | store_true | 헤드리스는 저장된 신뢰를 **무시**한다. 매번 줘야 한다(`hooks/trust.py:414-438`) |
| `--trust-project-mcp` | `main.py:2956-2961` | store_true | |
| `--mcp-config PATH` | `main.py:2945-2950` | Claude Desktop 형식 JSON | `--no-mcp`와 함께 쓰면 종료 2(`:5944-5953`) |
| `-s`, `--skill NAME` | `main.py:2750-2756` | `dest=initial_skill` | `-n`과 함께 쓸 수 있다(`non_interactive.py:2859-`) |
| `-y`, `--auto-approve` | `main.py:2878-2887` | 분류기 기반 Auto 모드 | **`-y`는 `--yolo`의 짧은 이름이 아니다** |
| `--yolo` | `main.py:2888-2896` | 무승인 | `-y`와 상호 배타. 헤드리스에서는 둘 다 **경고 후 무시**(`:5923-5941`) |
| `-q`, `--quiet` | `main.py:2778-2784` | 답변만 stdout, 나머지는 stderr | `-q`면 사용량 표도 안 나온다(`non_interactive.py:2523-2544`) |
| `--no-stream` | `main.py:2786-2792` | 답변을 한 번에 출력 | |
| `--json` | `output.py:18-46`, `main.py:2873` | 기본 `text` | **`-n` 실행에는 쓰이지 않는다.** `run_non_interactive` 호출에 넘기지 않는다(`main.py:6610-6649`). `agents`·`threads`·`tools`·`skills`·`update` 같은 관리 명령 전용 |
| `-M`, `--model MODEL` | `main.py:2667-2673` | `provider:model` | |
| `--max-retries N` | `main.py:2692-2701` | 0이면 끔. 기본 5(`config.py:3459`) | |
| `--interpreter` / `--no-interpreter` | `main.py:2983-2989` | 샌드박스가 없으면 기본 켜짐 | `js_eval`. §2.6 주의 |
| `--allow-fs-tools LIST` | `main.py:2998-3008` | `all` 또는 목록(`read_file` 필수) | 서브에이전트에도 적용 |
| `--goal TEXT` | `main.py:2823-2830` | 대화형 전용 | `-n`과 함께 쓰면 종료 2 |

**자동 평가에 쓸 수 있는 출력.**
- `-n` 전용 JSON 출력은 **없다**(코드와 공식 문서 모두). 쓸 수 있는 것은 ① 종료 코드, ② `-q`로 분리한 stdout(답변)/stderr(상태), ③ 콘솔 문구, ④ `dcode threads list --json`, ⑤ 체크포인트 DB `~/.deepagents/.state/sessions.db`와 내장 스킬 `deepagents-thread-inspector`의 `scripts/inspect_sessions.py`(`built_in_skills/deepagents-thread-inspector/SKILL.md`)다.
- 채점 문구(`non_interactive.py:1118-1163`): `Acceptance criteria satisfied` / `Acceptance criteria not yet satisfied` / `… (iteration limit reached)` / `Rubric is invalid or cannot be evaluated` / `Acceptance criteria check failed`.
- 끝 문구(`non_interactive.py:2538-2544`, `_session_stats.py:1388-1465`): `Task completed`, `Usage Stats` 표(Provider, Model, Reqs, InputTok, OutputTok, Cost), `Agent active <시간>`. 표는 `DEEPAGENTS_CODE_SHOW_USAGE_STATS=0`으로 끈다.
- 저장소 문서 일부에 헤드리스를 `-x`/`--execute`라고 쓴 곳이 남아 있다(`AGENTS.md:3`, `_env_vars.py:669-675`). 이 버전의 실제 플래그는 `-n`이다.

**헤드리스의 승인 동작 (`non_interactive.py:2747-2751`, `:3005-3014`).**
- `-S` 없음: 셸 꺼짐, **나머지 도구(파일 쓰기·편집·삭제 포함)는 전부 자동 승인.**
- `-S 목록` 또는 `recommended`: 셸 켜짐, 명령은 허용 목록으로 검사, 다른 도구는 자동 승인.
- `-S all`: 모든 명령 허용.
- 허용 목록은 `&&`, `||`, `|`, `;`로 나눈 **각 구간의 첫 토큰**을 본다. 리다이렉트·명령 치환 같은 패턴이 있으면 거부한다(`config.py:4566-4626`). 예: `uv run pytest -q`는 `uv`가 있으면 통과, `pytest > out.txt`는 거부, `cd x && pytest`는 `cd`도 있어야 한다.
- 거부되면 도구가 실행되지 않고 오류 메시지가 모델에 돌아간다(`agent.py:923-957`).

---

## 2. 미들웨어 확장 경로

### 2.1 기반 클래스와 훅 이름
- 기반 클래스: `from langchain.agents.middleware.types import AgentMiddleware` (`agent.py:53-58`, `memory_guard.py:34`, `model_retry.py:35`, `resume_state.py:71-78`). 같은 모듈에서 `TracePolicy`, `omit_payload`, `AgentState`, `PrivateStateAttr`, `ContextT`, `ModelRequest`, `ModelResponse`도 가져온다.
- `ToolCallRequest`는 `langgraph.prebuilt.tool_node`, `Command`는 `langgraph.types`(`memory_guard.py:46-47`).
- 이 버전의 저장소 미들웨어가 실제로 쓰는 훅(전수 조사, grep):

| 훅 | 서명 (저장소에서 쓰는 형태) | 쓰는 곳 |
|---|---|---|
| `before_agent` / `abefore_agent` | `(self, state, runtime) -> dict[str, Any] \| None`. `config`를 셋째 인자로 받는 형태도 있다 | `cost_tracking.py:2318-2343`, `plugins/adapters/skills_middleware.py:318-323`, SDK `middleware/memory.py:279`, `:313` |
| `before_model` / `abefore_model` | `(self, state, runtime)` | `goal_tools.py`, `hooks/server_middleware.py` |
| `wrap_model_call` / `awrap_model_call` | `(self, request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse` (비동기는 `Awaitable`) | `model_retry.py:1229-1323` 외 다수 |
| `after_model` / `aafter_model` | `(self, state, runtime) -> dict[str, Any] \| None` | `resume_state.py:318-346`, `cost_tracking.py:2345-2349` |
| `wrap_tool_call` / `awrap_tool_call` | `(self, request: ToolCallRequest, handler: Callable[[ToolCallRequest], ToolMessage \| Command[Any]]) -> ToolMessage \| Command[Any]` | `memory_guard.py`(끝부분), `agent.py:960-998` |
| `after_agent` / `aafter_agent` | `(self, state, runtime) -> dict[str, Any] \| None` | `cost_tracking.py:2371-2375`, `hooks/server_middleware.py` |

- 저장소의 모든 미들웨어가 `wrap_*`는 **동기·비동기 둘 다** 정의한다. 서버 그래프는 비동기 경로로 돈다(`model_retry.py:1280` 주석 "서버 그래프의 기본 실행 경로"). 노드형 훅(`after_model` 등)은 동기만 둔 예가 있다(`resume_state.py`의 `ResumeStateMiddleware`).
- **미확인:** `AgentMiddleware` 자체의 소스(langchain 패키지)는 스냅샷에 없어서 읽지 못했다. 위 서명은 하위 클래스에서 역으로 확인한 것이다. `wrap_*`를 동기만 정의했을 때 비동기 실행에서 오류가 나는지는 실행해야 안다.

### 2.2 본보기: `ShellAllowListMiddleware` (`agent.py:880-998`)
게이트의 가장 작은 실제 예다. 핵심만 옮긴다(원문 그대로, 해설 주석 제외).

```python
class ShellAllowListMiddleware(AgentMiddleware):
    trace_policy = TracePolicy(process_inputs=omit_payload)
    """Omit hook inputs from traces by default; set a `TracePolicy` to override."""

    def _validate_tool_call(self, request: ToolCallRequest) -> ToolMessage | None:
        ...
        if request.tool_call["name"] != "execute":
            return None
        args = request.tool_call.get("args") or {}
        command = args.get("command", "")
        if is_shell_command_allowed(command, self._allow_list):
            return None
        return LCToolMessage(
            content=(...),
            name="execute",
            tool_call_id=request.tool_call["id"],
            status="error",
        )

    def wrap_tool_call(self, request, handler):
        if (rejection := self._validate_tool_call(request)) is not None:
            return rejection
        return handler(request)

    async def awrap_tool_call(self, request, handler):
        if (rejection := self._validate_tool_call(request)) is not None:
            return rejection
        return await handler(request)
```

- 거부는 **예외가 아니라 `status="error"`인 `ToolMessage`를 돌려주는 것**이다. 모델이 이유를 읽고 다음 행동을 정한다.
- 파일 I/O가 있는 예는 `memory_guard.py`의 `ManagedMemoryGuardMiddleware`다. 비동기 쪽에서 `await asyncio.to_thread(self._read, path)`로 블로킹 I/O를 스레드로 넘긴다(파일 끝부분 `awrap_tool_call`).

### 2.3 `create_cli_agent`에서 넣을 자리 (`agent.py`)

| 위치 | 줄 | 내용 |
|---|---|---|
| 함수 정의 | `2570` | `def create_cli_agent(` |
| 작업 폴더 계산 | `2823-2827` | `effective_cwd` (`cwd` 인자 → `project_context.user_cwd` → `None`) |
| 서브에이전트용 묶음 | `2885-2944` | `_subagent_cli_middleware()` |
| **메인 목록 시작** | **`3073-3079`** | `agent_middleware: list[...] = [ConfigurableModelMiddleware(...)]` |
| 재개·비용·목표 | `3114-3116` | `ResumeStateMiddleware(), CostTrackingMiddleware(), GoalToolsMiddleware()` |
| 메모리 | `3133-3165` | `MemoryMiddleware`, `ManagedMemoryGuardMiddleware` |
| 스킬 | `3169-3179` | `PluginSkillsMiddleware` |
| 셸 허용 목록 | `3281-3282` | `ShellAllowListMiddleware` |
| 사람 승인 | `3406-3438` | `AutoModeHITLMiddleware` 또는 `AsyncApprovalHITLMiddleware` |
| 훅 | `3447-3449` | `ServerHooksMiddleware(cwd=hooks_cwd, ...)` |
| 재시도 | `3555-3560` | `CodeModelRetryMiddleware`, `ToolErrorMiddleware` |
| 채점 | `3695` | `ReliableRubricMiddleware` |
| SDK 호출 | `3748-3760` | `create_deep_agent(..., middleware=agent_middleware, ...)` |

- 순서 규칙: **목록 앞쪽이 바깥쪽**이다(`agent.py:3063` 해설, LangChain 규칙). SDK가 이 목록을 자기 core(Filesystem → SubAgent → Summarization → PatchToolCalls) **뒤**, 프롬프트 캐싱 **앞**에 끼운다(SDK `graph.py:204-238`, `:928`). 이름(`.name`, 기본은 클래스 이름)이 core와 같으면 그 자리를 대체하고, 중복 이름은 허용되지 않는다(`agent.py:3405`, `:3435-3437`).
- **안전한 삽입 지점 (권고).**
  - 기록 미들웨어: `3079`(목록 리터럴) 바로 뒤. dcode 쪽 미들웨어 중 가장 바깥이라 안쪽에서 거부된 결과까지 본다.
  - 계획 게이트: `3282` 뒤 ~ `3406` 앞(사람 승인보다 바깥). 승인 창이 뜨기 전에 거부된다.
  - 재시도 횟수를 서버에서 세려면: `3560` 뒤(재시도 미들웨어 안쪽)에 모델 호출을 감싸는 작은 미들웨어를 하나 더 둔다. 안쪽은 시도마다, 바깥쪽은 호출마다 한 번 불린다.
  - 서브에이전트에도 적용: `2916`(재시도) 근처에서 `_subagent_cli_middleware`의 `middleware` 목록에도 **새 인스턴스**를 넣는다.
- `after_agent`는 목록 **역순**으로 실행된다(`agent.py:3101-3104` 원문 주석). 요약 지표를 `after_agent`에서 쓰면, 목록 앞쪽에 둔 미들웨어가 가장 나중에 돈다(채점 뒤).
- `check_process_cwd.py`의 허용 목록은 "문장 내용의 해시"로 묶여 있다(`scripts/check_process_cwd.py:36-55`). `create_cli_agent`에 줄을 **추가**하는 것은 기존 항목을 깨지 않는다. `hooks_cwd = ... Path.cwd()` 같은 **기존 문장을 고치면** 토큰이 바뀌어 "unreviewed"와 "stale"이 같이 뜬다.

### 2.4 작업 폴더를 `Path.cwd()` 없이 얻는 법
- 금지 대상(`scripts/check_process_cwd.py:1-20`, `:147-187`): `Path.cwd()`, `pathlib.Path.cwd()`, `os.getcwd()`, `from os import getcwd`의 `getcwd()`, 그리고 **`find_project_root(...)` 호출 전부**(인자가 있어도 잡힌다). `Path(".").resolve()`, `os.path.abspath(".")`는 못 잡지만 같은 이유로 쓰면 안 된다.
- `make lint`의 마지막 줄이 이 검사다(`Makefile:76`). 허용 목록에 없는 호출이 하나라도 있으면 종료 1.
- 기존 코드가 쓰는 두 방법:
  1. **조립할 때 받는다.** `create_cli_agent`가 `effective_cwd`를 계산해 생성자에 넘긴다: `ServerHooksMiddleware(cwd=hooks_cwd, ...)`(`agent.py:3447-3448`). 그래프는 작업 폴더(워크스페이스)마다 따로 조립된다(`server_graph.py:601-631`, `:922-940`).
  2. **실행할 때 읽는다.** `CLIContextSchema.from_payload(runtime.context)`의 `workspace["cwd"]`(`offload_middleware.py:888-895`, `agent.py:1941-1943`). 같은 컨텍스트에 `thread_id`, `turn_id`, `prompt_id`도 있다(`_cli_context.py:63-91`). 도구 감싸기에서는 `request.runtime.context`, `request.runtime.config`로 접근한다(`hooks/server_middleware.py:452-457`).
- 새 코드는 `effective_cwd`가 `None`이면 **미들웨어를 설치하지 않는** 쪽이 안전하다(대체로 `Path.cwd()`를 부르지 않는다).

### 2.5 커스텀 스트림 이벤트
- 방출: `request.runtime.stream_writer(event_dict)`(`model_retry.py:1174-1190`). writer가 없으면 건너뛰고, `GraphBubbleUp`은 다시 던지고, 그 밖의 오류는 경고만 남긴다.
- `model_attempt`: `{"type": "model_attempt", "phase": "start"|"complete", "call_id": <hex>, "attempt": <0부터>}`(`model_retry.py:1014-1038`). 모델 호출 한 번의 모든 시도가 같은 `call_id`를 쓴다.
- `model_retry`: `{"type": "model_retry", "attempt": <1부터>, "max_retries", "message", "call_id", "failed_attempt", "output_may_have_started"}`(`model_retry.py:969-1010`).
- 헤드리스 클라이언트는 `model_retry`, `model_attempt`, 채점 이벤트만 처리하고 **모르는 type은 조용히 버린다**(`non_interactive.py:1705-1744`, `:1089-1091`). 직접 만든 이벤트는 화면에도 파일에도 남지 않는다. **기록은 미들웨어가 직접 파일에 쓴다.**

### 2.6 미들웨어 작성 때 코드에서 읽히는 제약
1. **이벤트 루프에서 블로킹 I/O 금지.** 서버는 `langgraph dev --no-browser --no-reload`로 뜨고(`client/launch/server.py:425-431`) `--allow-blocking`을 주지 않는다. 런타임이 Blockbuster로 블로킹 호출을 잡는다(`pyproject.toml:94-96`, `:189-191`, `server_graph.py:266`, `:395`, `:465`). `async def` 훅 안의 파일 쓰기는 `asyncio.to_thread`로 넘긴다. (실행 미확인)
2. **인터럽트를 오류로 세지 않는다.** 안쪽 미들웨어(승인, 훅)가 인터럽트를 걸면 `GraphBubbleUp` 계열 예외가 올라오고, 재개되면 도구 감싸기가 **다시 호출된다.** `except GraphBubbleUp: raise`를 먼저 둔다(`model_retry.py:637-639`가 같은 처리). (재호출 횟수는 실행 미확인)
3. **`execute` 실패는 `status`가 아니라 `artifact["exit_code"]`** 로 판정한다(§0-9).
4. **`delete` 도구가 있다.** 파일을 바꾸는 도구는 `write_file`, `edit_file`, `delete`, `execute` 네 개다(`agent.py:1001-1003`, SDK `filesystem.py:1470`). 게이트가 앞의 둘만 보면 뚫린다.
5. **`js_eval`의 도구 호출(PTC)은 승인 경로를 거치지 않는다**(`agent.py:2708-2718`). 기본 허용 목록 `safe`는 읽기 전용이라 기본값에서는 문제가 없다. 미들웨어 `wrap_tool_call`도 우회하는지는 **미확인**이다. 시연에서는 `--no-interpreter`가 안전하다.
6. **fork 서브에이전트는 부모 미들웨어 인스턴스를 그대로 쓴다**(SDK `graph.py:727-730`). 인스턴스에 요청별 상태를 두면 부모와 섞인다. 상태는 thread/turn id로 키를 잡는다.

---

## 3. 린트 설정

### 3.1 `make lint`가 실제로 돌리는 것 (`Makefile:62-80`)
`PYTHON_FILES=.`(= `libs/code` 전체: 패키지, tests, scripts, examples), `UV_FROZEN=true`.

```bash
uv run --all-groups ruff check .
uv run --all-groups ruff format . --diff
uv run --all-groups ty check .
uv run --all-groups python scripts/generate_commands_catalog.py --check
uv run --all-groups python scripts/check_process_cwd.py deepagents_code
```

- `make lint_package`는 범위만 `deepagents_code`로 줄인다(뒤 두 줄은 같다). `make format`은 `ruff format .` → `ruff check --fix .`(`Makefile:82-85`).
- `ruff`, `ty`는 **`test` 의존성 그룹**에 있다(`pyproject.toml:169-177`). `uv run ruff …`만 쓰면 그룹이 빠질 수 있으니 `--all-groups`나 `--group test`를 붙인다.

### 3.2 ruff 설정 (`pyproject.toml:243-343`)
- `preview = true`, `select = ["ALL"]`.
- `ignore`: `C90`, `COM812`, `CPY`, `FBT`, `FIX002`, `ISC001`, `PERF203`, `PLC0414`, `PLC0415`(지연 import 허용), `PLR09`, `PLR1702`, `PLW0717`, `noqa-comments`, `rule-codes-in-selectors`, `SLF001`, `TD002`, `TD003`.
- `ban-relative-imports = "all"`, isort `known-first-party = ["deepagents_code"]`, `combine-as-imports = true`.
- pydocstyle `convention = "google"`, `ignore-var-parameters = true`. 포매터 `docstring-code-format = true`, `docstring-code-line-length = 100`.
- **`line-length` 설정이 없다 → 기본 88.** 상위에 다른 ruff 설정 파일도 없다(스냅샷에서 확인).
- `per-file-ignores`: `tests/**`(ANN001, ANN201, D1, DOC, F401, PLC0415, PLC1901, PLC2701, PLR2004, PLR6201, PLR6301, PLW0108, RUF001, RUF076, S, SLF), `scripts/**`(BLE001, INP, S, T201), `examples/**`, `deepagents_code/built_in_skills/**/scripts/**`.
- 타입 검사: **`ty`** (`>=0.0.61,<0.0.62`). `python-version = "3.12"`, `extra-paths`에 `../deepagents`와 partners, 규칙 `division-by-zero = "error"`, `unused-ignore-comment = "ignore"`(`pyproject.toml:222-241`).
- pytest: `filterwarnings = ["error", ...]`(**경고가 곧 실패**), `asyncio_mode = "auto"`, `timeout = 30`, `--strict-markers --strict-config`(`pyproject.toml:347-395`).

### 3.3 새 코드가 지켜야 하는 것 (기존 코드에서 읽은 관례, 추정 포함)
- 모듈 첫 줄 docstring, `from __future__ import annotations`, 타입 전용 import는 `if TYPE_CHECKING:` 안(`memory_guard.py:24-47`).
- 모든 인자·반환에 타입. `Any`를 인자 타입으로 쓰면 `# noqa: ANN401`.
- 훅 서명 때문에 안 쓰는 인자는 `# noqa: ARG002`, `self`를 안 쓰는 훅은 `# noqa: PLR6301`(`resume_state.py:318-321`).
- 예외 메시지는 변수에 담아 던진다: `msg = "..."; raise ValueError(msg)`(`model_retry.py:1157-1167`).
- 로그는 `logger = logging.getLogger(__name__)`와 `%s` 형식. `print` 금지. 넓은 `except Exception`은 `exc_info=True`로 남기거나 다시 던진다(`model_retry.py:1183-1190`).
- docstring은 Google 형식. 기존 코드는 `Args:`/`Returns:`/`Raises:`를 쓰고, `Returns:`만 있는 짧은 형태도 통과한다(`memory_guard.py`의 `wrap_tool_call`). preview의 DOC 규칙이 켜져 있어 **반환·예외가 있으면 해당 구역이 있어야 한다**(추정). `__init__`에도 docstring이 있다.
- 억제 주석은 `# noqa: CODE  # 이유`와 `# ruff:ignore[rule-name] - 이유` 두 형태가 다 쓰인다(`hooks/models/domain.py:6-19`).
- 슬래시 명령을 추가하면 `make commands-catalog`, CLI 플래그를 추가하면 `ui.show_help()`도 고친다(`AGENTS.md` "CLI help screen", 테스트 `test_args.TestHelpScreenDrift`).

### 3.4 `# [해설]` 주석이 규칙에 걸리는가 — **추정이다. 돌려 보지 않았다.**

읽어서 센 것(`grep`, 코드포인트 기준):

| 항목 | 값 |
|---|---|
| `[해설]`이 들어간 줄 (`deepagents_code/**/*.py`) | 4,179줄, 35개 파일 (전체 258개 중) |
| 그중 88자 초과 | 1,752줄 |
| 그중 60~88자 (한글 폭 2를 치면 상당수가 88 초과) | 1,783줄 |
| 모양 | 전부 줄 전체 주석 `# [해설]…`. 코드 뒤에 붙은 주석 0, 빈 `# [해설]` 0 |
| 주석 속 비ASCII 기호 | `→` 805, `─` 547, `·` 519, `—` 143, 그 밖 소수(`↔ ①②③ ★ ≤ ∪ ∈ ± − – ×` 등) |
| tests / scripts / SDK의 `[해설]` | 0 |

| 규칙 | 추정 | 근거 |
|---|---|---|
| **E501 줄 길이** | **걸린다. 최소 약 1,750건, 많으면 3,000건 이상** | 기본 88. 원본 코드의 88자 초과 줄은 pragma 주석이 붙은 줄이나 공백 없는 한 단어 줄뿐이라 예외에 해당한다(표본 확인). 주석 줄은 예외가 아니다 |
| RUF003 (주석의 혼동 문자) | 소수(10건 이하로 추정) | `→`(9줄), `—`(556줄)는 원본 주석에도 억제 없이 쓰인다. 한글은 대상이 아니다. `−`, `–`, `×` 같은 기호 몇 개만 후보다. `─`, `·`는 원본에 없어 판단 근거가 없다 |
| ERA001 (주석 처리된 코드) | 거의 없음 | 모든 줄이 `[해설]`로 시작해 파이썬 문장으로 읽히지 않는다 |
| `ruff format --diff` | 영향 없음 | 포매터는 주석을 줄바꿈하지 않는다 |
| `ty`, `check_process_cwd.py`, 명령 목록 검사 | 영향 없음 | AST 기준이라 주석을 보지 않는다 |

결론(추정): **주석판에서 `make lint`는 E501 때문에 실패한다.** 제출용은 원본에서 시작한다. 원본은 `git clone https://github.com/langchain-ai/deepagents` 후 `git checkout 1d3232c0852c47af09119edea10eeec887e4f0da`(GitHub에서 커밋 제목 `release(deepagents-code): 0.1.69 (#6247)` 확인).

새로 쓰는 코드의 한국어 주석·docstring도 같은 규칙을 받는다. 한글은 한 글자가 폭 2로 계산되므로 **한 줄에 한글 약 40자**가 한도다(추정).

---

## 4. 훅 (`hooks.json`)

### 4.1 스키마 (`hooks/models/config.py:20-78`)
```text
{"hooks": { <이벤트 이름>: [ {"matcher": <문자열|생략>, "hooks": [ <핸들러> ]} ] }}
핸들러: {"type": "command", "command": <셸 문자열>, "argv": [..]?, "timeout": <초, 0 초과>?, "statusMessage": <문자열>?}
```
- `type`은 `"command"`만 된다. `async: true`는 로드 때 거부된다. 모르는 키는 무시된다.
- 위치: `~/.deepagents/hooks.json`(항상), `{프로젝트 루트}/.deepagents/hooks.json`(신뢰 후), 플러그인의 `hooks/hooks.json`(`HOOKS.md:9-13`, `hooks/loading.py:153-173`).
- 이벤트 12종(`hooks/models/domain.py:36-50`): `SessionStart`, `UserPromptSubmit`, `SessionEnd`, `PermissionRequest`, `Notification`(클라이언트 소유) / `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PreCompact`, `Stop`, `SubagentStart`, `SubagentStop`(서버 소유).
- 매처(`hooks/snapshot.py:41`, `:209-236`): 생략·빈 문자열·`*`는 전부 일치. 글자·공백·`,`·`-`·`|`만 있으면 **정확히 일치하는 이름 목록**(`|`나 `,`로 구분). 다른 문자가 있으면 **앵커 없는 정규식**. `UserPromptSubmit`과 `Stop`은 매처를 쓸 수 없다(`*` 외에는 로드 때 진단).
- 도구 이름은 wire 이름으로 맞춘다(`hooks/tools.py:68-76`): `execute→Bash`, `write_file→Write`, `edit_file→Edit`, `read_file→Read`, `glob→Glob`, `grep→Grep`, `ls→LS`, MCP는 `mcp__<서버>__<도구>`. **`delete`, `task`, `web_search`, `fetch_url`, `js_eval` 등은 원래 이름 그대로**다.
- 기본 시간 제한(`hooks/capabilities.py:82`, `:122`): **600초**, `UserPromptSubmit`만 **30초**.
- 실행 위치와 환경: 클라이언트 프로세스에서, 세션 작업 폴더를 cwd로 실행한다. 이름이 비밀처럼 보이는 환경 변수는 빠진다(`hooks/env.py:19-33`). stdout·stderr는 각각 100,000바이트까지만 읽는다(`hooks/runner.py:31`).

### 4.2 stdin 페이로드 (`hooks/models/wire.py`)
- 공통(`:205-217`): `session_id`, `transcript_path`, `cwd`, `hook_event_name`, 선택 `prompt_id`, `permission_mode`, `effort`, `agent_id`, `agent_type`.
- `PreToolUse`(`:276-283`): `tool_name`, `tool_input`, `tool_use_id`.
- `PostToolUse`(`:286-294`): 위에 `tool_response`, `duration_ms`. `PostToolUseFailure`(`:297-306`): `error`, `is_interrupt`, `duration_ms`.
- `UserPromptSubmit`(`:231-235`): `prompt`.
- `Stop`(`:317-324`): `stop_hook_active`, `last_assistant_message`.
- `tool_input`은 wire 형태로 바뀐다(`hooks/tools.py:19-65`): `Write`는 `file_path`, `content` / `Edit`은 `file_path`, `old_string`, `new_string`, `replace_all` / `Bash`는 `command`, `timeout`(밀리초). 매핑이 없는 도구(`delete` 등)는 원래 인자 그대로.
- `transcript_path`는 `~/.deepagents/transcripts/<thread_id>.jsonl`이다(`hooks/runtime.py:126-130`, `hooks/transcript.py:180-189`). 훅이 실행될 때 만들어진다.

### 4.3 출력 해석 (`hooks/runner.py:157-206`, `hooks/reducer.py`)
- **종료 2:** stdout JSON은 무시하고 stderr를 이유로 쓴다. 뜻은 이벤트별: `PreToolUse`·`PermissionRequest` 거부 / `UserPromptSubmit`·`PreCompact` 차단 / `PostToolUse`·`PostToolUseFailure` 피드백 / `Stop` 계속 진행(연속 8회까지, `reducer.py:56`) / `SubagentStop` 부모 컨텍스트에 추가 / `SessionStart`·`SessionEnd`·`Notification`·`SubagentStart` 진단만(`hooks/capabilities.py:100-246`).
- **그 밖의 0 아닌 종료, 시간 초과:** 진단만 남고 **결정은 적용되지 않는다(도구가 실행된다).**
- **종료 0 + JSON stdout**(`wire.py:483-499`): `continue`, `stopReason`, `systemMessage`, `suppressOutput`, `decision: "block"`, `reason`, `hookSpecificOutput`.
  - `PreToolUse`(`wire.py:381-396`): `hookSpecificOutput.permissionDecision`이 `allow`/`deny`/`ask`, `permissionDecisionReason`, `additionalContext`. `defer`와 `updatedInput`은 지원하지 않는다(진단, `reducer.py:336-349`). 여러 핸들러면 `deny > ask > allow` 순으로 이긴다(`reducer.py:55`).
  - `UserPromptSubmit`(`wire.py:368-378`): `additionalContext`, `suppressOriginalPrompt`.
- **종료 0 + JSON이 아닌 stdout:** `SessionStart`·`UserPromptSubmit`에서는 **추가 컨텍스트**가 된다. 다른 이벤트에서는 진단이다(`reducer.py:103-117`).
- 거부되면 모델은 `"<wire 이름> blocked by hook: <이유>"`라는 오류 `ToolMessage`를 받는다(`hooks/server_middleware.py:1297-1308`).
- 헤드리스에서 `UserPromptSubmit` 컨텍스트는 사용자 메시지 **바로 앞에 `role: system` 메시지**로 들어간다(`non_interactive.py:2372-2389`). 시스템 프롬프트를 고치는 것이 아니다.

### 4.4 신뢰
- 사용자 훅은 항상 로드. 프로젝트 훅은 대화형에서 묻고, "항상 허용"은 `~/.deepagents/.state/hooks_trust.json`에 남는다(`HOOKS.md:19-25`).
- **헤드리스는 저장된 신뢰를 보지 않는다.** `--trust-project-hooks`를 준 실행만 프로젝트 훅을 로드한다(`hooks/trust.py:414-438`, `non_interactive.py:3041`).
- 신뢰 단위는 프로젝트 루트(없으면 작업 폴더)다(`hooks/trust.py:327-338`).

### 4.5 서브에이전트 안에서 뜨는 이벤트 (`agent.py:2919-2933`)
- 서브에이전트마다 `ServerHooksMiddleware(cwd=hooks_cwd, emit_stop=False, mcp_tools=mcp_tools)`가 붙는다. 따라서 **`PreToolUse`, `PostToolUse`, `PostToolUseFailure`는 서브에이전트 안의 도구 호출에도 뜬다.**
- **`Stop`은 서브에이전트에서 뜨지 않는다**(`emit_stop=False`).
- `SubagentStart`·`SubagentStop`은 부모가 `task` 도구를 감쌀 때 뜬다(`hooks/server_middleware.py:541-569`, `:797-823`). 매처는 서브에이전트 이름이다.
- 서브에이전트 안에서 온 이벤트에는 `agent_id`, `agent_type`이 채워진다(wire 공통 필드). **실제로 채워지는지는 실행 미확인.**

### 4.6 헤드리스에서 훅의 비용
- 서버 소유 이벤트는 인터럽트로 클라이언트에 왕복한다(`hooks/server_middleware.py:1-6`).
- 헤드리스 루프는 인터럽트 한 번을 turn 하나로 센다. 한도는 `--max-turns` 또는 기본 50, 넘으면 종료 124(`non_interactive.py:174`, `:2409-2440`).
- 서버는 "그 이벤트에 핸들러가 있는가"만 보고 왕복한다. 매처는 클라이언트가 적용한다(`hooks/server_middleware.py:898-914`). `PreToolUse` 핸들러가 하나 있으면 매처가 `Write`여도 다른 도구 호출까지 왕복한다(추정. 모델 스텝당 한 번인지 도구 호출당 한 번인지는 **실행 미확인**).
- `PermissionRequest` 핸들러가 있으면 헤드리스의 자동 승인 지름길이 꺼진다(`non_interactive.py:3046-3050`).

---

## 5. 메모리

| 항목 | 사실 | 근거 |
|---|---|---|
| 소스 조립 | `memory_sources = [~/.deepagents/<에이전트>/AGENTS.md]` + 프로젝트 `AGENTS.md`들 | `agent.py:3133-3140` |
| 프로젝트 `AGENTS.md` | `{프로젝트 루트}/.deepagents/AGENTS.md`, `{프로젝트 루트}/AGENTS.md` **둘 다** 있으면 둘 다. 루트 밖을 가리키는 심링크는 건너뜀 | `project_utils.py:150-190` |
| 프로젝트 루트 | `.git`이 있는 가장 가까운 상위 폴더. 없으면 `None` → 프로젝트 메모리 없음 | `_git.py:136-160`, `project_utils.py:76-80` |
| 사용자 파일 자동 생성 | 없으면 빈 `AGENTS.md`를 만든다 | `agent.py:2831-2837` |
| 대화당 한 번 로드 | `if "memory_contents" in state: return None`. 상태는 thread별로 체크포인트된다 | SDK `middleware/memory.py:293-295`, `:327-329` |
| 주입 방식 | 매 모델 호출 때 시스템 메시지 끝에 전문을 붙인다. 검색 없음. HTML 주석은 제거 | SDK `middleware/memory.py:245-277`, `:347-361` |
| `auto_save` 설정 | `config.toml`의 `[memory] auto_save`(기본 `true`), 환경 변수 **`DEEPAGENTS_CODE_MEMORY_AUTO_SAVE`** | `config_manifest.py:2596-2608`, `_env_vars.py:438`, `config.py:4781-4796` |
| 끄면 | 로드는 계속하고 프롬프트만 읽기 전용판으로 바뀐다. 편집 도구는 그대로라 직접 편집은 가능 | `agent.py:186`, `:3142-3154`, docstring `:2689-2697` |
| `-a NAME` | `~/.deepagents/NAME/AGENTS.md`, `~/.deepagents/NAME/skills/`, `~/.deepagents/NAME/agents/`가 따로 생긴다. 프로젝트 쪽 파일은 공유 | `_paths.py:295-297`, `:309-311`, `:342-344` |
| 복사·초기화 | `dcode agents reset --agent X [--target Y] [--dry-run]` — Y의 `AGENTS.md`를 X로 복사 | `main.py:2420-2434`, `agent.py:1426-1438` |
| 프로필 통째 분리 | `DEEPAGENTS_HOME=<절대경로>` — `~/.deepagents` 아래 전부(설정, 훅, 메모리, 세션 DB)가 옮겨진다 | `_paths.py:78`, 공식 문서 `configuration.md:169-177` |
| `/remember` | 내장 스킬 `remember`가 있다. `auto_save`가 꺼져도 동작한다 | `built_in_skills/remember/SKILL.md`, `COMMANDS.md`, `agent.py:2692-2694` |
| 보호 미들웨어 | 사용자 `AGENTS.md`의 온보딩 이름 구역만 보호한다. 나머지 편집은 막지 않는다 | `memory_guard.py:1-22` |
| `memories/` 폴더 | 자동으로 쌓는 코드가 없다(문서에만 있음) | 문서 `memory-and-skills.md:27`, 코드 grep |

---

## 6. 서브에이전트

- 파일: `{agents_dir}/<폴더 이름>/AGENTS.md`. `agents/<이름>.md`처럼 폴더 없이 두면 경고 후 무시된다(`subagents.py:197-225`).
- 위치: 사용자 `~/.deepagents/<에이전트>/agents/`, 프로젝트 `{프로젝트 루트}/.deepagents/agents/`. 이름이 같으면 프로젝트가 이긴다(`agent.py:2873-2878`, `subagents.py:250-273`).
- 파서(`subagents.py:67-170`): 정규식 `^---\s*\n(.*?)\n---\s*\n?(.*)$`로 머리말을 떼고 `yaml.safe_load`. 읽는 키는 **`name`(선택, 없으면 폴더 이름), `description`(필수), `model`(선택, 문자열)** 셋뿐이다. 본문이 시스템 프롬프트다. 형식이 틀리면 경고 로그만 남기고 건너뛴다.
- **도구 제한 불가.** 로더가 `tools`를 읽지 않고(`subagents.py:128-130`), 조립 때도 넣지 않는다(`agent.py:2995-2999`). SDK는 `tools`가 없으면 부모 도구를 물려준다(SDK `graph.py:758-760`). 파일 도구와 `execute`는 서브에이전트 자체 `FilesystemMiddleware`로 들어간다(SDK `graph.py:692-699`). 즉 **리뷰어 서브에이전트도 파일을 쓰고 셸을 돌릴 수 있다.** 줄이는 방법은 전역 `--allow-fs-tools`뿐이다(`agent.py:3463-3495`).
- 모델: `model`이 있으면 `models.allowed` 정책을 검사하고(걸리면 실행 자체가 실패), 없으면 실행 중 메인 모델을 따른다(`agent.py:2993-3021`, `:2896-2903`).
- **fork 모드:** 파일로 정의한 서브에이전트는 fork가 아니다(독립 컨텍스트, 자기 시스템 프롬프트). **`general-purpose`만** 기본으로 fork다. 환경 변수 `DEEPAGENTS_CODE_FORKED_SUBAGENTS`(기본 켜짐)로 끈다(`agent.py:3045-3060`, `_env_vars.py:288`). fork는 부모 대화와 부모 미들웨어를 물려받는다.
- 서브에이전트가 받는 dcode 미들웨어(`agent.py:2885-2944`): 승인, 모델 선택, 비용(`nested=True`), 재시도, (있으면) 셸 허용 목록, 훅(`emit_stop=False`), 메모리 보호. **메모리·스킬 미들웨어는 없다**(fork 제외).

---

## 7. 스킬

- 소스와 우선순위(`agent.py:2491-2553`), **낮은 것 → 높은 것**(이름이 같으면 뒤가 이긴다):
  1. 내장 `deepagents_code/built_in_skills/` (`remember`, `skill-creator`, `deepagents-thread-inspector`)
  2. 플러그인
  3. 사용자 `~/.deepagents/<에이전트>/skills/`
  4. 사용자 `~/.agents/skills/`
  5. 프로젝트 `{루트}/.deepagents/skills/`
  6. 프로젝트 `{루트}/.agents/skills/`
  7. 사용자 `~/.claude/skills/` (실험적, 있을 때만)
  8. 프로젝트 `{루트}/.claude/skills/` (실험적)
  추가로 `DEEPAGENTS_CODE_EXTRA_SKILLS_DIRS`가 있다(`_env_vars.py:326`, 상세 미확인).
- 머리말(SDK `middleware/skills.py:373-473`): `name`(필수), `description`(필수), 선택 `license`, `compatibility`, `metadata`, `allowed-tools`.
- `allowed-tools`는 **표시만 된다.** 쓰이는 곳은 프롬프트 목록과 화면 출력뿐이다(SDK `skills.py:879-880`, `skills/commands.py:135-137`, `context_doctor.py:128-129`).
- 목록은 대화당 한 번 로드(`plugins/adapters/skills_middleware.py:331`, `:380`).
- 호출: 대화형 `/skill:<이름>`(`command_registry.py:516-527`), 실행 시 `-s/--skill NAME`(`-n`과 함께 가능).

---

## 8. 이미 있는 추적·지표

| 항목 | 사실 | 근거 |
|---|---|---|
| LangSmith 켜기 | 키(`LANGSMITH_API_KEY` 또는 `LANGCHAIN_API_KEY`)와 추적 플래그(`LANGSMITH_TRACING=true` 등)가 **둘 다** 있어야 한다. `/auth`로 저장한 키는 자동으로 켠다 | `config.py:4636-4657`, `:977`, `DEVELOPMENT.md` "LangSmith tracing projects" |
| 프로젝트 이름 | `DEEPAGENTS_CODE_LANGSMITH_PROJECT` → `LANGSMITH_PROJECT` → `deepagents-code`. 설정 파일은 `[tracing] langsmith_project` | `config.py:4639-4666`, `_env_vars.py:391` |
| 그 밖 | `DEEPAGENTS_CODE_LANGSMITH_TRACING=false`로 끔, `DEEPAGENTS_CODE_LANGSMITH_REDACT`, 대화형 `/trace` | `config.py:1869-1870`, `_env_vars.py:394` |
| 추적 태그 | 재개 라운드에 `dcode:resume` 태그 | `_tracing.py:21-58` |
| 재시도 | `CodeModelRetryMiddleware`. 기본 5회, `--max-retries` 또는 `[retries]` | `model_retry.py:1118-1323`, `config.py:3459` |
| 비용·토큰 | `CostTrackingMiddleware`가 `_session_cost_usd` 상태를, `ResumeStateMiddleware`가 `_context_tokens`를 체크포인트에 쓴다. 대화형 `/cost`, `/tokens` | `cost_tracking.py:2294-2390`, `resume_state.py`, `COMMANDS.md` |
| 세션 통계 | 클라이언트가 모델별 요청 수·입출력 토큰·비용을 모아 끝에 표로 출력 | `_session_stats.py:207-250`, `:1388-1465` |
| 대화 기록 | `~/.deepagents/transcripts/<thread_id>.jsonl`. **훅이 설정돼 있을 때** 만들어진다 | `hooks/runtime.py:126-130` |
| 체크포인트 DB | `~/.deepagents/.state/sessions.db`. `dcode threads list [--json]`, 내장 스킬의 `inspect_sessions.py` | `sessions.py:344-358`, `built_in_skills/deepagents-thread-inspector/SKILL.md` |
| 디버그 로그 | `DEEPAGENTS_CODE_DEBUG=1` → 클라이언트 `/tmp/deepagents_debug/<thread-id>.log`, 서버 `$TMPDIR/deepagents_server_log_*.txt`(종료 때 경로를 stderr에 출력). 위치는 `DEEPAGENTS_CODE_DEBUG_DIRECTORY` | `DEVELOPMENT.md` "Debugging", `_env_vars.py:148-218` |

단계 표시(계획/리뷰/코드 변경/테스트/결과)를 붙이는 코드는 없다(grep 수준 확인).

---

## 9. OpenRouter

- extra 이름: **`openrouter`** = `langchain-openrouter>=0.2.8,<2.0.0`(`pyproject.toml:129`). lock에 `langchain-openrouter 0.2.8`이 있다(`uv.lock:2907-2916`).
- 키: `OPENROUTER_API_KEY`(`model_config.py:989`). 엔드포인트 변수 `OPENROUTER_API_BASE`(`model_config.py:1210`).
- 모델 문자열: `openrouter:<모델>`(공식 문서 `providers.md:176`). 예: `-M openrouter:<벤더>/<모델>`. **과제 모델의 정확한 OpenRouter ID는 미확인**(OpenRouter에서 확인).
- 문서의 설치 경로: 대화형 `/install openrouter`, 셸 `dcode --install openrouter`(`providers.md:179-188`). 이는 `uv tool`로 설치한 배포판 기준이다.
- **소스(editable) 설치에서는 거부된다.** 메시지: `Editable install detected — cannot add extras automatically.` + `uv tool install --editable … --with 'deepagents-code[openrouter]'` 안내(`update_check.py:3916-3928`, `:3996-4003`).
- 키 우선순위(공식 문서 `credentials.md:103-111`, 코드 `model_config.py:60-75`, `:102-146`): **`DEEPAGENTS_CODE_OPENROUTER_API_KEY` > `/auth` 저장 키 > `OPENROUTER_API_KEY`**.
- 금지 모델을 코드로 막는 방법: `config.toml`의 `[models] allowed = [...]`. 메인·채점·Auto 분류기·서브에이전트 모델 문자열이 모두 검사된다(`agent.py:2957-2984`, `:3006-3013`, `:3653-3654`). `"openrouter:*"` 같은 와일드카드는 문서 예시에만 있다(`config-file.md:153-159`, 코드 미확인).

---

## 10. 테스트

- 위치: `tests/unit_tests/`(네트워크 차단), `tests/integration_tests/`. 단위 테스트는 대체로 `test_<모듈>.py`로 평평하게 놓이고, `hooks/`, `client/`, `skills/`, `plugins/`, `tui/`, `tools/`, `smoke_tests/` 하위 폴더가 있다.
- 실행(`Makefile:25-28`): `uv run --group test pytest -n auto --benchmark-disable --disable-socket --allow-unix-socket $(TEST_FILE) --cov=deepagents_code --cov-report=term-missing`. 파일 하나: `make test TEST_FILE=tests/unit_tests/test_x.py`.
- `conftest.py`(987줄)의 autouse 픽스처가 환경 변수 복원, LangSmith·Tavily 키 제거, 사용자 훅 설정 격리 등을 한다(`tests/unit_tests/conftest.py:100-490`).
- **따라 할 예: `tests/unit_tests/test_memory_guard.py`**(테스트 17개).
  - 요청 만들기(`:35-45`): `ToolCallRequest(runtime=cast("Any", None), tool_call={"id": "call-1", "name": tool_name, "args": {...}}, state={}, tool=None)`.
  - 동기(`:52-73`): 가짜 `handler`를 넘겨 `middleware.wrap_tool_call(request, handler)`를 직접 부르고 `result.status`와 파일 내용을 확인.
  - 비동기(`:165-182`): `async def test_…`를 그대로 쓴다(`asyncio_mode = "auto"`). 가짜 핸들러에 `# noqa: RUF029`.
  - `tmp_path`를 쓴다. 실제 홈 디렉터리를 건드리지 않는다.
- 모델 호출을 감싸는 미들웨어의 예는 `tests/unit_tests/test_model_retry.py`(837줄, `SimpleNamespace`와 가짜 `BaseChatModel` 사용).
- cwd 검사 자체의 테스트: `tests/unit_tests/test_process_cwd_check.py`(7개).

---

## 11. dcode.md 주장별 판정

### 1절 한눈에 보기
| 주장 | 판정 | 근거·메모 |
|---|---|---|
| ruff 전체 규칙, google docstring, 상대 import 금지, `make lint`/`make format` | 코드로 확인 | `pyproject.toml:247-249`, `:275-276`, `:283-285`, `Makefile:70-85` |
| 도구 단위 사람 승인 | 코드로 확인 (대화형만) | `agent.py:2863-2871`, `:3406-3438`. **`-n`에서는 없다**(§1) → 문구 보강 필요 |
| `/goal`의 수락 기준 초안과 채점 | 코드로 확인 | `COMMANDS.md`, `main.py:2823-2830`, `agent.py:3499-3541` |
| 파일로 정의하는 서브에이전트 | 코드로 확인 | `subagents.py` |
| 계획 모드가 없다 | 코드로 확인 (부재) | `plan mode`/`plan_mode`/`/plan` grep 0건. `wire.py:36`의 `PLAN`은 호환용 값 |
| `AGENTS.md` 주입, `/remember`, 이름별 메모리 | 코드로 확인 | §5 |
| 검색이 없다(한 번 로드, 전문 주입) | 코드로 확인 | SDK `memory.py:293-295`, `:347-361` |
| LangSmith, 재시도 이벤트, 비용·토큰, 훅용 기록, 체크포인트 DB | 코드로 확인 | §8. **내장 조회 스킬과 사용량 표가 빠져 있다** |
| 단계 단위 기록이 없다 | 코드로 확인 (부재, grep 수준) | |

### 2절 환경과 빌드
| 주장 | 판정 | 근거·메모 |
|---|---|---|
| WSL, 수업 폴더 밖 | 문서로만 확인 | `Day07/dcode_task.md:15`. `Day06/task.md`는 읽지 않음 |
| 모노레포 유지, 경로 참조 | 코드로 확인 | `pyproject.toml:213-220`, `:224-231`. 스냅샷에 `libs/deepagents`, `libs/acp`, `libs/partners/{daytona,modal,quickjs,runloop,vercel}` 모두 있음 |
| `libs/code`만 떼면 빌드가 깨질 수 있다(확인 필요) | 코드로 확인 (설정상), 실행 미확인 | uv 소스가 `../deepagents` 등 경로라 없으면 해석 실패 |
| `deepagents==0.7.14` (`pyproject.toml:30`), 수업 환경 0.7.32 | 코드로 확인 | 수업 저장소 `pyproject.toml:15`, `uv.lock:916-917` |
| Python 3.12 이상 (`pyproject.toml:13`) | 코드로 확인 | `>=3.12,<4.0` |
| OpenRouter, 금지 모델, 테스트 모델 | 문서로만 확인 | `Day07/dcode_task.md:6-9` |
| 주석판은 린트에 걸릴 수 있다(확인 필요) | **추정: 걸린다** | §3.4 |
| `make bootstrap` | 코드로 확인, **부작용 누락** | §0-4 |
| `uv run deepagents-code`, 소스 수정이 다음 실행에 반영 | 문서로만 확인 | `DEVELOPMENT.md` Quickstart. `--no-reload`라 재시작해야 반영(`server.py:431`) |
| `make lint` = 린트 + 타입 검사 | 코드로 확인, **불완전** | 명령 목록 검사와 cwd 검사도 돈다(`Makefile:75-76`) |
| `make test TEST_FILE=…` | 코드로 확인 | `Makefile:15`, `:25-28` |
| `dcode -n "요청"` 매번 새 대화 | 코드로 확인 | `non_interactive.py:2962`. 단 소스 빌드에서는 `dcode`가 PATH에 없다 → `uv run dcode` |
| `-S "pytest,uv,git"`, 허용 목록이 있어야 셸이 켜진다 | 코드로 확인 | `non_interactive.py:3005-3006` |
| OpenRouter는 `langchain-openrouter`와 `OPENROUTER_API_KEY` 필요, 정확한 명령은 문서에 없다 | 코드로 확인 | §9 |
| `/auth` 저장 키가 환경 변수보다 먼저 | 문서로만 확인 (코드 일부) | `credentials.md:103-111`. **접두 변수가 더 앞선다는 점이 빠짐** |
| `DEEPAGENTS_CODE_DEBUG=1` → `/tmp/deepagents_debug/` | 코드로 확인 | `_env_vars.py:148`, `:218` |

### 3절 끼어들 수 있는 자리
| 주장 | 판정 | 근거·메모 |
|---|---|---|
| `create_cli_agent`(2570줄 근처)의 `agent_middleware` | 코드로 확인 | 정의 `agent.py:2570`, 목록 `:3073` |
| 서버 프로세스에서 돈다 | 코드로 확인 | `server_graph.py:601` |
| `Path.cwd()`를 쓰면 `make lint` 실패 | 코드로 확인 | `Makefile:76`. `os.getcwd()`, `find_project_root()`도 대상 |
| 훅 위치 두 곳 | 코드로 확인 | `hooks/loading.py:153-173`. 플러그인 훅도 있음 |
| 이벤트 12종 | 코드로 확인 | `hooks/models/domain.py:36-50` |
| 프로젝트 훅 신뢰, `--trust-project-hooks` | 코드로 확인 | `main.py:2962-2967`, `hooks/trust.py:414-438` |
| 종료 코드 2가 차단이다 | **부정확** | 이벤트별로 다르고 다른 실패는 열림(§4.3) |
| `execute→Bash`, `write_file→Write`, `edit_file→Edit` | 코드로 확인, 불완전 | `hooks/tools.py:68-76`. `delete`는 그대로 |
| 스킬 위치, 대화당 한 번, `allowed-tools` 미강제, `/skill:<이름>` | 코드로 확인 | §7 |
| 서브에이전트 위치, 머리말 `name`, `description`, 선택 `model` | 코드로 확인, 사소한 정정 | `name`도 선택이다 |
| 머리말로 도구·미들웨어 설정 불가 | 코드로 확인 | `subagents.py:128-130` |
| 메모리 위치 세 곳, 한 번 로드, 전문 주입 | 코드로 확인 | §5. "루트"는 프로젝트 루트(.git) |
| `auto_save`가 켜져 있으면 모델이 직접 고친다 | 코드로 확인 (프롬프트 수준) | `agent.py:3144-3154` |
| `/goal`, `/rubric`, `--rubric "기준"`, `--rubric @파일` | 코드로 확인 | `main.py:2831-2840`, `:1645-1661` |
| 헤드리스에는 목표 리뷰 화면이 없다 | 코드로 확인 | `--goal`은 `-n`에서 종료 2 |

### 4절 구현 지도
| 주장 | 판정 | 근거·메모 |
|---|---|---|
| 1-1 `uv run ruff check deepagents_code/<새 모듈>` | 부정확 | `ruff`는 `test` 그룹. `--all-groups` 필요할 수 있음. 포맷 검사도 같이 |
| 1-3 `_tracing.py`가 docstring 예시 | 코드로 확인 | `_tracing.py:24-49` |
| 2-1 `--rubric @계획파일` | 코드로 확인, 주의 | 12,000자 제한, 파일 전체가 기준으로 읽힌다 |
| 2-4 도구 감싸기 또는 `PreToolUse`로 거부하고 이유를 돌려준다 | 코드로 확인 (가능) | `agent.py:948-957`, `hooks/server_middleware.py:1297-1308`. 구멍: `delete`, `execute`, 서브에이전트, `js_eval` |
| 3-2 시스템 프롬프트가 아니라 메시지로 | 미확인 (설계 권고) | 훅 경로는 실제로 메시지로 들어간다(`non_interactive.py:2380-2387`). 캐시 영향은 측정 필요 |
| 3-4 `-a/--agent`로 메모리 분리 | 코드로 확인 | §5. 프로젝트 쪽 파일은 공유된다는 점이 빠짐 |
| 4-3 재시도는 `model_attempt`가 원천 | **틀림** | §0-2 |
| LangSmith는 외부 키 필요 | 코드로 확인 | `config.py:4653-4657` |

### 5절 진행 순서
| 주장 | 판정 | 근거·메모 |
|---|---|---|
| S1 `dcode -n`, `--rubric`, 종료 코드로 자동 실행 | **부정확** | §0-1 |
| S2 기록 미들웨어를 목록 앞쪽에 | 코드로 확인 (가능) | §2.3 |
| S5 서브에이전트에도 게이트가 걸리는가 | 코드로 답 확인: 자동으로는 안 걸린다 | §0-6 |

### 6절 함정
| # | 판정 | 메모 |
|---|---|---|
| 1 | 코드로 확인 | `check_process_cwd.py:1-20` |
| 2 | 코드로 확인 | |
| 3 | 코드로 확인, 보강 필요 | 저장된 신뢰 무시, turn 한도 |
| 4 | 코드로 확인 | |
| 5 | 코드로 확인 | `agent.py:3209-3214`(`virtual_mode=False`). 헤드리스에서 `-y`/`--yolo`는 무시된다 |
| 6 | 코드로 확인 | `Makefile:75`, `AGENTS.md` "Slash commands" |
| 7 | 부정확 | §0-10 |
| 8 | 부분 확인 | Auto는 헤드리스에 설치되지 않는다(`agent.py:2657-2659`). 채점 모델 기본은 메인 모델 |

### 7절 문서와 코드가 다른 곳
| 주장 | 판정 | 메모 |
|---|---|---|
| `memories/` 자동 메모리는 코드에 없다 | 코드로 확인 | 문서 `memory-and-skills.md:27` |
| 확장 미들웨어: 문서 `/reload`, 실제 `/restart` | 문서로만 확인 | 공식 문서 `extensions.md:114`는 `/reload`, 저장소 `EXTENSIONS.md`는 `/restart`·"next server rebuild". `/reload`가 그래프를 다시 조립하는지 코드는 읽지 않음 |
| 한도에 닿으면 "최대 반복 도달" | 코드로 확인 | SDK `rubric.py:75-94`, `non_interactive.py:1143-1148`. 문서 문구는 대조하지 않음 |
| 스킬 계층 실제 8개 | 코드로 확인 | `agent.py:2497-2500` |
| `PostToolUseFailure`가 문서에 빠짐 | 코드로 확인 | 공식 문서 `hooks.md:134-147` 표는 11행. 저장소 `HOOKS.md:49-62`는 12행 |

---

## 12. 고칠 문장 (그대로 바꿔 넣을 수 있는 형태)

**① 1절 표, "2 계획·리뷰·승인"의 "이미 있는 것"**
> 대화형 실행의 도구 단위 사람 승인(화면 없는 실행 `-n`에는 없다. `-n`은 셸만 허용 목록으로 막고 파일 쓰기·편집·삭제는 자동 승인한다), `/goal`의 수락 기준 초안과 채점, 파일로 정의하는 서브에이전트

**② 1절 표, "4 모니터링"의 "이미 있는 것"**
> LangSmith 연동, 모델 재시도, 비용·토큰 집계와 실행 끝의 사용량 표, 훅용 대화 기록(`~/.deepagents/transcripts/`, 훅이 설정돼 있을 때만), 체크포인트 DB(`~/.deepagents/.state/sessions.db`)와 이를 읽는 내장 스킬 `deepagents-thread-inspector`

**③ 2절 표, "출발 소스"**
> **원본에서 시작한다.** `git clone https://github.com/langchain-ai/deepagents` 후 `git checkout 1d3232c0852c47af09119edea10eeec887e4f0da`(dcode 0.1.69). 수업 저장소의 해설 주석판은 읽기용으로만 쓴다. 주석판은 `# [해설]` 주석 약 4,200줄 중 1,700줄 이상이 줄 길이 한도(88자)를 넘어 `make lint`가 실패할 것으로 보이고(읽어서 낸 추정), `.git`이 없어 원본과 비교도 할 수 없다.

**④ 2절 명령 블록**
```bash
cd libs/code
uv sync --group test --extra openrouter   # 개발 환경 + OpenRouter. extra 없이 uv sync를 다시 돌리면 OpenRouter가 빠진다
uv run dcode --version                    # deepagents-code 0.1.69, 소스 경로가 함께 나온다
uv run deepagents-code                    # 소스로 실행. 소스를 고친 뒤에는 다시 실행해야 반영된다
make lint                                 # ruff check, ruff format --diff, ty, 명령 목록 검사, cwd 검사
make format                               # ruff format + 자동 수정
make test TEST_FILE=tests/unit_tests/test_x.py

# 시연은 git init 된 별도 폴더에서. dcode는 소스 폴더의 가상환경으로 부른다
cd /path/to/demo && git init
uv run --project /path/to/deepagents/libs/code dcode -n "요청" -S "pytest,uv,git" --max-turns 40 --timeout 900
```
> - `make bootstrap`은 쓰지 않는다. 의존성 설치 뒤 git 최상위에 pre-commit 훅(커밋 메시지 형식 검사, `main` 직접 커밋 금지 등)을 설치한다.
> - `-S`의 허용 목록은 `&&`, `|`, `;`로 나눈 각 구간의 첫 단어를 본다. 리다이렉트(`>`)나 `$(…)`가 있으면 거부된다. `uv run pytest`는 `uv`만 있으면 통과한다.
> - 화면 없는 실행은 셸만 막는다. 파일 쓰기·편집·삭제는 승인 없이 실행된다.

**⑤ 2절 OpenRouter·키 문장**
> - OpenRouter extra 이름은 `openrouter`다. 문서의 `dcode --install openrouter`는 소스 설치에서 거부되므로 `uv sync --group test --extra openrouter`로 넣는다(직접 돌려 확인하고 README에 적는다). 모델은 `-M openrouter:<모델 ID>` 형식이다.
> - 키는 `DEEPAGENTS_CODE_OPENROUTER_API_KEY` > `/auth`로 저장한 키 > `OPENROUTER_API_KEY` 순으로 쓰인다. 모델이 엉뚱하게 잡히면 접두 변수로 덮어쓴다.
> - 금지 모델은 `~/.deepagents/config.toml`의 `[models] allowed = [...]`로 막는다. 메인·채점·서브에이전트 모델이 모두 검사된다.

**⑥ 3절 표, 미들웨어 행의 "어디에 두나"와 "주의"**
> `libs/code/deepagents_code/agent.py`의 `create_cli_agent`가 만드는 `agent_middleware` 목록(원본 기준으로 `agent_middleware: list[` 를 검색한다)에 추가한다. **서브에이전트에도 걸려면 같은 함수 안의 `_subagent_cli_middleware()` 목록에도 넣는다**(파일로 정의한 서브에이전트는 메인 목록을 물려받지 않는다). 새 모듈은 `deepagents_code/` 아래.
>
> 주의: 서버 프로세스에서 돈다. `Path.cwd()`, `os.getcwd()`, `find_project_root()`를 쓰면 `make lint`가 실패한다. 작업 폴더는 `create_cli_agent`의 `effective_cwd`를 생성자로 받거나 `CLIContextSchema.from_payload(runtime.context).workspace["cwd"]`로 읽는다. `wrap_*`는 동기·비동기 둘 다 만든다. 비동기 훅 안의 파일 쓰기는 `asyncio.to_thread`로 넘긴다. 목록 앞쪽이 바깥쪽이다.

**⑦ 3절 표, 훅 행의 "주의"**
> 이벤트 12종. 프로젝트 훅은 신뢰 승인이 필요하고, 화면 없는 실행은 저장된 승인을 보지 않으므로 **매번 `--trust-project-hooks`** 가 필요하다. `PreToolUse`에서 종료 코드 2(또는 JSON `permissionDecision: "deny"`)가 거부다. **2가 아닌 실패와 시간 초과는 거부가 아니라 통과**이므로 스크립트는 오류 때도 2로 끝낸다. 매처는 `Bash`, `Write`, `Edit` 같은 공개 이름을 쓰고 `delete`는 원래 이름 그대로다. 화면 없는 실행에서는 훅 왕복이 turn으로 세어지므로(기본 한도 50, 초과 시 종료 124) `--max-turns`를 넉넉히 준다.

**⑧ 3절 표, 서브에이전트 행**
> `{프로젝트 루트}/.deepagents/agents/<이름>/AGENTS.md` (머리말에 `description` 필수, `name`·`model` 선택) | 계획 리뷰어(독립 컨텍스트, 다른 모델 지정 가능) | 머리말로 도구·미들웨어를 설정할 수 없다. **부모의 파일 쓰기·셸 도구를 그대로 갖는다.** 리뷰어가 파일을 고치지 못하게 하려면 게이트를 서브에이전트에도 건다

**⑨ 3절 표, 메모리 행의 "어디에 두나"**
> `~/.deepagents/<에이전트>/AGENTS.md`, `{프로젝트 루트}/.deepagents/AGENTS.md`, `{프로젝트 루트}/AGENTS.md` (프로젝트 루트 = `.git`이 있는 상위 폴더. 없으면 프로젝트 쪽은 로드되지 않는다)

**⑩ 4절 1-1의 README 확인 방법**
> `cd libs/code && uv run --all-groups ruff check deepagents_code/<새 모듈>.py tests/unit_tests/test_<새 모듈>.py` 가 `All checks passed!`, `uv run --all-groups ruff format --check <같은 파일>` 이 변경 0건, `make lint` 종료 코드 0

**⑪ 4절 4-3**
> 요청이 끝날 때 요약: 총 시간, 모델·도구 호출 수, 재시도 수, 토큰. dcode의 재시도 신호(`model_retry` 이벤트)는 화면으로만 가고 다른 미들웨어가 받을 수 없다. 재시도 수는 재시도 미들웨어 **안쪽**에서 모델 호출을 감싸 "시도 수 − 호출 수"로 센다. 못 세면 빈값으로 둔다. dcode가 끝에 찍는 사용량 표(Reqs, InputTok, OutputTok)는 대조용으로 쓴다

**⑫ 4절 4-1/4-2에 한 줄 추가**
> `execute`는 명령이 실패해도 결과 상태가 `success`다. 테스트 실패는 결과의 `artifact["exit_code"]`(또는 본문 끝의 `[Command failed with exit code N]`)로 판정한다

**⑬ 5절 S1**
> 고정 작업 5건. `dcode -n`과 `--rubric`으로 자동 실행한다. **종료 코드는 채점 결과를 담지 않는다**(0 성공, 1 오류, 124 turn·시간 초과). 통과 여부는 출력의 `Acceptance criteria satisfied` 문구나 자체 기록 파일로 판정한다 | 평가가 명령 한 줄로 다시 돈다

**⑭ 5절 S5**
> 계획 양식 → 리뷰어 서브에이전트 → 게이트. 게이트를 `_subagent_cli_middleware()`에도 넣었는가. `delete`와 `execute`(셸로 파일 수정)도 막는가 | 승인 전 편집과 계획 밖 편집이 메인과 서브에이전트 양쪽에서 막힌다

**⑮ 6절 함정 3, 7, 8**
> 3. 화면 없는 실행(`-n`)에서는 셸에 허용 목록(`-S`)이, 프로젝트 훅에 `--trust-project-hooks`가 **매번** 필요하다(이전에 화면에서 승인했어도 무시된다). 훅을 쓰면 `--max-turns`도 넉넉히 준다. README의 확인 명령에 빠뜨리지 않는다.
> 7. dcode는 **`.git`이 있는 상위 폴더**를 프로젝트 루트로 보고 그곳의 `AGENTS.md`, `.deepagents/`, `.agents/skills`, `.claude/skills`를 읽는다. 홈의 `~/.agents/skills`, `~/.claude/skills`도 읽는다. 시연은 `git init`한 별도 폴더에서 하고, 필요하면 `DEEPAGENTS_HOME`으로 프로필도 분리한다. dcode 소스 폴더 안에서 시연하면 소스 저장소의 설정이 섞인다.
> 8. 리뷰어(서브에이전트 머리말 `model`)와 채점 모델(`--rubric-model`, 기본은 메인 모델)을 허용된 모델로 지정한다. `config.toml`의 `[models] allowed`로 강제하면 금지 모델이 잡혔을 때 실행이 바로 실패한다. 자동 검토 모드(Auto)는 화면 없는 실행에서는 쓰이지 않는다.

**⑯ 7절 표에 추가할 행**
| 문서 | 실제 |
|---|---|
| `dcode --install openrouter`로 추가 패키지를 넣는다 | 소스 설치에서는 거부된다. `uv sync --extra`로 넣는다 |
| (저장소 문서 일부) 화면 없는 실행은 `-x`/`--execute` | 이 버전의 플래그는 `-n`/`--non-interactive`다 |

---

## 13. 초안 — **실행 검증 안 함**

아래 코드는 저장소의 실제 기반 클래스·서명·관례를 따라 쓴 초안이다. **한 번도 실행·린트·타입 검사하지 않았다.** 그대로 통과한다고 가정하지 말고 §14의 명령으로 확인한다.

### 13.1 미들웨어 뼈대 — `libs/code/deepagents_code/run_log.py` (실행 검증 안 함)

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


def _safe_stem(value: str) -> str:
    """Reduce an id to characters that are safe in a file name.

    Args:
        value: Thread id taken from the run context.

    Returns:
        The id with everything but letters, digits, `-`, and `_` removed, or
        the placeholder stem when nothing is left.
    """
    stem = "".join(ch for ch in value if ch.isalnum() or ch in "-_")
    return stem or _UNKNOWN_THREAD


class RunLogMiddleware(AgentMiddleware):
    """Append one JSON line per tool call to `<log_dir>/<thread_id>.jsonl`.

    Each record carries the tool name, duration, status, and the exit code of
    `execute` calls. A write failure is logged and never fails the tool call.
    """

    trace_policy = TracePolicy(process_inputs=omit_payload)
    """Omit hook inputs from traces by default; set a `TracePolicy` to override."""

    def __init__(self, log_dir: Path) -> None:
        """Initialize the recorder.

        Args:
            log_dir: Directory that receives one `.jsonl` file per thread. The
                graph builder passes a workspace-scoped path.
        """
        super().__init__()
        self._log_dir = log_dir

    @staticmethod
    def _thread_stem(request: ToolCallRequest) -> str:
        """Return the log file stem for the request's thread.

        Returns:
            A file-name-safe thread id, or the placeholder stem.
        """
        runtime = getattr(request, "runtime", None)
        context = CLIContextSchema.from_payload(getattr(runtime, "context", None))
        if context is None or not context.thread_id:
            return _UNKNOWN_THREAD
        return _safe_stem(context.thread_id)

    @staticmethod
    def _event(
        request: ToolCallRequest,
        result: ToolMessage | Command[Any] | None,
        error: BaseException | None,
        duration_ms: int,
    ) -> dict[str, object]:
        """Build the record for one finished tool call.

        Returns:
            A JSON-serializable record.
        """
        status = "error" if error is not None else "ok"
        exit_code: int | None = None
        if isinstance(result, ToolMessage):
            if result.status == "error":
                status = "error"
            artifact = result.artifact
            code = artifact.get("exit_code") if isinstance(artifact, dict) else None
            if isinstance(code, int) and not isinstance(code, bool):
                # `execute` reports a failed command as a successful tool call.
                exit_code = code
                if code != 0:
                    status = "error"
        return {
            "ts": datetime.now(UTC).isoformat(),
            "kind": "tool_call",
            "tool": request.tool_call["name"],
            "tool_call_id": request.tool_call["id"],
            "status": status,
            "exit_code": exit_code,
            "error": type(error).__name__ if error is not None else None,
            "duration_ms": duration_ms,
        }

    def _record(
        self,
        request: ToolCallRequest,
        result: ToolMessage | Command[Any] | None,
        error: BaseException | None,
        started: float,
    ) -> None:
        """Append the record for one finished tool call."""
        duration_ms = int((time.perf_counter() - started) * 1000)
        event = self._event(request, result, error, duration_ms)
        path = self._log_dir / f"{self._thread_stem(request)}.jsonl"
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError:
            logger.warning("Could not append run log %s", path, exc_info=True)

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command[Any]],
    ) -> ToolMessage | Command[Any]:
        """Run the tool and record its outcome.

        Args:
            request: The tool call being processed.
            handler: The next handler in the middleware chain.

        Returns:
            The tool result, unchanged.
        """
        started = time.perf_counter()
        try:
            result = handler(request)
        except GraphBubbleUp:
            # An interrupt is control flow; the call runs again on resume.
            raise
        except Exception as exc:
            self._record(request, None, exc, started)
            raise
        self._record(request, result, None, started)
        return result

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

근거가 된 원본: 기반 클래스·`trace_policy`·`super().__init__()`는 `memory_guard.py:34`, `:107-118`, 서명은 `agent.py:960-998`, `asyncio.to_thread`는 `memory_guard.py`의 `awrap_tool_call`, `GraphBubbleUp` 처리는 `model_retry.py:637-639`, `:1180-1182`, 컨텍스트 읽기는 `offload_middleware.py:888-895`.

걸릴 수 있는 곳(추정): `except Exception … raise`의 규칙 판정, `result.artifact`의 `ty` 타입 좁히기, DOC 규칙이 요구하는 구역. 걸리면 저장소의 같은 패턴을 찾아 맞춘다.

**거부를 돌려주는 형태(게이트용, 실행 검증 안 함).** `handler`를 부르지 않고 오류 메시지를 돌려준다(`agent.py:948-957`와 같은 모양):
```python
        return ToolMessage(
            content="Edit blocked: the plan is not approved yet.",
            name=request.tool_call["name"],
            tool_call_id=request.tool_call["id"],
            status="error",
        )
```

### 13.2 `create_cli_agent`에 끼우기 (실행 검증 안 함)

메인 목록: `agent_middleware: list[AgentMiddleware[Any, Any]] = [ ConfigurableModelMiddleware(...), ]` 리터럴 **바로 뒤**, `if not interactive:` **앞**.
```python
    # Record tool calls for monitoring. Installed only when the builder knows
    # the workspace directory; the process directory is never consulted.
    if effective_cwd is not None:
        from deepagents_code.run_log import RunLogMiddleware

        agent_middleware.append(
            RunLogMiddleware(Path(effective_cwd) / ".deepagents" / "runs")
        )
```
서브에이전트: `_subagent_cli_middleware()` 안, `middleware.append(CodeModelRetryMiddleware(max_retries=model_retries))` 뒤에 같은 블록을 `middleware.append(...)`로 넣는다(새 인스턴스). `effective_cwd`는 바깥 함수의 변수라 그대로 보인다.

주의: 기록이 작업 폴더의 `.deepagents/runs/`에 쌓인다. 시연 저장소의 `.gitignore`에 넣거나 경로를 프로필 쪽으로 바꾼다.

### 13.3 단위 테스트 — `libs/code/tests/unit_tests/test_run_log.py` (실행 검증 안 함)

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

    result = middleware.wrap_tool_call(_request(), handler)

    assert isinstance(result, ToolMessage)
    (event,) = _events(tmp_path / "runs")
    assert event["tool"] == "execute"
    assert event["status"] == "error"
    assert event["exit_code"] == 1


async def test_async_call_is_recorded(tmp_path: Path) -> None:
    """The async wrapper writes the same record as the sync path."""
    middleware = RunLogMiddleware(tmp_path / "runs")

    async def handler(_request: ToolCallRequest) -> ToolMessage:  # noqa: RUF029
        return ToolMessage(content="ok", name="ls", tool_call_id="call-1")

    await middleware.awrap_tool_call(_request("ls"), handler)

    (event,) = _events(tmp_path / "runs")
    assert event["tool"] == "ls"
    assert event["status"] == "ok"
    assert event["exit_code"] is None
```
본보기: `tests/unit_tests/test_memory_guard.py:35-45`, `:52-73`, `:165-182`.

### 13.4 `hooks.json` 예 — `{프로젝트 루트}/.deepagents/hooks.json` (실행 검증 안 함)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|delete",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .deepagents/hooks/plan_gate.py",
            "timeout": 10,
            "statusMessage": "Checking plan approval"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .deepagents/hooks/inject_memory.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```
- `PreToolUse` 매처 `Write|Edit|delete`는 정확히 그 세 이름과 일치한다. 셸까지 보려면 `Bash`를 더한다.
- `UserPromptSubmit`에는 `matcher`를 쓰지 않는다.
- 훅은 세션 작업 폴더에서 실행되므로 상대 경로가 통한다.

`plan_gate.py`가 지킬 규칙(실행 검증 안 함):
```python
"""PreToolUse gate: deny file edits until the plan is approved."""

import json
import sys
from pathlib import Path


def main() -> int:
    payload = json.load(sys.stdin)  # tool_name, tool_input, cwd, session_id, ...
    target = payload.get("tool_input", {}).get("file_path", "")
    approved = Path(payload["cwd"], ".deepagents", "plan", "APPROVED").exists()
    if approved:
        return 0  # no output: no decision, normal flow continues
    print(f"plan not approved; refusing to change {target}", file=sys.stderr)
    return 2  # deny; stderr becomes the reason the model sees


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # any crash must still deny (exit 1 would allow)
        print(f"plan gate failed: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
```
`inject_memory.py`는 종료 0으로 끝내고 stdout에 일반 텍스트를 쓰면 그 텍스트가 사용자 메시지 앞에 추가 컨텍스트로 들어간다. JSON으로 쓰려면 `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "..."}}`.

---

## 14. 사용자가 직접 돌려 마무리할 명령

원본을 받은 폴더의 `libs/code`에서 실행한다. "기대"는 코드를 읽고 쓴 것이라 문구가 다를 수 있다.

| # | 명령 | 기대 | 확인하는 것 |
|---|---|---|---|
| 1 | `uv sync --group test --extra openrouter` | 설치 목록에 `langchain-openrouter`, `deepagents==0.7.14`가 `../deepagents` 경로(editable)로 | 빌드, §0-5 |
| 2 | `uv run dcode --version` | `deepagents-code 0.1.69`와 SDK 0.7.14, 소스 경로 | 진입점 |
| 3 | `make lint; echo "exit=$?"` (아무것도 고치기 전) | ruff `All checks passed!`, 포맷 diff 없음, ty 통과, 뒤 두 검사 무출력, `exit=0` | 원본이 깨끗한 출발점인지 |
| 4 | 주석판에서: `uv run --all-groups ruff check deepagents_code --select E501 --statistics` | `E501` 수천 건(추정 1,750건 이상), 종료 1 | §3.4 추정 |
| 5 | 주석판에서: `uv run --all-groups ruff check deepagents_code --select RUF001,RUF002,RUF003 --statistics` | 0~10건(추정) | §3.4 추정 |
| 6 | `make test TEST_FILE=tests/unit_tests/test_memory_guard.py` | `17 passed`, 커버리지 표 | 테스트 환경 |
| 7 | 13.1~13.3을 넣은 뒤: `uv run --all-groups ruff check deepagents_code/run_log.py tests/unit_tests/test_run_log.py && uv run --all-groups ruff format --check deepagents_code/run_log.py tests/unit_tests/test_run_log.py && uv run --all-groups ty check deepagents_code/run_log.py` | 셋 다 통과. 실패하면 규칙 코드를 보고 고친다 | 초안의 린트 적합성 |
| 8 | `make test TEST_FILE=tests/unit_tests/test_run_log.py` | `2 passed` | 초안 동작 |
| 9 | `make lint; echo "exit=$?"` (13.2 반영 뒤) | `exit=0`. cwd 검사에서 `unreviewed`·`stale`이 없어야 한다 | 삽입이 허용 목록을 안 깨는지 |
| 10 | (확인용, 되돌린다) `run_log.py`에 `Path.cwd()`를 한 줄 넣고 `uv run --all-groups python scripts/check_process_cwd.py deepagents_code; echo $?` | `Reads of the process working directory must be allowlisted:` 와 `- run_log.py:<줄>: unreviewed Path.cwd call […]`, 종료 1 | 함정 1 |
| 11 | 시연 폴더(`git init`)에서: `OPENROUTER_API_KEY=… uv run --project <libs/code> dcode -n "hello.txt 파일을 만들어줘" -M openrouter:<모델> --max-turns 20 --timeout 300; echo "exit=$?"` | `Running task non-interactively...`, `Task completed`, `Usage Stats` 표, `exit=0`, `.deepagents/runs/<thread>.jsonl`에 `write_file` 기록 | 모델 연결, 기록 미들웨어, 블로킹 I/O 문제 유무 |
| 12 | 같은 명령에 `--rubric "world.txt 파일이 있어야 한다" --rubric-max-iterations 1` | `Checking acceptance criteria (iteration 1)…` 뒤 미충족 문구. **`exit=0`인지 확인** | §0-1 |
| 13 | 13.4를 넣고 플래그 없이 → 다음에 `--trust-project-hooks`를 붙여서 | 플래그 없이는 파일이 만들어진다. 플래그가 있으면 `Write blocked by hook: plan not approved…`가 도구 오류로 보이고 파일이 안 생긴다 | 훅 신뢰, 거부 문구 |
| 14 | 13번에서 `--max-turns 3`으로 | 도구 호출 몇 번 만에 `Exceeded 3 agentic turns`, `exit=124` | §0-8 (훅 왕복이 turn으로 세어지는지) |
| 15 | `.deepagents/agents/reviewer/AGENTS.md`를 만들고 "reviewer에게 a.txt를 만들게 해줘" | 서브에이전트의 `write_file`이 `runs/*.jsonl`에 남는지(13.2의 서브에이전트 삽입 전후 비교) | §0-6 |
| 16 | 서버 로그 확인: `DEEPAGENTS_CODE_DEBUG=1`로 11번을 돌리고 stderr의 `Server log preserved at:` 경로를 연다 | `BlockingError`가 없어야 한다. `asyncio.to_thread`를 빼면 나오는지도 본다 | §2.6-1 |

---

## 15. 확인하지 못한 것

- **실행이 필요한 것 전부.** 빌드 성공 여부, 원본·주석판의 실제 린트 결과, 초안 코드의 린트·타입·테스트 통과, 훅의 실제 동작과 turn 계산, Blockbuster 동작, 채점 문구의 실제 출력.
- `AgentMiddleware` 기반 클래스의 원본 서명(langchain 패키지가 스냅샷에 없다). 동기 `wrap_*`만 정의했을 때의 동작.
- ruff 세부 판정: RUF003의 대상 문자 목록, `─`·`·`가 걸리는지, DOC·D417이 요구하는 구역, `except Exception … raise`의 BLE 판정.
- `js_eval`의 도구 호출이 `wrap_tool_call`을 우회하는지(`libs/partners/quickjs`는 읽지 않음).
- `/reload`가 에이전트 그래프를 다시 조립하는지(7절의 `/reload`·`/restart` 주장).
- `[models] allowed`의 와일드카드 지원(문서 예시만 봄), `config.toml`의 프로젝트 단위 위치.
- `uv sync --extra`가 이 저장소에서 문제없이 되는지, `uv pip install -e`가 `tool.uv.sources`를 따르는지.
- `Day06/task.md`의 내용, `THREAT_MODEL.md`(670줄)와 `ARCHITECTURE.md` 본문, `analysis/00~09` 문서(코드로 직접 확인하는 쪽을 택했다).
- 공식 문서는 `cli-reference` 한 쪽만 요약 도구로 확인했다(2026-11 시점이라 0.1.69 이후 버전일 수 있다). 그 쪽에 `--trust-project-hooks`가 없다는 응답을 받았지만 요약 결과라 신뢰도가 낮다. 수집본(`docs_official/code/hooks.md:68`)에는 있다.
- 스냅샷의 `deepagents/`에 `.git`이 없는 것은 이 환경에서 본 사실이다. 수업 PC의 사본에는 있을 수 있다.
- 과제 모델(GLM-5.3-Flash 등)의 OpenRouter 모델 ID.
