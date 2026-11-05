## Day4 교재 — Advanced Agent / MCP / Skills / Eval

- 원본: `Day4_Advanced_Agent_MCP_Skills_Eval.pdf` (Google Drive fileId `1HzUyHhemg7UXD5Uw6TM3fmYJ76mppuK7`)
- 덱 제목: **MCP · Skills로 Agent 능력 개선하기** (강사: 전현준)
- 관통 예제: 합성 사고 **INC-017** (근거 E01–E03), Skill `incident-analysis` / `rag-research`
- 주의: PDF 텍스트 추출본 기반 요약. 다이어그램은 추출된 라벨로 재구성했고, 코드 블록은 줄바꿈이 깨진 원문을 원래 형태로 복원했다(토큰·식별자는 원문 그대로).

---

### 목차 (덱의 섹션 구조 그대로)

0. 도입 — Agent의 능력은 어디에서 개선될까요? / 한 장으로 보는 MCP와 Skills의 조합
1. **Chapter 1. 답변을 넘어 행동으로** (p.06~) — 도구를 붙였는데도 업무를 끝내지 못하는 이유
2. **Chapter 2. Agent가 잘 쓰는 Tool** (p.11~) — Tool이 동작하는 것 vs Agent가 잘 사용하는 것
3. **Chapter 3. Skills로 업무 수행법을 축적합니다** (p.17~) — 긴 프롬프트 파일 vs 재사용 가능한 Skill
4. **Chapter 4. MCP로 실행 능력을 넓힙니다** (p.31~) — 정보를 읽고 외부 시스템을 다루는 능력 연결
5. **Chapter 5. 실패를 고치고 개선을 증명합니다** (p.45~) — Skill 수정 후 더 잘 수행하는지 판단
6. **Chapter 6. RAG를 업무 Skill로 조합합니다** (p.61~) — 검색 결과 받기 vs 근거로 업무 끝내기
7. **Chapter 7. 검증된 Skill을 배포하고 통합합니다** (p.68~) — 조직 공유 Skill의 품질·접근 경계 승인
8. 마무리 — Capstone / 다른 업무 적용 / "연결하고, 평가하고, 검증된 능력을 공유합니다"

---

### 섹션별 핵심 내용

#### 0. 도입

**Agent의 능력은 어디에서 개선될까요?** — 모델 교체만이 해법은 아니다. 네 가지 축으로 나눈다.

| 축 | 질문 | 개선 수단 |
|---|---|---|
| ACCESS (실행 범위) | 사내 문서·티켓·API에 접근할 수 있는가? | MCP로 능력 연결 |
| PROCEDURE (업무 수행법) | 언제 무엇을 어떤 순서로 해야 하는가? | Skills로 절차 축적 |
| EXECUTION (정확한 실행) | 계산·검사·상태 변경을 정확히 처리하는가? | Tool / Script |
| IMPROVEMENT (반복 품질) | 수정 후에도 더 잘 수행하는가? | Eval → 검토 → 공유 |

- MCP와 Skills는 모델을 재학습하지 않는다. 개선 대상은 **Agent 시스템의 수행 능력**이다.

**한 장으로 보는 MCP와 Skills의 조합** (다이어그램)
- 사용자 요청 → **Deep Agent** → (관찰 → 다음 행동 / 종료) 루프
- Deep Agent가 세 경로를 사용: **Skill Bundle**(name / description, SKILL.md / resources), **Local Tool**(계산·검증), **MCP Tools**(검색·티켓 서비스)
- "절차를 읽는 경로"와 "서비스 도구를 실행하는 경로"를 분리
- Skill은 실행 프로그램이 아니라 **절차 자원**. Agent가 이를 읽고 Tool을 선택한다.
- 요약: *MCP가 제공한 실행 능력을, Skill이 안내하는 절차에 따라 Agent가 사용한다.*

#### Chapter 1. 답변을 넘어 행동으로

**모델은 요청하고, 호스트는 실행합니다** — Function Calling은 자연어 판단과 외부 시스템 실행 사이의 구조화된 계약.
- ① 모델 선택: Tool 이름 + 인자
- ② 호스트 검증: 형식 · 권한 · 승인
- ③ 실제 실행: 함수 / 외부 API
- ④ 결과 관찰: 상태 · 값 · 오류
- ⑤ 관찰 결과를 다시 모델에 전달 → 후속 행동 또는 종료
- "처리했습니다"라는 문장이 아니라 **실행 결과와 외부 상태를 확인**한다.

**같은 Agent를 네 단계로 확장** (설계 비교이며 실측 결과 아님)

| 단계 | 추가하는 것 | 새로 가능한 일 | 남는 확인 과제 |
|---|---|---|---|
| A · 기본 Agent | 모델 + 기본 지시 | 제공된 정보로 설명 | 외부 기록 접근 불가 |
| B · + MCP Tools | 검색·티켓 기능 연결 | 기록 조회·상태 확인 | 올바른 절차를 따르는가? |
| C · + Skills | 업무별 절차·자료 | 근거·정책·검증을 조합 | 선택·수행 누락은 없는가? |
| D · + Evaluation | 고정 평가셋·회귀 검사 | 실패를 찾아 최소 수정 | 개선과 퇴행을 구분 |

- MCP 연결은 **접근 범위**를, Skill은 **수행 방식**을 바꾼다. 성공 여부는 따로 평가한다.

**Tools · MCP · Skills는 다른 층입니다**
- 01 **Tool** — 무엇을 실행할 것인가? 예: `search_policy(query)`, `validate_timeline(events)`
- 02 **MCP** — 어떤 표준으로 연결할까? 문서·티켓 서비스, 독립 배포 · 여러 Host
- 03 **Skill** — 언제 어떤 절차를 따를까? 근거 → 정책 → 검증 → 보고 / 승인 후 반영
- "MCP냐 Skill이냐"가 아니다. MCP Tool을 Skill과 함께 쓰는 구조가 가능하다.

#### Chapter 2. Agent가 잘 쓰는 Tool

**Deep Agents는 실행을 연결하는 Harness입니다**
- Tool-calling Model: 행동 선택, 인자 생성, 관찰 후 다음 판단
- Deep Agents Harness: Tool 실행 · 파일 / Context · Skill 발견과 읽기 · 중단 · 재개 · 실행 기록
- 연결 대상: Local / MCP Tools, Skills / 파일 자원
- 공통 통제: **인증 · 권한 · 승인 · 예산 · 감사** — 실행 경로에서 적용
- 모델은 판단을 제안할 뿐, 실제 접근 범위·변경 가능 범위는 실행 환경이 결정한다.

