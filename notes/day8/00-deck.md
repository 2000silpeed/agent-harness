## 8일차 교재 — Agent Guardrails: 입력과 출력을 방어하고, 실행 권한을 코드로 강제하기

> 출처:
> - 저장소 덱: 강의 저장소 `sds_ax_advanced_2026/Day08/Day8_Agent_Guardrails_이론자료.pdf` (66쪽, 16:9, 804KB, 2026-09-16 생성, 표지 "전현준"). `pdftotext -layout`으로 66쪽 전부를 추출해 읽었다. 본문이 빈 쪽은 없다(장 표지 4쪽만 제목뿐).
> - `Day08/README.md`가 기준 강의로 가리키는 `../Lecture_Note/Day8_Agent_Guardrails.pptx`의 PDF판이다. README·코드 주석의 "슬라이드 12·22·33·42" 같은 번호가 이 덱의 쪽 번호와 맞는다.
> - **Drive 사본은 다른 덱이다.** Google Drive `Day8_AI_Agent_Guardrails.pdf`(fileId `1j6L75dWydD6Bayi5u5KgoF0j--IhiT7j`, 7.3MB, 2026-11-10 등록)는 제목이 "AI Agent Guardrails — 행동을 통제하는 설계"이고 5개 Chapter + 부록 구성이다. 저장소 덱이 `Day08/`(방어 위치 축) 실습과 짝이고, Drive 덱은 `Day08_new/`(판정 주체 축) 실습과 짝이다. 차이와 Drive 덱 요약은 맨 아래 "부록 B"에 적었다.
> - 주의:
>   - 덱의 모델·날짜·언어 수는 덱 작성 시점(2026-09) 모델 카드 기준 표기다. 슬라이드 안에 "가상 판정 예시 · 모델 미실행", "수치는 가상 값"이라고 적힌 그림이 있다(29·30·35쪽). 측정 결과가 아니다.
>   - 덱 목차는 6개 장(01~06)인데 장 표지는 Chapter 1~4뿐이다. 05 "평가·관측·사고 대응"과 06 "도입 로드맵과 운영 Gate"는 별도 표지 없이 39~40쪽, 56~58쪽에 들어 있다.

---

### 목차 (덱 구조, 쪽 번호)

| 장 | 제목 · 부제 | 쪽 |
|---|---|---|
| 도입 | 표지, OT(과정 지도), 목차, 통제 지점 | 1~4 |
| Chapter 1 | Guardrail은 단순한 필터가 아님 — 실행의 경계 (정의와 신뢰 경계) | 5~12 |
| Chapter 2 | Input과 Output을 실행 전후로 방어합니다 (Input·Action·Output 방어) | 13~22 |
| Chapter 3 | 모델은 위험을 판별, 코드는 실행을 강제 (Guard 모델 선택, GuardSignal, Cascade, 평가, 코드 기반 구현 위치) | 23~43 |
| Chapter 4 | DeepAgents에 Guardrail을 연결합니다 (Hook·권한·HITL·Sandbox, 적용 사례, Go/No-Go, 점검표) | 44~59 |
| 참고 | 참고자료 3쪽, 모델 출처 4쪽 | 60~66 |

목차(3쪽)의 장별 질문: 01 무엇을 통제할 것인가 / 02 어디에서 막을 것인가 / 03 모델 선택과 코드 결합 / 04 어떤 Hook과 권한을 쓸 것인가 / 05 안전성을 어떻게 확인할 것인가 / 06 무엇부터 구현할 것인가.

---

### 섹션별 핵심 내용

#### 도입 (1~4쪽)

- **OT(2쪽) — 과정 지도.** 네 묶음이다. Agent Harness(Control Plane, Deterministic, Code Mode, Optimization) → Local Model(vLLM, KV Cache, Route Models, Hybrid Model Arch) → **Agent Guardrail(TODAY: Input Guardrail, Output Guardrail, Model Guardrail, Code Guardrail)** → PJT(Coding Harness, Context Control).
- **통제 지점 세 개(4쪽).** 질문은 "무엇이 들어오고, 무엇이 실행되며, 무엇이 밖으로 나가는가"다.

  | 지점 | 묻는 것 |
  |---|---|
  | 01 Input | 외부 정보와 지시를 구분했는가 |
  | 02 Action | 이 사용자가 이 자원에 실행해도 되는가 |
  | 03 Output | 공개 가능한 결과만 전달하는가 |

  역할 분담: MODEL은 의미·문맥·정책 위반을 판별하고, CODE는 권한·형식·한도를 강제한다. 검사 결과를 실행 제어에 연결해야 Guardrail이 실제로 동작한다.

#### Chapter 1. Guardrail의 정의와 신뢰 경계 (5~12쪽)

- **"하지 마라"와 "할 수 없다"(6쪽).** 시스템 프롬프트는 행동 지침이고 권한 검사는 실행 조건이다.
  - 지침만 있는 Agent: 전송 금지 지침 → 모델이 전송 제안 → API가 그대로 실행.
  - 강제 경계가 있는 Agent: 전송 금지 정책 → 수신자·권한 검사 → 비인가 요청은 실행하지 않음.
  - 정의: LLM이 실수해도 비인가 행위가 실행되지 않는 경계를 만드는 것.
- **Harness 내부의 Guardrail(7쪽).** Guardrail은 계획·도구·상태·검증을 가로지르는 통제 계층이다. 위에 "정책 · 권한 · 비용 한도 · 개인정보 규칙 · 사람 승인"이 놓이고, 아래 네 단계에 적용된다: 01 목표·계획(사용자 의도) / 02 실행·도구(행위와 인자) / 03 상태·메모리(출처와 저장) / 04 검증·완료(후조건과 결과). 실패하면 중단 · 수정 · 재검증.
- **Input은 사용자 프롬프트보다 넓다(8쪽).** Agent가 읽는 모든 정보가 새 입력이고 출처마다 신뢰 수준이 다르다: 사용자(요청·첨부 파일), 검색/RAG(문서·웹 페이지), Tools/MCP(API·DB 응답), Memory/Agent(저장 정보·다른 Agent의 결과). Input Guard는 출처 · 내용 · 권한을 검사한 뒤 컨텍스트로 넣는다.
- **Output은 답변만이 아니다(9쪽).** 최종 응답(텍스트·표·링크), 도구 호출(이메일·SQL·HTTP), 파일 생성(보고서·코드·첨부), 메모리 기록(후속 세션에 남는 정보)이 모두 출력이다. 사용자가 보지 않는 출력도 개인정보 유출과 상태 변경을 일으킨다.
- **신뢰 경계는 문자열이 아니라 시스템 상태다(10쪽).** `<TRUSTED_POLICY>` 같은 태그는 구분자이지 권한 증명이 아니다.

  | 영역 | 들어 있는 것 | 권한 |
  |---|---|---|
  | 외부 데이터 영역 | 문서 · 웹 · MCP 응답 | 읽을 수 있지만 명령권은 없음 |
  | Agent 추론 영역 | 계획 · 분석 · 행동 제안 | 위험 신호 생성. 권한 발급은 불가 |
  | 신뢰된 통제 영역 | 인증된 사용자 · tenant, Policy Engine · IAM | 실행·저장·전송을 강제 |

  정보의 출처를 아는 것과 그 정보에 실행 권한이 있는 것은 다르다.
- **간접 Injection(11쪽).** 사용자가 아니라 Agent가 읽은 외부 콘텐츠가 행동 방향을 바꾼다. 흐름: 01 정상 요청(보고서 요약) → 02 외부 문서(무관한 지시 포함) → 03 행동 제안(외부 전송 시도) → 04 실제 실행(자격·정책 확인). 방어는 두 곳이다. 입력 단계에서 출처와 무관한 지시를 탐지하고, 실행 단계에서 허용되지 않은 수신자를 차단한다.
- **위협·자산·통제 지점 표(12쪽).**

  | 위협 묶음 | 영향받는 자산 | 주요 방어 |
  |---|---|---|
  | 목표 탈취 / Injection | 정상 사용자 의도 | Input·Context 검사 + Action 권한 |
  | Tool 오용 / 권한 악용 | API · DB · 계정 권한 | 사용자-자원 권한 + 최소 Tool |
  | 데이터 유출 | PII · 기업기밀 · 키 | DLP + 수신자·Egress 제한 |
  | 코드 / 공급망 위험 | 호스트 · 네트워크 | Sandbox + 검증된 Tool·패키지 |
  | 메모리 / Agent 오염 | 장기 상태 · 다른 Agent | 출처·tenant 격리 + 쓰기 검증 |
  | 자원 소진 / 연쇄 실패 | 비용 · 가용성 | 호출·시간·토큰 상한 + 중단 |

#### Chapter 2. Input·Action·Output 방어 (13~22쪽)

- **연결된 방어 흐름(14쪽).** 01 외부 입력(요청·문서) → 02 Input Guard(내용·출처) → 03 Agent(계획·판단) → 04 Action Guard(권한·승인) → 05 Tool 실행(제한된 환경) → Tool Result Guard → 다시 Agent로. 마지막에 Output Guard → 최종 답변. 전 과정에 Trace · Budget · Stop이 걸린다. 도구 결과를 다시 Input으로 받는 반복 구조를 보호하는 것이 요점이다. Input 검사는 오염을 줄이고, Action 검사는 비인가 실행을 막는다.
- **Input Guard 5단계(15쪽).** 01 정규화(길이·인코딩·구조 제한) → 02 PII/DLP(개인정보·키, 최소 전달) → 03 Injection(지시 전환, 위험 신호) → 04 출처·권한(source / ACL, tenant 범위) → 05 결정·기록(통과 · 차단 · 검토 · 변환). 내용 검사와 인증·접근 권한 확인은 서로 다른 일이다. 정규화와 모델 판별을 통과해도 읽기 권한이 없는 데이터는 주지 않는다. (용어: PII 개인정보, DLP 민감정보 유출 방지, ACL 접근 제어 목록.)
- **RAG·MCP: 가져올 권한과 지시할 권한은 다르다(16쪽).** "사내 문서"나 "공식 도구 응답"이라는 이유만으로 신뢰하지 않는다.
  1. 조회 전에 권한을 확인한다. tenant · 문서 ACL · 자원 소유권을 검색 결과 필터와 연결한다(사용자별 검색 범위).
  2. 조회 후에는 내용을 확인한다. Injection · 비밀정보 · 크기 제한을 Tool Result에도 적용한다.
  3. 출처는 구조화해서 보존한다. `source_id` · `source_trust` · `version`을 신뢰된 런타임 상태에 유지하고, 명령이 아닌 데이터로 전달한다.
