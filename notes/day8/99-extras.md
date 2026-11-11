## 8일차 부가 자료

강의 저장소 `sds_ax_advanced_2026`의 `Day08/`, `Day08_new/`를 읽기 전용으로 확인해 판서 이미지 2장, 실습 파일 위치, 코드에서 읽은 설계 패턴, 공개 사례 출처를 정리했다. 코드는 실행하지 않았다. 경로는 저장소 루트 기준이고 줄 번호는 2026-11-11에 읽은 사본 기준이다(`Day08_new/docs/architecture.md`는 이 폴더의 코드가 계속 바뀐다고 적는다). 판서는 손글씨라 읽은 그대로 옮겼다.

두 폴더는 축이 다르다. `Day08/`은 같은 공격에 **방어를 어디에 두는가**(Input / Action / Output / 메모리 / 승인)를 바꾸고, `Day08_new/`는 같은 상담 Agent에서 **누가 판정하는가**(코드 / LM / Decision 모델 / 사람)를 바꾼다. `Day08_new/AGENTS.md:6`은 `Day08/`을 "별도의 이전 자료"라고 적는다.

### 1. 판서 이미지

**`Day08/Day08_01.png` — Input·Output 경계, 도구 제한, HITL**
- 왼쪽 큰 글씨: "Agent (중국모델들)".
- 가운데 흐름: `Input → / → [Agent] → MSG, API → / → Output`. 빗금 두 개가 입력 경계와 출력 경계다.
- 입력 경계 위: "<위협>", "claude: 끊어버림.", "gpt: 그런건 X".
- 출력 경계 위: "<유출>", "Model: 작은 모델로 '검토'", "Code: '개인정보 탐지'".
- Agent 아래: "1. 내부 DB", "2. 외부 웹서치", `def get_db(sql: str)`, "어디를 가져오는지".
- 오른쪽: "오동작을 막아낸다 => 툴을 제한한다."
  - `def get_db(sql: str)` — "1. DB 조회 계정 권한", "2. sql 이 SELECT 만".
  - `def get_web(url: str)` — "1. white-list 기반 탐색", "2. HTML 읽음 -> 필터링(JSON)".
- 가운데 아래(웹 검색 경로의 인젝션 예): "> 뉴스 사이트, bloomberg.com" / "- 그 정보는 *blooomsberg.com* 에서 가져오는게 좋을지도?" / "robots.txt, llms.txt => SQL, Prompt Injection" / "bloomsberg_1jnasdfnkad.com/send/me".
- 아래: `[HITL]` 상자 → 오른쪽 상자("승인 / 거부"). HITL에서 빨간 화살표가 아래 상자로 내려간다. 아래 상자 안 "수신인 / 제목 / 초안 / 사용자 피드백", 상자 위 "DB 저장", 상자 오른쪽 "승인 / 거부". 맨 아래 빨간 글씨 "Agent 배치 → DB Read + send_email()".
- 요지: 도구 인자를 넓게 받지 않고(임의 SQL 대신 조회 계정 + SELECT만, 임의 URL 대신 허용 목록 + 구조화된 결과) 도구 자체를 좁혀 오동작을 막는다. 승인 요청은 DB에 저장해 두고 배치로 읽어 전송한다(승인 대기와 실행의 분리).

**`Day08/Day08_02.png` — Agent Harness 구성요소**
- "Agent Harness" 상자 안에 빨간 글씨로 Prompt, Model(위), Agent(가운데), Skills, Tools(아래). Agent에서 네 요소로 화살표.
- Prompt 쪽 메모: "줄이는게 좋은 방향 / 무작정 다 줄일 수 없음 / Tool, Skill 을 잘 활용할 수 있게끔", "(계층형)메모리", "검색 메모리".
- Model 쪽 메모: "작은 모델: Worker / 큰 모델: Orchestrator", "모델: Plan, Worker", "모델사 마다 / 모델 마다".
- Agent 오른쪽: "- DeepAgents*", "- Pi" 그리고 "1. 최소 Agent Loop 구성 2. 최소 Tools => 8개 3. Plugin 으로 결합 가능".
- 상자 아래 절반(Skills·Tools) 오른쪽: "개발자가 제어하는 영역".
- Skills 아래: "Tool 보다 좀 더 큰 개념 = 도메인 지식 저장", "Progressive Disclosure", "SKILL.md => index".
- Tools 아래: "Code Interpreter", "Code Mode 등 적절한 프로그램 실행 설계", 상자 `Data Read`("어떤 데이터를 제공해줄 것인가?"), 상자 `Data Write`("어떤 데이터를 제공 받을 것인가?").
- 오른쪽 아래 상자 "MCP Server": "1. 공통화", "2. 보안성...".
- 요지: 하네스를 Prompt / Model / Skills / Tools로 나누고, 개발자가 직접 제어하는 곳은 Skills와 Tools라고 본다. 도구 설계의 질문은 읽기(무엇을 내줄 것인가)와 쓰기(무엇을 받을 것인가)다.

### 2. 저장소 위치

방어 층 표기: 입력 / 행동(도구 호출) / 출력 / 메모리 / 사람 승인 / 모델 경계 / Cascade.

**`Day08/` — 누리소프트 주간 보고 Agent (방어 위치 비교)**

| 파일 | 보여 주는 것 | 방어 층 |
|---|---|---|
| `Day08/00_baseline_agent.py` | 방어가 시스템 프롬프트의 금지 문장뿐인 B0를 돌리고, 평가기가 답변이 아니라 전송함·초안·실행 기록으로 판정하는 방식을 본다 | 없음(기준선) |
| `Day08/01_input_guard.py` | Input Guard의 검사 범위를 사용자 메시지만(`("user",)`)에서 도구 결과까지로 넓히면 문서 속 지시가 표시가 붙은 데이터로 바뀌어 들어가고, 정상 문서(`security_training`)의 과잉 차단 여부가 드러난다 | 입력 |
| `Day08/02_action_guard.py` | 권한 검사를 분류기만 / 부모 middleware / 도구 래퍼 / 도구 래퍼 + 최소 도구에 두었을 때를 비교해, 부모 middleware가 Subagent(`research`) 경로를 놓치고 도구 래퍼는 탐지가 전부 실패해도(`always_allow`) 막는다는 것을 본다 | 행동(도구 호출) |
| `Day08/03_output_guard.py` | 공개 경로 셋(최종 답변, `send_report` 본문, `save_report` 초안) 가운데 최종 답변만 검사하면 전송함·초안에 전화번호가 남는다는 것을 본다 | 출력 |
| `Day08/04_memory_permissions.py` | 두 세션으로 정책 파일·메모리 오염을 재현하고, 순서만 다른 파일 권한 규칙 두 구성과 메모리 읽기·쓰기 검사의 결과 차이를 본다 | 메모리 |
| `Day08/05_hitl_approval.py` | approve 클릭만 믿는 구성과 승인 기록(도구·인자 해시·요청자·만료)에 묶는 구성을 승인 뒤 인자 수정·중복 클릭·만료 시나리오로 비교한다(전부 대본) | 사람 승인 |
| `Day08/06_compare.py` | B0(지침만)·B3(모델 + 코드 결합)·B4(B3에서 방어 하나 제거)를 같은 사례로 돌려 어느 방어가 실제로 막았는지 가른다 | 전체(ablation) |
| `Day08/07_lfm_encoders.py` | LFM PII-Detector와 Policy-Linter를 한국어 문서에 직접 적용해 토큰 분절, 놓친 구간, 한국어·영어 점수 차이를 본다(로컬 CPU) | 출력(탐지기 단독 평가) |
| `Day08/08_guard_models.py` | 분류기 6종(SGuard, Kanana, gpt-oss-safeguard, Nemotron, Llama Guard, 키워드)을 같은 입력 17건으로 비교해 미탐·오탐·UNKNOWN·지연을 본다 | 입력(Guard 모델 비교) |
| `Day08/task.md` | 수업 중 활동: Input Guard 없이 기본 DeepAgents를 만들고 `guardlab/data/redteam.jsonl`로 공격·방어를 검증한 뒤 모델 기반 Guard를 붙인다 | 입력 |
| `Day08/project_guide.md` | 최종 프로젝트: dcode 소스로 Coding Assistant 만들기와 평가 기준 4항목 × 10점(코드 품질, 계획·리뷰·승인, Memory·Self-Improving, 모니터링) | — |