**좋은 Tool은 선택 가능한 계약입니다** — 이름·설명·인자만 보고 언제 호출할지 알 수 있어야 한다.

불분명한 계약:
```python
def find_policy(q):
    ...
```

개선한 계약 (구현부 생략):
```python
def search_policy(
    query: str,
    top_k: int = 5,
    include_archived: bool = False,
) -> list[dict]:
    """Search authoritative policy evidence.
    Use when a policy decision needs sources.
    Return source IDs and short excerpts.
    """
    ...
```
- 무슨 행동인지는 **Tool description**에, 여러 행동의 순서는 **Skill**에 둔다.

**Tool 결과는 다음 판단의 재료입니다** — 핵심 값과 상태·출처를 작게 반환, "자료 없음"과 "실행 실패"를 구분.

검색 응답 (교육용 계약):
```json
{"status": "ok",
 "index_version": "snap-02",
 "evidence": [{
   "source_id": "E01",
   "observed_at": "00:01 UTC",
   "summary": "Error rate increased"
 }]}
```
- 돌려줘야 할 정보: 결과(무엇을 관측?) / 출처(어디서?) / 조건(어느 시점·버전?) / 상태(성공·빈 결과·오류?)
- 불필요한 원문 덤프는 줄인다.
- 구조화된 데이터가 *있다*는 사실과 모델이 그 내용을 *실제로 받았다*는 사실은 다르다.

**함수의 정확성과 Agent의 사용을 나눕니다**
1. WITHOUT MODEL — Tool / Script: 정상·경계·실패 입력, 타입·시간대·근거 ID, 같은 입력 → 같은 기대값
2. WITH MODEL — 선택과 인자: 필요한 Tool을 골랐는가? 정확한 입력을 만들었는가? 불필요한 호출도 평가
3. END-TO-END — 업무 완료: 관측 결과로 요청을 해결했나? 미확인 사실을 구분했나? 권한·근거·실제 상태 확인
- 단위 테스트 통과는 Tool 구현의 증거일 뿐, 올바른 Tool 선택과 업무 성공은 별개다.

#### Chapter 3. Skills로 업무 수행법을 축적합니다

**Skill이 개선하는 두 가지**
- ① 수행 능력 보완 — 불안정하던 작업에 검증된 기법·자원 제공. 예: 근거 대조, 시간순 검증. 확인: *Skill 없이도 같은 품질인가?*
- ② 업무 방식 일관화 — 가능한 행동을 우리 업무의 판단 기준과 순서로 묶음. 예: 정책 판정, 승인 후 티켓 반영. 확인: *실제 업무 절차를 지켰는가?*
- 좋은 Skill은 오래 남는 긴 프롬프트가 아니라 **계속 검증할 수 있는 업무 자산**.

**Progressive disclosure · 필요한 만큼만 읽기**

| 단계 | 내용 | 질문 | 시점 |
|---|---|---|---|
| 1 · Metadata | name + description | 어떤 Skill이 필요한가? | 시작할 때 |
| 2 · Instructions | SKILL.md 본문 | 어떤 절차를 따르는가? | 선택한 뒤 |
| 3 · Resources | 정책 · 스크립트 · 양식 | 지금 어떤 자원이 필요한가? | 단계가 요구할 때 |
- 모든 본문을 처음부터 넣지 않는다. 단, metadata도 컨텍스트 비용이 든다.

**Skill은 절차와 자원의 묶음** — 최소 단위는 `SKILL.md`. 권장 폴더 구성:
```
skills/
  incident-analysis/
    SKILL.md
    references/
      severity-policy.md
    scripts/
      validate_timeline.py
    assets/
      report-template.md
```
| 위치 | 담을 내용 |
|---|---|
| `SKILL.md` | 선택 조건 · 절차 · 분기 · 완료 |
| `references/` | 상세 정책 · 도메인 참고자료 |
| `scripts/` | 계산 · 파싱 · 결정적 검사 |
| `assets/` | 보고서 양식 · 정적 자원 |
- 파일이 있다는 것만으로 활용되지 않는다. SKILL.md에서 **언제 사용할지** 연결해야 한다.

**Description은 선택을 위한 계약** — 무엇을 하는지 + 어떤 요청에서 선택해야 하는지.
- 모호: `Helps with research.` → 어떤 조사? 언제 선택? 결과는?
- 개선 (대상 + 요청 조건 + 결과): "운영 장애·지연 급증·사후 분석 요청에서 관련 근거로 영향과 시간순 경과를 재구성하고, 정책에 따라 심각도와 미확인 원인을 정리한다. 개념 설명이나 신규 정책 작성은 별도 업무다."
- 관련 단어 등장 ≠ 같은 업무. 선택해야 할 때와 아닐 때를 함께 평가.

**SKILL.md · 선택 조건과 수행 조건**

선택 조건 (YAML frontmatter):
```yaml
---
name: incident-analysis
description: >
  Analyze operational incidents using source evidence
  and severity policy. Use for outage reviews and
  postmortem requests.
---
```
수행 조건 (Markdown body):
```markdown
# Procedure
1. Fix the incident window.
2. Retrieve source evidence.
3. Read references/severity-policy.md.
4. Call validate_timeline(events).
5. On failure, recheck the evidence.
6. Separate facts from hypotheses.
7. Submit proposed changes for review.
8. Verify the approved change result.
```
- 절차에는 해야 할 행동뿐 아니라 자료가 없거나 검증 실패 시의 행동도 필요.

**절차는 순서보다 판단의 의존관계** (다이어그램)
- 범위 확정(시간 · 서비스) → 사고 근거 수집(관측 기록) / 적용 정책 확인(시점 · 심각도 기준) → 검증 · 판단(사실/가설 구분) → 보고 / 제안(완료 상태 명시)
- 실제 티켓 변경은 승인·권한 확인 이후
- 독립적인 검색 순서는 달라도 되지만, **정책 없는 심각도 판정**과 **검증 없는 확정**은 안 된다.

**좋은 Skill에는 예외와 종료가 있습니다**

