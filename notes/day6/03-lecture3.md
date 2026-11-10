## 6일차 3강 — Claude Code 훅(Hook) 생애 주기별 활용법

> 출처: 「6일차 3강 다시보기」(전사·분석, 46:40 분량), 「6일차 3강 장표 (보정)」(15장). 이후 「6일차 3강 다시보기 (보정)」·「6일차 3강 장표 (보정2)」와 재대조해 확인 필요 항목을 반영했다. SDS AX Advanced · 2026-11-09.
> 대응 저장소: `Day06_new/` — 훅 근거 대장 `docs/sources/claude_code/03_control.md`(C13~C21), 훅 시작 틀 `use_cc/lab/hook_templates/`. 강의는 이 자료를 따라가지 않고, 강사가 에이전트 루프 그림을 그리며 공식 훅 문서를 훑고 활용 아이디어를 말로 풀었다. 코드 시연은 없다.

### 핵심 요약 (3~5줄)
- 강사는 Claude Code Harness에서 **메모리 다음으로 중요한 것이 훅**이라고 했다. 훅을 얼마나 잘 다루느냐가 에이전트의 안정성을 가장 크게 좌우하고, 다른 사람과 Claude Code로 협업할 때도 중요하다. 훅은 "프로그램을 제어하는 것", 즉 에이전트 루프의 특정 시점에 끼어들어 내가 원하는 프로그램(스크립트)을 실행시키는 장치다.
- 루프 순서대로 SessionStart → UserPromptSubmit(**모델에 전달되기 전**) → Stop/StopFailure → PreToolUse/PostToolUse → SubagentStart/SubagentStop → PreCompact/PostCompact → Notification을 짚었다. SessionEnd는 정상 종료가 드물어 거의 발동하지 않으므로 다루지 않는다.
- **"모든 훅 제어 중에 툴 전후가 제일 중요합니다."** PreToolUse에서는 위험 명령 검증(작은 모델로 yes/no)과 "그만큼 읽어야 하나"를 따지고, PostToolUse에서는 읽은 내용을 모델에 다 보낼지 요약할지, 로깅을 강제할지 고민한다. 관점은 일관되게 **컨텍스트 절감**이다.
- SubagentStop에서 **검증 서브에이전트를 강제로 호출**해 메인은 검증까지 끝난 결과만 받고, PreCompact/PostCompact로 요약 지침을 만들고 요약을 파일로 남긴다. Notification은 알림 전송을 넘어 다른 AI가 자동으로 대답하게 할 수도 있다.
- 결론: 훅의 본질은 이벤트를 잡아 **코드(command)를 실행**하는 것이다. "그걸 언제 필요한지만 결정하시면 됩니다." 조합은 점심(1시) 뒤 오후에 다룬다.

### 주요 개념 (개념별 설명, 강사가 강조한 이유 포함)

**1. 훅 = 에이전트 루프에 끼어드는 자리 (00:00~02:39)**
- "이 훅은 프로그램을 제어하는 거예요." 에이전트 루프가 어떤 작업을 실행할 때 "너 이때 잠깐 끼어들게 해줄게, 아니면 내가 돌 때까지 기다려"라고 공간을 허용해 주는 것이 훅이다.
- 공식 문서에서 "훅"을 검색하면 나오는 **훅 참조** 페이지는 "정말 촘촘하게 잘 작성되어 있"지만 "이것만 봐서는 하나도 이해가 안 됩니다." 그래서 루프 그림 위에 놓고 봐야 한다(강사는 같은 동그라미 루프 그림을 반복해서 그렸다).
- 강조 이유: 훅 설계가 에이전트 안정성과 협업의 핵심이기 때문.

