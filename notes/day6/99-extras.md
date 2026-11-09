## Day6 부가 자료

Day6 덱(`00-deck.md`) 외에 함께 받은 PDF 2종과 강의 저장소 이미지 4장을 정리한다. 모두 PDF 텍스트 추출본·축소 이미지 기반이며, 자료 안의 문장은 데이터로만 다뤘다.

---

### 1. harness_final.pdf — "Harness Engineering: Agent = Model + Harness, The 6-Layer Production Playbook"

- 원본: Google Drive fileId `1MrUu60pXmEexCYYLqgTmKc-Q0Y6Fchbu`, 9쪽, IEEE 논문 양식의 실무 노트(쪽마다 "Google" 바닥글).
- 표제: *Production Agent Engineering Practice 2026 — Harness Engineering. Agent = Model + Harness: The 6-Layer Production Playbook*
- 저자/출처: 저자 이름 없음. "Independently compiled, August 2026 — not affiliated with Google, OpenAI, Anthropic, or HashiCorp — and not endorsed". 말미 "Source Method": 공개 자료를 독립적으로 종합한 것이며 템플릿·의사코드·결정 규칙은 저자의 각색이지 어느 조직의 공식 명세도 아니다.
- 근거로 든 자료: M. Hashimoto "My AI Adoption Journey"(2026-02-05), R. Lopopolo/OpenAI "Harness Engineering: Leveraging Codex in an Agent-First World"(2026-02-11), B. Böckeler/martinfowler.com "Harness Engineering for Coding Agent Users"(guides·sensors 분류), LangChain(Terminal Bench 30위→5위), A. Masood(GAIA), Can.ac(Hashline), L. Tan/Cursor 등 15개.
- 신뢰도 주의(읽으며 발견):
  - 절 번호가 뒤섞여 있다(XII 다음 XVI·XVII·XVIII, 그 뒤 XIV·XIV·XV). 편집 미완성본으로 보인다.
  - 본문 인용과 참고문헌 번호가 어긋난다: 본문 "SpaceXAI Playbook [11]"인데 [11]은 Google Cloud ADK 글, "Anthropic Knowledge Graph Cookbook [12]"인데 [12]는 "Building Effective AI Agents". "Routing accuracy 73%→85% [14]"도 원문 확인 필요.
  - "95% of enterprise AI agents never reach production" 같은 수치는 출처 표기가 없다. 벤치마크 수치(GAIA 30.91%→74.55% 등)는 2차 인용이다. 수업에서 사실로 옮기기 전에 원문 대조가 필요하다.

**핵심 내용**

