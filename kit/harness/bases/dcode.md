# 기반 참고: dcode로 Coding Assistant 만들기

> dcode(deepagents-code 0.1.69, SDK deepagents 0.7.14)를 기반으로 인수 기준(`../CRITERIA.md`)을 채울 때 보는 문서다. 단계 설명은 `../METHOD.md`에 있다.
> **이 문서의 어떤 내용도 실행해서 확인하지 않았다.** 스냅샷(수업 저장소 `Day08/dcode-analysis/`)의 코드와 문서를 읽기만 했다. 빌드·설치·린트·테스트·실행 결과는 전부 읽고 낸 예상이다. 8절의 명령을 직접 돌려 확정한다.
> **줄 번호는 한국어 해설 주석이 들어간 스냅샷 기준이라 원본과 다르다.** 원본에서는 함께 적은 이름으로 검색한다. 경로는 따로 적지 않으면 `libs/code/deepagents_code/` 기준이다. `pyproject.toml`, `Makefile`, `AGENTS.md`, `scripts/`, `tests/`는 `libs/code/` 기준, `SDK`라고 적은 것은 `libs/deepagents/deepagents/` 기준이다.
> **확신도 표기:** 〔코드〕 코드를 읽어 확인(실행은 안 함) · 〔문서〕 문서에만 있음 · 〔추정〕 읽고 낸 예상 · 〔미확인〕 확인 못 함.

## 1. 한눈에 보기

| 인수 기준 | 있는 것 | 비어 있는 것 (만들 것) |
|---|---|---|
| 1 코드 품질 | ruff 전체 규칙(`select = ["ALL"]`, preview), google docstring, 상대 import 금지, 타입 검사 `ty`, `make lint` / `make format` 〔코드〕 `pyproject.toml:243-343` | 새로 쓰는 코드가 같은 검사를 통과해야 한다 |
| 2 계획·리뷰·승인 | 대화형 실행의 도구 단위 사람 승인(**화면 없는 실행 `-n`에는 없다.** `-n`은 셸만 허용 목록으로 막고 파일 쓰기·편집·삭제는 자동 승인한다), `/goal`의 수락 기준 초안과 채점, 파일로 정의하는 서브에이전트 〔코드〕 | **계획 모드가 없다**(검색 0건). 계획 양식, AI 리뷰, 계획 승인 게이트, 범위 검사 |
| 3 메모리·자기개선 | `AGENTS.md` 주입, 내장 스킬 `remember`, 에이전트 이름별 메모리 〔코드〕 | **검색이 없다**(대화당 한 번, 전문 주입 — SDK `middleware/memory.py:293-295`, `:347-361`). 경험 저장소, 검색·주입, 개선안 생성·검증·채택 |
| 4 모니터링 | LangSmith 연동, 모델 재시도, 비용·토큰 집계와 **실행 끝의 사용량 표**(Reqs, InputTok, OutputTok, Cost), 훅용 대화 기록(`~/.deepagents/transcripts/`, 훅이 설정돼 있을 때만), 체크포인트 DB(`~/.deepagents/.state/sessions.db`)와 이를 읽는 **내장 스킬 `deepagents-thread-inspector`** 〔코드〕 | **단계 단위 기록이 없다.** 요청별 계획·리뷰·코드·테스트·결과 기록, 요약 지표, 실패 지점 조회 |

## 2. 환경과 빌드 (S0에서 정할 것)

| 결정 | 내용 | 근거 |
|---|---|---|
| 출발 소스 | **원본에서 시작한다.** `git clone https://github.com/langchain-ai/deepagents` 후 `git checkout 1d3232c0852c47af09119edea10eeec887e4f0da`(0.1.69 릴리스 커밋). 해설 주석판은 읽기용으로만 쓴다. 주석판은 `# [해설]` 주석 4,179줄 중 1,752줄이 88자를 넘어 `make lint`가 E501로 실패할 것으로 본다 〔추정〕. `.git`도 없어 원본과 비교할 수 없다 | `pyproject.toml:243-285`(`line-length` 설정 없음 → 기본 88) |
| 저장소 구조 | 모노레포 구조를 유지한다. `libs/code`가 `../deepagents`, `../acp`, `../partners/*`를 경로로 참조한다 〔코드〕. `libs/code`만 떼면 의존성 해석이 실패한다 〔추정〕 | `pyproject.toml:213-231` |
| 가상환경 | `libs/code`의 자체 lock으로 별도 환경을 만든다. dcode는 `deepagents==0.7.14` 고정이라 다른 버전이 깔린 공용 환경과 섞지 않는다 〔코드〕. Python은 3.12 이상 | `pyproject.toml:13`, `:30` |
| 작업·시연 위치 | 스냅샷 폴더 밖의 별도 경로. **시연 폴더는 `git init`한 별도 폴더**여야 한다. dcode는 `.git`이 있는 가장 가까운 상위 폴더를 프로젝트 루트로 보고, 없으면 프로젝트 메모리·스킬·서브에이전트를 로드하지 않는다 〔코드〕 | `_git.py:136-160`, `project_utils.py:76-98` |
| 모델 | OpenRouter 경유, OpenAI·Anthropic·Google 모델 금지, 시험 모델 GLM-5.3-Flash·DeepSeek-V4.1-Flash·Qwen3.8 〔문서: 과제 안내문〕. 최종 과제에도 같은 규칙인지, 각 모델의 OpenRouter ID는 〔미확인〕 | 모델 문자열 `-M openrouter:<모델 ID>` |

