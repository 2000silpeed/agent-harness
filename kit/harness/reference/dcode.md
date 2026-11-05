> 이 문서의 경로는 수업 저장소 `github.com/HyunjunJeon/sds_ax_advanced_2026` 기준이다(`R/` = 저장소 루트). 2026-11-05 클론 기준으로 조사했다.

# dcode 연구 지도 — 최종 프로젝트(Coding Assistant) 준비용

작성일: 2026-11-05 · 대상: `SDS AX 심화 과정` 최종 프로젝트 (`Day08/project_guide.md`)
근거 자료: `/home/user/hyunjunjeon/sds_ax_advanced_2026` (읽기 전용으로 조사함)

## 0. 인용 규칙 (먼저 읽기)

| 접두어 | 실제 경로 (저장소 루트 `R/` = `/home/user/hyunjunjeon/sds_ax_advanced_2026/`) |
|---|---|
| `C/` | `R/Day08/dcode-analysis/deepagents/libs/code/deepagents_code/` (dcode 패키지) |
| `L/` | `R/Day08/dcode-analysis/deepagents/libs/code/` (dcode 프로젝트 루트: pyproject, Makefile, DEVELOPMENT.md) |
| `S/` | `R/Day08/dcode-analysis/deepagents/libs/deepagents/deepagents/` (DeepAgents SDK) |
| `A/NN:줄` | `R/Day08/dcode-analysis/analysis/NN-*.md:줄` (분석 문서) |
| `D/` | `R/Day08/dcode-analysis/docs_official/` (공식 문서 스냅샷) |

- **`C/`·`S/`·`L/`의 줄 번호는 이번에 작업 트리에서 직접 연 결과다(소스 확인).**
- **주의:** 작업 트리는 `# [해설]` 한국어 주석이 들어간 `annotated-ko` 판이라, `agent.py`·`main.py`·`server_graph.py` 등 주석이 달린 파일은 분석 문서(`A/`)의 줄 번호와 **수백 줄씩 어긋난다** (`R/Day08/dcode-analysis/AGENTS.md:148-150`). 분석 문서는 `baseline-1d3232c` 태그 기준이라고 하지만, 이 사본의 `deepagents/`에는 `.git`이 없어 태그로 원본 줄을 볼 수 없다(직접 `ls -a`로 확인). 주석이 없는 `app.py`, `subagents.py`, `command_registry.py`, SDK(`S/`)는 분석 문서 줄 번호와 일치했다.
- 확인하지 못한 주장은 "확인 필요", 내 추론은 "(추론)"으로 표시한다.

---

## 1. dcode 개요

### 1.1 정체

- 패키지 `deepagents-code` 0.1.69, 진입점 `dcode`/`deepagents-code` = `deepagents_code:cli_main` (`L/pyproject.toml:6-7`, `:154-156`; `C/main.py:5496`).
- SDK `deepagents`를 **`==0.7.14`로 고정**하고(`L/pyproject.toml:30`), uv source로 모노레포의 `../deepagents`를 editable로 쓴다(`L/pyproject.toml:213-220`, `L/uv.lock:938-940`). `requires-python = ">=3.12,<4.0"` (`L/pyproject.toml:13`).
- 분석 기준 커밋 `1d3232c` (2026-09-14), 코드 규모: dcode 약 20만 줄, SDK 약 2.8만 줄 (`R/Day08/dcode-analysis/README.md:7-13`, `:49-56`).

### 1.2 설치·빌드·실행 (저장소 문서 그대로)

| 목적 | 명령 | 근거 |
|---|---|---|
| 릴리스판 설치(WSL 필수) | `curl -LsSf https://langch.in/dcode \| bash` | `R/Day07/dcode_task.md:15-21`, `D/code/quickstart.md:16` |
| 소스 개발 환경(훅 포함) | `cd deepagents/libs/code && make bootstrap` | `L/DEVELOPMENT.md:21-27`, `L/Makefile:101` |
| 의존성만 동기화 | `uv sync --group test` | `L/DEVELOPMENT.md:29` |
| 소스로 TUI 실행 | `uv run deepagents-code` (editable이라 다음 실행에 소스 변경 반영) | `L/DEVELOPMENT.md:31-37` |
| 별도 `dcode-dev` 명령 | `uv venv ~/.local/share/dcode-dev --python 3.13` → `uv pip install --python ~/.local/share/dcode-dev/bin/python -e <repo>/libs/code` → `ln -sf ~/.local/share/dcode-dev/bin/dcode ~/.local/bin/dcode-dev` | `L/DEVELOPMENT.md:154-176` |
| 전체 검사 / 단위 테스트 / 단일 파일 | `make check` / `make test` / `make test TEST_FILE=tests/unit_tests/test_x.py` | `L/DEVELOPMENT.md:39-56` |
| 포맷 / 린트+타입 | `make format` / `make lint` | `L/DEVELOPMENT.md:62-67`, `L/Makefile:70-84` |
| 헤드리스 1회 실행 | `dcode -n "..."` (매번 새 스레드, 파일 기반 상태(메모리·스킬·설정)는 유지) | `D/code/cli-reference.md:154`, `D/code/quickstart.md:185` |
| CI 예산 | `--max-turns N`, `--timeout S` → 초과 시 exit 124 | `D/code/cli-reference.md:181-185`, `:457-458` |
| 완료 기준 채점 | `dcode -n "..." --rubric "tests pass; ..."` 또는 `--rubric @file.md`, `--rubric-model`, `--rubric-max-iterations` | `D/code/cli-reference.md:217-230`, `:452-454` |
| OpenRouter | 패키지 `langchain-openrouter`, env `OPENROUTER_API_KEY`, `/install openrouter` 또는 `dcode --install openrouter` | `D/code/providers.md:78`, `:176-187`; 소스 extra `openrouter` (`L/pyproject.toml:129`) |

- 과정 규칙: OpenRouter 경유, OpenAI·Anthropic·Google 3사 모델 불허, 테스트 모델 GLM-5.3-Flash·DeepSeek-V4.1-Flash·Qwen3.8 (`R/Day07/dcode_task.md:4-9`, `R/Day07/README.md:54-62`).
- (추론) 소스 빌드에서 OpenRouter를 쓰려면 `uv sync --group test --extra openrouter`처럼 extra를 함께 설치해야 한다. 정확한 명령은 문서에 없으므로 **확인 필요**. 채점자가 README 그대로 빌드하므로 이 명령을 README에 명시하고 직접 검증할 것.

### 1.3 아키텍처 요약