- **Memory와 Subagent도 다시 들어오는 Input이다(17쪽).**

  | 경로 | 단계 | 확인할 것 |
  |---|---|---|
  | Memory | 저장 제안 → 쓰기 검증 → 다시 읽기 | 사용자 사실·업무 상태 / 출처·민감도·tenant / 만료·권한·현재 정책 |
  | Subagent | 업무 위임 → 제한된 실행 → 결과 재검사 | 의도와 허용 범위 전달 / 필요한 Tool만 제공 / 외부 결과처럼 검증 |

  메모리는 쓰기와 읽기를 모두 검사하고, Subagent 결과는 자동으로 신뢰하지 않는다.
- **Action Guard는 실제 호출 직전에 둔다(18쪽).** 최종 답변을 차단했어도 이미 이메일을 보냈다면 늦다. 너무 늦은 차단: 이메일 초안 → `send_email()` → 외부 전송 완료 → 답변 검사. 실행 전 차단: 이메일 초안 → Action Guard → 조건 불충족 → 실행 없음. 실행 성공 여부는 답변 문구가 아니라 실제 Tool 호출 이력으로 확인한다.
- **Policy Decision과 Enforcement의 분리(19쪽).** 모델이 제안하고, Policy Engine이 결정하고, Tool Wrapper가 집행한다.
  - PDP(정책 결정 지점)의 입력은 둘이다. 신뢰된 서버 상태(인증 사용자·tenant, 자원 소유권, 원본 사용자 의도)와 모델의 제안(Tool 이름, 정규화할 인자, 의미적 위험 신호).
  - PDP의 출력은 ALLOW / BLOCK / REVIEW / TRANSFORM이다.
  - PEP(정책 집행 지점)는 Tool Wrapper이고, 미허용이면 호출 0회다.
  - 핵심: ALLOW가 없는 실행 경로가 존재하지 않게 만든다.
- **Output Guard: 무엇이 어디로 나가는가(20쪽).**

  | 출력 경로 | 확인할 내용 | 실패 시 동작 |
  |---|---|---|
  | 최종 답변 | 형식 · 유해성 · 근거 · 민감정보 | 차단 / 최소정보로 재생성 / 사람 검토 |
  | 이메일 / HTTP | 수신자 · 도메인 · body / URL | 전송 전 거부 / 필요한 범위로 축소 |
  | 파일 / 리포트 | 첨부 내부의 PII · 비밀 · 권한 | 격리 / 비식별 처리 후 재검증 |
  | 메모리 저장 | 보존할 정보 · 출처 · tenant | 저장 거부 / 임시 상태로 제한 |

  이미 외부로 전송한 데이터는 나중의 Output 검사로 되돌릴 수 없다. 화면의 답변뿐 아니라 첨부 파일·URL·도구 인자·메모리도 검사한다.
- **HITL 승인 화면(21쪽).** 승인자는 수신자·데이터·실행 인자를 직접 확인한다. 예시 화면의 항목: `REVIEW REQUIRED`, 도구 `safe_send_email`, 수신자 `review@example.co.kr`, 포함 데이터 "주문 합계 / 개인식별정보 제외", 정책 사유 "외부 상태 변경 전 승인 필요", 실행 바인딩 "tool + args_hash + 사용자", 버튼 승인 / 수정 후 재검증 / 거절.
  1. 실행 대상을 표시한다. 원본 수신자·자원·인자를 보여 주고 모델 요약과 다르면 강조한다.
  2. 승인자를 확인한다. 승인자의 업무 권한과 세션 상태를 신뢰된 서버에서 확인한다.
  3. 실행 전에 재검증한다. 수정된 인자·현재 자원 상태·정책을 다시 확인한 뒤 실행한다.
  
  승인 후 인자가 바뀌면 다시 검증한다. 승인은 권한 검사를 대체하지 않는다.
- **결과 네 가지 표준화(22쪽).**

  | 결과 | 뜻 |
  |---|---|
  | ALLOW | 현재 정책의 조건을 충족한 실행만 진행 |
  | BLOCK | 도구를 호출하지 않고 사유 코드를 반환 |
  | REVIEW | 실행을 보류하고 사람 또는 별도 검증 |
  | TRANSFORM | 내용·인자를 축소한 뒤 처음부터 재검증 |

  TRANSFORM → 재검증 → 새 PolicyDecision. 사유 · 정책 버전 · 검사 단계를 기록한다. **Guard 장애·파싱 실패·시간 초과를 ALLOW로 해석하지 않는다.**

#### Chapter 3. 모델 기반 판단 + 코드 기반 강제 (23~43쪽)

- **Model Guardrail과 Code Guardrail의 역할(24쪽).**

  | 구분 | 모델 기반 | 코드 기반 |
  |---|---|---|
  | 잘하는 판단 | 의미·문맥·복합 정책 위반 | 스키마·범위·권한·정확한 한도 |
  | 주요 도구 | Classifier / LLM Judge | Validator / IAM / Policy Engine |
  | 실패 가능성 | 우회 · 오탐 · 미탐 · 변동성 | 규칙 누락 · 설정 오류 · 경로 우회 |
  | 역할 경계 | 위험 신호와 검토 필요성 생성 | 최종 실행 조건을 확인하고 강제 |
  | 평가 기준 | Recall · FPR · 한국어 적합성 | 정책 행렬 · 실행 거부 · 경로 커버리지 |

- **모델 기반 Guardrail 패턴 4종(25쪽).** Classifier(Injection 또는 안전성 분류: 입력 → 위험 label), LLM-as-a-Judge(업무 정책과 요청·행동 비교: 정책 + 행동 → 판정), Critique–Revise(후보 결과를 평가한 뒤 수정: 초안 → 평가 → 제한된 수정), Cascade / Ensemble(저비용 검사 후 불확실 사례만 승격: 규칙 → 소형 모델 → Judge). 패턴마다 검사 대상과 추가 비용이 다르다. 복잡한 판단은 모델에 맡기되 **반복 수정과 승격에는 반드시 상한을 둔다.**
- **검사 목적별 Guard 모델(26쪽).**

  | 검사 목적 | HF 모델 예시 | 구분할 점 |
  |---|---|---|
  | Prompt Injection | Wolf v2 / Prompt Guard 2 / SGuard / Kanana | 외부 지시 탈취 탐지 ≠ 유해 콘텐츠 분류 |
  | PII · 자유문 정책 | LFM2.5 PII-Detector / Policy-Linter | 전문 Encoder 모델 ≠ 범용 LFM Instruct |
  | 입력 · 출력 안전성 | Shieldstral / Nemotron 3.5 / Qwen3Guard | 텍스트·이미지·정책 유연성·언어별로 선택 |
  | 정책 · 결과 Verifier | Granite Guardian 4.1 / gpt-oss-safeguard | RAG·Tool 환각 검사는 권한 부여가 아님 |
  | Managed 서비스 | HF 가중치 목록과 별도 관리 | Model Armor / omni-moderation 참고 |

  공개 가중치 모델과 관리형 API를 구분해 배포 조건을 비교한다.
- **Wolf Defender v2와 GLiGuard(27쪽).**
  - Wolf Defender v2(`patronus-studio/wolf-defender-prompt-injection`): 외부 문서·Tool 결과의 지시 탈취 탐지, BENIGN / INJECTION 이진 분류, 2,048-token window, ONNX 변형 제공, 주요 평가 언어는 영어·독일어. 긴 문서는 분할·집계하고 단순 잘림과 구분한다.
  - GLiGuard(`fastino/gliguard-LLMGuardrails-300M`): 스키마로 검사 Task와 라벨을 지정, 한 번의 Encoder 통과로 다중 분류(입력·출력 안전성 / Jailbreak / 거절 분류), CPU-first, GLiNER2 interface, 영어 카드 표기(한국어 검증은 별도).
  - 둘 다 모델 카드 표기 Apache 2.0. 서로 다른 데이터셋의 점수는 직접 순위화하지 않는다. 한국어·긴 문서·Tool 결과를 포함한 내부 평가로 적용 범위를 확인한다.
- **LFM2.5 Encoder 기반 2종(28쪽).** Base는 LFM2.5-Encoder-230M / 350M이고 업무별 파인튜닝 모델이 따로 있다.
  - `LiquidAI/LFM2.5-Encoder-350M-Policy-Linter`: 자유문 규칙 × 텍스트 토큰, 위반 후보 위치와 점수 산출, 15개 언어 표기(**한국어 미포함**).
  - `LiquidAI/LFM2.5-Encoder-350M-PII-Detector`: 40개 PII 유형의 위치·라벨 탐지, 마스킹·제거는 후속 코드가 수행, 16개 언어 표기(**한국어 포함**).
  - 둘 다 LFM Open License v1.0, custom code. 한 계열이라고 언어 성능을 공유한다고 가정하지 않는다.
