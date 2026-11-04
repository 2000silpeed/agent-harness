# docs — 단계별 가이드

강의(SDS AX Advanced 2~3일차) 내용을 하네스 구축 순서로 다시 배열했습니다. 위에서부터 차례로 읽으면 됩니다.

| 단계 | 문서 | 핵심 질문 |
|---|---|---|
| 0 | [00-environment-setup.md](00-environment-setup.md) | 작업 환경을 어떻게 안전하게 시작할까? |
| 1 | [01-rag-and-retrieval.md](01-rag-and-retrieval.md) | 무엇을, 얼마나 가져와 넣을까? |
| 2 | [02-skills.md](02-skills.md) | 배경지식을 어떻게 캐시를 깨지 않고 붙일까? |
| 3 | [03-multiturn-memory.md](03-multiturn-memory.md) | 멀티턴 기억은 어떻게 관리할까? |
| 4 | [04-context-and-cache.md](04-context-and-cache.md) | 컨텍스트 윈도우를 어떻게 배치하고 아낄까? |
| 5 | [05-tools-and-structured-output.md](05-tools-and-structured-output.md) | 도구와 출력 규격은 어떻게 설계할까? |
| 6 | [06-deep-agent-middleware-hooks.md](06-deep-agent-middleware-hooks.md) | 루프의 어디에 개입할 수 있을까? |
| 7 | [07-workflow-vs-agent.md](07-workflow-vs-agent.md) | 어디에 에이전트를 둘까? |
| 8 | [08-execution-patterns.md](08-execution-patterns.md) | 어떤 실행 구조로 엮을까? |
| 9 | [09-single-vs-multi.md](09-single-vs-multi.md) | 언제 나눌까? |
| 10 | [10-harness.md](10-harness.md) | 모델을 뺀 나머지를 어떻게 만들까? |
| 11 | [11-tool-enforced-ordering.md](11-tool-enforced-ordering.md) | 순서를 프롬프트가 아니라 도구로 지키려면? |
| 12 | [12-agent-optimization.md](12-agent-optimization.md) | 동작은 그대로 두고 빠르고 싸게 만들려면? |
| 13 | [13-evaluation.md](13-evaluation.md) | 좋아졌는지 어떻게 알까? |
| 14 | [14-observability-and-cost.md](14-observability-and-cost.md) | 근거를 어떻게 남기고 비용을 어떻게 줄일까? |
| 15 | [15-working-habits.md](15-working-habits.md) | 에이전트에게 어떻게 일을 잘 시킬까? |
| 참고 | [resources.md](resources.md) | 강의에서 공유된 외부 저장소는? |
| 소스 | [sources.md](sources.md) | 어떤 강의 자료가 언제 반영됐나? |
| 사례 | [case-menu-tagging.md](case-menu-tagging.md) | 싱글에서 멀티로 실제로 어떻게 진화했나? |

- `decisions/`: 최적화·구조 변경 근거 기록(`templates/optimization-log.md` 형식)
- 표시 규칙: **[강의]** 강의에서 직접 나온 내용 · **[제안]** 강의 아이디어를 바탕으로 하네스용으로 덧붙인 내용 · **[불확실]** 전사 품질 등으로 원문 확인이 어려운 내용