```text
[클라이언트 프로세스]  cli_main(C/main.py:5496) ─┬─ TUI: app.py · tui/  (C/app.py:16503 _handle_command)
                                                  ├─ 헤드리스 -n: client/non_interactive.py
                                                  └─ 훅 실행기 hooks/ (서버 이벤트도 여기서 실행)
        │  HTTP+SSE, 설정은 DEEPAGENTS_CODE_SERVER_* env로 전달 (A/01:3, A/00:31-32)
[서버 프로세스: langgraph dev] server_graph._make_graphs(C/server_graph.py:366)
        → MCP 도구 로드(C/server_graph.py:274) → (EXPERIMENTAL) 확장 로드(:669)
        → create_cli_agent(C/server_graph.py:601 → C/agent.py:2570)
        → SDK create_deep_agent(C/agent.py:3748 → S/graph.py:271)
        → 미들웨어 스택 + CompositeBackend(LocalShell/Sandbox) + sessions.db 체크포인터
```

- **부팅**: `cli_main` → 플래그 검증 → 헤드리스/TUI/`--acp` 분기 → 임시 디렉터리에 `langgraph.json` 생성 후 `langgraph dev` 서브프로세스 기동 → `/ok` 폴링 → `RemoteAgent` 연결 (A/01:3, A/01 동작 흐름 A~E). `--acp`만 서버 없이 인프로세스(A/00:41).
- **조립**: dcode는 SDK의 `skills=`/`memory=`/`interrupt_on=` 인자를 쓰지 않고 전부 `middleware=`로 넘긴다. `.name`이 SDK 기본 미들웨어와 같으면 그 슬롯을 제자리 교체하고, 다르면 "마지막 core 뒤"에 끼운다 (`S/graph.py:204` `_apply_custom_middleware`; A/02:3, A/02:197-217).
- **실제 메인 스택(앞=바깥쪽)** — A/00:57-66, A/02:108-143을 작업 트리에서 재확인:

| 순서 | 미들웨어 | 작업 트리 위치 |
|---|---|---|
| SDK core | Filesystem → SubAgent → **CLICompaction**(이름이 `SummarizationMiddleware`라 요약 슬롯 교체) → PatchToolCalls | `S/graph.py`, `C/offload_middleware.py:1084` |
| dcode | ConfigurableModel | `C/agent.py:3074`, 클래스 `C/configurable_model.py:943` |
| dcode | ResumeState · CostTracking · GoalTools | `C/agent.py:3115` |
| dcode | AskUser | `C/agent.py:3124` |
| dcode | Memory(SDK) · ManagedMemoryGuard | `C/agent.py:3133-3165` |
| dcode | PluginSkills | `C/agent.py:3171-3180` |
| dcode | LocalContext (셸 백엔드일 때) | `C/agent.py:3271` |
| dcode | AutoModeHITL 또는 AsyncApprovalHITL (이름 `HumanInTheLoopMiddleware`) | `C/agent.py:3421`, `:2198` |
| dcode | ServerHooks (HITL 뒤) | `C/agent.py:3440-3448` |
| dcode | GoalCriteria(목표 모드) · CodeModelRetry · ToolError(task) | `C/agent.py:3540`, `:3557-3558` |
| dcode | ReliableRubric (항상 설치, 루브릭 있을 때만 동작) | `C/agent.py:3695` |
| dcode | (실험) 확장 미들웨어 · ExtensionRuntime | `C/agent.py:3711-3735` |
| SDK tail | 프로필 extras → 프롬프트 캐싱(Anthropic 항상, Bedrock·Fireworks는 패키지 있을 때) → ToolExclusion | `S/middleware/_prompt_caching.py:41-49` |

- **백엔드**: 로컬은 `LocalShellBackend(virtual_mode=False)` — 에이전트 경로가 곧 호스트 절대경로이며 `root_dir`는 경로 제한이 아니다(`C/agent.py:3209` 근처 `[해설][주의]` 주석, A/02:273-278). 대용량 결과는 `/tmp/dcode-artifacts-<uid>/large_tool_results`, 대화 아카이브는 `~/.deepagents/conversation_history`로 라우팅(A/02:92, A/02:304).
- **시스템 프롬프트**: 패키지 내 `C/system_prompt.md` 템플릿을 `get_system_prompt`가 치환(`C/agent.py:1617`, `:1661`). 기본 사용자 프롬프트는 `C/default_agent_prompt.md`(`C/config.py:5811` 주석).

### 1.4 설정·데이터 파일 위치

| 무엇 | 위치 | 근거 |
|---|---|---|
| 프로필 루트 | `~/.deepagents/` (`DEEPAGENTS_HOME`으로 이동 가능) | `D/code/configuration.md:810-815` |
| 사용자 설정 | `~/.deepagents/config.toml`, 관리자 `managed_config.toml` | `D/code/configuration.md:9-19` |
| 우선순위 | managed → `DEEPAGENTS_CODE_` 접두 env → 표준 env → config.toml → 기본값 (프로젝트 config.toml 계층은 없음) | A/03:12, A/03:61 |
| 체크포인트 | `~/.deepagents/.state/sessions.db` (SQLite) | `D/code/configuration.md:821-822` |
| 사용자 메모리/스킬/서브에이전트 | `~/.deepagents/{agent}/AGENTS.md`, `.../skills/<n>/SKILL.md`, `.../agents/<n>/AGENTS.md` | `D/code/configuration.md:827-834` |
| 프로젝트 | `{repo}/AGENTS.md`, `{repo}/.deepagents/{AGENTS.md, skills/, agents/, extensions/}`, `{repo}/.agents/skills/` | `D/code/configuration.md:841-855` |
| 훅 | `~/.deepagents/hooks.json`, `{project}/.deepagents/hooks.json`(신뢰 후) | `D/code/hooks.md:17` |
| MCP | `~/.deepagents/.mcp.json` < `{project}/.deepagents/.mcp.json` < `{project}/.mcp.json` | A/07:10, A/07:55 |
| 훅 transcript | `~/.deepagents/transcripts` (JSONL) | `D/code/hooks.md:187`, `C/hooks/runtime.py:129` |
| 디버그 로그 | 클라이언트 `/tmp/deepagents_debug/<thread-id>.log`, 서버 `$TMPDIR/deepagents_server_log_*.txt` (`DEEPAGENTS_CODE_DEBUG=1`) | `L/DEVELOPMENT.md:104-115` |

---

## 2. 확장 지점 지도

> 요약: SDK는 "미들웨어 스택 + backend 라우팅 + subagent"라는 **꽂을 자리**만 주고, 확장 메커니즘의 정책·보안·수명주기는 모두 dcode가 맡는다 (A/07:282).

### 2.1 훅 (Hooks v2)

