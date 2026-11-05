# 2일차 종합 — RAG, 멀티턴, LangGraph·Deep Agent 첫 실습

## 실습 코드 위치

수업 저장소 `github.com/HyunjunJeon/sds_ax_advanced_2026` 기준 경로입니다. 각 폴더의 README로 확인했습니다.

| 강의 | 저장소 위치 | 근거 |
|---|---|---|
| 4강 실습 환경 | `Day01/` — LangGraph V1 튜토리얼(원본 `braincrew-lab/langgraph-v1-tutorial` 스냅샷), `.env.example`에 Anthropic·Tavily 키 | `Day01/README.md`, `Day01/UPSTREAM.md:5` |
| 5강 LangGraph 챗봇 | `Day01/PART02-에이전트/Ch02-에이전트/02-LangGraph-ChatBot.ipynb` | 강의 속 "agent 02 → 챕터 02 → 랭그래프 챗봇", 노트북에 수업 시연 값(`claude-sonnet-5-5`, 가상 주가)이 남아 있음 |
| 6강 Structured Output·Deep Agent | `Day01/PART02-에이전트/Ch04-구조화된-출력/05-LangGraph-Structured-Output.ipynb` (셀 #35 Tavily 저장, 셀 #36 Day01 요약), 결과 `Day01/sample_data/tavily/`, `Day01/sample_data/summary/day01_overview.md` | 노트북 마지막 두 셀 |
| 7(딥에이전트 실습·훅) | 위 6강 노트북 셀 #36, 미들웨어는 `Day01/PART03-에이전트-확장/Ch06-미들웨어/01-LangGraph-Middleware.ipynb`, 스킬 문서 `.agents/skills/deep-agents-core/SKILL.md` | 07 노트의 과정 페이지 출처 |
| 1~3강 RAG 이론의 실습판 | `Day02/` (스크립트 `00`~`13`, `Day2_Production_RAG_수업자료.pdf`), 병렬 새 버전 `Day02_new/` 노트북 `00-Setup`~`06-Lab-DeepAgents-RAG` | `Day02/README.md`, `Day02_new/README.md`. 강의 녹음에서 이 폴더를 직접 연 장면은 없음 |
| 디시전 모델 Jev | `used_jev_deepagents/` (Jev + Deep Agents RAG 예제), `.agents/skills/langgraph-decision-models/` | `used_jev_deepagents/README.md:1-4` |

> 근거 칸이 강의 노트(직접 언급)가 아닌 행은 같은 날 주제에 맞는 저장소 자료입니다. 수업에서 그 폴더를 직접 열었는지는 노트로 확인되지 않습니다.

| 파일 | 내용 |
|---|---|
| [01-lecture1.md](01-lecture1.md) | 1강: RAG의 핵심, 잘 찾아오기와 잘 이야기하기 (+ 10일 과정 로드맵) |
| [02-lecture2.md](02-lecture2.md) | 2강: 파일로 저장(계층 폴더 + index.md), 스킬로 말하기, 멀티턴 관리 |
| [03-lecture3.md](03-lecture3.md) | 3강: 멀티턴 기억 관리, "멀티턴은 허상", 출력 줄이기 |
| [04-lecture4.md](04-lecture4.md) | 4강: 재귀적 자기 개선(RSI)·소프트웨어 팩토리, Claude Code 실습 환경 세팅 |
| [05-lecture5.md](05-lecture5.md) | 5강: LangGraph 챗봇, 메시지·툴·컨텍스트 구조, 캐시 |
| [06-lecture6.md](06-lecture6.md) | 6강: Structured Output과 도구 호출, Deep Agent 코드 읽기 |
| [07-deepagent-practice.md](07-deepagent-practice.md) | 딥에이전트 실습 (녹음 없음, 재구성 장표) |

## 하루 요약
- **과정 로드맵(1강):** 2일차 RAG → 3~4일차 멀티 에이전트·MCP/Skills → 5일차 옵저버빌리티 → 6일차 하네스 엔지니어링·Claude Code 팁 → 7~8일차 로컬 LLM·KV 캐시·가드레일 → 9~10일차 코딩 에이전트 프로젝트.
- **RAG = 잘 찾아오기 + 잘 이야기하기.** 검색은 적게, 정확히 해야 한다. 벡터 DB는 기본값이 아니다. 대·중·소 계층 폴더에 `index.md` 목차를 두고, 목차 탐색은 작은 모델이나 디시전 모델 서브에이전트에 맡긴다.
- **생성 쪽:** 시스템 프롬프트를 바꾸면 캐시가 깨진다. 시스템 프롬프트는 앞에 고정하고 지식은 스킬로 뒤에 붙인다. Lost in the Middle은 앞에서 짧게 안내하고 뒤에서 연결하는 "똑같지 않은 반복"으로 막는다.
- **스킬 = 조각 지식.** name·description(what·when)으로 로드 여부를 판단한다. 커지면 폴더로 쪼개고 `skill.md`를 인덱스로 만든다.
- **멀티턴:** 압축하면 품질이 떨어진다. 요약에 원본 대화로 가는 경로를 남긴다. 품질이 최우선이면 "사용자는 멀티턴, 내부는 단일턴"으로 간다. 주제 변경은 작은 모델이 0/1로 감지한다.
- **출력은 입력보다 비싸다.** 클로즈드 퀘스천(선택지 고르기)으로 출력을 줄인다.
- **실습:** Claude Code를 WSL + 작업 폴더로 세팅하고 `.env`에 Anthropic·Tavily 키를 넣는다. LangGraph 챗봇(State → 노드 → 그래프)을 만들고 `create_deep_agent` = `create_agent` + 미들웨어(파일시스템·서브에이전트 등)를 읽는다. 마지막으로 Day01 폴더를 요약해 저장한다.
- **보안 포인트:** 가짜 도구 호출 기록을 넣으면 모델이 믿는다. 이건 세션 분리로 막는다(8일차 가드레일).
- **Anthropic API 캐시는 명시적으로 켜야 한다.** `usage`에서 확인한다.
