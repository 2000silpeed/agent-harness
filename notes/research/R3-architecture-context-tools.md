# R3 — 아키텍처·컨텍스트·도구 (S0, S2, S3, S4) 1차 자료 조사

대상 문서: `/home/user/agent-harness/kit/harness/METHOD.md` (저장소는 수정하지 않음)
조사일: 2026-11-11

## 0. 읽는 법

- 인용 신뢰도 표기
  - **[직]** 원문 페이지를 내려받아 텍스트로 바꾼 뒤 직접 읽고 옮긴 인용. 문자 단위로 대조했다(따옴표·아포스트로피 모양만 다를 수 있다).
  - **[원문반환]** WebFetch가 문서 마크다운을 그대로 돌려준 페이지에서 옮긴 인용. 신뢰할 만하다.
  - **[요약경유]** WebFetch의 소형 모델이 뽑아 준 인용. 문자 단위 대조를 못 했다. 문서에 인용문으로 넣기 전에 원문 확인이 필요하다.
- 출처 ID(A1, D1 …)는 2·3절에서 근거 표시로 쓴다. METHOD.md에 반영할 때는 지워도 된다.
- 수치는 전부 "그 출처가 자기 환경에서 잰 값"이다. METHOD.md에는 규칙이 아니라 **출발값(참고값)** 으로 적고, 우리 평가셋으로 다시 재야 한다.
- 2절 제안문은 METHOD.md의 문체(평서문, 프레임워크 중립)에 맞춰 바로 옮길 수 있게 썼다. 특정 제품 이름은 근거 설명에만 둔다.

---

## 1. 출처별 핵심

### 1-1. Anthropic 엔지니어링 글

| ID | 출처 | 핵심 지침 (코딩 에이전트에 쓸 것) | 짧은 인용 | URL |
|---|---|---|---|---|
| A1 | Building effective agents [직] | ① 가장 단순한 해법에서 시작. 워크플로(코드가 경로 결정)와 에이전트(모델이 경로 결정)를 구분 ② 프레임워크는 프롬프트·응답을 가리므로 내부를 이해하고 쓴다 ③ 종료 조건(최대 반복) ④ 코딩이 에이전트에 맞는 이유는 테스트로 검증되기 때문 ⑤ 도구 형식: 모델이 인터넷에서 자주 본 형식, 줄 수 세기·이스케이프 부담 없는 형식, 절대 경로 강제(poka-yoke) | "we recommend finding the simplest solution possible, and only increasing complexity when needed" / "If you do use a framework, ensure you understand the underlying code." / "Writing a diff requires knowing how many lines are changing in the chunk header before the new code is written." / "we actually spent more time optimizing our tools than the overall prompt" | https://www.anthropic.com/engineering/building-effective-agents |
| A2 | Effective context engineering for AI agents [직] | ① 컨텍스트는 한정 자원(context rot). 최소·고신호 토큰 ② 시스템 프롬프트는 구역으로 나누되 형식 자체는 덜 중요해지는 중 ③ 최소 프롬프트 + 최고 모델로 시작해 실패 유형에 맞춰 추가 ④ just-in-time 검색: 경로 같은 가벼운 식별자만 들고 필요할 때 읽는다. 지침 파일은 미리, 나머지는 glob/grep(하이브리드) ⑤ 긴 작업 3기법: 압축, 구조화 노트, 서브에이전트. 압축 프롬프트는 재현율 먼저, 정밀도 나중 ⑥ 서브에이전트는 수만 토큰을 쓰고 1,000~2,000 토큰만 돌려준다 | "find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome" / "If a human engineer can’t definitively say which tool should be used in a given situation, an AI agent can’t be expected to do better." / "returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)" / "Start by maximizing recall ... then iterate to improve precision by eliminating superfluous content." / "although the exact formatting of prompts is likely becoming less important as models become more capable" | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| A3 | Writing effective tools for agents [직] | ① 프로토타입 → 평가 과제(현실적, 다중 호출) → 실행 → 대화 기록 읽기 → 에이전트와 함께 설명문 개선 → 별도 held-out 셋으로 과적합 확인 ② API 1:1 래핑 금지, 고빈도 작업 단위로 통합 ③ 이름 공간(접두/접미에 따라 결과가 달라지므로 평가로 고름) ④ 반환은 고신호만, 의미 있는 식별자, `response_format`(concise/detailed) ⑤ 페이지·범위·필터·잘라내기에 기본값, 잘랐을 때는 다음 행동을 안내 ⑥ 오류 메시지는 고치는 방법을 담는다 ⑦ 측정: 정확도 + 도구별 실행 시간, 호출 수, 토큰, 도구 오류 | "More tools don’t always lead to better outcomes." / "For Claude Code, we restrict tool responses to 25,000 tokens by default." / "rather than opaque error codes or tracebacks" / "lots of tool errors for invalid parameters might suggest tools could use clearer descriptions or better examples" / "We relied on held-out test sets to ensure we did not overfit" | https://www.anthropic.com/engineering/writing-tools-for-agents |
| A4 | How we built our multi-agent research system [직] | ① 멀티는 병렬성 높은 넓은 탐색에 강하다. 코딩은 병렬화 여지가 적고 에이전트 간 실시간 조율이 약하다 ② 비용: 에이전트 ≈ 채팅의 4배, 멀티 ≈ 15배 토큰 ③ 위임 계약 4요소: 목표, 출력 형식, 도구·출처 안내, 작업 경계 ④ 노력 규모 규칙을 프롬프트에 명시 ⑤ 서브에이전트 산출물은 파일로 쓰고 가벼운 참조만 돌려준다 ⑥ 오류 시 처음부터가 아니라 중단 지점에서 재개 ⑦ 도구가 실패 중임을 모델에 알리면 스스로 적응 ⑧ 도구 시험 에이전트가 설명문을 고쳐 완료 시간 40% 감소 | "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats" / "most coding tasks involve fewer truly parallelizable tasks than research" / "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries." / "Subagents call tools to store their work in external systems, then pass lightweight references back to the coordinator." | https://www.anthropic.com/engineering/multi-agent-research-system |
| A5 | Effective harnesses for long-running agents [직] | 컨텍스트 창을 넘는 코딩 작업의 구조: ① 첫 세션(초기화)과 이후 세션(코딩)의 프롬프트를 다르게 ② 인계 산출물: 기능 목록(JSON, `passes` 필드만 수정 허용), 진행 파일, git 커밋, 환경 기동 스크립트 ③ 한 번에 기능 하나 ④ 세션 시작 의식: 작업 디렉터리 확인 → 진행 파일·git log 읽기 → 기본 동작 시험 → 다음 항목 선택 ⑤ 세션 종료 시 "main에 병합해도 되는 상태" ⑥ 실패 유형 4가지(한 번에 다 하려 함, 조기 완료 선언, 시험 없이 완료 표시, 실행 방법 재탐색) | "compaction isn’t sufficient" / "a later agent instance would look around, see that progress had been made, and declare the job done" / "the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files" / "Claude’s tendency to mark a feature as complete without proper testing" | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents |
| A6 | Harness design for long-running application development [직] | ① 하네스 구성요소는 "모델이 혼자 못 한다"는 가정이며 모델이 바뀌면 낡는다. 한 번에 하나씩 빼 보며 확인 ② 자기 평가는 후하다. 만드는 쪽과 판정하는 쪽을 분리 ③ 압축과 컨텍스트 리셋은 다르다(리셋 = 새 에이전트 + 구조화된 인계). 필요 여부는 모델에 따라 다름 ④ 계획은 산출물·상위 설계 수준. 세부를 못박으면 오류가 전파 ⑤ 구현 전 "완료가 무엇인지" 합의(스프린트 계약), 에이전트 간 소통은 파일 ⑥ 평가자는 과제가 모델 단독 능력 경계 밖일 때만 값어치 ⑦ 비용: 단독 20분·$9 대 풀 하네스 6시간·$200, 단순화 후 3시간 50분·$124.70 | "every component in a harness encodes an assumption about what the model can't do on its own, and those assumptions are worth stress testing" / "agents tend to respond by confidently praising the work" / "While compaction preserves continuity, it doesn't give the agent a clean slate" / "It is worth the cost when the task sits beyond what the current model does reliably solo." / "removing one component at a time and reviewing what impact it had on the final result" | https://www.anthropic.com/engineering/harness-design-long-running-apps |
| A7 | Building agents with the Claude Agent SDK [직] | ① 루프: 컨텍스트 수집 → 행동 → 검증 → 반복 ② 에이전틱 검색(grep 등)으로 시작, 의미 검색은 속도가 필요할 때만 추가 ③ 서브에이전트의 두 용도: 병렬화, 컨텍스트 격리 ④ 검증 3종: 규칙(린트·타입), 시각, LLM 판정(가장 덜 견고) ⑤ 실패 분석 질문 목록 | "gather context -> take action -> verify work -> repeat" / "we suggest starting with agentic search, and only adding semantic search if you need faster results or more variations" / "Code linting is an excellent form of rules-based feedback." | https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk |
| A8 | Code execution with MCP [직] | 도구 정의와 중간 결과가 컨텍스트를 먹는다. 도구를 코드 API로 노출하고 에이전트가 코드를 써서 호출하면 필요한 정의만 읽고 결과를 실행 환경에서 걸러낸다. 샌드박스가 전제 | "This reduces the token usage from 150,000 tokens to 2,000 tokens—a time and cost saving of 98.7%." | https://www.anthropic.com/engineering/code-execution-with-mcp |
| A9 | Equipping agents for the real world with Agent Skills [직] | ① 점진적 공개 3단: 메타데이터(시작 시 로드) → SKILL.md 본문(관련 있을 때) → 딸린 파일(필요할 때) ② 결정적이어야 하는 일은 스킬 안의 스크립트로 ③ 평가에서 시작해 빈틈만 메운다 ④ 스킬은 신뢰할 수 있는 출처만, 설치 전 스크립트·의존성 감사 | "At startup, the agent pre-loads the name and description of every installed skill into its system prompt." / "We recommend installing skills only from trusted sources." | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills |
| A10 | Introducing advanced tool use [직] | ① MCP 5개 서버 58개 도구 ≈ 55K 토큰 ② 도구 검색(지연 로드): 정의 >10K 토큰 또는 도구 10개 이상일 때 쓰고, 10개 미만·전부 자주 쓰면 불필요. 정확도 49→74%(Opus 4), 79.5→88.1%(Opus 4.5). 캐시를 깨지 않음 ③ 코드로 도구 호출: 의존적 호출 3개 이상·큰 데이터 집계에 유리, 토큰 37% 감소. 모델이 중간 결과를 봐야 하는 일에는 불리 ④ 스키마만으로는 사용 패턴을 못 전한다 → 입력 예시 | "That's 58 tools consuming approximately 55K tokens before the conversation even starts." / "Average usage dropped from 43,588 to 27,297 tokens, a 37% reduction on complex research tasks." | https://www.anthropic.com/engineering/advanced-tool-use |
| A11 | Raising the bar on SWE-bench Verified (Claude 3.5 Sonnet) [직] | 코딩 에이전트 최소 뼈대 = 프롬프트 + 셸 도구 + 편집 도구. 편집은 문자열 치환(`old_str`가 정확히 1곳에서만 일치해야 적용, 아니면 오류로 재시도)이 가장 안정적. 절대 경로 강제. 프롬프트의 권장 순서: 저장소 탐색 → 오류 재현 스크립트 → 수정 → 재현 스크립트 재실행 → 경계 사례. 단계 전환은 강제하지 않음 | "The agent has a prompt, a Bash Tool for executing bash commands, and an Edit Tool, for viewing and editing files and directories." / "had the highest reliability with string replacement" / "The replacement will only occur if there is exactly one match of `old_str`." | https://www.anthropic.com/engineering/swe-bench-sonnet |
| A12 | Best practices for Claude Code (현행 문서) [직] | ① 지침은 비결정적(모델이 읽고 판단), 훅·거부 규칙은 결정적 ② 지침 파일에는 "저장소를 읽어도 알 수 없는 것"만: 검증 명령, 오해하기 쉬운 곳, 저장소 밖 결정, 두 번 고쳐 준 것 ③ 통과/실패가 나오는 검사를 준다. "완료" 주장에는 증거(명령과 출력) 요구 ④ 리뷰는 작성 과정을 못 본 새 컨텍스트로 ⑤ 서브에이전트의 값: 병렬, 시끄러운 출력 격리, 새 눈의 리뷰, 도구 제한. 같은 일을 넘긴다고 답이 좋아지지 않고, 컨텍스트를 다시 모으느라 더 느릴 수 있음 ⑥ 무인 실행 전 5문항 ⑦ "이제 안 해도 되는 것" 표 | "Only write down what Claude can't find by reading the repo, or what it would otherwise spend time rediscovering every session." / "Give Claude something it can run that comes back pass or fail." / "Handing the same task to a subagent doesn't make the answer any better." / "Whatever the scope, keep the enforced set small." | https://code.claude.com/docs/en/best-practices |
| A13 | Scaling Managed Agents: Decoupling the brain from the hands [요약경유] | 하네스(두뇌)·샌드박스와 도구(손)·세션 기록을 분리. 세션 기록이 하네스 밖에 있으면 하네스가 죽어도 마지막 이벤트에서 재개. 자격 증명은 샌드박스 밖 | "those assumptions need to be frequently questioned because they can go stale as models improve." | https://www.anthropic.com/engineering/managed-agents |
| A14 | Building a C compiler with a team of parallel Claudes [요약경유] | 병렬 쓰기 에이전트 사례(16개 에이전트, 약 2,000 세션, $20,000). 작업 잠금 파일, 테스트 하네스는 수천 바이트를 출력하지 말고 로그 파일로 보내며 오류 줄은 grep 가능하게, 빠른 표본 실행 옵션. 독립된 실패 테스트가 많을 때만 병렬이 쉬웠고 하나의 큰 과제에서는 서로 덮어씀 | "The test harness should not print thousands of useless bytes." | https://www.anthropic.com/engineering/building-c-compiler |