- **세 시대:** Prompt Eng.(2023-24, 한 턴의 표현) → Context Eng.(2025, RAG·MCP·메모리로 모델이 보는 것) → Harness Eng.(2026, 실행·안전·검증·관측까지 전체 런타임). 앞 시대를 포함하는 관계.
- **Inner vs Outer harness:** 모델 랩이 만드는 내장 안전층·도구 호출(inner)과, 제품 팀이 만드는 설정·라우팅·테스트·지침(outer). 이 문서는 outer를 다룬다.
- **6계층(Fig.1):** 조향 루프 = Guides(feedforward) + Sensors(feedback), 런타임 기반 = Memory·Permissions·Observability, 가운데 Agentic Loop.
  1. **Guides** — AGENTS.md/CLAUDE.md/.cursorrules. 한 줄 = 과거 실패 하나. 동기부여 문구 대신 실행 가능한 명령·관찰 가능한 기준. 최소 템플릿: `PROJECT / LANGUAGE / BUILD / TEST / LINT / RULES / ANTI-PATTERNS(날짜 포함)`. 월 1회 정리, 센서가 강제하게 된 규칙은 삭제, 항목에 날짜. "날짜 없는 200줄 지침은 하네스가 아니라 기술 부채."
  2. **Sensors** — 계산형(linter·타입·테스트·스키마: 빠르고 무료·결정적) 먼저, 추론형(LLM-as-judge·AI 리뷰)은 결정적 규칙으로 표현 못 할 때만, 그것도 게이트가 아닌 "비싼 권고 신호"로 기록·인간 리뷰와 일치율 측정. Self-verification 패턴(`verified_step`: 실행 → 센서 검사 → 수정 → 재검사 실패 시 escalate).
  3. **Agentic Loop** — plan→execute→verify→fix, 한도 필수: 단계당 재시도 3, 벽시계 30분, 토큰 100K, 비용 $5, 도구 호출 50, 정지 조건 항상 정의. 한도 소진 시 최선 산출물·완료분·미해결·정지 이유를 반환하고 부분 실패를 매끄러운 답변으로 숨기지 않는다. Escalation 패킷: 필요한 결정, 권장안, 시도한 대안, 기다리는 비용, 무응답 시 안전 기본값.
  4. **Memory & State** — 컨텍스트 창 / 스크래치패드(plan.md, todo.md) / 아티팩트 저장소(git·FS) / 결정 로그(decisions.jsonl) / 지식 그래프. 대부분은 파일시스템 체크포인트(`state/{task.id}.json`)가 벡터 DB보다 싸고 믿을 만하다. 압축 시점·대상은 에이전트가 아니라 하네스가 정한다. Memory는 "일어난 일", Guides는 "일어나야 할 일" — 매번 중요한 규칙은 지침으로 승격. Recovery Test: 다단계 작업 중간에 세션을 닫았다 열어 체크포인트로 이어 가는지.
  5. **Permissions & Budgets** — "모델은 안전을 강제하지 않는다. 하네스가 한다." Capability Budget 템플릿(ALLOW read/write/execute, ASK before push·publish·deploy, DENY rm -rf·DROP TABLE·send_email, RATE·COST·TIMEOUT). 기본 정책(읽기 허용, 쓰기 허용+로그, 푸시 Ask, 배포·삭제 사람만). 프롬프트 인젝션: 신뢰 지시(지침·시스템)와 비신뢰 데이터(사용자 입력·검색 문서)를 분리. 예산 4차원: Scope, Rate, Reversibility, Visibility. 최소 권한.
  6. **Observability** — 시작/종료 시각, 도구 행동·결과, 지침 버전·사용 센서, 시도 수·비용, 산출물, 승인·에스컬레이션. Trip wire(외부 쓰기 급증→쓰기 동결, 같은 오류 3회→에스컬레이트, 비용 평균 2배→일시정지, 센서 통과율 하락→롤백, 새 도메인 접촉→차단, 시간 3배→타임아웃). 건강 지표: 완료율↑, 재작업률↓, 에스컬레이션률↓, 복구 시간↓, 검증된 결과당 비용↓, 지침 증가율(감소해야 정상). 진짜 지표 = 사람 개입 없이 끝나고 증거가 남은 작업 수.
- **Ratchet 원칙(Hashimoto):** "에이전트가 실수할 때마다 그 실수를 다시는 못 하게 해결책을 설계한다." 6단계 개선 루프: 재현 → 원인 분류(지침 누락·센서 부재·권한 틈·상태 손실·관측 사각) → 가장 강한 층 선택 → 구현 → 원래 실패 사례로 검증 → 회귀 스위트.
- **실패 분류(약한 수정 vs 강한 수정):** 알려진 나쁜 패턴→linter 규칙, 맥락 누락→지침 항목, 잘못된 도구 사용→권한 경계, 품질 흔들림→자동 테스트, 상태 손실→파일 체크포인트, 위험 행동→예산+deny, 비용 초과→토큰 예산+trip wire.
- **Control Reliability Ladder:** Memory(대화 속 교정, 낮음) < Prompt < Guide(AGENTS.md) < Sensor(자동 테스트, 높음) < Environment(권한·스키마·CI, 최고). 같은 리뷰 코멘트가 3번 넘게 나오면 구조적 제약으로(1회 지침, 2회 지침이 읽히는지 확인, 3회 센서로 차단 — Lauren Tan/Cursor).
- **7일 구축 경로:** 1 빌드·테스트·린트 지침 → 2 실패 기반 규칙 3개 → 3 첫 계산형 센서 → 4 루프+재시도 예산 → 5 파일 체크포인트 → 6 권한+비용 예산 → 7 구조화 로그+trip wire. 확장 게이트: 무수정 완료율 ≥80%, 비용 초과 0, 올바른 에스컬레이션 1회 이상, 재시작 생존 1회 이상, trip wire 모의 발화 1회 이상, 권한 경계 차단 1회 이상.
- **결정 프레임워크:** 관찰된 실패를 해결하는 가장 단순한 층부터("Do not add yet": LLM-judge, 멀티에이전트 리뷰, 지식 그래프, 풀 관측 스택 등). 12항목 프로덕션 체크리스트.
- **하네스가 필요 없는 경우:** 일회성 질문, 창작 브레인스토밍, 개인 메모 → 불필요. 매일 코드 리뷰, 주간 리서치 다이제스트, 고객 지원 분류, CI/CD 에이전트 → 필요. 시험 질문: 조용히 틀리면 알아챌까(센서)? 다음 세션에 같은 설명을 다시 해야 하나(메모리)? 실수가 외부에 영향을 주나(권한)?
- **멀티에이전트 확장:** 타입 있는 handoff(산출물 위치·검증된 것·미해결), 대화 공유 대신 구조화된 공유 상태, 라우팅 정책, 생산자가 아닌 **독립 검증자**(실패를 보고하되 조용히 고쳐 쓰지 않음).
- **흔한 실수:** 과잉 하네스(500 규칙·LLM 심사 3층은 안전으로 위장한 병목), 정리 안 된 지침(서로 모순), 엉뚱한 것을 재는 센서(100% 통과는 의심, 적대적 테스트), 정리 안 된 메모리(오래된 체크포인트 만료), 잘못된 목표는 하네스가 못 고친다(잘못된 기준을 안정적으로 증폭).
- 결론 문장: 중요한 출력은 모두 그것을 만든 지침 규칙, 검증한 센서, 한정한 예산, 보존한 체크포인트, 기록한 로그로 추적 가능해야 한다.