| 관측한 조건 | Skill이 안내할 다음 행동 | 결과에 남길 것 |
|---|---|---|
| 근거가 충분하다 | 사실을 정리하고 인용·검증 | 근거 ID와 확인한 범위 |
| 필수 사실이 빠졌다 | 부족한 항목을 특정해 추가 검색 | 추가 검색의 이유 |
| 자료가 충돌한다 | 시점·권위·적용 범위 비교 | 채택 근거 또는 미해결 충돌 |
| Tool이 실패했다 | 오류 유형에 맞게 복구하거나 중단 | 미완료 작업과 실패 이유 |
| 승인 또는 예산이 부족하다 | 변경하지 않고 부분 답변·보류 | 대기·보류·완료를 구분 |
- 실패를 숨긴 완성 답변보다, 부족한 근거와 다음 확인 사항을 남기는 결과가 낫다.

**자원은 "언제 읽고 실행할지"까지 연결**

| 자원 | 사용할 시점 | Agent가 해야 할 일 |
|---|---|---|
| `references/severity-policy.md` | 심각도 판정 전 | 정책 시점·조건을 읽고 판단에 적용 |
| `validate_timeline` Tool | 시간순 경과 확정 전 | 정리한 events로 호출하고 오류 확인 |
| `scripts/validate_timeline.py` | 스크립트 실행 경로를 선택했을 때 | 준비된 sandbox에서 실제 실행 |
| `assets/report-template.md` | 최종 보고서 작성 시 | 근거·미확인 항목·변경 상태를 채움 |
- `read_file(script)`는 코드 실행이 아니다. 파일 위치와 실행 권한도 별도로 준비.

**Deep Agents에는 Skill의 부모 경로를 줍니다** (조립 발췌 · 파일과 MODEL_ID는 사전 준비)
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

backend = FilesystemBackend(
    root_dir="workspace",
    virtual_mode=True,
)
agent = create_deep_agent(
    model=MODEL_ID,
    backend=backend,
    tools=[validate_timeline],
    skills=["/skills/"],
)
```
- 경로 대응: 물리 root `workspace/` ↔ Agent 경로 `/skills/incident-analysis/SKILL.md`
- 개별 SKILL.md나 단일 Skill 폴더가 아니라 **Skill들을 포함한 source(부모 경로)** 를 지정.
- Skill 발견은 실행보다 먼저 확인.

**여러 Skill은 명확한 인계 기준으로 조합**
- `incident-analysis`: 범위 · 판단 · 보고 (전체 업무 책임)
- `rag-research`: 검색 · 출처 · 충돌 (근거 조사 절차)
- 인계물 **Evidence Pack**: 출처 · 시점 · 사실 / 부족한 근거 → 상위 업무는 반환된 근거로 계속 진행
- Skill은 서로를 자동 호출하는 함수가 아니다. Agent가 읽고 조합한다.

**Skill을 늘리는 것 ≠ 컨텍스트를 늘리는 것**
- Skill 쪽에서 줄일 것: 서로 겹치는 description, 시작부터 주입하는 긴 본문, 매번 필요하지 않은 참고 문서 → 작은 업무 단위 + 필요 시 읽기
- MCP / Tool 쪽에서 줄일 것: 업무에 필요 없는 도구, 중복 기능과 모호한 이름, 다음 판단과 무관한 큰 반환값 → 노출 범위 + 명확한 결과 계약
- Skills의 progressive disclosure가 모든 MCP Tool schema까지 자동으로 줄여 주지는 않는다.

**Skill의 차이는 결과물의 기준에서 드러남** (같은 E01–E03 사용)
- 실패 답변: "배포가 원인이었습니다. Rollback으로 해결했으며 티켓 반영도 완료했습니다." → 원인·변경 완료의 근거 없음
- 기대 결과: "오류 증가 → rollback → 정상화를 E01–E03에서 확인했습니다. 근본 원인과 영향 규모는 미확인입니다. 티켓 반영안은 검토 대기입니다."
- 절차의 목적은 양식 채우기가 아니라 근거와 판단의 경계를 일관되게 지키는 것.

#### Chapter 4. MCP로 실행 능력을 넓힙니다

**MCP는 같은 능력을 여러 Host에 연결**
- Host: Support Agent(사고 대응), Analysis Agent(근거 조사) → MCP Client / Adapter(능력 발견 · 표준 호출, LangChain Tool로 연결) → 문서 검색 서비스(검색 팀 소유), 사고 · 티켓 서비스(운영 팀 소유)
- MCP의 가치는 모델 추론력 상승이 아니라 **외부 능력의 표준 연결과 재사용**.

**MCP는 Tools만 제공하는 규격이 아님**

| 구분 | 주체 | 설명 | 예 |
|---|---|---|---|
| Tools | MODEL-DRIVEN | 행동을 실행하는 함수 | `search_documents(query)`, `get_incident(id)` |
| Resources | APPLICATION-DRIVEN | 맥락으로 사용할 자료, URI로 식별 | 정책 문서 · DB schema |
| Prompts | USER-DRIVEN | 선택해서 쓰는 템플릿, 인자로 메시지 구성 | 사고 검토 질문 템플릿 |
- MCP Prompt와 Agent Skill은 같지 않다(파일 묶음·발견·실행 방식이 다름). Host의 지원 방식도 확인.

**MCP를 고르기 전에 부족한 능력을 적는다**

| 업무에서 부족한 능력 | 제공할 실행 인터페이스 | 결과 계약 |
|---|---|---|
| 사고와 근거를 식별 | `get_incident(incident_id)` | 근거 ID · 사건 범위 |
| 정책과 관련 자료를 찾음 | `search_documents(query)` | 출처 · 버전 · 발췌문 |
| 시간순 경과를 검사 | `validate_timeline(events)` | 검사 결과 · 오류 위치 |
| 검토할 변경안을 만듦 | `propose_case_note(case_id, note)` | 고정된 change_id · 검토 상태 |
| 승인된 변경을 반영 | `append_case_note(case_id, change_id)` | 반영 상태 · 중복 여부 |
- Tool을 연결한 뒤에도 사용 순서는 Skill에 남는다.

**언제 MCP를 쓰고, 언제 쓰지 않을까**
- MCP 유리: 제공 팀과 사용 팀이 다름 / 여러 Host가 같은 능력 사용 / 독립 배포·권한·감사 필요 → 서비스 계약을 표준으로 공유
- 다른 층이 더 직접적: 프로세스 안 계산 → Local Tool, 반복되는 업무 순서 → Skill, 결정적 업무 규칙 → 서버 코드 → 불필요한 연결·운영 복잡성 축소

**최신 MCP는 protocol core가 무상태** (기준: 2026-07-28)
- 이전 규격(≤ 2025-11-25): `initialize` 기반 협상, protocol session을 고려하는 연결, legacy 호환성은 별도 테스트
- 현재(2026-07-28): 요청별 버전·capability metadata, protocol session 제거, `server/discover`로 능력 발견
- 무상태 protocol ≠ 업무 상태 없음 ≠ 스트리밍 연결 없음. 업무 상태는 명시적 ID와 저장소로 관리, 실제 Client 호환성은 따로 확인.

**업무 상태는 일반 인자로 명시**
- `create_case`(업무 생성 → `case_id`) → `propose_case_note`(검토할 내용 고정 → `change_id`) → `append_case_note`(승인된 변경안 반영 → 반영 상태)
- 외부 저장소: 업무 · 소유자 · 만료 · 변경안 · 승인 · 요청 키 · 반영 결과
- Handle 보유는 권한이 아니다. 인증된 사용자·만료·승인 상태를 서버가 확인.

**MCP 서버는 검증한 기능을 노출** (Python SDK v2 · 합성 사고 조회 예제)
```python
from mcp.server import MCPServer

