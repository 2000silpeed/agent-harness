# 참고 자료

`harness/METHOD.md`와 `harness/reference/*.md`가 근거로 삼은 1차 자료를 단계별로 모은 목록이다.
확인 칸의 "직접"은 원문을 직접 읽은 자료이고, "요약 경유"는 요약 도구가 뽑아 준 내용만 본 자료라서 인용하기 전에 원문 대조가 필요하다.
두 문서에서 "(제안값)"이라고 적은 값은 자료에서 온 것이 아니라 우리가 정한 출발값이다.

## S0·S2 구조와 흐름

| 자료 | 이 문서에서 가져온 것 | 확인 |
|---|---|---|
| [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 가장 단순한 구조에서 시작하고, 코드가 경로를 정하는 흐름과 모델이 정하는 흐름을 구분하며, 반복 상한을 종료 조건으로 둔다. | 직접 |
| [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | 에이전트를 여럿으로 나누면 토큰이 크게 늘므로 병렬 탐색에만 쓰고, 위임할 때는 목표·출력 형식·도구 안내·작업 경계를 적는다. | 직접 |
| [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 컨텍스트 창을 넘는 작업은 기능 목록·진행 파일·커밋으로 인계하고 한 번에 기능 하나만 진행한다. | 직접 |
| [Anthropic — Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) | 하네스 구성요소는 모델이 혼자 못 한다는 가정이므로 하나씩 빼 보며 확인하고, 만드는 쪽과 판정하는 쪽을 분리한다. | 직접 |
| [Anthropic — Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) | 요청 처리 흐름을 맥락 수집, 행동, 검증의 반복으로 잡고 검증은 규칙 기반 검사를 먼저 둔다. | 직접 |
| [Anthropic — Raising the bar on SWE-bench Verified](https://www.anthropic.com/engineering/swe-bench-sonnet) | 최소 뼈대를 프롬프트·셸 도구·편집 도구로 잡고, 편집은 한 곳만 일치할 때 적용되는 문자열 치환으로 한다. | 직접 |
| [Claude Code Docs — Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) | 지침은 부탁이고 훅·거부 규칙은 강제라는 구분을 쓰고, 완료 주장에는 실행한 명령과 출력을 증거로 요구한다. | 직접 |
| [Anthropic — Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) | 세션 기록을 하네스 밖에 두어 중단 지점에서 재개하고, 자격 증명은 실행 환경 밖에 둔다. | 요약 경유 |
| [Anthropic — Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) | 병렬 쓰기는 서로 독립된 실패 테스트가 많을 때만 쓰고, 테스트 출력은 로그 파일로 보내 컨텍스트를 아낀다. | 요약 경유 |
| [Anthropic Docs — Choosing the right model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model) | 모델 교체는 자체 평가셋으로 판단하고, 모델을 바꾸기 전에 노력 수준부터 조절한다. | 직접 |
| [Anthropic Docs — Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) | 첫 세션과 이후 세션의 프롬프트를 다르게 두고, 상태는 구조화된 파일과 git으로 추적한다. | 직접 |
| [Claude Code Docs — Subagents](https://code.claude.com/docs/en/sub-agents) | 서브에이전트는 탐색과 컨텍스트 격리에 쓰고, 도구 제한과 턴 상한은 프롬프트가 아니라 하네스가 강제한다. | 직접 |
| [Claude Code Docs — Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) | 기반을 고를 때 기반이 제공하는 것(도구 루프, 훅, 권한, 세션)과 직접 짜야 하는 것을 구분한다. | 직접 |
| [OpenAI — A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) | 단일 에이전트를 먼저 끝까지 키우고, 종료 조건(최종 출력, 도구 호출 없는 응답, 오류, 최대 턴)을 명시한다. | 직접 |
| [OpenAI — Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide) | 쉬운 작업은 계획을 생략하고, 진전 없는 재읽기·재편집에 상한을 둔다. | 요약 경유 |
| [Cognition — Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) | 기본은 단일 흐름으로 두고, 서브에이전트는 잘 정의된 질문에 답하는 용도로만 쓴다. | 직접 |
| [Cognition — Multi-Agents: What's Actually Working](https://cognition.com/blog/multi-agents-working) | 읽기 전용 서브에이전트와 컨텍스트를 공유하지 않는 리뷰 에이전트는 허용하되 쓰기는 한 흐름에서만 한다. | 요약 경유 |

## S1 평가

| 자료 | 이 문서에서 가져온 것 | 확인 |
|---|---|---|
| [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 과제·시도·채점기·기록 용어를 쓰고, 실제 실패에서 뽑은 소수 과제로 시작하며, 시도마다 깨끗한 환경에서 경로가 아닌 산출물을 채점한다. | 요약 경유 |
| [Anthropic — A statistical approach to model evals](https://www.anthropic.com/research/statistical-approach-to-model-evals) | 평균 옆에 표준오차를 적고, 기준과 후보는 과제별 짝 차이로 비교한다. | 요약 경유 |
| [Evan Miller — Adding Error Bars to Evals (arXiv 2411.00640)](https://arxiv.org/abs/2411.00640) | 점수에 95% 구간을 붙이고, 같은 과제를 반복 실행해 분산을 줄인다. | 요약 경유 |
| [Anthropic — Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise) | 자원과 시간 제한을 평가 조건으로 기록하고, 작은 점수 차이는 판정 근거로 쓰지 않는다. | 요약 경유 |
| [Anthropic Docs — Define success criteria](https://platform.claude.com/docs/en/test-and-evaluate/define-success) | 성공 기준은 구체적이고 측정 가능한 수치나 척도로 적는다. | 요약 경유 |
| [Anthropic Docs — Develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) | 채점 방법은 코드 채점을 먼저 고르고, 모델 채점은 신뢰성을 시험한 뒤에 늘린다. | 직접 |
| [SWE-bench 논문 (arXiv 2310.06770)](https://arxiv.org/abs/2310.06770) | 과제를 실제 이슈와 그 이슈를 닫은 변경으로 만들고, 실패에서 통과로 바뀌는 테스트가 하나 이상 있어야 한다. | 요약 경유 |
| [Hugging Face — SWE-bench Verified 데이터셋 카드](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified) | 과제 스키마의 필드(기준 커밋, 요청문, 정답 패치, 고쳐야 할 테스트, 깨뜨리면 안 되는 테스트)를 정한다. | 요약 경유 |
| [SWE-bench — 저장소](https://github.com/SWE-bench/SWE-bench) · [평가 가이드](https://www.swebench.com/SWE-bench/guides/evaluation/) | 채점은 컨테이너에서 하고, 정답 패치로 환경과 채점기를 먼저 검증한다. | 요약 경유 |
| [OpenAI — Introducing SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) · [미러 사본](https://bittide.aicompass.dev/article/97de7998-f4a6-4479-86a7-6ae83bb4d791?locale=en) | 과제마다 요청문이 명확한지, 테스트가 유효한 해답을 떨어뜨리지 않는지 사람이 검수한다. | 요약 경유 |
| [OpenAI — Why we no longer evaluate SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) | 한 번 검수한 평가셋도 주기적으로 다시 감사한다. | 요약 경유 |
| [SWE-bench — 이슈 #465 (git 기록 누출)](https://github.com/SWE-bench/SWE-bench/issues/465) | 평가 환경에서 원격·브랜치·미래 커밋을 지워 정답이 git 기록으로 새지 않게 한다. | 요약 경유 |
| [SWE-Bench+ (arXiv 2410.06992)](https://arxiv.org/abs/2410.06992) | 요청문에 답이 들어 있거나 테스트가 약한 과제를 과제 검증에서 걸러낸다. | 요약 경유 |
| [SWE-bench-Live (arXiv 2505.23419)](https://arxiv.org/abs/2505.23419) | 정답 패치 전후의 테스트를 여러 번 돌려 결과가 일관된 과제만 남긴다. | 요약 경유 |
| [METR — Many SWE-bench-Passing PRs Would Not Be Merged into Main](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/) | 테스트 통과만으로 완료로 보지 않고, 코드 품질과 무관한 코드의 손상을 따로 본다. | 요약 경유 |
| [Terminal-Bench 2.0 논문 (arXiv 2601.11868)](https://arxiv.org/abs/2601.11868) | 과제를 지시문·환경·테스트·예시 해답·시간 제한으로 구성하고, 환경의 최종 상태를 채점한다. | 요약 경유 |
| [Harbor — Tasks overview](https://docs.harborframework.com/tasks/overview) | 과제 디렉터리를 지시문·환경·해답·테스트로 나누는 배치를 참고한다. | 요약 경유 |
| [τ-bench 논문 (arXiv 2406.12045)](https://arxiv.org/abs/2406.12045) | 과제당 여러 번 실행하고, 모든 시도가 성공하는 비율을 일관성 지표로 쓴다. | 요약 경유 |
| [METR — Task Standard](https://github.com/METR/task-standard) | 에이전트를 낮은 권한으로 실행해 채점 자료에 닿지 못하게 하고, 네트워크 허용 범위를 과제에 적는다. | 요약 경유 |
| [METR — Measuring AI Ability to Complete Long Tasks](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) | 과제 난이도를 숙련자가 걸리는 시간으로 적는다. | 요약 경유 |
| [Establishing Best Practices for Building Rigorous Agentic Benchmarks (arXiv 2507.02825)](https://arxiv.org/abs/2507.02825) | 빈 응답이나 불충분한 테스트가 성공으로 세어지지 않는지 채점기를 반례로 확인한다. | 요약 경유 |
| [AI Agents That Matter (arXiv 2407.01502)](https://arxiv.org/abs/2407.01502) | 정확도와 비용을 함께 보고, 최종 확인용 평가셋을 따로 떼어 둔다. | 요약 경유 |
| [Hamel Husain — Creating a LLM-as-a-Judge That Drives Business Results](https://hamel.dev/blog/posts/llm-judge/) | 모델 채점은 통과/실패와 근거로 받고, 사람 라벨과 맞춰 본 뒤 참양성률과 참음성률을 따로 본다. | 요약 경유 |
| [Hamel Husain — Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) | 비용이 싼 검사일수록 자주 돌리고, 목표 통과율은 제품 결정으로 정한다. | 요약 경유 |
| [Hamel Husain — A Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/) | 실제 기록에서 실패 유형을 뽑아 세고, 합성 데이터는 입력만 만든다. | 요약 경유 |
| [Hamel Husain·Shreya Shankar — AI Evals FAQ](https://hamel.dev/blog/posts/evals-faq/) | 기록을 읽어 첫 상류 실패에 집중하고, 여러 검사는 전부 통과한 비율로 합친다. | 요약 경유 |
| [Shankar 외 — Who Validates the Validators? (arXiv 2404.12272)](https://arxiv.org/abs/2404.12272) | 모델 채점기는 사람 검증을 거치고, 채점해 보면 기준이 바뀐다는 점을 전제로 둔다. | 요약 경유 |
| [Eugene Yan — Evaluating the Effectiveness of LLM-Evaluators](https://eugeneyan.com/writing/llm-evaluators/) | 판정기는 이진 출력으로 받고, 정밀도·재현율 같은 분류 지표로 평가한다. | 요약 경유 |
| [Zheng 외 — Judging LLM-as-a-Judge (arXiv 2306.05685)](https://arxiv.org/abs/2306.05685) | 모델 채점기의 위치·장황함·자기 선호 편향을 채점기 검증 항목에 넣는다. | 요약 경유 |
| [Stureborg 외 — LLMs are Inconsistent and Biased Evaluators (arXiv 2405.01724)](https://arxiv.org/abs/2405.01724) | 여러 속성을 한 번에 매기지 않고 차원마다 따로 채점한다. | 요약 경유 |
| [Thakur 외 — Judging the Judges (arXiv 2406.12624)](https://arxiv.org/abs/2406.12624) | 일치율만 보지 않고 판정기가 관대한 쪽으로 기우는지 확인한다. | 요약 경유 |
| [UK AISI — Inspect AI](https://inspect.aisi.org.uk/) · [Sandboxing](https://inspect.aisi.org.uk/sandboxing.html) · [Scorers](https://inspect.aisi.org.uk/scorers.html) | 표본마다 격리 환경과 실행 제한을 두고, 채점을 실행과 분리해 나중에 다시 채점할 수 있게 한다. | 요약 경유 |
| [LangChain — LangSmith 평가 개념](https://docs.langchain.com/langsmith/evaluation-concepts) · [반복 실행](https://docs.langchain.com/langsmith/repetition) | 참조 출력은 채점기만 보게 하고, 평가셋을 분할과 버전으로 관리한다. | 요약 경유 |
| [Langfuse — Evaluation overview](https://langfuse.com/docs/evaluation/overview) | 운영에서 본 사례를 평가셋으로 옮기고, 변경 전후를 나란히 비교한다. | 요약 경유 |

## S3 컨텍스트·메모리

| 자료 | 이 문서에서 가져온 것 | 확인 |
|---|---|---|
| [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 컨텍스트를 한정 자원으로 보고, 식별자만 들고 있다가 필요할 때 읽으며, 긴 작업은 압축·메모·서브에이전트로 나눈다. | 직접 |
| [Anthropic Docs — Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | 프롬프트를 도구, 시스템, 메시지 순으로 배치하고 요청마다 바뀌는 값은 뒤에 둔다. | 직접 |
| [Anthropic Docs — Context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) | 오래된 도구 결과를 비울 때는 캐시가 깨지는 손해보다 이득이 크도록 한 번에 충분히 비운다. | 직접 |
| [Anthropic Docs — Compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) | 대화가 길어지면 품질이 떨어지므로 압축을 품질 유지 수단으로 둔다. | 직접 |
| [Anthropic Docs — Memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) | 메모리를 파일 디렉터리로 두고, 경로 검증·크기 상한·만료·민감정보 필터를 구현 쪽 책임으로 정한다. | 직접 |
| [Claude Code Docs — Memory](https://code.claude.com/docs/en/memory) | 지침 파일은 짧게 유지하고, 사람이 쓰는 지침과 에이전트가 쓰는 메모리를 나누며, 같은 실수가 두 번 나오면 지침으로 올린다. | 직접 |
| [Claude Code Docs — Context window](https://code.claude.com/docs/en/context-window) | 압축 뒤에 무엇이 남는지 확인하고, 중요한 지시는 문서 앞쪽에 둔다. | 직접 |
| [OpenAI — Codex: Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md) | 지침 파일의 병합 순서와 크기 상한을 확인하고, 로드된 지침을 요약시켜 검증한다. | 직접 |
| [AGENTS.md — 규격 사이트](https://agents.md/) | 지침 파일에 빌드·테스트 명령, 코드 스타일, 보안 구역을 두고, 편집 파일에 가까운 지침이 우선하게 한다. | 직접 |
| [Aider — Repository map](https://aider.chat/docs/repomap.html) | 저장소 지도는 토큰 예산 안에서 관련 부분만 보낸다. | 직접 |
| [Manus — Context Engineering for AI Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) | 프롬프트 접두를 고정하고 추가만 하며, 실패한 행동을 컨텍스트에서 지우지 않는다. | 직접 |
| [Anthropic — 컨텍스트 관리 발표 글](https://claude.com/blog/context-management) | 메모리와 컨텍스트 비우기를 함께 쓰는 구성을 긴 작업의 기본으로 삼는다. | 요약 경유 |
| [Anthropic Docs — Managed Agents memory](https://platform.claude.com/docs/en/managed-agents/memory) | 신뢰할 수 없는 입력을 다루는 에이전트의 참조용 메모리는 읽기 전용으로 두고, 변경마다 버전을 남긴다. | 직접 |
| [GitHub Blog — Building an agentic memory system for GitHub Copilot](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/) | 기억마다 근거가 되는 코드 위치를 붙이고, 쓸 때 현재 코드와 대조해 낡은 기억을 걸러낸다. | 요약 경유 |
| [GitHub Docs — Copilot Memory](https://docs.github.com/en/copilot/concepts/agents/copilot-memory) | 기억에 기본 만료를 두고, 검증되어 쓰이면 연장한다. | 요약 경유 |
| [LangChain — LangGraph memory](https://docs.langchain.com/oss/python/langgraph/memory) | 기억을 사실·경험·절차로 나누고, 작업 중에 쓸지 백그라운드에서 쓸지를 정한다. | 요약 경유 |
| [LangChain — LangMem conceptual guide](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/) | 너무 많이 뽑으면 정밀도가, 너무 적게 뽑으면 재현율이 떨어진다는 기준으로 저장 조건을 정한다. | 요약 경유 |
| [Sumers 외 — CoALA (arXiv 2309.02427)](https://arxiv.org/abs/2309.02427) | 기억 종류와 행동 공간을 나눠 설계하는 용어의 틀로 쓴다. | 요약 경유 |
| [Packer 외 — MemGPT (arXiv 2310.08560)](https://arxiv.org/abs/2310.08560) · [Letta — Memory blocks](https://docs.letta.com/guides/agents/memory-blocks) | 항상 보이는 작은 블록과 검색해서 꺼내는 저장소를 계층으로 나눈다. | 요약 경유 |
| [Chhikara 외 — Mem0 (arXiv 2504.19413)](https://arxiv.org/abs/2504.19413) | 대화 전체를 넣지 않고 추출·통합·검색으로 줄이는 방향만 참고한다. | 요약 경유 |
| [Xu 외 — A-MEM (arXiv 2502.12110)](https://arxiv.org/abs/2502.12110) | 기억 항목에 키워드·태그·맥락 설명을 붙인다. | 요약 경유 |
| [Ouyang 외 — ReasoningBank (arXiv 2509.25140)](https://arxiv.org/abs/2509.25140) | 성공뿐 아니라 실패 경험에서도 일반화된 전략을 뽑아 저장한다. | 요약 경유 |
| [Anthropic — Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) | 식별자와 오류 코드는 정확 일치 검색을 함께 쓰고, 작은 지식은 검색 없이 통째로 넣는다. | 요약 경유 |
| [Dong 외 — MINJA (arXiv 2503.03704)](https://arxiv.org/abs/2503.03704) | 평범한 질의만으로도 메모리가 오염될 수 있으므로 저장 전 검사를 둔다. | 요약 경유 |
| [OWASP — LLM04:2025 Data and Model Poisoning](https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/) | 저장 데이터의 출처를 추적하고 버전을 관리한다. | 요약 경유 |

## S4 도구·스킬

| 자료 | 이 문서에서 가져온 것 | 확인 |
|---|---|---|
| [Anthropic — Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | 도구는 API를 그대로 감싸지 않고 작업 단위로 묶으며, 반환은 필요한 것만, 오류 메시지는 고치는 방법을 담는다. | 직접 |
| [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) | 도구가 많으면 코드로 호출하게 해 필요한 정의만 읽고, 결과는 실행 환경에서 걸러낸다. | 직접 |
| [Anthropic — Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | 스킬을 메타데이터, 본문, 딸린 파일의 3단으로 나눠 필요할 때만 읽히고, 결정적인 일은 스크립트로 둔다. | 직접 |
| [Anthropic — Introducing advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) | 도구 정의가 컨텍스트를 크게 차지하면 지연 로드를 쓰고, 복잡한 입력에는 예시를 붙인다. | 직접 |
| [Anthropic Docs — Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools) | 도구 설명에 무엇을 하는지, 언제 쓰는지, 인자의 뜻과 제약을 여러 문장으로 적는다. | 직접 |
| [Anthropic Docs — Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) | 자주 쓰는 도구만 상시 로드하고 나머지는 찾아 쓰게 한다. | 직접 |
| [Anthropic Docs — Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | 스킬은 평가를 먼저 만들고, 본문은 짧게, 참조는 한 단계 깊이로 둔다. | 직접 |
| [Claude Code Docs — Extend Claude Code](https://code.claude.com/docs/en/features-overview) | 규칙을 지침·스킬·서브에이전트·훅 가운데 어디에 둘지를 도입 계기와 컨텍스트 비용으로 정한다. | 직접 |
| [Claude Code Docs — Skills](https://code.claude.com/docs/en/skills) | 스킬 설명은 목록에서 잘리므로 핵심 용도를 앞에 쓰고, 부작용이 있는 절차는 모델이 스스로 호출하지 못하게 한다. | 직접 |
| [OpenAI — apply_patch tool guide](https://developers.openai.com/api/docs/guides/tools-apply-patch) | 패치 적용은 하네스가 맡고, 경로를 검증하며 실패를 명확한 메시지로 돌려준다. | 요약 경유 |
| [Agent Skills — Specification](https://agentskills.io/specification) | 스킬의 이름·설명 길이 상한, 본문 5,000 토큰 미만 권장, 폴더 구성을 따른다. | 직접 |
| [Model Context Protocol — Specification: Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) | 도구 실행 오류는 프로토콜 오류와 구분해 결과로 돌려주고, 도구 호출을 거부할 수 있는 사람을 둔다. | 직접 |
| [SWE-agent: Agent-Computer Interfaces (arXiv 2405.15793)](https://arxiv.org/abs/2405.15793) | 도구는 단순한 행동, 간결하되 정보가 있는 피드백, 가드레일로 설계하고, 검색 결과가 너무 많으면 좁히라고 안내한다. | 직접 |
| [Aider — Unified diffs](https://aider.chat/docs/unified-diffs.html) · [Edit formats](https://aider.chat/docs/more/edit-formats.html) | 편집 형식은 모델에 익숙하고 줄 번호가 없는 것을 고르고, 적용은 관대하게 한다. | 직접 |

## S5 실행 제어·보안

| 자료 | 이 문서에서 가져온 것 | 확인 |
|---|---|---|
| [Claude Code Docs — Permission modes](https://code.claude.com/docs/en/permission-modes) | 계획 단계에서는 읽기만 허용하고 승인 뒤에 편집을 열며, 보호 경로는 허용 규칙으로 미리 풀리지 않게 한다. | 요약 경유 |
| [OpenAI — Codex 승인·샌드박스 문서](https://learn.chatgpt.com/docs/agent-approvals-security) | 승인 정책과 샌드박스를 따로 정하고, 네트워크는 기본으로 끈다. | 요약 경유 |
| [Cursor — Plan Mode](https://cursor.com/docs/agent/plan-mode) | 결과가 어긋나면 덧대어 고치지 않고, 되돌린 뒤 계획을 고쳐 다시 실행한다. | 요약 경유 |
| [Aider — architect/editor 글](https://aider.chat/2024/09/26/architect.html) | 무엇을 할지 정하는 역할과 편집하는 역할을 나누는 근거로 쓴다. | 요약 경유 |
| [GitHub Docs — Copilot cloud agent 위험과 완화](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations) | 요청자가 승인자를 겸하지 못하게 하고, 에이전트는 전용 브랜치에만 푸시하며 머지 권한을 주지 않는다. | 요약 경유 |
| [GitHub — Spec Kit](https://github.com/github/spec-kit) | 단계마다 만든 문서를 다음 단계의 입력으로 삼는 계획 흐름을 참고한다. | 요약 경유 |
| [Kiro — Specs](https://kiro.dev/docs/specs/) | 요구사항·설계·작업 목록 사이에 검토를 두고, 작은 작업에는 빠른 경로를 따로 둔다. | 요약 경유 |
| [Beurer-Kellner 외 — Design Patterns for Securing LLM Agents against Prompt Injections (arXiv 2506.08837)](https://arxiv.org/abs/2506.08837) · [Simon Willison 해설](https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/) | 계획을 먼저 고정해 도구 결과가 행동 종류를 바꾸지 못하게 하되, 인자가 오염되는 것은 따로 막는다. | 요약 경유 |
| [Anthropic — Claude Code auto mode 설계 글](https://www.anthropic.com/engineering/claude-code-auto-mode) | 독립 판정기에는 행위자의 설명을 보여 주지 않고, 판정기도 틀린다는 전제로 사람 검토를 남긴다. | 요약 경유 |
| [Claude Code Docs — Permissions](https://code.claude.com/docs/en/permissions) | 규칙은 거부, 확인, 허용 순으로 평가하고, 명령 패턴 거부는 우회되므로 샌드박스와 함께 쓴다. | 직접 |
| [Claude Code Docs — Hooks](https://code.claude.com/docs/en/hooks) | 훅은 실패하면 통과시키는 것이 기본이므로, 차단용 훅은 실패 시 차단으로 설정하고 시험한다. | 직접 |
| [Claude Code Docs — Sandboxing](https://code.claude.com/docs/en/sandboxing) | 샌드박스는 셸 명령만 가두므로 파일 격리와 네트워크 격리를 함께 두고 허용 도메인을 좁힌다. | 직접 |
| [Anthropic — Claude Code sandboxing 엔지니어링 글](https://www.anthropic.com/engineering/claude-code-sandboxing) | 승인 요청이 많으면 사람이 읽지 않으므로 샌드박스로 요청 수를 줄이고, 자격 증명은 샌드박스 밖에 둔다. | 요약 경유 |
| [Claude Code Docs — Security](https://code.claude.com/docs/en/security) | 작업 폴더 경계는 승인 요청일 뿐이므로 승인한 명령이 쓸 수 있는 범위를 따로 제한한다. | 직접 |
| [Simon Willison — The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) | 비공개 데이터 접근, 신뢰할 수 없는 내용, 외부 통신이 한 에이전트에 모이지 않게 한다. | 요약 경유 |
| [Meta — Agents Rule of Two](https://ai.meta.com/blog/practical-ai-agent-security/) | 신뢰 못 할 입력, 민감 데이터 접근, 상태 변경·외부 통신 가운데 둘까지만 허용하고, 셋이 필요하면 사람 승인을 받는다. | 요약 경유 |
| [OWASP — Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) | 위협 점검표의 항목 이름으로 쓴다. | 요약 경유 |
| [OWASP — Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) · [Giskard 항목 목록](https://www.giskard.ai/knowledge/owasp-top-10-for-agentic-application-2026) | 에이전트 위협 점검표의 항목 이름으로 쓴다. | 요약 경유 |
| [Model Context Protocol — Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices) | MCP 서버는 설치 전에 실행될 명령 전체를 확인하고, 최소 권한의 격리 환경에서 띄운다. | 직접 |
| [Pillar Security — Rules File Backdoor](https://pillar.security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents) | 규칙·지침 파일도 코드처럼 리뷰하고 보이지 않는 문자를 검사한다. | 요약 경유 |
| [Invariant Labs — GitHub MCP toxic agent flow](https://invariantlabs.ai/blog/mcp-github-vulnerability) | 한 세션이 닿는 저장소를 하나로 두고 토큰 범위를 좁힌다. | 요약 경유 |
| [Zhong·Raghunathan·Carlini — ImpossibleBench (arXiv 2510.20270)](https://arxiv.org/abs/2510.20270) | 테스트를 고쳐 통과시키는 편법을 막기 위해 테스트 파일 수정을 위험 표시로 다룬다. | 요약 경유 |
| [Spracklen 외 — We Have a Package for You! (USENIX Security 2025)](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen) | 모델이 지어낸 패키지 이름이 설치되지 않도록 의존성 추가를 사람 승인 대상으로 둔다. | 요약 경유 |
| [Claude Code Docs — Sandboxing](https://code.claude.com/docs/en/sandboxing) | 격리의 기본 읽기 범위에 자격증명 파일이 들어 있으므로 따로 막고, 자격증명은 자리표시 값만 보여 준 뒤 허용한 대상으로 나가는 요청에서 바꿔 넣는다. | 직접 |
| [Claude Code Docs — Hooks (PreToolUse decision control)](https://code.claude.com/docs/en/hooks) | 실행 전 검사는 차단·묻기·허용·보류를 정할 수 있고 입력을 고쳐 실행할 수도 있지만, 기본은 고치지 않고 사유를 붙여 막는다. | 직접 |
| [LangChain Docs — Built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in) · [Custom middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom) | 실행 전 메시지 검사, 도구 호출 감싸기, 검토에서만 멈추는 사람 승인, 호출 수 제한, 민감 값 가림을 항상 지나가는 경로에 둔다. | 요약 경유 |

## S2 관측

| 자료 | 이 문서에서 가져온 것 | 확인 |
|---|---|---|
| [OpenTelemetry — GenAI semantic conventions 저장소](https://github.com/open-telemetry/semantic-conventions-genai) | 이벤트 이름(모델 호출, 도구 실행, 계획, 토큰 사용량)을 이 규약에 맞추고, 내용은 기본으로 남기지 않는다. | 요약 경유 |
| [Claude Code Docs — Monitoring](https://code.claude.com/docs/en/monitoring-usage) | 한 요청의 이벤트를 요청 ID와 순번으로 묶고, 도구 결정·재시도·서브에이전트를 이벤트로 남긴다. | 요약 경유 |
| [Langfuse — Data model](https://langfuse.com/docs/observability/data-model) | 요청 1건을 기록 단위로 두고 그 안에 단계를 중첩한다. | 요약 경유 |
| [Langfuse — Masking](https://langfuse.com/docs/observability/features/masking) | 민감 정보는 기록을 내보내기 전에 애플리케이션 안에서 가린다. | 요약 경유 |
| [LangChain — LangSmith observability concepts](https://docs.langchain.com/langsmith/observability-concepts) | 기록에는 보존 기한이 있으므로 오래 둘 것은 평가셋으로 옮긴다. | 요약 경유 |
| [OpenTelemetry — Sampling](https://opentelemetry.io/docs/concepts/sampling/) | 기록량이 적으면 전부 남기고, 표본을 뽑아야 하면 오류가 난 요청은 항상 보관한다. | 요약 경유 |

## S6 자기개선

| 자료 | 이 문서에서 가져온 것 | 확인 |
|---|---|---|
| [Shinn 외 — Reflexion (arXiv 2303.11366)](https://arxiv.org/abs/2303.11366) | 실패 피드백을 글로 정리해 경험 메모리에 넣고 다음 시도에 쓴다. | 요약 경유 |
| [Zhao 외 — ExpeL (arXiv 2308.10144)](https://arxiv.org/abs/2308.10144) | 경험 사례와 거기서 뽑은 통찰을 두 층으로 나눠 저장한다. | 요약 경유 |
| [Wang 외 — Voyager (arXiv 2305.16291)](https://arxiv.org/abs/2305.16291) | 검증을 통과한 행동만 다시 쓸 수 있는 스킬로 저장한다. | 요약 경유 |
| [Zhang 외 — ACE (arXiv 2510.04618)](https://arxiv.org/abs/2510.04618) | 메모리를 통째로 다시 쓰지 않고 항목 단위로 두고 증분만 붙인다. | 요약 경유 |
| [Agrawal 외 — GEPA (arXiv 2507.19457)](https://arxiv.org/abs/2507.19457) | 실행 기록을 읽어 원인을 진단한 뒤 고치고, 후보를 하나로 줄이지 않고 여럿 유지한다. | 요약 경유 |
| [Yuksekgonul 외 — TextGrad (arXiv 2406.07496)](https://arxiv.org/abs/2406.07496) | 같은 개선 루프를 프롬프트 밖의 구성요소에도 적용한다. | 요약 경유 |
| [Zhang 외 — Darwin Gödel Machine (arXiv 2505.22954)](https://arxiv.org/abs/2505.22954) · [Sakana AI 글](https://sakana.ai/dgm/) | 개선 루프는 격리 환경과 사람 감독 아래에서 돌리고, 평가 절차는 루프가 고칠 수 없게 고정한다. | 요약 경유 |
| [Robeyns 외 — SICA (arXiv 2504.15228)](https://arxiv.org/abs/2504.15228) | 점수와 함께 비용·시간을 넣어 후보를 고르고, 과제당 비용과 시간에 상한을 둔다. | 요약 경유 |
| [OpenAI Cookbook — Self-evolving agents](https://developers.openai.com/cookbook/examples/partners/self_evolving_agents/autonomous_agent_retraining) | 개선 재시도에 상한을 두고, 버전과 되돌리기를 관리하며, 개선용과 검증용 데이터를 나눈다. | 요약 경유 |
| [METR — Recent frontier models are reward hacking](https://metr.org/blog/2025-06-05-recent-reward-hacking/) | 하지 말라는 지시만으로는 채점 우회를 막지 못하므로 구조로 막고, 이상하게 높은 점수는 사람이 검토한다. | 요약 경유 |
| [Zhong·Raghunathan·Carlini — ImpossibleBench (arXiv 2510.20270)](https://arxiv.org/abs/2510.20270) | 개선 중에는 테스트를 숨기거나 읽기 전용으로 두고, 사람에게 넘기는 출구를 준다. | 요약 경유 |

## S7 최적화

| 자료 | 이 문서에서 가져온 것 | 확인 |
|---|---|---|
| [Anthropic Docs — Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | 캐시는 접두 일치이므로 대화 중에 도구 정의와 시스템 프롬프트를 바꾸지 않고, 캐시 읽기 토큰으로 적중을 확인한다. | 직접 |
| [Anthropic Docs — Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence) | 비용은 완료된 작업 1건당으로 재고, 캐시, 배치, 프롬프트, 노력 수준, 모델 순으로 바꾼다. | 요약 경유 |
| [Anthropic Docs — Effort](https://platform.claude.com/docs/en/build-with-claude/effort) | 노력 수준은 우리 평가셋에서 품질이 유지되는지 잰 뒤에만 낮춘다. | 직접 |
| [Anthropic Docs — Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing) | 기다려도 되는 실행(평가 포함)은 배치로 돌린다. | 직접 |
| [Anthropic Docs — Reducing latency](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency) | 먼저 품질이 나오는 구성을 만든 뒤에 줄이고, 지연은 첫 토큰 시간과 전체 시간으로 잰다. | 직접 |
| [vLLM — Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/) | 직접 서빙에서 접두 캐시는 입력 처리 시간만 줄인다는 점을 감안해 기대 효과를 잡는다. | 요약 경유 |
| [vLLM — Structured outputs](https://docs.vllm.ai/en/latest/features/structured_outputs/) | 분류나 예/아니오 판단 단계는 출력을 선택지·스키마로 강제한다. | 요약 경유 |
| [vLLM — Metrics](https://docs.vllm.ai/en/latest/usage/metrics/) | 서빙 지표(첫 토큰 시간, 대기 요청 수, 접두 캐시 적중률)를 측정 항목으로 삼는다. | 요약 경유 |

## S8 배포·운영

| 자료 | 이 문서에서 가져온 것 | 확인 |
|---|---|---|
| [Google SRE Workbook — Canarying Releases](https://sre.google/workbook/canarying-releases/) | 일부에게만 정해진 기간 동안 배포하고, 전후 비교가 아니라 같은 기간의 대조군과 비교한다. | 요약 경유 |
| [Anthropic — A postmortem of three recent issues](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues) | 배포 뒤에도 운영 환경에서 평가를 계속 돌리고, 사용자 신고 경로와 되돌리기 절차를 둔다. | 요약 경유 |
| [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 자동 평가·운영 모니터링·사용자 피드백·기록 검토를 겹쳐 쓰고, 평가셋에 담당자를 둔다. | 요약 경유 |
| [LangChain — LangSmith online evaluations](https://docs.langchain.com/langsmith/online-evaluations) | 운영 기록 채점은 필터와 표본 비율로 비용을 통제한다. | 요약 경유 |
| [Langfuse — Datasets](https://langfuse.com/docs/evaluation/experiments/datasets) | 기대대로 되지 않은 운영 기록을 평가셋 항목으로 올리고, 변경마다 버전을 남긴다. | 요약 경유 |
| [Claude Code Docs — 플러그인 마켓플레이스 운영](https://code.claude.com/docs/en/plugins/host-marketplace) | 스킬·훅·지침 묶음을 버전을 고정해 배포하고, 안정 채널과 선행 채널을 나눈다. | 직접 |
| [Claude Code Docs — 조직 플러그인 관리](https://code.claude.com/docs/en/plugins/org) | 조직 차원의 강제는 사용자가 끌 수 없는 관리 설정으로 하고, 설치·로드 이벤트를 감사한다. | 직접 |

## 확인하지 못한 것

- "요약 경유"로 적은 자료의 문장은 원문과 글자 단위로 대조하지 못했다. 인용문으로 옮기려면 링크에서 다시 확인한다. 한 페이지에서 일부만 직접 읽은 자료(Hooks, Sandboxing)는 가져온 내용이 직접 읽은 부분이면 "직접"으로 적었다.
- OpenAI의 "Harness engineering: leveraging Codex in an agent-first world"는 403이어서 읽지 못했고, 이 글을 근거로 쓴 내용이 없어 표에 넣지 않았다.
- OpenAI의 SWE-bench Verified 글 두 편은 원문이 403이다. 소개 글은 미러 사본으로, 평가 중단 글은 검색 결과 요약으로만 확인했다.
- Pillar Security와 Invariant Labs의 글, ImpossibleBench와 패키지 이름 지어내기 논문의 수치는 검색 결과 요약으로만 봤다. 방향만 가져오고 수치는 넣지 않았다.
- OWASP Agentic Top 10(2026)은 공식 PDF를 읽지 못해 항목 제목을 2차 자료로 확인했다. OWASP LLM Top 10(2025)은 항목 제목만 확인했고 항목별 완화책은 읽지 않았다.
- 긴 문서의 뒷부분은 읽지 못했다(Prompt caching, Optimizing for cost and intelligence, Context editing, Monitoring). 캐시와 도구 결과·서브에이전트의 상호작용 세부가 빠졌을 수 있다.
- 자료의 수치는 각 자료가 자기 모델과 과제에서 잰 값이다. 방향만 믿고 값은 우리 평가셋으로 다시 잰다. 오래된 모델로 잰 편집 형식·파일 창 크기 수치와, 큰 컨텍스트 창을 전제로 한 권고가 특히 그렇다.
- 평가셋 건수, 환경 오류율 한도, 회귀 허용폭, 메모리 주입 건수, 반복 횟수, 완료율, 만료 기간, 표본 비율, 최대 라운드처럼 "(제안값)"으로 적은 값은 자료의 범위나 예시 안에서 우리가 고른 출발값이다.
- 공개 URL이 없는 자료는 표에 넣지 않았다. 개발 도구에 번들된 Anthropic의 평가 기반 개선·캐시 설계·비용·지연 가이드가 여기에 해당하며, 도구 버전에 따라 내용이 바뀐다.
- 규격과 도구 문서는 바뀔 수 있다. OpenTelemetry GenAI 규약은 개발 중 상태이고 저장소가 옮겨졌으며, MCP 보안 문서는 초안 판을 읽었고, 훅·권한·모니터링의 설정 이름은 Claude Code 버전에 따라 다르다.
- 직접 근거를 찾지 못한 것이 있다. 계획 리뷰가 결과 품질을 올린다는 측정, 지침 파일 길이와 준수율의 독립 측정, 메모리 검색에서 키워드와 임베딩을 비교한 자료, 결과·궤적·최종 응답 3축 구분의 1차 자료가 그렇다.
- 자료끼리 엇갈리거나 조사하지 않은 것도 있다. 판정 모델을 평가 대상과 다르게 둘지는 자료마다 다르고, Copilot 메모리의 만료 기간은 판본에 따라 다르게 나온다. NIST AI RMF 생성형 AI 프로파일과 DSPy 문서는 읽지 못했다.