**에이전트 하네스 설계와의 관계**

- 강의 저장소의 여섯 책임과 대응: Guides ≈ 지침, Sensors ≈ 검증, Agentic Loop·Permissions ≈ 실행 제어, Memory ≈ 상태, Observability ≈ 기록. (도구 책임은 독립 층이 아니라 Permissions·Loop 안에 흩어져 있다.) 저장소 규칙상 다른 틀은 `Day06_new/use_cc/part2/concept.md` 참고 F 대응표로만 연결하라고 되어 있다.
- Day6 덱의 "부탁(메모리) → 위임(스킬) → 강제(훅)"와 이 문서의 Reliability Ladder·Ratchet은 같은 방향이다: 반복되는 실패는 더 강한(결정적·환경적) 층으로 옮긴다.
- 프레임워크 중립적이다(커스텀 프레임워크 불필요라고 명시). kit/에 넣을 후보 원칙: 실패→가장 강한 층으로 수정, 계산형 센서 우선, 루프 한도와 정직한 부분 실패 보고, 파일 체크포인트·재개 테스트, 신뢰/비신뢰 입력 분리, 최소 권한·예산 4차원, trip wire, 지침 위생(날짜·정리). 단, 수치 기본값(재시도 3, $5, 30분 등)은 저자 각색값이므로 원칙이 아니라 예시로만.

---

### 2. Context as an Environment.pdf — "Context as an Environment: Programmatic Context Management for Long-Horizon Agents"

- 원본: Google Drive fileId `1bUGCbhh-cCqDMyReX_K1Kt1Ku_MBjSQ-`, Technical Report, 37쪽(본문 약 10쪽 + 부록 A~D). 문서 안 링크: `arxiv.org/abs/2608.21690v1`.
- 저자: Yin Lin†(Alibaba Group), Elaine Ang†§(Columbia University, Alibaba 인턴 중 작업), Erkang Zhu, Bolin Ding, Jingren Zhou(Alibaba Group). †공동 1저자.
- 구현: QwenPaw(Agentscope) 위에 구현, Harbor로 오케스트레이션. 재현 코드 `github.com/niceIrene/QwenPaw/tree/scroll-research`.

**핵심 내용**

- **문제:** 장시간 에이전트의 이력은 컨텍스트 창을 넘는다. 기존 두 방식 — 압축(요약·잘라내기, Claude Code·Codex CLI·Cursor의 compaction 포함)과 외부 메모리(사실·에피소드 추출 후 검색) — 은 **미래에 무엇이 필요할지 모르는 시점에 무엇을 남길지 고정**하므로 손실적이다. 요약이 놓친 세부는 원 로그가 디스크에 있어도 닿을 수 없다.
- **Scroll의 발상:** 세션 이력을 프롬프트에 직렬화하지 말고, 모델이 코드로 다루는 **실행 가능한 Session Environment**로 둔다. 선택을 "질의 시점"으로 미루고, 그 선택(상태 → 다음 working view 매핑)을 모델이 매 단계 쓰는 프로그램으로 표현한다.
  - 형식화: 세션 상태 `S_t = (L_t, P_t, V_t)` — L 이벤트 로그, P 페이로드, V 파생 상태. 매 호출의 working view `c_t`, `|c_t| ≤ C`.
