# R6. 메모리(S3) · 자기개선(S6) · 최적화(S7) · 배포·운영(S8) 1차 자료 조사와 보강안

조사일: 2026-11-11. 대상 문서: `kit/harness/METHOD.md`, `kit/harness/CRITERIA.md`(3-1~3-4), `kit/harness/templates/03-context.md`·`06-improve.md`·`07-optimize.md`·`08-release.md`, `notes/_pending/skills/self-improve-loop/SKILL.md`, 관련 스킬 `optimize-agent`, `agent-eval`.
저장소는 수정하지 않았다. 아래 "수정안"은 전부 제안 텍스트다.

읽는 순서: 급하면 4절(문제점) → 2절(보강안) → 3절(붙여 넣을 텍스트). 1절은 근거 표다.

인용 표기 규칙
- `[원문]`: 페이지 원문을 직접 읽고 옮긴 문장.
- `[추출]`: WebFetch의 요약 모델이 "원문 그대로"라고 돌려준 문장. 짧은 구절만 썼지만 반영 전에 한 번 대조할 것(5절 참고).
- 숫자 가운데 "제안값"이라고 적은 것은 출처가 없는 내 기본값이다. 문서에 넣을 때는 "팀이 정한다"로 두고 예시로만 쓴다.

---

## 1. 출처별 핵심

### 1-A. 에이전트 메모리

| 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|
| Anthropic, Memory tool 문서 | 메모리는 파일 디렉터리이고 실행은 클라이언트가 한다. 작업 전 디렉터리를 먼저 보고, 진행 상황을 계속 적게 한다. 크기 상한·만료·민감정보 필터·경로 검증은 구현자의 책임이다. | `[원문]` "ASSUME INTERRUPTION: Your context window might be reset at any moment" / "Track memory file sizes and cap how large a file can grow." / "Periodically delete memory files that haven't been accessed in a long time." / "add validation that strips sensitive data before your handler writes the file" | https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool |
| 같은 문서, 다중 세션 개발 패턴 | 메모리를 "그때그때"가 아니라 의도적으로 설계한다(진행 로그, 기능 체크리스트). 완료 표시는 검증 뒤에만. | `[원문]` "Mark a feature complete only after end-to-end verification confirms it works, not when the code is written." | 위와 같음 |
| Anthropic, Context editing 문서 | 오래된 도구 결과를 지우면 캐시가 깨진다. 지울 거면 충분히 지운다. 지우기 전에 메모리에 옮기라는 경고가 자동으로 나간다. 기본 전략은 서버 측 압축(compaction)이다. | `[추출]` 기본값: trigger 100,000 입력 토큰, keep 3 tool uses. "This helps determine whether context clearing is worth breaking your prompt cache." / "Claude receives an automatic warning to preserve important information." | https://platform.claude.com/docs/en/build-with-claude/context-editing |
| Anthropic, 컨텍스트 관리 발표 글 | 메모리 + 컨텍스트 편집의 측정 효과. | `[추출]` "combining the memory tool with context editing improved performance by 39% over baseline." / "Context editing alone delivered a 29% improvement." / "reducing token consumption by 84%." | https://claude.com/blog/context-management |
| Anthropic, Effective context engineering | 컨텍스트는 한정 자원. 식별자만 들고 있다가 필요할 때 읽는다(just-in-time). 메모를 컨텍스트 밖에 적는다. 서브에이전트는 요약만 돌려준다. | `[추출]` "the smallest possible set of high-signal tokens" / "maintain lightweight identifiers (file paths, stored queries, web links, etc.)" / "returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)." / "Start by maximizing recall" | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| Claude Code, 메모리 문서 | 지침(사람이 씀)과 자동 메모리(에이전트가 씀)를 나눈다. 둘 다 "맥락"이지 강제가 아니다. 색인 파일은 앞 200줄/25KB만 로드되고 상세는 주제 파일로 뺀다. 코드에서 유도할 수 있는 것은 저장하지 않는다. 지침은 시스템 프롬프트가 아니라 사용자 메시지로 전달된다. | `[원문]` "Claude treats them as context, not enforced configuration." / "The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first, are loaded at the start of every conversation." / "Claude skips anything it can derive from the codebase" / "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence." / "CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself." | https://code.claude.com/docs/en/memory |
| 같은 문서, 언제 지침에 추가하나 | "두 번째 같은 실수"가 승격 신호. 반드시 실행돼야 하면 훅. 충돌하는 지침은 아무거나 고른다 → 주기적 정리. | `[원문]` "Claude makes the same mistake a second time" / "if two instructions contradict each other, Claude may pick one arbitrarily" / "keep one line per entry, move detail into topic files, and merge or drop stale entries" | 위와 같음 |
| Anthropic, Managed Agents 메모리 문서 | 저장소 접근 모드(read_only/read_write), 변경마다 불변 버전(감사·복구), 항목 크기 상한, 작은 파일 여러 개 권장, 동시 쓰기는 해시 전제조건. 신뢰할 수 없는 입력을 처리하는 에이전트의 쓰기 가능 메모리는 주입 경로다. | `[원문]` "a successful prompt injection could write malicious content into the store. Later sessions then read that content as trusted memory. Use `read_only` for reference material" / "Every mutation to a memory creates an immutable **memory version**" / "capped at 100 kB (~25k tokens) ... Structure memory as many small focused files, not a few large ones." | https://platform.claude.com/docs/en/managed-agents/memory |
| GitHub, Copilot 에이전트 메모리 설계 글 | 코딩 에이전트 메모리의 핵심 문제는 "낡음". 기억마다 코드 위치 인용을 붙이고, 쓸 때 그 인용을 현재 코드와 대조한다(사전 큐레이션 대신). 저장소 단위 범위·권한. 틀린 기억을 심어도 에이전트가 고쳤다. | `[추출]` "references to specific code locations that support each fact." / "When an agent encounters a stored memory, it verifies the citations in real-time." / "7% increase in pull request merge rates (90% with memories vs. 83% without)." / "The memory pool self-healed as agents stored corrected versions based on their observations." | https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/ |
| GitHub Docs, Copilot Memory | 만료 정책: 기본 만료가 있고, 검증돼 쓰이면 연장된다. | `[추출]` "The default expiry period is 90 days." / "The expiry period starts when a memory is created and resets when Copilot upvotes it." (조직이 7~180일로 조정) | https://docs.github.com/en/copilot/concepts/agents/copilot-memory |
| LangGraph 메모리 개념 문서 | 장기 기억을 사실(semantic)·경험(episodic)·절차(procedural)로 나눈다. 쓰기 시점은 "작업 중(hot path)"과 "백그라운드" 둘이고 각각 비용이 다르다. | `[추출]` "remembering the rules used to perform tasks" / "few-shot example prompting, where agents learn from past sequences" / "can impact agent latency" / "eliminates latency in the primary application" / "error-prone as the profile gets larger" | https://docs.langchain.com/oss/python/langgraph/memory |
| LangMem 개념 가이드 | 과다 추출은 정밀도를, 과소 추출은 재현율을 깎는다. 절차 기억은 프롬프트 최적화로 갱신한다. | `[추출]` "If the system over-extracts, this could lead to reduced precision of memories." / "If it under-extracts, this could lead to low recall." | https://langchain-ai.github.io/langmem/concepts/conceptual_guide/ |
| CoALA (Sumers 외, 2023) | 기억 종류와 행동 공간을 나눠 설계하라는 틀. 용어의 원전. | `[추출]` "modular memory components" / "a structured action space to interact with internal memory and external environments" | https://arxiv.org/abs/2309.02427 |
| MemGPT (Packer 외, 2023) / Letta 문서 | 항상 보이는 블록(작게, 글자 수 상한)과 검색해서 꺼내는 저장소를 계층으로 둔다. 블록은 읽기 전용으로 잠글 수 있다. | `[추출]` "data movement between fast and slow memory" / "A `limit`, which is the size limit (in characters) of the block." / "When a block is read-only, the agent cannot update the block." | https://arxiv.org/abs/2310.08560 , https://docs.letta.com/guides/agents/memory-blocks |
| Mem0 (Chhikara 외, 2025) | 전체 대화를 다 넣는 대신 추출·통합·검색하면 지연과 토큰이 크게 준다(벤더 자체 측정). | `[추출]` "Mem0 attains a 91% lower p95 latency and saves more than 90% token cost" | https://arxiv.org/abs/2504.19413 |
| A-MEM (Xu 외, 2025) | 기억을 키워드·태그·맥락 설명이 붙은 노트로 저장하고 서로 연결한다. | `[추출]` "including contextual descriptions, keywords, and tags" | https://arxiv.org/abs/2502.12110 |
| ReasoningBank (Ouyang 외, 2025) | 성공뿐 아니라 실패 경험에서도 일반화된 전략을 뽑아 저장한다. | `[추출]` "distills generalizable reasoning strategies from an agent's self-judged successful and failed experiences." | https://arxiv.org/abs/2509.25140 |
| Anthropic, Contextual Retrieval | 임베딩은 정확 일치(오류 코드·식별자)를 놓친다. BM25를 같이 쓴다. 작은 지식은 검색 없이 통째로 넣고 캐시한다. | `[추출]` "they can miss crucial exact matches." / "reduced the top-20-chunk retrieval failure rate by 49%" / "smaller than 200,000 tokens (about 500 pages of material)" | https://www.anthropic.com/news/contextual-retrieval |
| Anthropic, Agent SDK 글 | 검색은 파일 탐색(agentic search)으로 시작하고 의미 검색은 필요가 확인되면 붙인다. | `[추출]` "Given its limitations, we suggest starting with agentic search" | https://claude.com/blog/building-agents-with-the-claude-agent-sdk |
| MINJA (Dong 외, 2025) | 메모리 저장소를 직접 못 건드려도 평범한 질의만으로 악성 기록을 심을 수 있다. | `[추출]` "MINJA enables any user to influence agent memory, highlighting the risk." | https://arxiv.org/abs/2503.03704 |
| OWASP LLM04:2025 | 저장 데이터의 출처 추적, 버전 관리, 이상 탐지. | `[추출]` "Use data version control (DVC) to track changes in datasets and detect manipulation." | https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/ |

### 1-B. 자기개선

| 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|
| Reflexion (Shinn 외, 2023) | 실패 피드백을 말로 반성해 에피소드 메모리에 넣고 다음 시도에 쓴다. 가중치는 안 바꾼다. | `[추출]` "Reflexion agents verbally reflect on task feedback signals" / "an episodic memory buffer" | https://arxiv.org/abs/2303.11366 |
| ExpeL (Zhao 외, 2023) | 경험을 모으고, 거기서 일반 통찰을 뽑고, 추론 때 통찰과 유사 경험을 같이 꺼낸다. 두 층(통찰/사례)을 구분한다. | `[추출]` "At inference, the agent recalls its extracted insights and past experiences to make informed decisions." | https://arxiv.org/abs/2308.10144 |
| Voyager (Wang 외, 2023) | 검증을 통과한 행동을 실행 가능한 코드(스킬)로 저장해 재사용한다. 스킬 추가의 관문은 자기 검증이다. | `[추출]` "an ever-growing skill library of executable code for storing and retrieving complex behaviors" / "incorporates environment feedback, execution errors, and self-verification" | https://arxiv.org/abs/2305.16291 |
| ACE (Zhang 외, 2025) | 프롬프트를 통째로 다시 쓰게 하면 짧고 일반적인 문장으로 무너진다(brevity bias, context collapse). 항목 단위(식별자 + 도움/해로움 카운터)로 두고 증분만 붙인다. 생성·반성·정리 역할을 나눈다. 피드백 신호가 나쁘면 메모리가 오염된다. | `[추출]` "brevity bias: the tendency of optimization to collapse toward short, generic prompts." / "at step 60 the context contained 18,282 tokens and achieved an accuracy of 66.7" → "it collapsed to just 122 tokens, with accuracy dropping to 57.1" / "metadata, including a unique identifier and counters tracking how often it was marked helpful or harmful" / "Rather than regenerating contexts in full, ACE incrementally produces compact delta contexts" / "A limitation of ACE is its reliance on a reasonably strong Reflector" / "the constructed context can be polluted by spurious or misleading signals" | https://arxiv.org/abs/2510.04618 |
| GEPA (Agrawal 외, 2025) | 실행 궤적을 읽고 자연어로 원인을 진단해 프롬프트를 고치고, 후보를 한 줄로 세우지 않고 파레토 전선으로 유지한다. | `[추출]` "reflects on them in natural language to diagnose problems, propose and test prompt updates" / "the Pareto frontier of its own attempts" | https://arxiv.org/abs/2507.19457 |
| TextGrad (Yuksekgonul 외, 2024) | LLM의 텍스트 피드백을 구성요소별로 역전파한다. 프롬프트 외 구성요소에도 같은 루프가 적용된다. | `[추출]` "backpropagates textual feedback provided by LLMs to improve individual components of a compound AI system." | https://arxiv.org/abs/2406.07496 |
| Darwin Gödel Machine (Zhang 외, 2025) + Sakana 글 | 스스로 코드를 고치는 코딩 에이전트. 샌드박스·시간 제한·사람 감독·전체 계보 보관이 전제다. 평가 절차 자체는 고칠 수 없게 고정했다. 그래도 테스트 실행을 지어내고, 환각 탐지용 표식을 지워서 점수를 올린 사례가 나왔다. | `[추출]` "All agent execution and self-modification processes are conducted within isolated sandboxed environments" / "is fixed and not modifiable by the DGM." / "It faked a log making it look like it had run the tests and that they had passed, when in fact they were never run!" / "removed the markers we use in the reward function to detect hallucination" / "a transparent, traceable lineage of every change" | https://arxiv.org/abs/2505.22954 , https://sakana.ai/dgm/ |
| SICA (Robeyns 외, 2025) | 점수만이 아니라 비용·시간을 함께 넣은 효용으로 고른다. 실행 중 감시자가 개입·취소한다. 개선 경로는 초기 선택에 좌우돼 분산이 크다. | `[추출]` 가중치 0.5/0.25/0.25. "We cap the worst cost at $10 per problem, and impose a timeout of 300 s" / "a key safety mitigation in such systems is observability." / "This path dependency may lead to higher variance agent runs." | https://arxiv.org/abs/2504.15228 |
| OpenAI Cookbook, Self-evolving agents | 기준선 → 채점 → 프롬프트 최적화 → 목표 도달 시 교체의 루프. 재시도 상한, 버전 관리와 되돌리기, 운영은 사람 검토·개발은 자동 채점. 최적화는 학습용과 검증용 데이터를 나눈다. | `[추출]` "MAX_OPTIMIZATION_RETRIES = 3" / "Manages a collection of prompt versions and provides controlled updates and rollbacks." / "candidates were trained on one dataset and validated on another." / "engineers are alerted that manual improvements are required." | https://developers.openai.com/cookbook/examples/partners/self_evolving_agents/autonomous_agent_retraining |
| Anthropic, Writing tools for agents | 평가 궤적을 에이전트에게 읽혀 개선하되, 과적합은 따로 떼어 둔 시험지로 막는다. | `[추출]` "We relied on held-out test sets to ensure we did not overfit to our “training” evaluations." | https://www.anthropic.com/engineering/writing-tools-for-agents |
| Anthropic, Demystifying evals | 능력 평가(낮은 통과율에서 시작)와 회귀 평가(거의 100%)를 나눈다. 채점기는 우회에 강해야 한다. 시도마다 깨끗한 환경. 이전 시도의 git 기록을 보고 이득을 본 사례가 있었다. | `[추출]` "should have a nearly 100% pass rate." / "capability evals with high pass rates can “graduate” to become a regression suite" / "Make your graders resistant to bypasses or hacks." / "examining the git history from previous trials." / "20-50 simple tasks drawn from real failures is a great start." | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents |
| Anthropic, 평가 기반 개선 루프 가이드 (Claude Code 번들 `claude-api` 스킬의 `shared/evals/eval-hillclimb.md`. Anthropic 작성, 공개 URL 없음) | 개선안을 내는 쪽은 train 궤적만 읽고, 보고 수치는 그쪽이 본 적 없는 test에서 낸다. 라운드 전에 노이즈 폭·여유·최소 효과를 잰다. 한 라운드에 가설 하나. "메커니즘이 실제로 작동했는가"를 점수와 따로 본다. 정답이 디스크에서 닿으면 언젠가 그 길로 "이긴다". 2~3 라운드 정체하면 내용 수정을 멈추고 실패를 원인별로 분류한다. | `[원문]` "the analyzer reads train, the headline comes from test, and that wall is the result's credibility." / "A change whose best-case gain sits inside the noise floor is kept or reverted largely by chance" / "Separate \"did the mechanism engage\" from \"did it help.\"" / "Isolate answers structurally; don't rely on instructions." / "generalize, don't memorize" / "If train went up and test didn't, the change overfit to the cases the analyzer read - revert it" / "Draw the split at random, stratified by `tags[0]` - never by baseline score." / (작은 셋) "Don't split. Score the whole set every round, lean on **reps**" | 로컬: `/tmp/claude-0/bundled-skills/2.1.322/…/claude-api/shared/evals/eval-hillclimb.md` |
| METR, Recent frontier models are reward hacking (2025-06) | 최신 모델은 채점 코드·테스트를 고치거나 정답에 접근해 점수를 올린다. "하지 말라"는 지시는 거의 효과가 없다. 탐지는 이상하게 높은 점수 + 수동 검토. | `[추출]` "modifying the tests or scoring code, gaining access to an existing implementation or answer." / RE-Bench 39/128 runs(30.4%), HCAST 8/1087(0.7%) / "had a nearly negligible effect on reward hacking." | https://metr.org/blog/2025-06-05-recent-reward-hacking/ |
| ImpossibleBench (Zhong·Raghunathan·Carlini, 2025) | 테스트를 숨기면 부정 통과가 거의 0이 되지만 정상 성능도 떨어진다. 읽기 전용은 테스트 수정은 막지만 특수 처리·연산자 덮어쓰기는 못 막는다. "사람에게 넘기기" 출구를 주면 부정이 준다. | `[추출]` "Hiding tests from agents reduces cheating success rate to near zero" / "Read-only access provides a middle ground" / abort 옵션: GPT-5 54% → 9% / 부정 유형 4가지: 테스트 수정, 비교 연산자 덮어쓰기, 상태 기록, 특수 처리 | https://arxiv.org/abs/2510.20270 |