```bash
cd libs/code
uv sync --group test --extra openrouter   # 개발 환경 + OpenRouter. extra 없이 uv sync를 다시 돌리면 OpenRouter가 빠진다
uv run dcode --version                    # 소스 빌드에서는 dcode가 PATH에 없다. uv run으로 부른다
uv run deepagents-code                    # 소스로 실행. 소스를 고친 뒤에는 다시 실행해야 반영된다(서버가 --no-reload)
make lint                                 # ruff check, ruff format --diff, ty, 명령 목록 검사, cwd 검사 (Makefile:62-80)
make format                               # ruff format + 자동 수정
make test TEST_FILE=tests/unit_tests/test_x.py
cd /path/to/demo && git init              # 시연은 별도 폴더에서, dcode는 소스 폴더의 환경으로 부른다
uv run --project /path/to/deepagents/libs/code dcode -n "요청" -S "pytest,uv,git" --max-turns 40 --timeout 900
```

| 주제 | 사실 | 확신도·근거 |
|---|---|---|
| `make bootstrap` | **쓰지 않는다.** `uv sync --group test` 뒤에 git 최상위에 pre-commit 훅을 설치한다. 다른 저장소 안에 풀어 둔 사본에서 돌리면 바깥 저장소에 훅이 깔린다 | 〔코드〕 `Makefile:8`, `:101-104` |
| OpenRouter 설치 | extra 이름은 `openrouter`. 문서의 `dcode --install openrouter`는 **소스(editable) 설치에서 거부된다.** `uv sync --extra`로 넣는다(이 명령의 성공 여부는 〔미확인〕) | 〔코드〕 `pyproject.toml:129`, `update_check.py:3996-4003` |
| 키 우선순위 | `DEEPAGENTS_CODE_OPENROUTER_API_KEY` > `/auth`로 저장한 키 > `OPENROUTER_API_KEY`. 모델이 엉뚱하게 잡히면 접두 변수로 덮어쓴다 | 〔문서〕 + 일부 〔코드〕 `model_config.py:60-146` |
| 금지 모델 강제 | `~/.deepagents/config.toml`의 `[models] allowed = [...]`. 메인·채점·서브에이전트 모델을 모두 검사하고 걸리면 실행이 실패한다. 와일드카드 지원은 〔미확인〕 | 〔코드〕 `agent.py:2957-3013` |
| `-n`의 승인 | `-S` 없음: 셸 꺼짐. **그 밖의 도구(파일 쓰기·편집·삭제)는 전부 자동 승인.** `-S 목록`: 셸 켜짐, 명령만 목록으로 검사 | 〔코드〕 `client/non_interactive.py:2747-2751`, `:3005-3014` |
| `-S` 판정 | `&&`, `\|\|`, `\|`, `;`로 나눈 각 구간의 첫 단어를 본다. 리다이렉트(`>`)·`$(…)`는 거부. `uv run pytest`는 `uv`만 있으면 통과, `cd x && pytest`는 `cd`도 필요 | 〔코드〕 `config.py:4566-4626` |
| `-y` / `--yolo` | `-y`는 `--auto-approve`(분류기 기반 Auto 모드)다. `--yolo`(무승인)의 짧은 이름이 아니다. `-n`에서는 둘 다 경고 후 무시된다 | 〔코드〕 `main.py:2878-2896`, `:5923-5941` |
| `-n` 종료 코드 | 0 성공(훅이 멈춘 경우 포함) / 1 오류 / 2 사용법 오류 / 124 `--max-turns`·`--timeout` 초과 / 130 Ctrl-C. **채점 결과는 반영되지 않는다** | 〔코드〕 `client/non_interactive.py:3153-3181`, `main.py:6665` |
| `-n` 출력 | 전용 JSON 출력이 없다(`--json`은 `threads`·`skills` 같은 관리 명령 전용). `-q`면 답변만 stdout, 나머지는 stderr | 〔코드〕 `main.py:6610-6649` |
| 디버그 | `DEEPAGENTS_CODE_DEBUG=1` → 클라이언트 `/tmp/deepagents_debug/<thread>.log`, 서버 로그 경로는 종료 때 stderr에 나온다 | 〔코드〕 `_env_vars.py:148-218` |

## 3. 끼어들 수 있는 자리

