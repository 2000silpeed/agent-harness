## 6일차 2강 — Claude Code 메모리 계층: CLAUDE.md, rules, CLAUDE.local.md, AGENTS.md

> 출처: 「6일차 2강 다시보기」(전사·분석, 40:18), 「6일차 2강 장표」(15장). SDS AX Advanced · 2026-11-09 (1강에 이어 오전, 10시 5분 휴식 후).
> 강의는 공식 문서(한국어 Claude Code Docs)와 실습 폴더의 `CLAUDE.md`, 강의 자료의 "클로드의 메모리 섹션"을 띄워 설명했다. 대응 저장소 폴더는 `Day06/`·`Day06_new/`(둘 다 `CLAUDE.md`가 `@AGENTS.md` 한 줄)이며, 저장소의 `Day06_new/docs/sources/claude_code/01_instructions.md`가 같은 공식 문서 문장을 원문으로 정리해 두었다.

### 핵심 요약 (3~5줄)
- 메모리를 담당하는 것은 1강에서 본 **프로젝트 MEMORY.md**만이 아니라 **CLAUDE.md**도 있다. **글로벌 CLAUDE.md**(유저 단위, PC에 하나)는 모든 곳에 들어가므로 공통 작업 내용만 신중히 쓰고, **프로젝트 CLAUDE.md**("프로젝트의 시스템 프롬프트")는 팀이 함께 본다.
- 세션 시작 시 **모델 시스템 프롬프트 → MEMORY.md → 환경 정보 → MCP 툴·스킬 설명 → 글로벌 CLAUDE.md → 프로젝트 CLAUDE.md** 순으로 자동 적재되고, 사용자가 제어할 수 있는 건 **뒤쪽 두 CLAUDE.md**다. 시스템 프롬프트가 XML로 쓰이므로 이 문서들도 **XML로 양식을 통일**하라(작은 팁이지만 쌓이면 차이).
- 특정 폴더·파일에서만 필요한 지엽적 규칙은 **`.claude/rules/`**에 **경로(glob) 범위**를 지정해 두면 그 파일을 다룰 때만 로드된다. **메모리는 계층적으로, 필요할 때만 로드되게** 설계한다. 하네스는 **자율보다 강제**를 우선하므로 스킬보다 rules를 추천.
- rules는 **협업**에서 더 중요하다: 나만 잘 되면 팀원 결과를 계속 리뷰해야 한다. 글로벌은 사람마다 달라 제어가 어렵지만 프로젝트는 제어할 수 있다. 엔터프라이즈는 **조직 CLAUDE.md**를 로그인만으로 강제 주입할 수 있다.
- **AGENTS.md**는 최근 지원이 추가됐지만 **CLAUDE로 시작하는 파일(특히 CLAUDE.local.md)이 있으면 AGENTS.md를 읽지 않는다** → 한쪽으로 통일하거나 `@` 참조를 유지한다. 메모리는 "지시일 뿐 강제가 아니다" → 다음은 **훅**.

### 주요 개념 (개념별 설명, 강사가 강조한 이유 포함)

**1. 메모리를 담당하는 두 가지: MEMORY.md와 CLAUDE.md (00:01~)**
- 1강에서 본 프로젝트 메모리(MEMORY.md) 외에 "**CLAUDE.md 파일도 메모리입니다.**"
- MEMORY.md는 **프로젝트** 단위, 글로벌 CLAUDE.md는 **유저** 단위. 이 PC의 유저는 나 혼자이므로 글로벌 CLAUDE.md는 **하나**만 존재한다. 강사 PC에는 없다 — 없으면 `.claude` 폴더에 **만들어 넣으면 된다**.
- 강조 이유: 글로벌 CLAUDE.md는 "이 컴퓨터에서 어디에 클로드를 키시든 … 계속 들어가게" 된다(전역 스킬과 같은 성격). 그래서 "굉장히 조심해서", **공통 작업 내용만** 담아야 프로젝트별 MEMORY.md와 잘 어울린다.
  - (저장소 확인: 사용자 파일 위치 `~/.claude/CLAUDE.md` — `Day06_new/docs/sources/claude_code/01_instructions.md:15`)

