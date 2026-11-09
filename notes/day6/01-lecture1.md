## 6일차 1강 — 하네스 수업 도입과 Claude Code 환경 구성: 웹·앱·CLI 비교, .claude 폴더와 settings.json

> 출처: 「6일차 1강 다시보기 (보정)」(전사·분석, 48:24), 「6일차 1강 장표 (보정)」(16장). SDS AX Advanced · 2026-11-09 (2주차 첫날 오전 앞부분).
> 이 강의는 Claude Code 화면·공식 문서·강사 PC의 `~/.claude` 폴더를 띄워 놓고 말로 설명한 시간이다. 대응 저장소 폴더는 `Day06/`(이론 PDF, 공개 하네스 목록)과 `Day06_new/`(Claude Code 실습)이지만, 강의에서 실제로 연 것은 공식 문서와 강사 PC 화면이고 실습 폴더는 열지 않았다.

### 핵심 요약 (3~5줄)
- 오늘(6일차)은 **하네스를 Claude Code 위주로 세팅하는 날**이다. 목·금 프로젝트와 해커톤의 "근간이 되는 환경"을 만들고, 공개된 하네스를 설치·테스트해 **자신만의 하네스**를 구축한다. 오전 이론 → 점심 후 이론 정리·환경 세팅·플러그인 안내 순서.
- 기능이 궁금하면 **공식 문서**를 보라. 문서의 "질문하기"(하단)·"어시스턴트에게 묻기"(상단)를 쓰고, 한국어 문서의 **핵심 개념 메뉴 5개**(작동 방식, 확장, .claude 디렉토리, 컨텍스트 윈도우 등)는 최소한으로 공부하더라도 꼭 읽는다. 프롬프트 캐싱은 "오늘이나 내일 제일 중요한 내용".
- 웹의 Code는 클라우드 전용(GitHub 연동 필수)이라 거의 안 쓰고, 앱과 CLI는 큰 차이가 없다. 앱은 아티팩트·예약 작업·브라우저·iOS 시뮬레이터·그래픽 표시가 강점이지만 Electron이라 무겁고, CLI는 자원 효율·커스텀·SSH 원격에 유리하다.
- 모든 설정은 홈 폴더의 **`.claude`**(글로벌)에서 출발하고 프로젝트 레벨 설정이 따로 있다. 특히 **projects/…/memory**(프로젝트 메모리)는 **각자 PC에만 저장**되어 "같은 Claude인데 왜 체감이 다르지"의 원인이 되고 협업에 불리하다.
- **전역 스킬은 어디서 켜든 다 로드**되므로 공통으로 쓰는 것만 두고, **settings.json**(env·permissions deny·모델·effort·status line·advisor 등)은 PC를 옮길 때 **직접 들고 가야** 한다.

### 주요 개념 (개념별 설명, 강사가 강조한 이유 포함)

**1. 오늘의 자료 (01:59~)**
- PDF 3개. **"이론 자료"** PDF가 메인 교재. "자료는 항상 거들 뿐이고요."
  - (저장소 확인: 같은 계열 교재가 `Day06/Day6_Agent_Harness_이론자료.pdf`로 있음 — 표지 "Agent Harness / 서비스 개발 사례로 배우는 실행·검증·수정의 구조 / 지침 · 도구 · 실행 제어 · 상태 · 검증 · 기록", p.1. 이 강의에서는 PDF 본문을 넘겨 보지 않았다.)
- 참고 논문 ①: "말도 많고 탈도 많은" **하네스 엔지니어링이 대체 뭔가를 잘 정리한 논문**(8월쯤 나온 것). 남들이 하네스를 어떻게 이해·정리하는지 보고 싶거나 설명이 애매하게 와닿을 때 참고.
- 참고 논문 ②: **Context as an Environment**(알리바바 테크니컬 리포트). 오래 도는 에이전트에서 **프로그래매틱 컨텍스트 매니지먼트**를 어떻게 할지. 강사: 컨텍스트 매니지먼트 쪽은 "중국 쪽이 미국 쪽보다 훨씬 더" 논문·실질 해결책을 잘 낸다.
- 강조 이유: 내일 로컬 LLM을 공부하는 이유도 결국 "에이전트가 원하는 작업을 잘 하도록 **컨텍스트를 넣어주고 빼주고 관리**"하는 문제와 연결된다.