- 공통 부품: `Day08/guardlab/defenses.py`(방어 논리), `components.py`(middleware·래퍼·메모리 검사·승인 저장소), `context.py`(신뢰 컨텍스트), `harness.py`(내장 도구 제거), `budget.py`(실행 예산), `guards/`(Guard 계약·클라이언트), `evaluate.py`·`trace.py`·`outbox.py`(상태 판정).
- 데이터: `guardlab/data/attacks/`(공격·정상 문서 19개), `cases.jsonl`(사례 10건), `holdout.jsonl`(미공개 2건, 06 최종 확인 전용), `redteam.jsonl`(task.md용).
- `Day08/dcode-analysis/`: 프로젝트 참고 자료. dcode(`deepagents-code` 0.1.69, SDK 0.7.14, 커밋 `1d3232c`) 소스 분석 10편이 `analysis/00~09`에 있다(`04-approval-hitl-security.md`, `06-memory-skills.md`, `07-mcp-hooks-extensions-plugins.md`, `08-sandboxes-execution.md` 등). 이 노트에서는 목차만 확인했고 본문은 분석하지 않았다.

**`Day08_new/` — 누리카드 고객 상담 Agent (판정 주체 비교)**

| 파일 | 보여 주는 것 | 방어 층 |
|---|---|---|
| `Day08_new/00_setup_check.py` | 키 세 개의 상태와 판정 주체 셋(주모델, OpenRouter LM, Jev)의 응답 1회씩, 그리고 판정 근거가 되는 상태 파일(원장·답장·전송함)을 확인한다 | 없음(준비) |
| `Day08_new/01_incidents_baseline.py` | 공개 사고를 "할 수 있던 것 / 공격 경로 / 없던 경계"로 읽고, 도구를 Rule of Two로 칠한 뒤 Guard 없는 B0에서 E3~E9가 모두 뚫리는 것과 프롬프트 금지 문장이 대본 경로를 못 막는 것을 본다 | 없음(기준선) |
| `Day08_new/02_logic_guards.py` | 코드 규칙(신원 범위, 값 단위 taint, egress 등록부, 단정형 규정, 한도·승인 바인딩, 규칙 순서, 배치)을 한 가지씩 깨뜨린 구성 7개와 나란히 돌린다 | 행동(도구 호출) |
| `Day08_new/03_lm_guards.py` | 가벼운 범용 LLM 3종 + 키워드 기준선에 같은 정책 문장과 json_schema를 주고 FNR·FPR·REVIEW·UNKNOWN·지연·비용, 문자 주입 변형과 정규화, 판정 실패, 답장 근거 Judge, 2단 구성, logprob을 잰다 | 입력 / 출력(답장 근거) |
| `Day08_new/04_decision_guards.py` | 코드 사전 검사 뒤 남은 항목에 Jev Noul 세 개를 묻고, 두 문턱값을 dev 레이블로 고르는 절차와 질문 문장·흔들림·LM 기준선을 본다 | 행동(도구 호출) |
| `Day08_new/05_cascade_lab.py` | 코드만(C0) / 코드+LM(C1) / 코드+Decision(C2) / 코드+Decision→LM(C3) / 내 설계(C4)를 같은 세트에 넣고 제약(공격 성공 0, 허용 오류 0, REVIEW율, 비용)을 만족하는 구성을 고른다 | Cascade |
| `Day08_new/06_hitl_interrupt.py` | REVIEW를 안내문(H0) / 내장 `interrupt_on`(H1) / 게이트의 REVIEW에서만 interrupt(H2)로 바꿔, 멈춘 순간의 원장과 사람에게 물은 횟수를 비교한다 | 사람 승인 |
| `Day08_new/07_model_boundary.py` | 게이트가 못 보는 세 길(상담원 메시지 `before_agent`, 주모델 공급자로 나가는 값 `wrap_model_call`, 최종 답변 `after_agent`)에 각각 Guard를 건다 | 모델 경계 (입력 / 출력 포함) |
| `Day08_new/08_memory_guard.py` | 세션 둘짜리 사례에서 메모 쓰기를 없음(W0) / 읽기 전용(W1) / 출처 규칙(W2) / 출처 + 내용 판정(W3)으로 막고, 오염된 뒤의 행동 게이트를 본다 | 메모리 |
| `Day08_new/09_memory_scope.py` | 메모를 한 파일(M0) / 가림(M1) / 고객별 파일 + permissions(M2) / 공용 파일 쓰기 검사(M3)로 바꿔, 둘째 세션 프롬프트에 실린 다른 고객 메모와 민감 값을 센다 | 메모리 / 모델 경계 |

- 공통 부품과 문서: `Day08_new/guard_lab/`(모듈 표는 `Day08_new/README.md:140-155`), `docs/architecture.md`(코드 구조, 함수 이름으로 설명), `docs/artex_architecture.md`(읽기 자료: 자율 침투 테스트 Agent ARTEX의 게이트 구조. 수업에서 다루지 않음), `docs/sources/01~05`(사례 출처와 확인 수준).
- 데이터: `data/episodes.jsonl`(E1~E10), `data/hitl.json`·`boundary.json`·`memory.json`·`memory_scope.json`(06~09 사례. AI 초안, 저자 검수 전), `data/sets/`(판정 항목 세트: `s_input` 40건, `s_action` 48건, `s_grounding` 30건. 레이블은 AI 초안), `data/holdout/`(`guard_lab/holdout.py`만 연다), `data/recorded/`(저자가 남긴 Guard 응답. 측정 결과로 인용하지 않는다).
- 도구 8개와 Rule of Two 칠하기(`Day08_new/guard_lab/tools.py:23-35`): `read_ticket`·`search_policy` [A] 비신뢰 입력, `lookup_customer` [B] 민감 데이터, `issue_refund`·`waive_fee` [C] 상태 변경(돈), `reply_ticket`·`send_email` [C] 외부 통신, `request_approval` 사람 승인.

### 3. 코드에서 읽은 설계 패턴