### 1-2. Anthropic API·Claude Code 문서

| ID | 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|---|
| D1 | Prompt caching [직] | ① 캐시 접두 순서는 `tools` → `system` → `messages`. 앞 단계가 바뀌면 뒤가 전부 무효 ② 도구 정의 변경은 전체 캐시 무효. 도구 선택 방식·이미지 변경은 메시지 캐시 무효. 사고·노력 설정 변경도 무효(범위는 모델별) ③ 수명 기본 5분(쓰기 1.25배), 1시간(2배), 읽기 0.1배(모델별 예외). 수명은 요청 **시작** 기준 ④ 최소 길이 모델별 512~4,096 토큰. 미만이면 오류 없이 캐시 안 됨 ⑤ 중단점 최대 4개, 조회는 20블록까지만 거슬러 올라감 ⑥ 매 요청 바뀌는 내용(시각 등)에 중단점을 걸면 영영 적중 없음 ⑦ 측정 필드: `cache_read_input_tokens`, `cache_creation_input_tokens`, `input_tokens` ⑧ 동시 요청은 첫 응답이 시작된 뒤에야 적중 | "Cache prefixes are created in the following order: `tools`, `system`, then `messages`." / "Modifying tool definitions (names, descriptions, parameters) invalidates the entire cache" / "The lookback window is 20 blocks." / "a cache entry only becomes available after the first response starts" | https://platform.claude.com/docs/en/build-with-claude/prompt-caching |
| D2 | Context editing [직] | 오래된 도구 결과를 임계값에서 자동 비움(자리표시 텍스트로 대체). 비우면 캐시가 깨지므로 한 번에 충분히 비우게 최소량을 정한다. 예시 설정: 30,000 입력 토큰에서 발동, 최근 도구 사용 3개 유지, 최소 5,000 토큰 비움, 특정 도구 제외 | "Tool result clearing: Invalidates cached prompt prefixes when content is cleared. To account for this, clear enough tokens to make the cache invalidation worthwhile." | https://platform.claude.com/docs/en/build-with-claude/context-editing |
| D3 | Compaction overview [직] | 압축은 긴 작업을 창 안에 두는 것뿐 아니라 품질 유지 수단. 최근 턴은 원문 유지 옵션, 요약 프롬프트 교체 가능 | "response quality degrades as a conversation grows" | https://platform.claude.com/docs/en/build-with-claude/compaction |
| D4 | Define tools — Best practices for tool definitions [직] | ① 설명문이 성능에 가장 큰 요인. 무엇을·언제(언제 아닌지)·인자 의미·제약을 최소 3~4문장 ② 복잡한 입력은 예시 ③ 관련 작업은 `action` 인자로 묶어 도구 수를 줄임 ④ 서비스 접두 이름 ⑤ 응답은 고신호 필드만 | "Provide extremely detailed descriptions. This is by far the most important factor in tool performance." / "Aim for at least 3–4 sentences for each tool description, more if the tool is complex." | https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools |
| D5 | Tool search tool [직] | 도구가 30~50개를 넘으면 선택 정확도가 떨어진다. 자주 쓰는 도구만 상시 로드, 나머지는 지연 로드 | "Claude’s ability to pick the right tool degrades once you exceed 30–50 available tools." | https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool |
| D6 | Memory tool [직] | 파일 기반 메모리, 실행은 클라이언트 쪽. 저장 위치·보존을 직접 통제. 경로 탈출 방지 필수. 작업 시작 전 메모리 디렉터리를 먼저 본다 | "The memory tool operates client-side" / "Your handler must reject paths outside `/memories`" | https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool |
| D7 | Skill authoring best practices [직] | ① 간결: 모델이 이미 아는 것은 쓰지 않는다 ② 자유도 조절(깨지기 쉬운 절차는 구체적으로) ③ 쓸 모델 전부로 시험 ④ 설명은 3인칭, 무엇+언제 ⑤ 본문 500줄 미만, 참조는 한 단계 깊이, 100줄 넘는 참조 파일은 맨 위에 목차 ⑥ 검증 루프(검사 → 수정 → 반복), 체크리스트 ⑦ 평가 먼저(시나리오 3개), 스킬 쓰는 인스턴스와 시험하는 인스턴스 분리 | "Create evaluations BEFORE writing extensive documentation." / "Keep the `SKILL.md` body under 500 lines for optimal performance." / "What works perfectly for Opus might need more detail for Haiku." | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| D8 | Choosing the right model [원문반환] | 두 출발법: 효율 우선(작은 모델로 시작해 부족하면 올림) / 능력 우선(강한 모델로 구현 후 내림). 고자율 코딩 에이전트는 능력 우선. 모델 교체 판단은 자체 평가셋으로. 모델을 바꾸기 전에 노력(effort) 조절이 더 나은 손잡이인 경우가 많음. 저가 실행자 + 상위 조언자, 오케스트레이터 + 저가 작업자 조합 | "Having a good evaluation set is the most important step in the process." / "Tuning effort is often a better lever than switching models." | https://platform.claude.com/docs/en/about-claude/models/choosing-a-model |
| D9 | Prompting best practices — long-horizon·state tracking·subagent [원문반환] | ① 첫 컨텍스트 창은 다른 프롬프트(테스트·셋업 스크립트 작성), 이후는 할 일 목록 반복 ② 테스트를 구조화 형식(`tests.json`)으로 관리, 테스트 삭제·수정 금지 문구 ③ 상태 데이터는 구조화 형식, 진행 메모는 자유 텍스트, git으로 상태 추적 ④ 압축 대신 새 창에서 파일 상태로 재개하는 선택지 ⑤ 서브에이전트 과용 경고: grep 한 번이면 될 탐색에 서브에이전트를 띄움 | "consider starting with a brand new context window rather than using compaction" / "the model might spawn subagents for code exploration when a direct grep call is faster and sufficient" | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices |
| C1 | Claude Code — memory(지침 파일) [직] | ① 지침 계층: 조직 관리 / 사용자 / 프로젝트 / 로컬(커밋 제외) / 경로 한정 규칙 ② 파일당 200줄 미만 목표. import로 쪼개도 컨텍스트 비용은 그대로 ③ 여러 파일은 덮어쓰기가 아니라 **이어 붙임**(루트 → 작업 디렉터리 순). 상충하면 임의로 하나를 고름 → 주기적 감사 ④ 하위 디렉터리 지침과 경로 한정 규칙은 그 파일을 다룰 때 로드 ⑤ 루트 지침은 압축 후 디스크에서 다시 주입, 대화로만 준 지시는 사라짐 ⑥ 자동 메모리 색인은 첫 200줄 또는 25KB만 로드, 상세는 주제 파일로 ⑦ 어떤 지침이 언제 로드됐는지 기록하는 수단 제공 | "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence." / "if two instructions contradict each other, Claude may pick one arbitrarily" / "All discovered files are concatenated into context rather than overriding each other." | https://code.claude.com/docs/en/memory |
| C2 | Claude Code — Extend Claude Code(기능 선택) [원문반환] | 기능을 **도입하는 계기** 표: 규칙·명령을 두 번 틀리면 지침 파일, 같은 절차를 세 번째 붙여넣으면 스킬, 시끄러운 부수 작업은 서브에이전트, 매번 일어나야 하면 훅. 기능별 컨텍스트 비용 표(지침 = 매 요청, 스킬 = 설명만 상시, 훅 = 0) | "You paste the same playbook or multi-step procedure into chat for the third time" / "An instruction like \"never edit `.env`\" in CLAUDE.md or a skill is a request, not a guarantee." | https://code.claude.com/docs/en/features-overview |
| C3 | Claude Code — context window [원문반환] | 압축 후 살아남는 것 표: 시스템 프롬프트 유지, 루트 지침·자동 메모리·계획 재주입, 읽거나 고친 파일은 최근 5개까지 재읽기(5,000 토큰 넘으면 경로만), 호출된 스킬 본문은 스킬당 5,000·합계 25,000 토큰 상한(앞부분만 유지), 훅이 넣은 컨텍스트는 요약에 섞임 | "put the most important instructions near the top of `SKILL.md`" | https://code.claude.com/docs/en/context-window |
| C4 | Claude Code — subagents [직] | 탐색용 내장 서브에이전트는 읽기 전용 도구만. 서브에이전트 설명 합계가 15,000 토큰을 넘으면 경고. 도구 제한은 프롬프트가 아니라 하네스가 강제. 턴 상한, 워크트리 격리 | "the subagent does that work in its own context and returns only the summary" | https://code.claude.com/docs/en/sub-agents |
| C5 | Claude Code — skills [직] | 설명+사용 시점 텍스트는 목록에서 1,536자에서 잘림 → 핵심 용도를 앞에. 부작용 있는 절차는 모델 호출 차단. 경로 패턴으로 자동 로드 범위 제한. 포크 컨텍스트 실행 | "the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing" | https://code.claude.com/docs/en/skills |
| C6 | Agent SDK overview [원문반환] | SDK가 주는 것: 내장 도구, 훅, 서브에이전트, MCP, 권한, 세션. API 직접 호출이면 도구 루프를 직접 짠다. 약관: 상용 약관 적용, 자체 제품에 구독 로그인 제공 불가(API 키), 브랜딩 제한 | "You write the tool loop yourself" | https://code.claude.com/docs/en/agent-sdk/overview |

