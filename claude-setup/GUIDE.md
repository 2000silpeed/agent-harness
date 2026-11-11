# 내 Claude Code 세팅 가이드

> 내 Claude Code를 어떻게 세팅해서 쓰면 좋은지를 순서대로 정리했다. 단계마다 왜 하는지, 무엇을 정해야 하는지, 무엇을 하는지, 어떻게 확인하는지, 언제 끝났다고 보는지를 적었다.
> 사실 관계는 공식 문서(맨 아래 참고 자료)와 대조했고 기준 버전은 Claude Code 2.1.322다. 버전 조건이 있는 기능은 "(v2.1.277+)"처럼 적었다. `claude --version`으로 먼저 확인한다.
> **확인 필요**는 문서 근거만 있거나 문서에 없어서 내 환경에서 직접 돌려 봐야 하는 것이다. **(제안값)** 은 공식 값이 아니라 이 가이드가 제안하는 기준이다.

## 한눈에 보기

```
A0 기본 이해 ─► A1 전역 정리 ─┬─► A2 프로젝트 지침 ─┐
                              ├─► A3 설정 파일 분리 ─┼─► A5 스킬 ─► A6 훅 ─► A8 검증
                              └─► A4 기록 붙이기 ────┘
                              A7 공개 하네스 분석·포크 (A1 뒤 언제든, 격리된 환경에서)
                              A9 비용·컨텍스트 관리, A10 작업 루틴 (계속)
```

| 단계 | 먼저 끝낼 것 | 같이 할 수 있는 것 | 끝났다는 기준 |
|---|---|---|---|
| A0 기본 이해 | 없음 | 없음 | 무엇이 언제 컨텍스트에 들어가고 무엇이 강제인지 설명할 수 있다 |
| A1 전역 정리 | A0 | 없음 | 빈 폴더에서 켰을 때 내가 의도한 것만 로드된다 |
| A2 프로젝트 지침 | A1 | A3, A4 | 새 세션이 지침을 따르고, 팀원도 같은 지침을 받는다 |
| A3 설정 파일 분리 | A1 | A2, A4 | 팀 설정과 개인 설정이 나뉘고 금지 항목이 실제로 막힌다 |
| A4 기록 붙이기 | A1 | A2, A3 | 한 턴을 돌리면 기록이 보인다 |
| A5 스킬 | A2 | A7 | 불려야 할 때 불리고 아닐 때 안 불린다 |
| A6 훅 | A3 (안내 문구는 A5) | A7 | 위반을 넣으면 막히고, 훅이 고장 나도 정한 대로 동작한다 |
| A7 공개 하네스 | A1 | A5, A6 | 포크본 하나만 설치돼 있다 |
| A8 검증 | A2~A6 | 없음 | 빈 폴더의 작은 작업이 끝까지 통과한다 |

A9·A10은 끝이 없는 습관이다. 매주 회고하면서 조정한다.

## A0. 기본 이해

**왜:** 설정은 "무엇을 언제 컨텍스트에 넣고, 무엇을 하네스가 강제하게 할지"를 정하는 일이다. 구조를 모르면 지침이 안 지켜질 때 원인을 찾지 못한다.

**고민할 것**
- 이 내용은 매 요청마다 컨텍스트를 차지하는가, 필요할 때만 올라오는가. 압축 뒤에도 남는가.
- 이 규칙은 모델에게 하는 부탁인가, 하네스가 집행하는 강제인가.
- 지침이 안 지켜질 때 "로드되지 않았다"와 "로드됐지만 따르지 않았다"를 구분할 수 있는가.

**할 일**
- 공식 문서를 읽는다: 작동 방식, 확장 개요, `.claude` 디렉터리, 컨텍스트 윈도우, 메모리, 설정, 권한, 설정 디버깅.
- 세 가지를 구분한다.
  - **지침**(`CLAUDE.md`, 규칙 파일, 자동 메모리)은 부탁이다. 시스템 프롬프트가 아니라 유저 메시지로 들어가고, 따른다는 보장이 없다. 여러 파일은 덮어쓰지 않고 이어붙으며, 서로 모순되면 어느 쪽을 따를지 정해져 있지 않다.
  - **스킬**은 위임이다. 설명만 항상 올라오고 본문은 쓸 때 읽는다.
  - **훅, 권한 금지(`deny`) 규칙, 샌드박스, 관리 설정**은 강제다. 모델이 아니라 하네스가 실행한다. auto 모드의 분류기는 모델의 판단이므로 강제가 아니다.
- 로드 시점을 익힌다. 세션 중에 `CLAUDE.md`를 고쳐도 그 세션에는 반영되지 않고 `/clear`, `/compact`, 재시작 뒤에 반영된다.

| 무엇 | 언제 로드 | 무엇이 올라오나 | 압축 뒤 |
|---|---|---|---|
| 시스템 프롬프트·도구 정의 | 시작 | 전부 | 유지 |
| `CLAUDE.md`(전역·프로젝트·로컬, 상위 디렉터리 포함), `paths` 없는 규칙 | 시작 | 파일 전체(import 포함) | 디스크에서 다시 주입 |
| 자동 메모리 | 시작 | `MEMORY.md` 앞 200줄 또는 25KB까지. 주제 파일은 필요할 때 | 다시 주입 |
| 스킬 | 시작 + 사용 시 | 시작 시 이름과 설명, 본문은 쓸 때 | 본문은 스킬당 앞 5,000토큰, 합계 25,000토큰까지 |
| MCP | 시작 + 사용 시 | 도구 이름과 서버 안내. 도구 정의(스키마)는 쓸 때 | — |
| `paths` 규칙, 하위 디렉터리 `CLAUDE.md` | 해당 파일을 읽거나 고칠 때 | 파일 내용 | 사라졌다가 그 파일을 다시 다루면 로드 |
| 훅 | 이벤트 발생 시 | 없음(출력을 돌려주면 그만큼) | 붙인 글은 요약에 섞인다 |
| 서브에이전트 | 호출 시 | 별도 컨텍스트. 내장 Explore·Plan은 `CLAUDE.md` 없이 시작 | — |

**확인:** 아무 프로젝트에서 세션을 열고 `/context all`(범주별 점유: 시스템 프롬프트, 도구, MCP 도구, 메모리 파일, 스킬, 대화), `/memory`(로드된 지침 파일과 자동 메모리), `/skills`, `/mcp`, `/hooks`, `/status`(읽은 설정 파일)를 본다.

**끝났다는 기준**
- [ ] 표를 보지 않고 "시작 시 로드 / 필요할 때 로드 / 압축 뒤 남는 것"을 말할 수 있고, `/context all`의 각 범주가 무엇인지 설명할 수 있다
- [ ] 부탁(지침·스킬·auto 모드)과 강제(훅·`deny` 규칙·샌드박스)의 예를 하나씩 들 수 있다

**흔한 함정:** 지침에 적었으니 강제된다고 믿기. auto 모드를 안전장치로 여기기.

## A1. 전역 정리 (`~/.claude`)

**왜:** 전역에 둔 것은 어느 폴더에서 켜든 다 로드된다. 전역이 지저분하면 모든 프로젝트가 영향을 받고, 팀원과 결과가 달라진다.

**고민할 것**
- 이 항목은 내 모든 프로젝트에 필요한가. 아니면 프로젝트로 옮긴다.
- 시작 권한 모드를 무엇으로 둘 것인가. 터미널·VS Code의 대화형 세션은 기본이 `auto`다(v2.1.283+, 그 전 버전은 요금제에 따라 다르다). 분류기 모델이 호출마다 판단하는 방식이다. 매번 직접 승인하려면 Manual(`default`)로 바꾼다. `claude -p`는 Manual로 시작한다.
- 자동 메모리를 켜 둘 것인가(켜 두면 PC마다 Claude의 행동이 달라질 수 있다). claude.ai 계정에서 내려오는 스킬·플러그인을 받을 것인가.
- 대화 기록이 평문으로 며칠 남아도 되는가(`cleanupPeriodDays`, 기본 30일).