- **Policy Linter는 "토큰 × 정책"을 평가한다(29쪽).** 한 번의 Encoder 통과로 규칙별 위반 후보 구간을 찾는다. 예: 규칙 R1 "절대적 품질 보장 탐지", R2 "개인 연락처 탐지"와 문장 "Always error-free service." → 구간별 신호 행렬(R1: Always 위험 / error-free 위험 / service 낮음, R2: 전부 낮음). 가상 판정 예시이고 모델을 실행한 결과가 아니다. 처리: 토큰 점수 → 구간 병합 → 정책별 임계값 → BLOCK / REVIEW / 수정 후 재검사.
- **PII Detector(30쪽).** 모델은 민감 구간을 찾고 코드는 공개 범위에 맞게 처리한다. 01 원문(`연락처: demo@example.com`) → 02 PII 모델(`contact.email`, 원문 구간·유형) → 03 정책 코드(구간·허용 범위 검증, 외부 공개는 마스킹) → 04 검사 후 공개(`연락처: [EMAIL]`). 국내 식별자·주소·업무 약어는 별도 평가 후 규칙·검증기와 조합한다. 설계 예시: 누락률과 과잉 삭제율을 함께 측정하고, 구간 오류·모델 장애 시에는 원문 공개를 보류하고 검토 경로로 보낸다. 이메일·Tool 인자·로그·Memory도 검사한다. 최종 답변만 마스킹하면 늦을 수 있다.
- **Shieldstral(31쪽).** `mistralai/Shieldstral-1.0-3B`, 공식 발표 2026-08-04, 3B, 텍스트 + 이미지, 12개 언어(한국어 포함), 권장 입력 ≤ 32K, Apache 2.0. 입력을 Instruct(검사 맥락·엄격도) / Query(하나의 yes/no 질문) / Document(검사할 내용)로 나눈다. 단일 forward pass의 yes/no logits를 연속 점수로 쓴다. 정책을 추론 시점에 바꿀 수 있고 정책별 판단은 질의별로 분리한다. 서비스별 Gate: "정책 위반인가? yes = 위험"처럼 yes가 뜻하는 판정을 고정하고, 검증셋으로 정책별 임계값을 보정하고, 불확실하면 REVIEW로 보낸다. 권한·DLP·실행 통제는 별도다.
- **콘텐츠 안전성 모델 비교(32쪽).**

  | 모델군 | 검사 범위 | 출력·유의점 |
  |---|---|---|
  | Nemotron 3.5 Content Safety | 텍스트 + 단일 이미지, 기본 분류 + 사용자 정책, 한국어 포함 12개 언어 | User Safety / Response Safety, 표준 라벨 · 선택적 추론, HF 공개 2026-06-02 |
  | Qwen3Guard Gen / Stream | 0.6B · 4B · 8B. Gen은 프롬프트·응답 분류, Stream은 생성 중 토큰 분류 | Safe / Controversial / Unsafe, 119개 언어·방언 표기, 경계 등급의 처리 정책 필요 |
  | Llama Guard 4 12B | 텍스트 · 이미지 검사, Llama Guard 계열의 멀티모달 비교 기준선 | Safe / Unsafe + 위험 범주, Llama 4 라이선스 조건 확인, 3-1B INT4는 경량 기준선 |

  스트리밍 설계 예시: 검사 완료 전 외부 전송을 보류한다. Prompt Injection 탐지와 PII 구간 처리는 별도 검사로 구성한다.
- **정책·결과 검증용 Judge(33쪽).**
  - Granite Guardian 4.1 8B(`ibm-granite/granite-guardian-4.1-8b`): RAG groundedness · relevance, Function-calling hallucination, 사용자 정의 판단 기준(BYOC), Thinking / Non-thinking 모드. 공식 카드 2026.04, Apache 2.0.
  - gpt-oss-safeguard(`openai/gpt-oss-safeguard-20b`): 정책을 입력으로 받는 추론형 Guard, 20b / 120b, 복잡한 정책의 예외·경계 사례용. **상시 1차 필터보다 승격 경로 후보.** 공식 발표 2025.10.29, Apache 2.0.
  - Judge는 위험 신호를 반환하고 API 실행 권한은 정책 코드가 결정한다.
- **한국어 전용 Guard(34쪽).**

  | 후보 | 전용 역할 | 한국어 근거·한계 |
  |---|---|---|
  | Samsung SDS SGuard-v1 | JailbreakFilter-2B-v1, ContentFilter-2B-v1 | 한국어·영어 중심 학습/평가, 권장 입력 ≤ 8K, 2025-11-17 |
  | Kakao Kanana Safeguard | prompt-2.1b: Injection·Prompt leaking, 8b: 콘텐츠 안전성 | 한국어·영어 최적화 표기, Prompt 모델의 대화 맥락 한계 |
  | LiquidAI PII vs Policy | PII-Detector: 개인정보 구간, Policy-Linter: 자유문 규칙 매칭 | PII는 ko 포함, Policy는 ko 미포함 |

  SGuard의 평가 범위는 한국어·영어다. 기반 모델의 언어 목록과 구분한다.
- **LLM Judge 결과의 구조화(35쪽).** 정책 · 원래 의도 · 비신뢰 컨텍스트 · 제안 행동을 구분해 전달한다. 판정 JSON 예시(수치는 가상 값):

  ```json
  {"decision": "REVIEW", "risk_labels": ["external_send"], "reason_code": "NEEDS_APPROVAL",
   "evidence_spans": ["..."], "confidence": 0.0}
  ```
  1. 자유 서술 대신 enum. ALLOW·BLOCK·REVIEW·TRANSFORM 가운데 허용된 값만 받는다.
  2. 근거와 식별자를 보존한다. 어느 정책·어느 구간 때문에 판정했는지 추적한다.
  3. 잘못된 응답은 통과시키지 않는다. JSON 파싱 실패·누락·알 수 없는 값은 차단 또는 검토 경로로 보낸다.
  
  모델이 생성한 confidence는 보정된 확률이나 실행 권한으로 해석하지 않는다.
- **GuardSignal: 모델별 출력의 정규화(36쪽).** 원시 출력 · 내부 신호 · 정책 결정 · 실행 제어를 서로 다른 계약으로 관리한다.
  - 서로 다른 모델 출력: LFM(token / rule / span), Shieldstral(yes-no 점수), Qwen(3단계 라벨), Nemotron(안전성 라벨), Granite(`<score>` 판정).
  - 내부 GuardSignal 필드: `stage`, `status`, `risk_labels`, `evidence_spans`, `score_type`, `score`, `model_id`, `revision`, policy / threshold version.
  - 정책 + 실행 Gate: 인증된 사용자 / tenant, 현재 리소스 권한 → ALLOW / BLOCK / REVIEW / TRANSFORM, 실행 직전 재검증.
  - `score_type`에 토큰 매칭 점수 · yes/no 확률 · 생성형 라벨의 차이를 보존한다. 파싱 실패·시간 초과·점수 누락은 **UNKNOWN**으로 전달해 차단 또는 검토한다.
- **Cascade(37쪽).** 명확한 규칙을 먼저 검사하고 애매한 사례만 큰 Judge로 넘긴다. 규칙 검사(길이·형식·비밀) → 소형 Guard(Injection · PII 신호) → 불확실하면 LLM Judge(애매한 정책 판단)로 승격 → Action 권한 검사(모든 실행 경로가 통과) → 고위험은 사람 승인 추가. **어떤 경로로 지나왔든 Action authorization은 생략하지 않는다.**
- **서비스별 Guard 조합 예시(38쪽).**

  | 서비스 | 조합 |
  |---|---|
  | 사내 한국어 업무 Agent | 입력 공격: SGuard / Kanana, PII: LFM PII + 형식 검증기, 콘텐츠: SGuard Content, 고난도 정책: 별도 Judge |
  | 텍스트·이미지 서비스 | 콘텐츠: Shieldstral vs Nemotron, 개인정보: 별도 DLP, 지시 탈취: 별도 Injection 검사, 검사 전 이미지·본문 공개 금지 |
  | 로컬 문서·초안 검사 | PII: LFM PII-Detector, 정책 구간: LFM Policy-Linter, 한국어 규칙: 검증 후 채택, RAG 근거: Granite 후보 |

  배포 조건: 동일 데이터·정책으로 후보를 비교한 뒤 운영 조합을 확정한다. 모든 조합의 공통 기반은 **IAM · Tool Wrapper · egress 제한 · HITL · 감사 로그**다.
- **Guard 모델의 동일 조건 비교 평가(39쪽).** 입력·정책·지표를 고정하고 안전성과 정상 업무 성공률을 함께 측정한다.
  1. 같은 입력과 정책: 정상 / 공격 / 애매한 사례, 한국어·혼합어·긴 문서, Input / RAG / Tool / Output.
  2. 목적별 정답 정의: Injection은 미탐·오탐, PII는 구간 누락·과잉 삭제, Policy는 규칙별 위반 구간.
  3. 정책별 Gate 보정: 검증셋에서 threshold 선정, 별도 holdout에서 최종 평가, UNKNOWN / REVIEW 비용.
  4. Agent 영향 확인: 정상 업무 성공률, 비인가 실행·실제 유출률, p95 지연·메모리·총비용.
  
  양자화·모델 교체·프롬프트·라벨 매핑을 바꾸면 임계값과 전체 Agent 회귀 평가도 다시 실행한다.
- **Threshold 보정(40쪽).** 위험 신호 축 위에 세 구간을 둔다: ALLOW 후보(명확한 정상 요청) / REVIEW(불확실·경계 사례) / BLOCK 후보(명확한 정책 위반). 구간은 운영 정책이 정한다. 함께 측정할 것: 공격 미탐률 · 정상 오차단률 · 사람 검토 비율 · 정상 업무 성공률. 모델·정책·언어·업무가 바뀌면 임계값과 검토 비율도 다시 평가한다.
- **코드 기반 Guardrail의 구현 위치 4곳(41쪽).**

  | 위치 | 역할 | 하는 일 |
  |---|---|---|
  | Middleware | 전 실행 경로 | 입력·출력 공통 검사, 모델·도구 호출 가로채기 |
  | Tool Wrapper | 실제 실행 경계 | 함수 실행 직전 사용자 권한, 승인·한도·대상 자원 재검증 |
  | Validator | 명시적 계약 | 인자·스키마·URL·경로, 허용된 타입과 값만 통과 |
  | Sandbox | 피해 반경 제한 | 파일·네트워크·프로세스, 실행 권한과 자원 제한 |

- **정책 코드: 사용자 신원은 모델 인자가 아니다(42쪽).** 서버가 확인한 identity와 검증된 인자로 정책 입력을 구성한다.

  ```python
  def decide(ctx, args, resource):
      # ctx comes from authenticated runtime
      if resource.tenant_id != ctx.tenant_id: return "BLOCK"
      if not ctx.can("send", resource): return "BLOCK"
      if args.recipient_domain not in ALLOWLIST: return "BLOCK"
      if not ctx.has_valid_approval(args): return "REVIEW"
      return "ALLOW"
  ```
  서버가 제공하는 것은 사용자 · tenant · scope, 자원 소유권과 현재 상태다. 모델이 제안하는 것은 Tool 이름 · 대상 · 수신자 · 본문 등 업무 인자다. 실행 전에 둘을 결합하고 권한과 스키마를 따로 검사한다. schema validation은 형식을, authorization은 실행 자격을 확인한다.
