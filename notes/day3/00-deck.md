# Day3 교재: Multi Agent Architecture

> 원본: `Day3_Multi_Agent_Architecture_Complete.pdf` (Google Drive, 43쪽, 강사 전현준)
> 원본은 PDF 텍스트 추출본을 바탕으로 정리했습니다. 다이어그램 설명은 슬라이드 안 텍스트 배치를 보고 재구성한 것입니다.

## Day3 교재: Multi Agent Architecture

### 목차 (덱 구조 그대로)

**표지 / 과정 로드맵 (p.1–3)**
- 표지: "Multi Agent Architecture", 전현준
- 과정 흐름: `Production RAG` (Era of AI Models / RAG / Search / Answer) → **Multi Agent Architecture (TODAY)** → `Agent Harness`
- TODAY 범위: Workflow vs Agent, Agent Architecture, Single vs Multi, Some Engineering
- 이후 주제(로드맵):
  - Advanced Agent: Agent Capability, Agent Skills, Function Call, Tool & MCP
  - Agent Ops: Agent Observability, Agent Evaluation, Trajectory, Gold Dataset
  - Agent Harness: Control Plane, Deterministic, Code Mode
  - Optimization: Local Model, vLLM, KV Cache, Route Models, Hybrid Model Arch
  - Agent Guardrail: Input Guardrail, output Guardrail, Model Guardrail, Code Guardrail
  - PJT: Coding Harness, Context Control

**목차 (p.4)**
1. Workflow vs Agent: 제어
2. AI Agent Architecture: 실행 구조
3. Single Agent? Multi Agent?: 분리 기준
4. 무슨무슨 Engineering: 설계 범위

**전체적인 방향성 (p.5)**

**Chapter 1. Workflow vs Agent (p.6–12)**
- Workflow와 Agent의 차이는 "다음 행동의 결정권"
- LLM 호출, 도구 사용, Agent Loop를 구분해서 봅니다
- 같은 고객 요청도 서로 다른 구조로 처리할 수 있습니다
- Workflow 안에 Agent를 넣을 수 있습니다
- 모델의 제안과 시스템의 실행 권한은 다릅니다
- 먼저 Single Agent 기준선을 만듭니다

**Chapter 2. AI Agent Architecture (p.13–24)**
- 패턴X, 먼저 업무의 상태와 의존관계를 그립니다
- 복잡한 구조도 네 가지 실행 방식으로 읽을 수 있습니다
- 패턴 이름을 실행 구조로 번역해 봅시다
- Network와 Swarm | 연결 형태와 제어권 전환을 구분합니다
- Supervisor | 전문가를 호출하되 최종 제어를 유지합니다
- Hierarchical Supervisor | 계층을 추가할 이유가 있어야 합니다
- Orchestrator-Worker | 작업을 나누고 결과를 다시 합칩니다
- Plan-and-Execute는 반드시 Waterfall이 아닙니다
- 결과를 돌려받을까요, 대화를 넘길까요?
- LangGraph에서는 구조가 State·Node·Edge로 드러납니다
- 같은 요청의 실행 경로를 비교합니다

**Chapter 3. Single Agent? Multi Agent? (p.25–33)**
- Multi-Agent를 만들기 전에 Single Agent의 실패를 확인합니다
- Multi-Agent의 이득과 비용은 함께 증가할 수 있습니다
- SubAgent를 나누는 기준은 Persona보다 Context 경계입니다
- Skill과 SubAgent는 대체재이면서 조합 가능한 도구입니다
- 성능 향상 수치보다 먼저 비교 조건을 읽어야 합니다
- Latency는 Agent 수보다 가장 긴 실행 경로로 봅니다
- 단순 문의와 복합 문의에 같은 비용을 쓸 필요는 없습니다
- 같은 문제·같은 제약으로 다양한 구조를 비교

