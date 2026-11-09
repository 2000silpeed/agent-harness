## 6일차 4강 — Anthropic 에이전트 메모리 글과 드리밍, pstack·우로보로스 플러그인 분석 실습

> 출처: 「6일차 4강 다시보기」(전사·분석, 45:21 분량), 「6일차 4강 장표」(16장). SDS AX Advanced · 2026-11-09.
> 대응 저장소: `Day06_new/info.md`(강의 시 언급한 사이트: pstack, ouroboros, superpowers, claude-mem, Anthropic 메모리 글)와 `Day06/ouroboros/`(우로보로스 스냅샷). 오후 미니 프로젝트 과제는 `Day06/task.md`. pstack은 저장소에 사본이 없어 GitHub README로 확인했다.
> 참고: 앞 약 9분은 글·뉴스 소개, 이후는 설치 실습이며 설치 대기 구간은 발화가 적다.

### 핵심 요약 (3~5줄)
- Anthropic 리서치 글 「The components of agent memory」(랜스 마틴)를 소개했다. 메모리는 **트랜스크립트 → 메모리 노트 → 리프레젠테이션 → 인젝티드 컨텍스트** 계층으로 압축되고, 사람이 자는 동안 단기 기억이 장기 기억이 되듯 **드리밍**이 불필요한 것을 걷어내고 핵심만 남긴다. 강사가 본 핵심: "메모리에 아주 조그만한 내용을 남겼어도 의미있게 동작하더라."
- Claude Code·Codex의 드리밍 로직은 공개된 게 없지만(OpenClaw·Hermes Agent는 오픈소스), 목적이 텍스트 압축이니 **작업 종류에 따라 무엇을 남길지**가 핵심이라고 봤다. 곁들여 Qwen4 출시 임박 소식(27B 기대)을 전했다.
- 실습: 참고 프로젝트로 Cursor 플러그인 **pstack**(Lauren Tan, 닉네임 poteto)을 Claude Code에 설치하고 setup으로 추론 예산·역할별 모델을 고른 뒤, 전역 rules와 플러그인 구조를 뜯어봤다. 스킬 58개·에이전트 2개, "토큰 엄청나게 잡아먹습니다."
- 가장 흥미로운 구조: 대부분의 스킬이 **`disable-model-invocation: true`**라 모델이 스스로 고를 수 없고, 진입점 poteto 모드가 **23개 플레이북** 중 하나를 골라 단계 그대로 따르며 다른 스킬의 md를 read로 직접 읽어 엮는다. poteto 모드조차 사용자만 실행할 수 있어 무한 루프를 막는다.
- 계획 수립용으로 소크라테스식 질문을 던지는 **우로보로스(Ouroboros)**를 설치·setup하고, `ooo interview`로 "pstack을 내 작업 지침에 맞게 개선한 나만의 플러그인"을 만드는 인터뷰를 걸어 둔 채 2시까지 휴식.

### 주요 개념 (개념별 설명, 강사가 강조한 이유 포함)