- **무엇**: 라이프사이클 이벤트마다 셸 명령을 실행하고, exit code·stdout JSON으로 허용/거부/컨텍스트 주입/턴 계속을 제어한다. 이벤트 12종: `SessionStart, UserPromptSubmit, SessionEnd, PermissionRequest, Notification, PreToolUse, PostToolUse, PostToolUseFailure, PreCompact, Stop, SubagentStart, SubagentStop` (`C/hooks/models/domain.py:39-50`, 사양표 `C/hooks/capabilities.py:102`).
- **어디서 실행되나**: 핸들러는 **항상 클라이언트 프로세스**에서 돈다. 서버 이벤트는 `ServerHooksMiddleware`(`C/hooks/server_middleware.py:342`; `aafter_model` `:427`, `awrap_tool_call` `:479`, `aafter_agent` `:526`)가 LangGraph `interrupt`로 클라이언트에 요청을 보낸다 (A/07:117-149).
- **추가 방법**: `~/.deepagents/hooks.json` 예시는 `D/code/hooks.md:19-47`에 있다. stdin 페이로드에는 `session_id`, `transcript_path`, `cwd` 등이 들어간다(`D/code/hooks.md:178-187`, `:209-211`). 도구 매처는 wire 이름을 쓴다: `execute→Bash`, `write_file→Write`, `edit_file→Edit`, MCP는 `mcp__srv__tool` (`C/hooks/tools.py:69-77`, `:81-92`).
- **제어 의미**: exit 2 효과는 PreToolUse=Deny, PostToolUse=Feedback, Stop=Continue turn, UserPromptSubmit=Block (`D/code/hooks.md:135-147`). 여러 결정은 `deny > ask > allow` 순으로 합치고(`C/hooks/reducer.py:56`), Stop 연속 계속은 최대 8회다(`C/hooks/reducer.py:57`, `D/code/hooks.md:317`). `SessionStart`·`UserPromptSubmit`·`SubagentStart`는 `additionalContext`로 모델 컨텍스트를 주입할 수 있고, PostToolUse·SubagentStop은 덧붙이기만 한다(`D/code/hooks.md:321-332`).
- **한계**: 기본 timeout 600초(`C/hooks/capabilities.py:80`). `updatedInput`·`updatedToolOutput` 등은 파싱만 하고 적용하지 않는다(A/07:29). 이름에 KEY/TOKEN/SECRET 등이 들어간 env는 제거된다(A/07:26, A/07:242). 프로젝트 훅은 workspace trust가 필요하고 헤드리스에서는 `--trust-project-hooks`가 필요하다(A/07:23). 공식 `hooks.md`에는 `PostToolUseFailure`가 빠져 있다(A/07:234). 레거시 훅 제거일(2026-09-01)이 지났는데도 아직 호출된다(A/07:249).

### 2.2 미들웨어 (LangChain `AgentMiddleware`)

- **무엇**: `before_agent / before_model / wrap_model_call / after_model / wrap_tool_call / after_agent` 훅 포인트를 가진 클래스. dcode 기능 대부분이 이 형태다(§1.3 표).
- **추가 방법 ①(소스 수정)**: `create_cli_agent`(`C/agent.py:2570`)의 `agent_middleware` 리스트에 append한다. 리스트 앞쪽일수록 바깥쪽이다(A/02:110). SDK 슬롯을 바꾸려면 `.name`을 SDK 이름과 맞춘다(`S/graph.py:204`).
- **추가 방법 ②(확장)**: Python 확장의 `d.register_middleware(...)`를 쓴다(§2.8).
- **한계**: 서버 프로세스에서 돈다. 서버 하나가 여러 워크스페이스를 서빙하므로 `Path.cwd()`/`os.getcwd()`는 금지 대상이며 `make lint`의 `scripts/check_process_cwd.py`가 잡아낸다(`L/scripts/check_process_cwd.py:1-19`, `L/Makefile:76`). fork 서브에이전트는 부모 미들웨어를 **이름 기준으로 전부 상속**한다(A/02:257-266). 추가한 미들웨어도 서브에이전트 안에서 다시 돌 수 있다(추론, 확인 필요).

### 2.3 스킬 (`SKILL.md`)

- **무엇**: frontmatter(name/description)만 시스템 프롬프트에 목록으로 넣고, 모델이 필요할 때 `read_file`로 본문을 읽는다(progressive disclosure). SDK `SkillsMiddleware`(`S/middleware/skills.py:766`)를 상속한 `PluginSkillsMiddleware`(`C/plugins/adapters/skills_middleware.py:262`)가 담당한다.
- **위치·우선순위(뒤가 이김)**: Built-in → plugins → `~/.deepagents/<agent>/skills` → `~/.agents/skills` → `.deepagents/skills` → `.agents/skills` → `~/.claude/skills`(존재할 때만) → `.claude/skills` (`C/agent.py:2491` `get_skill_sources`, A/06:153-162).
- **추가 방법**: `dcode skills create NAME [--project]`(`D/code/cli-reference.md:541`) 또는 디렉터리를 직접 만든다. `/skill:<name> args`로 명시 호출하면 클라이언트가 본문을 사용자 메시지로 주입한다(`C/app.py:16921`, A/06:122). 헤드리스에서는 `--skill`.
- **Built-in 3종**: `remember`, `skill-creator`, `deepagents-thread-inspector` (`C/built_in_skills/`, A/06:89-95).
- **한계**: 스킬 인덱스는 스레드당 1회만 로드된다(A/06:182). `allowed-tools`는 표시만 하고 강제하지 않는다(A/06:263). 공식 문서의 탐색 계층(4~6개)은 실제 8계층과 다르다(F3, A/00:103). 서브에이전트는 스킬 인덱스를 받지 않는 것으로 보인다(A/06:172, 추정).

### 2.4 메모리 (`AGENTS.md`)

- **무엇**: SDK `MemoryMiddleware`(`S/middleware/memory.py:180`)가 소스 파일을 읽어 `<agent_memory>` 블록으로 시스템 메시지 뒤에 붙인다. 템플릿 `MEMORY_SYSTEM_PROMPT`는 `S/middleware/memory.py:105`에 있다.
- **소스**: `~/.deepagents/<agent>/AGENTS.md`와 프로젝트의 `.deepagents/AGENTS.md`·루트 `AGENTS.md` (`C/agent.py:3133-3140`). 백엔드는 `FilesystemBackend(virtual_mode=False)`다.
- **쓰기**: 모델이 `edit_file`로 AGENTS.md를 수정한다. `/remember`는 built-in `remember` 스킬의 별칭이며, 대화에서 규칙·교훈을 뽑아 AGENTS.md나 스킬로 저장한다(`C/built_in_skills/remember/SKILL.md:1-5`, A/06:93). `[memory].auto_save=false`면 `_MEMORY_READONLY_SYSTEM_PROMPT`(`C/agent.py:186`)로 바꾸는데, 이것은 프롬프트만 바꾸는 소프트 제어다(A/06:184-195).
- **한계**: **스레드당 1회만 로드**한다(`if "memory_contents" in state` — `S/middleware/memory.py:294`, `:328`). 같은 스레드에서 수정한 내용은 다음 스레드부터 보인다. **검색 기능이 없고 전문을 항상 주입**한다. 문서가 말하는 `~/.deepagents/<agent>/memories/` 자동 저장은 코드에 없다(F1, A/00:100, A/06:239). 프로젝트 AGENTS.md는 사용자 확인 없이 로드된다(S8, A/00:94).

### 2.5 서브에이전트