**Chapter 4. 무슨무슨 Engineering (p.34–43)**
- 새로운 이름은 이전 기술을 없애는 것이 아닙니다
- Prompt | 역할보다 작업·근거·완료 기준을 구체화합니다
- Context | 전달할 정보와 반환할 결과를 설계합니다
- Harness | 모델이 실제 일을 끝내도록 실행을 관리합니다
- Graph와 Loop는 다음 단계와 종료 조건을 명시합니다
- 승인은 실행 전에, 재시도는 중복 실행 없이 설계합니다
- 완성형 시스템 | Workflow 안에 필요한 Agent만 배치합니다
- 마지막 질문 | 왜 이 구조를 선택했고, 어떤 장-단점이 있나요?
- 부가정보: 실시간 대화와 깊은 작업을 분리할 수 있습니다

---

### 섹션별 핵심 내용

#### 0. 전체적인 방향성 (p.5)
- 핵심 문장: **"업무를 먼저 나누고, 필요한 곳에만 Agent를 배치합니다."**
- 단계 다이어그램 (01–05):
  1. **작업 목표**: 무엇을 완료할까?
  2. **작업 Graph**: 순차·병렬·분기·루프
  3. **필요한 Agent**: 어디에 판단을 맡길까?
  4. **Context 분리**: 어떤 작업을 독립시킬까?
  5. **시스템 설계 / 검증·운영**: 상태·권한·예산·종료
- 최종 결과물은 "에이전트 조직도"가 아니라, **이유를 설명할 수 있는 실행 구조**입니다.
- 패턴 이름을 외우는 것보다 **왜 이 구조를 선택했는지**가 중요합니다.

#### Chapter 1. Workflow vs Agent

**Workflow와 Agent의 차이는 "다음 행동의 결정권" (p.7)**
- **Workflow (CODE)**: 코드가 정한 경로 안에서 실행합니다.
  - 다이어그램: 요청 분류(LLM 가능) → 환불 경로 / FAQ 경로 → 완료 시 종료. 분기는 있어도 선택지는 코드로 정의합니다.
- **Agent (MODEL)**: 모델이 결과를 보고 다음 행동을 선택합니다.
  - 다이어그램: 요청 → 판단 ↔ 도구 (관찰 → 재판단 루프)
- **LLM을 사용한다고 모두 Agent는 아닙니다.**

**LLM 호출, 도구 사용, Agent Loop 구분 (p.8)**
- 세 구조는 세대교체가 아니라 업무에 따라 선택하는 실행 방식입니다.
  - 01 **LLM 호출**: 입력 → LLM. 한 번의 생성 결과를 받습니다.
  - 02 **도구 사용**: 코드 → Tool. 외부 기능 호출만으로는 자율 실행 구조가 아닙니다.
  - 03 **Agent Loop**: 판단 ↔ 실행. 관찰 후 계속할지 끝낼지 선택합니다.
- 도구 호출 유무보다 **관찰 뒤의 행동 선택과 종료 조건**을 확인합니다.

**같은 고객 요청, 다른 구조 (p.9)**
- 가상 사례: "결제가 두 번 됐어요. 취소하고 보상안도 함께 확인해 주세요."
- **고정 경로**: 결제 조회(정해진 조회 항목) → 정책 확인(정해진 규칙) → 응답. 범위 밖 문의는 전환하며, 예외를 미리 정의해야 합니다.
- **동적 조사**: 의도 해석(결제 + 장애) → 필요 근거 선택(결제·정책·장애) → 종합·확인 → 추가 질문 / 종료. 근거에 따라 조사 경로가 바뀝니다.
- 같은 업무를 놓고 구조를 바꾸면 선택 이유와 비용을 비교할 수 있습니다.

**Workflow 안에 Agent를 넣을 수 있습니다 (p.10)**
- 예측 가능한 절차는 고정하고, 모호한 판단만 모델에게 맡깁니다.
- 다이어그램: `CODE` 본인 확인 → `MODEL` 복합 의도 해석 → `API` 자료 조회 → `RULE` 정책·권한 확인 → `AGENT` 조사·종합
- 코드 경로: 인증·조회·한도·쓰기 실행 / 모델 판단: 의도·계획·근거 종합
- 좋은 Agentic System은 "모든 노드가 Agent"인 시스템이 아닙니다.