| 방법 | 어디에 두나 | 쓰기 좋은 곳 | 주의 |
|---|---|---|---|
| **미들웨어** (소스 수정) | `agent.py`의 `create_cli_agent`(`:2570`)가 만드는 `agent_middleware` 목록(`:3073`, 원본에서는 `agent_middleware: list[` 검색). **서브에이전트에도 걸려면 같은 함수 안의 `_subagent_cli_middleware()`(`:2885-2944`)에도 넣는다.** 새 모듈은 `libs/code/deepagents_code/` 아래 | 기록, 지표, 계획 게이트, 메모리 검색·주입 | 서버 프로세스에서 돈다. `Path.cwd()`, `os.getcwd()`, `find_project_root()`를 쓰면 `make lint`가 실패한다(`scripts/check_process_cwd.py`). `wrap_*`는 동기·비동기 둘 다 만든다 〔코드〕 |
| **훅** (소스 수정 없음) | `~/.deepagents/hooks.json`, `{프로젝트 루트}/.deepagents/hooks.json`, 플러그인 | 빠른 시험, 입력 제출 때 컨텍스트 추가 | 아래 "훅의 종료 코드" 표. `-n`은 저장된 신뢰를 보지 않아 **매번 `--trust-project-hooks`** 가 필요하다(`hooks/trust.py:414-438`) 〔코드〕 |
| **스킬** | `{프로젝트 루트}/.deepagents/skills/<이름>/SKILL.md` | 계획 작성 절차, 개선안 문안 | 목록은 대화당 한 번 로드. `allowed-tools`는 표시만 되고 강제되지 않는다. 대화형 `/skill:<이름>`, 실행 시 `-s 이름`(`-n`과 함께 가능) 〔코드〕 |
| **서브에이전트** | `{프로젝트 루트}/.deepagents/agents/<이름>/AGENTS.md` (머리말 `description` 필수, `name`·`model` 선택. 폴더 없이 `<이름>.md`로 두면 무시) | 계획 리뷰어(독립 컨텍스트, 다른 모델) | 머리말로 도구·미들웨어를 설정할 수 없다. **부모의 파일 쓰기·셸 도구를 그대로 갖는다**(`subagents.py:128-130`, SDK `graph.py:758-760`) 〔코드〕 |
| **메모리** | `~/.deepagents/<에이전트>/AGENTS.md`, `{프로젝트 루트}/.deepagents/AGENTS.md`, `{프로젝트 루트}/AGENTS.md` | 항상 지킬 규칙 | 대화당 한 번 로드, 검색 없이 전문 주입. `auto_save`(기본 켜짐)면 모델이 직접 고친다 〔코드〕 `agent.py:3133-3165` |
| **목표·채점** | 대화형 `/goal`, `/rubric`. `-n`은 `--rubric "기준"` 또는 `--rubric @파일`(12,000자 제한, 파일 전체가 기준이 된다) | 완료 조건을 채점에 연결 | `-n`에는 목표 리뷰 화면이 없다(`--goal`은 종료 2). 채점 결과는 콘솔 문구로만 나온다 〔코드〕 `main.py:2823-2855` |

**미들웨어를 넣는 자리** (`agent.py`, 목록 앞쪽이 바깥쪽 〔코드〕 `:3063`)

| 넣을 것 | 위치 (스냅샷 줄 / 원본 검색어) | 이유 |
|---|---|---|
| 기록 | `:3079` 목록 리터럴 바로 뒤, `if not interactive:` 앞 | 가장 바깥이라 안쪽에서 거부된 결과까지 본다. `after_agent`는 역순이라 가장 나중에 돈다(`:3101-3104`) |
| 계획 게이트 | `:3282`(`ShellAllowListMiddleware`) 뒤 ~ `:3406`(사람 승인) 앞 | 승인 창이 뜨기 전에 거부한다 |
| 재시도 계수 | `:3560`(`CodeModelRetryMiddleware`) 뒤 | 안쪽은 시도마다, 바깥쪽은 호출마다 불린다. 같은 이름의 미들웨어는 두 번 넣을 수 없으니 클래스를 나눈다 〔추정〕 |
| 서브에이전트용 | `:2916` `middleware.append(CodeModelRetryMiddleware(` 뒤에 **새 인스턴스** | 파일로 정의한 서브에이전트는 메인 목록을 물려받지 않는다. `general-purpose`만 fork라 부모 인스턴스를 그대로 쓴다(`:3056-3057`, SDK `graph.py:726-735`) 〔코드〕 |

- 작업 폴더는 `create_cli_agent`의 `effective_cwd`(`:2823-2827`)를 생성자로 받거나 `CLIContextSchema.from_payload(runtime.context).workspace["cwd"]`로 읽는다. 같은 컨텍스트에 `thread_id`, `turn_id`, `prompt_id`가 있다(`_cli_context.py:63-91`) 〔코드〕. `effective_cwd`가 `None`이면 설치하지 않는다.
- 거부는 예외가 아니라 `status="error"`인 `ToolMessage`를 돌려준다. 본보기는 `ShellAllowListMiddleware`(`agent.py:880-998`), 파일 I/O가 있는 예는 `memory_guard.py` 〔코드〕.
- `create_cli_agent`에 줄을 추가하는 것은 cwd 검사 허용 목록을 깨지 않는다. `Path.cwd()`가 든 기존 문장을 고치면 깨진다(`scripts/check_process_cwd.py:36-55`) 〔코드〕.

**훅의 종료 코드** (`hooks/capabilities.py:100-246`, `hooks/runner.py:157-206` 〔코드〕)