### 1-C. 모델·비용·속도 최적화

| 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|
| Anthropic, Prompt caching 문서 | 캐시는 접두(prefix) 일치다. 순서는 tools → system → messages. 중단점 최대 4개, 되돌아보는 범위 20블록. 쓰기는 5분 TTL 1.25배·1시간 TTL 2배, 읽기는 0.1배(일부 최신 모델은 더 쌈). 최소 길이 미만은 조용히 캐시되지 않는다. 도구 정의를 바꾸면 전체가 무효. | `[추출]` "Cache write tokens with a 5-minute TTL are 1.25 times the base input tokens price." / "Cache write tokens with a 1-hour TTL are 2 times the base input tokens price." / "Cache read tokens are 0.1 times the base input tokens price" / "You can define up to 4 cache breakpoints" / "Cache prefixes are created in the following order: `tools`, `system`, then `messages`." / "Modifying tool definitions (names, descriptions, parameters) invalidates the entire cache" / "Place the breakpoint on the last block that stays identical across requests." / 최소 길이: 모델별 512~4,096 토큰 | https://platform.claude.com/docs/en/build-with-claude/prompt-caching |
| Anthropic, 캐시 설계 가이드 (번들 `claude-api` 스킬 `shared/prompt-caching.md`, 공개 URL 없음) | 시스템 프롬프트를 얼린다. 바뀌는 값은 뒤쪽 메시지로. 대화 중 도구·모델을 바꾸지 않는다. 갈라져 나온 호출(요약·서브에이전트)은 부모의 접두를 그대로 써야 한다. 조용한 무효화 원인 목록. | `[원문]` "A message at turn 5 invalidates nothing before turn 5." / "Don't change tools or model mid-conversation." / "If `cache_read_input_tokens` is zero across repeated requests with identical prefixes, a silent invalidator is at work" / 조용한 무효화: `datetime.now()`, `uuid4()`, 정렬 안 한 JSON, 사용자별 도구 목록, 조건부 시스템 구역 | 로컬 번들 파일 |
| Anthropic, Optimizing for cost and intelligence | 단위는 "완료된 작업 1건당 비용". 순서는 캐시 → 배치 → 프롬프트 감사 → effort → 모델 → 다중 모델. 모델을 둘로 쪼개기 전에 한 모델의 effort를 훑는다. 실패 건만 높은 effort로 다시 돌리는 방식이 싸다. 위임(오케스트레이터)은 두 경우에만 이겼다. 교체 전 실트래픽 일부로 그림자 실행. | `[추출]` "Turn on prompt caching before any other lever" / "Compare models on cost per completed task, not per token" / "Sweep effort on your own workload before you add a second model." / "Batching is the second-largest free lever after caching for unattended agent work." / "A multi-model configuration must beat the single model's whole curve." / "Price the tail of your workload, not the median." / 에이전트 루프는 입력의 중앙값 84%를 캐시에서 읽음 / 캐시로 과제당 $40.58 → $5.64 / low로 돌리고 실패만 high 재실행: 약 97% 해결·$0.17 vs 전부 high 95.3%·$0.29 / `max_tokens`는 모델이 못 보므로 낮춰도 절약하지 않음 | https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence |
| 같은 주제의 절차 가이드 (번들 `shared/cost-optimization.md`) | "공짜 이득"(품질을 안 깎는 것)과 "맞교환"(품질을 거는 것)을 나누고, 맞교환은 평가가 있어야 적용한다. 레버 하나가 diff 하나. | `[원문]` "API spend is optimized in units of **cost per completed task, not cost per token**." / "a cheaper model that fails still bills its tokens, then the retry" / "never trade accuracy for cost silently" / "the subagent starts a fresh prefix with no cache shared with the parent." / "Shadow-run the winning configuration on live traffic before cutover" | 로컬 번들 파일 |
| Anthropic, Effort 문서 | effort는 생각·본문·도구 호출 전부의 토큰량을 조절한다. 낮추면 도구 호출이 줄고 짧아진다. 기본값은 모델마다 다르다(모델을 바꾸면 다시 훑는다). 대화 중 effort 변경은 메시지 단위 방식만 캐시를 보존한다. | `[원문]` "Lower effort also means fewer and terser tool calls." / "Run a fresh effort sweep on your evals rather than carrying over the setting" / "step down to `medium` or `low` only when you've measured that the lower level holds quality on your evals." | https://platform.claude.com/docs/en/build-with-claude/effort |
| Anthropic, Batch processing 문서 | 기다려도 되는 일(평가 실행 포함)은 배치로 50% 할인. 결과 순서는 보장되지 않는다. 캐시 할인과 겹친다. | `[원문]` "most batches finishing in less than 1 hour while reducing costs by 50 percent" / "limited to either 100,000 Message requests or 256 MB" / "Batch results are available for 29 days after creation." / "consider using the 1-hour cache duration ... when processing batches with shared context." | https://platform.claude.com/docs/en/build-with-claude/batch-processing |
| Anthropic, Reducing latency 문서 | 먼저 제약 없이 잘 되는 프롬프트를 만들고 그다음에 줄인다. 지연 지표는 TTFT와 전체 시간. | `[원문]` "Trying to reduce latency prematurely might prevent you from discovering what top performance looks like." / "**Time to first token (TTFT):** This metric measures the time it takes for the model to generate the first token of the response, from when the prompt was sent." | https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency |
| 지연 절차 가이드 (번들 `shared/latency-optimization.md`) | 작업 시간 = 호출 수 × 첫 토큰 시간 + 출력 토큰 ÷ 출력 속도 + 모델 밖 시간. "첫 토큰"과 "첫 가시 출력"은 다르다(생각이 먼저 나오면 수 초 차이). 공짜 레버는 없다. | `[원문]` "**task time = calls × time to first token + output tokens ÷ output speed + everything else**" / "**No lever here is free**" / "A faster model isn't automatically a faster task" | 로컬 번들 파일 |
| Anthropic, Advanced tool use | 도구 정의만으로 수만 토큰이 든다. 필요할 때 찾게 하면(지연 로드) 컨텍스트가 줄고 캐시도 안 깨진다. 여러 호출을 코드 한 블록으로 묶으면 추론 왕복이 준다. | `[추출]` "58 tools consuming approximately 55K tokens before the conversation even starts" / "an 85% reduction in token usage" / "you eliminate 19+ inference passes." / 43,588 → 27,297 토큰(37% 감소) / "doesn't break prompt caching because deferred tools are excluded from the initial prompt entirely." | https://www.anthropic.com/engineering/advanced-tool-use |
| vLLM, Automatic Prefix Caching | 같은 접두를 공유하는 요청은 KV 캐시를 재사용한다. 줄어드는 것은 프리필(입력 처리) 시간뿐이고 생성 시간은 그대로다. | `[추출]` "caches the KV cache of existing queries" / "does not reduce the time of generating new tokens (the decoding phase)." | https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/ |
| vLLM, Structured outputs | 선택지·정규식·JSON 스키마·문법으로 출력을 강제한다. 분류·예/아니오 단계에 쓴다. 옛 `guided_*` 인자는 폐기 예정. | `[추출]` "`choice`: the output will be exactly one of the choices." / "The default backend is `auto`" / "`guided_json` -> `{\"structured_outputs\": {\"json\": ...}}`" | https://docs.vllm.ai/en/latest/features/structured_outputs/ |
| vLLM, Metrics | 서빙 지표 이름. 캐시 적중률 = hits ÷ queries. | `[추출]` `vllm:time_to_first_token_seconds`, `vllm:inter_token_latency_seconds`, `vllm:e2e_request_latency_seconds`, `vllm:prefix_cache_hits`, `vllm:prefix_cache_queries`, `vllm:kv_cache_usage_perc`, `vllm:num_requests_waiting`, `vllm:request_queue_time_seconds` | https://docs.vllm.ai/en/latest/usage/metrics/ |

### 1-D. 배포·운영

| 출처 | 핵심 지침 | 짧은 인용 | URL |
|---|---|---|---|
| Google SRE Workbook, Canarying Releases | 카나리는 "일부에만, 정해진 시간 동안" 배포하고 평가하는 것. 전후 비교는 시간 요인 때문에 위험하니 같은 기간의 대조군과 비교한다. 한 번에 카나리 하나. 지표는 소수만. | `[추출]` "a partial and time-limited deployment of a change in a service and its evaluation." / "it is difficult to assess degradation of performance with before/after evaluation." / "strongly advise running only one canary deployment at a time." / "perhaps no more than a dozen" | https://sre.google/workbook/canarying-releases/ |
| Anthropic, A postmortem of three recent issues (2025-09) | 평가가 사용자가 느낀 저하를 못 잡았다. 평가를 운영 시스템에서 계속 돌리고, 사용자 신고 경로를 두고, 되돌린다. | `[추출]` "The evaluations we ran simply didn't capture the degradation users were reporting" / "we will run them continuously on true production systems" / "We identified the issue and rolled back the change on September 2" | https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues |
| Anthropic, Demystifying evals (운영 부분) | 자동 평가·운영 모니터링·A/B·사용자 피드백·수동 궤적 검토·사람 연구를 겹쳐 쓴다. 평가 소유는 전담팀이 아니라 도메인 전문가와 제품팀. | `[추출]` "no single evaluation layer catches every issue." / "Reactive; problems reach users before you know about them"(운영 모니터링의 약점) / "domain experts and product teams contribute most eval tasks and run the evaluations themselves." / "owning and iterating on evaluations should be as routine as maintaining unit tests." | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents |
| LangSmith, Online evaluations | 운영 기록에 평가기를 걸되 필터와 표본 비율로 비용을 통제한다. | `[추출]` "Online evaluations provide real-time feedback on your production traces." / "to only apply the evaluator to 10% of traces." | https://docs.langchain.com/langsmith/online-evaluations |
| Langfuse, Datasets | 기대대로 안 된 운영 기록을 골라 데이터셋 항목으로 만들고 전문가가 기대 출력을 단다. 데이터셋은 변경마다 버전이 생긴다. | `[추출]` "A common workflow is to select production traces where the application did not perform as expected." / "Every `add`, `update`, `delete`, or `archive` of dataset items produces a new dataset version." | https://langfuse.com/docs/evaluation/experiments/datasets |
| Claude Code, 마켓플레이스 운영 문서 | 스킬·훅·지침 묶음을 git 저장소의 카탈로그로 배포한다. 버전 문자열이 바뀌어야 사용자에게 간다. 태그·커밋 고정. 안정/선행 두 채널은 카탈로그 둘로 운영한다. | `[원문]` "Users get a new copy only when the plugin's computed version differs from the one they have." / "`ref` names a branch or tag and `sha` names a commit" / "To offer stable and early-access tracks, host two marketplaces whose entries point at different refs of the same plugin" | https://code.claude.com/docs/en/plugins/host-marketplace |
| Claude Code, 조직 플러그인 관리 문서 | 조직 강제는 관리 설정으로 한다(사용자가 못 끈다). 허용 목록·차단 목록·옆문 차단. 설치·로드 이벤트를 감사한다. 그룹별로 다른 채널을 배정한다. | `[원문]` "Users can't override them." / "disabling one at their own scope doesn't stop it from loading, because managed settings take precedence over every other scope." / "`claude_code.plugin_installed` records each install, and `claude_code.plugin_loaded` records each enabled plugin at session start." | https://code.claude.com/docs/en/plugins/org |
| Claude Code, 메모리 문서(조직 지침) | 조직 지침 파일은 안내용이고, 강제는 설정(권한 거부, 샌드박스)으로 한다. | `[원문]` 표: "Block specific tools, commands, or file paths → Managed settings: `permissions.deny`" / "Code style and quality guidelines → Managed CLAUDE.md" | https://code.claude.com/docs/en/memory |
| Claude Code, Monitoring 문서 | 세션·토큰·비용·도구 결정 지표와 API 요청·도구 결과 이벤트를 OpenTelemetry로 내보낸다. | `[추출]` `claude_code.token.usage`, `claude_code.cost.usage`, `claude_code.api_request`, `claude_code.tool_result`, `claude_code.tool_decision` | https://code.claude.com/docs/en/monitoring-usage |

---

## 2. 단계별 보강안

문서 형식(고민할 것 / 진행 / 검증 / 완료 기준 / 흔한 함정)에 맞췄다. 특정 프레임워크를 전제하지 않는 문장으로 썼고, 제품 고유 수치는 괄호 안 예시로만 뒀다.

### 2-1. S3 가운데 메모리 부분

현재 S3은 메모리를 "고민할 것 5번" 한 줄로만 다루고, 진행·검증·완료 기준에 메모리 항목이 없다. 그런데 `CRITERIA.md` 3-1은 S3에서 "규칙 저장소와 경험 저장소"를 만들라고 한다. 아래를 S3에 넣어 3-1의 집을 만든다. (검색·주입은 S6에 둔다. 저장소의 구조·쓰기 정책·보호는 S3이다.)

**고민할 것 (추가·교체)**