**모델의 제안과 시스템의 실행 권한은 다릅니다 (p.11)**
- "가능할 것 같다"는 모델 출력이 곧 실행 허가는 아닙니다.
- 흐름: 모델의 처리 제안(환불 후보·필요 근거) → **실행 검증 게이트**(정책 · 권한 · 입력, 필요 시 사람 승인) → 허용된 제안 전달 → 쓰기 도구(검증을 통과한 요청만)
- 거절·보류 → 미실행 또는 사람에게 전환
- **모델은 행동을 제안하고, 시스템은 허용된 행동만 실행합니다.**

**Single Agent 기준선 (p.12)**
- 작은 사례를 실행하고 성공 여부·시간·호출 수를 기록합니다.
- 구조: 고객 요청 → Agent ↔ 허용된 Tools → 응답
- 측정 기록:
  - `task_success`: 성공 / 실패
  - `total_latency`: 소요 시간
  - `model / tool calls`: 각 호출 수
  - `input / output tokens`: 토큰 수
- 관찰 질문: 어떤 요청에서 실패했습니까? 정보 부족과 실행 오류를 구분했습니까?
- 실행 기록 + 실패 사례 1개. **기준선 없이는 개선 여부도 알 수 없습니다.**

#### Chapter 2. AI Agent Architecture

**패턴보다 업무의 상태와 의존관계를 먼저 그립니다 (p.14)**
- 순서: 목표 → 필요한 상태 → 작업 → 선행 조건 → 종료 조건
- 다이어그램: 본인·권한 확인(선행 조건) → [결제 확인 / 정책 확인 / 장애 확인] (독립 조회가 가능한 범위만 병렬화) → 처리 제안 + 근거 (완료·미확정 상태 구분)
- 상태 예시: `customer_verified`, `billing_facts`, `policy_evidence`, `outage_facts`
- "Billing Agent를 만들자"보다 **"무엇이 먼저 필요할까?"**를 질문합니다.

**네 가지 실행 방식 (p.15)**
- **순차 Sequence**: 선행 결과가 있어야 다음 단계를 실행 (예: 인증 → 조회 → 응답)
- **병렬 Parallel**: 독립적인 작업을 실행한 뒤 합류 (예: 결제 조회 / 장애 조회 → 합류)
- **분기 Branch**: 조건에 따라 실행 경로를 선택 (예: 의도 분류 → 환불 경로 / FAQ 경로)
- **루프 Loop**: 검증 후 재시도하거나 종료 (예: 생성 → 검증 → 종료)
- 새로운 패턴을 만나도 **순서·독립성·조건·종료**부터 확인합니다.

**패턴 이름 → 실행 구조 번역 (p.16)**
Supervisor, Swarm 같은 패턴도 완전히 새로운 제어 구조는 아닙니다.

| 패턴 | 실행 구조로 읽기 | 확인할 질문 |
|---|---|---|
| Router | 조건 분기 | 어떤 경로로 보낼까? |
| Supervisor | 분기 + 루프, 필요 시 병렬 | 누가 결과를 받고 다음 일을 정할까? |
| Orchestrator-Worker | 분해 → 작업 실행 → 집계 | 어떻게 나누고 다시 합칠까? |
| Swarm / Handoff | 담당자 전환 + 반복 | 누가 대화를 이어받을까? |
| Hierarchical Supervisor | 위 구조를 계층으로 중첩 | 새 경계가 정말 필요한가? |

- Plan-and-Execute는 계획·실행·재계획을 바라보는 별도의 관점입니다.

**Network와 Swarm (p.17)**
- Network는 연결의 모양이고, 이 강의의 Swarm은 동적 Handoff 규칙에 초점을 둡니다.
- **Network**: A, B, C가 서로 연결된 그림. 여러 연결이 있다는 뜻입니다.
- **Swarm / Handoff**: Triage(초기 분류) → handoff → Billing(결제 담당, 현재 담당 ACTIVE) / Technical. 다음 대화는 현재 담당자가 이어받습니다.
- 한 시점의 **active agent와 전환 조건**을 명시해야 합니다.

**Supervisor (p.18)**
- 전문가의 결과를 받은 뒤 다음 작업과 최종 응답을 결정합니다.
- 다이어그램: 사용자 → 요청 → Supervisor(최종 응답·다음 작업 결정) → 호출 → Billing / Policy / Outage → 결과 반환 → Supervisor → 최종 응답
- 전문가는 결과를 반환하고, 대화의 제어권은 Supervisor에 남습니다.