**할 일**
- 전역에 있는 것을 뽑아 본다: `ls ~/.claude`, `wc -l ~/.claude/CLAUDE.md`(200줄 이하인지), `claude mcp list`. `~/.claude/settings.json`과 `~/.claude.json`은 다른 파일이다. 권한·훅·`env`는 앞의 파일에 둔다. 뒤의 파일은 Claude Code가 쓰는 상태 파일이고 사용자·로컬 범위 MCP 서버도 여기에 저장된다.
- **전역 지침**(`~/.claude/CLAUDE.md`, `~/.claude/rules/`)은 비우거나 모든 프로젝트에 공통인 것만 둔다. 둘 다 매 세션 로드된다.
- **전역 스킬**도 공통인 것만 둔다. 계정에 켜 둔 스킬은 로그인한 PC마다 `~/.claude/skills/synced/`로 내려온다. 원하지 않으면 사용자 설정에 `"syncClaudeAiSkills": false`, `"syncClaudeAiPlugins": false`를 둔다.
- **사용자 설정**을 정리한다. 엄격한 JSON이라 주석과 끝 쉼표는 오류다. 예시(Manual로 시작하게 한 것이고, 금지 경로는 제안값):
  ```json
  {
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "permissions": { "defaultMode": "default", "deny": ["Read(~/.ssh/**)", "Read(~/.aws/**)"] },
    "statusLine": { "type": "command", "command": "python3 ~/.claude/statusline.py" },
    "cleanupPeriodDays": 30
  }
  ```
  - 시작 권한 모드는 `permissions.defaultMode`로 정한다. `auto`와 `bypassPermissions`는 사용자 설정에서만 효과가 있다(프로젝트·로컬 파일에 적으면 무시된다).
  - 전역 금지 경로는 `~/` 또는 `//`(절대 경로)로 쓴다. 사용자 설정에서 `/path`는 `~/.claude/path`로 풀린다.
  - 모델은 `/model`, 추론 강도는 `/effort <low|medium|high|xhigh>`로 고른다. 강도는 모델별로 `modelSettings`에 저장된다(v2.1.251+). 사용자 설정에 `effortLevel`을 직접 적지 않는다. 구형 키라 Opus 5.5 이후 모델은 무시한다. `max`는 그 세션에만 적용된다.
  - 안 쓰는 기능을 끈다: 내장 스킬은 `disableBundledSkills`나 스킬별 `skillOverrides`, 도구는 `deny`에 도구 이름만 적기(컨텍스트에서 빠진다), 권한 우회 모드는 `permissions.disableBypassPermissionsMode: "disable"`.
- **상태줄**은 `/statusline <보여 줄 내용>`으로 만들거나 [`hooks/statusline.py`](hooks/statusline.py)를 `~/.claude/`에 복사해 위처럼 연결한다. 내용은 A9에서 정한다.
- **자동 메모리**를 `/memory`에서 열어 읽고 틀린 내용을 지운다. 위치는 `~/.claude/projects/<프로젝트>/memory/`이고 이 PC에만 있다. 같은 저장소의 워크트리는 공유한다. 끄려면 `/memory`의 토글이나 `"autoMemoryEnabled": false`.
- PC를 여러 대 쓰면 `~/.claude/settings.json`, `CLAUDE.md`, `rules/`, `skills/`를 dotfiles 저장소로 관리한다. 사용자 설정은 그 PC에만 적용된다(기기 간 동기화가 없다는 명시적 문장은 문서에서 찾지 못했다. 확인 필요).

**확인:** 빈 폴더에서 켠다(`mkdir -p ~/claude-clean/empty && cd ~/claude-clean/empty && claude`). 세션 없이 설정 오류만 보려면 `claude doctor`, 내 설정이 원인인지 가르려면 `claude --safe-mode`(커스터마이즈를 모두 끈 세션)와 비교한다. 빈 폴더 세션 안에서 `/context all`(메모리 파일·스킬·MCP 도구), `/status`(Setting sources에 사용자 설정만, 시작 모델), `/skills`, `/mcp`, `/hooks`, `/permissions`(금지 규칙과 출처 파일), `/effort status`를 본다.

**끝났다는 기준**
- [ ] 빈 폴더의 `/context all`에 의도하지 않은 지침·스킬·MCP 도구가 없고, `claude doctor`가 설정 오류를 보고하지 않는다
- [ ] 시작 권한 모드, 시작 모델, 추론 강도가 내가 고른 값이다
- [ ] 전역 금지 규칙이 `/permissions`에 보이고 실제로 거부된다
- [ ] 자동 메모리를 열어 봤고 켜 둘지 끌지 정했다

**흔한 함정:** `~/.claude.json`에 권한·훅 적기. 사용자 설정에 `effortLevel` 적기. 계정에서 동기화된 스킬을 모르고 두기.

## A2. 프로젝트 지침

**왜:** 팀이 같은 결과를 내려면 지침이 저장소에 있어야 한다. 파일이 길수록 컨텍스트를 더 쓰고 덜 지켜진다. **승격 규칙:** 같은 컨벤션을 **두 번 틀리면** 지침에 한 줄 추가한다.

**고민할 것**
- 이 줄은 모든 세션에 필요한가. 한 폴더에만 필요하면 경로 규칙, 여러 단계 절차면 스킬(A5), 예외가 없어야 하면 훅이나 `deny` 규칙(A3·A6)이다.
- 이 줄은 코드만 봐서는 알 수 없는 내용인가. 디렉터리 구조나 의존성 목록처럼 코드에서 읽을 수 있는 것은 뺀다.
- 원본을 `CLAUDE.md`로 둘 것인가 `AGENTS.md`로 둘 것인가. 팀이 다른 도구도 쓰는가, 팀원의 버전이 v2.1.277 이상인가.
- 모노레포라면 상위 디렉터리의 `CLAUDE.md`가 같이 로드된다. 남의 팀 지침이 섞이지 않는가(빼려면 `.claude/settings.local.json`의 `claudeMdExcludes`에 절대 경로 글롭을 적는다).
- 압축 뒤에도 남아야 하는 규칙이 경로 규칙에 들어가 있지 않은가.

**할 일**
- **프로젝트 지침(`CLAUDE.md`)** 을 커밋한다. 초안은 `/init`으로 만들고 줄인다. 템플릿: [`templates/CLAUDE.md`](templates/CLAUDE.md)
  - 200줄 이하로 쓴다. 구역은 마크다운 헤더와 불릿으로 나눈다. 공식 문서가 권하는 구조라서 템플릿도 이 형식으로 뒀다. 압축 때 꼭 남길 것은 `# Compact instructions` 구역에 적는다.
  - 넣는 것: 작업을 확인하는 정확한 명령(테스트 한 파일만 돌리는 법 포함), 코드가 오해를 부르는 곳, 저장소에 없는 결정, 두 번 고쳐 준 것. 검증할 수 있게 쓴다. "코드를 깔끔하게" 대신 "들여쓰기는 공백 2칸".
  - `@경로` import는 파일을 나눌 뿐 비용을 줄이지 않는다. 깊이는 4단계까지다. 경로를 글자 그대로 적으려면 백틱으로 감싼다.