server = MCPServer("incident-evidence")
records = {"INC-017": ["E01", "E02", "E03"]}

@server.tool()
def get_incident(incident_id: str) -> dict:
    """Read evidence IDs for a training incident."""
    if incident_id not in records:
        raise ValueError("unknown incident_id")
    return {"evidence_ids": records[incident_id]}
```
- 책임 분리: Tool = 작은 조회 동작 / Skill = 조회 후 분석 절차 / 서버 = 입력·권한·실제 상태
- 작게 시작: LLM 없이도 입력과 결과를 확인할 수 있는 Tool부터.

**연결 성공과 업무 계약 성공을 나눈다** (함수 → MCP Client → HTTP → Adapter → Agent 순으로 실패 범위 축소)

| 확인 단계 | 확인할 내용 | 여기서 아직 모르는 것 |
|---|---|---|
| Python 함수 | 정상·잘못된 입력과 결과 | MCP schema / transport 동작 |
| MCP Client · LLM 없이 | 발견·직렬화·Tool 호출·오류 | 실제 네트워크와 인증 환경 |
| HTTP / stdio | 연결·요청·인증·timeout | Agent의 Tool 선택 능력 |
| MCPAdapter | 이름·인자·내용·오류 변환 | Skill 선택과 절차 준수 |
| Agent E2E | 요청 → 호출 → 근거 → 완료 | 다른 요청에서의 일반화 |
- `tools/list` 성공은 시작일 뿐. 실제 호출·오류·거부 경로까지 확인.

**MCP Tools와 Skills를 같은 Agent에** (LangChain native MCP · 조립 발췌)
```python
from langchain.mcp import MCPAdapter

async with MCPAdapter(MCP_URL) as adapter:
    discovered = await adapter.list_tools()
    approved = select_approved_tools(discovered)
    agent = create_deep_agent(
        model=MODEL_ID,
        backend=backend,
        tools=[validate_timeline, *approved],
        skills=["/skills/"],
    )
    result = await agent.ainvoke({"messages": messages})
```
- `tools=` Local 함수 + MCP 도구(실행 능력) / `skills=` Skill source 부모 경로(읽을 절차). 둘을 연결하는 최종 판단은 Agent.

**발견한 모든 Tool을 그대로 넣지 않는다** (검토된 이름만 허용하는 교육용 필터)
```python
def select_approved_tools(discovered):
    names = {"get_incident", "search_documents"}
    by_name = {tool.name: tool for tool in discovered}
    missing = names - by_name.keys()
    if missing:
        raise RuntimeError(f"Missing tools: {missing}")
    return [by_name[name] for name in sorted(names)]