| 결과 | 뜻 |
|---|---|
| 종료 2 | 이벤트마다 다르다. `PreToolUse`·`PermissionRequest` 거부 / `UserPromptSubmit`·`PreCompact` 차단 / `PostToolUse`·`PostToolUseFailure` 피드백 / `Stop` 계속 진행(연속 8회까지) / 나머지는 진단만. stderr가 이유가 된다 |
| 2가 아닌 실패, 시간 초과 | **차단이 아니다. 진단만 남고 도구가 실행된다.** 게이트 스크립트는 예외 때도 2로 끝내야 한다 |
| 종료 0 + JSON | `PreToolUse`는 `hookSpecificOutput.permissionDecision`이 `allow`/`deny`/`ask`. 여러 핸들러면 `deny > ask > allow` |
| 종료 0 + 일반 텍스트 | `SessionStart`·`UserPromptSubmit`에서만 추가 컨텍스트가 된다. `-n`에서는 사용자 메시지 앞의 `role: system` 메시지로 들어간다(`client/non_interactive.py:2372-2389`) |

- 매처는 공개 이름으로 쓴다: `execute→Bash`, `write_file→Write`, `edit_file→Edit`, `read_file→Read`. **`delete`, `task`는 원래 이름 그대로**다(`hooks/tools.py:68-76`) 〔코드〕. 이벤트는 12종(`hooks/models/domain.py:36-50`), 기본 시간 제한 600초(`UserPromptSubmit` 30초).
- `-n`에서 훅 왕복(인터럽트)은 **turn으로 세어진다.** 기본 한도 50, 넘으면 종료 124(`client/non_interactive.py:174`, `:2412-2440`) 〔코드〕. `PreToolUse` 핸들러가 하나라도 있으면 매처와 무관하게 왕복한다(`hooks/server_middleware.py:898-914`) 〔추정: 도구 호출당인지 모델 스텝당인지 미확인〕.
- 서브에이전트 안의 도구 호출에도 `PreToolUse`·`PostToolUse`는 뜬다. `Stop`은 안 뜬다(`agent.py:2919-2933`) 〔코드〕.

**어느 경로로 구현하나 (권고).** 기준 1이 Python 코드 품질이고 평가자가 제출 소스를 빌드해 실행한다. 그래서 강제·기록은 소스 안 Python으로 만든다. 선택과 근거는 `design/decisions.md`에 적는다.

| 기능 | 권고 경로 | 이유 |
|---|---|---|
| 기록·지표 (4-1~4-3) | **소스 미들웨어** (메인 + 서브에이전트) | 채점 대상 코드와 단위 테스트가 생긴다. 직접 만든 스트림 이벤트는 `-n` 클라이언트가 버리므로(`client/non_interactive.py:1705-1744`) 어차피 파일에 직접 써야 한다. 훅으로 하면 turn을 소모한다 |
| 계획 게이트·범위 검사 (2-4) | **소스 미들웨어** (메인 + 서브에이전트) | 훅은 스크립트가 죽으면 통과되고, 평가자가 `--trust-project-hooks`를 빠뜨리면 게이트가 사라지고, 시연 폴더의 훅 스크립트는 린트 대상도 아니다 |
| 계획 형식 검사 (2-1, 2-2) | **Python 모듈의 순수 함수** (게이트가 호출) | 결정적 판정이고 모델 없이 단위 테스트로 증명된다 |
| 계획 작성 절차 | **스킬** (`-s` 또는 `/skill:`) | 절차 안내는 위임으로 충분하다. 강제는 게이트가 맡는다 |
| AI 리뷰 (2-3) | **서브에이전트** + 판정 기록은 미들웨어(`task` 도구 감싸기) | 독립 컨텍스트와 다른 모델을 파일 하나로 얻는다. 도구 제한이 안 되므로 게이트가 서브에이전트에도 걸려야 한다 |
| 경험 저장·검색·주입 (3-1, 3-2) | **소스 미들웨어** (`before_agent`, `after_agent`) 〔추정〕. 빠른 시험은 `UserPromptSubmit` 훅 | 조회·저장 이벤트를 같은 기록에 남길 수 있다 |
| 개선안·전후 비교·조회 (3-3, 3-4, 4-4) | **`scripts/` 아래 Python 스크립트** (+ 부르는 스킬) | 기록 파일만 읽으므로 모델 없이 재현된다. `scripts/**`는 `print`가 허용된다(`pyproject.toml` per-file-ignores) 〔코드〕 |
| 항상 지킬 규칙 | 프로젝트 루트 `AGENTS.md` | 부탁 수준이다. 어기면 안 되는 것은 게이트로 옮긴다 |

## 4. 인수 기준별 구현 지도

