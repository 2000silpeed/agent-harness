# 기반 참고: dcode로 Coding Assistant 만들기

> dcode(deepagents-code **0.2.5**, SDK `deepagents==0.7.34`, Python 3.14, 업스트림 커밋 `e20be5f22e87dd088d706525917b51f1a2945c63`)를 기반으로 인수 기준(`../CRITERIA.md`)을 채울 때 보는 문서다. 단계 설명은 `../METHOD.md`에 있다.
> **기준 저장소**는 dcode 0.2.5 사본과 설명 문서, 참고 구현이 들어 있는 `github.com/HyunjunJeon/sds_ax_advanced_2026`이다. 사본은 그 저장소의 `Day09/`에 있다.
> **이 문서의 어떤 내용도 직접 실행해서 확인하지 않았다.** 기준 저장소 `Day09/`의 코드와 문서를 읽기만 했다. 설치·린트·테스트·실행 결과는 읽고 낸 예상이다. 8절의 명령을 직접 돌려 확정한다.
> **경로:** 따로 적지 않으면 기준 저장소의 `Day09/deepagents/libs/code/deepagents_code/` 기준이다. `pyproject.toml`, `Makefile`, `scripts/`, `tests/`, `AGENTS.md`, `HOOKS.md`, `EXTENSIONS.md`, `DEVELOPMENT.md`는 `Day09/deepagents/libs/code/` 기준이고, `Day09/…`·`Day08_new/…`처럼 `Day`로 시작하는 경로는 기준 저장소 루트 기준이다. **줄 번호는 `# [해설]` 주석이 들어간 사본 기준이다.** 원본에서는 함께 적은 이름으로 검색한다.
> **SDK 소스는 사본에 없다**(설치 때 PyPI에서 받는다). SDK 동작은 `Day09/` 문서가 적은 내용〔문서〕이나 그 문서의 실행 기록으로만 적었다.
> **확신도 표기:** 〔코드〕 코드를 읽어 확인(실행은 안 함) · 〔문서〕 문서에만 있음 · 〔저장소 실행 기록〕 기준 저장소 문서가 실행해서 확인했다고 적은 것(`Day09/CLAIM_CHECKS.md`, `TRACE_WALKTHROUGH.md`, `TEST_MAP.md`, `STATE_AND_STORAGE.md`) · 〔추정〕 읽고 낸 예상 · 〔미확인〕 확인 못 함.

## 1. 한눈에 보기

| 인수 기준 | 있는 것 | 비어 있는 것 (만들 것) |
|---|---|---|
| 1 코드 품질 | ruff 전체 규칙(`select = ["ALL"]`, preview), 줄 길이 설정 없음(기본 88), google docstring, 상대 import 금지, 타입 검사 `ty`(0.0.61 고정), cwd 검사 스크립트 〔코드〕 `pyproject.toml:171-195`, `:253-359` | 새 코드가 같은 검사를 통과해야 한다. **이 사본에서는 `make lint`·`make test`가 그대로 돌지 않는다**(2절). 검사 도구를 따로 깔고 그 명령을 README에 적는다 |
| 2 계획·리뷰·승인 | 대화형 실행의 도구 단위 사람 승인. **`-n` 기본 실행에는 승인 미들웨어가 스택에 아예 없다** 〔저장소 실행 기록〕. `/goal`·`/rubric`과 읽기 전용 채점 에이전트, 파일로 정의하는 서브에이전트, 파일 도구 허용 목록(`--allow-fs-tools`), 같은 대화를 이어 가는 `-r <ID> -n` 〔코드〕 | **계획 모드가 없다.** `plan` 검색에 걸리는 것은 훅 전송 규격의 열거값 하나뿐이고 쓰는 곳이 없다(`hooks/models/wire.py:36`) 〔코드〕. 계획 양식, 형식 검사, AI 리뷰, 승인 기록, 게이트 |
| 3 메모리·자기개선 | `AGENTS.md` 주입, 내장 스킬 `remember`, `-n` 전용 메모리 안내문(검증한 사실을 `edit_file`로 저장하라고 시킨다) 〔코드〕 `agent.py:213-246`, `:3256-3293` | **검색이 없다**(전문 주입). 경험 저장소, 검색·주입, 개선안 생성·검증·채택 |
| 4 모니터링 | LangSmith 연동과 git 작업 귀속 메타데이터(`git_trace.py`, LangSmith 실행에만 붙는다), 모델 재시도, 비용 집계와 실행 끝의 `Usage Stats` 표, 체크포인트 DB(`<프로필>/.state/sessions.db`)와 내장 스킬 `deepagents-thread-inspector`, 훅용 대화 기록(`<프로필>/transcripts/`, 훅이 있을 때만 채워진다) 〔코드〕〔저장소 실행 기록〕 | **단계 단위 로컬 기록이 없다.** 요청별 계획·리뷰·코드·테스트·결과 이벤트, 요약 지표, 실패 지점 조회 |

- 업스트림 커밋 제목의 talon은 별도 패키지(`deepagents-talon`)다. 사본에는 그 패키지가 가져다 쓰는 이름을 유지하라는 주석만 있다(`tools.py:58`, `mcp_tools.py:87`). 사본 안의 비동기 서브에이전트는 `config.toml`의 `[async_subagents]`(원격 LangGraph 배포)뿐이다(`agent.py:1194`) 〔코드〕. 기준을 채우는 데 쓸 것은 없다.

## 2. 환경과 빌드 (S0에서 정할 것)

| 결정 | 내용 | 근거 |
|---|---|---|
| 출발 소스 | **`Day09/deepagents/libs/code`를 통째로 복사해 제출 저장소의 출발점으로 삼는다.** 저장소 스크립트가 설치·실행하는 것이 이 사본이다 〔문서〕. 복사본에서는 `# [해설]` 줄을 지운다. 39개 파일 2,080줄이 모두 독립된 주석 줄이고(코드 뒤에 붙은 것 0건), 그중 1,251줄이 88자를, 1,873줄이 화면 폭 88을 넘어 E501에 걸릴 것으로 본다 〔추정: 글자 수는 읽기 전용 도구로 셌고 ruff는 돌리지 않았다〕. 지우면 원본 커밋과 같은 코드가 된다 〔문서: 주석 줄만 더했다는 설명〕 | `Day09/README.md` |
| 저장소 구조 | `libs/code`만 있다. `[tool.uv.sources]`가 가리키는 `../deepagents`, `../acp`, `../partners/*`가 없어 그 폴더에서 `uv sync`가 실패한다 〔저장소 실행 기록: `uv sync --frozen --group test` 실패, `Day09/TEST_MAP.md`〕. 설치는 `uv pip install --no-sources`로 하고 SDK는 PyPI에서 받는다 | `pyproject.toml:28`, `:224-231` |
| 가상환경 | Python `>=3.14,<3.15` 전용이다(괄호 없는 `except A, B:` 문법). 기준 저장소 루트 환경(3.13)과 따로 둔다. 기준 저장소 안에서 `uv`를 부를 때는 루트의 날짜 고정이 상속되지 않게 `--no-config`를 붙인다 〔문서〕 | `pyproject.toml:13`, `Day09/scripts/setup_dcode.sh:13-17` |
| 프로필 | `Day09/scripts/dcode`는 `DEEPAGENTS_HOME`이 비어 있으면 `~/.deepagents-day09`를 쓴다. 키(`.state/auth.json`), `config.toml`, `sessions.db`, 사용자 `AGENTS.md`가 여기 있다. README의 확인 명령에는 `DEEPAGENTS_HOME=<절대경로>`를 적어 평가자의 프로필과 섞이지 않게 한다 | `Day09/scripts/dcode:29`, `_paths.py:78` 〔코드〕 |
| 작업·시연 위치 | **`git init`한 별도 폴더.** dcode는 `.git`이 있는 가장 가까운 상위 폴더를 프로젝트 루트로 보고, 없으면 프로젝트 메모리·스킬·서브에이전트를 로드하지 않는다. 기준 저장소 안에서 돌리면 그 저장소 루트의 `AGENTS.md`가 지침으로 읽힌다 | `_git.py:139-163`, `project_utils.py:76-98`, `:136-147` 〔코드〕 |
| 모델 | `-M provider:model`이나 `[models].default`가 있어야 한다. 없으면 `No model configured` 오류가 난다 〔코드. `-n`에서 어떻게 끝나는지는 미확인〕. 과제의 모델 제한은 〔미확인〕. 기준 저장소가 OpenRouter ID로 쓰는 문자열은 `z-ai/glm-5.3-flash`, `deepseek/deepseek-v4.1-flash`, `qwen/qwen3.8-flash`다 〔문서. dcode에서 동작하는지는 미확인〕 | `config.py:6059-6093`, `Day08/README.md`, `Day08_new/guard_lab/lm_guards.py:32-38` |