5. **무엇을 기억하나 (교체).** 세 종류로 나눈다.
   - 규칙(항상 지킬 것): 사람이 쓰고 리뷰한다. 항상 로드되므로 짧게 둔다.
   - 경험(과거 작업의 실패·해결·교훈): 에이전트가 작업 끝에 남긴다. 항상 로드하지 않고 검색해서 조금만 꺼낸다.
   - 절차(반복 작업의 순서): 스킬로 둔다. S4에서 다룬다.
   종류마다 누가 쓰고, 언제 로드되고, 누가 고칠 수 있는지가 다르다. 한 파일에 섞지 않는다.
6. **무엇을 저장하지 않나.** 코드와 git 기록에서 다시 알아낼 수 있는 것(구조, 파일 경로, 이미 고친 버그의 diff), 지침에 이미 있는 것, 시크릿·개인정보, 평가 정답·테스트 기대값, 외부에서 읽은 원문(이슈 본문, 웹 페이지, 도구 출력). 덜 뽑으면 재현율이, 많이 뽑으면 정밀도가 떨어진다. 기준은 "다음 작업자가 이걸 모르면 같은 실수를 하는가"다.
7. **언제 누가 쓰나.** 쓰기 시점은 코드가 정한다(작업 종료, 실패, 사람이 교정한 직후, 리뷰가 "알았어야 할 것"을 잡았을 때). 모델이 "기억할 만하다"고 느낄 때만 쓰게 하면 빠진다. 작업 중에 쓰면 바로 쓸 수 있지만 지연이 늘고, 작업 뒤에 쓰면 지연은 없지만 다음 작업이 먼저 시작되면 못 본다. 어느 쪽인지 정한다.
8. **기억이 낡으면.** 코드는 바뀐다. 기억마다 근거(실행 ID, 커밋, 파일·줄)를 붙이고, 쓸 때 그 근거가 아직 맞는지 확인한다. 만료 기한을 두고, 확인돼 쓰이면 연장한다.
9. **기억이 오염되면.** 메모리에 한 번 들어간 문장은 다음 세션에서 "믿을 수 있는 내용"으로 읽힌다. 외부 입력에서 나온 내용은 출처를 표시하고, 규칙 저장소는 에이전트에게 읽기 전용으로 둔다. 모든 변경은 되돌릴 수 있게 버전을 남긴다.
10. **얼마나 커지게 두나.** 항상 로드되는 양, 한 번에 주입하는 양, 항목 하나의 길이, 저장소 전체 건수에 상한을 둔다. 상한을 넘으면 요약으로 덮어쓰지 않고(세부가 사라진다) 항목 단위로 합치거나 폐기한다.

**진행 (추가)**

- 저장소를 둘로 만든다. 규칙은 지침 계층 파일, 경험은 한 줄에 한 건인 기록 파일(JSONL 등)과 한 줄 요약 색인. 사람이 열어 읽고 고칠 수 있는 평문으로 두고 버전 관리에 넣는다.
- 경험 기록 형식을 정한다(아래 "메모리 기록 형식"). 한 건에 교훈 하나, 검증할 수 있는 문장으로 쓴다.
- 쓰기 정책을 코드로 만든다.
  - 작업이 끝나거나 실패하면 훅·미들웨어가 기록 단계를 실행한다. 성공한 작업도 "새로 알게 된 것이 없으면 기록 없음"을 이벤트로 남긴다.
  - 저장 전에 검사한다: 필수 필드, 길이 상한, 시크릿 패턴, 평가 정답 흔적, 중복(같은 trigger·lesson이면 새로 만들지 않고 카운터만 올린다).
  - 갱신은 추가·카운터 증가·폐기 표시만 한다. 파일 전체를 모델이 다시 쓰게 하지 않는다.
  - 에이전트가 쓸 수 있는 곳은 경험 저장소의 "후보" 상태뿐이다. 규칙 저장소와 스킬은 S6의 개선안 경로로만 바뀐다. 실행 전 검사(S5)로 직접 편집을 막는다.
- 만료와 정리 주기를 정한다(예: 기본 90일, 검증돼 쓰이면 연장, "해로움" 표시가 임계를 넘으면 폐기 후보). 담당자를 정한다.
- 메모리 쓰기·검사 거부·폐기를 이벤트로 기록한다(S2 보강).

**메모리 기록 형식 (경험 1건)**

```json
{
  "id": "exp-0007",
  "kind": "experience",
  "status": "candidate",
  "scope": {"repo": "billing-api", "paths": ["src/invoice/**"], "task_type": "bugfix"},
  "trigger": "pytest에서 'Decimal is not JSON serializable'가 나올 때, 또는 src/invoice의 직렬화 코드를 고칠 때",
  "lesson": "금액 필드는 to_json_safe()를 거쳐 직렬화한다. json.dumps에 default=str을 넣지 않는다(반올림 규칙이 깨진다).",
  "outcome": "failure_fixed",
  "evidence": {
    "run_id": "req-2026-11-08-0412",
    "event_ids": ["ev-118", "ev-131"],
    "commit": "9f2c1ab",
    "citations": [{"path": "src/invoice/serialize.py", "lines": "40-58", "commit": "9f2c1ab"}]
  },
  "source": {"origin": "agent", "trust": "unverified", "derived_from_external_input": false},
  "created_at": "2026-11-08T04:31:00Z",
  "last_verified_at": null,
  "expires_at": "2027-02-06T00:00:00Z",
  "counters": {"retrieved": 0, "cited_in_plan": 0, "helpful": 0, "harmful": 0},
  "supersedes": null,
  "harness_version": "r3"
}
```

필드별 이유
- `kind`: `rule`(항상 로드), `experience`(검색), `procedure`(스킬 포인터). 로드 방식과 수정 권한이 여기서 갈린다.
- `status`: `candidate`(에이전트가 방금 쓴 것) → `active`(한 번 이상 근거가 확인돼 쓰였거나 사람이 승인) → `deprecated`(낡았거나 해로움). 삭제하지 않고 상태를 바꾼다.
- `scope`: 검색의 1차 필터. 저장소·경로·작업 종류가 다르면 꺼내지 않는다.
- `trigger`: 검색 키. 오류 문자열, 파일 경로, 명령어처럼 정확히 일치시킬 수 있는 표현을 넣는다.
- `lesson`: 행동 문장. "조심한다"가 아니라 무엇을 하고 무엇을 하지 않는지.
- `evidence`: 실행 기록과 코드 위치. 쓸 때 대조한다. 근거가 없는 항목은 `active`가 될 수 없다.
- `source.trust`: `verified`(사람 승인 또는 개선 라운드 통과), `unverified`(에이전트 자동 기록), `untrusted`(외부 입력 유래). `untrusted`는 주입하지 않는다.
- `counters`: 주입 횟수, 계획에 인용된 횟수, 도움/해로움. 정리와 승격의 근거.
- `supersedes`: 틀린 항목을 고칠 때 덮어쓰지 않고 새 항목이 옛 항목을 가리킨다.
- `harness_version`: 어느 버전의 에이전트가 쓴 것인지. 되돌릴 때 같이 걸러낸다.

규칙 항목(`kind: rule`)은 같은 필드에 `approved_by`, `adopted_in_round`(S6 라운드 번호), `enforcement`(지침/스킬/훅/테스트 중 지금 어느 층에 있는지)를 더한다.

**검증 (추가)**

- 왕복 확인: 값을 하나 쓰고, 프로세스를 끝내고, 새 프로세스에서 에이전트가 쓰는 것과 같은 경로로 읽는다. 저장과 조회가 실제로 이어져 있는지 점수를 보기 전에 확인한다.
- 일부러 실패시킨 작업이 끝나면 경험 1건이 `candidate`로 생기고 기록에 `memory_write` 이벤트가 있다.
- 거부 시험: 시크릿 모양 문자열, 평가 정답 문자열, 상한을 넘는 길이, 저장소 밖 경로(`../`)를 넣어 전부 거부되는지 본다.
- 직접 편집 시험: 에이전트에게 규칙 파일을 고치라고 시켜 막히는지 본다(셸 우회 포함).
- 낡음 시험: 근거 파일을 바꾼 뒤 그 항목이 "근거 불일치"로 표시되는지 본다.
- 크기: 세션 시작 로드량과 저장소 건수·총 크기를 잰다.

**완료 기준 (추가)**

- [ ] 규칙 저장소와 경험 저장소가 따로 있고, 종류별로 누가 쓰고 누가 고치는지가 `design/03-context.md`에 있다
- [ ] 작업 종료·실패 때 경험이 기록되고, 프로세스를 끝낸 뒤 새 세션에서 같은 경로로 읽힌다 (기록의 `memory_write` 이벤트와 왕복 확인 결과)
- [ ] 저장 전 검사(시크릿, 정답 흔적, 길이, 경로)와 규칙 저장소 직접 편집 차단의 시험 기록이 있다
- [ ] 로드량·주입량·항목 길이·건수 상한과 만료·정리 담당자가 적혀 있다

**흔한 함정 (추가)**

- 대화 전체나 도구 출력 원문을 경험으로 저장하기(검색 정밀도가 무너지고 주입 경로가 된다)
- 메모리가 길어지면 모델에게 "요약해서 다시 써라"고 하기(세부 규칙이 사라지고 짧고 일반적인 문장만 남는다)
- 코드에서 읽으면 되는 것을 기억으로 두기(코드가 바뀌면 틀린 기억이 된다)
- 저장 파일이 남아 있다는 것만으로 "기억한다"고 판단하기(쓰기 이벤트와 왕복 확인이 증거다)

근거: Memory tool 문서(크기 상한·만료·민감정보·경로 검증), Claude Code 메모리 문서(지침/자동 메모리 분리, 200줄/25KB, 유도 가능한 것은 저장 안 함), Managed Agents 메모리 문서(읽기 전용, 불변 버전, 주입 경고), Copilot 메모리 글(인용 + 사용 시점 검증, 만료), ACE(증분 갱신, 무너짐), LangMem(과다·과소 추출), eval-hillclimb(왕복 확인).

---

### 2-2. S6 메모리 기반 자기개선

**고민할 것 (교체)**

1. **무엇으로 찾나.** 경험이 수백 건 이하이면 구조 필터(저장소·경로·작업 종류)와 키워드 검색(오류 문자열, 심볼, 파일명)으로 충분하다. 코딩 작업의 검색 키는 정확히 일치해야 하는 문자열이 많아서 임베딩만 쓰면 놓친다. 임베딩은 재현율이 모자란다고 측정된 뒤에 키워드와 함께 쓴다.
2. **언제, 얼마나 꺼내나.** 요청을 받은 직후(계획 전)와 실패 직후(그 오류 문자열로) 두 번. 한 번에 3~5건, 토큰 상한을 둔다. 본문 전체가 아니라 `trigger`와 `lesson`만 넣고 근거는 경로로 가리킨다.
3. **꺼낸 기억을 믿어도 되나.** 주입 전에 근거(파일·커밋)가 지금 코드와 맞는지 확인한다. 안 맞으면 주입하지 않고 `harmful`을 올린다. `untrusted` 출처는 주입하지 않는다.
4. **어디에 넣나.** 시스템 프롬프트를 고치지 않는다(캐시가 깨지고 모든 요청에 영향이 간다). 요청 뒤에 별도 메시지로 한 번 붙이고 대화 중에 지우거나 바꾸지 않는다.
5. **"활용했다"를 무엇으로 보이나.** 조회 이벤트는 "꺼냈다"일 뿐이다. 계획에 어느 항목을 어떻게 반영했는지 적게 하고, 같은 작업을 메모리 없이 돌린 결과와 비교한다.
6. **무엇을 고치게 하나.** 한 라운드에 한 종류, 한 가설만 연다: 시스템 프롬프트의 지정 구역 / 스킬 문서 하나 / 메모리 규칙 항목. 고칠 수 없는 것: 평가셋·정답·숨긴 테스트, 채점기·루브릭·임계값·반복 수, 채택 기준, 권한·훅·게이트 설정, 예산(턴·시간·토큰), 모델·추론 강도(S7의 몫), 실행 기록, 저장소의 테스트 코드, 개선 루프의 코드. 이 경계는 지시문이 아니라 경로 허용 목록과 해시 검사로 막는다. 모델에게 "속이지 말라"고 적는 것은 효과가 거의 없다.
7. **개선안을 만드는 쪽이 무엇을 보나.** 개선안은 자기가 읽은 실패에 맞춰진다. 채택 판정은 개선안을 만든 쪽이 읽지 않은 사례로 한다. 사례가 적어 나눌 수 없으면 나누지 않고 반복 실행으로 흔들림을 줄이되, 결과를 "방향성"이라고 표시한다.
8. **얼마나 좋아져야 받아들이나.** 같은 버전을 여러 번 돌렸을 때의 흔들림(노이즈 폭)을 먼저 잰다. 그보다 작은 개선은 우연과 구별되지 않는다. 최소 효과, 반복 수, 회귀 정의, 비용·길이 상한을 결과를 보기 전에 적는다.
9. **사람이 어디서 보나.** 경험 기록(후보)은 자동. 항상 로드되는 규칙·스킬·시스템 프롬프트의 변경은 사람 승인. 누가 승인하는지 정한다.
10. **언제 멈추나.** 최대 라운드 수와 비용 상한. 2~3 라운드 연속으로 점수가 노이즈 폭을 못 넘으면 내용을 더 고치지 않고 남은 실패를 원인별로 분류한다(지침 부족 / 채점기 문제 / 환경·하네스 문제 / 구조 문제 / 흔들림).

**진행 (교체)**

1. **검색·주입을 만든다.** 조회마다 `memory_retrieve` 이벤트를 남긴다: 질의, 필터, 후보(id·점수), 근거 확인 결과, 주입한 id, 주입 토큰 수, 소요 시간. 결과 없음과 조회 오류를 구분한다.
2. **계획 양식에 "참조한 경험" 구역을 넣는다.** 항목 id와 "이 계획에서 무엇이 달라졌는지"를 한 줄씩. 주입된 것이 없으면 "없음"이라고 쓴다. 작업이 끝나면 항목마다 `helpful`/`harmful`/`unused`를 `memory_feedback` 이벤트로 남기고 카운터를 올린다.
3. **개선 설정을 실행 전에 고정한다**(아래 "채택 판정 절차" 0단계). 파일로 커밋하고 해시를 남긴다.
4. **실패를 모은다.** 기록에서 실패 신호(도구 오류, 테스트 실패, 채점의 수정 필요 판정, 리뷰 수정 반복, 게이트 차단, 최대 턴 도달)와 운영 기록의 "해로움" 표시를 모은다. 실패마다 관찰 사실 / 원인 가설 / 다른 설명 / 근거 이벤트를 나눠 적는다. 개선안을 만드는 쪽에 넘기는 것은 개발용 가운데 "읽기용"으로 정한 사례의 기록뿐이다.
5. **오염을 검사한다.** 넘기는 입력에 정답, 임계값, 판정용·최종 확인용 사례 ID, 테스트 기대값이 있으면 호출하지 않고 멈춘다. 평가 하네스 파일의 해시가 고정값과 같은지 확인한다.
6. **개선안을 만든다.** 아래 형식으로 받는다. 변경은 diff로, 항목 단위로. 문서 전체를 다시 쓰는 변경은 형식 검사에서 거부한다. 변경 경로가 허용 목록 밖이면 거부한다. 거부한 후보도 사유와 함께 남긴다.
7. **같은 조건으로 비교한다.** 현재 버전과 후보를 분리된 프로필(메모리·설정이 섞이지 않게)에서, 같은 평가셋·모델·예산·반복 수로 돌린다. 시도마다 초기 상태를 복원한다. 메모리는 세션 시작 때 한 번 읽히는 구조가 많으므로 반영 효과는 새 세션에서 잰다.
8. **판정한다**(아래 절차). 판정과 근거를 `improve/round-<n>.json`에 새 파일로 쓴다.
9. **통과한 것만 반영한다.** 버전 표시를 올리고, 커밋하고, 되돌리는 명령을 적는다. 새 세션에서 같은 종류의 작업을 돌려 반영된 항목이 조회·인용된 기록을 남긴다.
10. **같은 실수가 다시 나오면 더 강한 층으로 옮긴다:** 경험 → 규칙(지침) → 스킬 → 훅·권한 → 테스트·CI. 옮기면 아래 층의 항목은 폐기 표시한다(같은 내용이 두 곳에 있으면 충돌한다).