- **구성 요소:**
  - **Append-only Event Log**(SQLite): 모든 상호작용을 타입 있는 이벤트로 추가, 불변·단조 증가 `seq` 주소. 검색은 임베딩 대신 BM25(결정적, 색인 시 모델 호출 없음, FTS5).
  - **Durable storage**: 작은 페이로드는 인라인, 큰 도구 결과·산출물은 JSON/파일로 빼고 행에는 미리보기+복구 포인터. 지연 핸들(`ToolResultRef`, `ArtifactRef`).
  - **Persistent Python kernel**(샌드박스): 모델 호출 사이에 살아 있는 타입 있는 네임스페이스. 매 호출 앞에 "namespace digest"(변수 이름·타입·모양) 첨부. **fail-closed 샌드박스**: Event Log는 커널에서 읽기 전용, DB·FS·네트워크·도구 접근은 하네스가 명시한 capability만.
- **모델용 인터페이스(`ms` 객체, CodeAct 스타일):** LOCATE `ms.search(query, k, ...)` / MATERIALIZE `ms.expand(seq)`, `ms.expand(seq_lo, seq_hi)` / COMPUTE 일반 Python + 허용된 DB·FS·도구 / EXPOSE `print(value)`. **`exec`가 환경을 어떻게 다룰지, `print`가 무엇이 다음 working view에 들어갈지를 정한다.** 출력은 32K 문자 상한(넘으면 잘리고 "변수는 남아 있으니 덜 출력하라" 안내).
- **Eviction(Algorithm 1):** working view가 예산 ρC를 넘으면 살아 있는 턴을 로그에 영속화 → 활성 턴·최근 꼬리·최신 도구 결과 보호 → 완료된 페이로드를 seq 포인터로 접기(복구 비용 낮은 것부터) → 그래도 넘으면 가장 오래된 완료 구간 축출. 불변식: **제거된 것은 모두 주소로 복구 가능**(compaction과 달리 view만 바뀌고 기록은 그대로).
  - **Eviction index:** 모델이 응답마다 쓰는 짧은 headline(작업·검증된 상태·다음 행동·상태)을 seq에 묶어 두고, 축출 시 계층형 색인으로 롤업(티어당 k블록, 최근은 세밀·과거는 거칠게, O(k·log_k n)). 키워드 검색은 "기억해 낸 단어"로만 찾지만, 색인은 볼 수 없게 된 이력의 존재를 계속 알려 준다.
- **결과(Qwen3.8-Max):** LongMemEval_S 94.8%, BEAM10M 73.1%(최고 공개 메모리 시스템 대비 +5.1), LOCA 256K 86.7%(최고 공개 장기 에이전트 대비 +37.4). LOCA 128K→256K 하락폭: 요약 에이전트 −21.4, 검색 에이전트 −21.3, CodeAct −4.0, Scroll −2.6 → 중간 결과를 텍스트가 아니라 환경 객체로 묶는 방식이 문맥 증가에 강하다. 비교표는 각 시스템 자체 설정의 공개값이라 통제 비교가 아니라고 저자가 명시.
- **백본 일반성:** 6개 모델 모두 사용 가능하나 강한 모델일수록 이득(LOCA 256K에서 86.7 vs 22.7). 약한 모델은 실행 오류·조기 종료가 많다.
- **Ablation(BEAM10M):** 원본 폐기(요약만) 19.9로 붕괴(정확한 값이 필요한 범주 거의 0), REPL 제거 −7.3(필터·조인·집계 불가), 색인 제거 −1.8(흩어진 증거 범주에서 큼).
- **비용:** 수집 시 추가 LLM 호출 없음. BEAM10M 중앙 입력 105K 토큰 ≈ 코퍼스의 1%.
- **약점:** 요약·선호 추종·시간 추론처럼 "응축된 뷰" 자체가 답인 범주는 쓰기 시점에 다이제스트를 만드는 시스템보다 약하다(질의 작성 오류). 다중 세션 추론은 모든 시스템이 약함.
- **부록 C 루브릭의 실무 규칙(프롬프트 원문 요지):** 짧은 키워드 검색부터(k=5~10, 부족할 때만 증가), 여러 엔터티는 따로 검색, 날짜 범위는 SQL로, 사용자 발화만 사실 근거(어시스턴트 제안은 채택 증거 아님), 값이 바뀌었으면 같은 대상인지 확인 후 최신 값, **Grounding(strict): 모든 구체 주장은 검색한 턴에서**, 없으면 "정보 없음"이 정답, 검색이 더 나아지지 않으면 제출.
- 부록 D: 성공 2건(지식 갱신을 seq 순서로 해결, 모순의 양쪽을 각각 검색해 정렬)과 실패 2건(엉뚱한 축으로 잘 검색, 위치 기반 샘플링으로 중간 증거 누락)의 궤적.