### 1-3. OpenAI·공개 규격

| ID | 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|---|
| O1 | A practical guide to building agents (PDF) [직] | ① 에이전트가 맞는 일: 복잡한 판단, 유지가 어려운 규칙, 비정형 데이터. 아니면 결정적 해법 ② 모델: 가장 강한 모델로 기준선 → 정확도 목표 달성 → 작은 모델로 교체 ③ 싱글 에이전트를 먼저 최대화. 쪼개는 신호: 조건 분기가 많은 프롬프트, 도구 과부하(수보다 유사·중복이 문제) ④ 종료 조건: 최종 출력 도구, 도구 호출 없는 응답, 오류, 최대 턴 | "Our general recommendation is to maximize a single agent’s capabilities first." / "Some implementations successfully manage more than 15 well-defined, distinct tools while others struggle with fewer than 10 overlapping tools." / "build your agent prototype with the most capable model for every task to establish a performance baseline" | https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf |
| O2 | Codex — Custom instructions with AGENTS.md [직] | 전역 → 저장소 루트 → 현재 디렉터리 순으로 이어 붙임(디렉터리당 1개). 뒤에 오는 파일이 앞을 덮는다. 합계 32 KiB에서 중단. 빈 파일 무시. 로드된 지침을 요약시켜 확인하는 검증 절차 | "Codex concatenates files from the root down, joining them with blank lines." / "stops adding files once the combined size reaches the limit defined by project_doc_max_bytes (32 KiB by default)" | https://developers.openai.com/codex/guides/agents-md |
| O3 | Codex Prompting Guide [요약경유] | 하네스 권장: 전용 패치 도구, `rg`, 전용 읽기 도구, 계획 갱신 도구. 도구 출력은 약 10k 토큰으로 제한하고 앞·뒤 절반씩 남김. 병렬 도구 호출. 가장 쉬운 약 25% 작업은 계획 생략. 진전 없는 재읽기·재편집 제한 | "Unless asked for a plan, never end the interaction with only a plan." | https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide |
| O4 | apply_patch tool guide [요약경유] | 패치 형식(V4A)으로 생성·수정·삭제. 하네스가 적용하고 실패는 `failed` 상태와 명확한 메시지로 돌려준다. 경로 검증(디렉터리 탈출 방지), 패치 뒤 테스트·린트 실행 후 실패를 모델에 전달, 원자성(전부/파일별) 결정 | "Your patch harness is responsible for interpreting the V4A diff format and applying changes." | https://developers.openai.com/api/docs/guides/tools-apply-patch |
| O5 | Harness engineering: leveraging Codex in an agent-first world | **가져오지 못함(403).** 4절 참고 | — | https://openai.com/index/harness-engineering/ |
| X1 | AGENTS.md 규격 사이트 [직] | 필수 필드 없는 일반 마크다운. 권장 구역: 개요, 빌드·테스트 명령, 코드 스타일, 테스트 지침, 보안. 모노레포는 하위 패키지마다 두고 편집 파일에 가장 가까운 것이 우선. Linux Foundation 산하 Agentic AI Foundation 관리 | "The closest AGENTS.md to the edited file wins; explicit user chat prompts override everything." / "at time of writing the main OpenAI repo has 88 AGENTS.md files" | https://agents.md/ |
| X2 | Agent Skills 규격 [직] | `name` 최대 64자(소문자·숫자·하이픈), `description` 최대 1,024자. 메타데이터 약 100 토큰, 본문 5,000 토큰 미만 권장·500줄 미만, 참조 한 단계. 본문 형식 제한 없음. `scripts/`, `references/`, `assets/` | "Instructions (< 5000 tokens recommended)" / "Keep file references one level deep from SKILL.md." / "There are no format restrictions." | https://agentskills.io/specification |
| X3 | MCP 규격(tools, architecture) [직] | 호스트–클라이언트–서버. 로컬(stdio)과 원격(Streamable HTTP) 모두 MCP 서버. 도구 실행 오류는 결과에 `isError: true`로(프로토콜 오류와 구분). 도구 주석(읽기 전용·파괴적 등)은 신뢰된 서버가 아니면 불신. 도구 호출을 거부할 수 있는 사람이 있어야 함 | "there **SHOULD** always be a human in the loop with the ability to deny tool invocations" / "clients **MUST** consider tool annotations to be untrusted unless they come from trusted servers" | https://modelcontextprotocol.io/specification/2025-06-18/server/tools |

### 1-4. 실무자 글·논문

| ID | 출처 | 핵심 지침 | 짧은 인용 / 수치 | URL |
|---|---|---|---|---|
| P1 | SWE-agent: Agent-Computer Interfaces (arXiv 2405.15793) [직] | ACI 원칙 4개: 단순한 행동, 압축된 행동, 간결하되 정보가 있는 피드백, 가드레일. 절제 실험(SWE-bench Lite, GPT-4 Turbo, 기준 18.0%): 파일 뷰어 100줄 창이 최적(30줄 14.3%, 파일 전체 12.7%), 편집 시 린트로 문법 오류 편집을 거부하지 않으면 15.0%, 하나씩 넘겨 보는 검색은 검색 도구가 없을 때(15.7%)보다 나쁜 12.0%. 검색 결과 50개 초과면 결과 대신 "더 좁혀라". 출력이 없으면 없다고 명시. 최근 5개 이전 관찰은 한 줄로 접음. 궤적의 51.7%에서 편집 실패가 1회 이상 | "The search commands return at most 50 results for each search query" / "Guardrails mitigate error propagation and hasten recovery." (원문 HTML은 수식 렌더링 때문에 숫자가 겹쳐 보여 정리해 옮김) | https://arxiv.org/abs/2405.15793 |
| P2 | Aider — Repository map [직] | 저장소 전체의 파일·핵심 심볼·시그니처를 압축한 지도를 매 요청에 보냄. 의존 그래프 순위로 관련 부분만, 기본 예산 1k 토큰 | "defaults to 1k tokens" | https://aider.chat/docs/repomap.html |
| P3 | Aider — Unified diffs / Edit formats [직] | 편집 형식 원칙: 익숙한 형식, 단순(줄 번호·이스케이프 없음), 함수 단위의 높은 수준 편집, 적용은 관대하게. 형식 변경만으로 벤치마크 20% → 61%. 관대한 적용을 끄면 편집 오류 9배. 모델마다 맞는 형식이 다름 | "GPT is terrible at working with source code line numbers." / "Experiments where flexible patching is disabled show a 9X increase in editing errors" | https://aider.chat/docs/unified-diffs.html , https://aider.chat/docs/more/edit-formats.html |
| P4 | Cognition — Don't Build Multi-Agents [직] | 원칙 1: 컨텍스트(전체 궤적)를 공유. 원칙 2: 행동은 암묵적 결정을 담고, 상충하는 결정은 나쁜 결과. 기본은 단일 스레드. 서브에이전트는 잘 정의된 질문에 답하는 용도, 병렬 쓰기 금지. 작은 모델이 편집을 "적용"하게 하던 방식은 지시를 오해해 깨졌음 | "Share context, and share full agent traces, not just individual messages" / "Actions carry implicit decisions, and conflicting decisions carry bad results" | https://cognition.ai/blog/dont-build-multi-agents |
| P5 | Cognition — Multi-Agents: What's Actually Working (2026-04-22) [요약경유] | 통하는 것: 컨텍스트를 공유하지 않는 리뷰 에이전트, 읽기 전용 서브에이전트, 강한 모델끼리의 조언자 구성. 안 통하는 것: 병렬 쓰기. 약한 주 모델 + 강한 조언자는 실패 | "multi-agent systems work best today when writes stay single-threaded." | https://cognition.com/blog/multi-agents-working |
| P6 | Manus — Context Engineering for AI Agents [직] | ① KV 캐시 적중률이 운영 단계 최우선 지표. 입력:출력 ≈ 100:1 ② 접두 고정(시스템 프롬프트 앞에 시각 넣지 않기), 추가만 하기, 직렬화 결정적으로(JSON 키 순서) ③ 도구를 중간에 넣고 빼지 않는다. 대신 가릴 것(마스킹), 도구 이름 접두 통일 ④ 파일 시스템이 궁극의 컨텍스트. 압축은 복원 가능하게(경로·URL은 남김) ⑤ 할 일 파일을 계속 다시 써서 목표를 컨텍스트 끝으로 ⑥ 실패한 행동을 컨텍스트에서 지우지 않는다 ⑦ 자체 서빙이면 접두 캐시를 켜고 세션 ID로 같은 워커에 라우팅 | "the KV-cache hit rate is the single most important metric for a production-stage AI agent" / "avoid dynamically adding or removing tools mid-iteration" / "leave the wrong turns in the context" | https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus |

---

## 2. 단계별 보강안

### S0. 범위·기반 결정

**고민할 것 (추가·교체)**