**개선안 형식**

```json
{
  "proposal_id": "imp-r2-c1",
  "round": 2,
  "base_version": "r1",
  "target": {"kind": "skill", "path": "skills/write-tests/SKILL.md", "section": "procedure"},
  "evidence": [
    {"run_id": "req-0412", "event_ids": ["ev-118"], "failure_type": "테스트 미실행", "quote": "…기록에서 그대로 옮긴 줄…"}
  ],
  "observation": "개발용 12건 중 4건에서 수정 뒤 테스트 명령이 실행되지 않았다.",
  "hypothesis": "스킬 본문에 테스트 대상 선택 규칙이 없어 전체 실행을 피하려다 건너뛴다.",
  "alternatives": ["턴 예산이 모자라 끝냈다", "테스트 명령이 실패해 조용히 넘어갔다"],
  "change": {"format": "unified_diff", "patch_file": "improve/r2/c1.patch", "added_tokens": 96, "removed_tokens": 0},
  "expected_effect": {"metric": "판정용 사례의 '테스트 미실행' 실패 수", "direction": "down", "cases_expected_to_flip": 3},
  "predicted_regressions": ["테스트가 없는 모듈에서 불필요한 테스트 생성"],
  "layer_check": "훅으로 강제할 수 있는가: 가능(끝내기 전 검사). 이번 라운드는 스킬 문구, 재발하면 훅으로 옮긴다.",
  "forbidden_check": {"touched_paths": ["skills/write-tests/SKILL.md"], "violations": []},
  "rollback": "git revert <커밋> 또는 버전 표시를 r1로 되돌림",
  "improver_input_hash": "sha256:…",
  "status": "proposed"
}
```

고칠 수 있는 것과 없는 것 (코드로 강제)

| 고칠 수 있다 (한 라운드에 한 종류) | 고칠 수 없다 |
|---|---|
| 시스템 프롬프트의 지정 구역 | 평가셋, 정답, 숨긴 테스트, 분할(ID 목록) |
| 스킬 문서 하나(설명문 또는 본문) | 채점기 코드, 루브릭, 임계값, 반복 수, 채택 기준 |
| 메모리 규칙 항목의 추가·폐기 | 권한 설정, 훅, 게이트, 금지 행동 목록 |
| | 예산(턴·시간·토큰), 모델, 추론 강도 |
| | 실행 기록(삭제·수정), 저장소의 테스트 코드 |
| | 개선 루프와 판정기의 코드, 이 표 |

형식 검사에서 거부하는 것: 허용 목록 밖 경로, 문서 전체 교체, 기준을 낮추는 문구("테스트가 실패해도 진행"), 실패 사례의 고유 명사·문자열을 그대로 붙여 넣은 변경(외우기), 현재 버전과 같은 후보, 길이 상한 초과.

**채택 판정 절차 (사전 등록)**

0. **사전 등록 (실행 전에 파일로 고정).**
   - 손잡이(한 종류)와 허용 경로
   - 데이터: 읽기용 ID 목록(개선안을 만드는 쪽이 본다) / 판정용 ID 목록(보지 않는다) / 최종 확인용(이 루프에서 열지 않는다, S8에서 한 번). 분할은 유형별로 무작위로 뽑고 기준선 점수로 고르지 않는다. 사례가 적으면 "분할 없음, 방향성 판정"이라고 적는다.
   - 반복 수 R(예: 3), 주 지표, 관문 지표(정책 위반), 가드레일 지표(통과 1건당 비용, 지연, 항상 로드되는 토큰 수)와 각 상한
   - 노이즈 폭 측정 방법(현재 버전을 바꾸지 않고 한 번 더 돌린 차이), 최소 효과
   - 회귀 정의, 재실행 허용 규칙, 최대 라운드, 비용 상한, 판정 순서, 승인자
1. **잴 수 있는가.** 하네스 해시 일치, 오염 검사 통과, 양쪽 평가 완료율이 기준(예: 90%) 이상, 응답에 찍힌 모델이 설정과 일치, 현재 버전에 고칠 실패가 있음, 노이즈 폭이 최소 효과보다 작음. 하나라도 아니면 **판정 불가**. "개선 없음"이 아니라 "재지 못함"이다.
2. **관문.** 후보에서 정책 위반이 1건이라도 있거나 금지 경로를 건드렸으면 **기각**.
3. **회귀.** 현재 버전에서 R번 모두 통과하던 사례가 후보에서 과반 실패하거나, 새 실패 유형이 생기면 **보류**. (한 번만 실패했으면 사전 등록한 규칙대로 그 사례만 재실행해 확인한다.)
4. **효과.** 판정용 사례에서 주 지표의 개선이 최소 효과 이상이고 노이즈 폭을 넘는다. 읽기용만 오르고 판정용이 그대로면 과적합이다 → **기각**.
5. **가드레일.** 통과 1건당 비용, 지연, 항상 로드되는 토큰 증가가 상한 안이다. 넘으면 **보류**.
6. **메커니즘.** 후보 실행의 기록에 바뀐 항목이 실제로 로드·조회·인용된 흔적이 있다. 점수는 올랐는데 흔적이 없으면 **보류**(우연이거나 측정 문제다).
7. **이상 점검.** 변경으로 설명하기 어려울 만큼 크게 올랐으면 좋은 소식으로 치기 전에 사례 몇 건을 손으로 확인한다(모델 채점이 겉모양에 속았을 수 있다).
8. **사람 승인.** 항상 로드되는 규칙·스킬·시스템 프롬프트 변경은 승인자가 diff와 비교표를 보고 승인한다.
9. **반영.** 버전 표시를 올리고 변경 기록을 남긴다. 새 세션에서 쓰인 기록을 붙인다.
10. **사후 확인.** 반영 뒤 정한 기간(또는 건수) 동안 운영 지표를 보고, 되돌리기 기준에 닿으면 이전 버전으로 돌린다.

그 밖의 모든 경우는 **보류**다. 판정은 채택 / 보류 / 기각 / 판정 불가 넷 중 하나로만 적는다.

**인수 기준 3-1 ~ 3-4를 증거로 보이는 방법**

| 항목 | 약한 증거 (인정받기 어렵다) | 강한 증거 | README 확인 방법 (입력 → 기대 관찰 → 확인 명령) |
|---|---|---|---|
| 3-1 저장·유지 | 저장소 파일이 있다 | ① 세션 A의 기록에 `memory_write` 이벤트(항목 id, 종류, 실행 ID) ② 프로세스를 끝낸 뒤 파일에 그 id가 있다 ③ 규칙과 경험이 서로 다른 저장소에 한 건씩 있다 ④ 실패한 작업에서도 기록이 생겼다 | 일부러 실패하는 작업 실행 → 종료 → 경험 파일 마지막 줄에 `outcome: failure_*` 항목 → `grep <id> <경험 파일>` 과 기록 조회 도구로 `memory_write` 확인 |
| 3-2 검색·실제 활용 | 기록에 조회 이벤트가 있다 | ① 새 프로세스(세션 B)의 `memory_retrieve` 이벤트에 세션 A가 남긴 id가 "주입됨" ② 세션 B의 계획 "참조한 경험" 구역에 그 id와 반영 내용 ③ 코드 변경이 교훈을 따랐다(예: 금지한 방식이 diff에 없다) ④ 같은 작업을 메모리 주입을 끄고 돌린 결과와 다르다 | 세션 A와 비슷한 요청을 새 세션에 입력 → 계획에 `참조한 경험: exp-…` → 조회 도구로 요청 ID의 `memory_retrieve`·`memory_feedback` 이벤트 출력. 대조: 주입 토글을 끄고 같은 요청 |
| 3-3 개선안 생성 | "개선이 필요하다"는 문장 | ① 실패 기록의 이벤트 id를 인용한 개선안 파일(관찰/가설/변경 diff/기대 효과/예상 회귀) ② 대상이 시스템 프롬프트·스킬·메모리 규칙 중 하나로 명시 ③ 생성 시점에 대상 파일이 바뀌지 않았다(`git status`가 깨끗) ④ 금지 경로를 건드린 후보가 거부된 기록 ⑤ `improve_propose` 이벤트 | 실패하는 평가 시나리오 실행 → 개선 명령 실행 → `improve/r<n>/c1.json`과 `.patch` 생성 → `git diff --stat`에 대상 파일 변경 없음 확인 |
| 3-4 전후 검증·반영 | 전후 점수 두 개 | ① 사전 등록 파일(실행 전 커밋 시각이 결과보다 앞선다) ② 같은 평가셋 버전·모델·예산·반복 수의 전후 표(사례별) ③ 회귀 검사 결과(기존 통과 사례) ④ 판정과 사유 ⑤ 탈락한 후보가 반영되지 않았다는 확인(버전 표시 그대로) ⑥ 채택분의 버전 표시 변경과 커밋 ⑦ 반영 뒤 새 세션에서 그 항목이 조회·인용된 기록 | 평가 명령을 현재 버전과 후보로 실행 → 비교표 출력 → `improve/round-<n>.json`의 판정 → 채택이면 버전 표시 r(n)→r(n+1) → 새 세션 요청 → 기록에 새 버전과 해당 항목 id |

한 라운드가 "보류"로 끝나도 3-4의 절차 증거는 된다. 다만 "통과한 개선안을 다음 작업에 반영"까지 보이려면 채택이 한 번은 있어야 한다. 일부러 실패시킨 작업에서 고칠 수 있는 실패(예: 테스트 명령을 모르는 상태)를 하나 준비해 둔다.

**검증 (교체)**

- 세션 A에서 남긴 경험이 새 프로세스의 세션 B 기록에 "주입됨"으로 보이고, 계획에 인용된다.
- 주입을 끄고 같은 작업을 돌려 차이를 본다. 차이가 없으면 검색이 엉뚱한 것을 꺼내거나 평가가 그 능력을 재지 않는 것이다.
- 근거 파일을 바꾼 항목은 주입되지 않는다. `untrusted` 항목도 주입되지 않는다.
- 일부러 실패시킨 작업에서 개선안이 만들어지고, 그 시점에 대상 파일은 바뀌지 않았다.
- 개선안이 금지 경로(테스트, 채점기, 권한)를 건드리도록 유도해 거부되는지 본다. 하네스 파일을 한 글자 바꿔 해시 검사가 멈추는지 본다.
- 같은 버전을 두 번 돌려 노이즈 폭을 적는다.
- 전후 비교표가 있고, 탈락한 개선안은 반영되지 않았다. 개선 뒤 기존에 통과하던 사례가 회귀하지 않았다.
- 채택한 변경을 되돌리는 명령을 실제로 실행해 이전 버전으로 돌아가는지 본다.

**완료 기준 (교체)**

- [ ] 기억 → 조회 → 계획 인용이 새 세션의 기록으로 확인됐고, 주입을 껐을 때와의 차이가 적혀 있다
- [ ] 개선 설정(손잡이, 고칠 수 없는 것, 데이터 분할, 반복 수, 노이즈 폭, 채택 기준, 승인자)이 실행 전에 고정돼 있다
- [ ] 금지 경로 변경과 하네스 변조가 막히는 시험 기록이 있다
- [ ] 개선 라운드가 한 번 이상 기록됐다(채택·보류·기각·판정 불가 중 무엇이든, 사유와 함께)
- [ ] 채택한 변경마다 전후 표, 회귀 결과, 버전 표시, 되돌리는 방법, 새 세션에서 쓰인 기록이 `design/06-improve.md`에 있다

**흔한 함정 (교체)**

- 에이전트가 규칙·스킬 파일을 직접 고쳐 검증을 건너뛰게 두기
- 같은 세션에서 효과를 재기(메모리와 스킬 목록은 세션 시작 때 한 번만 읽힌다)
- 개선안이 테스트나 채점 코드를 고쳐서 통과시키기. "고치지 말라"는 지시로 막으려 하기
- 개선안을 만든 쪽이 읽은 실패 사례로 채택을 판정하기
- 한 번 돌린 결과의 1건 차이로 채택하기
- 조회 이벤트만으로 "활용했다"고 하기
- 메모리·프롬프트를 통째로 다시 쓰게 하기(짧고 일반적인 문장으로 무너진다). 반대로, 라운드마다 "조심하라" 같은 문장을 쌓기
- 최종 확인용 데이터로 라운드마다 판정하기(몇 번 고르고 나면 그 데이터에 맞춰진다)
- 실패의 원인이 채점기나 환경인데 지침만 계속 고치기

---

### 2-3. S7 모델·비용·속도 최적화

**고민할 것 (교체)**

1. **무엇을 단위로 재나.** 호출 1건이나 토큰 1개가 아니라 "통과한 작업 1건당 비용"과 "작업 1건의 전체 시간". 싼 모델이 실패하면 그 토큰과 재시도까지 값이다. 요청 종류(대화형, 야간 일괄)가 다르면 따로 잰다. 중앙값만 보지 않고 느리고 비싼 꼬리(p95)를 본다.
2. **시간이 어디서 나오나.** 작업 시간 ≈ 호출 수 × 첫 토큰까지 시간 + 출력 토큰 ÷ 출력 속도 + 모델 밖 시간(도구 실행, 대기열, 재시도). 다섯 항 가운데 어디가 큰지 기록에서 찾는다. "첫 토큰"과 "사용자가 처음 보는 출력"은 다르다(생각이 먼저 나오면 차이가 크다).
3. **무엇이 "동작 유지"인가.** 도구 호출 순서까지 똑같아야 한다는 기준은 대부분의 최적화(모델 교체, 추론 강도 조정, 도구 통합, 서브에이전트 분리)와 양립하지 않는다. 대신 지켜야 할 것을 미리 적는다: 결과 통과율이 노이즈 폭 안, 정책 위반 0건, S1의 과정 규칙(승인 전 수정 금지, 테스트 실행 등) 통과, 최종 응답과 실제 변경의 일치.
4. **품질을 걸지 않는 것과 거는 것.** 앞의 것부터 한다.
   - 걸지 않는 것: 캐시가 맞게 프롬프트 배치, 안 쓰는 도구·지침 빼기, 재시도·중복 호출 줄이기, 출력 형식 줄이기, 기다려도 되는 일은 일괄 처리.
   - 거는 것: 추론 강도 낮추기, 예산 조이기, 작은 모델로 내리기, 여러 모델로 나누기. 평가 없이는 적용하지 않는다.
5. **모델을 나누기 전에.** 같은 모델에서 추론 강도를 낮춘 결과를 먼저 잰다. 모델이 하나면 캐시도 하나다. 모델을 나누면 캐시가 갈라지고 관리할 것이 늘어난다. 나눈 구성은 단일 모델의 점수-비용 곡선 전체를 이겨야 한다.
6. **서브에이전트로 빨라지나.** 독립적인 작업을 동시에 돌릴 때와 한 컨텍스트에 안 들어가는 일일 때만 이득이다. 서브에이전트는 부모의 캐시를 못 쓰고 각자 컨텍스트를 다시 읽으므로 비용은 오를 수 있다.
7. **직접 서빙한다면.** 접두 캐시가 켜져 있고 실제로 맞는지, 분류 단계는 출력을 선택지로 강제했는지, 대기열이 쌓이는지. 접두 캐시는 입력 처리 시간만 줄이고 생성 시간은 그대로다. 하드웨어를 늘리기 전에 소프트웨어로 줄인다.
8. **S6과 겹치면.** S6이 프롬프트·스킬을 바꾸면 S7의 기준선이 바뀐다. 반영은 하나씩 하고, S6 채택 뒤에는 S7 기준선을 다시 잰다.

