# 조사 보고서 (2026-11-11)

하네스 문서(`claude-setup/`, `kit/`)를 공식 문서와 1차 자료로 점검한 조사 기록이다. 하네스 문서에는 결론만 넣었고, 출처별 요약·인용·판단 근거는 여기에 둔다. 자료 목록은 `kit/harness/reference/sources.md`와 `claude-setup/GUIDE.md` 끝의 "참고 자료"에 있다.

| 파일 | 다룬 범위 | 반영한 곳 |
|---|---|---|
| `R1-settings-memory.md` | Claude Code 설정 범위, 지침·메모리, 권한, MCP 위치 | `claude-setup/GUIDE.md` A0~A3, `claude-setup/templates/` |
| `R2-hooks-skills.md` | 훅 동작(실패 시 기본값, 서브에이전트, 우회 경로), 스킬, 상태줄, 관측 | `claude-setup/GUIDE.md` A4~A10, `claude-setup/hooks/` |
| `R3-architecture-context-tools.md` | 구조·흐름, 컨텍스트·캐시, 도구·편집 형식 | `kit/harness/METHOD.md` S0·S2·S3·S4, 템플릿 00·02·03·04 |
| `R4-evals.md` | 과제 형식, 채점, 비교 규칙과 통계, 기준선 | `kit/harness/reference/eval.md`, METHOD S1, 스킬 `golden-dataset`·`agent-eval` |
| `R5-control-security-observability.md` | 계획·승인 게이트, 층별 방어, 위협 점검, 기록 형식 | `kit/harness/reference/{plan-gate,security,trace}.md`, METHOD S5·S2 |
| `R6-memory-improve-optimize.md` | 메모리 저장·조회, 개선안 채택 절차, 최적화, 배포·운영 | `kit/harness/reference/memory-improve.md`, METHOD S3·S6·S7·S8 |

읽을 때 주의
- 보고서는 조사 시점의 문서를 대상으로 썼다. 보고서가 가리키는 파일 경로와 "현재 문서의 문제점" 절은 그 뒤 고쳐졌거나 없어진 것이 있다.
- 보고서마다 인용 신뢰도 표시가 있다. "직접"은 원문을 내려받아 대조한 것이고, "요약 경유"는 요약 도구를 거쳐 얻은 것이라 문자 단위로 대조하지 못했다. 하네스 문서에는 인용문을 넣지 않았다.
- 보고서의 "제안"·"직접 계산" 표시는 출처에 없는 우리 쪽 판단과 계산이다. 하네스 문서에서는 "(제안값)"으로 표시했다.
- 각 보고서 끝의 "확인 못 한 것"은 아직 열려 있다.
- `kit/harness/reference/security.md` 8~10절(판정 주체, 도구를 거치지 않는 길, 가드 측정)은 이 보고서들 뒤에 추가했다. 근거는 그 문서의 "참고 자료"에 있다.