**2. Claude Code 공식 문서 활용법 (05:33~)**
- 문서 **하단 "질문하기"**, **상단 "어시스턴트에게 묻기"**(오른쪽 사이드에 띄워 놓고 읽으면서 묻거나 "읽기 귀찮으니까 시켜보면서"). 작동 방식, 에이전트 루프 같은 것을 꼼꼼히 이해하는 데 쓰라.
- 한국어 문서 기준 **"시작하기 > 핵심 개념"** 메뉴 5개: "이 다섯 개의 메뉴는 다른 건 다 안 읽으셔도 진짜 정말 정말 최소로만 공부하겠다. 그럼 이 다섯 개는 꼭 읽어주셔야 됩니다."
  - 작동 방식, Claude Code 확장(스킬·훅 등), `.claude` 디렉토리(무엇이 어디 있고 설정이 어디 들어가는지 — 계속 업데이트됨), 컨텍스트 윈도우 등.
- **컨텍스트 윈도우 그래픽**: 세션이 어떻게 차는지를 그래픽으로 보여 준다(수정은 안 되고 클릭만 됨). 내 프롬프트가 들어가고, Claude가 입력하는 컨텍스트가 무엇이고 어떤 순서로 들어가는지, 그래서 명령을 어떻게 넣어야 하는지 이해하기 쉽다. "이따 같이 볼 거예요." (공식 문서 확인: https://code.claude.com/docs/en/context-window.md — "An interactive simulation of how Claude Code's context window fills during a session")
- **프롬프트 캐싱** 문서도 같은 곳에서 다룬다 — "오늘이나 내일 제일 중요한 내용". 오늘은 자료·공식 문서·Claude에게 묻기 세 가지를 오가며 진행.

**3. Claude 웹의 구성, 커넥터 vs 플러그인 (09:12~)**
- Claude 웹 왼쪽 상단은 **Claude**와 **Code** 두 버튼(윈도우와 보이는 모습이 조금 다름). Claude 쪽에 예전 **코워크(Cowork)**가 포함됐고, **팀 플랜 담당자가 코워크를 켜고 끌 수 있다**(아예 안 주거나 주거나). → 코워크·챗·코드 세 가지.
- 챗의 + 버튼: 스킬, 커넥터, 디자인 시스템, 플러그인, 기기 추가, 리서치, 메모리.
- **커넥터** = 챗에서 Google Drive·Slack·Notion·Figma 등을 연동할 때. **플러그인** = Claude Code의 플러그인. Vercel처럼 **같은 이름이 둘 다 있는 경우**가 있어 헷갈리는데 "**챗용이냐 코드용이냐만 나눠 보시면 됩니다.**"
- 디자인 시스템: PPT·웹사이트를 구성할 때 미리 입력해 두고 쓰는 기능. Claude에서 PPT·엑셀도 만들 수 있다.

**4. 웹의 Code, 앱 vs CLI (14:28~)**
- 웹의 Code는 "거의 하실 수 있는 게 없다": 내 컴퓨터가 아니라 **클라우드에서** 돌아 GitHub 등을 **무조건 연동**해야 하는 불편함. "웹은 이제 앱의 하위 호환", "기억 속에서 지워버리고".
- 앱만의 기능: (클라우드 실행 환경도 선택 가능), **아티팩트 관리**(CLI는 불가), **예약된 작업**(어떤 기능으로·어느 환경에서·이 컴퓨터에서만 할지 등 결정), 오른쪽 상단 **브라우저·폴더·iOS 시뮬레이터** 지원, 컨텍스트·서브에이전트 동작을 **그래픽으로** 보기 쉬움. "생각보다 잘 만들어져 있어요 … 여기서만 작업을 하시는 경우도 되게 많습니다."
- 앱 단점: **Electron 기반이라 무겁다**(바꾸고 있다고 들었다).
- 결론: "앱이랑 CLI는 엄청 크게 차이가 나진 않아요." CLI는 **자원 효율**이 좋고 부가 기능 없이 **커스텀하기 좋다**.
- CLI에도 **보이스 모드**가 있다(앱에만 있다고 오해하는 사람이 많음). 강사는 이동 중 헤드폰으로 말로 많이 시킨다. (공식 문서 확인: https://code.claude.com/docs/en/settings-reference.md — `voice` "Turn on voice dictation and pick hold or tap mode")
- CLI 커맨드로 **Fast 모드**를 껐다 켰다 할 수 있다(앱에서는 "안 되는 걸로 알고 있는데" — 강사도 확신 못 함). (공식 문서 확인: https://code.claude.com/docs/en/settings-reference.md — `fastMode` "Turn fast mode on for sessions where it's available … speed at a higher cost per token")
- **릴리즈 노트**를 띄워 놓고 Claude에게 "업데이트 된 게 뭔데, 그중에 내가 필요한 거" 물어보면 잘 대답한다. (공식 문서 확인: https://code.claude.com/docs/en/claude-directory.md — `cache/changelog.md` "Cached copy of the Claude Code changelog, shown by `/release-notes`")

**5. 여러 컴퓨터 제어 (21:37~)**
- 앱: 상대 컴퓨터에도 **앱이 설치**돼 있어야 하고, 그쪽에서 내 Claude 계정에 로그인하면 명령 가능. 앱은 "그냥 클로드만" 쓸 수 있다.
- CLI: **SSH만 열려 있으면**(그쪽에도 Claude Code CLI는 설치) 접근 가능하고 여러 CLI도 쓸 수 있다.
- 공통: 상대 컴퓨터가 **켜져 있어야** 한다.
- 요즘 흔한 구성: 노트북은 들고 다니고, **작업 머신(Mac mini, 헤비하면 Mac Studio)**을 따로 둔다.

**6. 홈 폴더 `.claude` 구조 (24:17~)**
- "모든 클로드 설치는 … 홈 폴더 밑에 점 클로드로부터 출발합니다." CLI든 앱이든 같다. `.claude`는 **글로벌 설정**이고, 별도로 **프로젝트 레벨 설정**이 있다.
- 찾는 법: Claude에게 "내 홈 폴더 밑에 .claude 폴더의 위치가 어디냐" → 경로 → "그 경로 파일 탐색기로 보여줘". 강사는 VS Code로 띄워 설명. ("이런 건 오프스(Opus)를 쓸 필요가 없죠.")
- 폴더별 설명(강사 PC 기준):
  - `agents/`: 전역 에이전트 파일. 이 컴퓨터 어디서 Claude를 켜도 불려온다.
  - `backups`, 캐시: 프로그램용, 신경 안 써도 됨. `chrome`: Claude in Chrome 기능. `daemon`: 무시(강사 PC에만 있음).
  - `file-history`: 파일 수정 히스토리. "잔뜩 쌓여 있거든요. 나중에 용량 보시면 어마어마합니다." → **수시로 지운다**. Claude에게 "불필요한 것들 지워달라"고 해도 된다(Claude·Codex가 워낙 많은 작업을 해서 쓰레기 파일이 쌓인다).
  - `ide`: Claude가 인식하는 IDE 정보. `jobs`: 앱의 "예약된 작업". `paste-cache`: 복사한 캐시.
  - `plugins/`: 설치한 플러그인의 **원본** — "잘못 지우면 안 되는 거죠."
  - `projects/`: **"여기가 제일 중요합니다."** 폴더 경로를 **대시(-)로 바꾼 이름**으로 프로젝트별 폴더가 생기고(슬래시를 폴더명에 못 쓰니까), 그 안에 UID 기반 기록, 서브에이전트 생성 기록, 그리고 **memory**가 있다. (저장소 확인: `Day06_new/use_cc/CLAUDE.md:75` — "`~/.claude/projects/<작업 폴더 경로의 영숫자 아닌 글자를 -로 바꾼 이름>/<세션 ID>.jsonl`")
  - `session-env` 등 세션 데이터: 대부분 쓰레기 폴더라 가끔 지운다. 스냅샷류도 필요 없다.
- (공식 문서 확인: https://code.claude.com/docs/en/claude-directory.md — `file-history/<session>/` "Pre-edit snapshots of files Claude changed, used for checkpoint restore", `session-env/` "Per-session environment metadata"; 둘 다 `cleanupPeriodDays`(기본 30일) 지나면 자동 삭제 대상. 같은 문서: "Don't delete `~/.claude.json`, `~/.claude/settings.json`, or `~/.claude/plugins/`". 단, `file-history`를 지우면 "Checkpoint restore for past sessions"를 잃는다고 적혀 있다.)

**7. 프로젝트 메모리의 동작과 관리 (31:02~)**
- 구조: `projects/<프로젝트>/memory/` 밑에 **`MEMORY.md`**(목록, "어쩌고 저쩌고 MD문서 가라" + 짧은 설명)와 **개별 md 문서**. "요게 클로드가 프로젝트의 메모리를 관리하는 방식입니다." (저장소 확인: `Day06_new/docs/sources/claude_code/04_state.md:185` — "Each project gets its own memory directory at ~/.claude/projects/<project>/memory/")
- 제어 가능하다(내 컴퓨터의 문서니까). 직접 고치거나 Claude에게 시킨다. 방법: "메모리"라고 하지 말고 **"기억해"**, **"지워"**라고 지시.
- "재밌는 거 **욕하면 기억해요**." 사용자가 짜증 냈거나 좋아한 것, 프로젝트에서 반복되는 작업 등을 Claude가 능동적으로 판단해 기억한다. (강사가 "이따가 테스트 해보세요"라고 함)
- 강사는 자동으로 쌓이는 방식을 **선호하지 않는다** — "내가 뭘 기억하게 했는지 잘 몰라요." 그래서 **메인으로 보는 작업이면 무조건 직접 수정**한다.
- 예: 첫 줄 문서 `User Language Korean` — 영어로 자꾸 답해서 "야 한국어로 얘기해 앞으로" 했더니 기억함. 이걸 굳이 문서에 들어가 읽게 하는 건 "홉의 낭비", 목록에 한 줄 써 두면 될 일.
- **metadata type**: `user`(사용자가 지시한 것), `project`(작업하다 Claude가 중요하다고 판단한 것), `feedback`(사용자 피드백; original session id·수정 시각도 있음). 한국어/영어가 섞여 있기도 함.
- **강조점**: "이 메모리라는 것 자체는 **여러분들의 컴퓨터에만 저장되는 겁니다. 그래서 협업을 할 땐 안 좋아요.**" 교육용 PC를 새로 세팅하면 "같은 클로드인데 왜 내 거랑 체감이 달라" — "**요 메모리가 달라요.**" 이걸 모르면 "내 PC에서 잘 되는데 왜 쟤는 안돼요"가 된다 → 메모리를 계속 관리하면서 **다른 사람과 공유할 방법을 고민**해야 한다.
  - (저장소 확인: `Day06_new/docs/sources/claude_code/04_state.md:188` — "Auto memory is machine-local."; `Day06_new/use_cc/part3/concept.md:111` — "이 기계 안에만 있다 … 팀과 공유되지 않는다")

**8. 전역 스킬과 history.jsonl (37:49~)**
- `skills/`: 설치한 스킬이 보인다(강사 메인 PC: 브라우저 제어 스킬, 자기 프로그램이 올려 준 스킬, 다이어그램 디자인 스킬 등). 문제는 **글로벌이라 어디서 Claude를 켜도 다 로드**된다는 것. "그러니까 **공통으로 쓰는 거 아니면 여기다 두지 마세요.**"
- 예: 프로젝트마다 Python·Java·TypeScript로 언어가 다르면 전역에 언어별 스킬을 다 넣는 건 나쁘다 — **description이 길어지고 그것도 토큰**이다. 공통이 아닌 것은 프로젝트 쪽으로 나눈다. 또는 한 스킬(예: TypeScript 스킬)에서 **다른 스킬을 참조**하게 하나 만들어 두는 방식도 쓴다.
- 강사 PC는 전역 스킬을 대부분 정리해서 "이 사람 PC가 개발 PC가 맞나 싶을 정도로" 없다 — 다 프로젝트 폴더에 있다.
- **`history.jsonl`**: 업무 PC에 가서 꼭 볼 것. 직접 볼 일은 없다(강사 PC에선 너무 길다). 강사 설명: "내 PC에서 이 클로드를 사용할 때 했던 **대화기록이 모두 보관**", 나중에 Claude로 **내 작업을 리뷰**할 때 쓰기 좋고 관리 안 해도 알아서 관리된다.
  - **미확인(강의와 공식 문서 차이)**: 공식 문서는 `history.jsonl`을 "**Prompts you've typed**, with timestamp and project path. Used for up-arrow recall, `Ctrl+R` history search, and `!` shell-command completion"으로 설명하고, 대화 전체(메시지·도구 호출·결과)는 `projects/<project>/<session>.jsonl`에 둔다고 적는다. (공식 문서 확인: https://code.claude.com/docs/en/claude-directory.md) 강의의 "대화기록 모두"가 입력한 프롬프트만을 뜻했는지는 확인하지 못했다.

**9. settings.json 주요 설정 (41:38~)**
- "여러분들의 클로드 세팅의 모든 것" — Claude에 무언가 세팅하면 여기에 다 들어온다.
  - **`env`**: 환경 변수 로드(Langfuse 세팅할 때 본 것).
  - **`permissions`**: PC에 없을 수도 있다. 할 수 있는 작업은 상관없고 "**deny만 보시는 겁니다**".
    - 강사 예 ①: 쓸데없는 **아티팩트**를 자꾸 만들어서 막았다(그냥 html로 받고 싶음).
    - 강사 예 ②: 예전엔 **내장 웹서치**도 막았다 — "너무 후졌고 너무 오래 걸려요." 대신 1일차에 본 **Tavily·Exa** 같은 웹서치 API(무료 티어, 안 되면 약간 결제) 또는 웹서치 플러그인을 썼다. 요즘은 성능이 올라와 다시 쓴다("언제 또 삭제해 버릴 수 있습니다").
  - 기본 **모델**(예: Opus — "이따가 공부해 보실 거고요").
  - **status line**: CLI 화면 아래 회색 줄. Claude가 주는 정보 중 보고 싶은 것을 골라 표시, 완전 커스텀 가능. 강사는 **Claude에게 만들어 달라고** 해서 쓴다. (공식 문서 확인: https://code.claude.com/docs/en/settings-reference.md — `statusLine` "Run your own command to render a status line below the prompt")
  - 그 외: 플러그인, 마켓플레이스, output style, **effort 레벨 기본값**, **모델별 세부 세팅**(모델이 디폴트로 호출됐을 때 effort). (공식 문서 확인: https://code.claude.com/docs/en/settings-reference.md — `effortLevel` "Set a default effort level for models you haven't saved a level for", `outputStyle`, `enabledPlugins`, `extraKnownMarketplaces`)
  - `/config`로 하는 설정도 대부분 여기 들어간다. 시연 중 "아티팩트를 쓰지 말라는 기능이 이렇게 생겼네요" — 별도 키가 생겨 바로 `false`로 바꿈. (공식 문서 확인: https://code.claude.com/docs/en/settings.md — `enableArtifact` "`false` from any scope … nothing turns the Artifact tool back on", `disableArtifact`는 deprecated)
- **강조점**: "여러분들이 만약에 **pc를 여러 개를 쓰신다라고 하면 아쉽게도 이 settings.json을 가지고 가셔야 됩니다.** 글로벌이잖아요. 이거는 어디서도 복사 안 해주니까." (공식 문서 확인: https://code.claude.com/docs/en/settings.md — User scope `~/.claude/settings.json` "You, in every project on this machine")

**10. advisor 기능 (45:54~)**
- "어드바이저 꿀팁": 작업 중 **검토가 필요한 작업이 생기면 지정한 모델을 호출**. Claude가 **스스로 호출**하기도 하고 사용자가 **명시적으로 지시**할 수도 있다. CLI·앱 모두.
- 강사 화면에서는 advisor로 **Fable 5.1**이 선택돼 있었고, "이거 차감이 안 됩니다. **토큰 차감이 안 돼요**"라고 했다.
- 단점: **느려진다**(검토받는 동안). 장점: 결과가 **더 안정적이고 풍부**해진다. 강사는 계획 단계 등에서 많이 쓴다.
- (공식 문서 확인: https://code.claude.com/docs/en/advisor.md — 설정은 `/advisor` 명령, `advisorModel` 설정(예: `{"advisorModel": "opus"}`), `--advisor` 플래그. "Claude decides when to call it", 프롬프트로 `consult the advisor before you continue`처럼 요청 가능. advisor는 메인 모델 이상 등급이어야 함(예: Fable 5.1 메인 → Fable 5.2 또는 5.1 advisor).)
- **미확인(강의와 공식 문서 차이)**: 공식 문서 Cost 절은 "each call consumes tokens at the advisor model's rates in addition to your main model's usage", 구독 플랜에서는 "advisor usage counts toward your plan's usage limits, except that a Fable advisor bills to usage credits on plans where Fable usage does"라고 적는다. 강의의 "토큰 차감이 안 된다"는 강사 계정·플랜 조건에서의 관찰일 수 있으나 확인하지 못했다.

### 실습/데모 내용 (명령어, 파일 구조, 프롬프트, 코드 조각 등 원문 그대로 보존)

- 문서 탐색: Claude Code 공식 문서(한국어) → 시작하기 → **핵심 개념** 5개 메뉴, 하단 "질문하기", 상단 "어시스턴트에게 묻기", 컨텍스트 윈도우 그래픽 페이지, 프롬프트 캐싱 항목.
- `.claude` 찾기 프롬프트(원문):
  - "내 홈 폴더 밑에 점 클로드 폴더의 위치가 어디냐"
  - "그 경로 파일 탐색기로 보여줘요"
- 강사 PC의 `~/.claude` 하위(화면에서 언급된 순서): `agents/`, `backups/`, 캐시, `chrome/`, `daemon/`, `file-history/`, `ide/`, `jobs/`, `paste-cache/`, `plugins/`, `projects/`, 세션 데이터·`session-env`(전사 "세션 EMV"), 스냅샷, `skills/`, `history.jsonl`(강사 PC 화면에 "1154"라는 숫자가 보였다고 언급), 기타 json, `settings.json`.
- `projects/` 폴더명 예: "프라이빗 TMP 뭐 클로드 501 어쩌고" 같은 것들, 그리고 홈·데스크탑·폴더 경로를 대시로 이은 이름.
- 메모리 구조:
  ```
  ~/.claude/projects/<경로를-대시로-바꾼-이름>/
    ├── (UID 기반 기록, 서브에이전트 기록)
    └── memory/
        ├── MEMORY.md      # 목록: "어쩌고 저쩌고 MD문서 가라" + 짧은 설명
        └── *.md           # 개별 메모리 (metadata type: user / project / feedback)
  ```
  - 예시 메모리: `User Language Korean`(유저가 한국어로 무조건 얘기하라고 함).
- 메모리 수정 지시어(원문): "기억해", "지워". 테스트 예(원문 그대로): "아 씨 똑바로 안 해?" / "야 이 새끼야 똑바로 안 해?" → 바로 기억한다.
- settings.json에서 화면으로 짚은 항목: `env`, `permissions`(deny — 아티팩트, 예전 웹서치), 기본 모델, status line, 플러그인, 마켓플레이스, output style, effort 기본값, 모델별 세부 세팅, advisor, 아티팩트 끄기 키(시연 중 `false`로 바꿈).

### 강사 팁·주의사항
- 자료는 "항상 거들 뿐". 기능 자체가 궁금하면 **공식 문서 + 문서 내 질문 기능**을 쓴다. 핵심 개념 5개는 반드시.
- 커넥터/플러그인 이름이 같아도 **챗용인지 코드용인지**만 구분하면 된다.
- 웹 Code는 거의 쓰지 않는다(클라우드·GitHub 필수). 로컬은 앱 또는 CLI.
- 이동이 많으면 **보이스 모드**로 말로 시켜라(CLI에도 있음).
- 릴리즈 노트를 Claude에게 물어 "내게 필요한 업데이트"만 골라 보라.
- `file-history`, 세션 폴더, 스냅샷 같은 쌓이는 파일은 **수시로 지운다**(Claude에게 시켜도 됨). 단 `plugins/`는 원본이라 지우면 안 된다.
- 메모리는 자동으로 쌓이게 두기보다 **메인 작업이면 직접 수정**한다. 무엇을 기억했는지 사람이 모르게 된다.
- 메모리는 PC 로컬 → 협업 시 "내 PC에선 되는데"의 원인. **공유 방법을 고민**하라.
- **전역 스킬은 공통으로 쓰는 것만.** 나머지는 프로젝트로, 혹은 참조 스킬 하나로.
- settings.json은 **PC 이동 시 직접 복사**해야 한다.
- 권한은 **deny 위주**로 본다. 마음에 안 드는 내장 도구(예: 예전 웹서치)는 막고 외부 API로 대체할 수 있다.
- **advisor**는 적극 활용하되 느려진다는 점을 감안(계획 단계에 특히 유용).

### 실제 프로젝트에 적용할 체크리스트 (- [ ] 행동 지침, 특정 프레임워크에 묶이지 않는 원칙 위주)
- [ ] 쓰는 에이전트 도구의 공식 문서에서 "작동 방식·확장·설정 디렉터리·컨텍스트 윈도우" 같은 핵심 개념 문서를 먼저 읽는다.
- [ ] 도구의 **전역 설정 폴더**와 **프로젝트 설정 폴더**가 어디인지, 각각 무엇이 들어가는지 확인해 둔다.
- [ ] 에이전트가 **자동으로 쌓는 기억(메모리)**이 어디에 저장되는지 확인하고, 주요 프로젝트는 사람이 직접 검토·수정한다.
- [ ] 자동 메모리는 **개인 PC 로컬**이라는 전제로, 팀이 같은 결과를 내야 하는 지침은 저장소에 커밋되는 파일로 옮긴다.
- [ ] "내 PC에선 되는데 다른 사람은 안 된다"면 개인 메모리·전역 설정 차이부터 의심한다.
- [ ] **전역(모든 세션에 로드되는) 스킬·지침은 모든 프로젝트에 공통인 것만** 둔다. 언어·프로젝트별 것은 프로젝트 범위로 내린다.
- [ ] 스킬 description도 매 세션 토큰이라는 점을 염두에 두고 개수·길이를 관리한다.
- [ ] 개인 설정 파일(환경 변수·권한·기본 모델·effort 등)을 여러 PC에서 쓰면 **수동으로 옮기거나 버전 관리**하는 방법을 정해 둔다.
- [ ] 권한 설정은 **deny 목록**을 중심으로 관리하고, 원치 않는 내장 기능은 명시적으로 끈다.
- [ ] 체크포인트·세션 기록 같은 누적 데이터의 보존 기간·정리 주기를 정하되, 플러그인 원본·설정 파일은 지우지 않는다.
- [ ] 계획·완료 판단처럼 중요한 결정 지점에는 **더 강한 모델의 검토(advisor 류)**를 붙이는 것을 검토하고, 속도·비용 영향을 확인한다.
- [ ] 여러 기계에서 작업한다면 원격 접근 방식(앱 연동 vs SSH)과 "대상 기계가 켜져 있어야 한다"는 조건을 운영 계획에 넣는다.

> 확인 필요:
> - 02:21 "비틀리에 SDS AXAED 드라이브" — 자료를 받을 Drive 위치로 보이나 정확한 이름 불명.
> - 03:03 "하네스 엔지니어링을 정리한 논문"(8월 발표) — 논문 제목이 언급되지 않음. 저장소 `Day06/`에는 이론 PDF 1개만 있고 논문 2편은 없다.
> - 16:25 "반대로 클라우드도 선택해서" — 앞 문장이 없어 무엇을 선택한다는지 불분명(클라우드 실행 환경 선택으로 추정).
> - 20:30 앱에서도 Fast 모드를 켤 수 있는지 강사 스스로 확신하지 못함.
> - 34:19 "이 홉의 낭비" — 메모리 문서를 한 번 더 열어 읽는 단계를 낭비라고 한 것으로 추정.
> - 37:26 "세션 EMV" — `session-env` 폴더로 추정.
> - 43:49 "차를 웹서치하는 플러그인" — 어떤 플러그인인지 불명.
> - 45:41 "이거 뭐해, 엑사이죠?" — 모델·effort 설정 예시 중 일부로 보이나 뜻 불명.
> - 46:10 advisor "토큰 차감이 안 된다" — 공식 문서(advisor Cost 절)와 다름. 위 본문 "미확인" 참조.
> - 40:40 history.jsonl "대화기록 모두" — 공식 문서는 "입력한 프롬프트"로 설명. 위 본문 "미확인" 참조.
> - 강사가 연 한국어 문서 "핵심 개념" 메뉴 5개의 정확한 목록 — 전사에서는 작동 방식, 확장, .claude 디렉토리, 컨텍스트 윈도우까지만 이름이 나옴(5번째 미확인).