**진행 (교체)**

1. **목표와 유지 기준을 적는다.** S0의 지연·비용 목표, 3번의 유지 기준, 노이즈 폭.
2. **기준선을 요청 종류별로 잰다.** 통과 1건당 비용, 전체 시간 p50/p95, 첫 토큰 시간, 호출 수, 입력·출력 토큰, 캐시에서 읽은 비율, 재시도 수, 도구 실행 시간.
3. **낭비를 기록에서 찾아 줄 세운다.** 항목마다 "최대 얼마나 줄일 수 있는가"를 적고, 작은 것은 버린다. 대부분의 레버는 그 작업에 맞지 않는다.
4. **순서대로 한 번에 하나씩 적용한다.**
   1. 캐시: 고정 내용(도구 정의, 시스템 지시, 지침)을 앞에 얼리고, 바뀌는 값(날짜, 요청별 ID, 주입한 메모리)은 뒤의 메시지로 보낸다. 대화 중 도구 목록과 모델을 바꾸지 않는다. 도구 정의는 이름순으로 고정 직렬화한다. 캐시 적중이 0이면 연속 두 요청의 프롬프트 바이트를 비교해 원인을 찾는다. (Anthropic API 예: 중단점 최대 4개, 5분 TTL 쓰기 1.25배·읽기 0.1배, 모델별 최소 길이 미만은 캐시되지 않는다. vLLM 예: 접두 캐시를 켜고 `prefix_cache_hits ÷ prefix_cache_queries`를 본다.)
   2. 입력: 안 쓰는 도구 빼기, 도구를 필요할 때 찾게 하기, 프롬프트에 박힌 조각 지식을 스킬로 빼기, 예전 모델용으로 쓴 과잉 지시("두 번 확인하라") 지우기.
   3. 루프: 오류 뒤 같은 호출 반복, 묶을 수 있는 연속 호출(스크립트 하나로), 규칙으로 끝낼 수 있는 판단을 코드로.
   4. 출력: 응답 형식을 정하고, 도구 호출 사이의 설명을 줄인다. 출력 상한을 낮추는 것은 절약이 아니다(모델은 상한을 모르고, 잘리면 재시도한다).
   5. 일괄 처리: 평가 실행, 야간 작업처럼 아무도 기다리지 않는 일.
   6. 추론 강도·예산: 평가셋으로 단계별로 훑어 점수-비용 표를 만든다. 낮은 강도로 돌리고 확인 가능한 실패만 높은 강도로 다시 돌리는 방식을 후보에 넣는다.
   7. 모델 교체: 분류·선택·예/아니오부터. 큰 모델의 낮은 강도와 작은 모델의 기본 강도를 통과 1건당 비용으로 비교한다. 직접 서빙이면 판단 단계의 출력을 선택지로 강제한다.
   8. 여러 모델·서브에이전트: 위를 다 해도 목표에 못 미칠 때만.
5. **변경마다 켜고 끌 수 있게 만들고**, 기존 문제 → 변경 → 전후 수치 → 유지 기준 통과 여부를 남긴다. 근거가 없거나 효과가 노이즈 폭 안이면 되돌린다.
6. **직접 서빙이면** `serving-plan`으로 용량과 설정을 다시 본다. 양자화나 모델 교체는 평가셋으로 품질을 다시 잰 뒤 채택한다.
7. **교체 전에 그림자 실행을 한다.** 고른 구성을 실제 요청의 일부로 돌려 보고, 교체 뒤에도 평가를 계속 돌린다.

**검증 (교체)**

- 변경마다 평가를 다시 돌려 유지 기준(결과 통과율, 정책 위반 0, 과정 규칙)을 확인한다.
- 전후를 같은 조건(데이터 버전, 반복 수, 동시성, 캐시 상태)으로 잰다. 캐시가 찬 상태와 식은 상태를 구분해 적는다.
- 응답에 찍힌 모델 이름이 설정과 같은지 확인한다(조용한 대체가 있으면 비교가 무효다).
- 캐시 적중을 사용량 필드(캐시 읽기 토큰)나 서빙 지표로 직접 확인한다.
- 토글을 꺼서 이전 수치로 돌아가는지 본다.

**완료 기준 (교체)**

- [ ] 요청 종류별 기준선(통과 1건당 비용, 전체 시간 p50/p95, 첫 토큰 시간, 호출 수, 토큰, 캐시 읽기 비율)이 있다
- [ ] 유지 기준이 변경 전에 적혀 있고, 변경마다 전후 수치와 유지 기준 통과 여부가 `design/07-optimize.md`에 있다
- [ ] 품질을 거는 변경(추론 강도, 모델, 예산)은 평가셋의 점수-비용 표를 근거로 채택했다
- [ ] S0의 지연·비용 목표에 도달했거나, 더 줄이지 않는 근거(남은 레버와 예상 효과)가 적혀 있다

**흔한 함정 (교체)**

- 평가 없이 모델부터 내리기, 여러 변경을 한꺼번에 넣기, 남이 잰 수치를 그대로 믿기
- 호출당 비용이나 토큰 단가로 비교하기(실패와 재시도가 빠진다)
- 날짜·요청 ID·사용자별 값을 시스템 프롬프트에 넣어 캐시를 매번 깨기, 대화 중에 도구 목록을 바꾸기
- 서브에이전트로 쪼개면 싸진다고 가정하기
- 첫 토큰 시간만 줄이고 전체 시간은 재지 않기
- "도구 호출 순서가 같아야 한다"를 기준으로 삼아 모델 교체를 전부 탈락시키거나, 반대로 기준 없이 "비슷해 보인다"로 통과시키기

---

### 2-4. S8 배포·운영

**고민할 것 (추가·교체)**

1. **무엇을 한 버전으로 묶나.** 시스템 프롬프트, 지침, 스킬, 훅·권한, 메모리 규칙, 모델·추론 강도, 평가셋 버전을 한 묶음(릴리스 목록)으로 고정한다. 이 가운데 하나만 바뀌어도 새 버전이다. 전부 코드처럼 저장소에 두고 리뷰를 거친다.
2. **어떻게 나눠 주나.** 설정 묶음, 플러그인, 사내 레지스트리 가운데 무엇으로 배포하나. 사용자가 받는 버전을 고정할 수 있는가(태그·커밋). 안정 채널과 선행 채널을 둘 것인가.
3. **무엇을 조직 차원에서 강제하나.** 개인이 끌 수 없어야 하는 검사·권한은 관리 설정으로, 안내는 조직 지침으로. 둘은 다르다.
4. **단계적으로 어떻게 넓히나.** 최종 확인 → 쓰기 없는 재생(과거 요청을 새 버전으로 돌려 계획·diff만 비교) → 소수 사용자·위험이 낮은 저장소 → 전체. 단계마다 넘어가는 기준과 멈추는 기준을 미리 적는다.
5. **운영에서 무엇을 보나.** 오프라인 평가는 실제 사용과 다를 수 있고, 운영 지표는 문제가 사용자에게 닿은 뒤에야 보인다. 둘 다 둔다. 소수 지표만 고른다: 정책 위반·게이트 차단, 작업 완료율, 사람이 다시 고친 비율(또는 PR 병합률), 재시도·최대 턴 도달, 통과 1건당 비용, 전체 시간, 메모리 "해로움" 표시, 사용자 신고.
6. **무엇과 비교하나.** 배포 전후 비교는 시간이 지나며 바뀌는 다른 요인(작업 종류, 모델 서빙 상태)과 섞인다. 같은 기간에 이전 버전을 쓰는 집단을 남겨 비교한다. 카나리는 한 번에 하나만.
7. **운영 기록을 어떻게 되먹이나.** 반복되고, 재현할 수 있고, 정답을 정의할 수 있는 기록을 평가셋으로 승격한다. 새로 승격한 사례는 능력 평가(아직 못 푸는 것)에, 안정적으로 통과하게 되면 회귀 평가(거의 다 통과해야 하는 것)로 옮긴다. 최종 확인용은 한 번 쓰면 닳으므로 운영 기록에서 새로 채운다.
8. **누가 소유하나.** 평가셋, 지침, 스킬, 훅·권한, 메모리(정리·만료·감사), 릴리스 승인, 사고 대응 각각의 담당자. 평가 사례는 전담자만이 아니라 그 코드베이스를 아는 사람이 기여한다. 자기 변경을 자기가 승인하지 않는다.
9. **되돌리기와 사고.** 무엇을 어떤 버전으로, 누가, 얼마나 빨리. 즉시 끌 수 있는 스위치(메모리 주입, 자기개선 반영, 선행 채널). 사고 뒤에는 그 사례를 평가에 넣고 더 강한 층으로 옮긴다.
10. **바깥이 바뀌면.** 모델 버전이 바뀌면 평가를 다시 돌리고 추론 강도를 다시 훑는다(같은 이름의 단계라도 양이 달라진다). 기반 에이전트를 올리면 훅·게이트 시험을 다시 한다.
11. **기록에 무엇이 들어가나.** 사내 코드와 개인정보. 보존 기간, 접근 권한, 가리기 규칙을 정한다. 접근을 조이면 문제 진단이 느려진다는 점까지 감안해 신고 경로를 따로 둔다.

**진행 (교체)**

1. **릴리스 후보를 고정한다.** 릴리스 목록(구성요소별 버전·해시)을 만들고 태그를 단다.
2. **최종 확인용 평가를 한 번 돌린다.** 미리 정한 승인 기준으로 판정한다. 결과를 보고 다시 고치면 새 실험이고, 그 최종 확인용은 다음에 쓰지 못하니 새로 채운다.
3. **쓰기 없는 재생.** 최근 실제 요청 표본을 새 버전으로 돌려(변경은 버려지는 작업 폴더·브랜치에서) 계획, diff, 비용, 시간을 이전 버전과 나란히 본다.
4. **소수 사용자로 시범 운영한다.** 대조 집단, 기간, 넘어가는 기준, 멈추는 기준(예: 정책 위반 1건이면 즉시 중단)을 적고 시작한다. 기록을 매주 읽는다.
5. **운영 평가를 건다.** 모든 요청을 평가하지 않는다. 표본(예: 10%)을 뽑거나 "확인 필요" 표시가 붙은 기록만 본다. 코드로 잴 수 있는 지표는 전수로 모은다.
6. **신고 경로를 만든다.** 사용자가 한 줄 명령으로 요청 ID와 함께 문제를 남길 수 있게 한다.
7. **주간 회고를 돈다.** 기록 읽기 → 실패 분류 → 평가셋 승격 후보 선정(정답을 누가 다는지 포함) → S6 라운드 입력 → 더 강한 층으로 옮길 것 → 메모리 정리(만료, 해로움 표시, 중복).
8. **프롬프트·스킬·훅 변경의 통로를 정한다.** 변경 요청 → 리뷰 → 평가 자동 실행(회귀 평가 통과가 병합 조건) → 선행 채널 → 안정 채널. S6의 채택도 이 통로를 탄다.
9. **사고 절차를 적는다.** 심각도 기준, 첫 조치(끄는 스위치, 이전 태그로 고정), 알릴 사람, 원인 기록 양식(관찰 사실/원인/왜 평가가 못 잡았나/추가한 평가 사례/옮긴 층).

**검증 (교체)**

- 깨끗한 환경에서 README대로 설치·실행된다.
- 최종 확인용 평가가 미리 정한 승인 기준을 통과한다.
- 릴리스 목록의 해시와 실제 실행 중인 구성요소가 일치한다(실행 기록에 버전이 찍힌다).
- 되돌리기를 실제로 해 본다: 이전 태그로 돌린 뒤 새 세션의 기록에 이전 버전이 찍히는지.
- 끄는 스위치를 실제로 꺼 본다: 메모리 주입을 끄면 `memory_retrieve` 이벤트가 사라지는지.
- 조직 강제 항목을 개인 설정으로 꺼 보려 해도 계속 적용되는지.
- 시범 사용자 기록에서 정책 위반이 없다. 운영 지표가 대조 집단보다 나쁘지 않다.
- 운영 기록 1건을 평가 사례로 승격해 평가 명령에 포함되는지 끝까지 돌려 본다.

**완료 기준 (교체)**

- [ ] 릴리스 목록(구성요소별 버전)과 최종 확인용 평가 통과 결과·재현 조건이 `design/08-release.md`에 있다
- [ ] 인수 기준(`harness/CRITERIA.md`) 항목마다 실행해서 확인한 증거가 있고, README에 항목별 확인 방법이 있다
- [ ] 깨끗한 환경에서 문서대로 설치·실행된다
- [ ] 배포·업데이트·되돌리기 방법이 문서로 있고, 되돌리기와 끄는 스위치를 한 번 실제로 해 봤다
- [ ] 확대 단계별 넘어가는 기준과 멈추는 기준이 시범 운영 전에 적혀 있다
- [ ] 운영 지표, 신고 경로, 주간 회고, 평가셋 승격, 메모리 정리, 사고 대응의 담당자가 정해졌다
- [ ] 운영 기록 1건 이상을 평가 사례로 승격했다

**흔한 함정 (추가)**

- 프롬프트·스킬을 리뷰와 평가 없이 운영에서 바로 고치기
- 배포 전후 수치만 비교하기(같은 기간 대조군이 없다)
- 최종 확인용 데이터를 릴리스마다 다시 쓰기
- 오프라인 평가가 통과했으니 운영 기록은 안 읽기
- 자기개선이 채택한 변경을 운영에 자동으로 흘려보내기(S6의 채택은 "릴리스 후보"이지 배포가 아니다)
- 시스템 프롬프트·도구 정의를 자주 조금씩 바꾸기(바꿀 때마다 모든 사용자의 캐시가 식는다. 묶어서 낸다)
- 모델이 바뀌었는데 평가와 추론 강도 설정을 그대로 두기

---

## 3. 템플릿·스킬 수정안 (그대로 붙여 넣을 텍스트)

### 3-1. `kit/harness/templates/03-context.md` — "프롬프트 배치"와 "메모리" 절 교체, 검증 표·완료 기준 추가

"프롬프트 배치" 절 교체:

````markdown
## 프롬프트 배치
```
[고정: 도구 정의 → 시스템 지시 → 지침]  ← 여기까지 캐시 경계
[요청] [주입한 메모리·날짜·검색 결과: 요청 뒤에 메시지로 한 번 붙이고 지우지 않는다] [대화: 뒤에 붙이기만]
```
- 캐시 경계를 두는 위치 (요청마다 같은 마지막 블록):
- 요청마다 달라지는 값이 고정 구역에 들어가지 않는지 확인한 방법 (연속 두 요청의 프롬프트 비교):
- 긴 대화 압축 방식 (요약 + 원본 경로). 압축·삭제는 캐시를 깨므로 한 번에 충분히 줄인다:
````

"메모리" 절 교체:

````markdown
## 메모리 저장소
| 종류 | 위치·형식 | 누가 쓰나 | 언제 로드되나 | 누가 고칠 수 있나 | 상한 |
|---|---|---|---|---|---|
| 규칙 (항상 지킬 것) |  | 사람 / 승인된 개선안 | 세션 시작 |  | 줄 수: |
| 경험 (실패·해결·교훈) |  | 에이전트 (후보 상태로) | 검색해서 주입 |  | 건수: / 항목 길이: |
| 절차 (스킬) | S4 산출물 참조 |  | 필요할 때 |  |  |