- **무엇**: SDK `SubAgentMiddleware`(`S/middleware/subagents.py:842`)의 `task` 도구. dcode는 GP를 직접 만들고, 기본값으로 `mode="fork"`(부모 대화·시스템 프롬프트 상속)를 쓴다(A/05:113).
- **추가 방법**: `.deepagents/agents/<name>/AGENTS.md`(프로젝트) 또는 `~/.deepagents/<agent>/agents/<name>/AGENTS.md`(사용자). frontmatter는 `name`, `description`, 선택 `model`이고 본문이 system_prompt가 된다. 이름이 같으면 프로젝트가 이긴다(A/05:10-16; 파서 `C/subagents.py:67`, 로더 `C/subagents.py:251`).
- **한계**: frontmatter로 `tools`/`middleware`/`interrupt_on`/`skills`를 설정할 수 없다(A/05:14). 서브에이전트 호출 자체는 HITL 대상(`task`, `C/agent.py:2387`)이지만, Auto 모드에서는 서브에이전트 내부 동작이 부모 검토 대상이 아니다(S2, A/00:88). 비동기 서브에이전트는 문서상 미제공이지만 `config.toml [async_subagents]`가 있으면 동작한다(F2, A/00:101).

### 2.6 목표(`/goal`)·루브릭

- **무엇**: `/goal <목표>`를 입력하면 중첩 에이전트가 **수락 기준 초안**(2-5 bullet)을 만들고, 사용자가 리뷰(accept/edit/revise/cancel)한 뒤 적용한다. 이후 턴마다 `ReliableRubricMiddleware`(`C/reliable_rubric.py:121`, SDK `RubricMiddleware` `S/middleware/rubric.py:489`)가 모델이 멈출 때(`after_agent` `S/middleware/rubric.py:658`) 채점하고, `needs_revision`이면 수정 메시지를 넣어 다시 돈다(A/05:161-189).
- **위치**: `GoalCriteriaMiddleware`(`C/goal_rubric.py:1468`), `GoalToolsMiddleware`(`update_goal`, `C/goal_tools.py:304`), 커맨드 `/goal` `/rubric`(`C/command_registry.py:155`, `:274`).
- **추가 방법**: TUI는 `/goal ...`, `/rubric set|next|file|show|clear|model`. 헤드리스는 `--rubric TEXT|@PATH` (A/05:21-26).
- **한계**: 헤드리스는 목표 리뷰 UI가 없어서 `--rubric`만 쓸 수 있다(`D/code/cli-reference.md:217`). 반복 한도에 도달하면 문서와 달리 `max_iterations_reached`로 변환된다(F7, A/00:106). verdict와 custom 이벤트 `rubric_evaluation_start/end`가 있다(A/05:34). **모니터링에 바로 쓸 수 있는 신호다.**

### 2.7 MCP

- **무엇**: 외부 MCP 서버의 도구를 LangChain 도구로 바꿔 넣는다. `resolve_and_load_mcp_tools`(서버 쪽 호출 `C/server_graph.py:274`)가 맡고, SDK에는 MCP 코드가 없다(A/07:277).
- **추가 방법**: `.mcp.json`(§1.4)을 두거나 `--mcp-config PATH`를 쓴다. 전송은 stdio/sse/http이고, `${VAR}` 보간과 `allowedTools`/`disabledTools`를 지원한다(A/07:9-18).
- **한계**: 프로젝트 MCP는 기본 거부이고 승인이 필요하다. 헤드리스에서는 `--trust-project-mcp`가 없으면 조용히 skip한다(A/07:18). read-only로 일관되게 표시되지 않은 MCP 도구는 모두 HITL 대상이다(`C/agent.py:2393-2400`). 관리자 정책을 읽지 못하면 MCP 전체가 비활성화된다(A/07:110).

### 2.8 Python 확장·플러그인

- **확장**: `DEEPAGENTS_CODE_EXPERIMENTAL=1`이 필수다(`D/code/extensions.md:12`). 진입 함수는 `async def extension(d: ExtensionAPI)`(`D/code/extensions.md:31`)이고 API는 `register_middleware`·`register_tool`·`register_backend_route`·`on_shutdown`(`C/extensions/api.py:31`, `:90`, `:119`, `:144`, `:175`)이다. 실행은 `DEEPAGENTS_CODE_EXPERIMENTAL=1 dcode --extension ./extension.py`(`D/code/extensions.md:41`). 로드 순서는 `~/.deepagents/extensions/` → `[extensions].extra_paths` → `-e` → 플러그인 → entry point → 프로젝트(trust 필요)다(A/07:36). 예제는 `L/examples/extensions/memory_store.py`(`/memories/`를 StoreBackend로 라우팅)다.
  - 한계: 실험 기능이다. 도구는 다음 요청부터 반영되지만 **미들웨어·라우트는 `/restart`가 필요하다**(공식 문서의 `/reload`는 오기, F4, A/07:228). 확장 도구는 HITL 맵에 자동으로 들어가지 않는다(A/07:38).
- **플러그인**: skills·MCP·hooks·확장을 한 디렉터리로 묶는 배포 단위다(`.claude-plugin/plugin.json` 등, A/07:41-45). 설치하는 것이 곧 동의이며, 서버별 승인을 생략한다(S7, A/00:93). 플러그인 `commands/`·`agents/` 디렉터리는 unsupported로 표시된다(A/07:262).

### 2.9 슬래시 커맨드

- **무엇**: 선언은 `SlashCommand` dataclass(`C/command_registry.py:37`)를 쓰는 `COMMANDS` 튜플(`C/command_registry.py:77`, 공개 45개)에 있고, 실행은 `app.py`의 거대한 if/elif 분기(`C/app.py:16503`)에 있다(A/09:23, A/09:240).
- **추가 방법**: (a) 소스 수정: registry에 항목을 추가하고 `_handle_command`에 분기를 추가한다. `make lint`가 `generate_commands_catalog.py --check`를 돌리므로 `make commands-catalog`로 `COMMANDS.md`를 재생성해야 한다(`L/Makefile:75`, `:90-94`). (b) 코드 수정 없이 **스킬을 `/skill:<name>`으로 호출**한다(가장 간단).
- **관련 기존 커맨드**: `/goal`, `/rubric`, `/remember`, `/reload`, `/restart`, `/threads`, `/trace`, `/tokens`, `/cost`, `/context-doctor`, `/offload`(별칭 `/compact`), `/extensions`, `/mcp`, `/auto` (`C/command_registry.py:85-282` 각 name 줄).

### 2.10 승인 모드·HITL