- **특정 폴더·파일에만 필요한 규칙**은 `.claude/rules/<주제>.md`에 `paths`를 달아 둔다. 예시: [`templates/rules/testing.md`](templates/rules/testing.md)
  - frontmatter에서 읽는 필드는 `paths`뿐이다. `paths`가 없거나 YAML이 깨지면 매 세션 로드된다.
  - 압축하면 빠졌다가 해당 파일을 다시 다룰 때 돌아온다. 압축 뒤에도 꼭 있어야 하면 `paths`를 빼거나 `CLAUDE.md`로 옮긴다.
- **개인용 지침**은 `CLAUDE.local.md`에 두고 `.gitignore`에 넣는다. 워크트리마다 따로 만들어야 하므로, 워크트리를 쓰면 `CLAUDE.md`에 `@~/.claude/<파일>.md` import를 둔다.
- **다른 AI 도구와 같이 쓰면** 원본을 한 파일로 통일한다.
  - Claude Code는 `AGENTS.md`를 직접 읽는다(v2.1.277+). 다만 기본값에서는 작업 디렉터리나 그 위에 `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` 중 하나라도 있으면 읽지 않는다. 전역 `~/.claude/CLAUDE.md`와 `.claude/rules/`는 영향을 주지 않는다.
  - 둘 다 읽게 하려면 `/config`의 Project instructions를 `claude-md-and-agents-md`로 바꾼다. 버전과 설정에 상관없이 통하는 방법은 `CLAUDE.md` 첫 줄에 `@AGENTS.md`를 두고 그 아래에 Claude Code 전용 지침만 적는 것이다.
- 정기 점검: `/doctor`(코드에서 알 수 있는 내용 삭제 제안), `/doctor prompt-audit`(낡았거나 모순되는 지침, v2.1.283+).
- 기존 팀 노하우(위키 등)를 규칙 파일로 옮길 담당자를 정한다.

**확인:** `wc -l CLAUDE.md`(200 이하)와 `git check-ignore -v CLAUDE.local.md`(무시 규칙이 잡히는지)를 돌린다. 새 세션에서 `/context all`의 Memory files에 `CLAUDE.md`, `CLAUDE.local.md`, `paths` 없는 규칙이 있는지 본다. `AGENTS.md`를 쓰면 `/memory` 목록에 그 경로가 있는지 본다. 지침 파일이 권장 길이를 넘으면 시작할 때와 `/status`에 경고가 뜬다.

경로 규칙은 시작 시 목록에 나오지 않는다. `.claude/settings.local.json`에 로드 기록 훅(`jq` 필요)을 잠시 걸고, 해당 경로의 파일을 읽게 한 뒤 로그에 `path_glob_match` 줄이 생기는지 본다(로그 형식은 확인 필요). 훅 없이 보려면 `claude --debug`로 시작한다.
```json
{ "hooks": { "InstructionsLoaded": [ { "hooks": [ { "type": "command",
  "command": "jq -c '{file_path, load_reason}' >> \"${CLAUDE_PROJECT_DIR}/.claude/instructions-loaded.log\"" } ] } ] } }
```
마지막으로 지침의 명령·규칙이 필요한 작은 작업을 시켜 실제로 따르는지 본다.

**끝났다는 기준**
- [ ] `CLAUDE.md`가 커밋돼 있고 200줄 이하이며, 코드에서 읽을 수 있는 내용이 없다
- [ ] 새 세션의 `/context all`에 기대한 지침 파일이 모두 있고, 경로 규칙은 해당 파일을 읽을 때 로드된 기록이 있다
- [ ] 개인 지침 파일이 `git check-ignore`에 잡히고, `AGENTS.md`를 쓰는 경우 `/memory` 목록에 그 경로가 보인다
- [ ] 새 세션이 지침의 명령·규칙을 따른다

**흔한 함정:** 세션 중에 `CLAUDE.md`를 고치고 바로 시험하기(반영되지 않는다). `AGENTS.md`만 쓰는 저장소에 `CLAUDE.local.md` 만들기(`AGENTS.md`가 로드되지 않는다). 안 지켜지는 줄에 "중요"를 덧붙이기(길이를 줄이거나 A6으로 옮긴다).

## A3. 설정 파일 분리

**왜:** 팀이 공유할 설정과 나만 쓰는 설정이 섞이면 서로의 환경을 깨뜨린다. 금지 규칙은 막는 범위에 한계가 있어서, 모르고 쓰면 막혔다고 착각한다.

**고민할 것**
- 이 키는 누구에게 적용돼야 하는가: 내 모든 프로젝트(사용자), 이 저장소의 모두(프로젝트), 이 저장소의 나(로컬). 우선순위는 관리 설정 > 명령줄 > 로컬 > 프로젝트 > 사용자다. `permissions.allow` 같은 목록은 합쳐지고, `deny`는 어느 범위에 있든 이긴다.
- 이 키는 커밋되는 파일에서 효과가 있는가. `defaultMode`의 `auto`·`bypassPermissions`, OpenTelemetry 환경 변수는 프로젝트 파일에서 무시된다. 설정 참조의 Scope 열을 본다.
- 팀원에게 바로 적용되는가. `deny`·`ask`는 바로 적용되고, `allow`와 대부분의 `env`는 각자가 폴더를 신뢰한 뒤에 적용된다.
- 이 금지는 규칙 문자열로 충분한가. 꼭 막아야 하면 샌드박스나 훅을 같이 쓴다.
  - Bash 금지는 Claude가 흔히 쓰는 형태만 막는다. `Bash(rm *)`는 `/bin/rm`이나 `bash -c 'rm ...'`을 못 막는다. 보안 경계가 아니다.
  - `Read` 금지는 파일 도구, `cat`처럼 파일 이름을 대는 명령, 리다이렉션을 막는다. `grep -r`이나 스크립트가 직접 여는 것은 못 막는다.
- `deny`에 넣으면 `allow`로 예외를 뺄 수 없다. 넓게 잡은 금지가 필요한 작업까지 막지 않는가.
- 인증 값이 어디에 평문으로 남는가(설정 파일, 대화 기록).

**할 일**
- **`.claude/settings.json`** 은 팀 공유(커밋): 권한 규칙(`deny`·`ask`·`allow`), 훅, 플러그인, 팀 공통 `model`·`env`. 템플릿: [`templates/settings.json`](templates/settings.json)
- **MCP 서버는 설정 파일에 두지 않는다.** `settings.json`은 `mcpServers` 키를 읽지 않는다. 팀 공유 서버는 저장소 루트의 `.mcp.json`에 두고(예시: [`templates/mcp.example.json`](templates/mcp.example.json)), 개인 서버는 `claude mcp add --scope user`로 넣는다. `.mcp.json`의 서버는 팀원이 각자 승인해야 연결된다.
- **`.claude/settings.local.json`** 은 나만(커밋 제외). 템플릿: [`templates/settings.local.example.json`](templates/settings.local.example.json). 손으로 만들었으면 `.gitignore`에 직접 넣는다. Claude Code가 이 파일을 처음 쓸 때만 자동으로 전역 git 제외 목록에 들어간다.
- 규칙 문법을 지킨다. 형식은 `도구` 또는 `도구(지정자)`이고 평가 순서는 `deny` → `ask` → `allow`다.
  - Bash: `Bash(npm run *)`. 허용 규칙 하나가 `a && b` 같은 복합 명령 전체를 허용하지는 않는다.
  - 파일: `Read(./.env)`, `Read(./secrets/**)`. 쓰기 금지는 `Edit(...)`, 검색 금지는 `Read(...)`로 쓴다. `Write(...)`와 `Grep(...)` 규칙은 동작하지 않는다. `Read` 금지는 같은 경로의 수정·생성도 막는다.
  - 경로: `//절대경로`, `~/홈 기준`, `/설정 파일 기준`, `./현재 디렉터리 기준`. 파일 이름만 쓰면 모든 깊이에 걸린다.
  - 푸시처럼 막지는 않되 물어야 하는 것은 `ask`에 둔다. `.claudeignore`는 효과가 없으니 내용을 `Read` 금지 규칙으로 옮긴다.