0. **(신설, 맨 앞) 에이전트로 풀 일인가.** 단계 수와 경로를 미리 알 수 있으면 코드가 순서를 정하는 워크플로가 더 싸고 예측 가능하다. 에이전트는 단계 수를 예측할 수 없고, 결과를 자동으로 검증할 수 있을 때 쓴다. 판단 기준: ① 과거 사례에서 필요한 파일 수·단계 수가 건마다 다른가 ② 통과/실패로 돌아오는 검사(테스트, 빌드, 린트)가 있는가 ③ 건당 토큰 비용을 감당하는가(에이전트는 단발 호출의 여러 배, 서브에이전트를 쓰면 그보다 몇 배 더 든다). [A1, O1, A4]
1. **대상 작업 (기준 추가).** "완전히 맡길 수 있는 가장 작은 조각"에 **"자동 검증이 이미 있거나 붙일 수 있는 조각"** 을 더한다. 검사가 없으면 에이전트는 "된 것처럼 보이는" 지점에서 멈춘다. [A1 부록, A12]
2. **기반 (판단 기준 보강).** 기존 네 기준(소스 수정, 끼어들 지점, 사내 모델, 라이선스)에 아래를 더한다.
   - 모델에 실제로 들어가는 요청(시스템 프롬프트, 도구 정의, 메시지)과 응답 원문을 덤프할 수 있는가. 볼 수 없으면 고칠 수 없다. [A1]
   - 구성요소(계획 단계, 리뷰어, 압축, 서브에이전트)를 하나씩 끌 수 있는가. 모델이 바뀌면 필요 없어지는 것이 생긴다. [A6]
   - 컨텍스트 관리(압축 시점·요약 프롬프트, 오래된 도구 결과 정리, 캐시 중단점)를 우리가 제어할 수 있는가. [A2, D1, D2]
   - 세션 기록이 하네스 프로세스 밖에 남아 중단 지점에서 재개할 수 있는가. [A4, A13]
   - 공개 형식(지침 파일 AGENTS.md, 스킬 SKILL.md, MCP)을 읽는가. 읽는다면 지침·스킬·도구 자산이 기반과 무관해져 "기반은 나중에 바꿔도 된다"가 실제로 성립한다. [X1, X2, X3]
   - 선택지별 대가를 적는다: 포크(전부 고칠 수 있으나 상류 변경을 계속 따라가야 함) / SDK(도구·훅·서브에이전트·세션을 받지만 내부가 한 겹 가려지고 약관·모델 제약을 따름) / 직접 루프(몇 줄로 시작하지만 컨텍스트 관리·재개·권한을 전부 직접 만든다). [A1, C6]
3. **모델 (순서와 점검 항목 보강).**
   - 먼저 "쓸 수 있는 것 중 가장 강한 모델"로 기준선을 잡고, 목표 정확도에 닿은 뒤 내린다. 약한 모델로 시작하면 실패가 모델 한계인지 하네스 문제인지 가릴 수 없다. 역할별 모델 분리는 S0에서 후보 칸만 적고 교체는 S7에서 평가로 정한다. [O1, D8]
   - 코딩 에이전트용 점검표: 도구 호출 스키마 준수율, 우리가 쓸 편집 형식의 적용 성공률, 컨텍스트 창 크기, 접두 캐시 지원 여부(사내 서빙이면 접두 캐시 설정과 세션 단위 라우팅), 병렬 도구 호출, 추론 강도 조절 손잡이. [A11, P3, D1, P6, D8]
   - 모델을 바꾸면 하네스 가정(S2 구성요소 표)을 다시 본다. [A6]
4. **완료 정의 (무인 실행 5문항 추가).** 사람이 지켜보지 않는 실행을 목표로 하면 다섯 가지를 브리프에 적는다: 완료가 무엇인지 아는가 / 스스로 검사할 수 있는가 / 무엇을 건드릴 수 있는가 / 무엇이 멈추게 하는가(턴·비용 상한) / 결과가 어디로 가고 누가 승인하는가. [A12]
5. **성공 지표 (추가).** 건당 토큰 상한과 건당 최대 턴·시간을 목표값으로 적는다. 뒤 단계(S2 예산, S7 최적화)의 기준이 된다. [A4, A12]

**진행 (추가)**
- 기반 후보마다 같은 작은 작업(실패하는 테스트 하나 고치기)을 시키고, 요청·응답 원문을 덤프해 읽는다. 덤프가 안 되는 후보는 탈락 사유로 적는다. [A1]
- 모델 후보마다 편집 형식 스모크를 돈다: 같은 편집 과제 N건에서 적용 실패 수, 스키마 위반 수를 센다. N과 통과선은 돌리기 전에 정한다. [P3, A11]
- 기반이 기본으로 켜 두는 구성요소 목록을 뽑아 둔다(S2 구성요소 표의 재료).

**검증 (측정 가능한 신호)**
- 대상 작업의 과거 사례 중 자동 검사를 붙일 수 있는 비율(예: 최근 이슈·PR N건 중 몇 건).
- 선택한 기반에서 요청 원문 덤프와 구성요소 끄기가 되는지 예/아니오.
- 선택한 모델의 편집 적용 성공률, 스키마 위반 수, 캐시 사용 필드가 응답에 찍히는지.
- 무인 실행 5문항 각각에 "어떤 설정·파일로 보장하나"를 적을 수 있다.

**완료 기준 (추가)**
- [ ] 에이전트로 풀지 워크플로로 풀지 판단과 근거가 `design/decisions.md`에 있다
- [ ] 기반 후보별 스모크 결과(원문 덤프 가능 여부, 끌 수 있는 구성요소)가 브리프에 있다
- [ ] 기준선용 모델(가장 강한 허용 모델)과 나중에 내려 볼 후보 칸이 구분돼 적혀 있다
- [ ] 건당 토큰·턴·시간 상한 목표값이 있다

**흔한 함정 (추가):** 프롬프트를 가리는 추상화를 내부를 모른 채 쓰기, 약한 모델로 시작해 하네스로 메우기, 기반의 기본 구성요소를 전부 켠 채 무엇이 기여하는지 모르기, 검증 수단이 없는 작업을 첫 대상으로 고르기.

**순서와 병렬:** 대상 작업 결정(먼저) → 기반 후보 조사와 모델 후보 조사는 읽기 전용이라 동시에 → 기반×모델 조합 스모크는 한 번에 한 조합씩 → 승인. 대상 작업이 정해지기 전에는 스모크 과제를 고를 수 없으므로 앞당기지 않는다.

---

### S2. 뼈대·관측·기준선

**고민할 것 (추가·교체)**

1. **요청 한 건의 흐름 (보강).** 5단계 틀은 유지하되 세 가지를 정한다.
   - 단계 전환은 모델의 선언이 아니라 코드가 판정한다(승인 파일 상태, 테스트 종료 코드). 모델 안쪽의 진행(탐색 → 재현 → 수정 → 재실행)은 권장 순서로만 주고 강제하지 않는다. [A11, A1]
   - 계획에 담는 수준: 산출물, 수정 대상, 검증 방법까지. 구현 세부를 계획에서 못박으면 계획의 오류가 구현으로 번진다. [A6]
   - 구현 앞에 **재현**을 둔다: 버그면 실패하는 테스트나 재현 스크립트를 먼저 만들고, 같은 것을 수정 뒤에 다시 돌린다. [A11, A12]
   - 작업 크기에 따른 깊이: 한 줄 수정에 전체 계획·리뷰를 태우면 비용만 든다. 계획 게이트를 반드시 유지해야 한다면(인수 기준) 양식은 같되 크기별 최소 분량을 정한다. [A4의 노력 규모 규칙, O3]
2. **검증을 누가 하나 (신설).** 만든 에이전트의 자기 평가는 후하다. 판정은 ① 코드(테스트·린트·타입) ② 작성 과정을 보지 않은 독립 컨텍스트의 리뷰어 ③ 사람 순으로 둔다. 리뷰어에게는 "정확성에 영향을 주는 것만, 스타일 제외" 같은 범위를 준다. 범위 없는 리뷰어는 항상 무언가를 찾아내고, 전부 반영하면 불필요한 추상화가 쌓인다. [A6, A12, A7]
3. **쪼갤 것인가 (판단표로 교체).**

   | 쪼개도 되는 경우 | 조건 | 근거 |
   |---|---|---|
   | 코드 탐색·조사 | 읽기 전용, 질문이 잘 정의됨, 출력이 메인에 다시 쓰이지 않을 만큼 큼 | A2, P4, C4 |
   | 독립 리뷰 | 작성 컨텍스트를 공유하지 않음, 편집 도구 없음 | A6, A12, P5 |
   | 시끄러운 출력 격리 | 전체 테스트 실행, 넓은 검색 | A12 |
   | 독립 작업 병렬 | 서로 다른 파일·체크아웃, 결과가 서로의 가정에 의존하지 않음 | A12, A14 |

   쪼개면 안 되는 경우: 같은 작업 트리에 여러 에이전트가 동시에 쓰기, 서로의 결정을 알아야 하는 하위 작업, "더 좋은 답"을 기대한 단순 위임. 쓰기는 단일 스레드로 둔다. [P4, P5, A4, A12]
   쪼개는 비용도 적는다: 토큰이 몇 배로 늘고, 서브에이전트가 이미 있던 컨텍스트를 다시 모으느라 더 느릴 수 있다. [A4, A12]
4. **한 컨텍스트 창을 넘는 작업 (신설).** 대상 작업이 한 창에 안 끝날 수 있으면 압축만으로는 부족하다. 세션 사이를 잇는 **인계 산출물**을 정한다. [A5, A6, D9]
   - 상태 파일(구조화 형식): 항목별 완료 여부. 에이전트는 완료 표시만 바꿀 수 있고 항목을 지우거나 고칠 수 없다.
   - 진행 메모(자유 서술): 무엇을 했고 다음에 무엇을 할지.
   - 커밋: 작업 단위마다 설명 있는 커밋. 되돌릴 지점이 된다.
   - 환경 기동·검사 스크립트: 새 세션이 실행 방법을 다시 찾지 않게.
   - 압축으로 이어 갈지, 새 컨텍스트로 리셋하고 인계 산출물로 재개할지는 모델에 따라 다르므로 평가로 정한다.