- **모드**: Manual(기본, 매번 확인) / Auto(분류기 검토) / YOLO(검토 없음). Shift+Tab으로 순환하고 `/manual` `/yolo` `/auto`로 바꾼다(A/04:10-20; 실제 순환은 Manual→Auto→YOLO, F9).
- **게이트 도구 맵**: `execute, write_file, edit_file, delete, web_search, fetch_url, task, start/update/cancel_async_task` + read-only가 아닌 MCP 도구 (`C/agent.py:2380-2400`), `compact_conversation`(`C/agent.py:215`). 결정은 `approve/reject`만 허용한다(edit/respond 없음, A/04:60).
- **헤드리스**: 셸은 `-S/--shell-allow-list`가 없으면 꺼진다. 제한 목록일 때는 셸 외 도구를 무조건 승인하고, 셸 off/`all`이면 승인 자체가 없다(S1, A/00:87). `-y/--yolo`는 경고 후 무시된다(A/01 흐름 A-11).
- **PreToolUse 훅과의 관계**: 훅의 allow/deny는 HITL보다 먼저 결정되고, `ask`는 HITL로 넘어간다(A/04:100, A/07:201).
- **한계**: 사람이 도구 단위로 승인하는 것이지 "계획 승인" 개념이 아니다. **dcode에는 plan mode가 없고 `write_todos`(TodoListMiddleware)도 쓰지 않는다**(`D/code`·`C/agent.py`·`C/command_registry.py` grep 0건, A/02:311).

### 2.11 추적·로그 (모니터링 기반)

| 기존 수단 | 내용 | 근거 |
|---|---|---|
| LangSmith 트레이싱 | `LANGSMITH_API_KEY`와 `LANGSMITH_TRACING=true`면 에이전트 run을 기록. 프로젝트는 `DEEPAGENTS_CODE_LANGSMITH_PROJECT` 또는 `[tracing].langsmith_project`로 지정. 서버는 첫 워크스페이스의 트레이싱 설정을 수명 내내 유지 | `L/DEVELOPMENT.md:72-92` |
| `/trace` | 현재 스레드를 LangSmith에서 열기 | `C/command_registry.py:251`, `C/app.py:16718` |
| resume 태그 | interrupt 재개 run에 `dcode:resume` 태그 부여 | `C/_tracing.py:21-58` |
| 모델 시도 이벤트 | custom 스트림 `{"type":"model_attempt", phase, call_id, attempt}` (재시도 횟수 원천) | `C/model_retry.py:1033`, 클래스 `:1118`; 클라이언트 소비 `C/tui/textual_adapter.py:2074` |
| 비용·토큰 | `CostTrackingMiddleware`가 `_session_cost_usd` 누적(`C/cost_tracking.py:2195`, `:2294`), `SessionStats`/`RecordedRequest`(`C/_session_stats.py:207`, `:408`), `/tokens` `/cost` | 각 줄 |
| 훅 transcript | `~/.deepagents/transcripts`에 JSONL 대화 투영. 훅 payload의 `transcript_path` | `D/code/hooks.md:187`, `C/hooks/runtime.py:129` |
| 체크포인트 | `sessions.db` + built-in `deepagents-thread-inspector` 스킬(읽기 전용 조회), `dcode threads list --json` | A/06:95, `D/code/cli-reference.md:468`, `:544` |
| 디버그 로그 | `DEEPAGENTS_CODE_DEBUG=1` → 스레드별 클라이언트 로그 + 서버 로그 보존, `Ctrl+\` 디버그 콘솔(항상 켜진 링버퍼) | `L/DEVELOPMENT.md:104-152`; `C/_debug.py:369`, `:400`; `C/_debug_buffer.py:64`, `:193` |

- **한계**: "계획→리뷰→코드→테스트→결과" 같은 **도메인 단계 단위의 기록과 조회 도구는 없다.** LangSmith는 외부 키가 필요하다. 채점 환경에 LangSmith 키가 있을지는 **확인 필요**하며, 로컬 로그를 1차 수단으로 삼는 것이 안전하다(추론).

---

## 3. 루브릭 매핑표

표기: **기존** = dcode가 기본 제공 / **추가** = 구현할 것 / **위치** = 권장 구현 지점 / **시연** = README 테스트 케이스.

### 3.1 [1] Python 개발 기준 (10점)

| 항목 | 기존 | 추가 | 위치 | 시연 |
|---|---|---|---|---|
| 1-1 PEP8 (3) | ruff `select=["ALL"]`, `ruff format` (`L/pyproject.toml:243-270`), `make format`/`make lint` (`L/Makefile:70-84`) | 새로 만든 모듈에도 같은 검사를 통과시킨다 | 새 모듈은 `C/` 아래 (예: `C/harness/…`) | README: `cd libs/code && uv run ruff check deepagents_code/<새 모듈> && uv run ruff format --check …` 결과 0 에러 |
| 1-2 명명·import (3) | isort `known-first-party`, **상대 import 전면 금지** `ban-relative-imports="all"` (`L/pyproject.toml:275-281`) | snake_case 함수, PascalCase 클래스, 지연 import 규칙(PLC0415는 허용, `:259`) 준수 | 위와 같음 | 같은 ruff 출력 + `make lint_package`(타입검사 `ty` 포함, `L/Makefile:64-73`) |
| 1-3 docstring (4) | pydocstyle `convention="google"` (`L/pyproject.toml:283-285`), 기존 코드가 Args/Returns 형식 예시(`C/_tracing.py:24-48`) | 새 public 함수·클래스마다 Args/Returns/Raises와 역할 설명 | 새 모듈 전부 | ruff D 규칙 통과 + README에 주요 함수 표 |

- 주의: 분석용 사본에는 `# [해설]` 주석이 수천 줄 있다(`C/agent.py`에만 262개). 제출 소스를 이 사본에서 시작할지, 업스트림 원본에서 시작할지 정해야 한다. 한국어 주석에 들어간 `·`, `→` 같은 기호가 ruff `RUF003`(ambiguous unicode)에 걸리는지는 **확인 필요**(`make lint`로 검증).

### 3.2 [2] 작업 계획 구체화·리뷰 (10점)