**Hierarchical Supervisor (p.19)**
- 조직도를 모방하기보다 작업과 정보의 범위가 달라지는지 확인합니다.
- 다이어그램: Root Supervisor → 결제 팀 Supervisor(거래 사실, 환불 정책) / 기술 팀 Supervisor(장애 로그, 보상 정책)
- 계층 간 전달물은 전체 로그보다 **근거·상태·한계**입니다.
- 계층이 늘수록 전달 누락·지연·책임 분산도 함께 점검합니다.

**Orchestrator-Worker (p.20)**
- 요청마다 필요한 작업을 정하고, 독립적인 부분만 병렬로 수행합니다.
- 다이어그램: Orchestrator(계획·작업 분해) → Billing / Policy / Outage (Worker) → Synthesize(근거 집계) → 검증(근거·완료 기준) → PASS → 종료 / 근거 부족 + 예산 잔여 → 재계획
- Worker 수를 늘리는 것보다 **작업의 독립성과 결과 계약**이 중요합니다.

**Plan-and-Execute는 반드시 Waterfall이 아닙니다 (p.21)**
- 계획의 존재보다 실행 중 관찰과 재계획이 가능한지가 중요합니다.
- 고정 계획·일괄 실행: 계획 확정 → 전체 실행 → 마지막 검증. 변화에 대한 피드백이 늦습니다.
- 관찰·수정·재계획: 목표·완료 기준·현재 상태 → 실행 → 테스트 → 관찰 → 수정 + 계획 갱신 (반복)
- 한 Agent도 계획·실행·검증·재계획을 반복할 수 있습니다.

**결과를 돌려받을까요, 대화를 넘길까요? (p.22)**
- **MANAGER**: Manager(최종 응답 담당) → 작업 위임 / 결과 반환 ← Specialist(범위가 정해진 조사). 용도: 복합 조사, 근거 종합.
- **HANDOFF**: 현재 Agent(이전 대화 담당) → 제어권 + 필요한 Context → Specialist(새로운 대화 담당). 용도: 전문 상담, 대화 전환.
- 둘 중 하나만 고를 필요는 없습니다. 대화 전환 안에서 조사 Workflow를 쓸 수 있습니다.

**LangGraph: State·Node·Edge (p.23)**
- 상태는 무엇을 공유하는가, 노드는 무엇을 하는가, 엣지는 언제 실행되는가를 정합니다.
  - 업무 상태: `State / TypedDict`
  - 작업 노드: `add_node(...)`
  - 실행 관계: `add_edge(...) / conditional`
  - 동적 작업 배분: `Send("worker", task_input)`
- 설계 포인트: 최소 입력 전달, 결과 병합 규칙 명시, 예산·종료 조건 설정
- **Send는 동적 작업 배분 수단입니다. 그 자체가 Multi-Agent 아키텍처는 아닙니다.**

**같은 요청의 실행 경로 비교 (p.24)**
- 누가 다음 행동을 결정했는지, 결과가 어디로 돌아갔는지 표시합니다. (개념 TRACE, 실측 아님)
  - Supervisor: Supervisor → Billing → Supervisor → 응답
  - Handoff: Triage → Billing → Technical → 응답
- 기록 항목: control owner / 호출 수 / Context 전달 범위 / 최종 응답 주체
- 두 구조의 실제 Trace와, 제어권이 달라진 지점 1개를 확인합니다.

#### Chapter 3. Single Agent? Multi Agent?

**Single Agent의 실패부터 확인 (p.26)**
이미 해결되는 작업은 굳이 나누지 않습니다. 실패의 원인부터 구분합니다.

| 관찰한 문제 | 먼저 점검할 것 | 분리 검토의 근거 |
|---|---|---|
| 정보가 부족함 | 검색·조회·추가 질문의 적절성 | 서로 다른 근거 조사가 필요한가? |
| 도구를 잘못 선택함 | 도구 설명·입력 계약·권한 | 도구 범위를 독립시킬 이유가 있는가? |
| Context가 너무 큼 | 불필요한 이력·로그·검색 결과 | 별도 작업으로 분리 가능한가? |
| 단계 의존성이 강함 | 현재 상태·순서·종료 조건 | 분리보다 고정 경로가 적합한가? |