5. **재개 (신설).** 요청이 중간에 죽으면 처음부터가 아니라 마지막으로 기록된 이벤트에서 이어 간다. 그러려면 기록(S2의 로그)이 하네스 프로세스와 따로 살아 있어야 한다. [A4, A13]
6. **지표 (추가).** 기존 네 가지에 도구 오류율, 편집 적용 실패율, 캐시 읽기·쓰기 토큰, 컨텍스트 최대 사용량, 서브에이전트 반환 크기를 더한다. 뒤의 S3·S4·S7이 전부 이 수치로 판정한다. [A3, P6, D1, P1]
7. **종료 조건과 예산 (보강).** 최대 턴·시간·비용 외에 **무진전 감지**(같은 파일 재읽기·같은 편집 반복, 같은 오류 연속)를 넣는다. 같은 교정이 두 번 실패하면 이어 가지 말고 컨텍스트를 비우고 배운 것을 넣어 다시 시작하는 편이 낫다. 강제 장치(끝내기 전 검사)가 무한히 막지 않도록 반복 상한을 두고, 상한에 걸린 종료는 "완료"가 아닌 별도 상태로 기록한다. [A1, O1, O3, A12]
8. **구성요소마다 무엇을 가정하나 (신설).** 하네스의 각 부품은 "모델이 혼자서는 이것을 못 한다"는 가정이다. 표로 적어 두고 모델이 바뀌면 다시 확인한다. [A6]

**진행 (추가)**
- 가장 작은 구성(프롬프트 + 셸 + 편집 도구)으로 작은 작업 하나를 끝까지 돌려 본 뒤, 기반 기본 구성으로 같은 작업을 돌려 차이를 본다. [A11, A2]
- 구성요소 표를 쓴다: 구성요소 / 가정 / 끄는 방법 / 껐을 때 평가 결과(나중에 채움). 뺄 때는 한 번에 하나씩 뺀다. [A6]
- 서브에이전트를 둔다면 위임 양식을 정한다: 목표, 출력 형식, 쓸 도구·출처, 하지 말 것(경계), 노력 상한(도구 호출 수), 반환 크기 상한. 큰 산출물은 파일로 쓰고 경로만 돌려준다. [A4, A2]
- 긴 작업이 대상이면 세션 시작 절차를 고정한다: 작업 디렉터리 확인 → 진행 메모·상태 파일·최근 커밋 읽기 → 기본 동작 검사 실행 → 미완 항목 하나 선택. 세션 끝 절차: 검사 통과 → 커밋 → 진행 메모 갱신. [A5]
- 완료 보고에는 실행한 명령과 출력(증거)을 붙이게 한다. [A12]

**검증 (측정 가능한 신호)**
- **중단·재개 시험:** 실행 중인 요청을 강제로 죽인 뒤 다시 시작한다. 처음부터가 아니라 이어서 끝나는가. 재개 직후 도구 호출이 상태 파악(진행 메모, 커밋 기록, 기본 검사)인가.
- **조기 완료 시험:** 미완 항목이 남은 상태에서 새 세션을 시작한다. "완료"로 끝내는 비율이 0인가.
- **자기 평가 대 독립 판정:** 에이전트가 완료라고 보고한 건 중 숨긴 테스트가 실패한 비율(거짓 완료율).
- **쪼갬 비교:** 싱글과 서브에이전트 구성을 같은 평가셋·같은 조건으로 돌려 성공률, 토큰, 지연을 나란히 적는다. 성공률이 같으면 싱글을 택한다.
- **위임 품질:** 서브에이전트 반환 토큰 분포, 메인이 같은 탐색을 다시 한 횟수(재탐색이 잦으면 위임 양식이 부실).
- **무진전 감지:** 일부러 풀 수 없는 과제를 줘서 예산 안에서 정해진 종료 상태로 끝나는지.
- 기록에 캐시 읽기·쓰기 토큰과 도구 오류가 이벤트로 남는지.

**완료 기준 (추가)**
- [ ] 구성요소 표(구성요소·가정·끄는 방법)가 `design/02-baseline.md`에 있다
- [ ] 쪼갬 판단(싱글 유지 또는 분리)과 비교 수치가 있다
- [ ] (대상 작업이 한 창을 넘을 수 있으면) 인계 산출물 형식과 세션 시작·종료 절차가 정해졌고 중단·재개 시험을 통과했다
- [ ] 종료 상태에 "예산 초과"와 "무진전 중단"이 완료와 구분돼 기록된다
- [ ] 기준선 표에 도구 오류율, 편집 실패율, 캐시 읽기 비율, 거짓 완료율이 추가됐다

**흔한 함정 (추가):** 계획에서 구현 세부까지 못박기, 같은 작업 트리에 병렬로 쓰게 하기, 서브에이전트에 한 줄짜리 지시 주기, 압축만 믿고 긴 작업 맡기기, 진척이 보인다는 이유로 완료 선언을 받아들이기, 구성요소를 한꺼번에 덜어내고 무엇이 필요했는지 모르기, 범위 없는 리뷰어의 지적을 전부 반영하기.

**순서와 병렬**
- 뼈대 구동과 기록 스키마 설계는 동시에 할 수 있다. 기준선 측정은 둘 다 끝나고 구성을 동결한 뒤 한다.
- 실행 시점의 규칙: 읽기 전용 탐색과 독립 리뷰는 병렬로 돌려도 된다. 코드 쓰기는 한 번에 한 에이전트다. 병렬 쓰기가 꼭 필요하면 체크아웃을 분리하고 병합을 한 곳에서 순서대로 한다. [P4, P5, A12, A14]
- 구성요소 절제(하나씩 끄기)는 순차다. 두 개를 같이 끄면 어느 쪽 영향인지 모른다.

---

### S3. 컨텍스트·지식·메모리

**고민할 것 (추가·교체)**

1. **우리 규칙을 어디에 적나 (보강).**
   - 넣을 것의 기준을 둔다: 저장소를 읽어도 알 수 없거나 매 세션 다시 찾아야 하는 것만. 구체적으로 ① 검증 명령(테스트 하나만 돌리는 법, 타입 검사, 린트) ② 코드가 오해를 부르는 곳(따라 하면 안 되는 옛 패턴, 안 쓰는 것처럼 보이지만 쓰는 디렉터리) ③ 저장소에 없는 결정 ④ 두 번 이상 교정한 것. 아키텍처 설명과 파일 배치 설명은 넣지 않는다(모델이 직접 읽는다). [A12, C1]
   - 계층이 겹칠 때의 규칙을 정한다. 기반마다 다르다: 이어 붙이고 상충은 임의로 처리하는 것도 있고, 가까운 파일이 덮는 것도 있다. 우리 기반이 어느 쪽인지 확인하고, 상충이 생기지 않게 주기적으로 감사한다. [C1, O2, X1]
   - 합계 상한을 정한다. 파일당 줄 수뿐 아니라 세션 시작 때 로드되는 지침 전체의 토큰(또는 바이트). 쪼개서 가져오기(import)만 해서는 비용이 줄지 않는다. 줄이려면 특정 경로에서만 로드되는 규칙이나 스킬로 옮긴다. [C1, O2]
   - 파일 이름은 여러 도구가 읽는 공개 형식을 우선한다(기반 교체 비용). [X1]
   - 어떤 지침 파일이 언제 로드됐는지 기록에 남긴다. [C1, O2]
2. (유지) 기존 노하우를 누가 옮기나.
3. **코드 탐색 방식 (교체).** 두 가지를 따로 정한다.
   - **찾는 방법:** 기본은 에이전틱 검색(파일 목록, 문자열 검색, 범위 읽기)이다. 색인이 낡는 문제가 없다. 다음 신호가 측정되면 보조 수단을 더한다: 심볼 정의·참조를 찾느라 파일을 많이 읽는다 → 언어 서버나 심볼 색인 / 모델의 탐색이 약하거나 창이 작다 → 저장소 지도(파일·심볼 요약을 토큰 예산 안에서 주입) / 탐색 지연이 목표를 넘는다 → 의미 검색. [A2, A7, P2, C2]
   - **어디서 찾나(격리):** 탐색을 서브에이전트로 보낼지는 조건으로 정한다. 보낸다: 질문이 잘 정의됐고, 읽을 양이 많고, 읽은 원문을 메인이 다시 쓰지 않는다. 직접 한다: 검색 한두 번이면 되는 조회, 읽은 코드를 곧바로 고쳐야 하는 경우. 창이 작은 모델일수록 격리의 이득이 크고, 창이 큰 모델에서는 병렬·잡음 격리가 주된 이유다. [A2, A12, D9, P4]
   - 탐색을 작은 모델에 맡기려면 평가로 확인한다(탐색 재현율: 정답 변경이 건드린 파일을 찾아냈는가). 작은 모델이 지시를 오해해 깨진 사례가 있다. [P4, P5]
4. **프롬프트 배치와 캐시 (교체).** "고정은 앞, 변동은 뒤"를 다음으로 구체화한다. [D1, P6, D2]
   - 순서: 도구 정의 → 시스템 프롬프트 → 대화. 앞이 바뀌면 뒤 캐시가 전부 무효다. 그러므로 **도구 정의와 시스템 프롬프트는 세션 중에 바꾸지 않는다.** 도구를 상황별로 제한해야 하면 정의를 빼지 말고 호출을 막거나(권한·마스킹) 지연 로드를 쓴다.
   - 날짜·시각, 검색된 경험, 강제 로드한 스킬 본문 같은 변동값은 시스템 프롬프트가 아니라 메시지로 넣는다.
   - 직렬화를 결정적으로 한다(키 순서, 공백). 같은 내용이 다른 바이트로 나가면 캐시가 조용히 깨진다.
   - 모델, 추론 강도 설정을 세션 중에 바꾸면 캐시가 깨질 수 있다. 바꾸는 지점을 정해 둔다.
   - 캐시 수명과 최소 길이를 확인한다. 사람 승인 대기처럼 수명보다 긴 공백이 흐름에 있으면 그 뒤 첫 요청은 전액이다. 병렬 요청은 첫 응답이 시작된 뒤 보내야 적중한다.
   - 사내 서빙이면 접두 캐시를 켜고 같은 세션이 같은 워커로 가게 라우팅한다.
5. **컨텍스트를 언제, 어떻게 줄이나 (신설, 기존 "압축 방식"을 확장).** [A2, D2, D3, P6, C3, A6]
   - 손잡이는 가벼운 것부터 셋이다: 오래된 도구 결과 비우기 → 요약 압축 → 리셋(새 컨텍스트 + 인계 산출물).
   - 줄이는 것은 캐시를 깨는 사건이다. 조금씩 자주가 아니라 임계값에서 한 번에 충분히 비운다(발동 임계값, 최소 비움량, 남길 최근 호출 수를 정한다).
   - 압축에서 살아남아야 하는 것을 목록으로 정한다: 작업 목표, 계획과 승인 상태, 수정한 파일 목록, 검증 명령, 금지 행동, 미해결 오류. 지침 파일과 계획은 요약에 맡기지 말고 디스크에서 다시 주입한다. 대화로만 준 지시는 사라진다고 가정한다.
   - 요약은 복원 가능하게: 원문을 버려도 경로·URL은 남긴다.
   - 실패한 시도와 오류는 지우지 않는다. 같은 실수를 반복하지 않는 근거다.
