# 3일차 종합 — 멀티 에이전트 아키텍처와 하네스

## 실습 코드 위치

수업 저장소 `github.com/HyunjunJeon/sds_ax_advanced_2026` 기준 경로입니다. 각 폴더의 README로 확인했습니다.

| 강의 | 저장소 위치 | 근거 |
|---|---|---|
| 교재 | `Day03/Day3_Multi_Agent_Architecture_이론자료.pdf`, 판서 `Day03/Day03_01.png` | 00-deck·99-extras의 원본과 같은 자료로 보임(파일명은 다름) |
| 4강 실습 준비(`.env`) | `Day03_new/` — `.env.example` → `.env` (현재 `ANTHROPIC_API_KEY`·`EXA_API_KEY`만 있음) | 4강 노트, `Day03_new/README.md` "API 키 설정" |
| 노트북 과정 | `Day03_new/00-Setup` → `01-Workflow-vs-Agent` → `02-Agent-Architecture` → `03a-Sequence-Parallel`·`03b-Branch-Loop-Patterns` → `04a-Graph-Contracts-Budget`·`04b-Graph-Failure-Approval` → `05a-Failure-Cost-Boundary`·`05b-Measure-Fast-Compare` → `06-Lab-Research-Agents` (코드 `mas_lab/`, `rag_lab/`, 스킬 `skills/`) | `Day03_new/README.md` "노트북 순서" |
| 스크립트판 | `Day03/` — `00_prepare.py`~`13_mini_pjt.py`(순차·라우터·병렬·Supervisor·Handoff RAG) | `Day03/README.md` |
| 5·6강 FAQ 챗봇(LangGraph → Deep Agent) | 저장소에 없음 — 수업 중 Claude로 만든 코드(`classify_intent` 등 검색 결과 없음) | 05 노트 확인 필요 항목 |
| 디시전 모델 Jev | `used_jev_deepagents/`, `.agents/skills/langgraph-decision-models/` | `used_jev_deepagents/README.md` |

> 근거 칸이 강의 노트(직접 언급)가 아닌 행은 같은 날 주제에 맞는 저장소 자료입니다. 수업에서 그 폴더를 직접 열었는지는 노트로 확인되지 않습니다.

| 파일 | 내용 |
|---|---|
| [00-deck.md](00-deck.md) | 교재: Multi Agent Architecture (Ch.1 Workflow vs Agent ~ Ch.4 Engineering) |
| [01-lecture1.md](01-lecture1.md) | 1강: 에이전트 루프 복습, KV 캐시, 컨텍스트 격리 |
| [02-lecture2.md](02-lecture2.md) | 2강: 워크플로우에서 에이전트 배치, 싱글 우선, 패턴 4요소 |
| [03-lecture3.md](03-lecture3.md) | 3강: 싱글에서 멀티로, 배달앱 메뉴 태깅 사례 |
| [04-lecture4.md](04-lecture4.md) | 4강: 해킹 에이전트 사례, 하네스의 정의, 내 워크플로우(architecture.md) |
| [05-lecture5.md](05-lecture5.md) | 5강: LangGraph에서 Deep Agent로, 순서는 도구가 지킨다 |
| [06-lecture6.md](06-lecture6.md) | 6강: 동작은 그대로, 근거는 남기는 최적화 (4초 → 1.42초) |
| [07-lecture7.md](07-lecture7.md) | 7강: Claude Code 꿀팁 (워크플로우 패널, 토큰 절감, 캐시, 회고, 인터뷰 스킬) |
| [99-extras.md](99-extras.md) | 판서 이미지, `prompt.txt`(최적화 요청 원문), `cc_tip.txt`(팁 링크 모음) |

## 하루 요약
- **모든 멀티 에이전트 패턴의 출발점은 컨텍스트 격리다.** 모델은 자기회귀라 컨텍스트 관리가 핵심이다. KV 캐시는 텍스트 매칭이라 변하는 값(날짜)은 뒤에 둔다. 100만 컨텍스트도 탐색만으로 금방 차고, 80%를 넘으면 품질이 떨어진다.
- **구조를 먼저 고르지 않는다.** 비즈니스 워크플로우에서 사람이 판단하는 지점에 에이전트를 둔다. 규정·루틴은 코드로 처리한다. 돈·민감정보는 HITL로 보낸다.
- **시작은 무조건 싱글이다.** 싱글은 쪼갤 수 있지만 멀티는 합치기 어렵다. 측정과 기록을 근거로 큰 작업부터 서브에이전트로 뗀다. 기준은 "내 작업을 잘 해 주고 시간이 적정한가"다.
- **패턴 = 순차·병렬·분기·루프의 조합.** Router/Supervisor, Plan-and-Execute(실전에서 많이 씀), Swarm(종료 장치 필요). 서브에이전트는 페르소나가 아니라 컨텍스트 경계로 나눈다.
- **배달앱 사례:** 프롬프트 → 스킬 약 20개 → 라우팅 컬럼 사전 계산 → 데이터 사전 조회 + 캐시 → 카테고리별 에이전트. 사람이 확정한 골드셋으로 평가한다.
- **하네스 = 모델을 뺀 나머지 전부.** 도구·컨텍스트·상태·권한·예산·트레이스/이벨. 프롬프트 → 컨텍스트 → 하네스는 다루는 대상이 바뀌었을 뿐이다.
- **실습 흐름:** 내 워크플로우를 5단계 이하로 `architecture.md`에 쓴다 → 판단/생성 꼬리표 → LangGraph로 구현 → Deep Agent로 옮긴다(프롬프트로 순서를 지키는 건 "기도"이고, 도구가 강제해야 한다) → 동작을 유지한 채 최적화하고 근거를 남긴다(Haiku, 디시전 모델 jev, 토글).
- **Claude Code 팁:** 사람이 보고 개입하고 근거를 남기는 구조를 만든다. 출력 절감 도구(caveman 등), 상태줄에 캐시 깨짐 표시, 잘못 지시했으면 바로 멈추고 정정, "내 대화 기록 분석해줘"로 회고, `/goal`, 나를 인터뷰하는 스킬.