```bash
# 기준 저장소 루트에서(제출용 복사본의 같은 절차는 부록 B). 여기까지는 모델을 부르지 않는다
bash Day09/scripts/setup_dcode.sh        # Day09/.venv(3.14) + 사본 editable 설치. 검사 도구·OpenRouter는 안 깔린다
bash Day09/scripts/smoke_dcode.sh        # 가짜 모델로 서버 기동 → 응답 → 종료
cd Day09/deepagents/libs/code            # 아래 한 줄은 저장소 기록에 없는 조합이다 〔추정〕
uv pip install --no-config --no-sources --python ../../../.venv/bin/python -e ".[openrouter]" --group test
V=../../../.venv/bin                     # make lint가 하는 다섯 가지를 직접 돌린다
$V/ruff check deepagents_code/<새 모듈>.py tests/unit_tests/test_<새 모듈>.py
$V/ruff format --check deepagents_code/<새 모듈>.py tests/unit_tests/test_<새 모듈>.py
$V/ty check --python ../../../.venv deepagents_code/<새 모듈>.py
$V/python scripts/generate_commands_catalog.py --check && $V/python scripts/check_process_cwd.py deepagents_code
$V/python -m pytest -p no:cacheprovider --disable-socket --allow-unix-socket tests/unit_tests/test_<새 모듈>.py -q
# 시연: git init한 별도 폴더에서 절대 경로로 부른다
export DEEPAGENTS_HOME=/abs/profile
/abs/Day09/scripts/dcode auth set openrouter --from-env OPENROUTER_API_KEY
/abs/Day09/scripts/dcode -n "요청" -M openrouter:<모델 ID> -S "pytest" --max-turns 40 --timeout 900 < /dev/null
```

| 주제 | 사실 | 확신도·근거 |
|---|---|---|
| 설치 스크립트가 까는 것 | `uv venv --python 3.14` 뒤 `uv pip install --no-config --no-sources -e deepagents/libs/code`. extra도 `test` 그룹도 없다. `ruff`·`ty`·`pytest`·`langchain-openrouter`는 따로 넣는다 | 〔코드〕 `Day09/scripts/setup_dcode.sh:30-31`, `pyproject.toml:131`, `:171-195` |
| 검사 도구 설치 | 임시 가상환경에 `uv pip install --no-sources -e . --group test`로 넣고 단위 테스트 57건이 통과했다는 기록이 있다. 잠금 버전이 아니라 최신 의존성이라 `-W ignore::DeprecationWarning`을 붙였다고 한다. `Day09/.venv`에 넣는 것과 ruff·ty 실행은 기록에 없다 | 〔저장소 실행 기록〕 `Day09/TEST_MAP.md` / 나머지 〔미확인〕 |
| `make lint`·`make test`·`make bootstrap` | **쓰지 않는다.** 전부 `uv run`(잠금 고정)이라 이 구조에서는 실패할 것으로 본다 〔추정〕. `make lint`의 내용은 ruff check, ruff format `--diff`, ty check, 명령 목록 검사, cwd 검사다. `bootstrap`은 git 최상위에 pre-commit 훅을 깐다 | 〔코드〕 `Makefile:5-6`, `:70-76`, `:101-103` |
| ty 설정 | `[tool.ty.environment] extra-paths`가 없는 폴더(`../deepagents` 등)를 가리킨다. 이 상태에서 ty가 어떻게 도는지는 〔미확인〕 | 〔코드〕 `pyproject.toml:233-241` |
| OpenRouter | extra 이름은 `openrouter`. `dcode --install openrouter`는 editable 설치에서 거부된다. 위의 `uv pip install -e ".[openrouter]"`로 넣는다 | 〔코드〕 `pyproject.toml:131`, `update_check.py:4586-4630` |
| 키 우선순위 | `--model-params`의 `api_key` > `dcode auth set`으로 저장한 키 > 환경 변수(`DEEPAGENTS_CODE_OPENROUTER_API_KEY`가 있으면 `OPENROUTER_API_KEY` 대신 읽힌다). 저장 키와 접두 변수가 함께 있을 때 어느 쪽이 쓰이는지는 기준 저장소 문서도 확인하지 못했다. 한 가지 방법만 쓴다 | 〔코드〕 `model_config.py:2582-2616`, 〔문서〕 `Day09/CONFIG_REFERENCE.md` |
| 다른 게이트웨이 | `config.toml`의 `[models.providers.<이름>]`에 `class_path`, `models`를 적는다(저장소 스크립트의 가짜 모델이 이 방식이다). OpenRouter 주소는 `OPENROUTER_API_BASE`로 바꾼다 | 〔코드〕 `Day09/scripts/smoke_dcode.sh:27-34`, `model_config.py:1107-1140` |
| 금지 모델 강제 | `[models] allowed = ["openrouter:*"]`처럼 공급자 전체, 또는 정확한 `provider:model`. 메인·채점·분류기·서브에이전트 `model`을 기동 때 검사하고 걸리면 기동이 실패한다 | 〔코드〕 `model_config.py:553-620`, `:3819`, `agent.py:3084-3147`, `:3777-3778` |
| `-n`의 승인 | 승인 모드가 없다. 셸 허용 목록 없음: 셸 꺼짐, **나머지 도구(파일 쓰기·편집·삭제)는 전부 그냥 실행**. 제한 목록: 셸 명령만 미들웨어가 검사. `all`: 전부 실행. `PermissionRequest` 훅이 있으면 이 지름길이 꺼지고 승인 대상 호출이 모두 클라이언트로 온다 | 〔코드〕 `client/non_interactive.py:3106-3150` 〔저장소 실행 기록〕 |
| 셸 허용 목록 | `-S`가 없어도 `DEEPAGENTS_CODE_SHELL_ALLOW_LIST`나 `config.toml`의 `[shell] allow_list`가 있으면 셸이 켜진다. `&&`, `\|\|`, `\|`, `;`로 나눈 구간마다 첫 단어를 본다. `>`, `<`, `$(`, 백틱, `${`가 있으면 무조건 거부라 **`2>&1`도 막힌다** | 〔코드〕 `config_manifest.py:2670-2682`, `config.py:4439-4454`, `:4537-4592` |
| `-y` / `--yolo` | 둘 다 `-n`에서는 경고 후 무시된다 | 〔코드〕 `main.py:2887-2906`, `:6037-6054` |
| `-n` 종료 코드 | 0 성공(훅이 멈춘 경우 포함) / 1 오류 / 2 사용법 오류 / 124 `--max-turns`·`--timeout` 초과 / 130 Ctrl-C. **채점 결과는 반영되지 않는다** | 〔코드〕 `client/non_interactive.py:3272-3315`, `main.py:6810-6829` |
| `-n`의 stdin | 터미널이 아닌 stdin은 끝까지 읽어 요청 앞에 붙인다. 스크립트·CI에서는 `< /dev/null`을 붙인다 | 〔코드〕 `main.py:4046-4118` 〔문서〕 `Day09/README.md` |
| `-n` 출력 | `-q`면 답변만 stdout, 나머지는 stderr(`Thread: <id>` 줄은 `-q`에서도 나온다). 실행 결과를 JSON으로 내는 옵션은 없다(`--json`은 관리 명령 전용) | 〔코드〕 `client/non_interactive.py:3021`, `:3043-3047`, `main.py:6569-6672` |
| 디버그 | `DEEPAGENTS_CODE_DEBUG=1` → 기본 위치 `/tmp/deepagents_debug`, 서버 로그 경로는 종료 때 stderr에 나온다 | 〔코드〕 `_env_vars.py:144-209`, `client/launch/server.py:814` |

## 3. 끼어들 수 있는 자리