- 빈도와 영향도는 기준선 실행 후 기록합니다. 이 표는 실제 오류 통계가 아닙니다.
- 프롬프트·도구·검색으로 해결할 문제와, 작업 분리가 필요한 문제를 구분합니다.

**이득과 비용 (p.27)**
- 작업 분리로 얻는 이득이 추가 호출과 조정 비용을 정당화해야 합니다.
- 얻을 수 있는 이득:
  - 독립 작업 병렬화: 동시에 진행할 수 있는 조사
  - 집중된 Context: 작업에 필요한 정보만 제공
  - 전문화·검증 지점: 서로 다른 도구와 완료 기준
- 추가로 지불하는 비용:
  - 모델 호출·토큰: Agent 간 지시와 결과도 비용
  - 전달 손실·조정 지연: 요약 누락과 반복 호출
  - 추가 실패 지점: 공유 상태·재시도·권한 관리
- Agent 수가 아니라 같은 업무에서 얻은 **품질·시간·비용의 변화**를 비교합니다.

**SubAgent 분리 기준은 Persona보다 Context 경계 (p.28)**
- 각 작업에 필요한 정보만 주고, 근거와 한계를 포함한 결과를 받습니다.
- 왼쪽 "하나의 큰 Context": 결제 사실, 정책 문서, 장애 로그, 대화 이력, 검색 결과, 중간 추론. 모든 정보가 함께 누적됩니다.
- 오른쪽: Billing(결제 사실) / Policy(해당 정책) / Outage(장애 정보). 각각 필요한 정보만 받고, Supervisor ← 결과·근거·불확실성을 반환합니다.
- **Context 분리와 보안 격리는 다릅니다. 권한은 별도로 설계합니다.**

**Skill vs SubAgent (p.29)**
- 절차를 불러올 것인가, 별도 실행 Context로 위임할 것인가?
- **Skill**: 같은 Agent가 절차(지시·자료·절차)를 로드합니다. Agent가 제어를 유지하며, 하나의 실행 Context에서 동작합니다.
- **SubAgent**: 작업 실행을 위임합니다. Main이 최종 제어를 갖고, SubAgent는 별도 Context + 반환 계약으로 동작하며 Skill을 사용할 수 있습니다.
- 복잡도만으로 나누지 말고, **Context·도구·권한·병렬 실행의 필요성**을 확인합니다.

**성능 수치보다 비교 조건을 먼저 읽기 (p.30)**
- 아래 두 수치는 같은 비교 기준을 사용하지 않습니다.
  - **Research 평가 +90.2%**: 비교 대상은 Single-Agent Opus 5. Opus 5 리드 + Sonnet 5 SubAgents 구성의, 특정 내부 research eval에서의 상대 개선입니다.
  - **토큰 사용량 약 15배**: 비교 대상은 일반 Chat. Multi-Agent 시스템의 토큰 사용 보고이며 Single Agent 대비 수치가 아닙니다.
- "90.2%p 향상"도, "Single Agent보다 토큰 15배"도 아닙니다.

**Latency는 가장 긴 실행 경로로 봅니다 (p.31)**
- 직렬 작업은 누적되고, 병렬 작업도 조정·집계 시간을 지불합니다.
- 직렬: A → B → C → 집계
- 병렬: 조정 → [A / B / C] → 집계. 독립성·자원 제한·공유 상태에 따라 이득이 달라집니다.
- 독립 작업만 병렬화하고, 실제 전체 지연시간으로 확인합니다.

**Fast Path / Slow Path (p.32)**
- Fast Path와 Slow Path를 나누되, 쓰기 작업의 안전성 검사는 공통으로 둡니다.
- 다이어그램: Router(복잡도·의도) →
  - Fast Path: FAQ · 단순 Workflow → 조회 응답
  - Slow Path: Orchestrator-Worker 조사
  - 복잡도 오판 시 → Slow Path 또는 사람에게 전환
  - 쓰기 요청만 → 공통 실행 게이트(정책·권한·필요 승인) → 실행 → 결과 확인 → 응답