6. **무엇을 기억하나 (보강).** 규칙·경험에 더해 **작업 중 상태**(할 일 목록, 진행 메모)를 별도 층으로 둔다. 할 일 목록을 계속 갱신하면 목표가 컨텍스트 끝에 다시 놓인다. 세션 간 메모리는 색인 한 파일(줄 수·크기 상한) + 주제별 파일로 두고, 색인만 상시 로드한다. 메모리 저장소는 쓰기 경로를 제한한다(경로 탈출 방지). [A2, P6, C1, D6]
7. (유지) 모델이 고르지 않아도 되는 판단 — 단, 코드로 강제 로드한 내용은 메시지로 붙인다(4번).

**진행 (추가·교체)**
- 지침 파일의 구역을 통일한다(마크다운 제목이든 태그든 하나로). 형식보다 내용의 구체성이 중요하다: "코드를 잘 정리하라"가 아니라 실행할 명령과 경로를 적는다. [A2, C1, X1]
- 지침 파일의 각 줄에 대해 묻는다: 코드를 읽으면 알 수 있는가, 실제로 찾아볼 것인가. 둘 다 예면 지운다. [A12]
- 탐색 위임 양식에 경계(하지 말 것), 노력 상한, 반환 크기 상한을 더한다. [A4, A2]
- 압축 프롬프트를 실제 긴 실행 기록으로 조정한다. 먼저 빠뜨리는 것이 없게(재현율), 그다음 군더더기를 줄인다(정밀도). [A2]
- 캐시 측정을 붙인다: 요청마다 캐시 읽기·쓰기·비캐시 입력 토큰을 기록한다. [D1]
- 캐시를 깨는 사건 목록을 문서로 둔다(도구 변경, 시스템 프롬프트 변경, 모델·설정 변경, 컨텍스트 정리, 수명 만료).

**검증 (측정 가능한 신호)**
- **세션 시작 로드량:** 첫 요청의 입력 토큰을 구성별로(시스템, 도구 정의, 지침, 스킬 메타데이터, 메모리 색인). 목표값은 미리 정한다.
- **캐시 읽기 비율:** 캐시 읽기 ÷ (캐시 읽기 + 캐시 쓰기 + 비캐시 입력). 요청 단위와 세션 단위로. 두 번째 요청부터 접두가 읽히는지, 비율이 떨어진 요청마다 원인이 "캐시를 깨는 사건 목록"에 있는지 확인한다.
- **접두 안정성 시험:** 같은 세션의 연속 두 요청에서 시스템 프롬프트와 도구 정의의 바이트가 같은가(해시 비교).
- **지침 준수 탐침:** 지침의 규칙 N개를 새 세션에서 각각 건드리는 과제로 시험해 준수 건수를 센다. 지침을 줄이기 전후로 비교한다.
- **압축 생존 시험:** 강제로 압축(또는 리셋)한 직후, 살아남아야 할 목록의 항목을 에이전트가 여전히 지키는가(승인 상태, 검증 명령, 금지 행동, 수정 파일 목록).
- **탐색 품질:** 탐색 재현율(정답 변경 파일 중 찾아낸 비율), 탐색에 쓴 토큰, 메인으로 들어온 토큰. 격리 전후 비교.
- **규칙을 몰라서 틀린 실패 유형**의 건수(기존 유지).

**완료 기준 (교체)**
- [ ] 지침 계층, 겹칠 때의 규칙, 합계 상한, 담당자가 정해졌다
- [ ] 상시 로드 지침이 상한 안이고 "코드에서 알 수 있는 것"이 제거됐다
- [ ] 탐색 방식(검색 수단, 격리 조건)이 정해졌고 재현율 수치가 있다
- [ ] 시스템 프롬프트와 도구 정의가 세션 중 바뀌지 않음을 해시로 확인했다
- [ ] 컨텍스트 줄이기 정책(임계값, 최소 비움량, 생존 목록)이 있고 압축 생존 시험을 통과했다
- [ ] 평가 회귀가 없고 세션 시작 로드량·캐시 읽기 비율·컨텍스트 최대 사용량이 `design/03-context.md`에 있다

**흔한 함정 (추가):** 시스템 프롬프트에 시각·요청별 값을 넣기, 세션 중에 도구를 넣고 빼기, 쪼개서 가져오기만 하고 줄였다고 믿기, 대화로만 준 지시가 압축 뒤에도 남는다고 믿기, 조금씩 자주 비워 캐시를 매번 깨기, 검색 한 번이면 될 조회를 서브에이전트로 보내기, 강조 문구(반드시, 중요)를 더해서 준수율을 올리려 하기(안 지켜지는 규칙은 파일을 줄이거나 강제 장치로 옮긴다), 실패한 시도를 기록에서 지워 깨끗하게 보이기.

**순서와 병렬**
- 지침 파일 작성, 탐색 방식 실험, 메모리 구조 설계는 서로 독립이라 동시에 할 수 있다.
- **캐시 측정은 S4의 도구 정의가 동결된 뒤에 한다.** 도구 정의가 캐시 접두의 맨 앞이라 S4에서 설명문 한 줄을 고쳐도 S3의 캐시 수치가 바뀐다. S3·S4를 병렬로 만들 수는 있으나 "도구 스키마 동결 → 캐시·로드량 측정" 순서는 지킨다. [D1]
- 세션 시작 로드량은 S4의 스킬 수(메타데이터)에 따라 달라진다. S4 반영 뒤 다시 잰다. [A9, C2]
- 압축 정책은 S5의 계획 승인 상태를 살려야 하므로 S5의 계획 양식이 정해진 뒤 생존 시험을 다시 돈다.

---

### S4. 도구·스킬

**고민할 것 (추가·교체)**

1. **최소 도구 세트 (보강).** 시작은 셸 + 편집(보기 포함)으로도 된다. 전용 도구는 측정된 실패(잘못된 경로, 과도한 출력, 편집 실패)를 막을 때 더한다. 도구가 겹치면 사람도 어느 것을 쓸지 못 고른다는 것이 신호다. [A11, A2, O1]
2. **편집 형식 (신설, 코딩 에이전트의 핵심 결정).** [A11, A1, P3, P1, O4]
   - 후보: 문자열 치환(바꿀 원문이 정확히 한 곳에서만 일치해야 적용), 검색/치환 블록, 통합 diff 변형, 패치 문법, 파일 전체 다시 쓰기.
   - 고르는 기준: 모델이 학습에서 자주 본 형식인가 / 줄 번호·줄 수·이스케이프를 모델이 세지 않아도 되는가 / 일치가 0곳이거나 2곳 이상일 때 조용히 넘어가지 않고 무엇이 문제인지 알려 주는가 / 큰 파일에서 출력 토큰이 감당되는가.
   - 모델마다 맞는 형식이 다르다. S0에서 고른 모델로 적용 성공률을 재서 정한다. 모델을 바꾸면 다시 잰다.
   - 편집 뒤 문법 검사(린트)를 걸어 문법을 깨는 편집은 적용하지 않고 오류와 앞뒤 코드를 돌려준다.
   - 경로는 절대 경로만 받는다. 작업 디렉터리 밖 경로는 거부한다.
3. **읽기·검색 도구의 출력 규격 (신설).** [P1, A3, O3]
   - 파일 읽기: 줄 번호와 범위 지정. 기본 창 크기를 둔다(너무 작아도, 파일 전체여도 성능이 떨어진 실험이 있다).
   - 검색: 결과 수 상한. 넘으면 일부를 쏟아내지 말고 "더 좁혀라"와 좁히는 방법을 돌려준다.
   - 출력 상한: 도구 응답 토큰 상한을 정하고, 잘랐으면 잘렸다는 사실과 나머지를 보는 방법(범위, 필터)을 알린다.
   - 출력이 없으면 "성공했고 출력 없음"이라고 명시한다.
4. **테스트 실행 도구 (신설).** 통과/실패 요약과 실패한 항목만 돌려주고 전체 로그는 파일에 둔 뒤 경로를 준다. 오류 줄은 한 줄에 원인이 같이 있게 해 검색으로 찾을 수 있게 한다. 빠른 부분 실행(관련 테스트만)과 전체 실행을 구분한다. [A14, A3, A5]
5. **도구가 돌려주는 것 (교체).** "요약을 돌려준다"는 코드 읽기에는 맞지 않는다(정확한 원문이 필요하다). 원칙은 **범위·필터·페이지로 필요한 만큼만, 기본값은 작게**다. 식별자는 뜻이 있는 것으로(경로, 이름). 간결/상세를 인자로 고르게 할 수 있다. 응답 형식(JSON, 마크다운 등)은 평가로 고른다. [A3, D4]
6. **오류 정책 (교체).** 모든 실패를 모델에 알린다. 다만 종류를 나눈다. [A3, A4, X3, P6]
   - 모델이 고칠 수 있는 것(잘못된 인자, 일치 없음): 무엇이 틀렸고 어떻게 고치는지, 올바른 입력 예시와 함께.
   - 모델이 고칠 수 없는 것(연결 실패, 권한 없음): 재시도하지 말고 보고하라는 안내와 함께.
   - 하네스가 자동 재시도한 일시 오류: 재시도가 끝난 뒤 결과와 횟수를 알리고 기록에 남긴다.
   - 빈 결과, 실행 오류, 연결 실패는 서로 다른 메시지다(기존 유지). 실행 오류는 결과 안의 오류 표시로, 프로토콜 수준 오류와 구분한다.
7. **사내 시스템 연결 (기준 보강).** 명령줄 도구가 이미 있으면 그것을 셸로 쓰게 하고 사용법은 스킬에 적는다. 명령줄 도구가 없거나, 인증을 서버가 맡아야 하거나, 여러 클라이언트가 같이 써야 하면 MCP로 만든다. MCP 서버 하나가 수만 토큰의 도구 정의를 얹을 수 있으므로 붙일 때마다 정의 토큰을 잰다. 외부 서버가 주는 도구 주석(읽기 전용 등)은 믿지 않는다. [A12, X3, A10]
8. **도구 수가 늘 때 (신설).** 상시 노출 도구가 수십 개에 가까워지거나 정의가 1만 토큰대를 넘으면 자주 쓰는 것만 상시 로드하고 나머지는 지연 로드(도구 검색)한다. 도구가 적고 전부 자주 쓰이면 지연 로드는 지연만 더한다. [A10, D5, O1]
9. **무엇을 스킬로 묶나 (보강).** 스킬에는 모델이 이미 아는 것을 쓰지 않는다. 깨지기 쉬운 절차는 구체적으로, 판단이 필요한 일은 원칙만. 결정적이어야 하는 단계는 스킬 안의 스크립트로 둔다. 스킬은 평가에서 드러난 빈틈에서 시작한다. [D7, A9]
10. (유지) 누가 스킬을 부르나.
11. **호출 수 줄이기 (조건 보강).** 코드로 여러 도구를 묶는 방식은 의존적인 호출이 3개 이상이거나 큰 결과를 집계·필터할 때 쓴다. 모델이 중간 결과를 보고 판단해야 하는 일에는 쓰지 않는다. 샌드박스가 전제다. 스크립트 안의 호출도 S5의 검사를 거치는지 확인한다. [A10, A8]