| 방법 | 어디에 두나 | 쓰기 좋은 곳 | 주의 |
|---|---|---|---|
| **미들웨어** (소스 수정) | `agent.py`의 `create_cli_agent`(`:2622`)가 만드는 `agent_middleware` 목록(`:3191`). **파일로 정의한 서브에이전트에도 걸려면 같은 함수 안의 `_subagent_cli_middleware()`(`:2989-3070`)에도 넣는다.** 새 모듈은 `deepagents_code/` 아래 | 기록, 지표, 계획 게이트, 메모리 검색·주입 | 서버 프로세스에서 돈다. 클래스마다 `trace_policy = TracePolicy(process_inputs=omit_payload)`를 둔다 〔문서〕 `AGENTS.md:136-150`. `Path.cwd()`, `os.getcwd()`, `find_project_root()` 호출은 cwd 검사에 걸린다(`scripts/check_process_cwd.py:14-19`). 큰 값을 상태 채널에 넣지 않는다. `wrap_*`는 동기·비동기 둘 다 만든다 〔코드〕 |
| **Python 확장** (소스 수정 없음, 실험 기능) | `<프로필>/extensions/*.py`, `-e 경로`, `{프로젝트 루트}/.deepagents/extensions/`(`--trust-project-extensions`). `async def extension(d)` 안에서 `d.register_middleware(…)`, `d.register_tool(…)` 〔문서〕 `EXTENSIONS.md` | 빠른 시험 | `DEEPAGENTS_CODE_EXPERIMENTAL=1`이 없으면 통째로 무시된다(`agent.py:2866-2869`). 확장 미들웨어는 메인 목록 끝에만 붙고 `_subagent_cli_middleware`에는 안 들어간다(`:3851-3875`) 〔코드〕. 제출물의 게이트로는 쓰지 않는다 |
| **훅** (소스 수정 없음) | `<프로필>/hooks.json`, `{프로젝트 루트}/.deepagents/hooks.json`, 플러그인 | 빠른 시험, 입력 제출 때 컨텍스트 추가 | 아래 "훅의 종료 코드" 표. `-n`은 저장된 신뢰를 보지 않아 **매번 `--trust-project-hooks`** 가 필요하다(`hooks/trust.py:416-440`, `client/non_interactive.py:3136`) 〔코드〕 |
| **스킬** | `{프로젝트 루트}/.deepagents/skills/<이름>/SKILL.md` | 계획 작성 절차, 개선안 문안 | 목록은 스레드 상태에 없을 때만 로드한다(`plugins/adapters/skills_middleware.py:119`, `:619-632`). `allowed-tools`는 표시 코드만 찾았고(`skills/commands.py:136`) 강제 여부는 〔미확인〕. 대화형 `/skill:<이름>`, `-n`은 `-s 이름` 〔코드〕 |
| **서브에이전트** | `{프로젝트 루트}/.deepagents/agents/<이름>/AGENTS.md` (머리말 `description` 필수, `name`·`model` 선택. 폴더 없이 `<이름>.md`로 두면 무시) | 계획 리뷰어(독립 컨텍스트, 다른 모델) | 머리말에 도구 목록 칸이 없다(`subagents.py:54-74`, `:192-240`) 〔코드〕. 부모의 도구를 물려받는다 〔문서〕 `Day09/TOOLS_REFERENCE.md` 5장. fork 표시는 `general-purpose`에만 붙는다(`agent.py:3180-3182`) 〔코드〕. fork가 아닌 서브에이전트는 `task`의 `description`만 새 메시지로 받는다 〔저장소 실행 기록〕 |
| **별도 읽기 전용 실행** | `dcode -n "…" --allow-fs-tools read_file,ls,glob,grep` (셸 허용 목록 없이) | 도구가 제한된 독립 리뷰어 | 쓰기·편집·삭제·셸 도구가 메인과 동기 서브에이전트 모두에서 빠진다 〔코드〕 `main.py:3011-3021`, `agent.py:2726-2735`, `:3592-3624`. `fetch_url`, `task`, `js_eval`은 남는다. 실제 도구 목록은 8절 13번으로 확인 |
| **메모리** | `<프로필>/<에이전트>/AGENTS.md`, `{프로젝트 루트}/.deepagents/AGENTS.md`, `{프로젝트 루트}/AGENTS.md` | 항상 지킬 규칙 | 검색 없이 전문 주입. 새 `-n` 실행은 새 스레드라 다시 읽는다. `-r`로 이어 간 스레드에서 다시 읽는지는 〔미확인〕. `auto_save`가 켜져 있으면(기본) `-n`에서도 모델에게 `edit_file`로 저장하라고 시킨다 〔코드〕 `agent.py:3256-3281` |
| **목표·채점** | 대화형 `/goal`, `/rubric`. `-n`은 `--rubric "기준"` 또는 `--rubric @파일`(12,000자) | 완료 조건을 채점에 연결 | `-n`의 `--goal`은 종료 2. `--rubric`은 `-r`과 함께 못 쓴다. 채점 결과는 콘솔 문구로만 나온다 〔코드〕 `main.py:6134-6143`, `:6183-6191`, `goal_state_limits.py:29` |

**미들웨어를 넣는 자리** (`agent.py`. 목록 앞쪽이 바깥쪽이고 `before_*`는 앞에서 뒤로, `after_*`는 뒤에서 앞으로 돈다 〔저장소 실행 기록〕. SDK 핵심 스택인 파일 도구·`task`·요약·`PatchToolCalls`는 이 목록보다 더 바깥이다 〔문서〕 `Day09/ARCHITECTURE.md` 6.1)

| 넣을 것 | 위치 (사본 줄 / 원본 검색어) | 이유 |
|---|---|---|
| 기록 | `:3204` 목록 리터럴이 끝난 바로 뒤, `if not interactive:`(`:3205`) 앞. 검색어 `agent_middleware: list[` | 뒤에 붙는 모든 미들웨어보다 바깥이라 안쪽에서 거부된 결과까지 본다. `after_agent`는 역순이라 거의 마지막에 돈다 |
| 계획 게이트 | 기록 바로 뒤 | 기록이 차단을 본다. `wrap_tool_call`이므로 대화형 승인 창(`:2295-2343`)과 `PreToolUse` 훅(`hooks/server_middleware.py:422-447`)보다 늦게 돈다. 둘 다 `after_model` 단계다. 승인 창보다 먼저 거부하려면 `after_model`도 구현해야 한다 〔추정〕 |
| 시도 계수 | `:3681-3686` `CodeModelRetryMiddleware`·`ToolErrorMiddleware`를 `extend`하는 줄 뒤 | 재시도 미들웨어 안쪽이라 시도마다 불린다. 한 목록에 같은 이름의 미들웨어를 둘 수 없으니 클래스를 나눈다 〔문서〕 `Day09/ARCHITECTURE.md` 6.3 |
| 서브에이전트용 | `:3022` `middleware.append(CodeModelRetryMiddleware(max_retries=model_retries))` 뒤에 **새 인스턴스** | 파일 정의 서브에이전트와 fork를 끈 `general-purpose`는 이 목록만 쓴다. 기본값(fork)의 `general-purpose`에는 부모 목록이 이름 기준으로 합쳐진다 〔저장소 실행 기록〕 `Day09/TRACE_WALKTHROUGH.md` 6절. 같은 이름이 양쪽에 있을 때 어느 인스턴스가 남는지는 〔미확인〕(기존 `GitTrace`·`CodeModelRetry`도 양쪽에 있다) |

- **작업 폴더**는 `create_cli_agent`의 `effective_cwd`(`:2911-2915`)를 생성자로 넘긴다. `None`이면 기록은 설치하지 않고 게이트는 전부 거부한다.
- **요청 식별**은 `request.runtime.config["metadata"]`의 `thread_id`·`turn_id`로 한다. `GitTraceMiddleware`가 같은 방식이다(`git_trace.py:126-139`). `-n`은 실행마다 `turn_id`를 새로 만든다(`client/non_interactive.py:3123`, `config.py:2818-2819`). 런타임 컨텍스트에는 `thread_id`·`prompt_id`·`workspace`가 있다(`_cli_context.py:44-91`) 〔코드〕. 서브에이전트 안에서도 같은 값이 보이는지는 〔미확인〕.
- **거부**는 예외가 아니라 `status="error"`인 `ToolMessage`로 돌려준다. 본보기는 `ShellAllowListMiddleware`(`agent.py:897-1010`), `memory_guard.py:389-402`, 훅의 거부 메시지(`hooks/server_middleware.py:1285-1296`)다 〔코드〕.
- **한 인스턴스를 메인과 서브에이전트가 같이 쓰는 본보기**는 `git_trace.py:114-271`이다(스레드별 상태를 잠금으로 지킨다). 그 밖에는 인스턴스에 요청별 상태를 두지 않는다.
- fork 서브에이전트 그래프 안에서도 부모의 `before_agent`·`after_agent`가 돈다 〔저장소 실행 기록〕. 요청 시작·끝 이벤트는 최상위 그래프에서만 쓰게 가른다(하위 그래프는 체크포인트 네임스페이스가 `tools:<task_id>`다).
- `create_cli_agent`에 줄을 추가하는 것은 cwd 검사 허용 목록을 깨지 않는다. `Path.cwd()`가 든 기존 문장을 고치면 깨진다(`scripts/check_process_cwd.py:36-56`) 〔코드〕.
- 설치 여부는 단위 테스트로 증명한다. `create_deep_agent`를 가짜로 바꾸고 `kwargs["middleware"]`와 서브에이전트의 `middleware`를 보는 기존 테스트가 본보기다(`tests/unit_tests/test_agent.py:3413`, `:3458` 부근) 〔코드〕.

**훅의 종료 코드** (`hooks/capabilities.py:102-249`, `hooks/runner.py:107-196` 〔코드〕)