- **Tool Wrapper: ALLOW일 때만 실제 함수를 호출(43쪽).**

  ```python
  def guarded_call(ctx, proposed, impl):
      args = validate_args(proposed)
      decision = policy.check(ctx, args)
      if decision == "REVIEW": return pause_for_review(ctx, args)
      if decision != "ALLOW": raise PolicyDenied(decision)
      result = impl(**args)
      return validate_tool_result(result)
  ```
  실행 전(스키마 · 자원 권한 · 수신자 · 승인 상태) → 실제 호출(ALLOW일 때만 impl, 다른 경로에서는 호출 0회) → 실행 후(크기 · DLP · Injection 검사 후 모델로 결과 전달). 검사와 실행 사이에 Guardrail을 우회하는 별도 경로를 만들지 않는다. **BLOCK·REVIEW·판정 오류에서 impl이 호출되지 않는지 테스트한다.**

#### Chapter 4. LangChain DeepAgents 구현 (44~59쪽)

- **Planner–Executor–Verifier 참조 아키텍처(45쪽).** 위에 TRUSTED CONTROL PLANE(Identity · Policy · Approval · Audit)이 있다. Planner(원래 의도 유지, 계획·작업 분해), Executor(업무별 최소 Tool, 실행 전 Guard), Verifier(읽기 전용 검증, 출력·후조건 검사). 실행 권한은 모델의 분석 결과가 아니라 통제 계층의 정책으로 결정한다.
- **Middleware Hook과 방어 책임(46쪽).**

  | Hook | 시점 | Guardrail 책임 |
  |---|---|---|
  | `before_agent` | invocation 시작 | 사용자 · tenant · 실행 예산 초기화 |
  | `before_model` | 모델 호출 전 | 새 Input · Context · Tool Result 검사 |
  | `wrap_model_call` | 모델 호출 전후 | Timeout · Fallback · Guard 모델 routing |
  | `after_model` | 모델 응답 직후 | 최종 답변 후보 · Tool Call 후보 검사 |
  | `wrap_tool_call` | 도구 실행 전후 | 권한 강제 → 실행 → 결과 검사 |
  | `after_agent` | invocation 종료 | 최종 결과 검증 · DLP · 감사 기록 |

  실제 Tool을 감싸는 `wrap_tool_call`이 Action Gate의 핵심 연결 지점이다.
- **Input Middleware(47쪽).** 사용자 메시지·Tool 결과·RAG·Memory를 모델 호출 전에 검사한다.

  ```python
  def before_model(state, runtime):
      items = new_untrusted_inputs(state)
      for item in items:
          result = input_guard.scan(item)
          record_scan(item, result)
          if result.requires_block: return stop_with_reason(result)
      return apply_verified_context(state)
  ```
  검사 대상은 HumanMessage(최초 요청과 추가 메시지)와 새로 들어온 Tool / RAG / Memory / Subagent 데이터다. 원문 ID·검사 버전·결과를 기록해 중복과 누락을 관리하고, 권한은 현재 시점에 따로 확인한다. **검사 단위는 마지막 메시지가 아니라 새로 유입된 비신뢰 데이터다.**
- **`wrap_tool_call`: 실행과 결과를 한 경계로(48쪽).**

  ```python
  def wrap_tool_call(request, handler):
      ctx = trusted_context(request)
      verdict = authorize(ctx, request.tool_call)
      if verdict.needs_review: return pause_for_review(request)
      if not verdict.allowed: return blocked_tool_message(request)
      result = handler(request)
      return scan_result(result)
  ```
  request에서 읽을 것은 제안 Tool · 인자 · 호출 ID와 신뢰된 runtime의 identity다. 차단 시 handler를 부르지 않는다. 반환값도 입력이므로 DLP · 크기 · Injection을 검사한다. 차단·실패 상태를 ToolMessage에 구분해 기록하고 원래 `tool_call_id`를 유지한다.
- **DeepAgent 구성(49쪽).** Middleware는 공통 검사, 보호된 Tool은 실행 강제, HITL은 승인 대기다.

  ```python
  agent = create_deep_agent(
      model=model,
      tools=[safe_search, safe_send_email],
      middleware=[guard_middleware],
      interrupt_on={"safe_send_email": {"allowed_decisions": ["approve", "reject"]}},
      checkpointer=durable_checkpointer,
  )
  ```
  `safe_*` Tool 내부에서도 자원 권한과 정책을 확인한다. 고위험 승인은 `interrupt_on` + checkpointer이고 재개 시 현재 상태를 다시 확인한다. 사내 API의 자원 권한은 `safe_*` Tool 또는 Policy Service에서 따로 검사한다.
- **HITL: 중단·상태 보존·재개(50쪽).** 01 행동 제안(원본 인자 저장) → 02 Interrupt(실행 전 중단) → 03 Checkpoint(thread · 요청 ID) → 04 사람 결정(승인 / 거절) → 05 Resume(재검증 후 실행). 대기 상태는 아직 실행하지 않은 상태다. 승인 바인딩은 Tool + 인자 + 대상 자원이다. 재개 조건은 승인 만료 · 현재 권한 확인이다. 체크포인트 복구가 이미 발생한 외부 부작용을 자동 취소하지는 않는다.
- **Filesystem permissions: 규칙 순서(51쪽).** First-match-wins이고 아무 규칙도 맞지 않으면 기본 허용이다. 권장 순서: 01 민감 경로 DENY(`/workspace/.env`, credentials 등) → 02 업무 경로 ALLOW(`/workspace/**`) → 03 나머지 전체 DENY(`/**`). 넓은 `/workspace/**` ALLOW가 먼저면 뒤의 `.env` DENY까지 도달하지 않는다. 내장 파일 도구의 권한 규칙은 OS Sandbox나 임의 코드 실행 통제가 아니다.
- **Subagent마다 최소권한(52쪽).**

  | 역할 | 허용할 Tool 예 | 제한 원칙 |
  |---|---|---|
  | Planner | read / search / task | 쓰기·전송 권한을 직접 주지 않음 |
  | Research | 검색 / 공개 문서 읽기 | 외부 결과를 검사 후 반환 |
  | 업무 Executor | read_customer / update_case | 현재 사용자·자원 scope로 제한 |
  | Email Executor | draft_email / 보호된 send | send는 정책 + 사람 승인 |
  | Code Executor | 격리된 sandbox execute | 호스트 키·자유 네트워크 차단 |
  | Verifier | Tool 없음 또는 read-only | 검증을 위해 쓰기 권한을 주지 않음 |

  부모 Agent와 Subagent의 Tool 목록 · 권한 · Middleware를 각각 확인한다. **부모 permissions 상속과 custom middleware 적용은 별개의 설정이다.**
- **Sandbox(53쪽).** 생성 코드가 실행될 수 있다면 파일 도구 설정만으로 충분하지 않다. 격리 실행 환경 안에 Generated Code, 제한된 `/workspace`, 시간 · CPU · Memory quota를 두고 호스트 키·민감 볼륨을 넣지 않는다.
  1. 접근 범위 제한: 호스트 FS·비밀키 접근 금지, 업무에 필요한 경로만 제공.
  2. 밖으로 나가는 연결 제한: Network egress 기본 deny, 승인된 목적지만 허용.
  3. 결과도 다시 검사: 실행 출력·파일·다운로드 결과를 모델에 넣기 전 검증.
  
  요약: 네트워크는 기본 차단, 비밀정보는 미제공, 결과물은 비신뢰 입력으로 재검사.
- **Guard 교체를 위한 모듈과 내부 계약(54쪽).** 공급자 응답 형식보다 내부 PolicyDecision을 먼저 고정한다. 모듈 구성 예: `guardrails/`(input · context · action · output · dlp · policy_client), `tools/`(safe_search · safe_email · safe_database), `ops / evals`(trace · metrics · recovery, benign · attack · regression). 계약 두 개: GuardContext(trace · user · tenant · stage, source_trust · 원본 의도)와 PolicyDecision(action · reason_code · risk_labels, policy_version · 검사 결과). 모델 교체가 권한 정책과 Tool 실행 코드의 전면 수정으로 이어지지 않게 한다.
- **적용 사례: 내부 보고서를 검토자에게 전달하기(55쪽).**

  | # | 단계 | 검사 질문 | 예상 결과 |
  |---|---|---|---|
  | 1 | 보고서 조회 | 이 사용자가 읽을 수 있는 문서인가 | ACL 통과한 문서만 반환 |
  | 2 | 내용 수신 | 문서가 무관한 행동을 지시하는가 | 무관한 지시를 신뢰하지 않음 |
  | 3 | 요약 초안 | 필요 이상의 개인정보가 포함됐는가 | 합계 중심으로 최소화 |
  | 4 | 전송 제안 | 수신자·자원 권한·승인이 유효한가 | 필요 시 REVIEW로 중단 |
  | 5 | 실제 전송 | 승인된 인자와 현재 정책이 맞는가 | ALLOW일 때만 호출 |
  | 6 | 완료 기록 | 무엇이 전달됐고 정책은 무엇이었나 | 민감정보 없는 Trace 보존 |

  정상 작업은 완료하되 과도한 데이터와 비인가 목적지로의 전송은 막는다.
- **Go / No-Go: 단계별 배포 승인 기준(56쪽).**

  | Gate | 필수 확인 | 남길 증거 |
  |---|---|---|
  | 기반 설계 | Tool owner · 위험도 · scope · side effect 정의 | Tool 목록 · 데이터 흐름 · 정책표 |
  | PoC | 정상 업무 성공 + 공격 대응을 함께 측정 | Benign / Security 결과 |
  | Security | 알려진 Critical 비인가 실행 회귀 차단 | 실제 Tool 실행 이력 · 회귀 로그 |
  | Production | 고위험 실행의 정책·승인 경로 누락 없음 | Coverage · Runbook · 운영 승인 |

  고위험 실행에는 정책 판정과 필요한 승인 증거가 모두 있어야 한다.