**진행 (추가·교체)**
- 도구 명세표의 칸을 늘린다: 이름(접두 규칙) / 설명(무엇을, 언제, 언제 쓰지 않는지, 인자 의미, 제약 — 도구 설명은 짧게가 아니라 **충분히** 쓴다) / 타입 있는 인자와 입력 예시 / 반환(형식, 상한, 잘렸을 때 안내) / 오류(종류별 메시지) / 부작용 여부. [D4, A3, A10]
- 인자 이름으로 실수를 막는다(`user`가 아니라 `user_id`, 절대 경로만). [A3, A1]
- 도구 개선 루프를 돈다: 현실적인 다중 호출 과제 만들기 → 실행 → 대화 기록과 도구 호출 지표 읽기 → 설명문·스키마 수정 → 따로 떼어 둔 과제로 과적합 확인. 기록 분석과 설명문 수정에 에이전트를 써도 된다. [A3, A4]
- 스킬: 설명은 무엇·언제를 앞부분에(목록에서 잘릴 수 있다), 3인칭으로. 본문은 500줄·5천 토큰 안, 상세는 한 단계 깊이의 별도 파일. 가장 중요한 지시는 본문 맨 위에(압축 뒤 앞부분만 남을 수 있다). 스킬 묶음 안의 스크립트와 의존성은 설치 전에 읽는다. [X2, D7, C5, C3, A9]

**검증 (측정 가능한 신호)**
- 기존 3층(단위 → 선택·인자 → 전체 평가)에 지표를 붙인다.
  - 도구 오류율(전체, 도구별). 인자 오류가 많으면 설명·예시 문제다.
  - 잘못된 도구 선택 비율(기대 도구가 정해진 과제에서).
  - 편집 적용 실패율과 실패 뒤 복구에 든 호출 수.
  - 같은 호출의 반복 횟수(페이지 크기·상한이 안 맞는 신호).
  - 도구 결과 토큰 분포(중앙값, 상위 5%), 상한에 걸린 비율.
  - 과제당 도구 호출 수와 토큰.
- 도구 정의 총 토큰과 상시 노출 도구 수.
- 스킬 호출 시험: 불려야 할 요청과 불리면 안 되는 요청 묶음으로 적중·오발 수를 센다. 쓸 모델 전부로 돈다(강한 모델에서 되던 스킬이 작은 모델에서는 지시가 부족할 수 있다). [D7]
- 편집 가드레일 시험: 문법을 깨는 편집, 0곳 일치, 2곳 일치, 작업 디렉터리 밖 경로를 넣어 각각 정해진 오류가 나오는지.
- 잘라내기 시험: 상한을 넘는 출력에서 안내문이 나오고 다음 호출이 범위·필터를 쓰는지.

**완료 기준 (교체)**
- [ ] 도구마다 명세(설명, 인자 예시, 반환 상한, 오류 종류)와 단위 테스트가 있다
- [ ] 편집 형식이 선택 근거(모델별 적용 성공률)와 함께 정해졌고 가드레일 시험을 통과했다
- [ ] 읽기·검색·테스트 도구의 출력 상한과 잘림 안내가 구현됐다
- [ ] 스킬마다 호출 시험 결과(적중·오발)가 있다
- [ ] 도구 정의 총 토큰, 도구 오류율, 편집 실패율이 `design/04-tools-skills.md`에 있고 평가 회귀가 없다

**흔한 함정 (교체):** 도구를 늘려서 문제 풀기, 실패를 빈 결과로 숨기기, **도구 설명을 한 줄로 쓰기**(도구 설명은 길어도 된다. 짧게 써야 하는 것은 스킬 설명과 상시 로드 지침이다), 스킬 본문에 모델이 이미 아는 설명 늘어놓기, 줄 번호에 의존하는 편집 형식 쓰기, 긴 출력을 통째로 돌려주기, 잘라내고 알리지 않기, 한 모델에서만 시험하기, 평가 과제에 설명문을 맞추다가 과적합하기.

**순서와 병렬**
- 도구 구현과 단위 테스트는 도구별로 동시에 할 수 있다. 스킬 작성도 스킬별로 동시에 할 수 있다.
- 설명문·이름·스키마 조정은 순차다. 한 도구의 설명을 바꾸면 다른 도구의 선택률이 바뀐다. 한 번에 하나 바꾸고 선택 시험을 다시 돈다. [A3, A4]
- 편집 형식 결정이 먼저다. 편집 도구가 정해져야 S5의 "편집 전·후 검사"가 무엇을 가로챌지 정해진다.
- 도구 스키마를 동결한 뒤 S3이 캐시와 로드량을 잰다(S3 참고).
- 편집 뒤 린트를 도구 안에 둘지 S5의 실행 후 검사에 둘지 한 곳으로 정한다. 두 곳에서 돌면 같은 오류가 두 번 컨텍스트에 들어간다.

---

## 3. 현재 문서의 문제점과 수정안

분류: **틀림**(출처와 어긋남) / **모호**(행동으로 옮길 수 없음) / **빠짐**(코딩 에이전트에 필요한데 없음) / **조건 필요**(일부 상황에서만 맞음).