### 1. 코드 품질 [10]
| 항목 | 할 일 | 구현 위치 | README 확인 방법 |
|---|---|---|---|
| 1-1 스타일 | 새 모듈과 테스트가 `ruff check`, `ruff format`, `ty`를 통과. 줄 길이 88, 한글은 폭 2라 한 줄 약 40자가 한도다 〔추정〕 | 저장소의 `pyproject.toml` 설정을 그대로 쓴다(느슨하게 바꾸지 않는다) | `uv run --all-groups ruff check <파일들>` → `All checks passed!`, `uv run --all-groups ruff format --check <파일들>` → 변경 0건, `make lint` 종료 0. `ruff`·`ty`는 `test` 그룹에 있어 `--all-groups`가 필요하다 〔코드〕 |
| 1-2 명명·import | 상대 import 금지, `from __future__ import annotations`, 타입 전용 import는 `if TYPE_CHECKING:` 안, 예외 메시지는 변수에 담아 던지기, `print` 대신 `logger` | 본보기 `memory_guard.py:24-47`, `model_retry.py:1157-1190` 〔코드〕 | 같은 명령 |
| 1-3 docstring | google 형식. 모듈 첫 줄, 클래스, `__init__`, 공개 함수에 역할·`Args:`·`Returns:`. 반환·예외가 있으면 해당 구역이 있어야 한다 〔추정〕 | 본보기 `_tracing.py:24-49`, `memory_guard.py` | 린트 통과 + 주요 함수 표 |

- 테스트 설정: 경고가 곧 실패, 시간 제한 30초, 소켓 차단, `asyncio_mode = "auto"`(`pyproject.toml:347-395`) 〔코드〕. 본보기는 `tests/unit_tests/test_memory_guard.py`.
- CLI 플래그를 추가하면 도움말 화면도, 슬래시 명령을 추가하면 명령 목록(`make commands-catalog`)도 고쳐야 린트·테스트가 통과한다 〔코드〕. 새 플래그·명령 없이 미들웨어와 `scripts/`로 끝내는 쪽이 간단하다.

### 2. 계획·리뷰·승인 [10]
| 항목 | 할 일 | 구현 위치 | README 확인 방법 |
|---|---|---|---|
| 2-1 요구사항·범위·완료 조건 | 계획 양식의 필수 구역. 완료 조건만 따로 파일로 빼 `--rubric @파일`로 채점과 잇는다 | 형식 검사 모듈 + 계획 스킬 | 요청 하나 → 세 구역이 채워진 계획 파일 |
| 2-2 수정 대상·순서·테스트 방법 | 필수 구역 + 형식 검사. 수정 대상은 게이트가 읽을 수 있는 경로 목록으로 쓴다 | 같은 모듈 | 구역이 빠진 계획이 걸린 기록, 단위 테스트 |
| 2-3 AI 리뷰와 반영 | `plan-reviewer` 서브에이전트가 승인/수정과 의견을 낸다. 수정이면 다음 버전으로 고치고 리뷰 이력에 남긴다. 리뷰어 `model`은 허용된 모델로 지정 | 서브에이전트 + `task` 호출을 감싸는 미들웨어 | 테스트 방법이 빠진 요청 → 수정 판정 → 반영된 다음 버전 |
| 2-4 승인 후 변경·범위 재검토 | 게이트가 **`write_file`, `edit_file`, `delete`, `execute` 네 도구**를 본다(`agent.py:1001-1003`) 〔코드〕. 승인 전이거나 목록 밖이면 `status="error"` 메시지로 거부한다. 승인 표시와 계획 파일을 모델이 직접 고쳐 통과하지 못하게 그 경로도 보호한다 | 게이트 미들웨어 (메인 `:3282` 뒤 + `_subagent_cli_middleware`) | 승인 전 편집이 막힌 기록, 계획 밖 파일 편집이 막히고 계획이 갱신된 기록, 서브에이전트의 편집도 막힌 기록 |

- 셸로 파일을 고치는 우회는 `-S` 허용 목록(리다이렉트 거부)으로 좁힐 뿐 다 막지 못한다. 남는 우회 경로는 표로 적는다.
- `js_eval`(인터프리터)의 도구 호출은 승인 경로를 거치지 않는다(`agent.py:2708-2718`) 〔코드〕. 미들웨어 게이트도 우회하는지는 〔미확인〕이다. 시연은 `--no-interpreter`로 한다.

### 3. 메모리·자기개선 [10]
| 항목 | 할 일 | 구현 위치 | README 확인 방법 |
|---|---|---|---|
| 3-1 저장·유지 | 규칙은 프로젝트 루트 `AGENTS.md`, 경험은 별도 파일(예: `.deepagents/memory/experiences.jsonl`). 작업이 끝나거나 실패할 때 기록 | 미들웨어 `after_agent` 〔추정〕 | 실행 A에서 저장 → 새 `-n` 실행에서 남아 있음 |
| 3-2 검색·활용 | 요청으로 경험을 검색해 조금만 **메시지로** 주입한다(시스템 프롬프트를 바꾸면 캐시에 영향 〔미확인: 측정 필요〕). 주입 항목을 계획과 기록에 남긴다 | 미들웨어 `before_agent` 〔추정〕 | 비슷한 작업 → 계획에 "참조한 경험", 기록에 메모리 조회 이벤트 |
| 3-3 개선안 생성 | 도구 오류, `execute`의 0 아닌 종료 코드, 채점 미충족을 모아 개선안 파일(원인, 변경안, 기대 효과)을 만든다. 바로 적용하지 않는다 | `scripts/` 스크립트 + 스킬 | 일부러 실패시킨 작업 → 개선안 파일 |
| 3-4 전후 검증·반영 | 고정 작업을 현재 버전과 후보로 각각 돌려 비교하고 회귀가 없을 때만 반영 | 평가 스크립트 | 전후 비교표, 탈락안 미반영, 채택안이 다음 작업에 쓰인 기록 |