| 결과 | 뜻 |
|---|---|
| 종료 2 | 이벤트마다 다르다. `PreToolUse`·`PermissionRequest` 거부 / `UserPromptSubmit`·`PreCompact` 차단 / `PostToolUse`·`PostToolUseFailure` 피드백 / `Stop` 계속 진행(연속 8회까지, `hooks/reducer.py:59`) / `SubagentStop` 컨텍스트 추가 / `SessionStart`·`SessionEnd`·`Notification`·`SubagentStart` 진단만 |
| 2가 아닌 실패, 시간 초과 | **차단이 아니다. 진단만 남고 도구가 실행된다.** 게이트 스크립트는 예외 때도 2로 끝내야 한다 |
| 종료 0 + JSON | `PreToolUse`는 `hookSpecificOutput.permissionDecision`이 `allow`/`deny`/`ask`. 여러 핸들러면 `deny > ask > allow`(`hooks/reducer.py:58`) |
| 종료 0 + 일반 텍스트 | `SessionStart`·`UserPromptSubmit`에서만 추가 컨텍스트가 된다. `-n`에서는 사용자 메시지 앞의 `role: system` 메시지로 들어간다(`client/non_interactive.py:2372-2398`) |

- 매처는 공개 이름으로 쓴다: `execute→Bash`, `write_file→Write`, `edit_file→Edit`, `read_file→Read`, `glob→Glob`, `grep→Grep`, `ls→LS`. **`delete`, `task`는 원래 이름 그대로**다(`hooks/tools.py:69-77`). 이벤트는 12종(`hooks/models/domain.py:36-50`), 기본 시간 제한 600초(`UserPromptSubmit` 30초) 〔코드〕.
- `-n`에서 훅 왕복(인터럽트)은 **turn으로 세어진다.** 기본 한도 50, 넘으면 종료 124(`client/non_interactive.py:177`, `:2425-2445`) 〔코드〕. `PreToolUse` 핸들러가 하나라도 있으면 매처와 무관하게 도구 호출마다 서버가 클라이언트에 묻는다(`hooks/server_middleware.py:640-700`, `:876-908`) 〔코드. 왕복 횟수는 미확인〕.
- 서브에이전트 안의 도구 호출에도 `PreToolUse`·`PostToolUse`는 뜬다. `Stop`은 안 뜬다(`agent.py:3025-3039`) 〔코드〕.

**어느 경로로 구현하나 (권고).** 기준 1이 Python 코드 품질이고 평가자가 제출 소스를 빌드해 실행한다. 그래서 강제·기록은 소스 안 Python으로 만든다. 선택과 근거는 `design/decisions.md`에 적는다.

| 기능 | 권고 경로 | 이유 |
|---|---|---|
| 기록·지표 (4-1~4-3) | **소스 미들웨어** (메인 + 서브에이전트) | 채점 대상 코드와 단위 테스트가 생긴다. 직접 만든 스트림 이벤트는 `-n` 클라이언트가 버리므로(`client/non_interactive.py:1711-1756`) 파일에 직접 써야 한다. 훅으로 하면 turn을 소모한다 |
| 계획 게이트·범위 검사 (2-4) | **소스 미들웨어** (메인 + 서브에이전트) | 훅은 스크립트가 죽으면 통과되고, 평가자가 `--trust-project-hooks`를 빠뜨리면 게이트가 사라지고, 확장은 실험 플래그가 없으면 사라진다 |
| 계획 형식 검사 (2-1, 2-2) | **Python 모듈의 순수 함수** (게이트와 승인 명령이 호출) | 결정적 판정이고 모델 없이 단위 테스트로 증명된다 |
| 계획 작성 절차 | **스킬** (`-s` 또는 `/skill:`) | 절차 안내는 위임으로 충분하다. 강제는 게이트가 맡는다 |
| AI 리뷰 (2-3) | **파일 정의 서브에이전트** + 그 서브에이전트용 게이트는 쓰기·셸 전부 거부. 대안은 "별도 읽기 전용 실행" | 새 대화로 시작하고 다른 모델을 지정할 수 있다. 읽기 전용은 부탁이 아니라 코드로 건다. `_subagent_cli_middleware`에 서브에이전트 이름을 넘기도록 인자를 하나 더한다(부록 B) |
| 경험 저장·검색·주입 (3-1, 3-2) | **소스 미들웨어** (`before_agent`, `after_agent`) 〔추정〕. 빠른 시험은 `UserPromptSubmit` 훅 | 조회·저장 이벤트를 같은 기록에 남길 수 있다 |
| 개선안·전후 비교·조회·승인 명령 (3-3, 3-4, 4-4, 2-4) | **`scripts/` 아래 Python 스크립트** (+ 부르는 스킬) | 기록 파일만 읽으므로 모델 없이 재현된다. `scripts/**`는 `print`가 허용된다(`pyproject.toml:334-339`) 〔코드〕 |
| 항상 지킬 규칙 | 프로젝트 루트 `AGENTS.md` | 부탁 수준이다. 어기면 안 되는 것은 게이트로 옮긴다 |

## 4. 인수 기준별 구현 지도

### 1. 코드 품질 [10]
| 항목 | 할 일 | 구현 위치 | README 확인 방법 |
|---|---|---|---|
| 1-1 스타일 | 새 모듈과 테스트가 `ruff check`, `ruff format --check`, `ty check`를 통과. 줄 길이 88, 한글은 폭 2라 한 줄 약 40자가 한도다 〔추정〕 | 사본의 `pyproject.toml` 설정을 그대로 쓴다(느슨하게 바꾸지 않는다) | 2절의 다섯 명령과 기대 출력(`All checks passed!`, 변경 0건, 종료 0). 설치 명령부터 적는다 |
| 1-2 명명·import | 상대 import 금지, `from __future__ import annotations`, 타입 전용 import는 `if TYPE_CHECKING:` 안, 예외 메시지는 변수에 담아 던지기, `print` 대신 `logging.getLogger(__name__)` | 본보기 `memory_guard.py:24-48`, `git_trace.py:1-38` 〔코드〕 | 같은 명령 |
| 1-3 docstring | google 형식. 모듈 첫 줄, 클래스, `__init__`, 공개 함수에 역할·`Args:`·`Returns:`·`Raises:` | 본보기 `memory_guard.py`, `agent.py:897-1010` 〔코드〕 | 린트 통과 + 주요 함수 표 |

- 테스트 설정: 경고가 곧 실패, 시간 제한 30초, `asyncio_mode = "auto"`(`pyproject.toml:363-406`) 〔코드〕. 본보기는 `tests/unit_tests/test_memory_guard.py`(요청 객체를 만드는 법 `:36-46`).
- CLI 플래그를 추가하면 도움말 화면도, 슬래시 명령을 추가하면 명령 목록(`COMMANDS.md`)도 고쳐야 한다 〔문서〕 `AGENTS.md:166-184`. 새 플래그·명령 없이 미들웨어와 `scripts/`로 끝내는 쪽이 간단하다.

### 2. 계획·리뷰·승인 [10]
| 항목 | 할 일 | 구현 위치 | README 확인 방법 |
|---|---|---|---|
| 2-1 요구사항·범위·완료 조건 | 계획 양식의 필수 구역. 계획은 작업 폴더의 `design/plans/<plan_id>.md`. 완료 조건만 따로 파일로 빼 `--rubric @파일`로 채점과 잇는다 | 형식 검사 모듈 + 계획 스킬 | 요청 하나 → 세 구역이 채워진 계획 파일. 구역을 비운 계획이 거절된 출력 |
| 2-2 수정 대상·순서·테스트 방법 | 필수 구역 + 형식 검사. 수정 대상은 게이트가 읽는 경로 표 | 같은 모듈 | 구역이 빠진 계획이 걸린 기록, 단위 테스트 |
| 2-3 AI 리뷰와 반영 | `plan-reviewer` 서브에이전트가 `APPROVE`/`REVISE`와 지적을 JSON으로 낸다. `REVISE`면 `version`을 올리고 리뷰 이력에 남긴다. 리뷰어 `model`은 허용된 모델로 지정 | 서브에이전트 + `task` 결과를 기록하는 미들웨어 | 테스트 방법이 빠진 요청 → `REVISE` → 반영된 다음 버전. 리뷰어의 쓰기 시도가 막힌 기록 |
| 2-4 승인 후 변경·범위 재검토 | 게이트가 **`write_file`, `edit_file`, `delete`, `execute`** 를 본다(쓰기 능력이 있는 도구 목록 `agent.py:1014-1016`, 경로 인자는 `file_path`) 〔코드〕. 판정 순서는 보호 경로 → 작업 폴더 밖 → 계획·설계 문서 통과 → 승인 기록(`plan_id`·`version`·본문 해시 일치)과 수정 대상 범위. 하나라도 아니면 `status="error"`로 거부 | 게이트 미들웨어 (메인 + `_subagent_cli_middleware`), 부록 A2 | 승인 전 수정, 계획 파일에 승인 표시를 직접 쓴 뒤 수정, 범위 밖 수정, 승인 뒤 계획 수정이 각각 막힌 기록. 서브에이전트의 편집도 막힌 기록 |