| 항목 | 기존 | 추가 | 위치 | 시연 |
|---|---|---|---|---|
| 2-1 요구사항·범위·완료조건 (2) | `/goal` → 수락 기준 초안 + 리뷰 UI (`C/goal_rubric.py:1468`, A/05:161-171). 헤드리스 `--rubric` | 계획 문서 템플릿: 요구사항 / 범위(In/Out) / 완료조건. 완료조건을 `/goal` 기준이나 `--rubric @plan.md`로 넘겨 **채점과 연결** | 프로젝트 스킬 `.deepagents/skills/plan-first/SKILL.md` + 산출물 `plans/<task-id>.md` | TC: "X 기능 추가" 요청 → `plans/…md` 생성, 세 섹션 존재 확인 |
| 2-2 수정 대상·순서·테스트 방법 (3) | 없음 (plan mode·todo 없음, §2.10) | 템플릿에 "수정 대상 파일 목록 / 단계 순서 / 테스트 명령"을 필수 항목으로 넣는다. 형식 검증 스크립트 | 같은 스킬 + `scripts/validate_plan.py` | TC: 필수 항목이 빠진 계획이면 검증 실패 |
| 2-3 AI 계획 리뷰·반영 (3) | `task` 서브에이전트 (`S/middleware/subagents.py:842`), 파일 정의 서브에이전트 (`C/subagents.py:67`) | 읽기 전용 리뷰어 `plan-reviewer`가 체크리스트로 판정하고(APPROVE/REVISE + 의견), REVISE면 계획을 v2로 고친 뒤 재리뷰한다. 리뷰 의견과 반영 diff를 계획 파일 "리뷰 이력" 절에 기록 | `.deepagents/agents/plan-reviewer/AGENTS.md`(frontmatter `model:`로 다른 모델 지정 가능, A/05:13) | TC: 일부러 테스트 방법이 빠진 요청 → 리뷰어 REVISE → v2에 반영된 기록 |
| 2-4 승인 후 코드 변경·범위 변경 재검토 (2) | Manual 모드 HITL은 도구 단위 승인(`C/agent.py:2380-2391`) | **계획 승인 게이트**: `PreToolUse` 훅(matcher `Write\|Edit\|Bash`)이 `plans/<id>.md`의 `status: approved`를 확인하고, 없으면 exit 2(Deny)로 사유를 모델에 전달한다(`D/code/hooks.md:135-147`). 수정 경로가 계획의 "수정 대상" 밖이면 Deny + "범위 변경 — 계획 갱신·재리뷰 필요" | `~/.deepagents/hooks.json` 또는 `{project}/.deepagents/hooks.json` + 스크립트. 대안은 `wrap_tool_call` 미들웨어(§2.2) | TC1: 승인 전 편집 시도 → 차단 로그. TC2: 계획 밖 파일 편집 → 차단 → 계획 v3 + 재리뷰 후 진행 |

- 주의: 헤드리스 `-n`에서 프로젝트 훅을 쓰려면 `--trust-project-hooks`가 필요하다(A/07:23). 사용자 레벨 `~/.deepagents/hooks.json`은 trust가 필요 없다(A/07:290). 채점자 환경에 맞게 README에 설치 단계를 명시할 것.
- 대안: 훅 대신 미들웨어로 구현하면 `make test`로 단위 테스트를 만들 수 있어 1번·3-4 항목 증빙에도 유리하다(추론).

### 3.3 [3] Memory·Self-Improving Harness (10점)

| 항목 | 기존 | 추가 | 위치 | 시연 |
|---|---|---|---|---|
| 3-1 규칙·경험 저장, 세션 후 유지 (2) | AGENTS.md(사용자·프로젝트)가 매 스레드에 로드(`C/agent.py:3133-3165`). `/remember`(`C/command_registry.py:224`). 헤드리스도 파일 상태 유지(`D/code/cli-reference.md:154`) | 구조화된 **경험 저장소**(예: `.deepagents/memory/experiences.jsonl`: task, 실패 원인, 해결책, 태그, 날짜)와 규칙(`AGENTS.md`)을 분리한다. 작업 종료 시 자동 기록 | `after_agent` 미들웨어 또는 `Stop`/`SessionEnd` 훅 | TC: 세션 A에서 규칙 저장 → `dcode -n`(새 스레드) 세션 B에서 규칙 준수 확인 |
| 3-2 관련 메모리 검색·활용 (3) | **검색 없음.** AGENTS.md 전문을 항상 주입하고, 스레드당 1회 로드(`S/middleware/memory.py:328`). 스킬은 description 기반 자기 선택 | 요청 텍스트로 경험 저장소를 검색(키워드/BM25, 임베딩은 선택)해서 top-k를 주입하고, **주입된 메모리 ID를 계획 문서와 로그에 남긴다** | `UserPromptSubmit` 훅의 `additionalContext`(`D/code/hooks.md:321-332`) 또는 `MemoryMiddleware` 옆에 둔 커스텀 `before_agent`/`wrap_model_call` 미들웨어(`C/agent.py:3155` 직후) | TC: 과거 실패 경험과 비슷한 작업 → 계획에 "참조 메모리: exp-007" 표기, 같은 실수를 반복하지 않음 |
| 3-3 실패·평가 기반 개선안 생성 (3) | `remember`·`skill-creator` 스킬(수동). 턴 안의 루브릭 재시도(`S/middleware/rubric.py:658`). Stop 훅 계속(최대 8회) | 실패 신호(도구 오류, `PostToolUseFailure`, 테스트 실패, 루브릭 `needs_revision`/`max_iterations_reached`)를 모아 LLM이 **개선안**(AGENTS.md 규칙 / SKILL.md / 프롬프트 suffix 패치)을 `proposals/<id>.md`로 생성한다. 즉시 적용하지 않는다 | `after_agent` 미들웨어, 또는 실패 로그를 입력으로 받는 `improve` 스킬(`/skill:improve`) | TC: 일부러 실패하는 작업 → 개선안 파일 생성(원인·변경안·기대효과) |
| 3-4 전후 검증·채택 (2) | 헤드리스 배치 평가: `-n` + `--rubric` + exit code(124 등), `make test`(`L/DEVELOPMENT.md:53`). **에이전트별 독립 메모리** `-a/--agent NAME`(`D/code/cli-reference.md:137`, `:441`) | 고정 평가셋(N개 작업)을 baseline 에이전트와 후보 에이전트(`--agent candidate`에 개선안 적용)로 각각 실행 → 통과율·시간·재시도 비교 → 기존 기능 회귀(`make test` 또는 자체 테스트) 통과 시에만 본 메모리/스킬에 병합하고 `adoption_log`에 기록 | `scripts/eval_harness.py` + `dcode agents reset --agent NAME --target SOURCE`로 메모리 복제(`D/code/cli-reference.md:536`) | TC: 전후 비교표 출력, 탈락안은 미반영, 채택안은 다음 작업에서 사용됨 |

- 주의: 메모리는 스레드 시작 시 1회 로드되므로, 개선안을 같은 스레드에서 쓰면 반영되지 않는다. **"다음 작업에 반영"은 새 스레드(`-n` 또는 `/clear`)로 시연**한다(`S/middleware/memory.py:328`, A/06:174-182).
- 주의: `auto_save=true`(기본)이면 모델이 AGENTS.md를 스스로 고칠 수 있어 "검증 후 채택" 절차를 우회한다. 개선안 흐름을 강제하려면 `[memory].auto_save=false` 또는 `DEEPAGENTS_CODE_MEMORY_AUTO_SAVE=0`을 고려한다(A/06:13). 그래도 쓰기 차단은 아니라서, 필요하면 PreToolUse 훅으로 AGENTS.md 직접 편집을 막는다(추론).

### 3.4 [4] 모니터링 (10점)