**1. Anthropic 「에이전트 메모리의 구성 요소」 글 (00:01~03:11)**
- Anthropic에 에이전트 메모리 자체를 분석한 리서치 글이 올라왔다. 강사도 아직 다 안 읽어서 AI로 먼저 정리해 보고 같이 읽었다. (저장소 확인: Day06_new/info.md:12 — https://www.anthropic.com/research/components-of-agent-memory)
- 저자 **랜스 마틴**: 랭체인 유튜브로 알려졌고 랭체인 창업자와 같이 팀을 했던 것으로 알며, 커서 팀을 거쳐 최근 Anthropic으로 옮겼다(강사 발언). 글의 저자 표기는 공식 페이지에서 확인했다(공식 문서 확인: https://www.anthropic.com/research/components-of-agent-memory — 제목 "The components of agent memory", Lance Martin).
- 계층: 트랜스크립트 → 메모리 노트 → 리프레젠테이션 → 인젝티드 컨텍스트. 트랜스크립트를 노트로 표현하고, 노트를 더 줄이는 재설계를 거쳐 **최종적으로 작은 컨텍스트로 주입**한다. 공식 글의 그림은 아래부터 "transcripts (a searchable event log)", "memory notes written by Claude", "memory representations such as wikis", "injected context loaded into every session"이다(공식 문서 확인: 위 링크).
- 강조 이유: 오후에 Claude Code 개발 환경을 세팅할 때 "메모리를 어떻게 구성해야 잘 동작할까"의 참고가 된다. 글에 메모리 레이어 그림과 실제 메모리가 차지하는 비중 표가 있다. (저장소 확인: Day06/task.md:20, :28 — 오늘 미니 PJT "Claude Code & GJC 개발환경 구축", "메모리 시스템을 구성해야합니다")

**2. 드리밍(Dreaming) (01:38~04:48)**
- 사람이 꿈을 꾸는 것에서 차용. 잠자는 동안 단기 기억이 장기 기억으로 전환되듯, 세션을 돌리며 생긴 작은 메모리들을 드리밍 시간에 장기 기억으로 바꾼다. 에이전트 메모리에서는 **불필요한 내용을 걷어내고 핵심만 줄이는** 과정이고, 이를 반복해 메모리 단계를 계속 압축한다. OpenClaw나 Hermes Agent를 아는 사람에게는 익숙한 개념.
- 공개 현황: OpenClaw·Hermes Agent의 드리밍 로직은 오픈소스. Claude Code·Codex가 어떻게 하는지는 "사실 공개된 게 없어요."
- 강사 의견: "어차피 드리밍이라는 게 목적상 압축이고… 그중에 뭐가 필요한지를 남기는 게 핵심." 개발에 쓰면 개발 작업 위주로, 다른 서비스면 그 형태대로 드리밍해야 한다.
- 운영 디테일: MEMORY.md는 처음 **200라인 또는 25KB**만 로드되고 나머지는 인덱스라는 내용은 공식 문서에 이미 있어서 "그렇게 신기한 글인가라는 생각이 별로 안 드네요." (저장소 확인: Day06_new/docs/sources/claude_code/04_state.md:186 — "The first 200 lines of MEMORY.md, or the first 25KB, whichever comes first")
- 드리밍 켜고 끄기: "클로드에서 드리밍 기능을 껐다 켰다 하실 수 있어요. 그것도 볼 거고요." 공식 memory 문서에서는 드리밍 설정을 찾지 못했다(공식 문서 확인: https://code.claude.com/docs/en/memory.md). 제3자 글들은 `/memory` 메뉴의 "Auto-dream" 항목(기본 꺼짐)을 언급한다. 미확인.

**3. Qwen4 출시 임박 (04:48~07:47)**
- Qwen CTO가 "다음 주에 나온다"고 했고 그 다음 주가 이번 주라 곧 나올 것 같다. 이전 세대 Qwen3.8 Flash Next 대비 Qwen4 Flash의 성능 그림을 보여 줬다. "벤치마크는 이제 믿을 게 못 되지만" 전 세대보다는 발전.
- 작은 모델 = 요즘은 **30B 이하**. 그중 체감 성능이 가장 좋았던 것이 **Qwen3.8 27B**(dense 모델)이고, 후속 **Qwen4 27B**를 빨리 써 보고 싶다.
- 중국의 빠른 증류 기술에 감탄. 가격이 저렴하다고 홍보하는데 실성능이 궁금하다.
- (모델 이름·출시 일정은 강사 발언이며 확인하지 않았다. 미확인.)

**4. pstack 플러그인 (09:33~21:32)**
- 참고할 프로젝트로 pstack을 골랐다. 구글에서 "pstack"을 검색하면 GitHub의 **Cursor 플러그인** 저장소(`plugins` 밑 `pstack`)가 나오고, Claude Code에도 설치할 수 있게 제공한다. (저장소 확인: Day06_new/info.md:4 — https://github.com/cursor/plugins/tree/main/pstack)
- 목적: 단순 설치가 아니라 "뜯어서 커스텀을 하는 게 사실 핵심."
- 만든 사람: Lauren Tan(닉네임 **poteto**). "코드를 적게 쓰고 품질을 높게" 하고 싶어 만들었다. README 표현은 "write less, but higher quality code"(공식 문서 확인: https://github.com/cursor/plugins/tree/main/pstack).
- 단점: "**토큰 엄청나게 잡아먹습니다.**" 사전 작업을 엄청 한다.
- 구성(Claude 분석 결과): 스킬 **58개**, 에이전트 **2개** — poteto 모드를 실행하면 항상 뜨는 **poteto 에이전트**(스킬 실행 에이전트)와, AI가 쓸데없이 다는 **주석을 지우는 에이전트**. 훅이나 MCP 서버가 없는 순수한 스킬·에이전트 플러그인. README에는 "all skills" 표 34개와 "twenty-four short skills, one principle each"가 있어 합치면 58로 보이고, 서브에이전트 이름은 poteto-agent와 Comment Sicko다(공식 문서 확인: https://github.com/cursor/plugins/tree/main/pstack). 58 = 34 + 24는 추정.
- 강조 이유: 스킬을 엮는 방식이 독특해서 "꼭 소개시켜 드리고 싶었다"(아래 6절).

**5. setup과 전역 rules (14:32~21:32)**
- setup pstack에서 **역할별로 모델과 추론 예산**을 고르고, 그 선택을 rules에 기록한다. 이 rules는 **전역(글로벌)**에 설치된다.
- 추론 예산: 스킬 기본값 **x high**, 최대, medium, small 중 기본(x high)을 골랐다("꽤 오래 걸리긴 할 겁니다").
- 코드 작성 역할 모델: 보통 **Sonnet**. "계획만 Opus가 짜고 코드는 Sonnet이" 낫다고 봤지만 취향 문제. 강사는 빠른 코드 결과를 위해 Sonnet. 패널 역할도 추천대로 Sonnet.
- 생성된 rules(모델스 파일)에는 Sonnet·x high, 버그픽스, 퍼포먼스 이슈, 힐클라임브, 익스플로러, 익스플레이너, 인베스티게이터 등 역할과 "코드 작업하는 녀석, 판단이나 글쓰기 하는 녀석, 패널" 구분이 적혀 있었다.
- 로드 시점: 경로(paths)를 지정한 규칙처럼 그 경로에 들어가야 나오는 게 아니라, 전역 rules는 **글로벌 CLAUDE.md가 로드된 다음에 바로** 로드된다고 설명했다. 공식 문서는 "Claude Code loads user-level rules before project rules"라고 적는다(공식 문서 확인: https://code.claude.com/docs/en/memory.md). 프로젝트 rules는 paths가 없으면 시작 때 `.claude/CLAUDE.md`와 같은 우선순위로 로드된다(저장소 확인: Day06_new/docs/sources/claude_code/01_instructions.md:64).
- pstack README 기준: Claude Code에서 setup은 `/pstack:setup-pstack`, rules 파일은 `~/.claude/rules/pstack-models.md`, 기본값은 코드 위임(feature, refactoring, bug fix, perf, hillclimb)이 grok, 판단·글쓰기는 opus 5.5다(공식 문서 확인: https://github.com/cursor/plugins/tree/main/pstack). 강의 화면의 선택지(Sonnet)와 README 기본값(grok)이 다르다. 설치 환경별 선택지 차이로 보이나 미확인.
- **reload plugins**: 같은 세션에서 막 설치했으면 setup 명령이 바로 안 보이므로 reload plugins를 실행하니 "이제서야 이렇게 커맨드가 뜨는" 것을 확인했다. (저장소 확인: Day06_new/docs/sources/claude_code/02_tools.md:170 — `/reload-plugins`는 대화형 전용이라 저장소 대장에서 미확인) 공식 문서: 셸에서 설치한 플러그인은 다음 시작 때나 이미 열린 세션에서 `/reload-plugins`를 실행하면 로드된다(공식 문서 확인: https://code.claude.com/docs/en/discover-plugins.md).
- **poteto 모드**: 작업을 지시할 때 쓰는 모드. "엄밀하게 해야 되는 작업을 시작할 때 좋다", "기본 시작 모드가 이거다"라고 생각하면 된다. 강사는 이것으로 **pstack 플러그인 자체의 심층 분석**을 의뢰했다(결과는 마크다운이든 HTML이든 나온다).

**6. disable-model-invocation과 플레이북 (31:41~39:08)**
- 분석 결과: 진입점은 모두 poteto 모드. 순서는 목표를 다시 말하고(리프레젠테이션인지 강사도 해석이 모호하다고 함) → 요청을 **23개 플레이북** 중 하나에 맞추고 → 별도 분류 코드 없이 **모델이 플레이북 한 줄 설명을 읽고 고르고**("아 스킬이구나") → 플레이북의 단계를 그대로 복사해 **단계를 바꾸지 않고** 따르며 → 역할별로 정해진 모델로 하위 에이전트를 띄우고 → **리뷰 대기 상태의 PR**을 열며 종료.
- 23개 플레이북은 이 사람이 작업하며 얻은 결과를 케이스 스터디로 정리한 것. "나랑 같거나 다르면 필요한 건 취하고 아닌 건 바꾸고."
- **`disable-model-invocation: true`**: 아무 스킬이나 열어 보니 이 설정이 있었다. 모델이 직접 이 스킬을 호출할 수 없다. "스킬은 모델이 호출하라고 만들어 놓은 건데" 컨셉에 반하는 설정으로, 프로그램(또는 사용자)이 호출하겠다는 뜻. 모델에게는 이 스킬이 **스킬 목록에도 넘어가지 않는다**. (저장소 확인: Day06_new/docs/sources/claude_code/01_instructions.md:160 — "Claude can't invoke the skill on its own.", :163 — "Description not in context, full skill loads when invoked")
- 모델이 스스로 고를 수 있는 스킬은 **pstack setup 하나뿐**. 나머지는 실행 중인 스킬이 다른 스킬의 md 파일을 **read로 직접 읽어서** 쓴다. "첫 번째 스킬에 스킬들을 다 엮어 놓은 방식"으로, "저기 가면 이거 읽고 이거 읽고 다시 돌아와" 같은 지시만 해 둔 것.
- **poteto 모드조차 disable**: 사용자만 실행할 수 있다(강사가 슬래시로 직접 실행). "모델은 절대로 지가 알아서 이 poteto 모드를 줄 수 없음." → **무한 루프를 막은 것**.
- 강조 이유: 스킬은 "모델이 네임과 디스크립션으로 고르는 것"이라고 배웠지만 실제로 **고르지 못하는 스킬도 존재**한다. 이 옵션은 Claude Code·Cursor·Codex가 다 달라서 어디서 되고 안 되는지 단정하기 어렵다. Claude 기준으로는 이렇게 하면 모델이 실행할 수 없다.
- poteto 모드 설명 첫 줄에 "스킬의 SKILL.md를 찾아가서 읽어라"는 가이드가 있고, 나머지는 150줄에 달하는 꼼꼼한 설명(모델 지정, grok 설명 등)이라 강사 기준으로는 지워도 될 정보가 많다.

**7. 플레이북 폴더와 hill climb (39:08~42:54)**
- 플레이북 위치를 Claude에게 물어보니 **플러그인 캐시** 아래 poteto 모드 스킬 밑 `playbooks`에 있었다(전사: "플러그인스 캐시 … 모드 밑에 플레이북스").
- `bugfix` 플레이북: 15줄밖에 안 되지만 한 줄 한 줄이 매우 길다. "버그픽스를 할 때는 요렇게 하십시오"라는 작업 지침.
- **hill climb**: 중요한 플레이북 중 하나. 정해진 **수치 지표**로 떨어지는 작업을 반복해 개선할 때(언덕을 오르듯 목적지에 차근차근) 쓴다. 메트릭이 먼저 정해져 있어야 한다. 예) "모델 성능을 10% 개선하세요." 각 단계는 delegate(위임)한다.
- "물론 이걸 저는 그대로 활용하는 걸 추천드리진 않아요. … 필요한 것만 발췌하는 게 좋은데 그러려면 일단 써봐야 되거든요."

**8. superpowers (21:32~23:03)**
- pstack 외에 개발 작업용으로 괜찮은 플러그인. 올해 초중순에 많이 썼고 많은 사람이 효용을 느꼈지만, "너무 자세해서" 요즘 모델 성능에는 과하고 토큰을 많이 먹어 지금은 덜 찾는다. 업데이트는 잘 되고 있어 나쁘지 않다. 참고로만 소개. (저장소 확인: Day06_new/info.md:7 — https://github.com/obra/superpowers/)
- 강사는 이런 도구를 보면 "둘이 섞어서 쓸 수는 없나" 생각한다.

**9. 우로보로스(Ouroboros) — 계획 수립 (23:03~31:41)**
- 개발 자체는 이런 도구로 차근차근 진행할 수 있지만 "계획을 짜는 그게 제일 문제거든요." 계획에는 우로보로스를 추천. (저장소 확인: Day06_new/info.md:5 — https://github.com/Q00/ouroboros)
- **소크라테스식 논증법**으로 사용자에게 계속 질문하고, 질문에 대한 **근거를 파일로 남긴 뒤** 계획을 만들고 실행까지 해 준다. 강사는 실행은 맡기지 않고 **근거 파일**만 많이 활용한다. (저장소 확인: Day06/ouroboros/skills/interview/SKILL.md:3 — "Socratic interview to crystallize vague requirements")
- 스킬이 매우 많다(evaluate, interview 등). 강사는 **interview** 스킬을 가장 좋아해 가져다 쓴다. interview는 AskUserQuestion, 분석 모드, MCP로 다른 모델 호출, 서브에이전트에게 찾기 지시 등 다양하게 인터뷰를 수행한다. **개발이 아니어도** 충분히 쓸 수 있다.
- 약칭은 **`ooo`**("우로보로스의 약자를 ooo라고 쓰더라고요"). (저장소 확인: Day06/ouroboros/README.md:413-414 — `ooo setup`, `ooo interview`)

### 실습/데모 내용 (명령어, 파일 구조, 프롬프트, 코드 조각 등 원문 그대로 보존)
1. **pstack 설치 위치**: "플러그인 레벨을 설치할 때는 항상 제 홈 폴더에서 클로드를 실행", 정확히는 "점 클로드(`.claude`) 폴더가 있는 곳에서 실행" — 고쳐야(커스텀) 하기 때문.
2. **설치 방법(강의)**: GitHub pstack 링크를 복사해 Claude Code에 붙이고 "플러그인 분석 설치"를 요청 → Claude가 "후기(훅)나 MCP 서버가 없는 순수한 스킬 및 에이전트 플러그인"이라고 분석하며 설치.
   - pstack README의 Claude Code 설치 명령(공식 문서 확인: https://github.com/cursor/plugins/tree/main/pstack):
     ```
     /plugin marketplace add cursor/plugins
     /plugin install pstack@cursor-plugins
     ```
3. **setup**: 같은 세션이면 먼저 `reload plugins`(공식 명령 `/reload-plugins`) → setup pstack 실행(README상 `/pstack:setup-pstack`) → 추론 예산 `x high`(기본) → 코드 작성 역할 `Sonnet` → 패널 역할 추천대로 `Sonnet`.
4. **rules 확인**: 생성된 전역 rules의 모델스 파일 열기(README상 `~/.claude/rules/pstack-models.md`).
5. **심층 분석 의뢰**: poteto 모드(슬래시로 직접 실행, README상 `/pstack:poteto-mode`)로 "플러그인 심층분석" — 플러그인 그 자체를 분석시킴.
6. **아무 스킬 열어 보기**: frontmatter의 `disable-model-invocation: true` 확인.
7. **플레이북 찾기**: Claude에게 "플레이북 폴더는 어디에 있어?" → 플러그인 캐시 아래 `playbooks` → `bugfix`(15줄), `hill climb` 열람. 정확한 캐시 경로는 화면 낭독이 불분명해 미확인.
8. **우로보로스 설치(같은 폴더, 다른 세션)**: 설치 중 "구 버전이 발견이 돼서 신 버전으로 설치하겠다" 메시지. 설치 후 안내: "리스타트 클로드 코드, 런 ooo 셋업, 그 다음에 인터뷰" → 끄고 다시 켜서 `ooo setup`.
   - 저장소 스냅샷의 설치 명령(저장소 확인: Day06/ouroboros/README.md:263):
     ```bash
     claude plugin marketplace add Q00/ouroboros && claude plugin install ouroboros@ouroboros
     ```
     이어서 "Then run `ooo setup` inside a Claude Code session."(README.md:265)
9. **ooo setup 선택**: 백엔드를 모두 Claude로 — 오케스트레이터의 **런타임 백엔드 = Claude**, **LLM 백엔드 = Claude**. 이어서 "너의 글로벌 CLAUDE.md에 내가 이런 내용을 추가해도 되겠니?" → 선택 사항, 강사는 **스킵**(지금은 스킵이 recommend였다고 함). 저장소 스냅샷의 setup은 이 단계를 "CLAUDE.md integration (optional) — per-project"로 적고 선택지는 `[Integrate / Skip / Preview first]`다(저장소 확인: Day06/ouroboros/skills/setup/SKILL.md:32, :293). 강의의 "글로벌"과 스냅샷의 "per-project"가 다르다. 미확인.
10. **마무리 실습**:
    - pstack 세션은 끄고, 우로보로스 설치 세션에서 `clear`.
    - `ooo`를 쳐서 설치 확인(안 나오면 `reload plugins`). "ooo 인터뷰"라고 치면 "우로보로스 인터뷰"가 나온다. 슬래시 상태에서 interview를 치고 탭으로 자동 완성.
    - 인터뷰 입력(원문): **"pstack 플러그인을 내 작업 지침에 맞게 개선해서 나만의 플러그인으로 만들고 싶습니다."** + "플러그인을 분석하자" 취지.
    - 예상 동작: 명령 전에 pstack을 분석하고 "pstack에 이런 게 있는데 너 여기서 뭐 바꾸고 싶어?"로 출발. 오래 걸리므로 엔터 쳐 두고 2시까지 휴식, 세팅이 멈출 수 있으니 중간중간 확인.

### 강사 팁·주의사항
- 메모리는 많이 남기는 게 아니라 **작게 남겨도** 잘 동작한다. 무엇을 남길지는 작업 종류(개발인지 다른 서비스인지)에 따라 달라진다.
- 플러그인은 설치해서 쓰는 것보다 **뜯어서 커스텀**하는 것이 핵심. 그래서 `.claude` 폴더가 있는 곳(홈)에서 Claude를 띄워 설치한다.
- 같은 세션에서 설치한 플러그인 명령이 안 보이면 reload plugins.
- pstack은 품질은 좋지만 토큰을 매우 많이 쓴다. superpowers도 너무 자세해 요즘 모델엔 과하다.
- 계획은 Opus, 코드는 Sonnet 조합을 강사는 선호(취향). 빠른 코드 결과가 필요하면 Sonnet.
- 스킬은 "모델이 고른다"고만 알면 안 된다. `disable-model-invocation`으로 모델 목록에서 빼고, 진입 스킬이 다른 스킬 md를 read로 엮는 설계가 가능하다. 진입점도 사용자 전용으로 막아 무한 루프를 방지한다. 단, 이 옵션 동작은 Claude Code·Cursor·Codex마다 다르다.
- 남의 플레이북(pstack 23개)은 그대로 쓰지 말고 써 본 뒤 필요한 것만 발췌한다.
- hill climb은 수치 지표가 먼저 정해져 있어야 쓸 수 있다.
- 우로보로스는 실행까지 맡기기보다 인터뷰가 남긴 **근거 파일**을 활용하는 쪽이 강사 방식. 개발 외 업무에도 쓸 수 있다.
- 여러 Claude 창을 오가며 작업하면 헷갈리기 쉽다("이런 일이 정말 비일비재").

### 실제 프로젝트에 적용할 체크리스트 (- [ ] 행동 지침, 특정 프레임워크에 묶이지 않는 원칙 위주)
- [ ] 메모리를 계층(원 기록 → 노트 → 요약 표현 → 주입 컨텍스트)으로 나누고, 매 세션 주입되는 양은 작게 유지한다.
- [ ] 주기적으로 메모리를 정리·압축하는 단계를 두고, 내 작업 종류에 맞춰 "무엇을 남길지" 기준을 문서로 정한다.
- [ ] 메모리 시작 로드량의 상한(줄 수·크기)을 확인하고, 상한 밖 내용은 인덱스로만 가리킨다.
- [ ] 외부 플러그인·하네스는 설치 전에 에이전트에게 구성(스킬·에이전트·훅·MCP 유무)과 위험을 먼저 분석시킨다.
- [ ] 참고 하네스는 그대로 쓰지 말고 한 번 써 본 뒤 필요한 절차만 발췌해 내 지침으로 옮긴다.
- [ ] 진입점 하나가 정해진 절차 문서(플레이북) 중 하나를 고르고, 단계는 바꾸지 않고 따르게 하는 구조를 검토한다.
- [ ] 부작용이 있거나 순서가 중요한 절차는 모델이 스스로 부르지 못하게 하고(사용자·진입 절차만 호출), 진입점의 자기 호출로 생기는 무한 루프를 막는다.
- [ ] 스킬 호출 제어 옵션은 도구마다 동작이 다르므로, 쓰는 도구에서 실제로 모델 목록에서 빠지는지 확인한다.
- [ ] 역할별(계획·코드·판단·리뷰)로 모델과 추론 예산을 정하고, 그 결정을 항상 로드되는 규칙 파일에 기록한다.
- [ ] 수치 지표로 판정되는 개선 작업은 지표를 먼저 정한 뒤 단계별로 반복·위임한다.
- [ ] 계획 수립 단계에서는 질문 위주 인터뷰로 숨은 가정을 드러내고, 질문과 근거를 파일로 남겨 이후 계획·실행의 입력으로 쓴다.
- [ ] 토큰을 많이 쓰는 도구는 비용 대비 품질을 따져 범위를 좁혀 쓴다.
- [ ] 같은 세션에서 확장을 설치했다면 다시 로드해 명령이 보이는지 확인한다.

> 확인 필요:
> - 11:23~12:51 플러그인 분석 결과의 "위험은 없습니다"와 "위험인지 잘 모르겠네요"가 엇갈린다. "후기"는 훅(hook)의 오인식으로 보인다.
> - 17:23 "이 그룹 모델이 맞던 코드를 작성하는 역할"은 오인식으로 보이며, 역할별 모델 선택 질문으로 추정된다. 추론 예산 선택지(x high/최대/medium/small)도 화면 낭독이라 정확한 라벨은 미확인.
> - 19:55~20:37 rules에 적힌 역할 이름 중 "접지먼트"(judgment로 추정), "하티스트"(hardest로 추정) 등이 불분명하다.
> - 32:22 "다시 말한다는 게 뭐지, 그냥 리프레젠테이션인지"는 강사 본인도 문서의 한글 해석이 모호하다고 했다.
> - 38:27 "그록에 대한 설명"은 pstack README의 기본 코드 위임 모델 grok 설명으로 보인다(공식 문서 확인: https://github.com/cursor/plugins/tree/main/pstack). 화면과 같은 문구인지는 미확인.
> - 39:08 "pstack에 레이전트"는 `agents` 폴더로 추정. README 폴더 목록에는 `.cursor-plugin`, `agents`, `assets`, `automations/benny`, `docs`, `skills`가 있다.
> - 40:00 플레이북 위치 "플러그인스 캐시 … 모드 밑에 플레이북스"의 정확한 경로는 미확인(전사에 "스테이터 모드"로 들림, poteto 모드로 추정).
> - 08:35 "Claude에서 드리밍을 껐다 켰다 할 수 있다"는 공식 memory 문서에서 확인하지 못했다(미확인). 강의에서 "그것도 볼 거"라고 했으나 이 강에서는 다루지 않았다.
> - 04:48~07:02 Qwen4 출시 일정·모델명(Qwen4 27B, Qwen4 Flash, Qwen3.8 Flash Next)은 강사 발언 그대로이며 확인하지 않았다.
> - 01:38 OpenClaw·Hermes Agent의 드리밍 로직이 오픈소스라는 내용은 확인하지 않았다.
> - 28:13 "런 오 셋업"은 `ooo setup`으로 정정했다(저장소 확인: Day06/ouroboros/README.md:265). 43:44 "5555"로 전사된 부분도 `ooo`다.
> - 26:21~29:26, 30:57~31:41 설치 대기와 창 이동 구간은 발화가 적다.