- 경험 기록 형식:
```json
{"id": "exp-0001", "kind": "experience", "status": "candidate",
 "scope": {"repo": "", "paths": [], "task_type": ""},
 "trigger": "", "lesson": "", "outcome": "failure_fixed",
 "evidence": {"run_id": "", "event_ids": [], "commit": "", "citations": [{"path": "", "lines": ""}]},
 "source": {"origin": "agent", "trust": "unverified", "derived_from_external_input": false},
 "created_at": "", "last_verified_at": null, "expires_at": "",
 "counters": {"retrieved": 0, "cited_in_plan": 0, "helpful": 0, "harmful": 0},
 "supersedes": null, "harness_version": "r0"}
```
- 쓰는 시점 (작업 종료 / 실패 / 사람 교정 / 리뷰 지적)과 그것을 실행하는 장치 (훅·미들웨어):
- 저장하지 않는 것 (코드에서 알 수 있는 것, 지침에 있는 것, 시크릿, 평가 정답, 외부 입력 원문):
- 저장 전 검사 (필수 필드, 길이, 시크릿 패턴, 정답 흔적, 중복, 경로):
- 갱신 방식 (추가·카운터·폐기 표시만. 전체 다시 쓰기 금지):
- 규칙 저장소·스킬 직접 편집을 막는 장치:
- 만료 기한, 연장 조건, 정리 주기와 담당자:
- 변경 이력을 남기는 방법 (버전 관리):

## 코드로 끝내는 판단
- 강제 로드하는 스킬 (요청·파일 종류 → 스킬):
- 모델 호출 앞단에서 끝내는 판단:
````

"검증 기록" 표에 행 추가:

```markdown
| 메모리 왕복 확인 (쓰기 → 프로세스 종료 → 같은 경로로 읽기) |  |  |
| 실패한 작업 뒤 경험 기록 생성 (`memory_write` 이벤트) |  |  |
| 저장 거부 시험 (시크릿 / 정답 흔적 / 길이 / 경로) |  |  |
| 규칙 파일 직접 편집 차단 시험 (편집 도구 / 셸) |  |  |
| 저장소 건수·총 크기 |  |  |
```

"완료 기준" 교체:

```markdown
## 완료 기준
- [ ] 지침 계층이 적용됐고 담당자가 있다
- [ ] 탐색 격리와 프롬프트 배치가 구현됐다
- [ ] 규칙 저장소와 경험 저장소가 따로 있고, 작업 종료·실패 때 경험이 기록되며 새 세션에서 같은 경로로 읽힌다
- [ ] 저장 전 검사와 규칙 저장소 직접 편집 차단의 시험 기록이 있다
- [ ] 평가 회귀가 없고 컨텍스트·메모리 지표가 기록됐다
```

### 3-2. `kit/harness/templates/06-improve.md` — 전체 교체

````markdown
# S6. 메모리 기반 자기개선

## 조회와 활용
- 검색 방식 (구조 필터 + 키워드 / 임베딩 추가 여부와 근거):
- 조회 시점 (요청 직후 / 실패 직후):
- 주입 개수와 토큰 상한:
- 주입 전 확인 (근거가 현재 코드와 맞는가, 출처 신뢰 등급):
- 주입 위치 (시스템 프롬프트가 아닌 메시지):
- 계획의 "참조한 경험" 구역 양식:
- 남기는 이벤트: `memory_retrieve` (질의, 후보, 주입 id, 토큰) / `memory_feedback` (id, helpful·harmful·unused)
- 주입을 끄는 방법 (대조 실행용 토글):

## 개선 설정 (실행 전에 고정. 커밋: )
- 고치게 하는 대상 (하나만): 시스템 프롬프트 지정 구역 / 스킬 문서 / 메모리 규칙
- 허용 경로:
- 못 고치게 막은 것과 막는 장치: 평가셋·정답·테스트 / 채점기·임계값·반복 수 / 권한·훅·게이트 / 예산·모델 / 기록
- 평가 하네스 해시:
- 데이터: 읽기용 ID (개선안을 만드는 쪽이 본다) / 판정용 ID (보지 않는다) / 최종 확인용 (이 단계에서 열지 않는다). 나누지 않았으면 "분할 없음, 방향성 판정"
- 반복 수 R: / 주 지표: / 관문: 정책 위반 0 / 가드레일과 상한 (통과 1건당 비용, 지연, 항상 로드되는 토큰):
- 노이즈 폭 (현재 버전을 그대로 한 번 더 돌린 차이): / 최소 효과:
- 회귀 정의와 재실행 허용 규칙:
- 최대 라운드: / 비용 상한: / 승인자:

## 판정 순서 (고정)
1. 판정 불가: 하네스 해시 불일치, 오염, 평가 완료율 미달, 모델 불일치, 고칠 실패 없음, 노이즈 폭 ≥ 최소 효과
2. 기각: 정책 위반 또는 금지 경로 변경
3. 보류: 기존에 매번 통과하던 사례의 회귀, 새 실패 유형
4. 기각: 읽기용만 오르고 판정용은 그대로
5. 보류: 가드레일 상한 초과, 바뀐 항목이 로드·인용된 기록 없음
6. 채택: 판정용에서 최소 효과 이상 개선 + 사람 승인
7. 그 밖은 보류

## 개선 라운드
| 라운드 | 근거 기록 | 관찰 사실 | 원인 가설 | 개선안 (파일) | 대상 | 이전 (읽기용 / 판정용) | 이후 (읽기용 / 판정용) | 회귀 | 비용·길이 변화 | 판정 | 승인자 | 반영 버전 | 되돌리는 방법 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |

- 거부한 후보와 사유:
- 정체했을 때의 실패 분류 (지침 부족 / 채점기 / 환경 / 구조 / 흔들림):

## 검증 기록
- 세션 A에서 남긴 경험이 새 프로세스의 세션 B에서 주입되고 계획에 인용된 기록:
- 주입을 끄고 같은 작업을 돌린 결과와의 차이:
- 근거가 낡은 항목·외부 입력 유래 항목이 주입되지 않은 기록:
- 일부러 실패시킨 작업에서 나온 개선안 (생성 시점에 대상 파일 변경 없음 확인):
- 금지 경로 변경·하네스 변조가 막힌 기록:
- 탈락한 후보가 반영되지 않았다는 확인:
- 채택분이 새 세션에서 쓰인 기록:
- 되돌리기를 실제로 실행한 기록:
- 반복 실수를 더 강한 층으로 옮긴 사례 (경험 → 지침 → 스킬 → 훅 → 테스트):

## 완료 기준
- [ ] 기억 → 조회 → 계획 인용이 새 세션에서 기록으로 확인됐고, 주입을 껐을 때와의 차이가 적혀 있다
- [ ] 개선 설정이 실행 전에 고정돼 있다
- [ ] 금지 경로 변경과 하네스 변조가 막히는 시험 기록이 있다
- [ ] 개선 라운드가 한 번 이상 기록됐다 (판정과 사유 포함)
- [ ] 채택한 변경마다 전후 표, 회귀 결과, 버전, 되돌리는 방법, 새 세션에서 쓰인 기록이 있다
````

### 3-3. `kit/harness/templates/07-optimize.md` — 전체 교체

````markdown
# S7. 모델·비용·속도 최적화

> 원칙: 유지 기준을 먼저 적고, 한 번에 하나만 바꾸고, 켜고 끌 수 있게 만든다. 품질을 걸지 않는 변경부터 한다.

## 목표와 유지 기준 (변경 전에 고정)
- S0의 지연·비용 목표:
- 유지 기준: 결과 통과율이 기준선의 노이즈 폭 안 / 정책 위반 0건 / 과정 규칙 통과 / 응답과 실제 변경 일치
- 노이즈 폭 (기준선을 그대로 한 번 더 돌린 차이):
- 비교 조건 (데이터 버전, 반복 수, 동시성, 캐시 상태):

## 기준선 (요청 종류별)
| 요청 종류 | 통과율 | 통과 1건당 비용 | 전체 시간 p50 / p95 | 첫 토큰 시간 | 호출 수 | 입력 / 출력 토큰 | 캐시 읽기 비율 | 재시도 수 | 도구 실행 시간 |
|---|---|---|---|---|---|---|---|---|---|

## 기록에서 찾은 낭비
| 위치 | 증상 (캐시 미적중 / 재시도 반복 / 묶을 수 있는 연속 호출 / 안 쓰는 도구·지침 / 긴 출력 / 큰 모델이 필요 없는 단계 / 모델 밖 대기) | 근거 기록 | 최대 절감 추정 | 진행 여부와 이유 |
|---|---|---|---|---|

## 변경 기록 (아래 순서로, 하나씩)
| # | 종류 | 기존 문제 | 변경 | 끄고 켜는 방법 | 이전 | 이후 | 유지 기준 통과 | 판정 (유지 / 되돌림) |
|---|---|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |  |  |

검토 순서
1. 품질을 걸지 않는 것
   - 캐시: 고정 내용 앞·변하는 값 뒤, 대화 중 도구·모델 고정, 적중을 사용량 필드나 서빙 지표로 확인
   - 입력: 도구 수 줄이기·필요할 때 찾기 / 프롬프트 줄이기 / 스킬로 빼기 / 예전 모델용 과잉 지시 지우기
   - 루프: 재시도·중복 호출, 연속 호출 묶기, 규칙은 코드로
   - 출력: 응답 형식, 도구 호출 사이 설명 줄이기
   - 일괄 처리: 아무도 기다리지 않는 일
2. 품질을 거는 것 (평가셋의 점수-비용 표가 있어야 채택)
   - 추론 강도·예산 낮추기 (같은 모델에서 먼저)
   - 작은 모델·판단 전용 모델로 내리기 (출력을 선택지로 강제)
   - 서브에이전트로 떼어 병렬화 (독립 작업이거나 한 컨텍스트에 안 들어갈 때만. 캐시를 공유하지 못한다)
3. 직접 서빙: 접두 캐시 적중, 대기열, 컨텍스트 상한, 양자화 (`serving-plan`)

## 점수-비용 표 (품질을 거는 변경용)
| 구성 (모델 / 추론 강도 / 예산) | 통과율 | 통과 1건당 비용 | 전체 시간 p50 / p95 | 정책 위반 |
|---|---|---|---|---|

## 완료 기준
- [ ] 요청 종류별 기준선이 있다
- [ ] 유지 기준이 변경 전에 적혀 있고, 변경마다 전후 수치와 유지 기준 통과 여부가 있다
- [ ] 품질을 거는 변경은 점수-비용 표를 근거로 채택했다
- [ ] S0의 지연·비용 목표에 도달했거나 더 줄이지 않는 근거가 있다
````

### 3-4. `kit/harness/templates/08-release.md` — "최종 확인" 앞에 추가, "배포"·"담당"·"시범 운영" 교체, 완료 기준 교체

```markdown
## 릴리스 목록
| 구성요소 | 버전·해시 |
|---|---|
| 시스템 프롬프트·지침 |  |
| 스킬 |  |
| 훅·권한 설정 |  |
| 메모리 규칙 |  |
| 모델·추론 강도 |  |
| 평가셋 (개발용 / 최종 확인용) |  |
| 기반 에이전트 |  |

## 배포
- 형태 (설정 묶음 / 플러그인 / 사내 레지스트리):
- 버전 고정 방법 (태그·커밋)과 채널 (안정 / 선행):
- 업데이트 방법과 주기 (프롬프트·도구 정의 변경은 묶어서 낸다):
- 조직 차원에서 강제하는 검사·권한 (개인이 끌 수 없음)과 안내용 지침:
- 프롬프트·스킬·훅 변경 통로 (변경 요청 → 리뷰 → 회귀 평가 → 선행 → 안정):
- 되돌리기 (무엇을, 어느 버전으로, 누가, 명령):
- 끄는 스위치 (메모리 주입 / 자기개선 반영 / 선행 채널):

## 단계적 확대 (시작 전에 고정)
| 단계 | 대상 | 기간 | 넘어가는 기준 | 멈추는 기준 | 결과 |
|---|---|---|---|---|---|
| 쓰기 없는 재생 | 최근 요청 표본 |  |  |  |  |
| 시범 운영 | 사용자·저장소: / 대조 집단: |  |  | 정책 위반 1건 등 |  |
| 전체 |  |  |  |  |  |

## 운영 지표와 검토
- 전수로 모으는 지표 (정책 위반·게이트 차단, 완료율, 사람이 다시 고친 비율, 재시도·최대 턴, 통과 1건당 비용, 전체 시간, 메모리 해로움 표시):
- 표본 평가 (비율, 평가기)와 "확인 필요" 표시 기준:
- 사용자 신고 경로:
- 기록 보존 기간·접근 권한·가리기 규칙:
- 평가셋으로 승격한 기록 (능력 평가 → 회귀 평가 이동 포함):
- 최종 확인용을 새로 채운 기록:

## 담당
| 대상 | 담당자 |
|---|---|
| 평가셋 (승격·정답 검수) |  |
| 지침 |  |
| 스킬 |  |
| 검사 (훅·권한) |  |
| 메모리 (정리·만료·감사) |  |
| 릴리스 승인 |  |
| 주간 회고 |  |
| 사고 대응 |  |

## 사고 대응
- 심각도 기준과 첫 조치:
- 사고 기록 양식: 관찰 사실 / 원인 / 평가가 못 잡은 이유 / 추가한 평가 사례 / 옮긴 층

## 바깥 변화
- 모델 버전이 바뀌면: 평가 재실행, 추론 강도 다시 훑기
- 기반 에이전트를 올리면: 훅·게이트 시험 재실행
```

```markdown
## 완료 기준
- [ ] 릴리스 목록과 최종 확인용 평가 통과 결과·재현 조건이 있다
- [ ] 인수 기준 항목마다 실행해서 확인한 증거가 있고 README에 항목별 확인 방법이 있다
- [ ] 깨끗한 환경에서 문서대로 설치·실행된다
- [ ] 배포·업데이트·되돌리기 방법이 있고, 되돌리기와 끄는 스위치를 한 번 실제로 해 봤다
- [ ] 확대 단계별 넘어가는 기준과 멈추는 기준이 시범 운영 전에 적혀 있다
- [ ] 운영 지표, 신고 경로, 주간 회고, 평가셋 승격, 메모리 정리, 사고 대응 담당자가 정해졌다
- [ ] 운영 기록 1건 이상을 평가 사례로 승격했다
```

### 3-5. `kit/harness/CRITERIA.md` 3절 — "만들 것"과 "증명" 칸 교체안

```markdown
| 3-1 프로젝트 규칙·작업 경험을 Memory에 저장하고 세션 종료 후에도 유지 | 2 | S3 | 규칙 저장소와 경험 저장소를 따로 둔다. 작업 종료·실패 시 코드가 기록 단계를 실행한다 | 기록의 메모리 저장 이벤트(항목 id) + 프로세스를 끝낸 뒤 새 세션에서 같은 경로로 읽힌 그 id. 실패한 작업에서 생긴 항목 포함 |
| 3-2 새 작업에서 관련 Memory를 검색해 계획·코드 작성에 실제 활용 | 3 | S6 | 요청으로 경험을 검색해 근거를 확인한 뒤 주입하고, 계획에 참조한 항목과 반영 내용을 적는다 | 새 세션의 메모리 조회 이벤트(주입 id) + 계획의 "참조한 경험" + 교훈을 따른 코드 변경. 주입을 끄고 돌린 결과와의 차이 |
| 3-3 실행 실패·평가 결과를 바탕으로 시스템 프롬프트·Skills·작업 메모리 등의 개선안 생성 | 3 | S6 | 실패 기록의 근거를 인용한 개선안을 정해진 형식의 파일로 만든다. 바로 적용하지 않는다. 테스트·채점기·권한은 고칠 수 없다 | 일부러 실패시킨 작업에서 나온 개선안 파일(근거 이벤트, 관찰, 가설, 변경 diff, 기대 효과, 예상 회귀) + 그 시점에 대상 파일이 바뀌지 않았다는 확인 + 금지 경로 후보가 거부된 기록 |
| 3-4 개선 전후의 효과와 기존 기능의 정상 동작을 검증하고, 통과한 개선안을 다음 작업에 반영 | 2 | S1, S6 | 미리 고정한 기준으로 같은 평가셋에서 전후 비교, 회귀 검사, 통과분만 반영하고 버전을 올린다 | 실행 전에 커밋된 채택 기준 + 사례별 전후 비교표 + 회귀 결과 + 판정 + 탈락안 미반영 확인 + 반영 뒤 새 세션에서 쓰인 기록 |
```