- **이 프로젝트에서만 다른 모델**을 쓰려면 `model` 키를 둔다(팀 전체면 프로젝트 파일, 나만이면 로컬 파일). **엔드포인트**는 `env`의 `ANTHROPIC_BASE_URL`로 바꾼다. 이 값은 요청을 보낼 곳만 바꾸고 모델은 바꾸지 않는다. 전역은 건드리지 않는다.
- **인증 값**은 커밋되는 파일에 두지 않는다. 로컬 파일, 셸 환경 변수, `apiKeyHelper` 중 하나를 쓴다. 대화에도 넣지 않는다. 도구가 읽은 값은 대화 기록(`~/.claude/projects/`)에 평문으로 남는다. 이미 들어갔으면 `claude purge <경로> --dry-run`으로 지울 범위를 본다.
- **샌드박스**를 검토한다. 기본은 꺼져 있고 `/sandbox`나 `sandbox.enabled`로 켠다. 셸 명령만 감싸며(파일 도구·MCP 서버·훅은 밖) `Read` 금지 경로를 셸 명령도 못 읽게 한다. macOS·Linux·WSL2에서 동작하고 Linux는 `bubblewrap`과 `socat`이 필요하다. 쓸 수 없는 환경에서는 알림 없이 샌드박스 밖에서 실행되므로, 반드시 필요하면 `sandbox.failIfUnavailable: true`를 둔다.

**확인**
```bash
python3 -m json.tool .claude/settings.json > /dev/null && echo OK    # 엄격한 JSON인지
git check-ignore -v .claude/settings.local.json                      # 개인 설정이 무시되는지
git grep -n -i 'token\|api_key' -- .claude .mcp.json     # 커밋된 인증 값이 없는지
claude doctor
```
세션 안에서 `/status`(Setting sources, 게이트웨이를 쓰면 Anthropic base URL 줄)와 `/permissions`(규칙과 출처 파일)를 본다. 금지는 두 경로로 시험한다. ".env 파일 내용을 보여줘"와 "cat .env를 실행해줘" 둘 다 거부돼야 한다. 샌드박스를 켰으면 Claude에게 `touch ~/sandbox-probe`와 `curl --noproxy '*' https://example.com`을 실행시킨다. 둘 다 실패해야 한다. `!`로 직접 치면 샌드박스 밖에서 돈다.

**끝났다는 기준**
- [ ] 팀 설정(`.claude/settings.json`, `.mcp.json`)은 커밋돼 있고 개인 설정은 `git check-ignore`에 잡힌다
- [ ] `/status`의 Setting sources와 `/permissions`의 규칙 출처가 기대와 같다
- [ ] 파일 도구와 `cat` 두 경로 모두에서 금지 항목이 거부된다
- [ ] 금지 규칙이 못 막는 경로를 알고 있고, 필요하면 샌드박스나 훅으로 보완했다
- [ ] 커밋된 파일에 인증 값이 없고, 전역 설정에 프로젝트 전용 값이 없다

**흔한 함정:** MCP 서버를 `settings.json`에 적기. 하위 폴더에서 `claude`를 시작하기(공유 프로젝트 설정은 시작 디렉터리의 `.claude/`에서만 읽고 상위로 올라가지 않는다). `Read(./.env)`가 하위 폴더의 `.env`도 막는다고 믿기(시작 디렉터리만 막는다. 전부 막으려면 `Read(**/.env)`). 금지 규칙만으로 비밀이 안전하다고 믿기.

## A4. 기록 붙이기

**왜:** 측정해야 개선할 수 있다. 내 사용 기록을 봐야 낭비와 반복 실수가 보인다.

**고민할 것**
- 어디까지 남길 것인가. 지표(토큰·비용·시간)만인가, 프롬프트와 도구 인자까지인가.
- 기록이 어디로 가는가. 회사 코드가 외부 클라우드로 나가도 되는가. 안 되면 사내 수집기나 셀프호스팅을 쓴다.
- 도구를 새로 붙여야 하는가. 혼자 쓰는 수준이면 내장 명령으로 충분할 수 있다.