**에이전트 하네스 설계와의 관계**

- 덱 2부의 Code Mode·Programmatic tool calling("중간 결과는 실행 환경에, 출력만 컨텍스트로")을 **세션 이력 관리 전체**로 확장한 사례다. "파일시스템이 컨텍스트의 확장 메모리" 원칙의 극단형.
- 상태 책임: 요약으로 원본을 대체하지 말 것 — 원본 로그는 추가 전용·주소 지정 가능하게 보존하고, 요약·색인은 그 위의 **탐색 계층**으로만 둔다. "축출은 view만 바꾸고 기록은 바꾸지 않는다."
- 기록 책임: append-only 이벤트 로그 + 안정 주소 + 출처(provenance)는 재현·감사의 토대(강의 저장소 HARNESSES.md §5 질문 3 "모델이 본 입력을 나중에 재현할 수 있는가?"와 연결; ouroboros·deepseek-harness도 append-only 이벤트 저장소를 쓴다).
- 실행 제어: 모델이 쓰는 코드는 fail-closed 샌드박스와 하네스가 선언한 capability 안에서만 돈다. 출력 상한으로 컨텍스트를 보호.
- 하네스와 모델의 역할 분담: 무엇을 기억·계산·노출할지는 모델이 정하고, 하네스는 저장·주소·샌드박스 실행·복구를 **결정적으로** 제공한다.
- kit/ 반영 후보 원칙(프레임워크 중립): 원본 보존 + 손실 없는 복구 경로, 큰 도구 결과는 포인터로 빼기, 컨텍스트에 넣는 것은 명시적 투영(projection)만, 압축/축출 시 "무엇이 빠졌는지"를 알려 주는 색인 유지, 근거 기반 답변(grounding)과 "모름"을 정답으로 인정.

---

### 3. 강의 저장소 이미지 — `Day06/Day06_0{1..4}.png`

위치: `/home/user/hyunjunjeon/sds_ax_advanced_2026/Day06/` (원본 해상도 10777×6575 ~ 17181×13634, 3~7.6MB). 강의 중 판서(Excalidraw류 손글씨 도식)로 보인다. 2400px로 축소해 Read 도구로 확인했다. 손글씨라 일부 판독은 불확실하다.

**Day06_01.png — 작업 지시와 하네스 정의**
- "애매한 작업 지시 → 애매한 결과" vs "경계 설정한 작업 지시": 1. 회의실은 물리적으로 1개다 2. 회의실 예약은 같은 시간에 2개가 있을 수 없다 3. 예약자, 참석자 ⇒ 회의실 예약 앱 만들어. 고려 대상: 1. 사용자 2. (관리자) 3. 서비스 코드 4. 성능, 모니터링 등등…
- "Agent = Model + Tools", "harness = Model 외 나머지": 1. Skills 2. MCP(Tools) 3. 프롬프트 **4. Memory** (5. Hook)
- 방정식 88시간 → 풀었다… / Ticket N 시간
- 개발 하네스: > '보안' > '코딩 규칙' > '개발 과정' — 코딩 규칙 → "Java = 규칙 지켰는지 프로그램", 개발 과정 → "코드 리뷰(결과 기반) > 과정도 같이…"
- ⇒ 1. 비즈니스, 2. 보안, 3. 코딩규칙 ⇒ 고려해야될 사항들을 빠짐없이 = 기능을 개발했다