- `-a 이름`은 사용자 쪽(`~/.deepagents/이름/`의 메모리·스킬·서브에이전트)만 분리한다. **프로젝트 쪽 파일은 공유된다.** 통째로 나누려면 `DEEPAGENTS_HOME=<절대경로>`를 쓴다(`_paths.py:78`, `:295-344`) 〔코드〕.
- 반영 효과는 새 대화에서 보인다. 메모리와 스킬 목록은 대화당 한 번만 로드된다.
- `auto_save`는 끈다(`config.toml`의 `[memory] auto_save`, 환경 변수 `DEEPAGENTS_CODE_MEMORY_AUTO_SAVE`). 끄면 프롬프트만 읽기 전용판으로 바뀌고 편집 도구는 그대로다(`agent.py:3142-3154`) 〔코드〕. 직접 편집은 게이트로 막는다. `memory_guard.py`는 온보딩 이름 구역만 보호한다.

### 4. 모니터링 [10]
| 항목 | 할 일 | 구현 위치 | README 확인 방법 |
|---|---|---|---|
| 4-1 전체 흐름 기록 | 요청별 기록 파일(키는 `thread_id` + `turn_id`). 단계는 도구로 판정한다: 리뷰어 `task` → 리뷰, 쓰기·편집·삭제 → 코드 변경, `execute`의 테스트 명령 → 테스트 | 기록 미들웨어 (부록 A, B) | 요청 하나 뒤 기록에 다섯 단계가 시간순으로 있음 |
| 4-2 호출·도구·메모리·개선 기록 | 모델 호출(`wrap_model_call`), 도구 실행, 메모리 조회·저장, 개선안 이벤트와 오류. **`execute`는 실패해도 `status="success"`다.** `artifact["exit_code"]`나 본문 끝 `[Command failed with exit code N]`으로 판정한다(SDK `middleware/filesystem.py:2922-2941`) 〔코드〕 | 같은 미들웨어 | 일부러 실패시킨 명령 → 오류로 기록됨 |
| 4-3 지표 | 요청이 끝날 때 총 시간, 모델·도구 호출 수, 재시도 수, 토큰. 재시도 신호는 `model_retry` 이벤트인데(`model_attempt`는 시도의 시작·완료 경계) 클라이언트로만 가서 다른 미들웨어가 받을 수 없다(`model_retry.py:969-1038`) 〔코드〕. 재시도 미들웨어 **안쪽**에서 모델 호출을 감싸 "시도 수 − 호출 수"로 센다 〔추정〕. 못 세면 빈값 | 기록 미들웨어 + 안쪽 계수 미들웨어 | 요약 출력. 끝에 찍히는 사용량 표(`_session_stats.py:1388-1465`)와 대조 |
| 4-4 조회 | 요청을 지정하면 첫 실패 이벤트와 직전 맥락을 보여준다. `dcode threads list --json`과 내장 스킬 `deepagents-thread-inspector`의 `scripts/inspect_sessions.py`는 보조로 쓴다 | `scripts/` 스크립트 | 실패한 요청 → "첫 실패: 어느 단계, 어느 호출, 원인" |

- LangSmith는 키와 추적 플래그가 둘 다 있어야 켜진다(`config.py:4636-4657`) 〔코드〕. 키 없이 동작하는 로컬 기록을 주 증거로 삼는다.
- 서버는 블로킹 호출을 잡는 런타임으로 뜬다(`client/launch/server.py:425-431`, `pyproject.toml:94-96`). `async def` 훅 안의 파일 쓰기는 `asyncio.to_thread`로 넘긴다 〔추정: 실행 미확인〕.
- 안쪽에서 인터럽트(승인, 훅)가 걸리면 `GraphBubbleUp`이 올라오고 재개 때 감싸기가 다시 불린다. 오류로 세지 않게 먼저 다시 던진다(`model_retry.py:637-639`) 〔코드. 재호출 횟수는 미확인〕.
- fork 서브에이전트는 부모 미들웨어 인스턴스를 같이 쓴다. 인스턴스에 요청별 상태를 두지 않는다. 기록에 키·비밀이 들어가지 않게 가린다.

## 5. 진행 순서 (dcode 기준)