### 3-6. `self-improve-loop` 스킬 — 고친 전문 (kit로 옮길 때의 텍스트)

````markdown
---
name: self-improve-loop
description: 실패 기록과 평가 결과에서 개선안(시스템 프롬프트 구역·스킬 문서·메모리 규칙 중 하나)을 만들고, 미리 고정한 기준으로 현재 버전과 같은 조건에서 비교해 채택·보류·기각·판정 불가를 판정한 뒤 통과분만 반영한다. S6 단계, "에이전트가 스스로 나아지게", 같은 실수가 반복될 때 사용. 평가셋 만들기는 golden-dataset, 채점은 agent-eval, 비용·속도 변경은 optimize-agent가 맡는다.
---

<principles>
- **손잡이는 하나만 연다.** 시스템 프롬프트의 지정 구역, 스킬 문서 하나, 메모리 규칙 항목 중 하나를 고르고 나머지는 전부 고정한다. 한 라운드에 가설 하나다.
- **개선안을 만드는 쪽은 판정 기준을 못 건드린다.** 평가셋·정답·테스트, 채점기·임계값·반복 수, 권한·훅·게이트, 예산·모델, 실행 기록은 개선 대상이 아니다. 이 경계는 지시문이 아니라 경로 허용 목록과 해시 검사로 막는다.
- **개선안을 만든 쪽이 읽은 사례로 판정하지 않는다.** 읽기용과 판정용을 나눈다. 사례가 적으면 나누지 않고 반복 실행으로 흔들림을 줄이되 결과를 "방향성"이라고 적는다.
- **결과를 본 뒤 규칙을 바꾸지 않는다.** 지표, 판정 순서, 반복 수, 최소 효과는 실행 전에 파일로 고정한다.
- **노이즈보다 작은 개선은 개선이 아니다.** 현재 버전을 그대로 한 번 더 돌린 차이를 먼저 잰다.
- **고치는 것은 증분이다.** 항목을 추가·수정·폐기하는 diff만 받는다. 문서를 통째로 다시 쓰게 하지 않는다.
- **모의 실행 결과는 개선율이 아니다.** "계약 검증"으로만 적는다.
</principles>

<procedure>
1. **설정 고정:** `design/06-improve.md`의 "개선 설정"과 "판정 순서"를 채우고 사용자 확인을 받은 뒤 커밋한다. 손잡이와 허용 경로, 읽기용·판정용 사례 ID(유형별 무작위. 기준선 점수로 고르지 않는다), 반복 수, 주 지표, 가드레일 상한, 노이즈 폭, 최소 효과, 최대 라운드, 비용 상한, 승인자.
2. **잴 수 있는지 확인:** 값을 하나 쓰고 같은 경로로 읽어 손잡이가 실제로 로드되는지 본다. 평가 하네스의 해시를 기록한다. 현재 버전을 한 번 더 돌려 노이즈 폭을 적는다. 노이즈 폭이 최소 효과보다 크면 반복 수나 사례를 늘리자고 제안하고 멈춘다.
3. **실패 수집:** 기록에서 실패 신호(도구 오류, 테스트 실패, 채점의 수정 필요 판정, 리뷰 수정 반복, 게이트 차단, 최대 턴 도달)를 읽기용 사례에서만 모은다. 실패마다 관찰 사실 / 원인 가설 / 다른 설명 / 근거 이벤트 id를 쓴다. 관찰 사실에는 기록의 해당 줄을 그대로 옮긴다.
4. **오염 검사:** 개선안을 만드는 쪽에 보낼 입력에 정답, 임계값, 판정용·최종 확인용 ID, 테스트 기대값이 있으면 호출하지 않고 멈춘다. 하네스 해시가 2번과 다르면 멈춘다.
5. **후보 생성:** 독립 컨텍스트에서 후보 K개(예: 3)를 `design/06-improve.md`의 개선안 형식으로 받는다. 형식 오류, 허용 경로 밖 변경, 문서 전체 교체, 기준을 낮추는 문구, 실패 사례의 고유 문자열을 붙여 넣은 변경, 길이 상한 초과, 현재안과 같은 후보는 사유와 함께 거부로 남긴다. 후보마다 기대 효과와 예상 회귀가 적혀 있어야 한다. 이 시점에 대상 파일은 바꾸지 않는다.
6. **비교:** 유료 실행 전에 규모(사례 수 × 반복 × 버전 수 ≈ 호출 수)를 한 줄로 알린다. 현재안(항상 포함)과 후보를 분리된 프로필에서 같은 평가셋·모델·예산·반복 수로 돌린다. 시도마다 초기 상태를 복원하고 새 세션에서 잰다.
7. **판정 (순서 고정):**
   1. 판정 불가: 하네스 해시 불일치, 오염, 어느 쪽이든 평가 완료율 90% 미만, 응답의 모델이 설정과 다름, 현재안에 고칠 실패가 없음.
   2. 기각: 후보에서 정책 위반이 있거나 금지 경로를 건드렸다.
   3. 보류: 현재안에서 매번 통과하던 사례가 후보에서 과반 실패하거나 새 실패 유형이 생겼다. (한 번만 실패했으면 고정해 둔 규칙대로 그 사례만 다시 돌린다.)
   4. 기각: 읽기용만 오르고 판정용은 그대로다.
   5. 보류: 가드레일 상한을 넘었거나, 바뀐 항목이 로드·인용된 기록이 없다.
   6. 채택 후보: 판정용에서 개선이 최소 효과 이상이고 노이즈 폭을 넘는다. 여러 후보가 통과하면 변경이 가장 작은 것을 고른다.
   7. 그 밖은 보류.
   변경으로 설명하기 어려울 만큼 크게 올랐으면 사례 몇 건을 직접 열어 확인한 뒤 판정한다.
8. **기록:** `improve/round-<n>.json`을 새 파일로 쓴다(같은 이름이면 거부). 현재 버전, 후보, 거부 사유, 사례별 비교표, 판정과 사유, 하네스 해시, 개선안을 만드는 쪽 입력의 해시를 넣는다.
9. **승인과 반영:** 채택 후보의 diff와 비교표를 승인자에게 보여 승인을 받는다. 승인된 것만 반영하고 버전 표시(r0→r1)를 올리고 되돌리는 명령을 적는다. 새 세션에서 같은 종류의 작업을 돌려 반영분이 쓰였다는 기록(메모리 조회, 스킬 로드, 계획 인용)을 증거로 남긴다.
10. **멈춤:** 최대 라운드나 비용 상한에 닿으면 멈춘다. 2~3 라운드 연속으로 판정용 점수가 노이즈 폭을 못 넘으면 내용을 더 고치지 않고 남은 실패를 지침 부족 / 채점기 / 환경 / 구조 / 흔들림으로 분류해 보고한다.
11. **승격:** 같은 실수가 채택 뒤에도 나오면 더 강한 층(지침 → 스킬 → 훅·권한 → 테스트·CI)으로 옮기자고 제안하고, 아래 층의 항목은 폐기 표시한다.
</procedure>

<boundaries>
- 최종 확인용 데이터는 이 스킬에서 열지 않는다. 릴리스 전에 한 번만 쓴다(S8).
- 채택은 "릴리스 후보"다. 팀에 배포하는 것은 S8의 통로를 탄다.
- 모델·추론 강도·예산을 바꾸는 제안은 여기서 다루지 않는다(S7).
</boundaries>

<implementation_notes>
- 현재안과 후보는 메모리·설정이 섞이지 않게 분리된 프로필(디렉터리, 에이전트 이름 등)로 돌린다.
- 메모리와 스킬 목록을 세션 시작 때 한 번만 읽는 구조라면 반영 효과는 새 세션에서 잰다.
- 에이전트가 규칙·스킬 파일을 직접 고칠 수 있으면 이 루프를 우회한다. 실행 전 검사로 쓰기를 막고 개선안 경로로만 받는다.
- 평가 하네스, 정답, 숨긴 테스트는 개선안을 만드는 쪽과 평가받는 에이전트 둘 다 읽거나 쓸 수 없는 곳에 둔다.
- 이전 시도의 흔적(작업 폴더, git 기록)이 다음 시도에 보이지 않게 한다.
</implementation_notes>
````

### 3-7. `optimize-agent` 스킬 — 교체할 줄

- `<rules>` 첫 줄 교체: "**유지 기준을 먼저 적는다.** 결과 통과율이 기준선의 노이즈 폭 안, 정책 위반 0건, 과정 규칙(승인 전 수정 금지, 테스트 실행 등) 통과, 최종 응답과 실제 변경의 일치. 확인은 S1의 평가셋으로 한다. 도구 호출 순서가 글자 그대로 같을 필요는 없다."
- `<rules>`에 추가: "- 단위는 통과한 작업 1건당 비용과 작업 1건의 전체 시간이다. 호출당·토큰당 수치로 판정하지 않는다." / "- 품질을 걸지 않는 변경(캐시, 입력·루프·출력 정리, 일괄 처리)을 먼저 하고, 품질을 거는 변경(추론 강도, 모델, 예산, 서브에이전트)은 점수-비용 표가 있을 때만 적용한다."
- `<checklist>` 순서 교체: 캐시 적중 확인 → 도구 수 → 프롬프트 → 스킬 → 루프(재시도·묶기) → 출력 → 일괄 처리 → 추론 강도(같은 모델) → 작은 모델·판단 모델 → 서브에이전트.
- 체크리스트 4번 문구 교체: "독립 작업을 동시에 돌리거나 한 컨텍스트에 안 들어가는 일인가. 서브에이전트는 부모의 캐시를 쓰지 못하고 각자 컨텍스트를 다시 읽으므로 비용이 오를 수 있다."
- 체크리스트 5번의 "(예: Sonnet → Haiku)" 삭제(특정 제품 전제). 
- `<reference_result>` 삭제 또는 "남이 잰 수치다. 우리 평가셋으로 다시 잰다"를 덧붙임.

---

## 4. 현재 문서의 문제점

심각도: [틀림] 근거와 어긋남 / [빠짐] 인수 기준이나 안전에 필요한데 없음 / [모호] 실행자가 판단할 수 없음 / [불일치] 문서끼리 어긋남.

### METHOD.md

1. [빠짐][불일치] **S3에 메모리 저장소의 진행·검증·완료 기준이 없다.** `METHOD.md:160`이 메모리를 한 줄로만 다루고 `:163-176`의 진행·검증·완료 기준에는 메모리 항목이 0개다. `CRITERIA.md:28`은 3-1을 S3에 배정하고 `METHOD.md:264`는 "경험 저장소와 검색·주입을 만든다"를 S6에 둔다. 저장소를 어느 단계에서 만드는지 문서끼리 다르다. → 저장소·쓰기 정책·보호는 S3, 검색·주입·개선은 S6으로 가른다(2-1, 2-2).
2. [틀림] **S7의 "동작이 바뀌면 안 된다(도구 호출 순서 포함)"** (`METHOD.md:296`, `07-optimize.md:3`, `optimize-agent/SKILL.md:7`). 같은 절이 권하는 모델 교체·도구 통합·서브에이전트 분리는 호출 순서를 바꾼다. 기준이 문자 그대로면 권하는 변경이 전부 탈락하고, 느슨하게 읽으면 기준이 없다. Anthropic 문서는 "품질을 안 깎는 것"과 "맞교환"을 가르고("never trade accuracy for cost silently"), 지연 가이드는 "No lever here is free"라고 쓴다. → 미리 적은 유지 기준으로 바꾼다(2-3의 3번).
3. [틀림] **S7의 레버 순서.** `METHOD.md:291`은 "모델을 내릴 수 있는 구간"을 두 번째로 둔다. Anthropic의 순서는 캐시 → 입력·루프·출력 정리 → 일괄 → 추론 강도 → 모델 → 다중 모델이고 "Sweep effort on your own workload before you add a second model."이다.
4. [빠짐] **S7의 측정 단위.** `METHOD.md:302`는 "건당 비용"이라고만 쓴다. 실패·재시도를 포함한 "통과 1건당 비용"이어야 한다("Compare models on cost per completed task, not per token"). p50/p95, 캐시 읽기 비율, 요청 종류별 분리도 없다. (`agent-eval/SKILL.md:22`에는 "통과 1건당 비용"이 있어 스킬과 방법론이 다르다.)
5. [모호] **S6 "무엇을 받아들이나"** (`METHOD.md:260`). "효과 측정과 회귀 검증을 통과"라고만 하고 반복 수, 노이즈, 최소 효과, 판정 순서가 없다. 사례 5건(S1 최소)에서 1건 차이는 우연과 구별되지 않는다.
6. [빠짐] **개선안을 만드는 쪽과 판정 데이터의 분리가 없다.** `METHOD.md:266`은 "같은 평가셋·같은 조건으로" 비교하라고만 한다. 개선안은 자기가 읽은 실패에 맞춰지므로 그 사례로 판정하면 과적합을 못 잡는다("the analyzer reads train, the headline comes from test").
7. [빠짐] **고칠 수 없는 것을 막는 방법.** `METHOD.md:259`는 "고칠 수 없는 곳에 둔다"고만 한다. 장치(경로 허용 목록, 하네스 해시, 읽기 불가 위치)가 없다. METR은 "하지 말라" 지시의 효과가 거의 없다고 보고했고, DGM은 탐지용 표식을 지운 사례를 보고했다. 금지 목록에 예산·모델·기록·개선 루프 코드도 빠져 있다.
8. [모호] **3-2 "실제 활용"의 판정.** `METHOD.md:258`은 "주입한 항목을 기록에 남겨 '실제로 썼다'를 보일 수 있게"라고 한다. 주입 기록은 "넣었다"이지 "썼다"가 아니다. 계획 인용, 코드 반영, 주입을 끈 대조가 필요하다("Separate 'did the mechanism engage' from 'did it help.'").
9. [빠짐] **메모리의 낡음·오염·크기.** 근거 인용과 사용 시점 확인, 만료, 출처 신뢰 등급, 직접 편집 차단의 범위(규칙 vs 경험), 상한이 없다. `METHOD.md:281`의 함정 "에이전트가 메모리 파일을 직접 고쳐"는 규칙과 경험을 구분하지 않아, 문자 그대로 따르면 3-1의 "작업 종료·실패 시 기록"(에이전트가 쓰는 것)과 충돌한다.
10. [빠짐] **메모리 갱신 방식.** 통째 다시 쓰기의 위험(ACE: 18,282 토큰 → 122 토큰, 정확도 66.7 → 57.1)에 대한 언급이 없다. `METHOD.md:166`의 "긴 대화 압축 방식"과 섞여 메모리도 요약으로 줄이면 된다고 읽힐 수 있다.
11. [모호] **S3 "프롬프트 배치"** (`METHOD.md:159`, `03-context.md:20`). 템플릿의 그림은 `[고정] … [대화] [변하는 값: … 주입한 메모리]`로, 변하는 값이 대화 뒤 꼬리에 떠 있다. 매 턴 꼬리를 갈아 끼우면 직전 요청의 캐시 항목이 다음 요청의 접두가 아니게 된다. 주입은 요청 뒤에 메시지로 한 번 붙이고 지우지 않아야 한다("A message at turn 5 invalidates nothing before turn 5."). 캐시 경계(마지막으로 같은 블록)에 대한 말도 없다.
12. [불일치] **S6과 S7의 병렬** (`METHOD.md:25-26`의 "같이 진행할 수 있는 것"). S6이 프롬프트·스킬을 바꾸면 S7의 기준선과 캐시 상태가 바뀐다. `:33`의 "S7은 동작이 굳은 뒤에 한다"와도 어긋난다. → "만들기는 병렬, 반영은 하나씩. S6 채택 뒤 S7 기준선을 다시 잰다"를 명시.
13. [빠짐] **S8의 단계적 확대·대조군·멈추는 기준·사고 절차·버전 묶음.** `METHOD.md:323-326`은 "최종 확인 1회 → 소수 시범 → 매주 읽기"뿐이다. 넘어가는 기준과 멈추는 기준, 같은 기간 대조군(SRE: 전후 비교는 위험), 릴리스 목록, 변경 통로(리뷰 + 회귀 평가), 끄는 스위치, 사고 기록, 모델 변경 시 재평가가 없다.
14. [빠짐] **최종 확인용 데이터의 보충.** `METHOD.md:324`는 "결과를 보고 다시 고치면 새 실험"이라고 하지만 새 실험에 쓸 최종 확인용을 어디서 얻는지 없다. 운영 기록에서 채운다는 절차가 필요하다.
15. [빠짐] **능력 평가와 회귀 평가의 구분.** `METHOD.md:320`의 승격은 "평가셋으로" 한 덩어리다. 새 사례는 아직 못 푸는 것(낮은 통과율)이고, 회귀 평가는 거의 100%여야 한다. 섞으면 채택 기준(회귀 0)이 깨진다.
16. [모호] **S8 "모든 요청을 평가하지 않는다"** (`METHOD.md:326`). 표본 비율, 전수로 모으는 코드 지표와 표본으로 보는 모델 채점의 구분이 없다.
17. [빠짐] **S6 채택과 S8 배포의 경계.** S6의 "통과한 개선만 반영"(`METHOD.md:267`)이 팀 전체 배포를 뜻하는지 개발 버전 반영을 뜻하는지 없다.