**2. 루프 위의 훅 발동 시점 (02:39~07:42)**
- **SessionStart**: `claude` 명령 한 줄을 친 바로 그 순간. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:179)
- **UserPromptSubmit**: 프롬프트를 입력하고 엔터를 친 순간. "주의하셔야 되는 게 **모델에 전달되기 전**입니다… 전이에요, 전. 그게 되게 중요합니다." 이 시점에 무엇을 할 수 있는지가 여기서 갈리기 때문. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:180 — "When a prompt is submitted, before Claude processes it.")
- **Stop / StopFailure**: 모델 응답이 일반 텍스트면 끝났다(done)고 보고 Stop이 호출된다. 모종의 이유로 실패해 재시도 몇 번 끝에 멈추면 StopFailure. 성공이든 실패든 멈춘 뒤에는 모델 호출을 기다리는 상태. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:184, :189 — "per turn: UserPromptSubmit, Stop, and StopFailure") 공식 문서는 StopFailure를 "When the turn ends due to an API error"로 적는다(공식 문서 확인: https://code.claude.com/docs/en/hooks.md). 강의의 "재시도 끝에 멈춤"과 표현이 다르다.
- 부가 정보로, 프롬프트 캐시의 시간은 **모델에 전달된 직후(입력 때)부터** 잰다고 했다. 메타데이터는 최종 출력 뒤에 오지만 시간 측정은 그때부터라는 설명.
- **PreToolUse / PostToolUse**: 모델이 돌려주는 것은 텍스트 아니면 도구 호출 요청 두 가지이고, 도구 호출은 호출 전·후 두 지점에서 제어한다. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:181-182)
- **SubagentStart / SubagentStop**: 도구 중 "특별한 도구"가 서브에이전트 호출이라 시작·종료 훅이 따로 있다. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:185 — SubagentStop)