**할 일** (가벼운 것부터 고른다)
1. **설치 없이:** `/usage`(세션 비용·토큰·캐시 통계, 달러 값은 추정), `/context`(지금 컨텍스트 구성), `/insights`(이 PC의 최근 세션을 분석한 HTML 보고서. 분석에 내 사용량을 쓴다).
2. **내장 OpenTelemetry:** 수집기가 있으면 `~/.claude/settings.json`의 `env`에 `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_METRICS_EXPORTER`, `OTEL_LOGS_EXPORTER`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_ENDPOINT`를 넣는다. 저장소의 설정 파일에 넣으면 무시된다. 기본으로는 프롬프트 내용과 도구 인자를 남기지 않는다. 남기려면 `OTEL_LOG_USER_PROMPTS=1`, `OTEL_LOG_TOOL_DETAILS=1`을 따로 켠다.
3. **제3자 플러그인(예: Langfuse):** 턴 단위 추적 화면이 필요할 때 쓴다.
   ```
   claude plugin marketplace add langfuse/Claude-Observability-Plugin
   claude plugin install langfuse-observability@langfuse-observability
   ```
   uv가 PATH에 있어야 한다. 사용자 범위(기본)로 설치해야 어느 폴더에서든 기록된다. 설치 뒤 재시작하고, 키는 세션 안에서 `/plugin configure langfuse-observability@langfuse-observability`로 넣는다. 기본 주소는 EU 리전이다. 다른 리전이나 셀프호스팅이면 `LANGFUSE_BASE_URL`을 넣는다. 자동 업데이트가 꺼져 있어 업데이트는 직접 한다.

**확인:** 한 턴을 돌린 뒤 고른 수단에서 그 턴이 보이는지 확인한다. OTel은 수집기에서 지표 `claude_code.session.count`와 이벤트 `claude_code.user_prompt`를 찾고, 안 오면 `claude --debug-file <경로>`로 시작해 로그에서 `[3P telemetry]`를 찾는다. 플러그인은 `claude plugin list`와 `tail -n 20 ~/.claude/state/langfuse_hook.log`를 본다. Langfuse의 전송 시점은 문서에 없으니(확인 필요) 바로 안 보이면 이 로그의 최근 줄부터 본다.

**끝났다는 기준**
- [ ] 한 턴을 돌린 뒤 그 턴의 도구 호출·소요 시간·토큰을 볼 수 있다(`/usage`, 수집기, 플러그인 화면 중 하나)
- [ ] 프롬프트·도구 인자를 남길지 내가 정했고 설정이 그 결정과 같다
- [ ] 기록이 가는 곳(로컬, 사내 수집기, 외부 클라우드)을 알고 있다

**흔한 함정:** OTel 변수를 프로젝트 설정에 넣기. 플러그인을 프로젝트 범위로 설치해 놓고 모든 폴더가 기록된다고 믿기. 기록이 쌓이기 전에 패턴을 단정하기(제안값: 1주 이상 쌓은 뒤 본다. 오류 뒤 재시도 반복, 한 번에 묶을 수 있었던 연속 호출이 대표적인 낭비다).

## A5. 스킬

**왜:** 같은 절차를 매번 붙여넣는 건 낭비이고, 지침에 다 넣으면 항상 토큰을 먹는다. 스킬은 필요할 때만 본문을 읽는다. **승격 규칙:** 같은 절차를 **세 번째 붙여넣게 되면** 스킬로 만든다.

**고민할 것**
- 이 내용이 스킬인가. 항상 적용할 규칙이면 지침, 매번 강제해야 하면 훅, 필요할 때만 읽는 절차·지식이면 스킬이다.
- 누가 부르는가. 부작용이 있으면 나만(`disable-model-invocation: true`), 배경 지식이면 Claude만(`user-invocable: false`).
- 대화 맥락이 필요한가. 필요 없고 출력이 길면 `context: fork`로 서브에이전트에서 돌린다. 이 경우 대화 기록을 못 본다.
- 스킬이 몇 개인가. 설명 목록의 예산은 컨텍스트 창의 1%다. 넘으면 덜 쓰는 스킬부터 설명이 빠지고 이름만 남는다.

**할 일**
- 구조: `.claude/skills/<이름>/SKILL.md` + 필요하면 `scripts/`(실행 코드), `references/`(상세 문서), `assets/`(양식). 프로젝트 전용은 프로젝트에, 공통은 `~/.claude/skills/`에 둔다.
- **설명**은 무엇을 하는지와 언제 쓰는지(아닌 경우 포함)를 쓴다. `description`과 `when_to_use`를 합쳐 1,536자에서 잘리므로 핵심 용도를 맨 앞에 둔다.
- **본문**은 500줄 이하로 핵심만 두고, 가장 중요한 지시를 맨 위에 둔다. 한번 불리면 본문이 대화에 계속 남고, 압축 뒤에는 스킬당 앞 5,000토큰만 다시 붙는다. 상세는 `references/`로 빼고 언제 읽을지를 적는다.
- frontmatter는 필요한 필드만 쓴다. 필드 이름이 틀리면 오류 없이 무시된다.
  - `disable-model-invocation: true`: 부작용이 있거나 순서가 중요한 절차. 설명이 컨텍스트에서 빠져 상시 비용도 없어진다.
  - `allowed-tools`: 도구 제한이 아니라 그 턴 동안의 사전 승인이다. 저장소에 들어온 남의 스킬은 이 필드부터 읽는다.
  - `model`: 세션 모델과 다르면 그 턴은 모델 전환이라 캐시를 못 쓴다(A9).
  - `hooks`: 이 스킬을 쓸 때만 지켜야 하는 강제 규칙을 둔다.
- 쓰는 도구의 사용법도 스킬에 적는다.

**확인:** `claude plugin validate .claude/skills`로 frontmatter를 검사한다(모델 호출 없음, 종료 코드 0이면 통과, v2.1.233+). 세션 안에서 `/skills`(목록, `t`로 토큰 순 정렬), `/skill-doctor`(스킬별 비용과 사용 빈도, v2.1.252+)를 본다. 호출 시험은 **새 세션**에서 한다. 불려야 하는 요청 3개와 불리면 안 되는 요청 3개를 넣는다(제안값). 불렸다는 것과 결과가 나아졌다는 것은 다르다. 결과는 스킬을 끈 세션과 비교한다. 끄는 법은 `.claude/settings.local.json`의 `{"skillOverrides": {"<스킬 이름>": "off"}}`다.

**끝났다는 기준**
- [ ] `claude plugin validate`가 통과하고 새 세션의 호출 시험 결과가 기대와 같다
- [ ] 스킬을 켠 결과가 끈 결과보다 낫다는 것을 한 번 이상 비교했다
- [ ] 부작용 있는 스킬은 `disable-model-invocation: true`이고, 본문 500줄 이하·설명 1,536자 이하다

**흔한 함정:** 설명 앞부분에 핵심이 없기. 남의 스킬을 그대로 복사해 쓰기(동작을 보고 패턴만 가져온다). 매번 지켜야 하는 규칙을 스킬에 두기(A6으로 옮긴다).

## A6. 훅

**왜:** 지침과 스킬은 따를 수도 안 따를 수도 있다. 매번 일어나야 하는 일은 하네스가 실행하게 해야 한다. **승격 규칙:** 묻지 않아도 **매번 일어나야 하는 일**은 훅에 연결한다.

**고민할 것**
- 이 규칙에 예외가 정말 0개인가. 예외가 있으면 지침에 둔다. 강제 규칙은 적게 유지한다. 가끔 잘못 발동하고 누군가 유지해야 한다.
- 훅이 고장 나면 막을 것인가 통과시킬 것인가. 막는 훅(게이트)은 고장 나도 막게, 알려 주는 훅(피드백)은 건너뛰게 정하고 코드와 설정에 둘 다 반영한다.
- 어떤 경로가 이 훅을 비켜 가는가: 셸 명령으로 파일 쓰기, `@` 파일 첨부, 사람이 직접 고치기, 매처에 없는 도구.
- 얼마나 자주 도는가. 도구 훅은 호출마다, 서브에이전트 안에서도, 병렬 호출이면 동시에 돈다.

**할 일**
- **언제 동작해야 하는지**부터 정한다.
  - 실행 전(PreToolUse)은 **막는다.** 막기, 사람에게 묻기, 확인 창 건너뛰기를 결정할 수 있다.
  - 실행 후(PostToolUse)는 **고치게 한다.** 성공한 호출 뒤에만 돌고 되돌리지 못한다. exit 2와 stderr로 모델에 알린다. 무거운 검사는 묶음당 한 번 도는 PostToolBatch나 Stop으로 옮긴다.
  - 끝내기 전(Stop)은 **확인한다.** 작업이 끝날 때가 아니라 응답이 끝날 때마다 돈다(사용자가 중단하면 안 돈다). 입력의 `stop_hook_active`가 true면 다시 막지 않는다. 8번 연속 막으면 하네스가 턴을 끝낸다.
  - 입력 제출(UserPromptSubmit)은 모델에 가기 전이다. 현재 브랜치처럼 **그때그때 달라지는 상태**를 사실 진술로 짧게 붙인다. 변하지 않는 지침은 `CLAUDE.md`에 둔다. 예약 작업이나 백그라운드 서브에이전트 보고에도 돌고, 붙인 글은 요청마다 대화 기록에 쌓인다.
  - 세션 종료(SessionEnd)에는 중요한 정리를 맡기지 않는다. 막을 수 없고 기본 제한 시간이 1.5초다.
- **종료 코드:** 0은 통과, 2는 차단(stderr가 사유로 전달된다), 그 밖은 오류지만 통과다. 게이트 훅에는 설정에 `"onFailure": "block"`(v2.1.295+)과 짧은 `timeout`을 줘서 스크립트가 죽거나 시간을 넘겨도 막히게 한다. Stop 훅에는 이 키가 효과가 없다.
- **판정은 코드로 한다**(`command` 타입). 돌릴 테스트도 이름·폴더 규칙으로 고른다. `prompt`·`agent` 타입 훅은 다른 모델이 판단하므로 강제가 아니다. **검사는 훅, 해결은 스킬**로 나누고 훅 메시지에 고치는 방법을 적는다.
- **설정:** 경로는 `${CLAUDE_PROJECT_DIR}`로 쓰고 `command` + `args` 형식을 쓴다. 매처는 실제 도구 이름으로 쓰고 대소문자를 가린다. 파일 수정은 `Edit|Write`(노트북 포함이면 `Edit|Write|NotebookEdit`)다. `MultiEdit`는 현재 도구가 아니다. Stop과 UserPromptSubmit은 매처가 없다.
- **JSON 출력:** stdout에 JSON 객체 하나만 찍는다. PreToolUse의 결정은 `hookSpecificOutput.permissionDecision`에 둔다. 최상위에 두면 오류 없이 무시된다.
- 프로젝트 훅은 **규칙이 생긴 뒤 필요가 확인되면** 만든다. 예시를 [`hooks/`](hooks/)에 뒀고 기본으로 켜지지 않는다. 켤 때는 [`hooks/settings.example.json`](hooks/settings.example.json)을 보고 연결한다. 한계와 시험 방법은 [`hooks/README.md`](hooks/README.md)에 있다.
  - `plan_gate.py`: 승인된 계획이 없거나 계획 범위 밖인 수정을 막는다.
  - `approve_plan.py`: 사람이 터미널에서 실행해 계획 승인을 기록한다.
  - `test_after_edit.py`: 고친 파일과 짝지은 테스트만 돌리고 실패하면 모델에 알린다.
  - `prompt_reminder.sh` + `reminders.md`: 짧은 사실 진술을 매 요청에 붙인다.
  - `stop_check.py`: 끝내기 전에 검사 명령을 돌리고 실패하면 계속 일하게 한다.

**반드시 알아야 할 함정**
- 차단은 exit 2나 JSON 거부로만 된다. **exit 1, 스크립트 오류, 시간 초과, 경로 오타는 `hook error` 알림만 남기고 통과한다.**
- 셸 명령으로 파일을 쓰면 `Edit|Write` 매처를 거치지 않는다. `@`로 붙인 파일은 도구 호출이 아니라서 Read용 훅을 거치지 않는다. 읽기를 막으려면 `deny` 규칙을 쓴다.
- 훅의 거부는 모든 권한 모드에서 통한다. 훅의 허용은 확인 창을 건너뛰게 할 수 있지만 권한 설정의 `deny`·`ask` 규칙을 넘지 못한다. 꼭 막아야 하는 것은 `deny` 규칙(A3)으로도 이중으로 막는다.
- 훅은 서브에이전트의 도구 호출에도 돈다. 같은 이벤트의 훅은 병렬로 돌아서, 한 훅이 막아도 다른 훅의 부작용은 일어난다.
- 명령 훅은 내 사용자 권한으로, 샌드박스 밖에서 돈다. 대화형 세션은 폴더를 신뢰하기 전까지 훅을 보류하지만 `claude -p`는 신뢰 확인 없이 저장소의 훅을 돌린다. 남의 저장소는 `--bare`나 `--settings '{"disableAllHooks": true}'`로 연다.
- 훅은 하나씩 끌 수 없고 전부 끄는 `disableAllHooks`만 있다. 잘못된 훅 항목이 하나 있으면 그 설정 파일의 다른 설정까지 적용되지 않을 수 있다(`claude doctor`의 경고가 근거이고 공식 문서에서는 찾지 못했다. 확인 필요).
- `stop_hook_active`를 보고 물러난 두 번째 종료는 검사를 통과한 것이 아니다. 최종 방어선은 리뷰와 CI다.

**확인**
```bash
# 스크립트 단위: 승인된 계획이 없거나 범위 밖이면 2(차단). 깨진 입력도 게이트면 2여야 한다. 스크립트별 기대값은 hooks/README.md
echo '{"tool_name":"Edit","tool_input":{"file_path":"'"$PWD"'/src/a.py"}}' | python3 .claude/hooks/plan_gate.py; echo "exit=$?"
echo '{broken' | python3 .claude/hooks/plan_gate.py; echo "exit=$?"
claude doctor                                                                  # 설정 파일: "Invalid settings"가 없어야 한다
claude --debug-file /tmp/claude-hooks.log && grep 'Hooks:' /tmp/claude-hooks.log    # 실제 발동 기록 (v2.1.296+)
```
세션 안에서 `/hooks`로 등록을 확인하고, 위반을 시도해 대화 기록(`Ctrl+O`)에 차단 사유가 보이는지 본다. `onFailure: "block"`은 스크립트 경로를 일부러 틀리게 해서 막히는지 본다. 스크립트 단위 시험은 실제 세션의 차단을 보장하지 않는다. 예시 훅이 세션에서 실제로 막는지, auto 모드에서 훅의 묻기 결정이 확인 창으로 가는지는 재현하지 못했다(확인 필요).

**끝났다는 기준**
- [ ] 켠 훅마다 세 가지 입력(정상, 위반, 깨진 입력) 시험 결과가 있고, `claude doctor`에 `Invalid settings`가 없으며 `/hooks`에 훅이 보인다
- [ ] 실제 세션에서 위반을 시도했을 때 막힌다
- [ ] 게이트 훅은 스크립트가 없거나 죽어도 막힌다
- [ ] 막지 못하는 우회 경로를 적어 뒀다

## A7. 공개 하네스·플러그인

**왜:** 처음부터 짜는 것보다 검증된 것을 가져와 내 방식에 맞게 고치는 편이 빠르다. 다만 그대로 쓰면 내 작업 방식과 어긋나고 토큰을 많이 쓴다.

**고민할 것**
- 이 플러그인이 내 PC에서 무엇을 실행하는가. 훅과 MCP 서버는 내 권한으로, 샌드박스 밖에서 돈다.
- 매 세션 얼마를 더 내는가(스킬·에이전트 설명의 상시 토큰).
- 어느 범위에 설치할 것인가: 사용자(모든 프로젝트), 프로젝트(커밋), 로컬(나만, 이 저장소). 프로젝트 범위는 팀원에게 켜지기만 하고 내려받아지지는 않는다.
- 포크를 플러그인으로 유지할 것인가, 필요한 스킬·훅만 `.claude/`로 가져올 것인가. 한 프로젝트에서 나 혼자 쓰면 `.claude/`가 낫다.

**할 일**
1. 설치 전에 출처(`claude plugin marketplace list`)와 내용을 본다. 저장소를 클론해 `claude --plugin-dir <폴더> plugin details <이름>`으로 구성과 상시 토큰을 보고, `hooks/hooks.json`, `.mcp.json`, `bin/`은 직접 읽는다. 설치 화면은 훅이 있다는 것만 보여 주고 무엇을 실행하는지는 보여 주지 않는다.
2. 설치하지 않고 써 본다: `claude --plugin-dir <폴더>`는 그 세션에만 로드한다. 망가져도 되는 환경에서 한다.
3. **포크**해서 어긋나는 점만 바꾼다: 계획 승인 절차, 커밋·PR 자율성, 언어 규칙, 역할별 모델. 바꾼 뒤 `claude plugin validate <폴더> --strict`.
4. 설치한다: `claude plugin marketplace add <소스>` → `claude plugin install <이름>@<마켓> [--scope project|local]`.
5. **원본은 지운다:** `claude plugin uninstall <이름>@<마켓>`. 둘 다 켜 두면 훅이 두 번 돌고 스킬 설명이 두 벌 실린다.
6. 계획 단계에는 질문형 인터뷰 도구가 유용하다. 질문이 끝나지 않으면 20턴쯤(제안값)에서 멈추고 결과물을 만들게 한다.

**확인:** `claude --plugin-dir ./fork plugin details <이름>`(구성 목록과 Always-on 토큰), `claude plugin validate ./fork --strict`(0이면 통과), `claude plugin list`(설치·활성 상태)를 돌린다. 세션 안에서 `/plugin`, `/hooks`(플러그인 훅의 출처), `/context all`을 본다.

**끝났다는 기준**
- [ ] `claude plugin list`에 포크본 하나만 있고 원본은 지웠다
- [ ] 포크의 `hooks/hooks.json`, `.mcp.json`, `bin/`을 직접 읽었다
- [ ] 상시 토큰 비용을 알고 있고, 무엇을 왜 바꿨는지 적어 뒀다

**흔한 함정:** 설치 화면만 보고 설치하기. 자동 업데이트를 켜 두고 검토가 끝났다고 믿기(검토한 파일이 바뀔 수 있다).

## A8. 검증

**왜:** 설정이 맞는지는 실제 작업을 끝까지 돌려 봐야 안다.

**고민할 것**
- 무엇을 보면 "세팅이 동작한다"고 할 것인가. 지침·스킬·훅·기록 각각에 대해 관찰할 증거를 미리 정한다.
- 모델의 "됐습니다"가 아니라 명령 출력으로 확인할 수 있는가.

**할 일**
- 세션을 열기 전에 정적 점검부터 한다(모델 호출 없음).
- **빈 폴더**에 세팅을 설치하고 작은 개발 작업(예: 백엔드 API 하나)을 계획 모드로 시작해 끝까지 맡긴다(`claude --permission-mode plan` 또는 `Shift+Tab`).
- 지켜보면서 지침을 따르는지, 스킬이 제때 불리는지, 훅이 막을 것을 막는지, 기록이 남는지 본다. 끝에는 증거를 요구한다: 실행한 명령과 그 출력. 리뷰는 대화를 보지 않은 쪽에 맡긴다(`/code-review`).

**확인:** 정적 점검은 `claude doctor`(설치 상태, 설정 오류), `claude plugin validate .claude/skills`(스킬 frontmatter), `claude plugin list`다. 세션 안에서 `/context all`, `/memory`, `/hooks`, `/skills`, `/mcp`, `/status`를 본다. 훅이 실제로 돌았는지는 `claude --debug-file <경로>` 로그의 `Hooks:` 줄로 본다. 문제가 세팅 탓인지 가르려면 `claude --safe-mode`와 비교한다.

**끝났다는 기준**
- [ ] 정적 점검 명령이 모두 통과했다
- [ ] 작은 작업이 계획 → 구현 → 테스트 통과까지 끝났고, 완료를 테스트 출력으로 판정했다
- [ ] 지침·스킬·훅·기록 각각에 대해 동작했다는 증거(명령 출력, 로그 줄)를 남겼다
- [ ] 발견한 문제를 승격 규칙(두 번 → 지침, 세 번 → 스킬, 매번 → 훅)에 따라 반영했다

**흔한 함정:** 설정을 만든 프로젝트에서만 시험하기(전역과 프로젝트 설정이 섞여 원인을 가릴 수 없다).

## A9. 비용·컨텍스트 관리 (계속)

**왜:** 요청마다 대화 전체를 다시 보내므로 비용은 컨텍스트 크기에 비례한다. 캐시가 살아 있으면 할인되고 깨지면 전체를 다시 계산한다.

**고민할 것**
- 지금 비용을 키우는 것이 무엇인가: 긴 대화, 캐시 미스, 백그라운드 작업(서브에이전트, `/goal` 평가) 중 어느 것인가.
- 이 대화를 이어갈 것인가 버릴 것인가. 작업이 바뀌면 `/clear`(비용 없음), 이어가면 `/compact`(그 자체가 큰 요청), 잘못 든 길이면 `/rewind`(캐시 유지)다.
- 내 캐시 수명이 얼마인가. 구독의 메인 대화는 1시간, API 키·사용 크레딧은 5분, 서브에이전트는 5분이다. 이보다 오래 자리를 비우면 돌아와서 첫 요청이 전체 재처리다.
- 서브에이전트를 쓰는 이유가 맞는가. 병렬, 시끄러운 출력 격리, 독립 리뷰면 쓴다. 토큰은 더 들고 답이 더 좋아지지는 않는다.

**할 일**
- **상태줄에 컨텍스트 사용률과 캐시 상태를 띄운다.** 쓸 수 있는 필드는 `context_window.used_percentage`, `prompt_cache.warm`·`hit_ratio`·`misses`(v2.1.251+), `prompt_cache.last_miss_cause`(v2.1.260+), `cost.total_cost_usd`(추정)다. 예시: [`hooks/statusline.py`](hooks/statusline.py). 상태줄은 로컬에서 돌고 토큰을 쓰지 않는다.
- **캐시를 깨지 않는다.** 캐시는 프롬프트 앞부분이 정확히 같아야 맞는다.
  - 깨는 것: 모델 전환, 추론 강도 변경, MCP 서버 연결·해제, 플러그인 켜기·끄기, 도구 전체 금지, 압축, Claude Code 업그레이드.
  - 유지하는 것: 파일 수정, 권한 모드 전환, 스킬 호출, `/rewind`, 서브에이전트 호출. `CLAUDE.md` 수정도 캐시는 유지하지만 그 세션에는 적용되지 않는다.
- **모델과 추론 강도는 세션을 시작할 때 정한다.** 역할 분리는 세션 중 전환이 아니라 서브에이전트 정의(`model: haiku`)나 별도 세션으로 한다. 강도는 기본값(최신 모델은 medium)에서 시작하고 필요한 작업에만 올린다.
- **컨텍스트 사용률을 본다.** 공식 문서에는 "몇 %에서 압축하라"는 기준이 없다. 최신 모델은 창이 크고 자동 압축이 있어 창이 차는 일은 드물다는 입장이다. 그래도 집중된 컨텍스트가 답이 좋고 싸다. 내 기준은 60~65%에서 경고, 80%를 넘으면 다음 요청 전에 정리다(제안값. 1M 창에서는 같은 %가 훨씬 많은 토큰이므로 조정한다).
  - 압축은 작업의 자연스러운 끊김에서, 캐시가 살아 있을 때, 남길 것을 지정해서 한다: `/compact <남길 것>`. 자동 압축 시점은 `/autocompact`로 조정한다(v2.1.221+). 일부만 줄이려면 `/rewind`의 부분 요약을 쓴다. 중요한 요약은 파일로도 남긴다.
- **MCP 도구는 실제 점유를 확인한다.** 도구 정의는 기본으로 필요할 때만 로드되고 이름과 서버 안내만 상시 올라온다. 도구 검색이 꺼진 환경(`ENABLE_TOOL_SEARCH=false`, 일부 클라우드 배포, 옛 모델)에서는 전체 정의가 실린다. `gh` 같은 CLI가 있으면 MCP보다 가볍다.
- **큰 탐색은 서브에이전트에 맡기고** 짧은 요약만 받는다. **잘못 지시했으면** 기다리지 말고 멈추고 정정한다.
- **출력도 비용이다.** `/output-style concise`(v2.1.269+)를 검토한다. 추론 토큰은 출력 토큰으로 과금된다.
- 주기적으로 `/skill-doctor`, `/context all`, `claude plugin details <이름>`로 상시 비용을 줄인다.

**확인**
```bash
echo '{"model":{"display_name":"Opus"},"context_window":{"used_percentage":8},"prompt_cache":{"warm":true,"hit_ratio":0.91,"misses":2}}' | python3 ~/.claude/statusline.py
claude -p "hello" --output-format json     # usage.cache_creation에서 내 캐시 수명(1시간/5분) 확인. 모델 호출 1회
```
세션 안에서 `/usage`의 Prompt cache 줄(캐시에서 읽은 비율, 미스 횟수, warm 여부)과 `/context all`을 본다. 상태줄 `prompt_cache` 필드의 실제 값은 세션에서 직접 확인하지 못했다(확인 필요).

**점검 항목**
- [ ] 상태줄에서 컨텍스트 사용률과 캐시 warm 여부를 볼 수 있다
- [ ] 캐시 미스가 났을 때 원인을 찾을 수 있다(`last_miss_cause` 또는 `/usage`)
- [ ] 내 캐시 수명을 알고 있고, 작업이 바뀔 때 `/clear`하는 습관이 있다

**흔한 함정:** 세션 중에 `/model`로 계획용·구현용 모델을 오가기. 오래 비운 세션을 돌아와서 `/compact`하기(캐시가 식은 뒤라 가장 비싸다).

## A10. 작업 루틴 (계속)

**왜:** 세팅이 좋아도 작업마다 끝의 정의와 확인 수단이 없으면 "완료했다"는 말만 남는다.

**고민할 것**
- 이 작업의 끝을 무엇으로 판정할 것인가. 통과·실패가 나오는 검사(테스트, 빌드, 린터)가 있는가. 없으면 먼저 만든다.
- 지켜볼 것인가 맡기고 떠날 것인가. 떠날 거면 다섯 가지를 정한다: 끝의 정의, 스스로 확인할 수단, 건드려도 되는 범위, 멈추는 조건, 결과를 받는 곳과 승인자.

**할 일**
1. **요구 정리:** 모호하면 인터뷰하게 한다. 질문에 답하면서 숨은 가정을 드러낸다.
2. **계획 → 리뷰 → 승인:** `Shift+Tab` 또는 `/plan <설명>`으로 계획 모드에 들어간다. 계획(수정 대상, 순서, 테스트 방법)은 `Ctrl+G`로 직접 고칠 수 있다. 리뷰는 대화를 보지 않은 서브에이전트에 요구사항 대조로 맡긴다. 승인은 내가 한다.
3. **실행:** 긴 작업이면 `/goal`로 **완료 조건**을 건다. 방법을 맡기는 명령이 아니라, 턴이 끝날 때마다 조건이 충족됐는지 평가해서 충족될 때까지 계속 일하게 하는 명령이다.
   - 조건에는 측정 가능한 끝 상태, 확인 방법, 지킬 제약, 중단 조건을 넣는다. 예: `/goal tests/auth의 테스트가 모두 통과하고 lint가 깨끗하다. 다른 테스트 파일은 고치지 않는다. 20턴 안에 안 되면 멈춘다`
   - 평가자는 명령을 돌리거나 파일을 읽지 않고 대화에 나온 출력만 본다. 조건은 Claude가 직접 돌려 보여 줄 수 있는 것으로 쓴다. 권한 모드는 바꾸지 않으므로 확인 창 없이 돌리려면 auto 모드에서 쓴다. 최소 버전은 문서에 없다(확인 필요).
4. **검증:** "완료했다"는 말이 아니라 실행한 명령과 출력으로 확인한다. 필요하면 `/verify`(앱을 실제로 띄워 확인), `/code-review`(대화를 보지 않은 서브에이전트가 diff 리뷰)를 쓴다. 매번 강제하려면 Stop 훅(A6)에 건다.
5. **주간 회고:** `/insights` 보고서(`~/.claude/usage-data/report.html`), `/usage`, `/skill-doctor`를 읽고 낭비와 반복을 찾는다. 찾은 것을 승격 규칙에 따라 반영한다.

개입 수단: `Esc`(중단), `/rewind`(코드와 대화 되감기. 셸 명령으로 바꾼 파일은 git으로 되돌린다), `/btw`(기록에 남지 않는 곁질문), `/clear`. 정정이 두 번 실패하면 세 번째 정정 대신 `/clear`하고 배운 것을 넣어 프롬프트를 새로 쓴다.

**확인:** `/goal`(인자 없이: 현재 조건과 평가 상태), `/rewind`(체크포인트 목록). 무인 실행에는 상한을 건다(숫자는 제안값).
```bash
claude -p "/goal tests/auth의 테스트가 모두 통과한다" --max-turns 30 --max-budget-usd 5
```

**점검 항목**
- [ ] 작업마다 통과·실패가 나오는 검사가 하나 이상 있다
- [ ] 완료를 명령 출력으로 확인했다
- [ ] 주간 회고에서 한 가지 이상을 승격 규칙에 따라 반영했다

**흔한 함정:** `/goal` 조건을 평가자가 볼 수 없는 것으로 쓰기("코드가 깔끔하다"). 리뷰어에게 "문제를 찾아라"만 시키기(항상 무언가를 찾아낸다. 정확성에 영향을 주는 것만 보고하게 한다).

### 승격 규칙 (한 장 요약)

| 신호 | 옮길 곳 |
|---|---|
| 같은 컨벤션을 두 번 틀렸다 | 지침 (`CLAUDE.md` 또는 경로 규칙) |
| 같은 절차를 세 번째 붙여넣는다 | 스킬 |
| 묻지 않아도 매번 일어나야 한다 | 훅 |
| 다른 저장소에도 같은 구성이 필요하다 | 플러그인 |
| 그래도 실수가 반복된다 | 더 강한 층으로 (지침 → 스킬 → 훅·권한 → 테스트·CI) |

## 전체가 끝났다는 기준

1. 빈 폴더에서 켰을 때 의도한 것만 로드된다 (A1)
2. 프로젝트 지침·규칙·설정·MCP 구성이 저장소에 있고 팀원도 같은 것을 받는다 (A2, A3)
3. 한 턴을 돌리면 기록을 볼 수 있다 (A4)
4. 반드시 지켜야 하는 규칙은 훅이나 권한 설정으로 막히고, 막지 못하는 경로를 알고 있다 (A3, A6)
5. 빈 폴더의 작은 작업이 끝까지 통과했다 (A8)
6. 주간 회고 일정이 있다 (A10)

## 참고 자료

공식 문서(`https://code.claude.com/docs/en/` 아래)와 관련 공식 저장소다. 색인은 [Claude Code Docs](https://code.claude.com/docs/llms.txt)에 있다.

