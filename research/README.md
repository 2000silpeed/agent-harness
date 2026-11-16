# 조사 보고서

하네스 문서(`claude-setup/`, `kit/`)를 공식 문서와 1차 자료로 점검한 조사 기록이다. R1~R6은 2026-11-11, R8~R12는 2026-11-16에 조사했다(R7은 낡아서 지웠다). 하네스 문서에는 결론만 넣었고, 출처별 요약·인용·판단 근거는 여기에 둔다. 자료 목록은 `kit/harness/reference/sources.md`와 `claude-setup/GUIDE.md` 끝의 "참고 자료"에 있다.

| 파일 | 다룬 범위 | 반영한 곳 |
|---|---|---|
| `R1-settings-memory.md` | Claude Code 설정 범위, 지침·메모리, 권한, MCP 위치 | `claude-setup/GUIDE.md` A0~A3, `claude-setup/templates/` |
| `R2-hooks-skills.md` | 훅 동작(실패 시 기본값, 서브에이전트, 우회 경로), 스킬, 상태줄, 관측 | `claude-setup/GUIDE.md` A4~A10, `claude-setup/hooks/` |
| `R3-architecture-context-tools.md` | 구조·흐름, 컨텍스트·캐시, 도구·편집 형식 | `kit/harness/METHOD.md` S0·S2·S3·S4, 템플릿 00·02·03·04 |
| `R4-evals.md` | 과제 형식, 채점, 비교 규칙과 통계, 기준선 | `kit/harness/reference/eval.md`, METHOD S1, 스킬 `golden-dataset`·`agent-eval` |
| `R5-control-security-observability.md` | 계획·승인 게이트, 층별 방어, 위협 점검, 기록 형식 | `kit/harness/reference/{plan-gate,security,trace}.md`, METHOD S5·S2 |
| `R6-memory-improve-optimize.md` | 메모리 저장·조회, 개선안 채택 절차, 최적화, 배포·운영 | `kit/harness/reference/memory-improve.md`, METHOD S3·S6·S7·S8 |
| `R8-chatbot-eval.md` | 대화형 어시스턴트의 평가: 대화 단위 채점, 모의 사용자, 검색과 생성의 분리, 답하지 않기, 운영 지표 | `kit/harness/reference/erp-eval.md`, `METHOD-erp.md` C1 |
| `R9-chatbot-knowledge-memory.md` | 지식 검색과 권한, 대화 상태와 캐시 배치, 장기 메모리, 도구 등급과 신원 전달, 큰 결과, 변경 전 확인 | `kit/harness/reference/erp-knowledge-tools.md`, `METHOD-erp.md` C3·C4 |
| `R10-chatbot-guardrails-compliance.md` | 사내 어시스턴트의 통제: 신원과 권한, 승인과 직무 분리, 반출 통제, 감사 기록, 외부 모델로 나가는 데이터, 법규 점검표 | `kit/harness/reference/erp-control.md`, `METHOD-erp.md` C5 |
| `R11-chatbot-architecture-ops.md` | 유형, 한 턴의 흐름과 지연 예산, 대화 비용 모델, 확대 단계, 축소 응답, 지식 운영 | `kit/harness/reference/erp-pipeline-ops.md`, `METHOD-erp.md` C0·C2·C7·C8 |
| `R12-sap-abap-gui-tools.md` | SAP 연동: API 정책, ABAP 소스 접근과 이관, 검사 도구, 권한과 기록, 데이터 추출, 화면 스크립팅 | `kit/harness/bases/sap.md` |

읽을 때 주의
- 보고서는 조사 시점의 문서를 대상으로 썼다. 보고서가 가리키는 파일 경로와 "현재 문서의 문제점" 절은 그 뒤 고쳐졌거나 없어진 것이 있다.
- 보고서마다 인용 신뢰도 표시가 있다. "직접"은 원문을 내려받아 대조한 것이고, "요약 경유"는 요약 도구를 거쳐 얻은 것이라 문자 단위로 대조하지 못했다. 하네스 문서에는 인용문을 넣지 않았다.
- 보고서의 "제안"·"직접 계산" 표시는 출처에 없는 우리 쪽 판단과 계산이다. 하네스 문서에서는 "(제안값)"으로 표시했다.
- 각 보고서 끝의 "확인 못 한 것"은 아직 열려 있다.
- `kit/harness/reference/security.md` 8~10절(판정 주체, 도구를 거치지 않는 길, 가드 측정)은 이 보고서들 뒤에 추가했다. 근거는 그 문서의 "참고 자료"에 있다.
- R8~R12의 법규·계약 관련 내용은 법률 자문이 아니다. 적용 여부는 회사의 법무·개인정보·내부감사 담당자와 ERP 공급사가 확인한다.
- R8~R11의 제목에 있는 "chatbot"은 조사 당시의 가칭이다. 방법론에서는 "ERP 어시스턴트"라고 부른다.