```
- 확인할 것: 실제 발견 이름, 필수 Tool 존재, 입력 schema, 읽기/쓰기 범위, 사용자별 서버 권한
- 목록 필터는 노출 범위를 줄이는 장치일 뿐, 서버의 사용자별 권한 검사를 대신하지 않는다.

**오류를 구분해야 복구 능력이 생긴다**

| 상황 | 호출자 / Agent가 받는 정보 | 다음 행동 |
|---|---|---|
| 정상 검색 · 0건 | 성공 결과 + 빈 자료 | 범위 재검토 · 근거 부족 처리 |
| 서버가 보고한 Tool 오류 | `ToolMessage(status="error")` | 인자·업무 조건 확인 |
| 연결·전송 실패 | 호스트에 예외 전달 | 연결 복구 · 제한된 재시도 |
| 변경 요청의 timeout | 반영 여부가 아직 불확실 | 상태 조회 · 중복 방지 확인 |
- 실패를 `[]`로 숨기거나 같은 변경 요청을 무조건 재시도하지 않는다.

**능력을 넓힐수록 실행 경계도 명확해야**
- Agent 제안(대상 + 변경 내용) → 승인 Gate(승인 / 수정 / 거절) → 서버 검증(권한 · 내용 · 멱등성) → 실제 변경(반영 결과 + 감사)
- Skill은 "승인 후 반영"을 *안내*, Host·서버는 승인 전 실행을 *실제로 차단*.
- "승인받았다"는 모델의 문장이 아니라 신뢰된 승인 이벤트와 실제 인자를 확인. 승인·권한·중복 방지·감사는 서로를 대신하지 않는다.

#### Chapter 5. 실패를 고치고 개선을 증명합니다

**Skill Eval 없이는 개선을 판단할 수 없다** — 생애주기: 작성 → Eval → 개선 → 배포 → 재평가
- 01 ADD — 추가할 가치가 있는가? Skill 없이도 성공하는가? 같은 도구로 품질·비용 비교. 파일 추가 자체는 개선이 아님
- 02 CHANGE — 수정이 회귀를 만들었나? 정상 요청 + 인접 요청 재실행, 선택·수행·결과 분리, 한 사례 성공으로 끝내지 않음
- 03 KEEP / RETIRE — 계속 유지해야 하는가? 모델·정책·Tool 변경 후 재평가, 불필요한 기법은 축소 검토, 조직 필수 정책은 별도 유지

**MCP와 Skill의 효과를 분리해 비교** (같은 모델·요청·예산 유지, 2×2)

| | 외부 Tool 없음 | 외부 Tool 있음 · MCP 제공 |
|---|---|---|
| Skill 없음 | A · 기본 Agent (제공된 정보로 판단) | B · 실행 능력 추가 (같은 Tool로 업무 시도) |
| Skill 있음 | C · 절차만 추가 (정보 접근은 여전히 제한) | D · 능력 + 절차 (같은 Tool을 업무 기준으로 조합) |
- 이 비교는 *추가된 능력*의 효과. MCP 자체의 우월성을 보려면 동일 Local Tool 대조군 필요.

**LangChain · Skill 파일이 아니라 Agent를 평가**
- 동일 업무 · 동일 초기 파일 · 동일 도구 · 새 실행 환경에서 A(Skill 없음) vs B(Skill 있음)
- 비교 지표: 완료 단계 · 호출 수 · 시간 · Trace의 실패 원인. 분할 / 통합 / 내용 제거도 비교 실험으로 결정
- 자체 실험: **9% → 82%** (Skill 없음 → 있음), Claude Code를 통한 LangChain / LangSmith 실험

**선택 · 수행 · 결과를 각각 평가**
- ACTIVATION — 맞게 선택했는가? 필요한 Skill을 놓쳤는가/불필요한 Skill을 켰는가? → Precision / Recall
- EXECUTION — 올바르게 수행했는가? 정책·자원을 읽었는가, Tool 인자와 순서가 맞는가? → 필수 행동 / 유효 인자
- OUTCOME — 업무를 해결했는가? 근거가 주장을 지지하는가, 실제 변경 결과가 맞는가? → Task success / 근거 품질
- 정답 문장이 우연히 맞아도 잘못된 도구 선택·무단 변경이 있으면 좋은 수행이 아니다.

**OpenAI · 성공 기준부터 쓰고 실행을 채점**
- 흐름: Prompt(평가 요청) → Run(Trace + 산출물) → Checks(규칙 + Rubric) → Score(버전 간 비교)
- Outcome: 영향·경과·미확인 원인을 구분하고 실제 티켓 상태를 확인
- Process: Skill·정책 읽기, 검증 성공, 승인된 변경이라는 필수 조건 확인
- Style: 조직 보고서의 구획과 용어를 따르되 형식과 사실성을 혼동하지 않음
- Efficiency: 호출·토큰·전체 시간 기록, 불필요한 재시도와 예산 초과 탐지
- INC-017 적용: 명령 호출 흔적만이 아니라 반환값·산출물·외부 상태까지 확인

**Trace에서는 확인 가능한 행동을 본다** (보이지 않는 추론을 추측하지 않음)

| 관찰할 이벤트 | 필수 확인 내용 |
|---|---|
| `read_file` · SKILL.md | 해당 업무의 Skill을 선택했는가? |
| 정책 / 근거 읽기 | 적용 시점과 필요한 자료를 확인했는가? |
| Tool 호출 · 인자 · 결과 | 실제 검색 근거로 인자를 만들고 반환값을 사용했는가? |
| 검증 결과 → 보고서 | 검증 실패를 무시하지 않았는가? |
| 승인 이벤트 → 실제 변경 | 승인된 대상·내용만 한 번 반영했는가? |
- 전체 호출 순서의 완전 일치보다 필요한 행동과 선행 조건을 검증.

**평가셋에는 경계와 실패 사례가 필요**

| 종류 | 요청 / 상황 | 기대 행동 |
|---|---|---|
| Implicit | 어제 장애의 경과를 정리해. | 사고 Skill · 근거·정책·검증 |
| Explicit | incident-analysis로 경과를 정리해. | 지정한 Skill의 수행을 확인 |
| Negative | latency 뜻 / 새 정책 작성 요청 | 사고 Skill 오활성화 금지 |
| No evidence | 근거 없어도 원인을 확정해. | 확정하지 않고 부족한 근거 표시 |
| Unauthorized | 권한 없는 티켓을 바꿔. | 변경 금지 · 올바른 권한 경로 |
| Tool failure | 검색 서버가 응답하지 않는다. | 오류 구분 · 제한된 복구 / 보류 |
- 입력마다 정답 Skill뿐 아니라 **필수 행동 · 금지 행동 · 허용되는 완료 상태**를 기록.

**증상에 맞는 계층만 수정**

| 증상 | 우선 볼 곳 | 최소 수정 |
|---|---|---|
| Skill이 발견되지 않는다 | source · 경로 · frontmatter | 로딩과 파일 배치 수정 |
| 다른 Skill을 고르거나 놓친다 | description · trigger · overlap | 선택 조건과 범위 조정 |
| 정책·검증 단계를 생략한다 | SKILL.md · 자원 경로 | 필수 행동·실패 분기 명시 |
| 호출은 맞는데 계산이 틀린다 | Tool / script 구현 | 코드 수정 + 단위 테스트 |
| 여러 업무에서 공통 규칙 위반 | middleware · 서버 · sandbox | 실행 경계의 강제 정책 수정 |
- 발견 → 선택 → 수행 → 코드 → 공통 정책 순으로 실패 위치를 좁힌다. 한 Skill 문제를 전체 시스템 프롬프트로 덮지 않는다.

**수정 예시 · 넓은 설명을 좁은 조건으로**
- 실패: latency 개념 질문에도 사고 분석 Skill 선택
- 수정 전: "API·latency·정책과 관련된 모든 질문을 조사하고 분석한다." → 개념 설명과 사고 분석이 겹침
- 수정 후: "실제 운영 장애의 영향·경과를 근거와 정책으로 분석할 때 사용한다." → 개념 설명·신규 정책 작성 제외
- 재확인 요청: "장애 경과 분석" / "latency 뜻" / "새 정책 작성". 성공 판단은 문구 인상이 아니라 같은 긍정·경계·혼동 요청의 결과.

**규칙 검사와 의미 평가를 함께**
- DETERMINISTIC(빠른 규칙 검사): 필수 파일·Tool 호출, 유효한 ID·인자·순서, 무단·중복 변경 여부 → 코드로 재현 가능하게
- SEMANTIC(의미와 업무 결과): 근거가 주장을 지지하는가? 질문을 해결했는가? 보류 이유가 타당한가? → Rubric + 사람 / Judge
- DO NOT CONFUSE: ID 존재 ≠ 주장 지지 / 파일 읽기 ≠ script 실행 / API 성공 ≠ 업무 완료 → 각 검사가 증명한 것만 보고

**개선 비교는 같은 조건에서 반복**
- 조건 고정(모델 · 도구 · 데이터) → 변수 하나 수정(description / 절차 / 코드) → 함께 비교(품질 · 비용 · 지연) → 분리해서 반복(새 Context · 검증 요청)
- 결과표 포함 항목: 실행 건수, 실패 종류, 수정한 버전, 성공·실패 요청의 시간과 호출 수
- 정답률만 높이고 비용·지연·오활성화를 악화시킨 변경도 드러나야 한다.

**Anthropic · skill-creator로 비교 실험 반복**
- BENCHMARK: 통과율 · 시간 · 토큰 (품질과 수행 비용 함께 기록)
- INDEPENDENT RUNS: 깨끗한 Context로 병렬 실행 (평가 사례 간 맥락 오염 감소)
- BLIND COMPARISON: 버전 A/B · Skill 유무 비교를 어느 쪽인지 모르는 비교자가 판정
- TRIGGER TUNING: description의 오탐·누락 개선 (출력 평가와 활성화 평가 구분)
- Capability uplift는 추가 효과를, Encoded preference는 실제 업무 절차의 충실도를 확인.

**잘 만든 Skill도 변경·회귀 관리 필요**
- 초안(목표 · 선택 · 절차) → 검증(구조 · 실행 · 결과) → 비교(Skill 유무 / 버전) → 배포(검토 · 고정 버전) → 회귀(변경 후 재평가)
- 변경 트리거: 업무 정책 변경 / MCP Tool 계약 변경 / 모델 변경 / 실제 실패 Trace
- 승인된 원본과 결과를 함께 배포. Marketplace 등록은 품질 승인이 아니다.

**실행 중 검증 vs Skill Eval**
- RUNTIME · VERIFICATION: 이번 작업이 기준을 만족하는가? 보고서 작성 → 검사 → 실패 수정 (예: timeline의 시각·ID 정합성). 종료 조건과 재시도 예산을 Skill에 연결
- OFFLINE · SKILL EVAL: 이 버전이 반복해서 도움이 되는가? 평가 요청 묶음 → 독립 실행 → 비교 (예: Skill 없음 / v1 / v2의 실패 분포). 평가 코드·정답·승인 권한은 별도 관리
- 자기 검증을 통과한 결과도 외부 평가셋에서 다시 평가, 게시 승인은 그 다음.

#### Chapter 6. RAG를 업무 Skill로 조합합니다

**검색 구현은 Tool, 검색 정책은 Skill**
- Tool / MCP(검색 능력): 문서·인덱스 접근, 질의 실행·결과 반환, ACL·버전 조건 실제 적용 → `source_id` · 본문 · 적용 버전
- Skill(근거 사용 절차): 언제 무엇을 검색? 어떤 자료가 권위 있는가? 충돌·부족·종료 처리 → 질문 조건 · 판단 · 보고 기준
- Skill은 Retriever를 대체하지 않는다.

**추가 검색은 "빠진 사실"을 채우기 위해**

| 단계 | 찾으려는 사실 | 실행 / 판단 |
|---|---|---|
| 1차 검색 | INC-017의 시간순 사건 | INC-017 → E01 · E02 · E03 |
| 충분성 확인 | 심각도·영향도 판단 근거가 있는가? | 경과는 있음 / 정책·영향 근거는 부족 |
| 추가 검색 | 사고 시점에 유효한 정책과 영향 기록 | 질문 목적을 나눠 검색 |
| 결과 처리 | 필수 사실이 실제로 채워졌는가? | 채워진 내용만 확정 · 나머지는 보류 |
- `top_k`만 늘리지 않는다. 무엇이 부족한지 먼저 특정하고 검색 목적을 바꾼다.

**근거 ID가 있다고 주장이 맞는 것은 아님**

| 보고서의 주장 | 출처 | 원문 대조 판정 |
|---|---|---|
| 00:01 UTC에 오류 증가가 관측됐다. | E01 | 지지됨 |
| 00:07 UTC에 rollback을 수행했다. | E02 | 지지됨 |
| 00:12 UTC에 정상화가 관측됐다. | E03 | 지지됨 |
| 배포가 장애의 원인으로 확정됐다. | 제공된 근거 없음 | 확정 불가 |
- 관측된 순서만으로 원인을 확정하지 않는다.

**종료 규칙이 있어야 업무가 끝난다** (다이어그램)
- 질문 조건(필요한 사실) → 검색 Tool → 근거 반환 → 충분성 확인(근거 · 예산)
  - 충분한 근거 → 답변 · 검증
  - 부족 + 예산 남음 → 부족한 사실을 겨냥해 질의 변경
  - 예산 종료 · 새 근거 없음 → 부분 답변 / 보류
- 더 찾는 것만이 능력이 아니다. 충분하면 멈추고 부족한 것은 명확히 남긴다.

**최종 보고서에는 완료 상태까지** (E01–E03만 주어진 상황의 기대 산출물)
```
INC-017 · 사고 분석 요약
확인된 경과  00:01 오류 증가 [E01] → 00:07 rollback [E02] → 00:12 정상화 관측 [E03]
미확인 항목  사용자 영향 규모 · 적용 정책에 따른 심각도 · 근본 원인
변경 상태    티켓 반영안 준비 / 검토 대기 / 아직 실제 변경하지 않음
```
- 분석 완료와 티켓 반영 완료는 다르다. 실제 확인한 상태만 보고.

#### Chapter 7. 검증된 Skill을 배포하고 통합합니다

**최종 아키텍처** (다이어그램)
- INC-017 요청(영향 · 경과 · 변경) → Deep Agent(모델 + Harness) → 보고 / 변경 상태(근거 · 미확인 · 완료)
- Deep Agent가 사용: Skills(`incident-analysis` / `rag-research`), Local Tools(시간순 검증 · 근거 ID 검사), MCP Services(문서 검색 · 사고 · 티켓)
- 런타임: MCP + Skills + Tool | 배포: 원본 고정 + Eval + 검토 + Marketplace

**Skills Marketplace는 조직의 공유 창구**
- REGISTRY — 무엇을 등록했는가? 이름·설명·분류, 버전·원본 위치 (중앙 관리)
- MARKETPLACE — 누가 찾아 사용할까? 업무에 맞는 Skill 탐색, 설치할 배포 항목 선택 (조직 재사용 접점)
- AGENT RUNTIME — 실제로 무엇을 할까? Skill 선택과 자원 읽기, Tool·MCP·Script 사용 (권한과 결과는 실행에서 검증)
- **등록 ≠ 품질 승인 · 설치 ≠ 활성화 · 활성화 ≠ 업무 성공**

**LiteLLM · 중앙 Registry에서 Claude Code로 배포**
- 흐름: 원본 Skill(Git 저장소 / 하위 폴더) → 등록(Skills UI 또는 API) → 게시(선택 항목 enable) → 탐색·설치(Hub / Claude Code)
- 문서에 명시된 등록 정보: `name` · `source` · `description` · `version` · `domain` · `namespace` · `keywords`
- 문서가 제공하는 범위는 등록·게시·탐색·Marketplace 연결. Eval 자동 통과, 보안 심사, 배포 승인까지 기본 제공된다고 가정하지 않는다.
- 조직이 연결할 품질 절차: 평가 보고서 · 승인자 · 승인된 원본 · 호환성 검사 · 철회 / 롤백

**사내 Gateway라도 공개 조회 API를 확인** (LiteLLM 문서의 인증 표)

| 경로 | 역할 | 문서의 Auth |
|---|---|---|
| `POST /claude-code/plugins` | 등록 | Required |
| `POST /claude-code/plugins/{name}/enable` | 게시 | Required |
| `GET /public/skill_hub` | 공개 목록 | None |
| `GET /claude-code/marketplace.json` | 설치용 목록 | None |
- 공개 UI도 로그인 불필요. 사내 전용 배포는 네트워크/접근 제어와 실제 Client 호환성 확인 필요.
- Self-hosting만으로 비공개가 되지 않는다. 노출 경계와 원본 저장소 접근을 함께 검사.

**Eval 결과를 게시 승인 조건으로 연결** (조직 운영 설계안 — LiteLLM 기본 기능 아님)
- 원본 고정(commit / digest) → 격리 Eval(비교 + 회귀) → 사람 검토(품질 + 권한) → 게시(enable) → 운영(재평가 / 철회)
- `not_run`·기준 미달은 게시 승인 보류
- 게시 전 Eval 카드 (INC-017 · v2 후보, 측정값: 미기입)
  - 재현 조건: 모델 · Harness · MCP/Tool 계약 · 데이터셋 · Grader
  - 관측 결과: 실행 수 · 선택/수행/결과 · 비용/지연 · 실패 Trace
  - 배포 근거: 승인자 · 승인된 원본 · 호환 범위 · 철회/롤백 대상

**같은 Skill도 실행 환경별 연결은 따로 확인**
- DOCUMENTED · CLAUDE CODE: Marketplace를 연결해 설치 — manifest를 읽고 배포 항목 선택 → plugin 설치 → Skill 사용. 확인: 실제 이름 · 파일 구조 · 원본 접근
- INTEGRATION DESIGN · DEEP AGENTS: 승인된 파일을 Backend에 공급 — 원본 검증 → Skill 디렉터리 구성 → `skills=["/skills/"]`로 source 지정. 별도 구현: 배포 동기화 · 경로 · 권한
- Marketplace가 MCP 연결·권한·Script 실행 환경을 대신하지 않는다. 소비 환경별로 다시 평가.

#### 마무리

**같은 구조를 다른 업무에도 적용**

| 반복 업무 | 연결할 실행 능력 | Skill에 축적할 수행법 |
|---|---|---|
| 사고 대응 | 문서·사고·티켓 조회와 반영 | 범위 → 근거 → 정책 → 검증 → 승인 |
| 주간 운영 보고 | 지표·변경 기록·티켓 조회 | 대상 기간 → 누락 확인 → 비교 → 보고 |
| 내부 문서 질의 | 권한 있는 문서 검색 | 출처 우선순위 → 충돌 처리 → 근거 답변 |
| 업무 변경 검토 | 변경안·정책·검증 결과 조회 | 기준 확인 → 위험 검토 → 승인 요청 |
- 처음부터 모든 업무를 포괄하지 말고 한 가지 반복 업무에서 개선 효과를 확인.

**연결하고, 평가하고, 검증된 능력을 공유합니다**
- MCP(능력 연결): 어떤 외부 기능이 부족한가? → 실행 범위 정의
- SKILLS(수행법 축적): 언제 어떤 순서와 기준으로 사용할까? → 업무 절차 재사용
- EVALUATION(개선 검증): 같은 요청을 더 잘 수행하게 되었는가? → 품질·비용·회귀 확인
- MARKETPLACE(검증된 자산 공유): 무엇을 누구에게 배포해도 되는가? → 원본·승인·철회 관리
- Agent 능력 개선은 기능 추가 한 번이 아니라 업무와 평가를 연결하는 반복 과정.

---

### 실습 과제 / 실습 단계

덱에 명시적인 "Lab" 슬라이드는 없고, 아래가 실습·평가에 해당하는 내용이다.

**Capstone (25분 평가)**
- 최종 업무 요청: "INC-017의 영향·경과·미확인 원인을 구분하고, 승인된 내용만 티켓에 반영해 주세요."
- 추가 설명 질문: 이 Skill을 게시해도 되는 근거는? → Eval 결과 · 승인된 원본 · 접근·철회 경계
- 설명할 것: 최종 답변 + 실행 통제 + Eval 증거 + Marketplace 게시 조건
- 시간 배분: **10분 설계 정리 → 10분 테스트·증거 확인 → 5분 설계 근거 설명**

**덱의 예제를 따라가는 구현 단계 (본문 코드·구성 기반)**
1. Local Tool `validate_timeline(events)` 구현 및 모델 없이 단위 테스트(정상·경계·실패 입력)
2. `skills/incident-analysis/` 폴더 구성: `SKILL.md`(frontmatter + `# Procedure` 8단계), `references/severity-policy.md`, `scripts/validate_timeline.py`, `assets/report-template.md`
3. MCP 서버 `incident-evidence` 작성 (`get_incident` Tool, Python SDK v2 `MCPServer`)
4. 연결 단계별 검증: Python 함수 → MCP Client(LLM 없이) → HTTP/stdio → MCPAdapter → Agent E2E
5. `MCPAdapter(MCP_URL)`로 `list_tools()` → `select_approved_tools()`로 `get_incident`, `search_documents`만 허용
6. `create_deep_agent(model=MODEL_ID, backend=FilesystemBackend(root_dir="workspace", virtual_mode=True), tools=[validate_timeline, *approved], skills=["/skills/"])` 조립 후 `ainvoke`
7. 평가셋(Implicit / Explicit / Negative / No evidence / Unauthorized / Tool failure) 작성, 각 입력의 필수·금지 행동과 허용 완료 상태 기록
8. A/B/C/D(Skill·외부 Tool 유무) 교차 비교, Trace 기반 Activation/Execution/Outcome 채점
9. 실패 증상에 맞는 계층만 최소 수정(예: description을 좁은 조건으로) 후 같은 조건으로 재평가
10. 기대 산출물: INC-017 사고 분석 요약(확인된 경과 / 미확인 항목 / 변경 상태)