**Day06_02.png — Closed Loop, 훅 이벤트, 시스템 메모리**
- "Closed Loop 이해하기 / 결과물: Flow Diagram / 1. 어떤 '검증'이 필요할까요?" — 1. Mermaid Diagram[코드] 2. Excalidraw[손]
- [회의실 예약] 1. 회의실은 '중복' 예약이 "가능"함 > 중복 예약의 우선순위는 '직급순'. 흐름: 중복 예약 가능 여부 → 직급 구분 가능 여부 → 직급의 순위 구분 여부 → DONE, 각 단계 Fail 분기와 "테스트 코드 검증 / DB 데이터 - 테스트 코드 검증"(직원의 직급 데이터 필요, 직급의 순위 구분 데이터 필요). ⇒ 1. 기능의 검증 ⇒ 테스트 2. 기반 데이터의 검증
- "테스트 코드 만들어서 검증해" 의 함정: 1. Layer 분리된… 2. 하드코딩 기반의… 3. 실제 기능과 별 상관없는 쓸모없는 테스트들..
- 훅 이벤트별 용도: SessionStart — 직전 세션에 내가 뭐했나? > 작업 메모리 / 장기 메모리. UserPromptSubmit — 요청 감시(Guardrail), Langfuse, 프롬프트 증강 → 'LLM 호출' > 모델에 맞게 프롬프팅 했는가?, "적절한 스킬이 있는가?" 있으면 무조건 실행, 없으면 요청 거부. PreToolUse — 도구 호출 증거(JSON 껍데기), 방어 "위험한 도구 실행 방어" (서브에이전트 호출? Computer Use?). PostToolUse — 도구 호출 증거 남김. Notification — 1. 완료(→ Codex가 리뷰) 2. AskUserQuestion, HITL(Human In the Loop). SessionEnd — 이 대화 세션의 요약 → 메모리 가능성 추출. Stop — 서브 프로세스 정리…
- 시스템 메모리: `.claude/CLAUDE.md`, `projects/CLAUDE.md`, `projects/CLAUDE.local.md`, `projects/.claude/rules/*.md`. 작업 지시 - "내 작업 지시를 리뷰". "테스트 코드 실행해라."

**Day06_03.png — 모델별 특성, Code Mode, 인터뷰, 소스 파악**
- Harness / DeepAgents Code / Harness Profile — 모델별 특성(강사 의견): OpenAI·Qwen(·GLM-5.3) — 프롬프트 지시 이행력 ⇒ "안주면 안해요", 공격에 대한 방어가 뛰어남 → MCP 호출. Anthropic·DeepSeek·Kimi — Context 기반의 작업 능력 ⇒ 뭘 주든 일단 해요, 개발 작업 특화(글쓰기 등의 창작 작업 x). Gemini — 전체적으로 아쉽다, Image 인식 등 멀티모달.
- Code Mode → 파이썬 코드 `/tmp/claude-projects/**/test.py`
- `/deep-interview`: 1. 현재 상황 점검 2. Evidence File 유무 3. 최초 질문 입력 4. 판단 - 5. "AskUserQuestion"
- LLM → `function_calls: [{1}, {2}]`, Tool Message ⇒ 호출이 자주… 1. 다 끝날때까지 message 안주겠다… 1,2는 2분, 3번은 10분… 2. 비동기 ⇒ 작업 "스크립트"
- https://github.com/abhigyanpatwari/GitNexus [소스 파악] 1. "읽고" 2. '연결'짓고 3. 해석하고 >> 얘는 어떤 기능을 하는가?

**Day06_04.png — 계층형 메모리 시스템, 미니 프로젝트**
- 계층형 메모리 시스템(Hierarchical). 참고 링크: learn.chatgpt.com/docs/agent-configuration/agents-md, code.claude.com/docs/ko/memory
- `~/.claude/projects/` MEMORY — 클로드가 마음대로 쓰는 메모리, 장기 메모리, 프로젝트 단위로 기억
- USER(SYS) SCOPE: `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` → 코딩/이메일/메신저/웹서핑 등등… 명령을 충실히 이행하도록… / PJT SCOPE ×2: `project/CLAUDE.md` → 이 플젝 취지, 디렉토리 구성, 코딩가이드, 아키텍처 / PJT Rule SCOPE("여긴 툴마다 다름") → 폴더 구조 - 비즈니스 로직(SQL) > SQL, "주문", 1-10번 - 로직~
- 예: `/work = claude CLAUDE.md` - `/pjt_1` > Gitnexus: READ, GREP 등 코드 서치하는 양을 줄여야됨… LSP, AST(Abstract Syntax tree) / - `/pjt_2` `src/biz/sql/AGENTS.md`
- [Claude Code & GJC 개발환경 구축] 1. 개발에 필요한 Skills 설치하시고 2. 메모리 시스템을 구성해야합니다. 3. Claude Code: Sonnet-5 기준, GJC: DeepSeek-v4-pro, GLM-5.3 기준 4. Langfuse 연동은 안해도 됩니다. (`Day06/task.md:20-33`과 같은 내용)