**2. 프로젝트 CLAUDE.md와 로드 순서 (03:19~)**
- 프로젝트 레벨에도 CLAUDE.md가 있다. "프로젝트 메모리" 또는 "**프로젝트에 있는 시스템 프롬프트**"라고도 부른다. 실습 자료(하나의 프로젝트)의 CLAUDE.md는 **AGENTS.md를 참조**하도록 연동돼 있다.
  - (저장소 확인: `Day06/CLAUDE.md:1`, `Day06_new/CLAUDE.md:1` — `@AGENTS.md`; 수업 저장소 루트도 `CLAUDE.md:4` `@AGENTS.md`)
- 글로벌과 프로젝트 양쪽에 있으니 **어떤 순서로 로드되는지, 무엇을 써야 충돌이 안 나는지**가 중요하다 → 공식 문서 **"컨텍스트 윈도우 확장하기"**(1강의 컨텍스트 윈도우 그래픽 페이지)로 확인.
- 강사가 짚은 순서: ① **모델별 시스템 프롬프트**("invisible in your terminal" — 우리도 모르게 로드) → ② **MEMORY.md**(있으면 로드, 없으면 안 됨) → ③ **환경 정보**(현재 디렉토리, 플랫폼, 셸 버전, OS 버전, Git 등) → ④ **MCP 툴, 스킬 description** → ⑤ **글로벌 CLAUDE.md** → ⑥ **프로젝트 CLAUDE.md**(마지막).
- "모델의 시스템 프롬프트부터 여기까지. 이건 **자동**이에요." → 우리도 모르는 새 컨텍스트 앞부분을 많이 차지한다. 사용자가 제어할 수 있는 건 **뒤쪽 두 개**(글로벌·프로젝트 CLAUDE.md).
  - (공식 문서 확인: https://code.claude.com/docs/en/context-window.md — "Before you type anything: CLAUDE.md, auto memory, MCP tool names, and skill descriptions all load into context." 공식 문서는 이 네 가지를 나열할 뿐 강의의 6단계 순서를 문장으로 적지는 않는다. 글로벌→프로젝트 순서는 https://code.claude.com/docs/en/memory.md "a project instruction appears in context after a user instruction"로 확인 — 저장소 확인: `Day06_new/docs/sources/claude_code/01_instructions.md:13`. 나머지 순서(MEMORY.md가 환경 정보보다 앞인지 등)는 미확인.)

**3. XML로 문서 양식 통일 (07:56~)**
- 시스템 프롬프트·스킬 작성법에서 말했듯 "**XML입니다. 별거 아니에요. 왜? 얘네가 이렇게 쓴다니까요.**" 앞에 들어가는 시스템 프롬프트가 XML 구조이므로, 우리도 XML에 맞춰 써야 "문법이 바뀌지 않았구나" 하고 계속 참조한다. (Claude가 내부적으로 XML 꺽쇠를 씌워 프로그램적으로 로드할 수도 있지만 거기까지는 알 수 없다.)
- 효과: 제어 측면, 내용 수정할 때도 도움. → 글로벌 CLAUDE.md와 프로젝트 CLAUDE.md를 **섹션으로 나눠 최대한 같은 양식**으로.
- MEMORY.md는 기본이 마크다운 리스트 + 개별 문서(YAML + MD로 구성)인데, 이것도 **XML 기준으로 통일**하면 괜찮다.
- 강조 수준: "엄청나게 큰 장점이 있냐? 그것보다는 **명령을 조금 더 잘 찾고 이해한다** 정도." "아주 작은 팁들이지만 이런 게 쌓이면 … 우리 말을 좀 더 잘 듣고 안 듣고가 정해지기 때문에" 굉장히 추천.
- 귀찮으니 **주 1회 회고 때** 통일 작업을 돌린다 — 손으로 하지 말고 "**금요일 오후 4시**" 같은, 작업이 가장 적을 때 **자동으로 돌아가게 스케줄링**.

**4. rules: 경로별 규칙 (11:48~)**
- 문제: 특정 폴더에 들어갔을 때만 필요한 규칙. 가상 예: `src/ddl/create.sql`에 DDL 한 문장을 추가하라는 작업 — SQL 작성 규칙(DDL은 이렇게, SELECT는 이렇게)이 필요하지만 "프로젝트의 시스템 프롬프트인 CLAUDE.md에서 주기에는 좀 내용이 너무 **지엽적**"("좀 짜치죠").
- 해법: **rules**(기능 이름). 공식 문서: 구글에서 "Claude Code Docs" → 한국어 문서에서 "rules" 검색 → 두 번째 결과 **".claude/rules로 규칙 정리하기"**(위치: 시작하기 > Claude Code 사용하기 > **지침 및 메모리 저장** 사이드바 중간).
- 문서 문장(강사 낭독): 더 큰 프로젝트는 `.claude/rules` 디렉터리로 지침을 **여러 파일로 모듈화**, 유지보수 쉬움, 그리고 **특정 파일 경로로 범위 지정** → "클로드가 일치하는 파일로 작업할 때만 컨텍스트에 로드된다" → **노이즈 감소, 컨텍스트 공간 절약**.
  - (저장소 확인: `Day06_new/docs/sources/claude_code/01_instructions.md:65` — "A path-scoped rule loads when Claude uses the Read, Write, or Edit tool on a matching file."; `:64` — paths 없는 rule은 "loaded at launch with the same priority as .claude/CLAUDE.md")
- **원칙**: "**메모리는 무조건 계층적으로 설계를 해야 돼요. 필요할 때만 딱딱딱 로드 되고 그게 아닐 땐 빠져줘야 됩니다.**"(스킬도 같다) SQL 작업 직전에 룰이 들어와야 안 까먹고 작업하고, 끝나면 빠져나간다 → 작업 안정성 + 컨텍스트 과다 사용 방지.

**5. rules가 협업에서 중요한 이유, 회사 지침 주입 (17:48~)**
- "이 룰즈를 많이들 빼먹어요." 혼자 쓸 때는 개인 메모리에 쌓여(알아서 룰처럼 쪼개져) 신경 안 써도 되지만, 모두가 Claude로 협업할 때 **나만 잘 돼 있으면** 나만 멀쩡한 프로그램을 만들고 다른 사람은 못 만든다 → "제가 하는 작업을 내가 계속 리뷰를 해줘야 돼요. 너무 힘들어요."
- 그래서 누군가 **먼저 좋은 룰이나 자기 업무 영역의 룰을 정리**한다. 예전엔 Confluence에 문서를 잔뜩 썼지만 사람도 까먹고 Claude도 까먹으니 "안 까먹게 해두자". rules는 개인 레벨보다 **협업 관점**에서 더 중요 — "저 사람이나 나나 똑같은 룰이 로드 됐을 때 작업을 하자."
- 글로벌 vs 프로젝트: 글로벌은 그 사람 PC에 세팅되고 명령 스타일도 달라 **제어가 어렵지만**, "최소한 **프로젝트는 제어**할 수 있어요." 프로젝트는 "개인과 회사의 몫".
- **회사 강제 주입**: 엔터프라이즈 계정 담당자는 **로그인만 해도 지침을 강제 주입**할 수 있다("무섭죠"). 강사는 팀원 계정을 관리할 때 **훅도 강제 주입**해 사용량을 보던 "빅브라더" 역할을 했다고. 회사가 주입한 것은 개인이 **없앨 수 없고 최우선으로 동작**한다.
  - (공식 문서 확인: https://code.claude.com/docs/en/memory.md — "Organizations can deploy a centrally managed CLAUDE.md that applies to all users on a machine. Developers can exclude other CLAUDE.md files with the `claudeMdExcludes` setting, but not this one." 관리 정책 위치 macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`, Linux·WSL `/etc/claude-code/CLAUDE.md`, Windows `C:\Program Files\ClaudeCode\CLAUDE.md` — 저장소 확인: `Day06_new/docs/sources/claude_code/01_instructions.md:14,20`. 설정의 우선순위는 "managed settings, command line, project local, shared project, user" — 저장소 확인: `Day06_new/docs/sources/claude_code/03_control.md:53`. 단 공식 문서는 관리형 CLAUDE.md를 "guidance"로 쓰고 강제는 managed settings의 `permissions.deny` 등으로 하라고 적는다.)
- 강사의 글로벌 CLAUDE.md는 **비워 둔다**. 예전엔 "다양한 서브 에이전트로 활용해서 작업을 해라"처럼 모든 프로젝트 공통인 것을 썼지만, 혼자·소수로 작업해도 "이게 있음으로써 이 사람이랑 오히려 **맞추기가 어렵더라**" → 없앰. (자동 메모리 쌓이는 건 굳이 끄지 않음.) "이거는 선택이에요."
- 목적: 프로젝트는 팀원과 공유하니 **공통으로 세팅해 같은 환경을 유지**. "**차라리 다 같이 실수를 해서 다 같이 개선을 하자**." 나는 되고 쟤는 안 되는 데서부터 힘들어진다.

**6. rules 폴더 구성과 glob 패턴 (22:54~)**
- 핵심은 폴더 구성: 프로젝트의 `.claude/` 안에 `CLAUDE.md`를 둘 수 있고, **`rules/` 폴더를 직접 만들어** 여러 문서(코드 스타일, 테스트, 보안 등)를 둔다.
- 문서 모양(공식 문서 예시): `src/api` 아래 `.ts` 파일을 작성할 때 "api를 만드는 거니까 이 룰을 무조건 참고해라".
- "**원래는 스킬로 많이 썼었거든요 … 저는 그 방식보다는 룰즈를 추천드려요. 얘는 강제로 로드되거든요.**" 오늘 배울 하네스는 **자율과 강제 중 강제를 우선**한다 — 자율은 많이 경험해 봤고 "케이스가 너무 다양해. 그러니까 열받아요." Claude가 **프로그램으로 로드**를 강제해 주니 그것을 활용한다. rule 문서는 코드·스니펫 포함해 **스킬처럼 촘촘하게** 쓸 수 있다.
- **glob 패턴**을 모두 지원: `*`(별, 아스테리스크) 사용, 확장자 여러 개 중 하나 등. "이 룰즈를 얼마나 우리가 프로젝트에 촘촘하게 잘 세팅을 해줬냐에 따라서 이 프로젝트의 **안정성**이 달라집니다."
  - (공식 문서 확인: https://code.claude.com/docs/en/memory.md — 예시 frontmatter `paths:` `- "src/api/**/*.ts"`, 여러 확장자 `"src/**/*.{ts,tsx}"`; "`paths` is the only field Claude Code reads from a rule; any other field is ignored without an error." 저장소 확인: `Day06_new/docs/sources/claude_code/01_instructions.md:66`)
- **레거시 코드베이스**: AI가 잘 작업하게 하려면 rules를 세팅해야 한다. Confluence에 쌓아 온 노하우를 누군가 rules로 정리해야 코드베이스 **이해**뿐 아니라 **수정**에도 도움이 된다. "**클로드.md에 다 쓰는 건 의미가 없어요. 까먹어요.**"
- 작성 형식 자체는 중요하지 않다 — 어차피 Claude에게 1차 작성을 시키면 규칙을 알고 쓴다.
- "네트워크 경로" 같은 것은 잘 로드되지 않는다는 내용이 문서에 있다(그렇구나 하고 보면 됨). (공식 문서 확인: https://code.claude.com/docs/en/memory.md — "If you point a `.claude/rules/` or `CLAUDE.md` symlink at a network path such as the UNC share `\\server\share` or a path under `/net` or `/Network`, the linked instructions don't load.")

**7. 글로벌 rules와 조직 CLAUDE.md 배포 (28:13~)**
- 글로벌에도 룰을 넣을 수 있다(문서의 "3차 수준" 규칙). 강사는 처음엔 넣었다가 **잘 안 쓰게** 됐다 — 모든 프로젝트에 적용돼 특정 폴더를 지정하기 어렵고, 그런 건 **글로벌 스킬이 다 해 주더라**. 다만 **회사의 큰 지침** 같은 건 이 레벨로 적용할 수도 있겠다.
  - (공식 문서 확인: https://code.claude.com/docs/en/memory.md — "Personal rules in `~/.claude/rules/` apply to every project on your machine … Claude Code loads user-level rules before project rules")
- 공식 문서 **"대규모 팀을 위한 CLAUDE.md 관리하기 > 조직 전체 CLAUDE.md 배포하기"**: 엔터프라이즈 계정 담당자가 중앙에서 CLAUDE.md를 꽂아 주고 로그인하는 순간 내려받게 할 수 있다.
  - (공식 문서 확인: https://code.claude.com/docs/en/memory.md — "Use MDM, Group Policy, Ansible, or similar tools to distribute the file across developer machines.")
- 강의 자료 **"클로드의 메모리 섹션"**: 오토 메모리가 언제 로드되고 어떤 특성인지, **Copilot과 비교**, 오토 메모리 저장 방식 그림, **메모리를 팀과 공유하기 위한 고민**을 정리해 두었다(강의에서는 화면만 넘김). (저장소의 `Day06/Day6_Agent_Harness_이론자료.pdf`에서는 이 섹션을 찾지 못했다 — 확인 필요 참조.)
- 공식 문서로도 **계층별로 메모리가 로딩**되는 것을 봤다: CLAUDE.md부터 rules, 하위의 개별 CLAUDE.md까지 촘촘하게 로드 → 메모리 제어가 정말 중요하고, 대부분 XML로 쓰는 게 도움.

**8. 컨텍스트 적재 순서와 API 메시지 구조 (31:33~)**
- API 입장: **시스템 메시지는 전체 API 요청에서 딱 한 개**(보통 최상단), 나머지는 **유저·AI 메시지**의 반복. 앞에 쌓이는 MCP 등도 API 입장에서는 유저 메시지 쪽.
- 그래서 시스템이 자동으로 넣어 주는 것 외에 **우리가 제어하는 영역은 유저 메시지 속**에 들어간다 → **XML로 통일**해 시스템처럼 인식되게 만든다.
- "이 시스템을 우리가 대신 쓸 수 있다? **못 써요.** 시스템처럼 인식하게 하는 건 할 수 있어요." 완벽하게 속일 수는 없지만 시스템처럼 만들 수는 있고, "그 모든 꼼수들이 다 XML로 출발".
- "**이 메모리는 클로드가 대신 해주지 않습니다. 이건 여러분들이 설계하셔야 돼요.**"
  - (저장소 확인: `Day06_new/docs/sources/claude_code/01_instructions.md:105` — "CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself." 강의 앞부분(02:06경)의 "시스템 프롬프트로써 CLAUDE.md는 계속 들어가게 됩니다"는 이 절의 설명(유저 메시지 속)과 표현이 다르다 — 공식 문서는 유저 메시지 쪽.)

**9. AGENTS.md와 CLAUDE.local.md (33:40~)**
- 다른 AI 시스템은 **AGENTS.md**를 기본 로드하는데 Claude만 CLAUDE.md를 써 왔다("짜증나요. 통일하지"). Claude가 "**진짜 최근에 한 2주 3주**" 전에 AGENTS.md 지원을 추가했다.
  - (공식 문서 확인: https://code.claude.com/docs/en/memory.md — "Reading `AGENTS.md` directly requires Claude Code v2.1.277 or later." 지원 시점(2~3주 전)은 미확인. 저장소 확인: `Day06_new/docs/sources/claude_code/01_instructions.md:40`)
- 실습 폴더에는 AGENTS.md도 있고, CLAUDE.md는 예전 방식대로 **`@`(골뱅이)로 참조**를 걸어 두었다. `@`는 "AGENTS.md에 있는 문서 이렇게 복사해가지고 붙여넣기 하는 거랑 똑같아요" — **단순 참조**.
  - (저장소 확인: `Day06_new/docs/sources/claude_code/01_instructions.md:56` — "Imports help you organize a long file but don't reduce its context cost"; `Day06_new/README.md:69` — 위쪽 폴더의 `CLAUDE.md`가 `@AGENTS.md`로 가져오므로 처음 열 때 "External imports"에서 허용을 고른다)
- 주의: 공식 지원됐으니 "둘 다 같이 써야지"는 안 된다. **둘 중 하나만**. CLAUDE가 붙은 모든 문서를 지워야 하는데, 특히 "골 때리는 녀석"이 하나 더 있다 → **`CLAUDE.local.md`**.
- **CLAUDE.local.md** = Claude 메모리 계층의 **가장 마지막**. 프로젝트 CLAUDE.md는 팀원 모두가 공유하지만, 이건 **내 Claude에만 로드**된다 → **Git에 푸시하면 안 되고 ignore 처리**.
  - 용도 예: 팀에서 DB 담당인데, 팀 규칙과 **상충하거나 추가**되는 것, **팀 규칙에 아직 올리기 전**인 것을 내 Claude에서 돌릴 때.
  - (저장소 확인: `Day06_new/docs/sources/claude_code/01_instructions.md:17` — "Personal project-specific preferences; add to .gitignore"; `:28` — "Within each directory, CLAUDE.local.md is appended after CLAUDE.md, so your personal notes are the last thing Claude reads at that level.")
- **함정**: "얘가 있으면 이게 절대로 동작을 안합니다. agent.md." CLAUDE.md만 지우고 CLAUDE.local.md를 남기면 AGENTS.md가 로드되지 않아 "머리가 아픕니다". → **CLAUDE가 붙은 MD를 싹 제거하고 한쪽으로 통일**하거나, 아니면 **`@` 참조를 계속 걸어** 원본은 AGENTS.md에 두고 그것만 수정.
  - (저장소 확인: `Day06_new/docs/sources/claude_code/01_instructions.md:39` — "By default, Claude reads AGENTS.md only when you have no CLAUDE.md in your working directory or above it."; `:41` — "Because CLAUDE.local.md counts, adding one … in a project that relies on AGENTS.md stops Claude from reading AGENTS.md for you."; `:42` — import를 유지해도 AGENTS.md를 두 번 읽지 않음. 공식 문서 확인: https://code.claude.com/docs/en/memory.md — 이 판정에 세는 파일은 작업 폴더와 그 위의 `CLAUDE.md`·`.claude/CLAUDE.md`·`CLAUDE.local.md`이고, `~/.claude/CLAUDE.md`·조직 관리형 CLAUDE.md·`.claude/rules/`는 세지 않는다.)
- 강사 자신은 귀찮아서 **CLAUDE.md는 `@AGENTS.md` 참조만 두고 내용은 AGENTS.md에** 둔다(옛 방식이라 일단 이렇게; 나중에 옮겨갈지 모름). 또 어떻게 바뀔지 몰라서.

**10. 마무리와 훅 예고 (39:37~)**
- Claude의 메모리는 **계층적으로 차근차근 나눠서 관리**된다.
- "메모리는 자율적으로 관리가 되는 거긴 하죠. 우리가 **지시를 내릴 뿐 강제하는 요소는 아닙니다.**" → 다음은 **강제하는 요소 = 훅**. 스킬은 많이 했으니 안 한다. 11시에 재개.
  - (저장소 확인: `Day06_new/docs/sources/claude_code/01_instructions.md:104` — "To block an action regardless of what Claude decides, use a PreToolUse hook instead.")

### 실습/데모 내용 (명령어, 파일 구조, 프롬프트, 코드 조각 등 원문 그대로 보존)

- 공식 문서 찾아가기(원문 흐름): 구글에 "클로드 코드 독스" → 한국어 문서 → 상단 검색에 "룰즈"(대문자 안 써도 됨) → 두 번째 글 "**점 클로드의 룰즈로 규칙 정리하기**" (사이드바: 시작하기 > 클로드 코드 사용하기 > **지침 및 메모리 저장**). 로드 순서는 "**컨텍스트 윈도우 확장하기**" 문서, 조직 배포는 "**대규모 팀을 위한 클로드 MD 관리하기 > 조직 전체 클로드 MD 배포하기**".
- 메모리 계층(강의에서 다룬 것):
  ```
  ~/.claude/CLAUDE.md                 # 글로벌(유저) — PC에 하나, 없으면 만들어 넣기
  ~/.claude/rules/                    # 글로벌 rules — 강사는 잘 안 씀
  ~/.claude/projects/<…>/memory/MEMORY.md   # 프로젝트 자동 메모리(1강)
  <프로젝트>/CLAUDE.md                 # 프로젝트 시스템 프롬프트(팀 공유)
  <프로젝트>/.claude/CLAUDE.md
  <프로젝트>/.claude/rules/*.md        # 경로 범위 규칙 (폴더는 직접 만든다)
  <프로젝트>/CLAUDE.local.md           # 개인용, .gitignore
  <프로젝트>/AGENTS.md                 # 다른 AI 도구 공용
  (조직) 엔터프라이즈 관리형 CLAUDE.md   # 로그인 시 강제 주입, 개인이 못 없앰
  ```
- 세션 시작 시 적재 순서(강사 설명 그대로): 모델 시스템 프롬프트 → MEMORY.md → 환경 정보(현재 디렉토리, 플랫폼, 쉘 버전, OS 버전, Git 버전 등) → MCP 툴, 스킬 디스크립션 → 글로벌 CLAUDE.md → 프로젝트 CLAUDE.md.
- rules 예시(가상): `src/ddl/create.sql`에 DDL 한 문장을 추가하는 작업 → SQL/DDL/SELECT 작성 규칙을 그 경로에만.
- rules 문서 예(공식 문서 화면, 강사 설명: "src 폴더 밑에 api라는 폴더 밑에 … ts 파일을 만들면 이 룰을 무조건 참고해라"). 공식 문서 원문:
  ```markdown
  ---
  paths:
    - "src/api/**/*.ts"
  ---

  # API Development Rules

  - All API endpoints must include input validation
  - Use the standard error response format
  - Include OpenAPI documentation comments
  ```
  (공식 문서 확인: https://code.claude.com/docs/en/memory.md)
- 실습 폴더 CLAUDE.md(저장소 원문): `@AGENTS.md` (저장소 확인: `Day06/CLAUDE.md:1`, `Day06_new/CLAUDE.md:1`)
- XML 통일 운영 예: 주 1회 회고 작업을 "금요일 오후 4시"에 자동 스케줄링해 CLAUDE.md·메모리 문서를 XML 기준으로 정리.

### 강사 팁·주의사항
- 글로벌 CLAUDE.md는 **모든 곳에 들어간다** → 공통 작업만, 신중히. 강사는 협업 시 맞추기 어려워 **비워 둔다**(선택 사항).
- CLAUDE.md·메모리 문서는 **XML 섹션으로 양식 통일**. 큰 효과는 아니지만 쌓이면 말을 더 잘 듣는다. 통일은 주간 회고에 자동으로.
- 지엽적 규칙은 CLAUDE.md에 넣지 말고 **rules + 경로 범위**로. CLAUDE.md에 다 쓰면 **까먹는다**.
- 스킬보다 **rules 추천** — 강제로 로드되기 때문. 하네스는 **자율보다 강제**.
- rules는 **협업용**이다. 누군가 먼저 자기 영역 규칙을 정리해 모두가 같은 룰로 작업하게 한다. "다 같이 실수하고 다 같이 개선".
- 레거시 코드베이스라면 기존 노하우(Confluence 등)를 rules로 옮기는 작업을 **누군가 해야** 한다.
- 엔터프라이즈 관리자는 지침·훅을 **강제 주입**할 수 있고 개인은 못 없앤다.
- 시스템 메시지는 **대신 쓸 수 없다**. 제어 가능한 부분은 유저 메시지 쪽이므로 그 구조를 이해하고 설계하라. 메모리 설계는 **Claude가 해 주지 않는다**.
- AGENTS.md와 CLAUDE.md를 **둘 다 쓰지 말 것**. 특히 **CLAUDE.local.md**가 있으면 AGENTS.md가 안 읽힌다. 통일하거나 `@` 참조 유지.
- CLAUDE.local.md는 **반드시 git ignore**.
- 메모리는 **지시일 뿐 강제가 아니다** → 강제는 훅으로(다음 강의).

### 실제 프로젝트에 적용할 체크리스트 (- [ ] 행동 지침, 특정 프레임워크에 묶이지 않는 원칙 위주)
- [ ] 에이전트에 지침이 들어가는 **모든 계층**(조직·개인 전역·프로젝트·경로별·개인 로컬·자동 메모리)을 목록으로 만들고, 각 계층에 무엇을 둘지 정한다.
- [ ] 세션 시작 시 무엇이 **어떤 순서로 자동 적재**되는지 도구 문서로 확인하고, 내가 제어할 수 있는 부분이 어디인지 표시한다.
- [ ] 개인 전역 지침에는 **모든 프로젝트에 공통인 것만** 두거나 비워 둔다. 팀과 맞춰야 하는 것은 프로젝트 지침으로 옮긴다.
- [ ] 프로젝트 지침은 저장소에 커밋해 **팀 전원이 같은 지침으로** 작업하게 한다.
- [ ] 특정 폴더·파일 유형에만 필요한 규칙은 **경로 범위가 있는 규칙 파일**로 분리해, 해당 파일을 다룰 때만 로드되게 한다(항상 로드되는 지침은 짧게).
- [ ] 반드시 지켜야 하는 규칙은 모델의 자율 판단(스킬 선택 등)에 맡기지 말고 **프로그램이 강제로 로드·집행**하는 장치를 우선한다.
- [ ] 레거시 코드베이스라면 사람이 쌓아 온 노하우 문서를 **에이전트가 읽는 규칙 파일**로 옮기는 담당자를 정한다.
- [ ] 지침 문서들은 **하나의 구조화된 양식**(예: XML 섹션)으로 통일하고, 정리 작업을 **정기 회고에 자동으로** 묶는다.
- [ ] 지침은 모델 입장에서 시스템 메시지가 아니라 **대화(유저 메시지) 안에 들어간다**는 점을 전제로 쓴다.
- [ ] 여러 AI 도구를 함께 쓰면 지침 원본을 **한 파일로 통일**하고, 다른 파일은 참조만 둔다. 도구별 "어떤 파일이 있으면 다른 파일을 안 읽는다" 규칙을 확인한다.
- [ ] 개인용 로컬 지침 파일은 **.gitignore**에 넣고, 그 파일이 공용 지침 로딩을 막지 않는지 확인한다.
- [ ] 조직 차원 지침이 있다면 중앙 배포 방식과 **개인이 덮어쓸 수 없는 범위**를 팀에 공유한다.
- [ ] 지침(메모리)은 강제가 아니라는 전제로, 예외 없이 막아야 하는 행동은 **훅·권한 규칙 같은 집행 장치**로 옮긴다.

> 확인 필요:
> - 05:14 "이 시스템 프롬프트는 클로드.md 문서를 기준으로 합니다" — 강사가 곧바로 "죄송해요, 설명 안 드렸었네"라며 모델별 시스템 프롬프트로 정정. 정정된 설명을 본문에 반영.
> - 06:14~ 적재 순서 6단계 중 MEMORY.md·환경 정보·MCP/스킬 설명 사이의 순서 — 공식 문서는 네 가지를 나열만 함(미확인).
> - 10:08 "힐 같은 문서죠. 그래서 야물 플러스 MD" — YAML 프론트매터가 있는 MD 문서를 가리키는 것으로 추정.
> - 13:25 "프로젝트에서 주기는 좀 작아요", "제공자와 같은 아주 그 폴더에" — 전사가 어색해 정확한 뜻 불명(맥락상 "CLAUDE.md에 넣기엔 지엽적").
> - 18:04 "알아서 막 룰처럼 막 쪼개져 있습니다" — 개인 자동 메모리가 나뉘어 쌓인다는 뜻으로 추정.
> - 28:01 "네트워크 경로 … 잘 로드가 되지 않는다" — 공식 문서의 "네트워크 경로를 가리키는 symlink는 로드하지 않음"으로 보이나 강사가 가리킨 문장인지 미확인.
> - 28:01 "3차 수준의 규칙" — 문서의 어느 구분을 말하는지 불명(글로벌 `~/.claude/rules/`로 이어짐).
> - 30:11~ 강의 자료 "클로드의 메모리 섹션"(오토 메모리, Copilot 비교, 저장 방식 그림, 팀 공유) — 저장소 `Day06/Day6_Agent_Harness_이론자료.pdf`(50쪽)에서 해당 섹션을 찾지 못함. 드라이브의 다른 PDF일 수 있음.
> - 31:39 "잔뜩 2위에 쌓이고" — 의미 불명(앞선 자동 로드 항목이 쌓인다는 뜻으로 추정).
> - 33:36 "이 메모리 수명은 크게 중요하진 않습니다" — 맥락 불명.
> - 34:00 AGENTS.md 지원이 "2주 3주" 전에 추가됐다는 시점 — 공식 문서는 버전 조건(v2.1.277 이상)만 있음(미확인).
> - 38:36 강사 자신의 방식(CLAUDE.md는 @ 참조만, 내용은 AGENTS.md) 설명 일부가 불명확.