- 구조(A0): [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works), [Extend Claude Code](https://code.claude.com/docs/en/features-overview), [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory), [Explore the context window](https://code.claude.com/docs/en/context-window)
- 지침·메모리(A1, A2): [How Claude remembers your project](https://code.claude.com/docs/en/memory), [Debug your configuration](https://code.claude.com/docs/en/debug-your-config)
- 설정·권한(A1, A3): [Settings files and precedence](https://code.claude.com/docs/en/settings), [All settings](https://code.claude.com/docs/en/settings-reference), [Example settings files](https://code.claude.com/docs/en/settings-example), [Environment variables](https://code.claude.com/docs/en/env-vars), [설정 JSON 스키마](https://json.schemastore.org/claude-code-settings.json), [Configure permissions](https://code.claude.com/docs/en/permissions), [Choose a permission mode](https://code.claude.com/docs/en/permission-modes), [Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing)
- 모델·게이트웨이·MCP(A1, A3): [Model configuration](https://code.claude.com/docs/en/model-config), [Connect Claude Code to an LLM gateway](https://code.claude.com/docs/en/llm-gateway-connect), [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
- 기록(A4): [Monitoring](https://code.claude.com/docs/en/monitoring-usage), [Manage costs effectively](https://code.claude.com/docs/en/costs), [Langfuse Observability Plugin for Claude Code](https://github.com/langfuse/Claude-Observability-Plugin)
- 스킬·서브에이전트(A5): [Extend Claude with skills](https://code.claude.com/docs/en/skills), [Agent Skills specification](https://agentskills.io/specification), [Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- 훅(A6): [Hooks reference](https://code.claude.com/docs/en/hooks), [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide)
- 플러그인(A7): [Create a Claude Code plugin](https://code.claude.com/docs/en/plugins/create), [Install and manage plugins](https://code.claude.com/docs/en/plugins/install), [Plugin security and trust](https://code.claude.com/docs/en/plugins/security), [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference), [Measure plugin cost and usage](https://code.claude.com/docs/en/plugins/measure)
- 비용·캐시·상태줄(A9): [How Claude Code uses prompt caching](https://code.claude.com/docs/en/prompt-caching), [Customize your status line](https://code.claude.com/docs/en/statusline), [Checkpointing](https://code.claude.com/docs/en/checkpointing), [Output styles](https://code.claude.com/docs/en/output-styles)
- 작업 루틴(A8, A10): [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices), [Keep Claude working toward a goal](https://code.claude.com/docs/en/goal), [Commands](https://code.claude.com/docs/en/commands), [CLI reference](https://code.claude.com/docs/en/cli-reference)