---

### 실제 프로젝트 적용 체크리스트

**능력 진단**
- [ ] 부족한 것이 접근(MCP) / 절차(Skill) / 정확한 실행(Tool·Script) / 반복 품질(Eval) 중 무엇인지 구분했다
- [ ] 서비스 이름보다 먼저 업무 단계별 "부족한 능력 → 실행 인터페이스 → 결과 계약" 표를 작성했다
- [ ] MCP가 필요한지 판단했다(제공·사용 팀 분리, 여러 Host, 독립 배포·권한·감사). 아니면 Local Tool / Skill / 서버 코드로 처리

**Tool 설계**
- [ ] Tool 이름·설명·인자만으로 언제 호출할지 알 수 있다 (`search_policy` 예시처럼 docstring에 "Use when…")
- [ ] 반환값에 status, 출처(source_id), 시점/버전(index_version, observed_at), 요약이 있고 원문 덤프가 없다
- [ ] 빈 결과 / Tool 오류(`ToolMessage(status="error")`) / 연결 실패 / 변경 timeout을 구분한다
- [ ] 실패를 `[]`로 숨기지 않고, 변경 요청을 무조건 재시도하지 않는다 (멱등성·중복 방지)
- [ ] 모델 없이 단위 테스트 → 모델 포함 선택·인자 평가 → E2E 업무 완료 평가를 분리했다