- **통합 아키텍처(57쪽).** 인증·tenant + Policy Engine + Human Approval 아래에 외부 입력 → Input Guard → Agent → Action Gate → 제한된 Tool → Output Gate가 놓인다. Tool Result · Memory는 재검사로 되돌아간다. 운영 피드백 고리: Trace / Version → Eval → Alert / Contain → Regression → 개선.
- **운영 전 점검표(58쪽).**

  | 항목 | 질문 |
  |---|---|
  | 읽기 경계 | RAG·MCP·Memory까지 권한과 출처가 남아 있는가 |
  | 실행 경계 | 모든 위험 Tool이 정책과 승인 Gate를 지나는가 |
  | 권한 근거 | identity·tenant·소유권을 서버가 결정하는가 |
  | 격리 범위 | 호스트 비밀·파일·네트워크·자원이 제한되는가 |
  | 평가 증거 | 정상 업무 성공과 비인가 실행을 함께 측정하는가 |
  | 운영 복구 | 탐지 → 중단·격리 → 복구 → 회귀 등록이 가능한가 |

  확인되지 않은 항목은 보완한 뒤 운영 승인 여부를 결정한다.
- **핵심 정리(59쪽).** 모델에게 안전을 요청하되, 모델이 실패해도 시스템이 안전하도록 설계한다.
  1. 입력과 출력의 범위를 넓게 본다: RAG · Tool Result · Memory · Tool Call까지 검증.
  2. 모델의 판단과 실행 권한을 분리한다: 의미적 위험은 모델이, 허용된 실행은 코드가 확인.
  3. 평가와 운영으로 통제를 검증한다: 실제 실행 이력 · 정상 업무 성공 · 사고 회귀를 함께 본다.
  
  **구현 순서: 권한 경계 → 의미 기반 검사 → 평가·운영.**

#### 참고자료와 모델 출처 (60~66쪽)

- **정의·원칙·위협 모델(60쪽).** R: "Agent 시스템 Guardrail 심층 리서치 및 LangChain DeepAgents 구현 보고서"(덱의 기초 자료). O1: OWASP Top 10 for Agentic Applications 2026. O2: NIST AI Risk Management Framework / GenAI Profile. O3: Open Policy Agent(정책 결정과 집행을 분리하는 참조 구조). O4: Rebedea et al., NeMo Guardrails, EMNLP 2023 Demo.
- **Guard 모델·한국어 Judge·평가(61쪽).** W5: Meta Llama Prompt Guard 2 모델 카드(Injection 분류 범위, 512-token 컨텍스트, 다국어 평가 범위). W6: OpenAI omni-moderation. K2: NAVER HyperCLOVA X THINK Technical Report, arXiv:2506.22403(한국어 정책 Judge 후보, 전용 Guard와 구분). P1: Debenedetti et al., AgentDojo(2024), arXiv:2406.13352(공격 대응과 정상 업무 성공을 함께 평가). P2: Shi et al., PromptArmor(2025), arXiv:2507.15219(LLM 기반 입력 정화, 특정 조건의 실험). P3: Li et al., AgentDyn(2026), arXiv:2602.03117(동적·개방형 작업에서 보안과 over-defense 한계).
- **DeepAgents 구현·관리형 Guard(62쪽).** W3: LangChain Custom middleware(node-style / wrap-style). W2: Human-in-the-loop(interrupt_on, 승인 결정, checkpointer). W1: Permissions(파일 권한 규칙 순서, 적용 범위, subagent 상속 조건). W4: Sandboxes(격리 실행, 네트워크 경계, 비신뢰 결과 처리). W7: Google Cloud Model Armor release notes(서울 리전 조건, 필터 버전 일정). W8: Feature availability for templates by region(data residency 설정에 따른 리전별 기능 범위).
- **모델 출처(63~66쪽).** H1 LFM2.5 Policy-Linter(15개 언어, ko 미포함, 최초 public commit 2026-07-28). H2 LFM2.5 PII-Detector(40개 유형, 16개 언어, 한국어 포함, 최초 public commit 2026-07-28). H3 LiquidAI 공개 모델 코드·어댑터. H4 Shieldstral-1.0-3B(기술 보고서 7/28, 공식 발표 8/4). H5 Nemotron-3.5-Content-Safety(HF 공개 2026-06-02, 4B, OpenMDW-1.1 + Gemma 조건). H6 granite-guardian-4.1-8b(2026.04). H7 Qwen3Guard-Gen-4B / Stream-4B. H8 SGuard-v1(2025-11-17). H9 Kanana Safeguard(prompt-2.1b, 8b). H10 gpt-oss-safeguard-20b. H11 Llama Guard 4. H13 Wolf Defender v2(공식 소개 2026-09-07, 영어/독일어 주요 평가). H14 GLiGuard(가중치 2026-05-09, 링크 수정 2026-08-11).

---

### 부록 A. 저장소 실습과의 대응 (저장소 덱 기준)

| 덱 쪽 | 덱 내용 | `Day08/` 실습 |
|---|---|---|
| 8·14·47 | Input은 도구 결과까지, 새로 유입된 비신뢰 데이터 단위 | `01_input_guard.py` (scope `("user",)` 대 `("user","tool_result")`) |
| 18·19·42·43 | Action Guard, PDP/PEP, Tool Wrapper | `02_action_guard.py`, `guardlab/defenses.py`의 `PermissionTable`·`guarded_call` |
| 20·30 | Output은 답변·전달 본문·초안, PII 구간 처리 | `03_output_guard.py`, `07_lfm_encoders.py` |
| 17·51 | 메모리 읽기·쓰기 검사, 파일 권한 순서 | `04_memory_permissions.py` |
| 21·50 | 승인 바인딩(tool + args_hash + 사용자), 재검증 | `05_hitl_approval.py` |
| 39·56 | 동일 조건 비교, 방어 하나 제거 | `06_compare.py` |
| 26~34·36 | Guard 모델 비교, UNKNOWN | `08_guard_models.py`, `guardlab/guards/` |

자세한 줄 번호는 `99-extras.md`에 있다.

### 부록 B. Drive 덱 「Day8_AI_Agent_Guardrails.pdf」와의 차이

Drive `read_file_content`가 돌려준 텍스트 전체로 확인했다. 원본 PDF는 내려받지 않아 쪽 번호와 그림은 확인하지 못했다. 아래는 장 단위 요약이고, 쪽 번호 대신 슬라이드 제목으로 가리킨다.

| 항목 | 저장소 덱 (`Day08/`) | Drive 덱 |
|---|---|---|
| 제목 | Agent Guardrails — 입력과 출력을 방어하고, 실행 권한을 코드로 강제하기 | AI Agent Guardrails — 행동을 통제하는 설계 |
| 분량 | 66쪽, 804KB, 2026-09-16 | 7.3MB, 2026-11-10 등록 (쪽수 미확인) |
| 축 | 방어 위치: Input / Action / Output + 모델 대 코드 | 판정 주체: Agent 로직(코드) / LLM Judge / Decision Model + 결합 |
| 첫 슬라이드 뒤 | OT, 6장 목차, 통제 지점 | 5장 + 부록 목차 |
| 마지막 | 모델 출처 Wolf Defender v2 · GLiGuard | 부록 "참조 아키텍처" |
| 주 예시 | Guard 전용 모델 카탈로그(SGuard, Kanana, LFM2.5, Shieldstral 등) | 공개 사고(Replit, EchoLeak, GitHub MCP 등), Claude Code·Codex·OpenAI Agents SDK의 실제 장치, TypeSafe Jev |
| 짝이 되는 실습 | `Day08/00~08` | `Day08_new/00~09` |

**Drive 덱 장별 요약.**

- **Chapter 1. 정의와 위협.**
  - LLM Guardrail 대 Agent Guardrail: 통제 대상이 생성된 텍스트(유해성, 주제 이탈, PII)에서 행동(도구 호출, 코드 실행, 파일·네트워크 접근, 상태 변경, 위임)으로 옮겨 간다. 최악의 결과는 부적절한 답변에서 데이터 유출·되돌릴 수 없는 실행·금전 손실·권한 상승으로, 강제 지점은 입력과 출력에서 도구 호출 전·후, 실행 환경, 자격증명, 메모리, 에이전트 간 메시지로 넓어진다. 실패하면 다시 답하면 되던 것이 한 번 놓치면 되돌릴 수 없게 된다. 정의: 에이전트가 움직이는 단계마다 허용할지, 고칠지, 사람에게 물을지, 막을지를 강제하는 장치 전체.
  - 루프와 강제 지점: 1 입력(Input rail: 인젝션 분류, PII 마스킹) → 2 계획(Plan 고정: 계획 검증, 목표 이탈 감시) → 3 도구 호출(Pre-tool 게이트: 정책, 인자 검증, 승인) → 4 실행(Sandbox: 파일·네트워크 격리) → 5 관찰(Post-tool 검사: 결과 스캔, 출처 태깅) → 6 메모리·출력(Output rail: 쓰기 검증, 유출 검사). 루프 바깥: 자격증명 격리, 정책 엔진과 게이트웨이, 예산과 circuit breaker, tracing과 audit log, kill switch.
  - 세 가지 Guardrail(판단 주체로 구분): Agent 로직 기반(코드·정책·실행 환경, 허용 또는 거부, 같은 입력에 항상 같은 결과, 모델이 우회할 수 없고 테스트 가능, 코드로 쓸 수 있는 규칙만 다룸) / LLM 모델 기반(범용 LLM Judge, 판정과 글로 쓴 사유, 맥락을 읽고 처음 보는 상황도 판단, 느리고 비싸고 읽은 글에 속을 수 있음) / Decision Model 기반(판정 전용 모델, 예: Jev, 정해진 형태의 답과 확률, 빠르고 저렴하고 확률로 임계값을 정함, 사유를 쓰지 못하고 긴 추론에 약함).
  - Lethal Trifecta(Simon Willison, 2025년 6월): 비공개 데이터 접근 + 믿을 수 없는 콘텐츠 읽기 + 외부 통신 능력. 셋이 한 에이전트에 모이면 인젝션 하나로 데이터를 빼낼 수 있다. 이 모델은 유출만 다루고 상태 변경·삭제는 다루지 않는다.
  - Agents Rule of Two(Meta, 2025-10-31): A 믿을 수 없는 입력 처리 / B 민감 시스템·비공개 데이터 접근 / C 상태 변경 또는 외부 통신. A+B, A+C, B+C는 자율 실행 가능(lower risk), A+B+C는 자율 실행 금지(사람의 승인 필요). 에이전트 여럿이 서로 오염시키는 경우는 다루지 못한다는 비판이 있다.
  - Replit DB 삭제 사고(2025년 7월, SaaStr Jason Lemkin 공개 기록): 12일 vibe coding, 코드 프리즈를 대화로 지시(지시는 프롬프트 안에만 존재), 9일차에 에이전트가 프로덕션 데이터 삭제, "롤백 불가"는 잘못된 보고였고 실제로는 복구됨. 막았어야 할 층 세 가지: 쓰기 명령을 거부하는 정책(런타임이 강제), 환경과 자격증명의 분리, 되돌릴 수 없는 실행 앞의 승인 절차와 dry run. Replit의 후속 조치(개발·프로덕션 DB 자동 분리, 원클릭 복구, planning-only 모드)는 모두 모델 바깥의 장치다.
  - 사고의 공통 원인 표: 지나친 권한 / 신뢰 경계 없음 / 말로만 있던 규칙. 사고 목록은 Replit, EchoLeak, GitHub MCP, MCP Tool Poisoning, Supabase MCP, PocketOS.