| 항목 | 기존 | 추가 | 위치 | 시연 |
|---|---|---|---|---|
| 4-1 요청별 전체 흐름 기록 (3) | LangSmith run 트리 + `/trace`, `dcode:resume` 태그(`C/_tracing.py:21`). 훅 transcript JSONL. sessions.db | **요청(run) ID별 JSONL 이벤트 로그**: `phase ∈ {plan, review, code, test, result}`. phase는 도구로 판정한다(`task`+`plan-reviewer` → review, Write/Edit → code, `execute` 중 pytest → test, 계획 파일 생성 → plan, `after_agent` → result) | 커스텀 미들웨어(`before_agent`/`wrap_model_call`/`wrap_tool_call`/`after_agent`)를 `agent_middleware` 앞쪽에 추가(`C/agent.py:3074` 근처). 경로는 workspace에서 받는다(§2.2 cwd 주의) | TC: 한 요청 후 `logs/<thread_id>.jsonl`에 5단계가 시간순으로 있음 |
| 4-2 LLM·도구·메모리·자기개선 결과·오류 (3) | `model_attempt` 이벤트(`C/model_retry.py:1033`), PostToolUse/PostToolUseFailure 훅(`C/hooks/models/domain.py:45-46`), ToolError 포매터(`C/agent.py:173`) | 이벤트 스키마 통일: `llm_call`(모델, 토큰, 지연, 오류), `tool_call`(이름, 인자 요약, 상태, 소요, 오류), `memory_retrieve`/`memory_write`(ID, 점수, 경로), `improve_proposal`/`improve_eval`/`improve_adopt` | 같은 미들웨어 + 3-2/3-3 구현부에서 같은 로거 호출 | TC: 일부러 실패하는 도구 → `status:error` + 메시지가 기록됨 |
| 4-3 시간·호출 수·재시도 (2) | `SessionStats`(`C/_session_stats.py:207`), `/tokens` `/cost`, 재시도 예산 `--max-retries`(A/03:36) | run 종료 시 `summary.json`: 총 소요, LLM 호출 수, 도구 호출 수, 재시도 수(`model_attempt.attempt>0` 또는 wrap_model_call 재진입), 루브릭 반복 수, 토큰 | `after_agent`에서 집계 | TC: summary 수치 출력 |
| 4-4 로그·Trace 조회로 실패 지점 확인 (2) | `dcode threads list --json`, thread-inspector 스킬, 디버그 로그(`L/DEVELOPMENT.md:114-115`) | 조회 CLI `scripts/trace_query.py --run <id> [--errors] [--phase test]`(첫 오류 이벤트와 직전 컨텍스트 출력) 또는 스킬 `/skill:trace-report` | 별도 스크립트 + 스킬 | TC: 실패 run → "첫 실패: tool_call execute(pytest) exit 1, 원인: …" 출력 |

- LangSmith는 보조 수단으로 둔다. 키가 없어도 동작하는 로컬 JSONL을 1차 증빙으로 삼는다(추론). 비밀값을 기록하지 않도록 훅 env 정화 규칙(A/07:242)처럼 마스킹한다.
- 미들웨어 순서 주의: CLICompaction은 `.name` 때문에 SDK 3번 슬롯으로 옮겨져 모든 dcode 미들웨어보다 바깥에 있다(A/02:145). 로거가 보는 `request.messages`는 요약 이후 메시지다(추론).

---

## 4. Day07 `dcode_task.md` 요약 — 프로젝트의 사전 과제

원문은 제목만 있다(`R/Day07/dcode_task.md:27-33`). 같은 내용이 `R/Day08/dcode-analysis/README.md:83-89`에도 있다. 채점 과제는 아니다(`R/Day07/README.md:5-7`). 각 과제가 가르치는 내용과 코드 진입점은 아래와 같이 정리했다(내용 해석은 추론, 위치는 소스 확인).

| # | 과제 | 배우는 것 | 코드·문서 진입점 | 프로젝트 연결 |
|---|---|---|---|---|
| 1 | Prompt Caching을 고려한 DeepAgents 구성 | 시스템 프롬프트·도구 목록을 바이트 단위로 고정해야 캐시가 적중한다. dcode는 LocalContext 변경분을 system prompt가 아니라 메시지로 덧붙인다(A/00:76, A/02:251). fork 서브에이전트는 `task` 도구를 남겨 도구 목록을 맞춘다(A/05:196-197) | SDK 캐싱 미들웨어는 **Anthropic·Bedrock·Fireworks만** 지원(`S/middleware/_prompt_caching.py:41-49`). `[models].openai_prompt_cache_key`(`C/config_manifest.py:2583`). cold-cache 경고 `C/cold_cache.py:758` | 메모리 검색 결과를 **system prompt가 아니라 메시지로** 주입해야 캐시가 깨지지 않는다(3-2 설계에 직접 영향). OpenRouter 경유 모델의 캐시 동작은 **확인 필요** |
| 2 | 모델별 Harness Profile 분리 호출 | SDK `HarnessProfile`(프롬프트 suffix, extra middleware, 도구 제외·설명 재작성)을 모델 spec별로 등록한다(`S/profiles/harness/harness_profiles.py:483`, `register_harness_profile` `:980`). dcode 실례는 GLM-5.2 프로필(`C/_glm_5p2_profile.py:268`, 등록 `:281`, 호출 `C/agent.py:3703`) | 주의: config.toml의 `[models.providers.<n>].profile`은 **LangChain 모델 프로필**(`max_input_tokens` 등)이라 harness profile과 다르다(`D/code/config-file.md:275-276`, `:388`) | 계획용·리뷰용·코딩용 모델 분리, 약한 모델에 맞춘 프롬프트 suffix. 리뷰어 서브에이전트 `model:` 지정 |
| 3 | 메모리 구성 확인·테스트 | AGENTS.md 계층(사용자/프로젝트/루트), `/remember`, auto_save, 스레드당 1회 로드, StoreBackend 라우팅 예제 | §2.4, `L/examples/extensions/memory_store.py` | 3-1·3-2의 기반. "검색 없음·1회 로드"라는 한계를 알고 보완할 것 |
| 4 | Middleware로 구성하는 Self-Improving | `AgentMiddleware` 훅 포인트로 실패를 관찰하고 개선한다. 레퍼런스는 SDK `RubricMiddleware`의 채점→`jump_to="model"` 루프(`S/middleware/rubric.py:489`, `:658`) | §2.2 추가 방법 ①·② | 3-3·3-4·4-x를 하나의 미들웨어 계열로 구현 |

---

## 5. 위험·주의 사항

### 5.1 버전·빌드

- **SDK 버전 충돌**: 과정 루트 워크스페이스는 `deepagents==0.7.32`(`R/pyproject.toml:15`, `R/Day08/pyproject.toml:9`), dcode는 `deepagents==0.7.14` 고정에 경로 source(`L/pyproject.toml:30`, `:214`). **dcode를 과정 루트 `uv sync` 환경에 넣으면 해석이 실패하거나 버전이 섞인다(추론).** `libs/code`에서 자체 `uv.lock`(`L/uv.lock`)으로 별도 venv를 만들어야 한다. Python도 루트는 `>=3.13,<3.14`(`R/pyproject.toml:6`), dcode는 `>=3.12`(`L/pyproject.toml:13`)다.
- **모노레포 구조 유지 필수**: uv sources가 `../deepagents`, `../acp`, `../partners/{daytona,modal,quickjs,runloop,vercel}`를 경로로 참조한다(`L/pyproject.toml:213-220`). 제출 저장소에서 `libs/code`만 떼어 내면 빌드가 깨진다(추론, 확인 필요).
- **private API 의존**: 요약 미들웨어의 LangChain private 슬롯 교체(A/02:236-247), 플러그인 스킬 어댑터의 SDK private 함수(A/06:223), genai-prices private 이름(`L/pyproject.toml:67-74`). 그래서 버전 범위를 넓히면 깨진다.
- dcode 단독 의존 범위는 `langchain>=1.4.0,<2.0.0`, `pydantic>=2.12.5,<2.14.0a0` 등이다(`L/pyproject.toml:31`, `:44`).