**Skill 설계**
- [ ] `SKILL.md` frontmatter description에 대상 + 요청 조건 + 결과, 그리고 "아닌 경우"를 적었다
- [ ] 본문에 필수 행동, 실패 분기, 종료 조건, 승인 후 반영 단계가 있다
- [ ] references / scripts / assets 각 자원을 "언제 읽고 실행할지" 단계에 연결했다
- [ ] 스크립트 실행 경로(sandbox, 권한)를 별도로 준비했다 (`read_file` ≠ 실행)
- [ ] 정책 없는 판정·검증 없는 확정을 금지하는 의존관계를 명시했다
- [ ] 여러 Skill은 인계물(예: Evidence Pack)로 책임을 나눴고, description 중복이 없다
- [ ] Deep Agents에는 Skill 부모 경로(`skills=["/skills/"]`)를 주고 물리 경로와 Agent 경로 대응을 확인했다

**MCP 연결·통제**
- [ ] 대상 MCP 규격 버전(≤2025-11-25 vs 2026-07-28 무상태 core, `server/discover`)과 Client 호환성을 확인했다
- [ ] 업무 상태는 `case_id` / `change_id` 같은 명시적 인자와 외부 저장소로 관리한다
- [ ] 발견된 Tool 중 승인된 이름만 노출하고, 필수 Tool 누락 시 실패시킨다
- [ ] 목록 필터와 별개로 서버가 사용자별 권한·만료·승인 상태를 검사한다
- [ ] 승인 Gate는 Host·서버에서 실제로 차단되며, 신뢰된 승인 이벤트와 실제 인자를 확인한다 (감사 로그 포함)
- [ ] `tools/list` 성공 이후 실제 호출·오류·거부 경로까지 테스트했다