| 단계 | 먼저 확인할 것 | 끝났다는 기준 |
|---|---|---|
| S0 | 2절의 결정. 원본 커밋에서 `make lint`가 종료 0인가(8절 3번). 고른 모델로 한 번 응답하는가(11번) | 빌드·실행 명령이 README 초안에 있다 |
| S1 (S2와 병렬) | 고정 작업 5건을 `dcode -n`과 `--rubric`으로 돌린다. **종료 코드는 채점 결과를 담지 않는다.** 통과 여부는 `Acceptance criteria satisfied` 문구(`client/non_interactive.py:1118-1163`)나 자체 기록 파일로 판정한다 | 평가가 명령 한 줄로 다시 돈다 |
| S2 | 기록 미들웨어를 메인 목록 맨 앞과 서브에이전트 묶음에 넣는다. 새 모듈이 `make lint`를 통과하는가 | 요청 하나의 기록과 요약 지표가 나온다 |
| S5 (S3과 병렬) | 계획 양식 → 리뷰어 서브에이전트 → 게이트. 게이트를 `_subagent_cli_middleware()`에도 넣었는가. `delete`와 `execute`도 보는가 | 승인 전 편집과 계획 밖 편집이 메인과 서브에이전트 양쪽에서 막힌다 |
| S3 | 규칙과 경험 저장소. `auto_save` 끄기 | 새 대화에서 저장소가 남아 있다 |
| S6 | 검색·주입 → 개선안 → 전후 비교(`DEEPAGENTS_HOME`으로 프로필 분리) | 개선 한 바퀴가 기록에 있다 |
| S8 | README에 항목별 확인 방법. 깨끗한 환경에서 그대로 돌린다 | `criteria-check` 표의 모든 항목이 "실행해서 확인"이다 |

## 6. 함정

1. 서버 코드에서 `Path.cwd()`, `os.getcwd()`, `find_project_root()`를 쓰면 `make lint`가 실패한다. 서버 하나가 여러 작업 폴더를 맡기 때문이다 〔코드〕.
2. 메모리와 스킬 목록은 대화당 한 번만 로드된다. "다음 작업에 반영"은 새 대화로 보인다 〔코드〕.
3. `-n`에서는 셸에 `-S`가, 프로젝트 훅에 `--trust-project-hooks`가 **매번** 필요하다(화면에서 승인해 둔 것은 무시된다). 훅을 쓰면 `--max-turns`도 넉넉히 준다. README 확인 명령에 빠뜨리지 않는다 〔코드〕.
4. `-n`은 파일 쓰기·편집·삭제를 승인 없이 실행한다. 게이트가 없으면 "승인 후 변경"은 지켜지지 않는다 〔코드〕.
5. 평가 스크립트가 종료 코드만 보면 "기준 미충족"도 통과로 센다. 124(한도 초과)와 1(오류)만 종료 코드로 구분된다 〔코드〕.
6. 훅 게이트는 스크립트가 예외로 죽으면(종료 1) 열린다. 미들웨어 게이트도 판정 중 예외가 나면 거부로 처리하게 짠다 〔코드 / 설계 권고〕.
7. 게이트가 `write_file`·`edit_file`만 보면 `delete`, `execute`, 서브에이전트로 뚫린다 〔코드〕.
8. dcode는 **`.git`이 있는 상위 폴더**의 `AGENTS.md`, `.deepagents/`, `.agents/skills`, `.claude/skills`를 읽고, 홈의 `~/.agents/skills`, `~/.claude/skills`도 읽는다. dcode 소스 폴더 안에서 시연하면 소스 저장소의 설정이 섞인다. 시연은 `git init`한 별도 폴더에서 하고 필요하면 `DEEPAGENTS_HOME`으로 프로필도 나눈다 〔코드〕.
9. 로컬 셸에는 경계가 없다. `-S all`로 시연하지 않는다 〔코드〕 `agent.py:3209-3214`.
10. 리뷰어(`model`)와 채점 모델(`--rubric-model`, 기본은 메인 모델)을 허용된 모델로 지정하고 `[models] allowed`로 강제한다. Auto 모드는 `-n`에서 쓰이지 않는다 〔코드〕.
11. 기록이 작업 폴더의 `.deepagents/` 아래 쌓이면 시연 저장소의 `.gitignore`에 넣는다. 대화 기록(`transcripts/`)은 훅이 설정돼 있을 때만 생기므로 증거로 기대하지 않는다 〔코드〕.

## 7. 문서와 코드가 다른 곳

| 문서 | 실제 | 확신도 |
|---|---|---|
| `~/.deepagents/<에이전트>/memories/`에 자동 메모리가 쌓인다 | 그런 코드가 없다. `AGENTS.md`를 편집 도구로 고친다 | 〔코드〕 |
| `dcode --install openrouter`로 추가 패키지를 넣는다 | 소스 설치에서는 거부된다. `uv sync --extra`로 넣는다 | 〔코드〕 |
| (저장소 문서 일부) 화면 없는 실행은 `-x`/`--execute` | 이 버전의 플래그는 `-n`/`--non-interactive`다 | 〔코드〕 `AGENTS.md:3` |
| 채점 반복 한도에 닿으면 "수정 필요"로 끝난다 | `… (iteration limit reached)` 상태로 바뀐다. 문서 쪽 문구는 대조하지 않았다 | 〔코드〕 SDK `middleware/rubric.py:75-94`, `client/non_interactive.py:1143-1148` |
| 스킬 탐색 계층 4~6개 | 8개(내장 → 플러그인 → 사용자 2 → 프로젝트 2 → `.claude` 2, 뒤가 이긴다) | 〔코드〕 `agent.py:2491-2553` |
| 공식 문서의 훅 이벤트 표(11행) | 12종. `PostToolUseFailure`가 빠져 있다 | 〔코드〕 |
| 확장으로 넣은 미들웨어는 `/reload`로 반영 | 저장소 문서는 `/restart`라고 한다. `/reload`가 그래프를 다시 조립하는지 코드는 읽지 않았다 | 〔문서〕〔미확인〕 |