- 양식, 상태 전이, 리뷰 기준, 규칙 ID, 시험 목록은 `../reference/plan-gate.md`를 그대로 따른다. **승인 기록은 계획 파일과 따로 `design/approvals/<plan_id>.json`에 두고, 계획 본문의 해시를 담고, 사람이 터미널에서 돌리는 승인 명령만 쓴다.** 게이트 판정 중의 예외·읽기 실패는 전부 차단(`gate.failure`)이다.
- `-n`에는 사람 승인 화면이 없다. 흐름은 "계획 실행(`-n`) → 사람이 승인 명령 → 실행(`-r <thread_id> -n` 또는 새 실행)"이다. `-r`은 같은 작업 폴더에서만 되고 `--rubric`과 함께 못 쓴다 〔코드〕 `main.py:6175-6191`, `client/non_interactive.py:2636-2667`, 〔저장소 실행 기록: 이어 가기 관측〕 `Day09/STATE_AND_STORAGE.md`.
- 셸로 파일을 고치는 길은 게이트가 대상 경로를 알 수 없다. 승인 전에는 `execute`를 막고, 승인 뒤에는 `-S` 허용 목록(리다이렉트 거부)으로 좁히고, 끝난 뒤 `git diff --name-only <base_commit>`이 수정 대상 안인지 스크립트로 확인한다. 허용한 명령(`pytest`, `uv`, `git`)도 임의 코드를 돌릴 수 있다. 남는 우회 경로는 표로 적는다.
- `js_eval`은 기본으로 켜져 있다 〔저장소 실행 기록〕. 인터프리터 안에서 부를 수 있는 호스트 도구의 기본값은 `read_file`·`glob`·`grep`뿐이다(`config.py:3108`, `config_manifest.py:74-79`) 〔코드〕. 그 호출이 `wrap_tool_call`을 거치는지는 〔미확인〕이다. `--interpreter-tools`를 넓히지 않고, 시연은 `--no-interpreter --no-mcp`로 한다(쓰기 능력이 있는 MCP 도구는 `-n`에서 내장 가드가 거부한다, `agent.py:3208-3215` 〔코드〕).

### 3. 메모리·자기개선 [10]
| 항목 | 할 일 | 구현 위치 | README 확인 방법 |
|---|---|---|---|
| 3-1 저장·유지 | 규칙은 프로젝트 루트 `AGENTS.md`, 경험은 별도 파일(제안값: `.deepagents/memory/experiences.jsonl`). 작업이 끝나거나 실패할 때 코드가 기록한다 | 미들웨어 `after_agent` 〔추정〕 | 실행 A의 저장 이벤트(항목 ID) → 새 `-n` 실행에서 같은 ID가 읽힘 |
| 3-2 검색·활용 | 요청으로 경험을 검색해 몇 건만 **메시지로** 주입한다(시스템 프롬프트를 바꾸면 캐시에 영향 〔미확인〕). 주입한 ID를 계획의 "참조 메모리·근거"와 기록에 남긴다 | 미들웨어 `before_agent` 〔추정〕 | 비슷한 작업 → 계획에 참조한 경험, 기록에 메모리 조회 이벤트. 주입을 끈 실행과의 차이 |
| 3-3 개선안 생성 | 도구 오류, `execute`의 0 아닌 종료 코드, 채점 미충족, 게이트 차단을 모아 개선안 파일(근거 이벤트, 가설, 변경 diff, 기대 효과)을 만든다. 바로 적용하지 않는다 | `scripts/` 스크립트 + 스킬 | 일부러 실패시킨 작업 → 개선안 파일. 금지 경로를 건드린 후보가 거부된 출력 |
| 3-4 전후 검증·반영 | 고정 작업을 현재 버전과 후보로 각각 돌려 비교하고 회귀가 없을 때만 반영 | 평가 스크립트(프로필을 `DEEPAGENTS_HOME`으로 분리) | 전후 비교표, 탈락안 미반영, 채택안이 새 실행에 쓰인 기록 |

- `-a 이름`은 사용자 쪽(`<프로필>/이름/`의 메모리·스킬·서브에이전트)만 분리한다. **프로젝트 쪽 파일은 공유된다.** 통째로 나누려면 `DEEPAGENTS_HOME=<절대경로>`를 쓴다(`_paths.py:78`, `:295-378`) 〔코드〕. 이 값은 `.env`로는 못 바꾼다 〔문서〕 `Day09/scripts/dcode:13-17`.
- `auto_save`는 끈다(`config.toml`의 `[memory] auto_save = false`, 환경 변수 `DEEPAGENTS_CODE_MEMORY_AUTO_SAVE`) 〔코드〕 `config_manifest.py:2729-2740`. 끄면 읽기 전용 안내문으로 바뀔 뿐 편집 도구는 그대로다(`agent.py:184-210`, `:3267-3281`). 직접 편집은 게이트의 보호 경로로 막는다. `memory_guard.py`는 온보딩 이름 구역만 보호한다.
- 절차와 기록 형식은 `../reference/memory-improve.md`를 따른다.

### 4. 모니터링 [10]
| 항목 | 할 일 | 구현 위치 | README 확인 방법 |
|---|---|---|---|
| 4-1 전체 흐름 기록 | 요청별 기록 파일(대화 = `thread_id`, 요청 = `turn_id`. 승인 전후로 실행이 나뉘면 `thread_id`와 `plan_id`로 잇는다). 단계 표시는 호출 시점의 계획 상태로 붙인다: 승인 전 → 계획, 리뷰어 `task` → 리뷰, 승인 뒤 쓰기·편집·삭제 → 코드 변경, `execute`의 테스트 명령 → 테스트, 종료 → 결과 | 기록 미들웨어 (부록 A, B) | 요청 하나 뒤 기록에 다섯 단계가 시간순으로 있음. 실행 중 강제 종료해도 그때까지의 줄이 남음 |
| 4-2 호출·도구·메모리·개선 기록 | 모델 호출(`wrap_model_call`), 도구 실행, 메모리 조회·저장, 개선안 이벤트, 게이트 차단. **`execute`는 실패해도 `status="success"`다.** `artifact["exit_code"]`로 판정한다. dcode 자신도 그렇게 본다(`hooks/server_middleware.py:1460-1482`, 테스트 `tests/unit_tests/hooks/test_server_lifecycle.py:906-915`) 〔코드〕 | 같은 미들웨어 | 일부러 실패시킨 명령 → 오류 종류와 함께 기록됨 |
| 4-3 지표 | 요청이 끝날 때 총 시간, 모델·도구 호출 수, 종류별 재시도 수, 토큰. 모델 재시도 신호(`model_retry`·`model_attempt`)는 스트림으로만 나가 다른 미들웨어가 받을 수 없다(`model_retry.py:996-1062`, `:1195-1212`) 〔코드〕. 재시도 미들웨어 **안쪽**에서 "시도 수 − 호출 수"로 센다 〔추정〕. 못 세면 빈값 | 기록 미들웨어 + 안쪽 계수 미들웨어 | 요약 출력. 끝에 찍히는 `Usage Stats` 표(`_session_stats.py:1491`)와 대조 |
| 4-4 조회 | 요청을 지정하면 첫 오류, 복구 안 된 첫 오류, 게이트 차단을 직전 맥락과 함께 보여 준다. 내장 스킬 `deepagents-thread-inspector`의 `scripts/inspect_sessions.py`는 보조로 쓴다 | `scripts/` 스크립트 | 실패한 요청 → 어느 단계, 어느 호출, 오류 종류 |

- 이벤트 형식과 "첫 실패" 정의는 `../reference/trace.md`를 따른다. 기록 폴더(제안값: 작업 폴더의 `.deepagents/runs/`)는 게이트의 보호 경로에 넣고 시연 저장소의 `.gitignore`에도 넣는다.
- LangSmith는 키와 추적 플래그가 둘 다 있어야 켜진다(`config.py:4606` 부근) 〔코드〕. 키 없이 동작하는 로컬 기록을 주 증거로 삼고 시연에는 `--no-tracing`을 붙인다.
- 서버는 블로킹 호출을 잡는 런타임 위에서 돈다(`pyproject.toml:95-98`, `:192-194`의 주석) 〔코드〕. `async def` 훅 안의 파일 입출력은 `asyncio.to_thread`로 넘긴다(본보기 `memory_guard.py:450` 이하, `git_trace.py:222-225`).
- 안쪽에서 인터럽트(승인, 훅)가 걸리면 `GraphBubbleUp`이 올라온다. 오류로 세지 않게 먼저 다시 던진다(`model_retry.py:667`, `:717`) 〔코드. 재개 때 감싸기가 몇 번 다시 불리는지는 미확인〕.
- `sessions.db`를 직접 읽을 때 마지막 체크포인트에는 메시지가 없다(쓰기 기록을 되풀이해 복원한다) 〔저장소 실행 기록〕 `Day09/TRACE_WALKTHROUGH.md` 7절.