- **Fast Path는 안전 검사를 생략하는 지름길이 아닙니다.**

**같은 문제·같은 제약으로 구조 비교 (p.33)**
- 성공률만 보지 말고 지연시간·토큰·정책 위반도 함께 기록합니다.

| 사례 유형 | Single | Single + Skills | Supervisor | Handoff | Hybrid |
|---|---|---|---|---|---|
| 단순 문의 | 측정 | 측정 | 측정 | 측정 | 측정 |
| 복합 문의 | 측정 | 측정 | 측정 | 측정 | 측정 |
| 정보 부족 | 측정 | 측정 | 측정 | 측정 | 측정 |
| 승인 필요 | 측정 | 측정 | 측정 | 측정 | 측정 |

- 고정 조건: 동일 데이터 · 도구 권한 · 모델 조건 · 예산 정책 · 반복 실행
- 유형별 결과와 선택 근거를 확인합니다.

#### Chapter 4. 무슨무슨 Engineering

**새로운 이름은 이전 기술을 없애지 않습니다 (p.35)**
- Prompt는 지시, Context는 제공 정보, Harness는 실행 환경을 설계합니다.
  - **Prompt**: 무엇을 어떻게 지시할까?
  - **Context**: 매 순간 어떤 정보를 보여줄까?
  - **Harness**: 어떻게 실행·검증·중단·복구할까?
- 함께 보는 관점: **Graph**(작업·상태·의존관계), **Loop**(반복·재시도·종료)

**Prompt: 역할보다 작업·근거·완료 기준 (p.36)**
- 무엇을 할까, 무엇을 근거로 판단할까, 어떤 형식으로 끝낼까?
- 역할만 있는 지시: "너는 환불 전문가야." 역할은 있지만 작업 계약은 부족합니다.
- 작업 계약이 있는 지시 (원문):

```
작업  이중 결제 여부와 보상 가능 근거를 확인
근거  제공된 거래 사실·정책·장애 자료만 사용
출력  확인된 사실 / 근거 / 미확정 항목을 반환
한계  자료가 없으면 확인 불가로 명시
권한  실제 환불은 제안만 하고 실행하지 않음
```

- 역할 프롬프트가 무의미한 것은 아니지만, 역할 이름만으로 업무가 완성되지 않습니다.

**Context: 전달할 정보와 반환할 결과 설계 (p.37)**
- 원문 전체를 복제하지 말고, 필요한 입력과 검증 가능한 결과를 전달합니다.

```
Supervisor → Worker            Worker → Supervisor
task_id        어떤 작업인가      status         완료 / 미확정 / 실패
goal           무엇을 완료할까    facts          확인된 사실
facts          이 작업에 필요한 사실  evidence_refs  검증 가능한 근거
allowed_tools  허용된 도구        uncertainty    확인되지 않은 부분
```

- 짧은 요약만 받기보다 **사실과 근거와 불확실성**을 함께 받습니다.

**Harness: 모델이 실제 일을 끝내도록 실행을 관리 (p.38)**
- 실행·검증·중단·복구는 모델 주변 시스템의 책임입니다.
- HARNESS 구성 요소 (Agent Loop를 둘러싼 형태):
  - Tools: 호출·입력 검증
  - Context: 필요 정보 제공
  - State: 저장·재개
  - Permissions: 권한·승인
  - Budget: 호출·시간 한도
  - Trace · Eval: 관찰·평가
- 좋은 프롬프트에 더해, 상태와 검증 기준을 가진 실행 환경이 필요합니다.

**Graph와 Loop: 다음 단계와 종료 조건 명시 (p.39)**
- 실패했다고 무조건 다시 호출하지 않습니다. 실패 종류에 따라 다음 행동이 달라집니다.
- 검증(근거·정책·결과) 결과별 분기:
  - PASS → 응답·종료
  - 근거 부족 → 예산 확인 → 재조사
  - 정책 불가 → 미실행·이유 안내
  - 시스템 오류 → 상태 확인 → 재시도 / 전환
- 재시도 횟수뿐 아니라 전체 예산과 미실행·전환·종료 상태를 정합니다.