| # | 위치 | 현재 문구 | 분류 | 문제 | 근거 | 수정안 |
|---|---|---|---|---|---|---|
| 1 | S4 흔한 함정 | "설명문을 길게 쓰기" | 틀림 | 도구 설명문에 대해서는 출처가 정반대로 말한다. 설명문이 도구 성능의 최대 요인이고 최소 3~4문장을 권한다. 짧아야 하는 것은 스킬 설명(1,024자 상한)과 상시 로드 지침이다 | D4 "Provide extremely detailed descriptions. This is by far the most important factor in tool performance." / X2 | "도구 설명을 한 줄로 쓰기, 스킬 본문에 모델이 아는 내용을 늘어놓기"로 나눈다. S4 목적의 "적고 명확하게"는 유지 |
| 2 | S4 고민 2 | "모델이 고칠 수 있는 오류만 전달한다" | 틀림 | 같은 절의 함정("실패를 빈 결과로 숨기기")과 충돌한다. 출처는 실패를 알리면 모델이 적응한다고 보고하고, 규격은 실행 오류를 결과 안에 표시하게 한다. 가려야 하는 것은 불친절한 원문(스택 트레이스)이지 실패 사실이 아니다 | A4 "letting the agent know when a tool is failing and letting it adapt works surprisingly well" / A3 / X3 / P6 | 2절 S4 고민 6(오류 종류별 정책)으로 교체 |
| 3 | S4 고민 2 | "상태, 출처, 요약을 돌려주고 원문을 통째로 넣지 않는다" | 조건 필요 | 코드 읽기·편집은 정확한 원문이 필요하다. 요약 반환은 조사형 도구에만 맞다 | A3(페이지·범위·필터·잘라내기), P1(100줄 창) | "범위·필터·페이지로 필요한 만큼만, 기본값은 작게. 잘랐으면 알린다" |
| 4 | S4 전체 | (없음) | 빠짐 | 편집 형식 선택이 없다. 코딩 에이전트에서 가장 실패가 잦은 도구다(궤적의 51.7%에서 편집 실패 1회 이상). 편집 형식만 바꿔 벤치마크 점수가 20%에서 61%로 오른 사례가 있다 | P1, P3, A11, A1, O4 | 2절 S4 고민 2, 검증의 편집 가드레일 시험 |
| 5 | S4 전체 | (없음) | 빠짐 | 읽기 창 크기, 검색 결과 상한, 도구 출력 상한, 테스트 출력 규격이 없다 | P1, A3, O3, A14 | 2절 S4 고민 3·4 |
| 6 | S4 고민 3 | "공유·원격 자원만 MCP로 만들고, 로컬에서만 쓰는 것은 스크립트로" | 조건 필요 | 방향은 맞지만 기준이 "원격 여부"가 아니다. 규격상 로컬 MCP 서버도 정상이고, 출처의 기준은 "명령줄 도구가 있는가"다. MCP의 컨텍스트 비용(서버 5개 ≈ 55K 토큰)도 빠져 있다 | A12, X3, A10 | 2절 S4 고민 7 |
| 7 | S4 고민 6 | "연관된 여러 호출은 스크립트 하나로 묶는다(코드 모드)" | 조건 필요 | 언제 이득이고 언제 손해인지, 샌드박스 전제, S5 검사 우회 가능성이 없다 | A10("three or more dependent tool calls", 중간 결과를 봐야 하면 불리), A8 | 2절 S4 고민 11 |
| 8 | S3 고민 4 | "고정 내용은 앞, 바뀌는 값은 뒤. 대화는 뒤에 붙이기만 한다. 중간을 압축하면 캐시가 깨진다." | 모호 | 맞지만 실행할 수 없다. 빠진 것: 도구 정의가 접두 맨 앞이라는 점(도구 변경 = 전체 무효), 수명과 최소 길이, 결정적 직렬화, 모델·설정 변경, 측정 방법. 또 "압축하면 깨진다"가 "압축하지 마라"로 읽힌다. 출처는 압축을 첫 번째 손잡이로 꼽고, 한 번에 충분히 비우라고 한다 | D1, D2, P6, A2 | 2절 S3 고민 4·5 |
| 9 | S3 고민 3 | "탐색은 서브에이전트나 작은 모델에 맡기고 메인은 결론만 받는다" | 조건 필요 | 무조건 규칙으로 쓰면 과용이 된다. 출처는 검색 한 번이면 될 일에 서브에이전트를 띄우는 것을 문제로 꼽고, 창이 큰 모델에서는 "컨텍스트 보호용 서브에이전트"를 낡은 조언으로 분류한다. 작은 모델 위임은 지시 오해 위험이 보고돼 있다. 창이 작은 사내 모델에서는 여전히 유효하므로 삭제가 아니라 조건화가 맞다 | D9, A12("Use subagents to protect your context window" 항목), P4, P5, A2 | 2절 S3 고민 3 (격리 조건 + 재현율 측정) |
| 10 | S3 전체 | (없음) | 빠짐 | 검색 수단 선택(에이전틱 검색, 저장소 지도, 언어 서버, 의미 검색)이 없다. 저장소 탐색 방법은 코딩 에이전트의 핵심 결정이다 | A2, A7, P2, C2 | 2절 S3 고민 3 "찾는 방법" |
| 11 | S3 진행 | "지침 계층 파일을 만들고 양식(XML 구역)을 통일한다" | 조건 필요 | 통일은 맞다. XML이어야 한다는 근거는 1차 자료에 없다. 지침 파일 규격은 일반 마크다운이고, 문서는 마크다운 제목·목록을 권하며, 형식의 중요성은 줄고 있다고 한다. 스킬 규격도 본문 형식 제한이 없다(스킬의 name·description에는 XML 태그를 쓸 수 없다). 사내 관례로 XML을 쓰는 것은 문제없다 | A2, C1, X1, X2, D7 | "구역을 나누고 한 가지 방식으로 통일한다(마크다운 제목 또는 태그)". S4 진행의 "본문은 XML 구역"도 같은 취급 |
| 12 | S3 고민 1 | "항상 로드되는 지침은 짧게 둔다(200줄 이하 권장)" | 모호 | 수치는 출처와 일치한다(특정 제품의 파일당 권장값). 빠진 것: 무엇을 넣고 빼는지의 기준, 합계 상한(다른 제품은 합계 32 KiB), 쪼개서 가져와도 비용이 그대로라는 점, 계층이 겹칠 때의 규칙 | C1, O2, A12, X1 | 2절 S3 고민 1 |
| 13 | S3 진행 | "긴 대화 압축 방식을 정한다. 요약에는 원본으로 가는 경로를 남긴다." | 모호 | 경로 보존은 출처와 일치한다. 빠진 것: 무엇이 살아남아야 하는지, 발동 임계값, 압축·결과 비우기·리셋의 구분, 검증 방법 | A2, D2, C3, A6, P6 | 2절 S3 고민 5, 압축 생존 시험 |
| 14 | S2·S3 | (없음) | 빠짐 | 컨텍스트 창을 넘는 작업의 인계 산출물(상태 파일, 진행 메모, 커밋, 기동 스크립트), 세션 시작 절차, 조기 완료 선언 방지가 어디에도 없다 | A5, A6, D9 | 2절 S2 고민 4, 중단·재개 시험, 조기 완료 시험 |
| 15 | S2 고민 3 | "서브에이전트는 컨텍스트 경계가 분명한 곳(코드 탐색, 독립 리뷰어)에만 둔다" | 모호 | 출처와 방향이 일치한다. 판단 기준(읽기 전용, 잘 정의된 질문, 단일 스레드 쓰기), 비용, 위임 양식이 없어 "분명한 곳"을 판정할 수 없다 | P4, P5, A4, A12, O1 | 2절 S2 고민 3 판단표, 쪼갬 비교 |
| 16 | S2 고민 1·S5 | "요구 확인 → 계획·리뷰·승인 → 구현 → 검증 → 보고·학습"을 모든 요청에 적용 | 조건 필요 | 계획·리뷰·승인은 인수 기준 항목이라 유지해야 한다. 다만 출처는 ① 계획이 세부를 못박으면 오류가 전파된다 ② 평가자·분해 구조는 모델 능력 경계 밖에서만 값어치가 있다 ③ 쉬운 작업은 계획을 생략한다고 한다. 계획의 수준과 크기별 분량을 정하지 않으면 작은 작업에서 비용만 든다 | A6, A4, O3 | 2절 S2 고민 1. 구성요소 표에 "계획 리뷰어"를 넣고 껐을 때의 수치를 남긴다(유지 근거) |
| 17 | S2 고민 7 | "최대 턴·시간·재시도, 종료 상태" | 모호 | 무진전 감지, 비용 상한, 강제 장치의 반복 상한, 상한에 걸린 종료의 구분이 없다 | A1, O1, O3, A12 | 2절 S2 고민 7 |
| 18 | S2 고민 5 | "실행 시간, 호출 횟수, 재시도 횟수, 토큰" | 빠짐 | 뒤 단계가 판정에 쓸 지표(도구 오류율, 편집 실패율, 캐시 읽기·쓰기, 컨텍스트 최대 사용량)가 없다. 캐시 적중률은 S3 검증에 나오지만 S2 기록 항목에 없어 잴 수 없다 | A3, P6, D1 | 2절 S2 고민 6 |
| 19 | S0 고민 2 | "처음부터 짜지 말고 포크해서 어긋나는 점만 바꾸는 쪽을 권한다" | 조건 필요 | 출처는 반대 방향(API 직접 호출로 시작)을 권하지만 이유는 "내부를 이해하라"다. 포크는 소스를 읽을 수 있으므로 양립한다. 조건을 붙여야 한다: 요청 원문을 볼 수 있고 구성요소를 끌 수 있을 때 | A1, A6 | 2절 S0 고민 2. "권한다" 뒤에 "단, 모델에 들어가는 요청 원문을 볼 수 있고 구성요소를 하나씩 끌 수 있는 기반에 한한다" |
| 20 | S0 고민 3 | "계획·코드·판단·리뷰에 같은 모델을 쓸 필요는 없다" | 조건 필요 | 출처와 일치하지만 S0에서 섞으면 기준선이 흐려진다. 출처의 순서는 "가장 강한 모델로 기준선 → 목표 달성 → 내리기"다 | O1, D8 | 2절 S0 고민 3. 분리는 후보 칸으로만 |
| 21 | S0 고민 1 | 대상 작업 선정 기준 | 빠짐 | "에이전트로 풀 일인가"와 "자동 검증이 가능한가"가 없다 | A1, O1, A12 | 2절 S0 고민 0·1 |
| 22 | 1절 표·"왜 이 순서인가" | "S3·S4·S5는 서로 다른 손잡이라 동시에 만들 수 있다" | 조건 필요 | 만드는 것은 병렬이 맞다. 그러나 독립이 아닌 결합이 세 곳 있다: 도구 정의는 캐시 접두의 맨 앞(S4 → S3 측정), 스킬 메타데이터는 세션 시작 로드량(S4 → S3 측정), 편집 도구가 정해져야 편집 검사가 정해짐(S4 → S5) | D1, A9, C2 | "병렬 작업 규칙"에 한 줄 추가: "S4의 도구 스키마를 동결한 뒤 S3의 캐시·로드량을 잰다. 편집 도구가 정해진 뒤 S5의 편집 검사를 붙인다" |
| 23 | S4 검증 | "실제로 노출되는 도구 수와 컨텍스트 점유율을 확인한다" | 모호 | 무엇과 비교할지 없다. 참고 임계값이 있다 | A10(정의 >10K 토큰·10개 이상이면 지연 로드 검토), D5(30~50개에서 선택 정확도 저하), O1(중복이 수보다 문제) | 2절 S4 고민 8, 검증 지표 |
| 24 | S4 진행 | 스킬: "설명은 무엇·언제(아닌 경우 포함)를 짧게, 본문은 XML 구역, 상세는 별도 파일" | 모호 | 대체로 일치한다. 빠진 것: 설명이 잘리는 길이, 3인칭, 본문 500줄·5천 토큰, 참조 한 단계, 중요한 지시는 맨 위, 여러 모델로 시험, 평가 먼저, 스크립트 감사 | X2, D7, C5, C3, A9 | 2절 S4 진행 |

**범위 밖 참고(S1):** S1의 "0~1점으로 매겨라만 쓰지 않는다. 점수가 0.7 근처로 쏠린다"는 A4의 보고와 결이 다르다. A4는 기준표를 준 단일 호출에서 0.0~1.0 점수와 통과/실패를 함께 내게 한 것이 사람 판정과 가장 일치했다고 한다. 현재 문장은 "기준 없이 점수만"을 경계하는 것이라 모순은 아니지만, S1 담당이 표현을 확인할 만하다.

---

## 4. 확인 못 한 것

1. **OpenAI "Harness engineering: leveraging Codex in an agent-first world"** — openai.com이 403을 돌려줘 원문을 가져오지 못했다. 검색 결과로 저자(Ryan Lopopolo)와 날짜(2026-02-11), 저장소 최상위에 지침 파일과 아키텍처 문서를 두고 `docs/` 아래에 설계 문서·실행 계획을 둔다는 것까지는 확인했으나, 널리 인용되는 문구(지침 파일을 백과사전이 아니라 목차·지도로 쓴다, 약 100줄)는 **원문 대조를 못 했다.** 이 글을 근거로 한 인용은 이 보고서에 넣지 않았다. 브라우저로 직접 열어 확인해야 한다.
2. **[요약경유] 표시 출처 5건**(A13, A14, O3, O4, P5) — WebFetch의 소형 모델이 뽑은 인용이라 문자 단위 대조를 못 했다. 방향과 수치는 2절 제안의 보조 근거로만 썼고, 핵심 주장은 [직] 출처로 따로 받쳤다. METHOD.md나 notes에 인용문으로 옮기려면 원문 확인이 필요하다.
3. **"Which Claude model should you build with?"**(Anthropic 블로그, 2026-11-09 목록에 보임) — 추정 URL이 404였다. 모델 선택은 D8(문서)과 O1로 대신했다.
4. **수치의 이식성** — 모든 수치는 각 출처의 모델·과제에서 나온 값이다. 특히 P1(2024년, GPT-4 Turbo)의 절제 수치와 P3(GPT-4 Turbo)의 편집 형식 수치는 현재 모델에 그대로 맞지 않을 수 있다. "창 크기·편집 형식·가드레일이 성능을 바꾼다"는 방향만 믿고 값은 우리 모델로 다시 재야 한다. A12의 "컨텍스트 창이 주된 제약이 아니다"는 100만 토큰 창 모델 기준이다. 사내 서빙 모델의 창이 작으면 적용되지 않는다.
5. **Agent Skills 규격 본문** — agentskills.io/specification은 [직]으로 확인했으나 사이트의 다른 페이지(스킬 작성 안내, 클라이언트 구현 안내)는 읽지 않았다.
6. **MCP 규격** — 2025-06-18판의 tools 페이지와 architecture 개요만 읽었다. 그 뒤 개정판의 변경, 인증(Authorization) 절은 확인하지 않았다(S5 범위).
7. **지침 파일이 실제로 성능을 올리는지에 대한 독립 측정** — 이번 조사에서는 공급자 문서의 권고만 확보했다. 지침 파일 길이와 준수율의 관계를 제3자가 잰 자료는 찾지 않았다. 2절 S3의 "지침 준수 탐침"으로 직접 재는 것을 권한다.
8. **저장소의 다른 파일과의 정합성** — METHOD.md, CRITERIA.md 일부, `bases/dcode.md` 일부만 읽었다. 2절 제안이 스킬(`tool-design-review`, `skill-authoring`, `workflow-to-architecture`)과 `templates/`의 현재 내용과 겹치거나 어긋나는지는 대조하지 않았다.