## 8. 실행해서 확인할 것

**아래는 아무것도 돌려 보지 않았다.** "기대"는 코드를 읽고 쓴 것이라 문구와 수치가 다를 수 있다. 다르면 이 문서를 고친다. 원본을 받은 폴더의 `libs/code`에서 실행한다.

| # | 명령 | 기대 | 확인하는 것 |
|---|---|---|---|
| 1 | `uv sync --group test --extra openrouter` | 설치 목록에 `langchain-openrouter`, `deepagents` 0.7.14가 `../deepagents` 경로로 | 빌드, OpenRouter extra |
| 2 | `uv run dcode --version` | `deepagents-code 0.1.69`, SDK 0.7.14, 소스 경로 | 진입점 |
| 3 | `make lint; echo "exit=$?"` (고치기 전) | `All checks passed!`, 포맷 diff 없음, `exit=0` | 원본이 깨끗한 출발점인가 |
| 4 | 주석판에서 `uv run --all-groups ruff check deepagents_code --select E501 --statistics` | `E501` 1,750건 이상, 종료 1 | 주석판 린트 예상 |
| 5 | 주석판에서 같은 명령에 `--select RUF001,RUF002,RUF003` | 0~10건 | 주석 속 기호 |
| 6 | `make test TEST_FILE=tests/unit_tests/test_memory_guard.py` | `17 passed` | 테스트 환경 |
| 7 | 부록 A·C를 완성해 넣고 두 파일에 `uv run --all-groups ruff check`, `ruff format --check`, `ty check` | 셋 다 통과. 실패하면 규칙 코드를 보고 고친다 | 초안의 린트 적합성 |
| 8 | `make test TEST_FILE=tests/unit_tests/test_run_log.py` | `2 passed` | 초안 동작 |
| 9 | 부록 B 반영 뒤 `make lint; echo "exit=$?"` | `exit=0`. cwd 검사에 `unreviewed`·`stale` 없음 | 삽입이 허용 목록을 안 깨는가 |
| 10 | (확인 뒤 되돌린다) `run_log.py`에 `Path.cwd()` 한 줄을 넣고 `uv run --all-groups python scripts/check_process_cwd.py deepagents_code; echo $?` | `unreviewed Path.cwd call` 안내, 종료 1 | 함정 1 |
| 11 | 시연 폴더에서 `OPENROUTER_API_KEY=… uv run --project <libs/code> dcode -n "hello.txt 파일을 만들어줘" -M openrouter:<모델> --max-turns 20 --timeout 300; echo "exit=$?"` | `Task completed`, `Usage Stats` 표, `exit=0`, `.deepagents/runs/<thread>.jsonl`에 `write_file` 기록 | 모델 연결, 기록 미들웨어 |
| 12 | 11번에 `--rubric "world.txt 파일이 있어야 한다" --rubric-max-iterations 1` | 미충족 문구가 나오고 **`exit=0`** | 채점 결과가 종료 코드에 없는가 |
| 13 | 부록 D를 넣고 플래그 없이, 다음에 `--trust-project-hooks`를 붙여서 | 없으면 파일이 생긴다. 있으면 `Write blocked by hook: …`가 도구 오류로 보이고 파일이 안 생긴다 | 훅 신뢰, 거부 문구 |
| 14 | 13번을 `--max-turns 3`으로 | 도구 호출 몇 번 만에 turn 초과, `exit=124` | 훅 왕복이 turn으로 세어지는가 |
| 15 | `.deepagents/agents/reviewer/AGENTS.md`를 만들고 "reviewer에게 a.txt를 만들게 해줘" | 서브에이전트의 `write_file`이 기록에 남는가(부록 B의 서브에이전트 삽입 전후 비교) | 서브에이전트가 메인 목록을 안 물려받는가 |
| 16 | `DEEPAGENTS_CODE_DEBUG=1`로 11번을 돌리고 stderr의 `Server log preserved at:` 경로를 연다 | `BlockingError` 없음. `asyncio.to_thread`를 빼면 나오는가 | 블로킹 I/O 제약 |

**그 밖에 확인하지 못한 것:** `AgentMiddleware` 기반 클래스의 원본 서명(스냅샷에 langchain 패키지가 없어 하위 클래스에서 역으로 읽었다)과 `wrap_*`를 동기만 정의했을 때의 동작 · ruff 세부 판정(DOC 규칙이 요구하는 구역, `except Exception … raise`의 판정) · `before_agent`·`after_agent`에서 메시지와 요약을 다루는 방식 · `js_eval`이 `wrap_tool_call`을 우회하는지 · 훅 이벤트의 `agent_id`·`agent_type`이 실제로 채워지는지 · `[models] allowed`의 와일드카드와 `config.toml`의 프로젝트 단위 위치 · `auto_save` 환경 변수의 값 형식 · 과제 모델의 OpenRouter ID.

## 부록. 초안 (전부 실행 검증 안 함)

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