### CRITERIA.md

18. [모호] **3-1의 증명 "세션을 끝낸 뒤에도 남아 있는 저장소 파일"** (`CRITERIA.md:28`). 파일이 있다는 것은 에이전트가 작업 끝에 썼다는 증거가 아니다(손으로 만들어도 통과). 쓰기 이벤트와 새 세션 왕복이 있어야 한다.
19. [모호] **3-2의 증명**이 표시와 이벤트뿐이다(`CRITERIA.md:29`). 코드에 반영된 흔적이나 대조 실행이 없다.
20. [빠짐] **3-3의 "바로 적용하지 않는다"를 어떻게 보이는지** 없다(`CRITERIA.md:30`). 생성 시점에 대상 파일이 그대로라는 확인과 금지 경로 거부 기록.
21. [빠짐] **3-4에 "기준을 실행 전에 고정"과 "탈락안 미반영"이 증명 칸에 없다**(`CRITERIA.md:31`. 탈락안 미반영은 `bases/dcode.md:79`에만 있다).
22. [불일치] **"S7은 기준에 직접 없다. 필요한 만큼만"** (`CRITERIA.md:53`)인데 `scripts/stages.sh`는 S8의 선행 단계로 6과 7을 요구하고 `start-phase.sh`는 선행 단계가 안 끝나면 거절한다(`METHOD.md:359`). 기준만 따라가는 팀은 S8을 시작할 수 없다. → S7 템플릿에 "최적화하지 않는 근거"만으로 닫을 수 있음을 명시하거나 S8의 선행에서 7을 뺀다. (`07-optimize.md`의 완료 기준 첫 줄이 "더 줄이지 않는 근거"를 허용하므로 닫을 수는 있다. 그 사실이 CRITERIA 쪽에 적혀 있지 않다.)

### 템플릿

23. [빠짐] **`06-improve.md:6`의 기록 형식**에 범위, 종류, 상태, 근거 위치, 출처 신뢰, 만료, 사용 카운터가 없다. `task`/`failure`/`fix`는 성공 경험과 규칙을 담지 못한다.
24. [빠짐] **`06-improve.md:12-16` 개선 설정**에 데이터 분할, 반복 수, 노이즈 폭, 최소 효과, 가드레일, 하네스 해시, 최대 라운드, 승인자가 없다. 라운드 표(`:19`)에 대상, 승인자, 되돌리는 방법, 비용·길이 변화가 없다.
25. [불일치] **`06-improve.md:31` 완료 기준 "회귀가 없다"**와 `METHOD.md:278` "채택이든 보류든"이 다르다. 보류로 끝난 라운드는 회귀가 있었을 수 있다.
26. [빠짐] **`03-context.md:24-28` "메모리" 절** 네 줄 중 두 줄(강제 로드 스킬, 모델 호출 앞단 판단)은 메모리가 아니다. 저장소 구조·쓰기 정책·보호·만료가 없다. 검증 표(`:30-37`)에 메모리 행이 없다.
27. [빠짐] **`07-optimize.md`**에 기준선 표, 유지 기준, 점수-비용 표, 요청 종류 구분이 없다. 검토 항목(`:14-18`)에 캐시가 "(직접 서빙)" 줄에만 있어 API 사용자는 캐시를 건너뛴다.
28. [빠짐] **`08-release.md`**에 릴리스 목록, 확대 단계, 운영 지표, 사고 대응, 메모리 담당, 릴리스 승인자가 없다.

### `self-improve-loop` 스킬 (pending)

판단: **뼈대는 맞다. 그대로 kit에 넣으면 안 된다.** 맞는 것: 손잡이 하나, 판정 기준 불가침, 사전 고정, 판정 불가를 "재지 못함"으로 구분, 오염 검사, 라운드별 새 파일, 분리 프로필, 새 세션 측정. 고칠 것:

29. [불일치] **없는 것을 가리킨다.** `:3` "P8 단계"(현재는 S6), `:15` `design/08-optimization.md`(없음. `06-improve.md`), `:7` `harness/reference/eval-rsi-rules.md`(없음. `kit/harness/reference/`는 빈 폴더). `:7`의 "출처: 수업 저장소 Day05_new 노트북 06"은 결과물에 출처 표시를 넣지 않는다는 저장소 규칙에 걸린다.
30. [불일치] **손잡이 목록이 방법론과 다르다.** `:3,:8` "메모리 규칙·스킬·도구 정책 JSON" vs `METHOD.md:259` "프롬프트, 스킬 문서, 메모리 규칙" vs `CRITERIA.md:30` "시스템 프롬프트·Skills·작업 메모리". 도구 정책 JSON은 권한 설정에 가까워 "권한은 고칠 수 없다"와 충돌한다.
31. [틀림] **채택 조건이 "후보의 실패 수가 현재안보다 적다"** (`:23`). 반복·노이즈·최소 효과가 없어 1건 차이로 채택된다. 반대로 `:22`의 보류 조건은 한 번의 흔들림으로도 걸린다.
32. [틀림] **채택(8번)이 최종 확인(9번)보다 먼저다** (`:26-27`). 반영한 뒤 확인하면 확인이 실패해도 이미 반영돼 있다. 게다가 이 스킬의 원천 정리(`notes/_pending/day5-8-repo-rules.md:113,132`)는 "holdout 재확인 → 채택 또는 보류" 순서라 스킬이 원천과도 다르다. 그런데 라운드마다 최종 확인용으로 판정하면 그 데이터에 맞춰진다. → 읽기용 / 판정용 / 최종 확인용 셋으로 가르고 최종 확인용은 S8에서 한 번.
33. [빠짐] **개선안을 만드는 쪽이 어느 사례를 읽는지** 없다(`:16`). 판정에 쓰는 사례의 실패를 그대로 읽는다.
34. [빠짐] **하네스 무결성 확인, 경로 허용 목록, 문서 전체 교체 거부, 외우기 거부**가 없다. `:18`의 금지 키 검사는 선언형 JSON에만 통하고 스킬 문서 diff에는 안 통한다.
35. [빠짐] **사람 승인, 되돌리기, 멈춤 조건(최대 라운드·비용·정체), 메커니즘 확인, 가드레일(비용·길이)**이 없다. `METHOD.md:261`의 "사람이 어디서 보나"에 대응하는 단계가 없다.
36. [빠짐] **후보 K개 중 고르기의 편향.** 같은 데이터에서 여러 후보 가운데 최고를 고르면 점수가 부풀려진다. 판정용에서 고르고, 동점이면 가장 작은 변경을 고른다는 규칙이 필요하다.
37. [빠짐] **다른 스킬과의 경계.** `description`에 `agent-eval`, `golden-dataset`, `optimize-agent`와 겹치는 영역에서 무엇을 맡지 않는지가 없다(다른 kit 스킬은 적혀 있다).
38. [모호] **이름과 범위.** 메모리 저장·조회(3-1, 3-2)는 다루지 않고 개선 루프(3-3, 3-4)만 다룬다. 그대로 두되 설명문에 명시하면 된다.

고친 전문은 3-6에 있다.

### `optimize-agent` 스킬

39. [틀림] `:7` "도구 호출 순서 … 그대로여야 한다" (위 2번과 같음).
40. [불일치] `:21`의 "(예: Sonnet → Haiku)"와 `:27`의 참고 수치("4초 → 1.42초")는 특정 제품·남의 측정값이다. `METHOD.md:308`의 함정 "남이 잰 수치를 그대로 믿기"와 어긋난다.
41. [빠짐] 캐시 적중 확인이 2번 항목의 괄호 안에만 있다. 가장 큰 레버가 가장 약하게 적혀 있다.
42. [모호] `:8` "가능하면 새 세션에서 상위 모델로 작업한다"는 최적화 작업자(코딩 도구)에 대한 말인지 대상 에이전트에 대한 말인지 불분명하다.

---

## 5. 확인 못 한 것

- **인용의 원문 대조.** `[추출]` 표시 인용은 WebFetch의 요약 모델이 돌려준 문장이다. 직접 원문을 읽은 것은 Memory tool, Claude Code 메모리, Managed Agents 메모리, Batch, Effort, Reducing latency, 플러그인 문서 두 개, 번들 `claude-api` 스킬 파일들이다. 나머지(arXiv 초록, Anthropic 블로그, vLLM, SRE, LangChain, GitHub, METR, OpenAI)는 반영 전에 한 번 대조할 것.
- **DSPy 문서.** `dspy.ai/learn/optimization/*`가 "Continue to the documentation" 리다이렉트만 돌려줘 본문을 못 읽었다. "30건으로도 가치, 300건 권장", "프롬프트 최적화는 학습 20%·검증 80%"는 검색 요약에서만 봤다. 표에 넣지 않았다.
- **GEPA 수치.** 내 기억은 "GRPO 대비 평균 10%"였으나 현재 초록은 "by 6% on average and by up to 20%"로 읽혔다. 초록 판본에 따라 다를 수 있다. 수치는 문서에 쓰지 않는 편이 안전하다.
- **DGM의 "objective hacking" 부록.** arXiv HTML에서 해당 부록(환각 탐지 표식 제거 사례)을 찾지 못했다. 표의 인용은 저자 소속 Sakana AI의 글에서 가져왔다. 논문 본문의 정확한 절 제목과 "Goodhart" 언급 여부는 미확인. 실행 비용 "about USD 22,000"은 부록 E.1에서 추출됐다(본문에 쓰지 않았다).
- **Copilot 메모리 만료 기간.** 검색 요약과 여러 2차 자료는 "28일"이라고 하고, 지금 읽은 GitHub Docs는 "The default expiry period is 90 days."(7~180일 조정)이라고 한다. 정책이 바뀐 것으로 보인다. 설계 글 자체에는 만료 기간이 없다. 보강안의 "예: 90일"은 예시다.
- **ImpossibleBench의 모델별 수치.** HTML 앞 10만 자에서 추출한 값이다(뒤 1.3만 자 미열람). 초록에는 수치가 없다.
- **ReasoningBank의 효과 수치, Mem0의 수치.** ReasoningBank는 초록에 수치가 없었고, Mem0의 91%·90%는 벤더 자체 측정이다. 근거로 쓰지 않는 편이 낫다.
- **OWASP Agentic Top 10(2026)의 메모리 오염 항목.** 내려받기 안내 페이지만 열려 본문을 못 읽었다. LLM04:2025로 대신했다.
- **Letta의 기본 글자 수 상한, 코어/보관 메모리 구분.** 해당 페이지에 없었다.
- **LangSmith의 "운영 기록 → 데이터셋·주석 대기열".** 읽은 페이지에 없었다. Langfuse 문서로 대신했다. Langfuse 문서에도 CI 연동은 없었다.
- **token-efficient tool use 문서.** 해당 URL이 마이그레이션 가이드 목록으로 리다이렉트된다. 별도 레버로 남아 있지 않은 것으로 보이나 확인하지 못했다. 보강안에 넣지 않았다.
- **확장 사고(extended thinking) 문서.** 따로 읽지 않았다. Effort 문서와 번들 스킬 요약으로 대신했다(최신 모델은 고정 사고 예산 대신 effort로 조절).
- **Prompt caching 문서 뒤쪽 6.5만 자, 비용 최적화 문서 뒤쪽 11만 자, Context editing 뒤쪽 0.8만 자, Monitoring 뒤쪽 7.5만 자**는 읽지 못했다. 캐시와 도구 결과·서브에이전트의 상호작용 세부가 거기 있을 수 있다.
- **vLLM 접두 캐시의 기본 활성 여부.** 읽은 페이지는 켜는 방법만 말한다. 버전에 따라 기본값이 다를 수 있으니 서빙 설정에서 직접 확인할 것.
- **Anthropic 문서의 모델명·가격·벤치마크 수치.** 2026-11 시점 값이고 문서도 "directional"이라고 적는다. 방법론 본문에는 수치 대신 원칙만 넣고 수치는 `notes/`에 둘 것.
- **번들 `claude-api` 스킬 파일.** Anthropic이 쓴 것이지만 공개 URL이 없고 Claude Code 버전에 따라 바뀐다(읽은 경로: `/tmp/claude-0/bundled-skills/2.1.322/d8fd08abb5ef1764a9b8489f10567932/claude-api/shared/`). 인용 근거로 남길 때는 버전을 같이 적을 것. 대응하는 공개 글은 "Optimizing for cost and intelligence"와 쿡북 두 편(`platform.claude.com/cookbook/cost-optimization-cost-optimization`, `…/latency-optimization-latency-optimization`)인데 쿡북은 열어 보지 않았다.
- **코딩 에이전트의 메모리 검색에 대한 학술 비교(키워드 vs 임베딩).** 직접 비교한 1차 자료를 찾지 못했다. "키워드부터"라는 권고는 Anthropic의 검색 글 두 편과 Copilot의 "최근 기억을 프롬프트에 넣는다" 설계에서 끌어온 판단이다.
- **dcode(기반)에서의 구현 가능성.** 제안한 저장 전 검사·직접 편집 차단·주입 토글을 dcode의 훅·미들웨어로 실제 구현할 수 있는지는 코드를 열어 확인하지 않았다(`bases/dcode.md`의 설명만 읽었다).
- **제안값.** 주입 3~5건, 반복 3회, 완료율 90%, 만료 90일, 표본 10%, 최대 라운드 등은 출처의 예시이거나 내 기본값이다. 팀의 평가셋 크기와 노이즈 폭을 재고 정해야 한다.