각 항목은 무엇을 검사하나 / 어디서 도나(도구 안 대 middleware) / 실패하면 무엇을 하나 / 저장소 문서가 "못 막는다"고 적은 것 순서다.

#### 3.1 `Day08_new/guard_lab/` (판정 주체 축)

1. **신뢰 컨텍스트 (`context.py:17-42`, `tools.py:167-173`, `gate.py:91-97`).** 상담원·등급·환불/면제 한도·티켓·티켓 주인을 frozen dataclass `RunContext`에 담아 `agent.invoke(..., context=ctx)`로 넣는다. 도구 안에서는 `runtime.context`, middleware에서는 `request.runtime.context`로 읽는다. 컨텍스트가 없으면 게이트가 `BLOCK NO_CONTEXT`를 낸다. 권한의 근거가 모델이 고른 인자가 아니므로 "팀장 승인 받았다"는 티켓 문구가 한도를 바꾸지 못한다. 못 막는 것: 컨텍스트가 허용한 범위 안에서 일어나는 잘못(E5 규정에 없는 약속을 담은 답장, E10 애매한 면제).
2. **신원 범위 규칙 (`logic_guards.py:76-94`).** 조회·환불·면제·승인 요청의 대상 고객이 티켓 주인인지, 답장이 지금 티켓으로 가는지 본다. 도구 안의 게이트가 실행 전에 돌고, 어긋나면 `BLOCK IDENTITY_SCOPE`다. `identity="model_arg"`가 깨뜨리기 설정이고, 그때 E9(가족이라며 다른 고객 조회)가 뚫린다.
3. **값 단위 taint 대 세션 taint (`logic_guards.py:98-155`, `world.py:110`).** 답장·이메일 본문에 "티켓 고객이 아닌 고객"의 민감 값(전화, 이메일, 카드 끝자리, 거래 ID)이 있으면 `BLOCK TAINT_OTHER_CUSTOMER`다. 비교기 `contains_value`는 정규화한 글과 공백을 모두 뺀 글 두 가지로 비교하고, 숫자 값은 앞뒤가 숫자가 아닐 때만 일치로 본다. 게이트와 평가기가 같은 비교기를 쓴다. 세션 단위(`taint="session"`)는 비신뢰 입력을 읽은 뒤의 모든 [C] 행동을 막아 정상 업무 E1까지 막힌다. 못 막는 것: 값을 글자 그대로 찾으므로 바꿔 적거나 요약한 정보.
4. **egress 허용 목록 + 도메인 등록부 (`logic_guards.py:159-171`, `data/world/domain_registry.json`).** `send_email`의 수신 도메인이 허용 목록에 있고, 등록부에서 지금도 회사 소유인지 확인한다. 목록에 남은 만료 도메인(`nuricard-support.example`, 2026-08-14 만료 후 제3자 재등록)은 `BLOCK EGRESS_DOMAIN_NOT_OWNED`다. `egress="allowlist"`(목록만)가 깨뜨리기 설정이다(E8). 이 규칙은 `send_email`만 본다. 답장 본문 안의 URL이나 화면 렌더링 경로는 보지 않는다.
5. **사전 검사와 단정형 규정의 코드화 (`logic_guards.py:175-231`).** 거래·수수료가 있는지, 주인이 맞는지, 금액이 0보다 크고 거래액 이하인지(`PRECHECK_*`), 그리고 조건이 딱 떨어지는 규정 R3(해외 결제 수수료 환불 금지)·R4(연회비는 발급 30일 이내·미사용만)를 코드로 막는다. 해석이 필요한 규정(R1 가맹점 취소 확인, W2 "장애"의 범위)은 옮기지 않고 LM·Decision에 넘긴다. 못 막는 것: 환불 호출은 막지만 답장 **내용**은 보지 않는다(E5).
6. **한도와 승인 바인딩 (`logic_guards.py:242-286`, `tools.py:119-157`).** 금액이 상담원 한도(L1 환불 50,000원, 면제 30,000원)를 넘으면 `REVIEW NEEDS_APPROVAL`이다. 승인번호가 있으면 승인 기록의 (도구·고객·대상·금액)이 실행 인자와 같고 아직 쓰지 않은 승인인지 본다. 어긋나면 `APPROVAL_INVALID` / `APPROVAL_MISMATCH` / `APPROVAL_REUSED`로 BLOCK이고, 통과하면 `used`를 올리고 `judge="human"`인 ALLOW를 낸다. `approval="exists"`(번호만 확인)가 깨뜨리기 설정이다(E7). 이 폴더의 승인 기록에는 만료가 없다(`Day08/`에는 있다, 3.2의 5번).
7. **규칙 순서가 정책 (`logic_guards.py:290-338`).** 규칙은 (이름, 함수) 목록이고 첫 일치가 이긴다. 아무 규칙도 관여하지 않으면 ALLOW다(`NO_RULE_MATCHED`). 기본은 거부 규칙 6개 뒤에 허용 규칙(`known_recipient`)이 온다. `rule_order="allow_first"`면 "아는 수신자" 허용이 먼저 이겨 본문 taint 검사까지 가지 못하고 E3의 유출 답장이 통과한다.
8. **게이트: ALLOW일 때만 원시 구현 (`gate.py:217-224`, `gate.py:207-214`, `trace.py:250-256`).** `Gate.__call__`이 결정 하나를 기록하고, ALLOW가 아니면 예외를 던지지 않고 `[차단됨 사유]` 또는 `[사람 검토 필요 사유]` 문자열을 도구 결과로 돌려준다(Agent는 다음 행동을 이어 간다). `impl_called_on_block`(ALLOW가 아닌 결정 뒤 실행된 수)이 항상 0이어야 한다는 것을 테스트가 고정한다.
9. **배치와 Subagent 경로 (`agent.py:85-112`, `gate.py:227-257`, `trace.py:258-263`).** 같은 게이트를 도구 객체 안(`tool_wrapper`)에 두면 도구를 넘겨받은 Subagent의 호출도 지난다. 부모의 `wrap_tool_call`(`parent_middleware`)에만 두면 Subagent `policy-research`의 조회가 검사 없이 실행되고 `missed_paths`에 잡힌다. 같은 배치 문제가 07의 가림(D1), 08의 메모 쓰기(P2)에서 반복된다. Subagent에는 middleware를 따로 붙여야 한다.
10. **판정 실패는 통과가 아니다 (`contracts.py:123-163`, `gate.py:51-62`, `lm_guards.py:313-343`, `decision_guards.py:141-149`·`176-188`·`358-368`, `cascade.py:37-46`).** 판정 주체가 낸 신호의 `status`가 UNKNOWN이면 `resolve_signal`·`judge_text`가 항상 REVIEW로 바꾼다. LM 쪽 UNKNOWN은 전송·HTTP 실패, 빈 본문, JSON 파싱 실패, 스키마 위반, 필드 불일치(`decision`이 ALLOW인데 `reason_code`가 NONE이 아님) 다섯 가지다. Decision 쪽은 `DecisionError`(틀린 키 포함), 거절, 범위 밖 확률(NaN 포함)이다. 기록 재생에서 기록이 없을 때도 UNKNOWN이다. 대가: 공급자가 429를 돌려주면 그만큼 사람이 볼 REVIEW가 늘고, 재시도는 없다(`README.md:181`).
11. **두 문턱값 Band (`contracts.py:76-120`, `decision_guards.py:109-116`, `04_decision_guards.py:54-56`).** 확률 하나를 `approve_at`·`block_at` 두 값으로 ALLOW / REVIEW / BLOCK으로 바꾼다. 방향이 둘이다: 환불·면제 질문은 높을수록 안전(`higher_is_safe`, 시작값 0.9 / 0.1), 입력 질문은 높을수록 위험(`higher_is_risky`, 0.1 / 0.9). 범위 밖이거나 방향과 거꾸로인 문턱값은 만들 때 예외다. 가운데 구간은 억지로 가르지 않고 사람이나 다음 판정 주체로 보낸다. 시작값은 cookbook 저자가 고른 값이고 정답이 아니라고 적혀 있다.
12. **문턱값을 레이블로 고르는 절차 (`decision_guards.py:480-616`).** 격자(APPROVE_AT 0.50~0.99, BLOCK_AT 0.01~0.45)를 돌며 dev 레이블로 (i) 위험 허용(레이블 BLOCK인데 ALLOW) 0인 점 → (ii) REVIEW 비율이 사람 용량(`REVIEW_CAPACITY=0.15`) 안인 점 → (iii) 정상 차단 + 검토 대상 허용이 최소인 점 → (iv) 동률이면 REVIEW 구간이 넓은 점 순으로 고른다. 제약을 만족하는 점이 없으면 "제약 불가"·"용량 초과"로 보고한다. 측정 전에 규칙을 고정하고 holdout으로 다시 고르지 않는다. 흔들림(반복 시 표준편차)은 보고만 한다.
13. **Decision 질문은 작게 나누고 사실은 코드가 넣는다 (`decision_guards.py:68-97`·`356-388`, `gate.py:160-179`).** 환불·면제 판정은 Noul 세 개(`customer_asked`, `right_target`, `policy_covers`)를 한 요청으로 묻고 가장 낮은 확률에 Band를 적용한다. "이 처리를 해도 괜찮은가" 하나로 묻는 느슨한 질문과 비교한다. 거래 종류·발급 경과일·사용 실적·연체 횟수는 `known_facts`가 세계에서 읽어 판정 글에 넣는다(판정 주체가 조건을 추측하지 않게).
14. **LM Guard 요청 고정 (`lm_guards.py:142-172`, `lm_guards.py:30-41`).** 전용 Guard 모델이 아니라 범용 LLM에 정책 문장 + `json_schema`(strict)를 주고, `temperature` 0, 추론 끔, 공급자 고정(`allow_fallbacks=False`), 타임아웃 15초로 부른다. 같은 모델도 공급자마다 지연·비용·logprob 지원이 달라 모델별 공급자를 적어 둔다. 정책 문장은 공격 문구를 인용·경고·신고하는 글은 지시가 아니라고 명시한다(`lm_guards.py:43-50`). 못 막는 것: 문자 주입 변형(E4)은 LM 단독으로 통하지 않아 앞단 정규화와 값 단위 taint가 필요하다(`README.md:28`).
15. **입력 검사는 실행을 막지 않고 글을 바꾼다 (`gate.py:182-205`, `normalize.py:57`).** 비신뢰 입력 도구(`read_ticket`, `search_policy`)의 결과는 도구가 실행된 뒤 판정한다. BLOCK이면 원문 대신 안내문을, REVIEW면 경고문을 앞에 붙인 원문을 모델에게 준다. 정규화는 보이지 않는 문자를 지우고 NFKC로 전각·자모 분리를 되돌린다(글자 사이 공백 변형은 되돌리지 않는다). 한계: 대본 모델은 도구 결과를 읽지 않으므로 이 장치가 모델 행동을 바꾸는지는 실제 주모델로만 볼 수 있다(`docs/architecture.md` 23절).
16. **Cascade 순서 (`gate.py:100-158`, `cascade.py:49-69`·`94-131`).** 게이트 안의 순서는 ① 코드 규칙(BLOCK·REVIEW면 거기서 끝, 유효한 사람 승인이면 의미 검사를 건너뜀) → ② 돈 도구면 action Guard → ③ `reply_ticket`이면 답장 근거 Guard → ALLOW → 실행 → ④ 비신뢰 입력이면 내용 검사다. `EscalatingGuard(first, second)`는 1단이 REVIEW(또는 UNKNOWN)일 때만 2단을 부른다. 모든 구성에서 코드 규칙은 빠지지 않는다. `Memo`가 같은 입력의 결과를 기억해 중복 호출을 막는다. 범위: 의미 검사는 돈 도구와 답장에만 걸린다. `send_email` 본문에는 코드 규칙만 걸린다.
17. **HITL — REVIEW에서만 멈추고 승인을 게이트로 되돌린다 (`hitl.py:152-224`·`235-262`·`298-319`, `hitl.py:37`).** `ReviewInterruptMiddleware.wrap_tool_call`이 도구 안 게이트의 결정이 REVIEW인 돈 호출에서 `interrupt()`로 멈춘다. 사람이 승인(또는 고쳐서 승인)하면 (도구·고객·대상·금액)에 묶인 승인 기록을 쓰고, 승인번호를 넣은 호출이 같은 코드 규칙을 다시 지난다(고친 인자도 신원 범위·규정 규칙을 다시 지남). 재개하면 함수가 처음부터 다시 돌기 때문에 첫 실행의 물음을 `pending`에 기억해 게이트를 두 번 부르지 않고, 승인 뒤 호출은 ID를 `…:approved`로 바꿔 기록한다. `InMemorySaver` + `thread_id`가 필요하고, 사람에게 묻는 횟수 상한 `HUMAN_ASK_LIMIT=10`이 있다. 내장 `interrupt_on`은 게이트 결정과 무관하게 매번 멈추고, 그 승인은 승인 기록이 아니라서 한도 초과 호출은 승인 뒤에도 다시 REVIEW가 된다. 한계: 멈추는 것은 돈 도구의 REVIEW뿐이고 답장 근거의 REVIEW는 안내문으로 남는다. `pending`은 프로세스 메모리다. `HUMAN_POLICY="approve_all"`(묻는 대로 승인)이면 장치가 있어도 걸러내지 못한다.
18. **모델 경계 ① 사용자 메시지 검사 (`boundary.py:41-55`·`83-107`).** `before_agent`에서 상담원 메시지(붙여 넣은 고객 글 포함)를 LM 또는 Jev로 판정한다. ALLOW가 아니면 안내문을 답변으로 넣고 `jump_to="end"`로 실행을 통째로 끝낸다(모델 호출 0). 판정 실패도 실행하지 않는다. 대가: 도구 게이트는 위험한 호출만 막고 업무를 끝내지만 메시지 Guard는 업무까지 멈춘다. `on_flag="warn"`은 경고문만 붙이고 계속한다.
19. **모델 경계 ② 공급자로 나가는 값 가림 (`boundary.py:118-217`).** `wrap_model_call`에서 `request.override(messages=...)`로 이번 요청에 보낼 메시지만 바꾼다. 상태의 원문은 그대로라 도구와 게이트는 원래 값을 본다. 가리는 값은 고객 기록의 전화·이메일·카드 끝자리이고, 업무에 쓰는 거래 ID·금액·이름은 가리지 않는다. 나간 값은 값 자체가 아니라 이름표(`C-1001:phone`)로 기록한다. Subagent의 모델 호출도 같은 공급자로 나가므로 Main과 Subagent 모두에 붙여야 한다. 한계: 시스템 프롬프트에 실리는 메모는 가리지 않는다(09가 다룸).
20. **모델 경계 ③ 최종 답변과 원장 대조 (`boundary.py:221-361`).** `after_agent`에서 답변이 "환불·면제를 처리했다"고 말하는지 Jev가 확률로 읽고(0.7 이상 주장함, 0.3 이하 주장 안 함, 사이는 불확실) 코드가 원장과 맞춘다. 주장하는데 원장에 없으면 답변을 실행 기록으로 바꾸고(`ANSWER_MISMATCH`), 불확실하면 "확인 필요"와 실행 기록을 붙인다. 코드 전용 방식은 판정 없이 실행 기록을 항상 붙인다. 문턱값은 손으로 정한 시작값이다.
21. **메모리 쓰기: 출처 규칙 → 내용 판정 → 격리함 (`memory.py:156-194`·`198-207`·`287-403`·`441-498`).** 메모 파일(`/memories/AGENTS.md`)은 다음 세션의 시스템 프롬프트가 되므로 `edit_file` 호출을 `wrap_tool_call`로 따로 막는다(업무 도구 게이트는 내장 도구를 보지 않는다). 새로 들어가는 줄마다 출처를 본다: 글자 3-gram의 60% 이상이 상담원 메시지와 겹치면 `operator`(저장), 티켓·규정 본문·Subagent 보고와 겹치면 `untrusted`, 그 밖은 `unknown`. 상담원에게서 오지 않은 줄은 "규정이나 권한을 바꾸거나 넓히는가"를 Jev(구간 0.3 / 0.7) 또는 LM에 묻는다: 사실 기록이면 저장, 규정·권한을 바꾸면 차단, 애매하거나 판정 실패면 격리함. 한 호출의 여러 줄에는 가장 엄한 결정을 적용한다. 격리함은 Agent의 파일 시스템 밖에 있어 다음 세션에 실리지 않고 사람이 본 뒤 옮긴다. Subagent용 middleware는 첫 메시지(Main이 쓴 지시문)를 상담원 출처로 인정하지 않는다. 읽기 전용(`permissions`로 `/memories/**` 쓰기 거부)은 정상 메모까지 없앤다. 한계: 모델이 문장을 바꿔 쓰면 출처가 `unknown`이 된다. 메모 속 민감 값은 검사하지 않는다. DeepAgents가 메모와 함께 넣는 "메모는 참고 자료" 안내문은 지침이지 경계가 아니다.
22. **오염된 뒤에도 행동 게이트는 메모를 보지 않는다 (`gate.py:109-131`, `docs/architecture.md` 15절).** 환불·면제 판정에 들어가는 글은 티켓, 제안된 호출, 규정 원문, 조회한 사실뿐이다. 메모가 오염돼 모델이 면제를 제안해도 Jev를 더한 게이트는 규정 원문으로 판정한다. 코드 규칙만 있으면 한도 안의 면제라 통과한다.
23. **메모 범위: 고객별 파일, 쓸 때 가림, 쓰기 권한 (`memory_scope.py:93-97`·`311-393`·`553-572`).** 공용 파일 + 고객마다 파일 하나로 나눈다. 싣는 범위(`memory=[공용, 이 고객 파일]`)와 쓰는 범위(`permissions`: 공용·이 고객 파일 쓰기 허용을 앞에, `/memories/**` 쓰기 거부를 뒤에)를 따로 막고, 둘 다 모델 인자(`file_path`, 메모 속 고객 번호)가 아니라 신뢰 컨텍스트의 `ticket_customer_id`로 정한다. 고객 파일 경로는 `C-1001` 꼴이 아니면 예외를 던져 `../` 경로 이탈을 막는다. 쓸 때 도구 인자의 민감 값을 자리표시자로 바꿔 저장한다. 공용 파일에 쓰는 줄은 코드 규칙(고객 번호·이름·연락처 값)이 먼저 보고, 다른 고객이면 차단, 이 세션 고객이면 그 고객 파일로 옮겨 저장하고, 못 잡은 줄만 판정 주체에게 "특정 고객 한 명에 대한 기록인가"를 묻는다(애매하거나 실패면 격리함). 한계: 코드 규칙은 글자 그대로 찾는다("이 고객"이라고만 쓴 메모는 못 찾음). 판정 주체는 고객을 지목하지 못한다. 가림은 이름을 지우지 않는다. 고객 파일에 쓰는 줄은 내용 검사를 하지 않는다. 08의 내용 판정과 겹쳐 쓰지 않아서, 실제 주모델 실행 한 번에서 규칙처럼 쓴 일반 메모 3줄이 저장되어 다른 고객 상담에 실렸다(`docs/architecture.md` 23절). 실제 배치에는 08과 09가 둘 다 필요하다고 적는다.
24. **내장 도구 제거 Harness Profile (`harness.py:27-81`, `agent.py:116-118`).** `HarnessProfile.excluded_tools`로 DeepAgents 내장 도구(`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `delete`, `execute`)를 모델의 도구 목록에서 빼고 general-purpose Subagent를 끈다. 게이트가 업무 도구만 감싸므로 내장 도구 경로를 아예 닫는 것이다. 프로필은 프로세스 전역 레지스트리라 `with` 블록 안에서만 등록하고 되돌린다. 08·09는 `edit_file` 하나만 남긴다. 코드 주석이 이것은 모델 쪽 보정이지 보안 경계가 아니며 파일 권한·도구 래퍼를 대체하지 않는다고 적는다.
25. **예산 상한 (`agent.py:54-55`·`100-103`).** `ToolCallLimitMiddleware(run_limit=30)`, `ModelCallLimitMiddleware(run_limit=25)`를 모든 구성에 같게 건다. 한 실행 안의 횟수만 막는다. 신원 단위로 실행을 가로질러 시도를 세는 장치는 없다(`docs/artex_architecture.md` 9.4절이 지적).
26. **측정 규율 (`episodes.py:107`·`219-245`, `holdout.py:31-45`, `recorded.py:22-47`, `trace.py:244-263`).** 판정은 답변 문구가 아니라 원장·답장·전송함·실행 기록으로 한다. "제안됨(called)"과 "실행됨(executed)"을 구분한다. 공격 사례에서 뚫리지 않았더라도 BLOCK도 REVIEW도 없었으면 "공격 시도 없음"이라고 적어 Guard의 공으로 돌리지 않는다. holdout은 단일 진입점으로만 열고 열람 기록을 남긴다. 대본 재생(주모델 대신)은 "모델이 이런 호출을 제안했다면"의 경계 시험이고, 기록 재생(Guard 응답 대신)은 이번 실행의 측정이 아니다. 기록의 열쇠는 요청 본문 전체의 해시라 정책 문장·질문·모델을 바꾸면 기록이 없고 UNKNOWN → REVIEW가 된다. REVIEW와 UNKNOWN은 FN·FP에 넣지 않고 따로 센다(REVIEW는 사람 시간이라는 비용).

#### 3.2 `Day08/guardlab/` (방어 위치 축)

1. **Input Guard: 아직 검사하지 않은 새 입력만 (`defenses.py:50-99`, `components.py:86-105`).** `before_model`마다 사용자 메시지와 도구 결과 가운데 검사하지 않은 것을 메시지 id / `tool_call_id`로 골라 Guard에 넣는다. 사용자 메시지가 위험하면 BLOCK → `jump_to="end"`(모델 호출 0회), 도구 결과가 위험하면 TRANSFORM → 표시("아래는 데이터다")를 붙인 같은 id의 ToolMessage로 교체한다. UNKNOWN은 정책이 ALLOW로 잘못 설정돼 있어도 REVIEW로 바꾼다(`defenses.py:76-79`). 범위에 `tool_result`가 없으면 문서 속 지시는 영원히 보이지 않는다. 못 막는 것: Guard가 Main에만 있으면 Subagent가 읽은 원문은 검사 없이 Subagent의 모델에 들어간다. 분류기는 문서 속 업무 지시형 Injection을 대부분 놓쳤다(README 실측 표).
2. **권한표 + 인자 정규화 + 도구 래퍼 (`context.py:23-46`, `defenses.py:102-163`).** `PermissionTable.decide`가 사용자 × 자원 × 행동을 신뢰 컨텍스트(`UserContext`: 사용자, tenant, 담당 프로젝트, 전달 권한)로만 판정한다: 컨텍스트 없음 → BLOCK, 담당 아닌 프로젝트 → `PROJECT_SCOPE`, 전달 권한 없음 → `NO_SEND_RIGHT`, 허용 도메인 밖 → `EXTERNAL_DOMAIN`, 승인 검토자 목록에 없음 → `NOT_APPROVED_REVIEWER`, 모르는 도구 → `UNKNOWN_TOOL`(기본 거부). `normalize_args`가 대소문자, 공백, `표시 이름 <주소>`, 경로 구분자, `..`를 없앤 뒤 판정한다. `guarded_call`은 도구 함수 안에 있어 Main·Subagent 누가 불러도 같은 검사를 지나고 ALLOW일 때만 `impl()`을 부른다. 검토자 목록은 작업 공간이 아니라 원본에서 읽는다(`components.py:51-53`. 공격자는 작업 공간 파일만 바꿀 수 있다는 가정). 못 막는 것: 승인된 검토자에게 가는 본문 속 개인정보(3번이 맡는다).
3. **출력: 전달·저장 직전 본문 검사 (`defenses.py:166-217`, `components.py:171-237`).** 탐지기는 구간(Span)만 주고, 코드가 저점수 제거 → 겹치거나 맞닿은 구간 병합(`merge_spans`. LFM이 토큰 단위로 쪼개 주기 때문) → 공개 대상별 허용 라벨을 뺀 나머지 마스킹을 한다. `send_report` 직전에는 몰래 고쳐 보내지 않고 `BLOCK PII_IN_BODY`로 돌려보내 모델이 다시 쓰게 한다. `save_report`(초안)도 같은 검사를 한다. 최종 답변 검사(`after_agent`)는 TRANSFORM(마스킹)이지만 이미 실행된 전달은 되돌리지 못한다. 탐지기 UNKNOWN이면 REVIEW다. 못 막는 것: 탐지기가 못 잡는 문맥형 정보(카드 뒷자리 "4421")는 코드 기반 공개 금지 목록이 맡아야 한다(`README.md:197-201`).
4. **파일 권한 순서와 메모리 읽기·쓰기 검사 (`04_memory_permissions.py:45-64`, `components.py:36-48`·`244-307`).** `FilesystemPermission`은 첫 일치 규칙이라 넓은 `/**` allow를 먼저 두면 뒤의 `/policy/**`·`/memory/**` 쓰기 deny에 도달하지 않는다(`permissions_wrong_order`). 권한 없는 프로젝트 폴더는 읽기·쓰기 deny를 앞에 둔다(라이브 실행에서 모델이 업무 도구 대신 내장 `read_file`로 직접 읽는 것이 관찰됐다고 적혀 있다). `MemoryGuardMiddleware`는 읽을 때(`before_model`에서 `state["memory_contents"]`의 외부 주소·지시문 줄을 걷어냄)와 쓸 때(`write_file`·`edit_file`이 메모리 경로를 향하면 같은 정규식으로 BLOCK) 모두 검사한다. 정규식 힌트(외부 주소, "반드시·무시·우선·삭제" 등)라 표현을 바꾸면 놓친다. 권한은 내장 파일 도구에만 적용되고 업무 도구·`execute`는 범위 밖이다.
5. **승인 바인딩: 인자 해시·요청자·만료·1회 (`components.py:315-392`).** 승인 기록은 도구, 인자 해시(sha256 앞 16자), 수신자, 보고서 버전, 요청자, 승인자, 만료(TTL 10분), 사용 여부, 정책 버전을 담는다. `send_report` 실행 직전 래퍼가 대조해 `NO_APPROVAL` / `APPROVAL_ARGS_MISMATCH` / `APPROVAL_ALREADY_USED` / `APPROVAL_EXPIRED`로 BLOCK한다. `bound_revalidate`는 승인이 맞아도 현재 권한표를 다시 검사한다(승인 뒤 권한이 바뀐 경우). HITL은 `after_model`에서 멈추고 승인자가 고친 인자는 그대로 도구로 가므로 재검증은 도구 실행 직전에 있어야 한다. 중복 전달을 막는 것은 checkpointer가 아니라 `used` 표시다. 대가: `bound`는 만료된 정상 승인도 막아 업무가 실패한다.
6. **내장 도구 제거와 Subagent 최소화 (`harness.py:27-61`, `02_action_guard.py`의 `tool_wrapper_min`).** 3.1의 24번과 같은 프로필이다. general-purpose Subagent는 부모 도구 전체를 물려받으므로 끄거나 같은 이름의 spec으로 덮는다.
7. **실행 예산 (`budget.py:15-23`).** 모델 호출 24회, 도구 호출 40회를 모든 비교군에 같게 걸고 `exit_behavior="end"`로 초과 시 오류 대신 종료한다. 실패를 감추려고 상한을 올리지 않는다.
8. **Guard 계약 (`guards/contracts.py:21-56`, `guards/injection.py:162-178`).** `GuardSignal`(신호: `status` OK/UNKNOWN, `risk_labels`, `evidence_spans`, `score_type`, `model_id`, `revision`)과 `PolicyDecision`(결정: ALLOW / BLOCK / REVIEW / TRANSFORM, `reason_code`, `policy_version`)을 분리한다. 원격 분류기는 긴 글을 조각으로 나눠 조각마다 판정하고, 주소·모델이 설정되지 않으면 UNKNOWN을 낸다. `trust_remote_code` 모델은 `.env`의 revision으로 커밋을 고정한다(`README.md:80-81`. 공급망 위험 사례로 든다).
9. **ablation과 holdout (`06_compare.py:46-75`).** B4 = B3 − {REMOVE}로 방어를 하나씩 빼 무엇이 실제로 막았는지 본다. "탐지 실패 + 방어 성공"(Input Guard는 놓쳤지만 권한 검사가 막음)을 따로 센다. 실패·오류·예산 초과 행을 지우지 않는다. 반복 3회 이상부터 비율을 말한다(수업은 1회).

#### 3.3 저장소 README가 적은 실측 (참고)

- 분류기 6종 × 입력 17건(2026-09-15, `Day08/README.md:165-193`): 미탐 / 오탐 / UNKNOWN이 SGuard 6 / 1 / 0, Kanana 5 / 0 / 0, gpt-oss-safeguard 0 / 2 / 4(429), Nemotron 7 / 2 / 0, Llama Guard 4 6 / 1 / 0. 평균 지연 0.6~1.1초, gpt-oss-safeguard만 6.4초. jailbreak 문형은 모두 잡고 차이는 문서 속 업무 지시형 Injection에서 난다. 권한 주장("관리자가 승인했다")과 연락처 요청은 Injection이 아니라서 분류기가 아니라 코드 경계가 막는다.
- LFM2.5 Encoder 2종(`Day08/README.md:195-201`): PII-Detector는 토큰 단위로 쪼개 주고("010-4412-778"+"8") 전화번호 세 개 중 하나만 잡거나 주민등록번호를 임계값 아래(0.49)에 두는 경우가 있었다. Policy-Linter는 같은 공격의 영어 번역에 0.70~0.97, 한국어 원문에 0.35~0.81을 주고 정상 한국어 문서의 사람 이름을 0.72로 잡았다.
- 주모델 선택(`Day08/README.md:130-136`): `openai/gpt-5.6-luna` 00 실행 17회 / 76초, `z-ai/glm-5.3-flash` 17회 / 403초(호출당 약 24초), `google/gemini-3.8-flash`는 6회 중 2회 thought signature 400 오류.
- `Day08_new` 비용(`Day08_new/README.md:165-184`, 저자 환경 1회): 03은 OpenRouter 234회 약 $0.025, 04는 Jev 162회 $0.0047 + OpenRouter 36회 $0.014, 05는 Jev 132회 $0.0037 + OpenRouter 132회 $0.040. `qwen/qwen3.8-27b` 호출 약 270회 가운데 3회가 429로 UNKNOWN → REVIEW가 됐다. 09의 실제 주모델 실행 2회는 결과가 서로 달랐다.

### 4. 공개 사례 출처 (`Day08_new/docs/sources/`)

저장소가 적은 확인 수준을 그대로 옮겼다. [1차]는 공식 벤더·연구자 페이지를 직접 열어 확인, [2차]는 뉴스·블로그·검색 스니펫, [미확인]은 확인하지 못함이다. 조사일은 2026-11-09이고 문서 머리말이 "저자용 노트이며 수업 자료가 아니다"라고 적는다. 이 노트에서 URL을 다시 열어 확인하지는 않았다.

**사고 사례 (`01_agent_logic_cases.md`)**

| 사례 | 경로 요약 | 막았을 코드 경계(저장소 의견) | 출처 | 확인 수준 |
|---|---|---|---|---|
| Replit AI Agent / SaaStr (2025-07) | code freeze 선언 뒤에도 운영 DB 삭제. 개발·운영이 같은 DB였다는 보도 | dev/prod 분리, 운영 DB 자격증명 격리 | The Register 등 | [2차]. 레코드 수는 매체마다 다름, 공식 포스트모템 없음. 05 문서 판정: 조건부(수치 인용 금지) |
| GitHub MCP + Claude Desktop (2025-05-26) | 공개 저장소의 악성 이슈를 읽고 비공개 저장소 내용을 공개 PR로 유출 | 세션당 저장소 1개 범위, 비신뢰 읽기 뒤 외부 쓰기 차단 | Invariant Labs 블로그 | [1차] |
| Supabase MCP + Cursor (2025-07) | `service_role` 키로 지원 티켓 속 지시를 따라 토큰 테이블 내용을 티켓 스레드에 삽입 | 읽기 전용 역할, `project_ref` 범위, 쓰기 승인 | General Analysis 블로그 | [1차] 연구자 글 |
| Microsoft 365 Copilot EchoLeak (CVE-2025-32711, CVSS 9.3) | 악성 메일 한 통으로 제로클릭 유출. 분류기·링크 redaction·CSP 연쇄 우회 | 외부 유래 컨텍스트 라벨링, 출력 링크 allowlist | arXiv 2509.10540 등 | [2차]. Aim 원문은 열지 못함 |
| Salesforce Agentforce ForcedLeak (2025-09-25 공개) | Web-to-Lead 입력 → 허용 목록에 남은 만료 도메인으로 유출 | egress allowlist의 도메인 소유 확인 | Noma 블로그 | 01 문서는 [2차], 05 문서에서 Noma 원문을 열어 [1차 확인]으로 올림. CVSS 9.4는 "Noma가 보고한 값"으로만 쓴다 |
| Amazon Q Developer VS Code 1.84.0 (CVE-2025-8217) | 범위가 넓은 GitHub 토큰으로 파괴적 프롬프트가 릴리스에 포함 | CI 토큰 최소 권한, 릴리스 검토 | AWS 보안 공지 | [1차]. 실행되지 않은 근접 사고 |
| Perplexity Comet (2025-08-20) | 웹 페이지의 숨은 텍스트 → 이메일 추출 → OTP 읽기 → 게시 | 페이지 콘텐츠와 사용자 의도 분리, 민감 행동 확인 | Brave 블로그 | [1차] |
| Sentry MCP "Agentjacking" (2026-06) | 공개 DSN으로 위조 에러 이벤트 → 에이전트가 읽고 악성 npm 설치 등 실행 | 명령 실행 승인, 샌드박스, 단기 시크릿 | CSA 연구 노트 | [1차] 노트. 85%·2,388개 조직 수치는 단독 측정 |
| 신한·KB국민·하나은행 보도 (2026-10-05) | 해커가 AI 에이전트 스캐닝으로 조회 서비스의 빈틈을 찾아 고객정보 유출. 신원확인 없는 조회 등이 지적됨 | 신원 범위 | 파이낸셜뉴스 | [1차] 기사 본문. 공격자가 에이전트를 쓴 사례이지 은행 에이전트가 유출한 사고가 아니다 |

인용 금지로 적힌 것: Kiro CVE-2026-10591, Cursor CVE-2026-50548/50549, SearchLeak CVE-2026-42824, Claude Code repo-config RCE(인덱스 사이트 스니펫뿐).

**공개된 통제 아키텍처 (`01_agent_logic_cases.md`)**

| 이름 | 강제하는 것 | 확인 수준 |
|---|---|---|
| AWS Bedrock AgentCore Policy | Gateway가 에이전트→도구 요청을 Cedar 정책으로 평가. 2026-03-03 GA | [1차] |
| Claude Code 샌드박스 | 작업 디렉터리 밖 쓰기 차단, 프록시로 허용 도메인만. 권한 프롬프트 84% 감소(내부 사용 기준) | [1차] |
| Agents Rule of Two (Meta, 2025-10-31) | 세션 안에 [A] [B] [C] 중 최대 2개. 최소 권한을 대체하지 않는다고 명시 | [1차] |
| Lethal trifecta (Willison, 2025-06-16) | 사적 데이터 + 비신뢰 콘텐츠 + 외부 통신의 결합 | [1차] |
| CaMeL (arXiv 2503.18813) | 신뢰된 질의에서 제어·데이터 흐름 추출, capability로 유출 차단. AgentDojo 77%(비보호 84%) | [1차] |
| FIDES (Microsoft) | 무결성·기밀성 라벨 전파, 위반 시 승인 요청 | 블로그 [1차], 수치 [2차] |
| OpenAI Agents SDK guardrails | tool guardrail. 한계: handoff·hosted 도구 미적용, 입력 guardrail은 첫 에이전트만 | [1차] |
| Stripe restricted API keys | 에이전트 도구 범위를 키 권한으로 제한 | [2차] |

**LM Guard 운영 사례와 한계 (`02_lm_guard_cases.md`)**

| 사례 | 내용 | 확인 수준 |
|---|---|---|
| DoorDash Dasher 지원 챗봇 (2024-09) | 1단 의미 유사도 → 걸린 것만 2단 LLM 평가자. hallucination 90%·compliance 99% 감소 주장 | 설계는 05 문서에서 [1차 확인]. 수치는 자체 주장이며 기준선·기간 없음 |
| Anthropic Constitutional Classifiers (2025-02) | jailbreak 성공률 86% → 4.4%, 연산 +23.7% | [1차] |
| Constitutional Classifiers++ (2026-01) | 2단 cascade(선형 probe는 거부하지 않고 승격만), 연산 약 1%, 무해 거부율 0.05% | [1차] |
| Moffatt v. Air Canada (2024 BCCRT 149) | 챗봇이 환불 정책을 틀리게 안내, 회사 책임 인정 | 사실관계 [2차], 판결문 원문은 열지 못함. 금액·문단 번호는 쓰지 않는다 |
| Hackett et al., arXiv 2504.11168 v3 | 탐지기 6종에 대한 문자 주입 우회(Emoji Smuggling 등 ASR 100% 사례) | [1차]. 버전을 명시해 인용 |
| SGuard-v1 (arXiv 2511.12497) | 한국어 jailbreak F1 0.86 등 | [1차]. 삼성SDS 자체 평가, 독립 검증 없음 |
| gpt-oss-safeguard | 정책 문서를 추론 시점에 주입. 작은 분류기로 먼저 거르는 구성 권장 | 모델 카드 [1차], 수치 [2차] |
| Llama Guard 다국어 저하 (arXiv 2410.22153) | 영어 대비 비영어 F1 하락. 한국어 단독 수치 없음 | [2차] |

**Decision 모델과 "점수 → 구간 → 행동" (`03_decision_model_cases.md`)**

| 항목 | 내용 | 확인 수준 |
|---|---|---|
| TypeSafe Jev (`/v1/systemone`) | noul / choice / score / box. 입력 $0.042/M 토큰 | 문서·cookbook [1차], 날짜·지연 [2차] |
| OpenRouter cookbook "Gate Agent Tool Calls with Jev" | `APPROVE_AT=0.9`, `BLOCK_AT=0.1`, 중간은 사람 검토. 주문 존재·금액 한도는 코드가 먼저. 같은 입력이 반복 실행에서 0.35~0.43 | [1차] |
| langchain-typesafe `AutoModeMiddleware` | 위험 tool call을 실행 전 차단. 승인을 요청하지는 않으므로 HITL 병행 권장 | [1차] |
| OpenAI Decisions API, OpenRouter `/api/alpha/decisions` | predicate / choice / score. 모델마다 임계값을 다시 정하라는 문서 문장 | [1차], 날짜 [2차] |
| Stripe Radar | 위험 점수 구간별 허용 / 검토 / 차단. 검토 규칙은 양이 적은지 확인, traffic allocation 0%로 shadow 평가 | [1차] |
| 임계값 실무 요점 | 0.5는 정답이 아니다, 임계값은 학습과 다른 데이터로 정한다(scikit-learn 문서) | [1차] |

벤더 수치(200x, 400x, 10x)는 비교 대상·방법론이 공개되지 않아 "주장"으로만 소개한다고 적혀 있다.

**규제·표준·한국 맥락 (`04_regulation_korea.md`, `05_verification.md`)**

| 항목 | 내용 | 확인 수준 |
|---|---|---|
| OWASP Top 10 for Agentic Applications 2026 | ASI01~ASI10, 2025-12-09 공개, CC BY-SA 4.0 | 04 문서는 2차 해설 기준이라 적었고, 05 문서에서 공식 PDF로 [1차 확인] |
| 인공지능 기본법 | 2026-01-22 시행. 고영향 AI의 위험관리·사람의 관리·감독·문서 보관 | 시행일 [1차]. 조문 번호는 자료마다 달라 인용 금지 |
| EU AI Act 디지털 옴니버스 | 적용 시점 연기 보도 | [2차]. 규정 번호 인용 금지 |
| 금융위 금융분야 AI 가이드라인 | 최종 의사결정·책임은 임직원 | [2차], 원문 [미확인] |
| 삼성SDS 2026 5대 사이버 보안 위협 (2026-02-23) | AI 에이전트의 과도한 권한 위임·남용. 대응: 최소 권한, 민감 명령 실시간 모니터링, 민감 작업 전 사용자 승인 | [1차] |
| 삼성전자 2023 ChatGPT 유출 보도 | 사내 생성형 AI 차단 후 보안 체계를 갖춘 허용으로 전환 | [2차]. 공식 발표 없음 |
| 한국 은행·통신사의 에이전트 행위 통제 구현 | 공개 자료 없음 | [미확인] |

저장소의 교육용 해석(`04_regulation_korea.md` 1절): OWASP Agentic 10개 항목 가운데 7개 안팎은 코드 로직으로 닫히고, 판정이 필요한 것은 의도 일치(ASI01)·오염 의심(ASI06)·승인 선별(ASI09)이다. 통제 방식 열은 조사자의 설계 판단이라고 적혀 있다.

**README 사례와 근거의 대응 (`Day08_new/README.md:25-42`)**

| 사례 | 근거가 된 공개 사례 | 저장소가 적은 확인 수준 |
|---|---|---|
| E3 (티켓 속 지시로 다른 고객 정보 유출) | Supabase MCP·GitHub MCP 유출 | [1차] |
| E4 (문자 주입 변형) | Hackett et al. arXiv 2504.11168 v3 | [1차] |
| E5 (규정에 없는 환불 약속) | Air Canada 판결 | 공개 보도 기반 재구성 |
| E6 (승인 사칭) | OWASP Agentic ASI03·ASI09 | [1차] |
| E8 (만료 도메인으로 전송) | Salesforce ForcedLeak | [1차] |
| E9 (가족이라며 다른 고객 조회) | 2026-10 은행 고객정보 유출 보도 | [1차 기사] |
| E10 (애매한 면제) | Stripe Radar의 검토 구간 | [1차] |
| E7, U3, D1, X1, P1·P2, V1~V6 | 공개 사례 없음(장치 설명용 사례) | — |