**승인은 실행 전에, 재시도는 중복 실행 없이 (p.40)**
- 흐름: 처리 제안(MODEL) → 정책·권한 검증(RULE) → 필요한 승인(HUMAN / CODE) → 쓰기 실행(API) → 결과 확인(STATE)
- 거절 → 미실행 종료
- 실행 전후: Checkpoint + 처리 상태 / 중복 방지: 요청 키 + 외부 결과 조회
- `idempotency_key`는 외부 시스템이 지원·강제해야 합니다.
- **Checkpoint로 재개해도, 외부 API의 exactly-once 실행이 자동 보장되지는 않습니다.**

**완성형 시스템 (p.41)**
- 구성: Fast/Slow 분석 경로 + Context 분리 + 공통 실행 게이트 + 검증·복구
- HARNESS (상태 · 권한 · 예산 · Trace · 복구) 안에서:
  - 본인·권한 확인 → 의도 Router →
    - FAQ · 단순 조회 → 조회 응답
    - O-W(Orchestrator-Worker) 조사·근거 집계 (Worker별 Context 분리) → 답변 / 처리 제안 (근거 + 불확실성)
  - 쓰기 요청만 → 공통 검증·필요 승인 → 쓰기 실행 → 결과 확인 → 응답 / 사람 전환
- 처음의 업무 목표를 끝까지 추적하고, 실행과 미실행의 결과까지 설명합니다.

**마지막 질문: 왜 이 구조를 선택했고, 어떤 장단점이 있나요? (p.42)**
- 업무 목표: 어떤 상태를 완료로 볼까?
- 작업 Graph: 순차·병렬·분기·루프는?
- Agent·SubAgent의 필요성: 코드나 Skill로 충분하지 않은 이유는?
- Context·권한: 무엇을 보고 무엇을 실행할 수 있을까?
- 예산·종료: 언제 재시도하고 언제 전환할까?
- 평가 근거: 어떤 결과로 선택을 정당화할까?
- **Agent 수가 아니라, 설계 이유가 결과물입니다.**

**부가정보: 실시간 대화와 깊은 작업 분리 (p.43)**
- 대화의 미디어 경로를 유지하면서, 깊은 조사와 도구 실행은 별도 비동기 경로로 보냅니다.
- LIVE MEDIA PATH: 사용자 음성 입·출력 ↔ Realtime Front (대화 흐름 유지, 대화 응답, 지속적 상호작용)
- ASYNC DELEGATION: Deep task / Tools (조사·추론·외부 실행). 작업 결과는 상태와 함께 반환합니다.
- Fast/Slow는 "어떤 경로인가"의 문제이고, 비동기는 "기다리는 동안 무엇을 할까"의 문제입니다.

---

### 실습 과제 / 단계

덱에 별도의 "실습" 슬라이드는 없습니다. 아래는 슬라이드 하단에 제시된 산출물·기록 항목을 순서대로 모은 것입니다.

1. **Single Agent 기준선 (p.12)**: 작은 고객 요청 사례를 Single Agent + 허용된 Tools로 실행하고 `task_success`, `total_latency`, `model / tool calls`, `input / output tokens`를 기록합니다. 산출물은 **실행 기록 + 실패 사례 1개**입니다.
2. **업무 상태·의존관계 그리기 (p.14)**: 목표 → 필요한 상태 → 작업 → 선행 조건 → 종료 조건 순으로 정리합니다. 상태 키 예시: `customer_verified`, `billing_facts`, `policy_evidence`, `outage_facts`.
3. **실행 경로 비교 (p.24)**: 같은 요청을 Supervisor와 Handoff로 실행해 control owner / 호출 수 / Context 전달 범위 / 최종 응답 주체를 기록합니다. 산출물은 **두 구조의 실제 Trace와, 제어권이 달라진 지점 1개**입니다.
4. **Single 실패 원인 분류 (p.26)**: 정보 부족 / 도구 오선택 / Context 과다 / 단계 의존성 중 무엇인지 구분하고, 빈도와 영향도를 기준선 실행 후 기록합니다.
5. **구조 비교 매트릭스 (p.33)**: 단순 문의 / 복합 문의 / 정보 부족 / 승인 필요 × Single / Single + Skills / Supervisor / Handoff / Hybrid를 측정합니다. 데이터·도구 권한·모델 조건·예산 정책·반복 실행 조건은 고정하고, 성공률·지연시간·토큰·정책 위반을 기록합니다.
6. **설계 이유 정리 (p.42)**: 업무 목표, 작업 Graph, Agent·SubAgent 필요성, Context·권한, 예산·종료, 평가 근거에 답합니다.