### 기준 저장소에서 가져다 쓸 수 있는 구현
직접 열어 읽은 파일만 적었다. 전부 실습용 업무 에이전트(상담·주문)에 맞춰져 있어 그대로는 못 쓴다. 공통으로 고칠 것: 동기 훅만 있다(`awrap_*` 추가), 거부 메시지에 `status="error"`가 없다, 상대 import, 타입·docstring 부족(기준 1), 메모리 안 객체에 기록한다(파일로).

| 기준 | 기준 저장소 경로 | 하는 일 | dcode에 맞추려면 |
|---|---|---|---|
| 2-4 게이트 | `Day08_new/guard_lab/gate.py` (`Gate.decide`, `GateMiddleware`) | 도구 호출마다 최종 결정 하나를 내고 기록한다. 컨텍스트가 없으면 차단. 부모 미들웨어에만 두면 서브에이전트 호출을 놓친다는 것을 보여 준다 | 판정 내용을 업무 규칙에서 "승인 기록·범위·보호 경로"로 바꾼다 |
| 2-4 승인 기록 | `Day08/guardlab/components.py` (`ApprovalStore`, `args_hash`) | 승인을 도구·인자 해시·요청자·만료에 묶고 불일치·재사용·만료를 사유 코드로 가른다 | 메모리 안 사전 → `design/approvals/<plan_id>.json`, 인자 해시 → 계획 본문 해시, 쓰는 주체 → 사람이 돌리는 명령 |
| 2-4 사람 승인(멈춤) | `Day08_new/guard_lab/hitl.py` (`ReviewInterruptMiddleware`, `run_with_human`), `Day08_new/06_hitl_interrupt.py` | 검토 결정에서 `interrupt()`로 멈추고 사람의 답으로 재개한다. 승인은 기록이 되어 같은 게이트를 다시 지난다 | 대화형에서만 쓸 수 있다. `-n`은 답할 사람이 없고 왕복이 turn을 쓴다. 대기 목록을 인스턴스에 두는 부분은 서버 재시작·fork에서 깨진다 |
| 2-3 판정 실패 처리 | `Day08_new/guard_lab/gate.py` (`judge_text`) | 판정 실패를 통과가 아니라 검토로 돌린다 | 리뷰어 출력의 JSON 해석 실패를 `REVISE`로 처리하는 규칙에 쓴다 |
| 2-4 사후 확인 | `Day05_new/eval_lab/trajectory_rules.py` (`check_write_before_approval`) | 기록에서 "허용 전에 쓰기"를 이름 있는 규칙으로 찾는다 | 자체 기록 형식에 맞춰 "승인 이벤트 전에 쓰기 도구가 성공한 줄이 있는가"로 다시 쓴다 |
| 3-1 메모리 쓰기 검사 | `Day08_new/guard_lab/memory.py` (`MemoryWriteMiddleware`, `MemoryStore.quarantine`) | 메모 파일을 고치는 `edit_file`·`write_file`만 골라 저장·격리·차단하고 서브에이전트에도 따로 붙인다 | 대상을 `AGENTS.md` 세 위치와 경험 저장소로. 출처 판정은 빼고 "에이전트의 직접 편집은 차단, 코드가 쓰는 길만 허용"으로 줄인다 |
| 3-1 파일 권한 | 같은 파일 `MemorySetup.permissions` | SDK 내장 `FilesystemPermission`으로 경로 쓰기를 거부한다 | dcode는 SDK에 `permissions`를 넘기지 않는다(`agent.py:3601-3607`의 주석). 넘기려면 `--allow-fs-tools` 교체본과 서브에이전트 주입까지 고쳐야 한다. 0.7.34에서의 동작은 〔미확인〕 |
| 3-3·3-4 개선 루프 | `Day05_new/eval_lab/rsi.py` (`failure_summaries`, `build_improver_prompt`, `propose_candidates`, `contamination_check`, `holdout_decision`) | 실패 요약 → 개선기 프롬프트 → 후보 → 형식 거부 → 미리 고정한 규칙으로 채택·보류·판정 불가. 개선기 입력에 정답 흔적이 섞였는지 검사한다 | 후보의 형태가 정책 JSON이다. 대상을 프롬프트 구역·스킬·메모리 규칙의 diff로, 실패 입력을 dcode 기록으로, 확인 실행을 `dcode -n` 반복으로 바꾼다 |
| 3-3 금지 경로 거부 | `Day05_new/eval_lab/policy.py` (`validate_spec`, `PolicyRejected`) | 허용한 모양 밖의 키를 형식 단계에서 거부한다 | "개선안이 건드릴 수 있는 경로 허용 목록" 검사로 옮긴다 |
| 3-4 전후 비교 | `Day05/business_lab/lesson_runs.py` (`assert_same_protocol`, `compare_scored`), `Day05/07_compare_candidate.py` | 조건·채점기가 같은지 확인한 뒤 과제별로 개선·회귀·유지·계속 실패·비교 불가로 가른다 | 실행 함수를 `dcode -n` 호출로, 채점을 기록·상태 검사로. 실행 조건에 dcode 버전·모델·플래그를 넣는다 |
| 4-1·4-2 기록 | `Day08_new/guard_lab/trace.py` (`RunLog`, `TraceMiddleware`) | 제안과 실제 실행을 구분하고 결정과 실행을 호출 ID로 이어, 차단됐는데 실행된 수와 검사 없이 실행된 경로를 센다 | 줄 단위 파일 추가로. contextvar가 서버의 비동기 경계에서 유지되는지 〔미확인〕. 필드는 `../reference/trace.md`에 맞춘다 |
| 4-3 호출 예산 | `Day08/guardlab/budget.py` | langchain 내장 호출 수 상한 미들웨어 두 개로 실행당 상한을 건다 | dcode 목록에 넣을 수 있는지 〔미확인〕. `--max-turns`·`--timeout`·`--recursion-limit`이 이미 있다 |
| 4-4 조회 신호 | `Day06_new/use_cc/tools/diagnose_sessions.py` | 세션 기록에서 같은 명령 반복, 실패 뒤 같은 재시도, 수정 뒤 검사 없음을 센다 | 입력이 다른 도구의 세션 형식이다. 신호 정의만 가져온다 |
| 끝내기 전 검사 | `Day06_new/use_cc/tools/check_evidence.py`, `Day06_new/use_cc/part3/stop_gate.py` | 완료 주장을 믿지 않고 검사를 다시 돌려 대조한다. 검사기의 종료 코드를 훅의 차단 코드로 바꿔 준다 | dcode의 `Stop` 훅도 종료 2가 "계속"이다. 범위 검사(`git diff --name-only`)를 여기에 둔다 |

## 5. 진행 순서 (dcode 기준)

| 단계 | 먼저 확인할 것 | 끝났다는 기준 |
|---|---|---|
| S0 | 2절의 결정. 설치·점검 스크립트가 통과하는가(8절 1~2번). 주석 줄을 지운 복사본이 린트를 통과하는가(3~5번). 고른 모델로 한 번 응답하는가(15번) | 설치·실행·검사 명령이 README 초안에 있다 |
| S1 (S2와 병렬) | 고정 작업 5건을 `dcode -n`과 `--rubric`으로 돌린다. **종료 코드는 채점 결과를 담지 않는다.** 통과 여부는 `Acceptance criteria satisfied` 문구(`client/non_interactive.py:1142-1146`)나 자체 기록 파일로 판정한다 | 평가가 명령 한 줄로 다시 돈다 |
| S2 | 기록 미들웨어를 메인 목록과 서브에이전트 묶음에 넣는다. 새 모듈이 다섯 검사를 통과하는가 | 요청 하나의 기록과 요약 지표가 나온다 |
| S5 (S3과 병렬) | 계획 양식 → 형식 검사 → 리뷰어 서브에이전트 → 승인 명령 → 게이트. 게이트를 `_subagent_cli_middleware()`에도 넣었는가. `delete`와 `execute`도 보는가 | `../reference/plan-gate.md` 9절의 시험이 메인과 서브에이전트 양쪽에서 기대대로 나온다 |
| S3 | 규칙과 경험 저장소. `auto_save` 끄기. 보호 경로 | 새 실행에서 저장소가 남아 있다 |
| S6 | 검색·주입 → 개선안 → 전후 비교(`DEEPAGENTS_HOME`으로 프로필 분리) | 개선 한 바퀴가 기록에 있다 |
| S8 | README에 항목별 확인 방법. 깨끗한 환경(새 가상환경, 새 프로필)에서 그대로 돌린다 | `criteria-check` 표의 모든 항목이 "실행해서 확인"이다 |

## 6. 함정