- **Chapter 2. Agent 로직 기반 Guardrail.**
  - Input Guardrail: 인젝션·jailbreak 분류, 주제 범위 제한, PII 탐지와 마스킹. OpenAI Agents SDK에서는 체인의 첫 에이전트에서만 실행되고 기본값은 에이전트와 동시 실행이다. 첫 턴부터 부작용 있는 도구를 부를 수 있으면 `run_in_parallel=False`로 검사를 먼저 끝낸다. 한계: 간접 인젝션은 도구 결과에 있어 여기서 못 막는다.
  - Output Guardrail의 한계: 형식·말투·사실처럼 틀려도 고칠 수 있는 규칙에 알맞다. tripwire가 걸려도 이미 끝난 도구 호출은 되돌릴 수 없다. 부작용은 출력이 아니라 도구 호출 전에 막는다.
  - Tool 인터셉트 지점 비교:

    | 프레임워크 | Pre-tool 지점 | 차단 방법 | Post-tool 지점 |
    |---|---|---|---|
    | Claude Code | PreToolUse hook | exit code 2 또는 `permissionDecision: deny` | PostToolUse hook |
    | OpenAI Agents SDK | tool input guardrail | tripwire 예외 또는 reject content | tool output guardrail |
    | LangChain 1.x | `wrap_tool_call` middleware | 예외, 인자 수정, HITL interrupt | `wrap_tool_call` 이후 |
    | Google ADK | before_tool_callback | dict를 반환하면 실행을 건너뜀 | after_tool_callback |
    | AWS AgentCore | Gateway Policy Engine | Cedar forbid, 기본 거부 | Response Interceptor |
    | NeMo Guardrails | execution rails | 액션 입력 검증 실패 | 액션 출력 검증 |

  - PreToolUse Hook 흐름(Claude Code): 모델이 도구 호출 요청 → PreToolUse hook → 권한 규칙 평가 → 샌드박스에서 실행. hook의 결정은 deny(차단, 거부 이유를 모델에게 알려 다른 방법을 찾게 함) / ask(자동 승인 대상이라도 사람에게 확인) / allow + `updatedInput`(인자를 재작성한 뒤 실행. 예: 위험한 플래그 제거, 경로 한정). PostToolUse는 이미 실행된 뒤라 exit 2가 피드백만 주고 되돌리지 않는다.
  - Deny wins: 허용은 모든 층이 동의해야 하고 거부는 한 층이면 충분하다. hook의 deny는 bypassPermissions 모드에서도 차단하고, hook의 allow는 settings의 deny·ask 규칙을 못 이긴다. Cedar(AgentCore Policy)도 forbid가 permit을 이기고 맞는 permit이 없으면 기본 거부다.
  - 위험도 등급: T0 읽기 전용(자동 허용) / T1 되돌릴 수 있는 쓰기(작업 디렉터리 안 파일 편집, 브랜치 커밋 — 자동 허용 + 체크포인트) / T2 외부 통신·공유 상태 변경(이메일, PR 생성, 외부 API POST, 패키지 설치 — 정책 기반 판단: 분류기, allowlist 또는 승인) / T3 되돌릴 수 없고 영향이 큼(프로덕션 DB 쓰기, 결제, 삭제, 권한 변경, force push — 항상 사람 승인 + dry run + 별도 자격증명). 등급이 만드는 사각지대: Claude Code auto mode는 읽기 전용 도구와 프로젝트 디렉터리 안 파일 편집을 분류기 없이 승인하고, 독립 평가(arXiv 2604.04978)가 이 면제를 사각지대로 지적했다.
  - 예산·상한·되돌리기: 모델 호출·도구 호출 상한, 스텝·비용 예산, checkpoint와 rollback, dry run, idempotency key. LangChain의 `ToolCallLimitMiddleware`(전역 또는 도구별)와 `ModelCallLimitMiddleware`. 한도 판정을 승인 요청보다 먼저 둔다(예산을 넘긴 작업에 승인을 묻는 낭비 방지). 되돌릴 수 있으면 자율을, 없으면 승인을.
  - Tripwire(중단) 대 Deny-and-continue(계속): tripwire는 예외로 종료하고 잘못 막으면 세션이 실패한다. deny-and-continue는 거부 사유를 도구 결과로 돌려주고 계속하며 잘못 막아도 재시도 한 번이다. 전자는 명백한 위반·입력 단계에, 후자는 장시간 자율 작업·도구 호출 단계에 맞는다. 계속 진행시키려면 circuit breaker가 필요하다: Claude Code auto mode는 분류기가 3회 연속 또는 세션 내 20회 차단하면 수동 승인으로 돌아간다.
  - 샌드박스: 파일시스템 격리(쓰기는 작업 디렉터리로 제한, 하위 프로세스 전체에 적용) + 네트워크 격리(기본 차단, 프록시로 allowlist 도메인만). 둘 중 하나만 있으면 뚫린다(네트워크 격리가 없으면 SSH 키 유출, 파일시스템 격리가 없으면 샌드박스 탈출). Anthropic 자체 측정으로 승인 프롬프트 84% 감소. 구현은 macOS Seatbelt와 Linux bubblewrap.
  - Credential 격리: 비밀을 모델 컨텍스트·에이전트가 읽는 파일시스템·환경변수 밖에 두고, 프록시나 게이트웨이가 요청 시점에 주입한다. 토큰은 수명을 짧게, 범위를 좁게. 토큰의 권한 범위가 곧 피해의 최대치다.
  - Policy as Code: Cedar 예시(환불 도구 호출의 `context.input.amount > 500`이면 forbid). 정책이 에이전트 코드 밖에 있어 보안팀이 코드를 고치지 않고 규칙을 바꾼다. LOG_ONLY 모드로 먼저 기록만 하다가 단계적으로 적용한다. 한계: Gateway를 거치지 않는 직접 호출은 경계 밖이다.
  - 메모리와 서브에이전트 권한: ASI06 메모리 쓰기를 도구 호출처럼 검증하고 provenance 태그를 함께 저장한다. 감시 에이전트는 원문이 아니라 행동과 사용자 의도만 보게 한다. ASI03 권한 상속은 줄이기만 한다(부모와 자식의 교집합). ASI07 다른 에이전트의 출력도 비신뢰 입력으로 다루고 정해진 형식의 요약만 돌려받는다.
  - 인젝션 방어 패턴 6종(Beurer-Kellner 외, arXiv 2506.08837): Action-Selector / Plan-Then-Execute / LLM Map-Reduce / Dual LLM / Code-Then-Execute(CaMeL) / Context-Minimization. 공통 원칙: 믿을 수 없는 입력을 읽은 뒤에는 그 입력 때문에 중요한 행동이 일어나지 않게 막는다.
  - 승인 피로: Claude Code 권한 프롬프트 수락률 93%(2026-03 엔지니어링 포스트)·97%(2026-08 기본값 전환 발표), 위장된 위험 명령을 잡아낸 비율 사람 13.6% 대 auto mode 분류기 89%. 대응 세 가지: 물어볼 일을 줄인다(샌드박스 안은 묻지 않음), 흔한 승인은 맡긴다(분류기·리뷰어 에이전트), 미리 정해 둔다(allowlist·정책 조건).
  - 승인 UI: 모델이 쓴 요약이 아니라 도구가 받을 실제 인자를 보여 준다(예: `Bash: rm -rf ./build ../shared/cache`, 영향 범위 "작업 디렉터리 밖 경로 1개 포함", 되돌리기 불가, 위험 등급 T3, 버튼 승인 / 수정 / 거부). 승인율을 모니터링하고 거의 100%면 재설계한다.
  - 가드레일의 고장: Claude Code 특정 버전에서 PreToolUse hook의 deny가 무시됐다는 버그 보고(GitHub issue #37210, #43407). hook만으로 보안 경계가 되지 않으므로 OS 샌드박스와 자격증명 격리를 함께 두고, deny 정책이 실제로 차단하는지 CI에서 회귀 테스트하고 하네스 업그레이드 때마다 다시 돌린다.
- **Chapter 3. LLM 모델 기반 Guardrail.**
  - LLM Judge의 역할: 코드로 쓸 수 없는 규칙(이 호출이 사용자가 시킨 일인가, 요청 범위를 넘지 않았는가, 외부 문서의 지시를 따르고 있지 않은가)을 에이전트와 분리된 LLM에게 묻는다. 두는 자리는 입력 / 도구 호출(가장 중요) / 궤적(예: LlamaFirewall의 AlignmentCheck).
  - Judge에게 주는 입력: 보여 주는 것은 사용자 요청 원문, 제안된 도구 호출과 인자, 조직의 판정 기준. 가리는 것은 도구 결과·외부 문서 원문, 에이전트의 설명과 추론. 대가로 값의 출처를 알 수 없으므로 그런 건은 사람에게 넘긴다. Claude Code auto mode 분류기가 같은 선택을 했다.
  - 판정 결과 구조화: `Verdict(decision: allow|deny|ask, reason)`을 structured output으로 받고, 예외가 나면 `ask`로 처리한다(실패하면 닫힘).
  - Auto Mode 2단계 분류기: 등급 면제(읽기 전용, 프로젝트 안 편집) → Stage 1 빠른 yes/no 필터(단독 오탐률 8.5%) → Stage 2 플래그된 것만 추론으로 재평가(전체 오탐률 0.4%) → 허용 또는 deny-and-continue. 실제 트래픽 10,000건 오탐률 0.4%, 실제 overeager 행동 52건 미탐률 17%, 합성 유출 시도 1,000건 미탐률 5.7%. 넓은 allow 규칙(전체 셸 접근 등)은 auto mode에서 무시된다.
  - 분류기의 가치와 비용(Meta LlamaFirewall, arXiv 2505.03574, AgentDojo ASR): 무방어 17.63% → PromptGuard 2 7.53% → AlignmentCheck 2.89% → 결합 1.75%. 유틸리티 47.73 → 42.68.
  - LLM Judge의 약점: 호출마다 1~2초(소형 Judge 지연 중앙값 1.7초·1.9초), 인젝션에 속을 수 있음, 확신 값이 여섯 가지뿐이라 임계값을 세밀하게 정하기 어려움, 모델 버전에 따라 판정이 달라짐(회귀 세트로 재확인).
- **Chapter 4. Decision Model 기반 Guardrail.**
  - Decision Model: 상태(state)와 타입이 정해진 질문을 받고 선택지·점수·확률만 돌려준다. Jev는 TypeSafe가 2026년 9월 공개했다. 질문 타입 4종: Noul(참일 확률 0~1), Choice, Score, Box. "위험한가"라고 묻지 않고 범위·유형·가역성을 나눠 묻고, 합치는 규칙은 코드에 둔다.
  - 확률과 임계값: `in_scope` 0.9 이상이고 되돌릴 수 있으면 바로 실행, 0.3 미만이면 거부(사유를 돌려주고 계속), 0.3 이상 0.9 미만이면 판정을 미루고 LLM Judge나 사람에게 넘긴다. TypeSafe 문서의 출발점은 0.7 초과 예 / 0.3 미만 아니오다. 되돌릴 수 없는 행동은 0.9를 넘어도 사람 확인을 함께 요구한다. confidence는 정답 확률이 아니다.
  - 배치 위치: 입력(새로 들어온 도구 결과에 지시가 있는가), 도구 호출(요청 범위 안인가, 가역성), 출력(승인받지 않은 약속, 비밀 값). 숫자 비교처럼 코드로 쓸 수 있는 규칙은 모델에 맡기지 않는다.
  - LLM Judge와 비교(OpenRouter 88건, Arize 데모): 사람 라벨 일치율 95.5 대 94.3, Brier 0.043 대 0.054, 1,000건 비용 $0.021 대 $0.114, 지연 중앙값 171ms 대 1,662ms(데모 104ms 대 1,915ms), 전문가 평가와의 상관 0.47 대 0.72(SummEval 50건).
  - 한계(Rao·Callison-Burch, arXiv 2609.29769): Decision Model이 확신하며 틀린 판정의 85% 이상을 소형 LLM Judge도 똑같이 틀림, 재판정으로 오른 정확도 최대 2.7점, LLM Judge 비용 16~357배·시간 5~350배. 사유가 없고, API 호출이라 state가 외부로 나간다.
- **Chapter 5. 결합과 구현.**
  - Attacker Moves Second(Nasr·Carlini·Tramèr 외, arXiv 2510.09023): 적응형 공격으로 최근 방어 12개 중 대부분에서 성공률 90% 이상. 탐지에만 기대는 방어는 언젠가 뚫린다고 보고 설계한다.
  - 분포 불일치: PromptGuard 2가 새 SaaS 통합 시나리오의 held-out 공격을 0% 탐지(AgentRedBench), 인젝션 문장으로 학습한 분류기를 도구 호출 내용에 쓰니 정상 행동의 36%를 차단(Parallax, arXiv 2604.12986), 재구성한 control-flow hijacking이 정렬 검사를 80%(코딩)·67%(컴퓨터 사용) 우회(arXiv 2510.17276).
  - 모델 판단의 신뢰 범위: 믿어도 되는 곳은 1차 필터, 되돌릴 수 있는 행동의 자동 승인, 사람이 볼 대상 고르기, 사후 모니터링. 믿으면 안 되는 곳은 되돌릴 수 없는 행동을 혼자 막는 자리, 학습한 적 없는 유형의 입력, 비신뢰 원문을 그대로 읽는 감시 모델, 방어를 아는 공격자를 고려하지 않은 평가.
  - 판정 순서: 1 코드 규칙(지연 거의 없음) → 2 Decision Model(100ms대) → 3 LLM Judge(1~2초) → 4 사람(분 단위). 항상 Sandbox와 자격증명 격리로 피해 범위를 제한한다.
  - DeepAgents 설계도와 `GuardMiddleware.wrap_tool_call` 코드: 정책 위반이면 deny → READ_ONLY면 바로 실행 후 scan → `ask_jev`로 (fit, risk) → fit < 0.3 deny → risk ≥ 1.5면 사람 필요 → fit < 0.9면 `llm_judge` → 필요하면 `interrupt` → 실행 후 결과 scan. 거부는 같은 `tool_call_id`의 ToolMessage로 돌려준다. interrupt로 멈춘 함수는 재개하면 처음부터 다시 실행되므로 앞의 검사는 반복해도 되는 것만 둔다. `interrupt_on`은 판정과 무관하게 항상 사람이 봐야 하는 도구에만 쓴다. 격리된 서브에이전트는 부모의 custom middleware를 물려받지 않으므로 서브에이전트마다 Guard를 다시 지정한다. permissions는 sandbox 경로에는 적용되지 않으므로 `/memories/`처럼 다른 backend로 보낸 경로에만 건다. deepagents 0.7.35에서 동작 확인이라고 적혀 있다.
  - 레이어 배치 의사결정 트리: 1 되돌릴 수 있는가(없으면 T3) → 2 Rule of Two 몇 점인가(3점이면 다리 하나를 끊음: 세션 분리, 도구 제거, 스코프 축소, egress 차단) → 3 코드로 정확히 쓸 수 있는가 → 4 정책이 실패하면 무엇이 피해를 막는가 → 5 사후에 무엇을 알 수 있는가. 강제(enforce)할 규칙은 어기면 되돌릴 수 없거나 피해가 밖으로 나가는 규칙, 부탁(prompt)해도 되는 규칙은 말투·형식·주제.
  - 설계 체크리스트 10항: Rule of Two 점수 / 모든 도구의 T0~T3 분류와 T3의 승인·별도 자격증명 / 프롬프트에만 있는 금지 규칙을 정책으로 / 비밀의 노출 여부 / egress 기본 거부와 allowlist, 렌더링 유출 / MCP 서버 pinning과 description 변경 감지 / 서브에이전트 권한 축소 상속 / 예산·스텝·도구 호출 상한과 circuit breaker / 승인 UI의 정확한 인자와 승인율 모니터링 / deny 정책의 CI 테스트와 적응형 레드팀.
  - 평가와 CI: AgentDojo(유틸리티와 ASR을 함께), InjecAgent, AgentHarm, ASB. 방어를 아는 공격으로 평가하고 오탐률·미탐률은 데이터셋·표본 크기와 함께 밝힌다. CI에는 정책 규칙 단위 테스트, 알려진 공격 회귀 세트, 정상 작업 회귀 세트를 둔다.
- **부록.** 용어 지도(Guardrail / Policy / Permission / Sandbox / Harness / Eval / Observability), 분류 방식 4가지(적용 지점 / 결정 방식 / 강제 수준 / 스택 위치), Google의 Hybrid Defense in Depth, OWASP Agentic Top 10(ASI01~10과 1차 설계 대응), 사례 EchoLeak(CVE-2025-32711) · GitHub MCP Toxic Flow · MCP Tool Poisoning(Poisoning / Shadowing / Rug pull) · Supabase MCP · PocketOS, Codex의 두 축(sandbox mode × approval policy), MCP 인가(2026-07-28 스펙)와 Gateway 패턴, CaMeL(949개 공격 중 0건 성공, 작업 성공률 77% 대 무방어 84%, 입력 토큰 중앙값 2.82배), 제품 비교표(Claude Code / OpenAI Agents SDK / Codex / LangChain 1.x / AWS AgentCore / Google ADK), 참조 아키텍처.

---

### 확인 필요

덱이 외부 사실에 기대는 주장이다. 확인한 것은 URL을 붙였고, 확인하지 못한 것은 `미확인`으로 적었다. 확인은 2026-11-11에 해당 페이지를 직접 열어 했다.

**저장소 덱(66쪽) 쪽의 주장**

1. DeepAgents 파일 권한은 선언 순서대로 첫 일치 규칙을 쓰고 일치가 없으면 허용한다. 내장 파일 도구에만 적용되고 custom 도구·MCP 도구·`execute`는 범위 밖이다(51쪽). (공식 문서 확인: https://docs.langchain.com/oss/python/deepagents/permissions)
2. Subagent는 부모 permissions를 기본으로 물려받고, 격리(isolated) Subagent는 부모의 custom middleware를 물려받지 않는다(52쪽). fork 방식은 물려받는다. general-purpose Subagent는 부모와 같은 도구를 갖는다. (공식 문서 확인: https://docs.langchain.com/oss/python/deepagents/subagents)
3. `interrupt_on`의 `allowed_decisions`, checkpointer 필수, 같은 `thread_id`로 재개(49·50쪽). (공식 문서 확인: https://docs.langchain.com/oss/python/deepagents/human-in-the-loop) 문서의 결정 종류는 approve / edit / reject / respond 네 가지다.
4. Middleware hook 여섯 개와 `jump_to`(46쪽). (공식 문서 확인: https://docs.langchain.com/oss/python/langchain/middleware/custom)
5. Llama Prompt Guard 2의 512-token 컨텍스트(61쪽 W5). (공식 문서 확인: https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M) 카드의 평가 언어 8개에 한국어는 없다.
6. gpt-oss-safeguard는 정책을 입력으로 받는 추론형 Guard, 20b / 120b, Apache 2.0(33쪽). (공식 문서 확인: https://huggingface.co/openai/gpt-oss-safeguard-20b) 발표일 2025-10-29는 카드에서 확인하지 못했다(미확인).
7. SGuard-JailbreakFilter-2B-v1은 한국어·영어 중심, 권장 입력 8K, 2025-11-17, Apache 2.0(34쪽). (공식 문서 확인: https://huggingface.co/SamsungSDS-Research/SGuard-JailbreakFilter-2B-v1)
8. LFM2.5 PII-Detector는 40개 유형·16개 언어·custom code(28쪽). (공식 문서 확인: https://huggingface.co/LiquidAI/LFM2.5-Encoder-350M-PII-Detector) 16개 언어에 한국어가 들어 있는지와 라이선스 정식 명칭은 카드 본문에서 확인하지 못했다(미확인). 저장소 README의 실측은 한국어 문서에서 구간 분절과 누락을 보고한다.
9. AgentDojo, arXiv:2406.13352(61쪽 P1). (공식 문서 확인: https://arxiv.org/abs/2406.13352)
10. OWASP Top 10 for Agentic Applications 2026(60쪽 O1). 제목과 공개일 2025-12-09. (공식 문서 확인: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) ASI01~10 항목 제목은 저장소 `Day08_new/docs/sources/05_verification.md`가 공식 PDF로 확인했다고 적는다.
11. Wolf Defender v2(2,048-token, 영어·독일어), GLiGuard, LFM2.5 Policy-Linter(15개 언어, ko 미포함), Shieldstral-1.0-3B(12개 언어, ≤ 32K, 2026-08-04), Nemotron 3.5 Content Safety(12개 언어, 2026-06-02), Qwen3Guard(3단계 라벨, 119개 언어), Llama Guard 4 12B, Granite Guardian 4.1 8B, Kanana Safeguard의 카드 표기(26~34쪽, 63~66쪽): 미확인(모델 카드를 열지 않았다).
12. PromptArmor(arXiv:2507.15219), AgentDyn(arXiv:2602.03117), HyperCLOVA X THINK(arXiv:2506.22403), NeMo Guardrails(EMNLP 2023 Demo), NIST AI RMF / GenAI Profile, OPA(60~61쪽): 미확인.
13. Google Cloud Model Armor의 서울 리전 조건과 리전별 기능 범위(62쪽 W7·W8): 미확인.

**Drive 덱 쪽의 주장 (에이전트 가드레일 설계에 직접 쓰이는 것 위주)**

14. Claude Code PreToolUse hook은 exit code 2 또는 `permissionDecision: "deny"`로 도구 호출을 막고, PostToolUse의 exit 2는 이미 실행된 호출을 되돌리지 못한다. `updatedInput`은 입력 객체 전체를 바꾼다. (공식 문서 확인: https://code.claude.com/docs/en/hooks) 문서의 `permissionDecision` 값은 allow / deny / ask / defer 네 가지이고, 여러 hook의 결정이 다르면 deny > defer > ask > allow 순이다. 덱은 defer를 적지 않았다.
15. hook이 allow를 돌려줘도 settings의 deny·ask 규칙은 그대로 평가된다. 권한 규칙은 deny → ask → allow 순으로 평가한다. (공식 문서 확인: https://code.claude.com/docs/en/permissions)
16. hook의 deny가 bypassPermissions 모드에서도 차단한다: 미확인(읽은 범위의 hooks·permissions 문서에서 이 문장을 찾지 못했다).
17. auto mode 수치: 수락률 93%, Stage 1 오탐률 8.5%, 전체 오탐률 0.4%(실제 트래픽 10,000건), 미탐률 17%(overeager 52건)·5.7%(합성 유출 1,000건), 분류기는 사용자 메시지와 도구 호출만 보고 도구 결과는 뺀다, 읽기 전용 도구와 프로젝트 안 편집은 분류기를 거치지 않는다, 3회 연속 또는 총 20회 차단이면 사람에게 넘긴다, 임의 코드 실행을 주는 넓은 allow 규칙은 auto mode 진입 시 빠진다. (공식 문서 확인: https://www.anthropic.com/engineering/claude-code-auto-mode , https://code.claude.com/docs/en/permission-modes) 모두 벤더 자체 측정이다.
    - 불일치 1: 덱은 헤드리스 모드에서 "종료"라고 적는다. 엔지니어링 포스트(2026-03-25)는 그렇게 적지만, 현재 permission-modes 문서는 `-p` 실행에서 그 행동만 실행하지 않고 작업을 계속한다고 적는다.
    - 불일치 2: 덱은 "2026년 8월 14일부터 Pro·Max·Team 기본값"이라고 적는다. 현재 문서는 v2.1.283 이상에서 모든 요금제의 대화형 세션 시작 모드가 auto이고 그 이전 버전에서는 Pro·Max·Ultra·Team만이라고 적는다. 날짜는 미확인.
    - 수락률 97%, 사람 13.6% 대 분류기 89%: 미확인.
18. Claude Code 샌드박스: 권한 프롬프트 84% 감소(내부 사용 기준), 파일시스템·네트워크 격리가 둘 다 필요, bubblewrap·Seatbelt, 2025-10-20. (공식 문서 확인: https://www.anthropic.com/engineering/claude-code-sandboxing)
19. PreToolUse deny가 무시됐다는 버그 보고(GitHub issue #37210, #43407): #37210은 존재하고 제목도 같은 취지다. 다만 2026-03-21에 "not planned"로 닫혔고, 보고자는 자기 hook의 종료 코드와 출력 형식 문제였다고 결론지었다(Anthropic 쪽 답변은 없다). (확인: https://github.com/anthropics/claude-code/issues/37210) Claude Code 결함으로 확정된 사례가 아니므로 "hook은 CI에서 회귀 테스트한다"는 교훈만 가져간다. #43407은 미확인.
20. Agents Rule of Two: 세 속성 [A][B][C], 한 세션에 둘까지, 셋이 다 필요하면 자율 실행하지 않고 사람 승인 등 감독이 필요, 2025-10-31. (공식 문서 확인: https://ai.meta.com/blog/practical-ai-agent-security/) "safe를 lower risk로 고쳤다"는 표기 변경은 본문 텍스트에서 확인하지 못했다(미확인. 그림 안 표기일 수 있다).
21. Lethal trifecta, 2025-06-16. (공식 문서 확인: https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
22. OpenAI Agents SDK: input guardrail은 첫 에이전트에서만, output guardrail은 최종 출력을 내는 에이전트에서만 실행, 기본은 에이전트와 병렬이고 `run_in_parallel=False`면 검사가 먼저 끝난다, tool guardrail은 handoff와 hosted 도구에 적용되지 않는다. (공식 문서 확인: https://openai.github.io/openai-agents-python/guardrails/)
23. Codex: `sandbox_mode`는 read-only / workspace-write / danger-full-access. (공식 문서 확인: https://learn.chatgpt.com/docs/config-file/config-reference) 불일치: 덱은 `approval_policy` 값을 untrusted / on-request / never / granular로 적지만, 현재 문서는 on-request / never / granular 객체만 받고 `untrusted`는 지원하지 않으며 `on-failure`는 deprecated라고 적는다. workspace-write의 네트워크 기본 꺼짐은 미확인.
24. MCP 2026-07-28 스펙: 클라이언트가 인가 응답의 `iss`를 검증, 자격증명을 발급한 인가 서버에 바인딩, Dynamic Client Registration deprecated(Client ID Metadata Documents 권장). (공식 문서 확인: https://modelcontextprotocol.io/specification/2026-07-28/changelog) 2025-11-25 개정 항목(점진적 스코프 동의, URL mode elicitation)은 미확인.
25. The Attacker Moves Second: 방어 12개, 대부분에서 공격 성공률 90% 이상, 원 논문들은 0에 가까운 성공률을 보고. (공식 문서 확인: https://arxiv.org/abs/2510.09023)
26. CaMeL: AgentDojo 작업의 77%를 보안 보장 상태로 해결(무방어 84%). (공식 문서 확인: https://arxiv.org/abs/2503.18813) "949개 공격 중 0건", "입력 토큰 2.82배"는 초록에 없어 미확인.
27. LlamaFirewall(arXiv 2505.03574)의 ASR 17.63 → 7.53 / 2.89 / 1.75, 유틸리티 47.73 → 42.68: 논문은 존재하나 수치는 초록에 없어 미확인. (논문 확인: https://arxiv.org/abs/2505.03574)
28. Design Patterns for Securing LLM Agents(arXiv 2506.08837)의 패턴 6종 이름: 논문은 존재하나 패턴 이름은 초록에 없어 미확인. (논문 확인: https://arxiv.org/abs/2506.08837)
29. TypeSafe Jev(2026-09 공개, 질문 타입 4종, 0.7 / 0.3 출발점), OpenRouter·Arize 비교 수치, arXiv 2609.29769: 미확인. 저장소 `docs/sources/03_decision_model_cases.md`는 TypeSafe 문서와 OpenRouter cookbook을 [1차], 출시 날짜·지연을 [2차]로 적는다.
30. 사고 사례(Replit, EchoLeak, GitHub MCP, MCP Tool Poisoning, Supabase MCP, PocketOS): 직접 확인하지 않았다. 저장소 `docs/sources/`의 확인 수준은 `99-extras.md` "공개 사례 출처"에 옮겼다. PocketOS(2026-04, The Register)와 MCP Tool Poisoning(Invariant Labs, 2025-04-01)은 그 문서에도 없다(미확인).
31. arXiv 2604.04978(auto mode 등급 면제 사각지대), AgentRedBench(PromptGuard 2 held-out 0%), Parallax arXiv 2604.12986(정상 행동 36% 차단), arXiv 2510.17276(정렬 검사 우회 80% / 67%), Google "An Introduction to Google's Approach for Secure AI Agents"(2025-05), AWS AgentCore Policy(Cedar), Google ADK 콜백: 미확인.
32. 버전 표기가 자료마다 다르다. Drive 덱은 deepagents 0.7.35, `Day08_new/docs/architecture.md`는 0.7.32(langchain 1.4.7, langgraph 1.2.19), `Day08/dcode-analysis`는 0.7.14 기준이다. 문서 확인(1~4번)은 2026-11-11 현재 공식 문서 기준이라 버전별 차이는 따로 대조하지 않았다.