---

### 실제 프로젝트 적용 체크리스트

**설계 출발점**
- [ ] 작업 목표와 "완료" 상태를 먼저 정의했다
- [ ] 작업 Graph(순차·병렬·분기·루프)를 그렸다
- [ ] 각 노드가 CODE / RULE / API / MODEL / AGENT 중 무엇인지 구분했다 (모든 노드를 Agent로 만들지 않았다)
- [ ] 상태 키와 선행 조건·종료 조건을 명시했다

**Single → Multi 판단**
- [ ] Single Agent 기준선(task_success, latency, calls, tokens)을 측정했다
- [ ] 실패 원인을 정보 부족 / 도구 선택 / Context 크기 / 단계 의존성으로 분류했다
- [ ] 프롬프트·도구·검색으로 해결할 수 있는지 먼저 확인했다
- [ ] SubAgent 분리 기준을 Persona가 아니라 Context 경계로 잡았다
- [ ] Skill로 충분한지, SubAgent(별도 Context + 반환 계약)가 필요한지 검토했다
- [ ] 병렬화는 독립 작업에만 적용하고, 실제 전체 지연시간으로 확인했다
- [ ] 이득(병렬화·집중 Context·검증 지점)이 비용(호출·토큰·전달 손실·실패 지점)을 정당화하는지 비교했다
- [ ] 외부 성능 수치를 인용할 때 비교 대상과 조건을 확인했다

**패턴 선택**
- [ ] 패턴 이름을 실행 구조(분기/루프/병렬/분해·집계/전환)로 번역해 설명할 수 있다
- [ ] Manager(결과 반환)와 Handoff(대화 이전) 중 무엇이 필요한지 정했다
- [ ] Handoff를 쓴다면 시점별 active agent와 전환 조건을 명시했다
- [ ] 계층(Hierarchical)을 추가할 이유(작업·정보 범위 차이)가 있다
- [ ] Plan-and-Execute에서 관찰·재계획 루프가 있다

**Prompt / Context 계약**
- [ ] 프롬프트에 작업·근거·출력·한계·권한을 명시했다
- [ ] Supervisor → Worker 입력: task_id, goal, facts, allowed_tools
- [ ] Worker → Supervisor 출력: status, facts, evidence_refs, uncertainty
- [ ] Context 분리와 보안 격리(권한)를 별도로 설계했다

**Harness / 안전**
- [ ] Tools 입력 검증, State 저장·재개, Permissions, Budget, Trace·Eval을 갖췄다
- [ ] 모델의 제안과 실행 권한을 분리하고, 쓰기 작업 앞에 실행 검증 게이트를 두었다
- [ ] Fast Path에서도 쓰기 요청은 공통 게이트(정책·권한·승인)를 거친다
- [ ] 실패 유형별(근거 부족 / 정책 불가 / 시스템 오류) 다음 행동을 정의했다
- [ ] 재시도 횟수와 전체 예산, 미실행·전환·종료 상태를 정했다
- [ ] 쓰기 실행 전후 Checkpoint와 처리 상태를 남긴다
- [ ] idempotency_key를 외부 시스템이 지원·강제하는지 확인했다 (exactly-once는 자동 보장되지 않음)
- [ ] 복잡도 오판이나 거절·보류 시 사람에게 전환하는 경로가 있다

**평가 / 운영**
- [ ] 같은 데이터·권한·모델·예산 조건으로 여러 구조를 비교했다
- [ ] 성공률 외에 지연시간·토큰·정책 위반도 기록했다
- [ ] 실시간 대화가 있다면 Live 경로와 비동기 Deep task 경로를 분리할지 검토했다
- [ ] "왜 이 구조인가"를 장단점과 평가 근거로 설명할 수 있다