1. 서버 코드에서 `Path.cwd()`, `os.getcwd()`, `find_project_root()`를 쓰면 cwd 검사가 실패한다. 서버 하나가 여러 작업 폴더를 맡기 때문이다 〔코드〕.
2. 이 사본에서 `uv sync`, `uv run`, `make`는 쓰지 않는다. `Day09/` 안에서 `uv sync`를 돌리지 말라고 기준 저장소도 적는다 〔문서〕. 소스를 고친 뒤에는 dcode를 다시 실행해야 반영된다(서버가 `--no-reload`로 뜬다 〔저장소 실행 기록〕).
3. 복사본에 `# [해설]` 줄이 남아 있으면 그 파일은 린트(E501)에 걸릴 것으로 본다 〔추정〕. `agent.py`처럼 고치는 파일은 반드시 지운다. 기준 저장소의 `check_comments_only.py`는 "주석만 바뀌었는가"를 보는 검사라 소스를 고치면 실패하는 것이 정상이다.
4. 메모리와 스킬 목록은 스레드에 없을 때만 로드된다. "다음 작업에 반영"은 새 실행으로 보인다 〔코드: 스킬 / 미확인: 메모리〕.
5. `-n`에서는 모델(`-M`), 셸(`-S`), 프로젝트 훅(`--trust-project-hooks`), `< /dev/null`이 **매번** 필요하다. 훅을 쓰면 `--max-turns`도 넉넉히 준다. README 확인 명령에 빠뜨리지 않는다 〔코드〕.
6. `-n`은 파일 쓰기·편집·삭제를 승인 없이 실행한다. 게이트가 없으면 "승인 후 변경"은 지켜지지 않는다 〔저장소 실행 기록〕.
7. 평가 스크립트가 종료 코드만 보면 "기준 미충족"도 통과로 센다. 124(한도 초과)와 1(오류)만 종료 코드로 구분된다 〔코드〕.
8. 훅 게이트는 스크립트가 예외로 죽으면(종료 1) 열린다. 미들웨어 게이트도 판정 중 예외가 나면 거부로 처리하게 짠다 〔코드 / 설계 권고〕.
9. 게이트가 `write_file`·`edit_file`만 보면 `delete`, `execute`, 서브에이전트로 뚫린다. 서브에이전트는 두 종류다. 파일 정의 서브에이전트는 `_subagent_cli_middleware` 목록만 쓰고, 기본 `general-purpose`는 부모 목록이 합쳐진다. 둘 다 시험한다 〔코드〕〔저장소 실행 기록〕.
10. 기록 미들웨어의 `before_agent`·`after_agent`가 fork 서브에이전트 안에서도 돈다. 가르지 않으면 요청 끝 이벤트가 두 번 남는다 〔저장소 실행 기록에서 낸 추정〕.
11. dcode는 **`.git`이 있는 상위 폴더**의 `AGENTS.md`, `.deepagents/`, `.agents/skills`, `.claude/skills`를 읽고 홈의 `~/.agents/skills`, `~/.claude/skills`도 읽는다(`agent.py:2550-2615`). 소스 폴더나 기준 저장소 안에서 시연하면 그쪽 설정이 섞인다. 시연은 `git init`한 별도 폴더에서 하고 `DEEPAGENTS_HOME`으로 프로필도 나눈다 〔코드〕.
12. 로컬 셸에는 경계가 없다. `-S all`로 시연하지 않는다. 테스트 명령에 `2>&1`이나 `> 파일`을 쓰면 허용 목록이 거부한다 〔코드〕.
13. 리뷰어(`model`)와 채점 모델(`--rubric-model`, 기본은 메인 모델)을 허용된 모델로 지정하고 `[models] allowed`로 강제한다 〔코드〕.
14. `auto_save` 기본값에서는 `-n`의 모델이 검증한 사실을 `AGENTS.md`에 `edit_file`로 저장하라는 안내를 받는다. 규칙 저장소가 사람 승인 없이 바뀔 수 있다 〔코드〕.
15. `-r <ID> -n`은 그 스레드를 만든 작업 폴더에서만 된다. 다른 폴더면 종료 1이다 〔코드〕 `client/non_interactive.py:2636-2667`, `:3028-3032`.

## 7. 문서와 코드가 다른 곳

| 문서 | 실제 | 확신도 |
|---|---|---|
| 과제 안내문(`Day08/project_guide.md`)은 소스 참고 위치를 `Day08/dcode-analysis`(0.1.69)로 적는다 | `Day09/README.md`는 그 분석이 이전 버전이고 다르면 `Day09/`의 코드가 맞다고 적는다. 실행 스크립트도 `Day09/` 사본을 설치한다 | 〔문서〕 |
| 사본의 `AGENTS.md:3`은 화면 없는 실행을 `-x`라고 적는다 | 플래그는 `-n`/`--non-interactive`다 | 〔코드〕 `main.py:2783-2790` |
| `create_cli_agent`의 서명과 docstring은 `enable_interpreter`의 기본값을 `False`로 둔다(`agent.py:2642`) | CLI 설정 기본값은 켜짐이라 `-n`·대화형 기본 그래프에 인터프리터가 들어간다 | 〔코드〕 `config_manifest.py:74` 〔저장소 실행 기록〕 |
| `Day09/ARCHITECTURE.md` 6.4의 "서브에이전트 스택은 메인과 따로" | fork를 끈 경우에만 맞다. 기본 `general-purpose`는 부모 스택을 따른다 | 〔저장소 실행 기록〕 `Day09/CLAIM_CHECKS.md` |
| 가짜 모델 docstring은 위임 표지를 주면 서브에이전트가 파일을 쓴다고 적는다(`_testing_models.py:267`) | 기본값(fork)의 `-n`에서는 쓰지 않았다. `DEEPAGENTS_CODE_FORKED_SUBAGENTS=0`에서만 썼다 | 〔저장소 실행 기록〕 `Day09/TRACE_WALKTHROUGH.md` 6절 |
| 설정 표시에 나오는 `--set-default-model` | 실제 플래그는 `--default-model`이다 | 〔문서〕 `Day09/CONFIG_REFERENCE.md`, 〔코드〕 `main.py:2739-2749` |
| 사본의 `DEVELOPMENT.md`와 `Makefile`은 `uv sync`·`make`를 쓴다 | 모노레포 전체가 있을 때의 방법이다. 이 사본에는 맞지 않는다. 같은 문서의 "Local dev installs"(`uv venv` + `uv pip install -e`)가 저장소 스크립트와 같은 방식이다 | 〔문서〕 `DEVELOPMENT.md:207-240` |

### 0.1.69 문서에서 달라진 점
- 기준 사본이 `Day08/dcode-analysis`(0.1.69, SDK 0.7.14, Python 3.12 이상)에서 `Day09/`(0.2.5, SDK 0.7.34 PyPI, Python 3.14 전용)로 바뀌었다. 줄 번호 인용을 전부 다시 맞췄다.
- 출발 소스 권고가 "원본 커밋을 받아 모노레포 구조를 유지"에서 "`Day09/` 사본을 복사해 해설 줄을 지운다"로 바뀌었다. 빌드가 `uv sync`·`make`에서 저장소 스크립트(`uv pip install --no-sources`)로 바뀌었고 검사 도구를 따로 깔아야 한다.
- 키 우선순위를 고쳤다. 저장한 키가 환경 변수보다 앞이다(이전 문서는 접두 변수가 가장 앞이라고 적었다).
- 모델을 반드시 지정해야 한다(`-M` 또는 `[models].default`). `[models] allowed`의 와일드카드는 `provider:*`로 확인됐다.
- `-n`에 `-r <ID>` 이어 가기가 생겼다. `-n` 전용 메모리 안내문이 생겨 기본값에서 모델이 메모리 파일을 고치도록 유도된다.
- 미들웨어 목록 맨 앞에 `GitTraceMiddleware`·`EmptyTruncatedReplyMiddleware`가 생겼다. 요청 식별에 `config["metadata"]`의 `thread_id`·`turn_id`를 쓰는 본보기가 생겼다.
- "게이트를 사람 승인 앞에 두면 승인 창 전에 거부한다"는 이전 설명을 뺐다. 승인 창은 `after_model` 단계라 `wrap_tool_call` 게이트보다 먼저 뜬다.
- fork 서브에이전트가 부모 미들웨어를 따른다는 것, `-n` 기본 그래프에 승인 미들웨어가 없다는 것, 인터프리터가 기본으로 켜진다는 것이 기준 저장소의 실행 기록으로 뒷받침됐다.
- 끼어들 자리에 Python 확장(실험 기능)과 `--allow-fs-tools` 읽기 전용 실행을 더했다. 이전 문서가 빠뜨린 것이고 0.1.69에도 있던 기능이다.
- 셸 허용 목록이 `-S` 말고도 환경 변수·`config.toml`에서 켜진다는 것, `-n`의 stdin 처리(`< /dev/null`), `SubagentStop`의 종료 2가 컨텍스트 추가라는 것, 매처 이름 `Glob`·`Grep`·`LS`를 더했다.