**Eval**
- [ ] Skill 유무 × 외부 Tool 유무 교차 비교를 같은 모델·요청·예산으로 수행했다
- [ ] 평가셋에 Implicit / Explicit / Negative / No evidence / Unauthorized / Tool failure 사례가 있다
- [ ] Activation(Precision/Recall), Execution(필수 행동/유효 인자), Outcome(Task success/근거 품질)을 분리 채점한다
- [ ] 결정적 규칙 검사(코드)와 의미 평가(Rubric + 사람/Judge)를 함께 쓰고, 각 검사가 증명한 것만 보고한다
- [ ] 조건 고정 + 변수 하나 수정 + 품질·비용·지연 동시 비교, 결과표에 실행 건수·실패 종류·버전·시간·호출 수 기록
- [ ] 증상에 맞는 계층만 수정한다 (발견 → 선택 → 수행 → 코드 → 공통 정책)
- [ ] 모델·정책·MCP Tool 계약 변경, 실제 실패 Trace 발생 시 회귀 재평가한다
- [ ] Runtime 자기 검증과 Offline Skill Eval을 분리하고, 평가 코드·정답·승인 권한을 별도 관리한다

**출력 품질**
- [ ] 주장별로 근거 원문이 실제로 지지하는지 확인한다 (ID 존재 ≠ 주장 지지)
- [ ] 최종 보고서에 확인된 사실 / 미확인 항목 / 변경 상태(준비·검토 대기·완료)를 구분해 남긴다
- [ ] 추가 검색은 `top_k` 증가가 아니라 빠진 사실을 특정해 수행하고, 예산 종료 시 부분 답변/보류한다

**배포·통합**
- [ ] 원본을 commit / digest로 고정하고 Eval 카드(재현 조건·관측 결과·배포 근거)를 함께 릴리스한다
- [ ] `not_run`·기준 미달 Skill은 게시하지 않는다 (등록 ≠ 품질 승인)
- [ ] LiteLLM 등 Gateway의 공개 조회 경로(`GET /public/skill_hub`, `GET /claude-code/marketplace.json`) 노출 범위를 점검했다
- [ ] 소비 환경별(Claude Code plugin 설치 vs Deep Agents Backend 공급) 연결·권한·경로를 따로 검증했다
- [ ] 철회 / 롤백 대상과 승인자를 정해 두었다
- [ ] 한 가지 반복 업무부터 시작해 개선 효과를 확인한 뒤 확장한다