### 5.2 문서 ↔ 코드 불일치 (영향 큰 것)

| # | 내용 | 근거 |
|---|---|---|
| F1 | 문서의 `~/.deepagents/<agent>/memories/` 자동 메모리는 코드에 없다. 실제로는 AGENTS.md를 `edit_file`로 편집한다 | A/00:100, A/06:239 |
| F3 | 스킬 탐색 계층: 문서 4~6계층, 실제 8계층 | A/00:102, A/06:248 |
| F4 | 확장 미들웨어 반영: 문서는 `/reload`, 실제는 `/restart` | A/00:103, A/07:228 |
| F7 | 루브릭 한도 도달 시 문서는 `needs_revision`, 실제는 `max_iterations_reached` | A/00:106 |
| F8 | Auto 모드에 `DEEPAGENTS_CODE_EXPERIMENTAL=1`이 필요하다는 문서와 달리 검사 없음 | A/00:107 |
| F9 | Shift+Tab: 문서는 Manual/Auto 토글, 실제는 Manual→Auto→YOLO 순환 | A/00:108 |
| S3 | API 키 우선순위: 문서는 접두 env 우선, 코드는 `/auth` 저장 키를 무조건 먼저 쓴다. **`/auth`로 저장한 옛 키가 `.env`의 OpenRouter 키를 덮어쓸 수 있다** | A/00:89 |
| S4 | SDK `FilesystemBackend.virtual_mode` 기본값: 문서 False, 코드 True (dcode 메인은 명시적으로 False) | A/00:90, A/02:302 |
| 훅 | 공식 hooks.md에 `PostToolUseFailure` 누락. `argv`는 문서가 권장하지만 코드는 제거 예정 | A/00:118, A/07:234, A/07:248 |
| 저장소 문서 | `ARCHITECTURE.md`가 링크한 `STREAMING_RETRY_DESIGN.md`가 없다. THREAT_MODEL 도구명이 구식이다. `EXTENSIONS.md`의 `extra_files/extra_dirs`는 실제로 `extra_paths` | A/00:115-117 |
| 스냅샷 | `D/code/changelog.md`는 마크다운이 아니라 GitHub HTML 페이지가 저장된 것(첫 줄 `<!DOCTYPE html>`, 직접 확인) | — |
| 분석 사본 | `R/Day08/dcode-analysis/AGENTS.md:153-154`에 같은 규칙 줄이 중복. 태그 `baseline-1d3232c` 안내가 있지만 사본에 `.git`이 없음(§0) | 직접 확인 |

### 5.3 보안

- **로컬 셸은 경계가 없다**: `LocalShellBackend(virtual_mode=False)`이고 SDK는 `shell=True`로 실행하며 명령을 검증하지 않는다. 통제 수단은 HITL뿐이다(`C/agent.py:3209` 주석, A/04:41). YOLO나 헤드리스 `-S all`은 사실상 무방비다(S1, A/00:87).
- **Auto 모드 × 서브에이전트**: 서브에이전트 내부 동작은 분류기·사람 모두 거치지 않을 수 있다(S2, 추정, A/00:88). 계획 게이트(2-4)를 훅으로 만들면 서브에이전트 도구 호출에도 걸리는지 검증할 것. 서브에이전트에도 `ServerHooksMiddleware(emit_stop=False)`가 붙는다는 근거가 있다(`C/agent.py:2928`, A/07:115).
- **프로젝트 AGENTS.md 자동 로드**: 클론한 저장소의 루트 AGENTS.md가 확인 없이 시스템 프롬프트에 들어간다(S8). 트리 밖 symlink만 막는다(A/06:197-199). 자기개선이 쓰는 메모리 파일도 프롬프트 인젝션 경로가 될 수 있다(추론). 채택 전 검증이 보안 장치 역할도 한다.
- **플러그인 = 설치가 곧 동의**: 플러그인 MCP·훅·확장은 개별 승인을 생략한다(S7, A/07:219).
- **비밀값**: 훅 env는 KEY/TOKEN 등 이름 기반으로만 제거한다(A/07:242). DEBUG 로그에는 MCP stderr가 들어가 자격증명이 노출될 수 있다(`L/DEVELOPMENT.md:146`). 모니터링 로그에는 마스킹이 필수다. 분석 가이드는 API 키·`.env` 값을 출력하거나 기록하지 말라고 한다(`R/Day08/dcode-analysis/AGENTS.md:163`).
- **원격 샌드박스 과금**: setup 실패 시 샌드박스가 삭제되지 않을 수 있다(S5). `$VAR` 치환으로 비밀이 원격 인자에 평문으로 실릴 수 있다(S6) (A/00:91-92). 프로젝트에서는 샌드박스를 쓰지 않는 편이 안전하다(추론).

### 5.4 구현 시 함정 (프로젝트용 체크리스트)

1. 서버 프로세스 코드에서 `Path.cwd()`를 쓰면 `make lint`가 실패한다(`L/scripts/check_process_cwd.py`). 경로는 run context의 workspace에서 받는다.
2. 메모리·스킬 인덱스는 스레드당 1회만 로드한다. "다음 작업 반영"은 새 스레드로 시연한다.
3. 확장(`-e`)으로 넣은 미들웨어는 `/restart` 후에 반영된다. 실험 플래그가 필요하므로 README에 env를 명시한다.
4. 헤드리스에는 goal 리뷰 UI가 없다. 2-1·2-3 시연을 `-n`으로 하려면 `--rubric @plan.md`와 리뷰 서브에이전트 조합을 쓴다.
5. 헤드리스에서 셸(pytest 실행 등)이 필요하면 `-S "pytest,uv,git"` 같은 allow-list가 필요하다(`D/code/quickstart.md:248-254`). 프로젝트 훅·MCP는 각각 `--trust-project-hooks`/`--trust-project-mcp`가 필요하다.
6. 슬래시 커맨드를 소스에 추가하면 `make commands-catalog`로 `COMMANDS.md`를 재생성해야 lint를 통과한다.
7. 3사(OpenAI·Anthropic·Google) 모델 금지 규칙 때문에 분류기(Auto) 기본 모델이 3사로 잡히지 않는지 확인한다. 기타 제공자는 메인 모델을 상속한다(A/04:17). 리뷰어·루브릭 모델 지정(`--rubric-model`, 서브에이전트 `model:`)도 OpenRouter 모델로 한다.