**3. 문서의 훅 이벤트 목록 훑기 (07:44~13:36)**
- 공식 문서의 훅 이벤트 표를 위에서부터 읽으며 소개했다: SessionStart, Setup("배우지 않았으니" 넘어감), InstructionsLoaded(역시 넘어감), UserPromptSubmit, **UserPromptExpansion**(사용자가 입력한 명령이 Claude에 도달하기 전에 프롬프트로 확장될 때, "너무 복잡해서" 잘 안 다룸), **메시지 디스플레이**(어시스턴트 메시지가 스트리밍되는 동안 = AI가 출력 중일 때, 가로챌 수도 있음), PreToolUse, **PermissionRequest**(도구 호출 때 권한 확인), PostToolUse, PostToolUseFailure, **PermissionDenied**(오토 모드에서 거부가 날 때), Notification, SubagentStart/Stop, Task(복잡해서 생략, 서브에이전트로 다 훅을 친다), Stop/StopFailure.
- "자주 쓰시진 않는" 것들: TeammateIdle, ConfigChange, 폴더 변경·디렉터리 추가, 파일 변경, 워크트리 생성·삭제, 컴팩트 전·후, 모델 변경 전·후, 세션 종료, **Elicitation**(MCP 서버와 통신할 때 필요).
- 공식 문서 이름: `Setup`, `InstructionsLoaded`, `UserPromptExpansion`, `MessageDisplay`, `PermissionRequest`, `PermissionDenied`("When auto mode denies a tool call"), `PostToolBatch`, `TeammateIdle`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`, `PreModelSwitch`, `PostModelSwitch`, `Elicitation`, `ElicitationResult`, `SessionEnd` (공식 문서 확인: https://code.claude.com/docs/en/hooks.md). 강의에서 말한 "폴더 체인지·디렉토리 추가"는 `CwdChanged`·`DirectoryAdded`, "모델 바꾸기 전/후"는 `PreModelSwitch`·`PostModelSwitch`에 대응하는 것으로 보인다(대응은 추정).
- 문서 후반에는 훅 제어 방식과 **프롬프트 기반 훅·에이전트 기반 훅**도 있으나 "잘 쓰지 않는 것 같아요."
- 생애 주기 관점에서 많이 쓰는 것만 추렸다. 그 밖에 필요한 훅은 문서에서 찾아 쓰면 된다.
- **SessionEnd를 빼는 이유**: 그레이스풀 셧다운을 하는 경우가 거의 없고 "그냥 이렇게 바로 꺼버리"기 때문에 잘 발동하지 않는다. 필요하면 쓸 수는 있다.

**4. SessionStart — 메모리·스킬 강제 주입 (14:17~17:28)**
- 세션 시작 때는 메모리(앞 시간에 다룬 내용)가 기계적으로 로드된다. 그 밖에 **특정 스킬을 강제로 로드**하거나, MEMORY.md 말고 추가로 넣을 내용, **이전 세션에서 쓰던 내용**을 넣어 세션을 이어갈 수 있다.
- 대표 사례 **claude-mem**(이전 전사 '클로드맵', 보정본에서 claude-mem으로 확정): Claude 세션 옆에 메모리를 따로 서버로 띄워 관리하고, 세션 시작 때 주입한다. "주입하려면 강제로 코드가 실행이 돼야 되잖아요. 그때 사용하는 대표적인 훅이 세션 스타트입니다." 강사는 "엄청 좋아서 소개하는 건 아니고" 대표 사례라고 했다. (저장소 확인: Day06_new/info.md:11 — https://github.com/thedotmack/claude-mem/) claude-mem README는 worker를 "a local HTTP service managed by Bun"으로 두고 SessionStart·UserPromptSubmit·PostToolUse·Stop·SessionEnd 등 여러 훅에 연결한다(공식 문서 확인: https://github.com/thedotmack/claude-mem).
- 소스 코드에서 훅을 정의한 구간을 찾아보면 동작을 알 수 있지만, 여러 플랫폼을 지원하면서 코드를 숨겨 놔서 찾기 귀찮다.
- 정리: SessionStart와 세션 종료를 **연동**해 **메모리 강제 주입**을 할 수 있다.
- 공식 문서 기준 SessionStart의 일반 텍스트 stdout은 Claude의 맥락에 더해진다. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:288)

**5. UserPromptSubmit — 프롬프트 가로채기 (17:29~21:51)**
- 보안·보완: 개인정보 **디텍션 후 치환(redact)**.
- **보강(증강)**: "이게 가장 많이 하는 작업인 것 같아요." 모델 직전에 프롬프트를 가로채 내 규칙대로 보강한다. 예) 한 줄짜리 지시를 촘촘한 프롬프트로 만들고, 구체적 지침이 없으면 사용자에게 써 달라고 요구하거나 임의로 보강. 비속어 제거 같은 것도 가능.
- **여러 AI 동시 호출**: Claude 기준 작업을 Codex·Gemini(Antigravity)에도 똑같이 지시해 결과를 비교한다. "물론 굉장한 토큰 낭비예요." 작업이나 계획을 세울 때 여러 AI 의견을 같은 프롬프트로 보고, 서로 놓친 점을 보강하는 데 많이 썼다. 시간 측정 목적은 아니고 "다양한 AI들의 의견 청취".

**6. PreToolUse / PostToolUse — 가장 중요한 훅 (21:51~29:25)**
- PreToolUse(도구 사용 전, 도구는 이미 선택돼 넘어온 상태):
  - 쓰면 안 되는 명령을 쓰는지 **검증**. 지금은 Claude 권한(permission)으로 제어할 수 있고, 권한 기능이 생기기 전에 훅으로 제어하던 "되게 오래된 사례"다.
  - 검증을 넣으면 느려지므로 작은 모델로 빠르게 돌려 **yes/no만** 받는다. 강사는 이 검증 절차를 **jev**로 한다("저는 이 검증이라는 절차를 jev로 해요 … 빨리빨리 돕니까", 보정본). "yes가 80%를 못 넘는다 그럼 의심하게 만드는" 식.
  - 수강생 의견으로 **순차(sequential) 호출 순서 제어**도 나왔다.
  - 컨텍스트 관점: "**그거 그만큼 읽어야 돼?**" Read 도구가 문서를 1~200줄 읽으려 할 때 정말 그만큼 필요한지 먼저 묻는다. 사례로 Spotify가 Opus 대신 Haiku에게 읽기를 맡겨 IO를 줄이고 메인 토큰을 아꼈다고 했고, 지난주에 디시전 모델(jev)로 줄이는 고민을 했던 것과 연결했다.
- PostToolUse(이미 실행된 뒤):
  - 권한 검증·순서 제어는 이미 돌았으니 의미가 없다. 재수행은 어느 정도 알아서 해 준다. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:300-301)
  - "**모델에 다 보낼 필요가 있을까**" — 읽은 결과는 아직 모델에 가기 전이므로 요약해서 보내는 식으로 컨텍스트를 줄인다. 모델이 무엇을 보려 했는지 추측하기는 어렵다. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:303 — 원래 출력을 바꾸려면 `updatedToolOutput`)
  - 쓸 내용이 더 많다: 어떤 도구가 호출되면 항상 이 툴/스크립트를 실행하도록 **매처(matcher)**로 설정. 예) 내가 만든 하네스에서 Read를 쓰면 항상 요약하거나 기록을 남기게 해 **로깅을 강제**하고, 그 로그로 개선한다. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:197 — "The matcher field filters when hooks fire.")

**7. 훅은 코드를 실행한다 (29:49~30:54)**
- 앞의 아이디어(예: UserPromptSubmit에서 Codex와 Antigravity에 같은 프롬프트 실행)가 실제로 어떻게 돌까? "코드로 실행시킵니다."
- 훅 설정에 들어가 보면 **command** 메뉴가 있고, 이것이 내 PC에서 스크립트를 실행하는 것이다. 이벤트가 발행되면 그 이벤트를 캐치해 프로그램을 실행한다. (저장소 확인: Day06_new/use_cc/lab/hook_templates/settings_example.json:8 — `"type": "command"`) 공식 문서의 핸들러 `type`은 `command`, `http`, `mcp_tool`, `prompt`, `agent`(실험적)이다(공식 문서 확인: https://code.claude.com/docs/en/hooks.md).

**8. SubagentStop — 검증 강제 호출 (30:57~36:44)**
- SubagentStart에서는 할 일이 별로 없다(프로세스가 잘 떴는지 정도는 Claude가 해 준다).
- 서브 3개, 메인 1개가 있을 때, 서브들이 "형님 끝났습니다"라고 보고하면 메인이 1번·2번·3번에게 잘했냐고 하나하나 검토를 또 시켜야 한다. 그러기 싫고 "보고만 받고 싶어요."
- 그래서 서브 실행이 끝나면 **검증하는 서브를 강제로 부른다**. "강제로 호출시키는 게 중요해요. 우리는 검증이라는 프로세스를 강제시키는 겁니다." 메인은 "**검증까지 다 끝난 결과를 받는 거예요**." 예) 1~5번 작업을 다 했는지 확인하는 정도는 어렵지 않다. 문제가 있으면 해결하도록 지시하거나, 보고하고 다시 지시받을 수도 있다.
- 컨텍스트 관점: 서브가 길게 쓴 결과를 메인이 다 봐야 하나? 중요한 내용만 전달하고 "나머지는 문서에 있습니다"라고 해서 보게 만든다.
- 공식 문서 기준 SubagentStop은 exit 2로 서브에이전트가 멈추는 것을 막을 수 있다. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:218)

**9. PreCompact / PostCompact — 요약 지침과 요약 파일 (36:44~42:37)**
- 서브에이전트 훅과 같이 묶은 이유: 비슷한 일(요약·전달)을 하기 때문.
- 컴팩트 명령에는 **optional custom summarization instructions**가 있어 요약 때 주의할 내용을 지시할 수 있다. (저장소 확인: Day06_new/docs/sources/claude_code/04_state.md:66 — `/compact focus on the API changes`)
- PreCompact: 지시하기 전에 세션에서 중요한 작업이 무엇이었는지 빠르게 확인한다. 강사는 "작업 시작·결과만 보도록, 중간 툴 호출 같은 건 볼 필요 없고", 마지막에 **요약 형식을 정해 줬다**(Claude 기본 요약 형식이 마음에 들지 않았다). 작은 모델(Haiku)로 훑으면 한 줄씩 3~4줄과 레퍼런스를 달아 주고, 그걸 Opus가 보고 지시문을 촘촘하게 써서 컴팩트에 넣는다. "오토 컴팩이 아니라 제가 컴팩을 시키는" 방식으로 전후를 감싼다. 공식 문서는 PreCompact의 stdout이 요약 지시가 된다고 적는다(공식 문서 확인: https://code.claude.com/docs/en/hooks.md — "your stdout becomes instructions for the compaction summary"). matcher 값은 `manual`·`auto`.
- PostCompact: 요약을 바로 컨텍스트로만 넘기지 말고 **파일로 남기게** 한다. 왜? "제가 볼려고." 컴팩트가 내가 원하는 대로 됐는지, 중요한 작업이 맞았는지, 요약 형식을 지켰는지 확인한다. "컴팩트로 맨날 이렇게 날리면 하나도 안 남습니다."
- **컴팩트 강제**: Stop에 걸어 명령이 끝날 때 사용률이 60~65%면 모니터링을 시작하고 상태 줄(status line)에 "얼마 안 남았다, 컴팩 해야 돼"를 띄운다. UserPromptSubmit에서 요청 직전에 **80%를 넘으면 요청을 보내지 않고** 가로채서 컴팩트를 먼저 돌린 뒤 다시 보낸다. 다른 예로 "세션이 70% 차면 강제로" 동작하게 할 수도 있다. 어디에 거느냐는 정해져 있지 않고 여러 군데에 심을 수 있다. "프로그램으로 그 정도 제어하는 거 어렵지 않잖아요. 그리고 짜 달라고 하면 되고요." 상태 줄 스크립트가 받는 사용률 필드는 `context_window.used_percentage`다(공식 문서 확인: https://code.claude.com/docs/en/statusline.md).
- 공식 문서 기준 PreCompact는 exit 2로 컴팩션을 막을 수 있다. (저장소 확인: Day06_new/docs/sources/claude_code/03_control.md:219)

**10. Notification — 알림과 자동 응답 (42:53~45:42)**
- Claude가 알림을 줄 때(질문, 멈춤, 끝났다, 도구 실행 전 퍼미션 승인 요청, AskUserQuestion 등) 발동한다. 문서상 Notification은 "어디서나 발생"할 수 있다.
- 알림을 회사 메신저·Slack·메일로 보내는 건 "너무 쉬운 작업"이다. 강사는 한 단계 더 나아가 **자동으로 대답해 주길** 원한다. 방법은 여러 가지: Computer Use(이전 전사 '컴퓨터 유지', 보정본에서 확정)나 CLI에서 억지로 제어, 다른 Claude·Codex·Antigravity가 대신 대답.
- 맥북 등에서 사용량(얼마 썼고 언제 리셋되는지)을 보여 주는 도구들(강사가 든 이름: "codex menu가였나" — 보정본)도 Notification이나 Stop 훅에 걸어 정보를 계속 갱신한다.
- 공식 문서의 Notification matcher 값에는 `permission_prompt`, `idle_prompt`, `elicitation_dialog`, `agent_needs_input`, `agent_completed` 등이 있다(공식 문서 확인: https://code.claude.com/docs/en/hooks.md).

### 실습/데모 내용 (명령어, 파일 구조, 프롬프트, 코드 조각 등 원문 그대로 보존)
- 별도의 코드 실습은 없었다. 강사가 화이트보드에 루프를 그리고, 공식 문서 「훅 참조」 페이지의 이벤트 표를 확대해 훑었다.
- 루프 그림(장표 순서):
  ```
  claude 실행 → SessionStart
  → (입력 후 엔터) UserPromptSubmit   ※ 모델 전달 "전"
  → 모델 → 텍스트 응답이면 Stop / 실패해 멈추면 StopFailure
         → 도구 호출이면 PreToolUse → (도구) → PostToolUse
         → 특별한 도구(서브에이전트) SubagentStart → SubagentStop
  (컴팩트) PreCompact → PostCompact
  (어디서나) Notification
  (거의 발동 안 함) SessionEnd
  ```
- claude-mem 데모: 왼쪽에 Claude 세션, 별도 메모리 서버 화면을 띄워 SessionStart 때 주입된다고 보여 줬다(작동 화면은 짧게).
- UserPromptSubmit 동시 호출 예의 결과 파일 이름(원문): "코덱스 플랜.md로 써놓게 하고 안티 플랜.md 요렇게" — 답변을 **파일로** 쓰게 해야 "이 프로세스의 제어를 안 받으니까". 프로그램만 실행해 놓고 끝낸다.
- PreToolUse 읽기 점검 예(원문 요지): Read가 "어떤 문서를 1번부터 200줄까지 읽는 거죠. 아 굳이 그만큼 읽어야 될까."
- 컴팩트 지시 항목(원문 화면 문구): `optional custom summarization instructions`
- 컨텍스트 사용률 기준(원문 수치): Stop에서 **60%**(또는 65%)부터 모니터링 → UserPromptSubmit 직전 **80%** 넘으면 요청 보류·컴팩트 먼저 → 재전송. 예시로 "70% 차면 강제로"도 언급.

### 강사 팁·주의사항
- UserPromptSubmit은 모델에 **전달되기 전**에 발동한다. 여기서 할 수 있는 일(치환·보강·차단)이 그래서 가능하다.
- 공식 훅 문서는 촘촘하지만 그것만 보면 이해가 안 된다. 루프 그림 위에 놓고 "언제 발동하나"로 읽어라.
- "모든 훅 제어 중에 툴 전후가 제일 중요합니다."
- 훅으로 검증을 넣으면 느려진다. 작은 모델로 yes/no만 받게 해 속도를 지킨다.
- PostToolUse에서 권한 검증은 의미 없다. 이미 실행됐다.
- 여러 AI 동시 호출은 토큰 낭비가 크다. 계획 세울 때처럼 놓친 점을 보강할 가치가 있을 때만.
- 서브에이전트 결과 검증은 메인에게 맡기지 말고 SubagentStop에서 **강제**한다.
- 컴팩트 요약은 파일로 남겨 직접 확인한다. 기본 요약 형식에 맡기지 말고 형식을 정해 준다.
- SessionEnd는 실제로 잘 발동하지 않는다(대부분 그냥 꺼 버리므로). 종료 처리를 여기에 기대지 말 것.
- 훅 구현 자체는 어렵지 않다. "내가 어떤 기능이 필요한데, 클로드에 언제 이게 동작했으면 좋겠다"만 결정하면 된다.
- 과제: 자신에게 필요한 기능이 Claude Code의 어느 시점에 동작해야 하는지 정해 보기. 점심 1시까지, 오후에 조합.

### 실제 프로젝트에 적용할 체크리스트 (- [ ] 행동 지침, 특정 프레임워크에 묶이지 않는 원칙 위주)
- [ ] 에이전트 루프를 그림으로 그리고, 각 단계(세션 시작·입력 제출·도구 전/후·서브에이전트 종료·컴팩트 전/후·알림·멈춤)에 끼어들 수 있는 지점을 표시한다.
- [ ] 원하는 기능마다 "언제 동작해야 하는가"를 먼저 정하고, 그 시점의 훅에 스크립트로 건다.
- [ ] 입력 제출 훅이 모델 전달 **전**인지 확인하고, 개인정보 치환·프롬프트 보강·요건 누락 시 사용자에게 되묻기를 여기에 둔다.
- [ ] 도구 실행 전 훅에서 위험 명령을 검증하되, 느려지지 않게 작은 모델이나 결정적 규칙으로 yes/no만 받는다.
- [ ] 읽기 도구 호출 전에 "정말 그만큼 읽어야 하나"를 점검하고, 읽은 뒤에는 모델에 원문을 다 보낼지 요약할지 정한다.
- [ ] 도구 실행 후 훅은 차단이 아니라 요약·기록·피드백 용도로 쓴다(이미 실행됐다는 전제).
- [ ] 특정 도구가 호출되면 항상 로깅 스크립트가 돌도록 매처를 걸고, 그 로그를 개선 근거로 쓴다.
- [ ] 서브에이전트가 끝나면 검증 단계를 자동으로 강제해, 메인은 검증된 결과와 핵심 요약만 받게 한다. 긴 결과는 문서로 남기고 경로만 넘긴다.
- [ ] 컴팩트 전에 중요 작업과 요약 형식을 지시문으로 만들어 넣고, 컴팩트 후 요약을 파일로 남겨 사람이 확인한다.
- [ ] 컨텍스트 사용률을 응답 종료 때마다 감시하고, 임계치(예: 60~65% 경고, 80% 초과 시 요청 보류)를 넘으면 요청 전에 압축을 먼저 돌린다.
- [ ] 알림 이벤트를 외부 채널로 보내고, 반복되는 질문·승인 요청에는 자동 응답을 검토한다.
- [ ] 세션 종료 이벤트에 중요한 정리 작업을 의존하지 않는다(비정상 종료가 대부분).
- [ ] 여러 모델에 같은 계획을 동시에 맡길 때는 결과를 파일로 남기게 하고, 비용을 감수할 만한 단계(계획 수립)에만 쓴다.

> 확인 필요:
> - 08:24 "Setup", "InstructionsLoaded" 훅은 강사도 "배우지 않았다"며 넘어갔다. 문서 정의는 위 3절 공식 문서 링크 참고.
> - ~~15:07 '클로드맵'은 claude-mem으로 추정된다(저장소 확인: Day06_new/info.md:11에 claude-mem 링크가 있음). 강의 화면의 프로젝트가 같은 것인지는 화면으로 확인하지 못했다.~~ → 해결(보정본): claude-mem.
> - 19:00~20:00 UserPromptSubmit에서 "또 하나 더 할 수 있는 것"을 묻는 부분의 전사가 끊겨 있다. 이어서 Codex·Antigravity 동시 호출 사례로 이어진다.
> - ~~22:49 "검증이라는 절차를 제보로 해요"는 작은 모델(또는 jev)로 빠르게 검증한다는 뜻으로 보이나 불확실하다.~~ → 해결(보정본): "검증이라는 절차를 jev로 해요". 단 "yes가 80%를 못 넘는다 → 의심" 기준의 정확한 맥락(무엇의 80%인지)은 보정본에서도 불분명하다.
> - 25:06 Spotify가 Haiku로 읽기를 맡겨 IO를 줄였다는 사례는 짧게만 언급됐다. 출처는 말하지 않았다.
> - ~~25:50 "제브라는 그 디시저 모델"은 5일차에 다룬 디시전 모델 jev로 보인다.~~ → 해결(보정본): "jev라는 그 디시저 모델".
> - 05:15~06:04 프롬프트 캐시 시간을 "모델에 전달된 직후(입력 때)부터" 잰다는 설명은 강사 발언이며 공식 문서로 확인하지 않았다(미확인).
> - 09:08 "메시지 디스플레이" 훅은 공식 문서의 `MessageDisplay`("While assistant message text is displayed")로 보인다. 강의는 "가로챌 수도 있다"고 했으나 이 훅의 제어 가능 범위는 확인하지 않았다(미확인).
> - 10:37 "PermissionDenied는 오토 모드일 경우에 발생"은 공식 문서와 일치한다(공식 문서 확인: https://code.claude.com/docs/en/hooks.md).
> - ~~43:22~44:07 "컴퓨터 유지"는 Computer Use로 추정된다.~~ → 해결(보정본): Computer Use.
> - ~~44:50 맥북 사용량 체크 도구 이름이 "코덱스 메뉴가"로 들리나 정확한 이름을 알 수 없다.~~ → 해결(보정본): "codex menu"(강사 자신도 "codex menu가였나"라고 확신하지 않음).
> - 강의 중 실제 훅 설정 파일이나 스크립트를 열어 보이지는 않았다. 오후 조합 실습에서 구체 코드가 나올 것으로 보인다.