## 8. 실행해서 확인할 것

**아래는 아무것도 돌려 보지 않았다.** "기대"는 코드와 기준 저장소 문서를 읽고 쓴 것이라 문구와 수치가 다를 수 있다. 다르면 이 문서를 고친다. 1~2번은 기준 저장소 루트에서, 3~12번은 제출용 복사본의 `libs/code`에서(`V`는 가상환경의 `bin`), 13번부터는 `git init`한 시연 폴더에서 `DEEPAGENTS_HOME`을 새 폴더로 두고 돌린다. `<dcode>`는 실행 스크립트의 절대 경로다. 13·14번은 부록 E의 가짜 모델 설정을 쓰므로 비용이 없다.

| # | 명령 | 기대 | 확인하는 것 |
|---|---|---|---|
| 1 | `bash Day09/scripts/setup_dcode.sh` | 끝에 `deepagents-code 0.2.5`와 `Editable install: …/Day09/deepagents/libs/code` | 설치 |
| 2 | `bash Day09/scripts/smoke_dcode.sh; echo "exit=$?"` | `통과:` 줄, `exit=0` | 서버 기동부터 응답까지 |
| 3 | 부록 B의 설치 명령(`-e ".[openrouter]" --group test`) 뒤 `$V/ruff --version; $V/ty --version; $V/python -c "import langchain_openrouter"` | 셋 다 오류 없이 끝남. `dcode --version`의 설치 경로가 그대로 | 검사 도구·OpenRouter 설치 조합 |
| 4 | (해설 줄을 지우기 전) `$V/ruff check deepagents_code --select E501 --statistics` | `E501` 1,200~1,900건, 종료 1 | 해설 줄의 린트 예상 |
| 5 | 해설 줄을 지운 뒤(부록 B) `$V/ruff check . ; $V/ruff format --check . ; echo "exit=$?"` | `All checks passed!`, 변경 0건, `exit=0` | 지운 복사본이 깨끗한 출발점인가 |
| 6 | `$V/ty check --python <가상환경> deepagents_code/memory_guard.py` | 통과. 없는 `extra-paths` 때문에 오류가 나면 그 문구를 적는다 | 이 구조에서 ty가 도는가 |
| 7 | `$V/python scripts/check_process_cwd.py deepagents_code; echo $?` 와 `$V/python scripts/generate_commands_catalog.py --check; echo $?` | 출력 없이 0, 0 | 두 보조 검사 |
| 8 | `$V/python -m pytest -p no:cacheprovider --disable-socket --allow-unix-socket tests/unit_tests/test_memory_guard.py -q` | `17 passed`. 경고로 실패하면 `-W ignore::DeprecationWarning`을 붙이고 그 사실을 README에 적는다 | 테스트 환경 |
| 9 | 부록 A·A2·C를 완성해 넣고 네 파일에 `ruff check`, `ruff format --check`, `ty check` | 셋 다 통과. 실패하면 규칙 코드를 보고 고친다 | 초안의 린트 적합성 |
| 10 | `$V/python -m pytest … tests/unit_tests/test_run_log.py tests/unit_tests/test_plan_gate.py -q` | `5 passed` | 초안 동작 |
| 11 | 부록 B 반영 뒤 7번과 `… pytest … tests/unit_tests/test_agent.py -q` | cwd 검사에 `unreviewed`·`stale` 없음. 기존 테스트 통과 | 삽입이 허용 목록과 기존 테스트를 안 깨는가 |
| 12 | (확인 뒤 되돌린다) `run_log.py`에 `Path.cwd()` 한 줄을 넣고 7번의 cwd 검사 | `unreviewed` 안내, 종료 1 | 함정 1 |
| 13 | `<dcode> -n "DCA_TEST_WRITE_FILE=$PWD/x.txt" -M itool:fake --allow-fs-tools read_file,ls,glob,grep --no-tracing --no-mcp < /dev/null; ls x.txt` | 파일이 생기지 않는다. `<dcode> tools list < /dev/null`은 기본 구성에서 `15 tools available` 〔저장소 실행 기록〕 | 읽기 전용 실행에서 쓰기 도구가 빠지는가 |
| 14 | 게이트를 넣은 뒤 `<dcode> -n "DCA_TEST_WRITE_FILE=$PWD/a.py" -M itool:fake --no-tracing --no-mcp < /dev/null`, 다음에 `DEEPAGENTS_CODE_FORKED_SUBAGENTS=0`을 붙이고 표지를 `DCA_TEST_DELEGATE_WRITE=$PWD/b.py`로 | 두 경우 모두 파일이 안 생기고 기록에 `gate_block`(`plan.approved_required`)이 남는다. 게이트가 없는 원본에서는 두 파일이 생긴다 〔저장소 실행 기록〕. fork 기본값에서는 가짜 모델이 쓰기를 시도하지 않으므로 그 경로는 17번처럼 실제 모델로 본다 | 게이트가 메인과 fork를 끈 서브에이전트에 걸리는가 |
| 15 | `<dcode> -n "hello.txt 파일을 만들어줘" -M openrouter:<모델 ID> --max-turns 20 --timeout 300 --no-mcp < /dev/null; echo "exit=$?"` (게이트를 넣기 전, 또는 승인된 계획이 있을 때) | `Task completed`, `Usage Stats` 표, `exit=0`, 기록에 `write_file` 줄과 요청 끝 요약 | 모델 연결, 기록 미들웨어 |
| 16 | 15번에 `--rubric "world.txt 파일이 있어야 한다" --rubric-max-iterations 1` | 미충족 문구가 나오고 **`exit=0`** | 채점 결과가 종료 코드에 없는가 |
| 17 | `.deepagents/agents/reviewer/AGENTS.md`를 만들고 실제 모델로 "reviewer에게 a.py를 만들게 해줘", 다음에 "general-purpose에게 b.py를 만들게 해줘" | 두 서브에이전트의 `write_file`이 기록에 남고 게이트가 막는다. 기록의 `thread_id`·`turn_id`가 메인과 같다 | 파일 정의 서브에이전트와 fork 경로, 서브에이전트 안의 요청 식별 |
| 18 | 부록 D를 넣고 플래그 없이, 다음에 `--trust-project-hooks`를 붙여서, 다음에 `--max-turns 3`으로 | 없으면 훅이 안 돈다. 있으면 `Write blocked by hook: …`가 도구 오류로 보인다. 한도를 줄이면 `exit=124` | 훅 신뢰, 거부 문구, 훅 왕복이 turn으로 세어지는가 |
| 19 | 계획 실행 뒤 승인 명령을 돌리고 `<dcode> -r <thread_id> -n "승인된 계획대로 진행해줘" … < /dev/null` | 같은 스레드로 이어지고 수정 대상 안의 편집만 통과한다. 프로젝트 `AGENTS.md`를 그 사이에 고쳤다면 반영됐는지 적는다 | 승인 전후 흐름, 이어 간 스레드의 메모리 재로드 |
| 20 | `DEEPAGENTS_CODE_DEBUG=1`로 15번을 돌리고 stderr의 `Server log preserved at:` 경로를 연다 | `BlockingError` 없음. `asyncio.to_thread`를 빼면 나오는가 | 블로킹 입출력 제약 |
| 21 | 15번을 긴 요청으로 돌리다 `kill -9`로 끊는다 | 기록 파일에 그때까지의 줄이 있고 요청 끝 이벤트는 없다 | 4-1의 "강제 종료해도 남는다" |

**그 밖에 확인하지 못한 것:** `AgentMiddleware` 기반 클래스의 원본 서명(langchain 소스가 사본에 없어 하위 클래스에서 역으로 읽었다)과 `wrap_*`를 동기만 정의했을 때의 동작 · SDK 0.7.34의 fork 병합에서 같은 이름의 미들웨어가 어느 쪽 인스턴스로 남는지 · SDK `MemoryMiddleware`가 이어 간 스레드에서 파일을 다시 읽는지 · ruff 세부 판정(DOC 규칙이 요구하는 구역, 한글 주석의 `RUF001~003`) · `before_agent`·`after_agent`에서 메시지를 주입하는 방식 · `js_eval`의 호스트 도구 호출이 `wrap_tool_call`을 거치는지 · 훅 이벤트의 `agent_id`·`agent_type`이 실제로 채워지는지 · `auto_save` 환경 변수의 값 형식 · 과제의 모델 제한과 각 모델 ID가 dcode에서 동작하는지 · 평가자가 Python 3.14와 `uv`를 쓸 수 있는 환경인지.

## 부록

미들웨어 뼈대(기록, 게이트), 넣는 자리와 설치 명령, 단위 테스트, `hooks.json` 예, 가짜 모델 설정의 초안(부록 A~E)은 [`dcode-drafts.md`](dcode-drafts.md)에 있다. 전부 실행·린트·타입 검사를 하지 않은 초안이다. 8절 9~11번으로 확인한다.
