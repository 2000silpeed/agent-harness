# 메모리와 자기개선: 기록 형식, 정책, 채택 절차

> S3(저장소·쓰기 정책·보호)과 S6(조회·주입·개선 루프)에서 같이 본다. 채우는 산출물은 `design/03-context.md`와 `design/06-improve.md`, 실행 절차는 `self-improve-loop` 스킬이다.
> "(제안값)"은 출처가 없는 기본값이다. 평가셋 크기와 흔들림 폭을 재고 팀이 정한다. "(확인 필요)"는 원문을 직접 대조하지 못한 내용이다. 이벤트·필드·파일 이름은 예시이고 S2의 기록 형식에 맞춘다.

## 1. 최소 버전

마감이 있는 작은 프로젝트는 아래만 만든다. 인수 기준 3-1~3-4는 이것으로 보일 수 있다(10절).

| 구분 | 최소 버전 | 나중에 더할 것 |
|---|---|---|
| 저장 | 규칙 파일 1개 + 경험 기록 파일 1개(한 줄에 한 건). 작업 종료·실패 때 코드가 기록 단계를 실행한다 | 만료 자동화, 카운터로 정리, 중복 합치기 |
| 저장 전 검사 | 필수 필드, 길이 상한, 시크릿 패턴 | 평가 정답 흔적 검사, 근거 대조 자동화 |
| 조회 | 범위 필터 + 키워드, 3건(제안값), 메시지로 주입, 주입한 ID를 계획과 기록에 남긴다 | 실패 직후 재조회, 임베딩 |
| 개선 | 손잡이 1개, 후보 1개, 사례 분할 없이 반복 실행, 사람 승인, 커밋 1개, 되돌리기 1회 실행 | 읽기용·판정용 분할, 후보 여러 개, 사후 확인 기간 |
| 차단 | 규칙 파일 직접 편집 차단, 개선안의 변경 경로 허용 목록, 평가 하네스 해시 확인 | 형식 검사 확대(외우기, 기준을 낮추는 문구) |

줄이면 안 되는 것: 채택 기준을 결과 보기 전에 고정하기, 개선안이 채점기·테스트·권한을 못 건드리게 코드로 막기, 효과를 새 세션에서 재기.

## 2. 메모리 층

| 층 | 담는 것 | 누가 쓰나 | 언제 읽히나 | 누가 고치나 | 상한 |
|---|---|---|---|---|---|
| 규칙 | 항상 지킬 것 (명령, 금지, 팀 관례) | 사람, 또는 채택된 개선안 | 세션 시작 때 전부 | 사람 승인을 거친 변경만. 에이전트에게는 읽기 전용 | 짧게 (제안값: 200줄 이하) |
| 경험 | 과거 작업의 실패·해결·교훈. 한 건에 교훈 하나 | 에이전트 (작업 종료·실패 때, 후보 상태로) | 요청과 맞는 것만 찾아서 몇 건 | 추가·카운터·폐기 표시만. 내용을 고칠 때는 새 항목으로 | 건수, 항목 길이, 한 번에 주입하는 양 |
| 절차 | 반복 작업의 순서 | 사람 (스킬로 둔다. S4) | 필요할 때 | 규칙과 같다 | 스킬 작성 기준 |

- 한 파일에 섞지 않는다. 층마다 읽히는 방식과 고칠 권한이 다르다.
- 규칙도 경험도 모델에게는 "맥락"이지 강제가 아니다. 반드시 지켜져야 하면 S5의 훅·권한으로 옮긴다.
- 같은 실수가 다시 나오면 더 강한 층으로 옮긴다: 경험 → 규칙 → 스킬 → 훅·권한 → 테스트·CI. 옮기면 아래 층의 항목은 폐기 표시한다(두 곳에 있으면 충돌한다).

## 3. 경험 기록 형식 (1건)

```json
{
  "id": "exp-0007", "kind": "experience", "status": "candidate",
  "scope": {"repo": "billing-api", "paths": ["src/invoice/**"], "task_type": "bugfix"},
  "trigger": "pytest에서 'Decimal is not JSON serializable'가 나올 때, 또는 src/invoice의 직렬화 코드를 고칠 때",
  "lesson": "금액 필드는 to_json_safe()를 거쳐 직렬화한다. json.dumps에 default=str을 넣지 않는다(반올림 규칙이 깨진다).",
  "outcome": "failure_fixed",
  "evidence": {"run_id": "req-2026-11-08-0412", "event_ids": ["ev-118", "ev-131"], "commit": "9f2c1ab",
               "citations": [{"path": "src/invoice/serialize.py", "lines": "40-58"}]},
  "source": {"origin": "agent", "trust": "unverified", "derived_from_external_input": false},
  "created_at": "2026-11-08T04:31:00Z", "last_verified_at": null, "expires_at": "2027-02-06T00:00:00Z",
  "counters": {"retrieved": 0, "cited_in_plan": 0, "helpful": 0, "harmful": 0},
  "supersedes": null, "harness_version": "r3"
}
```

| 필드 | 값과 쓰임 |
|---|---|
| `kind` | `rule` / `experience` / `procedure`(스킬을 가리킨다). 읽히는 방식과 수정 권한이 여기서 갈린다 |
| `status` | `candidate`(에이전트가 방금 씀) → `active`(근거가 확인돼 쓰였거나 사람이 승인) → `deprecated`. 지우지 않고 상태를 바꾼다 |
| `scope` | 조회의 1차 필터. 저장소·경로·작업 종류가 다르면 꺼내지 않는다 |
| `trigger` | 조회 키. 오류 문자열, 파일 경로, 명령처럼 그대로 일치시킬 수 있는 표현을 넣는다 |
| `lesson` | 행동 문장. 무엇을 하고 무엇을 하지 않는지 쓴다. "조심한다"는 쓰지 않는다 |
| `evidence` | 근거 위치(실행 ID, 이벤트, 커밋, 파일·줄). 꺼내 쓸 때 대조한다. 근거가 없으면 `active`가 될 수 없다 |
| `source.trust` | `verified`(사람 승인 또는 개선 라운드 통과) / `unverified`(에이전트 자동 기록) / `untrusted`(외부 입력에서 나옴. 주입하지 않는다) |
| `expires_at` | 만료일 (제안값: 90일). 근거가 확인돼 쓰이면 연장한다 |
| `counters` | 조회·계획 인용·도움·해로움 횟수. 정리와 승격의 근거 |
| `supersedes` | 틀린 항목은 덮어쓰지 않는다. 새 항목이 옛 항목을 가리킨다 |
| `harness_version` | 어느 버전의 에이전트가 썼는지. 되돌릴 때 같이 걸러낸다 |

규칙 항목(`kind: rule`)은 `approved_by`, `adopted_in_round`, `enforcement`(지금 어느 층에 있는지)를 더한다.

## 4. 쓰기 정책과 보호

| 물음 | 정책 |
|---|---|
| 언제 쓰나 | 코드가 정한 시점에 쓴다: 작업 종료, 실패, 사람이 교정한 직후, 리뷰가 "알았어야 할 것"을 잡았을 때. 모델이 기억할 만하다고 느낄 때에만 맡기면 빠진다. 새로 알게 된 것이 없으면 "기록 없음"을 이벤트로 남긴다 |
| 무엇을 쓰나 | 한 건에 교훈 하나, 확인할 수 있는 문장, 근거 위치. 실패뿐 아니라 통한 방법도 쓴다. 기준은 "다음 작업자가 이걸 모르면 같은 실수를 하는가"다 |
| 쓰지 않는 것 | 코드와 git 기록에서 다시 알 수 있는 것, 지침에 이미 있는 것, 대화 전체나 도구 출력·이슈·웹 페이지 원문, 평가 정답과 테스트 기대값 |
| 시크릿 | 키·토큰·비밀번호·개인정보 패턴을 저장 전에 검사해 거부한다. 거부도 이벤트로 남긴다 |
| 저장 전 검사 | 필수 필드, 길이 상한, 시크릿, 정답 흔적, 저장소 밖을 가리키는 경로, 중복(같은 `trigger`·`lesson`이면 새로 만들지 않고 카운터만 올린다) |
| 고치는 방식 | 추가, 카운터 증가, 폐기 표시만 한다. 모델에게 파일 전체를 다시 쓰거나 요약하게 하지 않는다(9절) |
| 낡음 | 코드가 바뀌면 기억이 틀린다. 근거를 붙이고 꺼내 쓸 때 대조한다. 만료일, 정리 주기, 담당자를 정한다 |
| 오염 | 한 번 저장된 문장은 다음 세션에서 믿을 만한 내용으로 읽힌다. 외부 입력(이슈 본문, 웹, 도구 출력)을 읽은 작업에서 나온 항목은 `derived_from_external_input`과 `untrusted`로 표시하고 사람이 확인하기 전에는 주입하지 않는다 |
| 크기 | 항상 읽히는 양, 한 번에 주입하는 양, 항목 길이, 전체 건수에 상한을 둔다. 넘으면 항목 단위로 합치거나 폐기한다 |

보호
- 에이전트가 쓸 수 있는 것은 경험 저장소의 `candidate` 항목 추가뿐이다. 규칙 저장소, 스킬, 시스템 프롬프트는 6~8절의 개선안 경로로만 바뀐다.
- 지시문으로 막지 않는다. 실행 전 검사(S5)로 편집 도구와 셸 양쪽의 쓰기를 막고 차단 시험을 남긴다.
- 사람이 열어 읽을 수 있는 평문으로 두고, 모든 변경을 버전 관리에 남겨 되돌릴 수 있게 한다.
- 저장(`memory_write`), 검사 거부, 폐기를 이벤트로 기록한다.

## 5. 조회·주입 정책

| 물음 | 정책 |
|---|---|
| 무엇으로 찾나 | 범위 필터(`scope`) 다음에 키워드(`trigger`의 오류 문자열·심볼·파일명). 코딩 작업의 조회 키는 그대로 일치해야 하는 문자열이 많다. 임베딩은 키워드가 놓치는 항목이 있다고 측정된 뒤에 함께 쓴다. 둘을 코딩 에이전트 메모리에서 직접 비교한 자료는 찾지 못했다. 이 순서는 판단이고 측정으로 고친다 |
| 언제 | 요청을 받은 직후(계획 전), 실패 직후(그 오류 문자열로) |
| 주입 전 확인 | 근거(파일·커밋)가 지금 코드와 맞는지 본다. 안 맞으면 주입하지 않고 `harmful`을 올린다. `untrusted`, `deprecated`, 만료된 항목은 주입하지 않는다 |
| 얼마나 | 3~5건(제안값)과 토큰 상한. `trigger`와 `lesson`만 넣고 근거는 경로로 가리킨다 |
| 어디에 | 시스템 프롬프트가 아니라 요청 뒤의 메시지로 한 번 붙인다. 대화 중에 지우거나 바꾸지 않는다. 시스템 프롬프트를 요청마다 바꾸면 캐시가 깨지고 모든 요청에 영향이 간다 |
| 무엇을 남기나 | 계획의 "참조한 경험" 구역에 항목 ID와 그 때문에 달라진 점(없으면 "없음"). 기록에 `memory_retrieve`(질의, 필터, 후보 ID, 근거 확인 결과, 주입한 ID, 토큰 수. 결과 없음과 조회 오류를 구분한다). 작업 뒤 `memory_feedback`(ID별 도움 / 해로움 / 안 씀)으로 카운터를 올린다 |
| 끄는 방법 | 주입 토글을 둔다. 대조 실행(주입 없이 같은 작업)과 사고 대응에 쓴다 |

조회 기록은 "꺼냈다"일 뿐이다. "썼다"는 계획 인용, 교훈을 따른 코드 변경, 주입을 끈 실행과의 차이로 보인다.

## 6. 개선안 형식

```json
{
  "proposal_id": "imp-r2-c1", "round": 2, "base_version": "r1", "status": "proposed",
  "target": {"kind": "skill", "path": "skills/write-tests/SKILL.md", "section": "procedure"},
  "evidence": [{"run_id": "req-0412", "event_ids": ["ev-118"], "failure_type": "테스트 미실행"}],
  "observation": "읽기용 12건 중 4건에서 수정 뒤 테스트 명령이 실행되지 않았다.",
  "hypothesis": "스킬 본문에 테스트 대상 선택 규칙이 없어 전체 실행을 피하려다 건너뛴다.",
  "alternatives": ["턴 예산이 모자라 끝냈다", "테스트 명령이 실패해 조용히 넘어갔다"],
  "change": {"format": "unified_diff", "patch_file": "improve/r2/c1.patch", "added_tokens": 96, "removed_tokens": 0},
  "expected_effect": {"metric": "판정용 사례의 '테스트 미실행' 실패 수", "direction": "down", "cases_expected_to_flip": 3},
  "predicted_regressions": ["테스트가 없는 모듈에서 불필요한 테스트 생성"],
  "layer_check": "끝내기 전 검사(훅)로 강제할 수 있다. 이번에는 스킬 문구, 재발하면 훅으로 옮긴다.",
  "forbidden_check": {"touched_paths": ["skills/write-tests/SKILL.md"], "violations": []},
  "rollback": "git revert <커밋>, 버전 표시를 r1로",
  "improver_input_hash": "sha256:…"
}
```

- 관찰 사실, 원인 가설, 다른 설명을 나눠 적는다. 근거는 기록의 이벤트 ID다.
- 개선안은 파일로만 만든다. 만드는 시점에 대상 파일은 바뀌지 않는다(작업 폴더에 변경이 없다).
- 변경은 항목 단위 diff로 받는다. 거부한 후보도 사유와 함께 남긴다.

## 7. 개선안이 고칠 수 있는 것과 없는 것

한 라운드에 한 종류, 가설 하나만 연다. 오른쪽 두 칸은 지시문이 아니라 코드로 강제한다.

| 고칠 수 있다 | 고칠 수 없다 | 막는 장치 |
|---|---|---|
| 시스템 프롬프트의 지정 구역 | 평가셋, 정답, 숨긴 테스트, 사례 분할(ID 목록) | 개선안을 만드는 쪽과 평가받는 에이전트가 읽지도 쓰지도 못하는 위치에 둔다 |
| 스킬 문서 하나 (설명문 또는 본문) | 채점기 코드, 채점 기준표, 임계값, 반복 수, 채택 기준 | 평가 하네스 해시를 실행 전후에 비교한다 |
| 메모리 규칙 항목의 추가·폐기 | 권한 설정, 도구 허용 정책, 훅·게이트 코드, 금지 행동 목록 | 변경 경로 허용 목록. 밖이면 거부한다 |
| | 예산(턴·시간·토큰), 모델, 추론 강도 (S7에서 다룬다) | 설정 파일을 허용 목록에서 뺀다 |
| | 실행 기록(삭제·수정), 저장소의 테스트 코드 | 기록은 추가만 되게 하고 테스트 경로를 허용 목록에서 뺀다 |
| | 개선 루프와 판정기의 코드, 이 표 | 위와 같다 |

형식 검사에서 거부하는 것: 허용 목록 밖 경로, 문서 전체 교체, 기준을 낮추는 문구(예: "테스트가 실패해도 진행"), 실패 사례의 고유 문자열을 그대로 붙여 넣은 변경(외우기), 현재 버전과 같은 후보, 길이 상한 초과.

## 8. 채택 절차 (사전 등록)

판정은 채택 / 보류 / 기각 / 판정 불가 넷 중 하나다. 위에서부터 보고, 걸리면 거기서 멈춘다. 어디에도 해당하지 않으면 보류다.

| # | 단계 | 확인하는 것 | 걸리면 |
|---|---|---|---|
| 0 | 사전 등록 | 결과를 보기 전에 파일로 커밋한다: 손잡이와 허용 경로 / 사례 ID 목록(읽기용, 판정용) / 주 지표와 최소 효과 / 가드레일 상한(통과 1건당 비용, 지연, 항상 읽히는 토큰) / 최대 라운드, 비용 상한, 승인자, 되돌리기 기준 | — |
| 1 | 잴 수 있는가 | 하네스 해시 일치. 개선안 입력에 정답·임계값·판정용 ID·테스트 기대값이 없다. 양쪽 평가 완료율이 기준 이상(제안값: 90%). 응답에 찍힌 모델이 설정과 같다. 현재 버전에 고칠 실패가 있다. 흔들림 폭이 최소 효과보다 작다 | 판정 불가 ("개선 없음"이 아니라 "재지 못함") |
| 2 | 관문 | 후보 실행에 정책 위반이 없고 금지 경로를 건드리지 않았다 | 기각 |
| 3 | 회귀 | 현재 버전과 후보를 같은 조건으로 돌려 "평가 회귀가 없다"를 만족한다. 정의, 반복 수, 흔들림 폭 재는 법은 [`harness/reference/eval.md`](eval.md)를 그대로 따른다 | 보류 |
| 4 | 효과 | 판정용 사례에서 주 지표가 최소 효과 이상 올랐다 | 읽기용만 올랐으면 기각(과적합), 모자라면 보류 |
| 5 | 가드레일 | 비용, 지연, 항상 읽히는 토큰 증가가 상한 안이다 | 보류 |
| 6 | 작동 확인 | 후보 실행의 기록에 바뀐 항목이 실제로 읽히고 인용된 흔적이 있다. 변경으로 설명하기 어려울 만큼 올랐으면 사례 몇 건을 직접 연다 | 보류 |
| 7 | 사람 승인 | 항상 읽히는 규칙·스킬·시스템 프롬프트의 변경은 승인자가 diff와 사례별 비교표를 보고 승인한다. 개선안을 만든 쪽은 승인자가 될 수 없다 | 보류 |
| 8 | 반영 전 최종 확인 | 승인받은 diff 그대로(해시 일치)를 현재 버전 위의 깨끗한 작업 폴더에 적용한다. 하네스 해시와 금지 경로를 다시 검사하고, 개발용 평가 전체를 한 번 돌려 2·3을 다시 본다. 비교 뒤 현재 버전이 그대로이고 분할 없이 전체를 이미 돌렸으면 재실행은 생략한다 | 보류 (반영하지 않는다) |
| 9 | 반영 | 커밋 하나로 넣고 버전 표시를 올린다(r1 → r2). 되돌리는 명령을 적는다. 새 세션에서 같은 종류의 작업을 돌려 반영분이 읽히고 인용된 기록을 남긴다 | — |
| 10 | 사후 확인 | 정한 기간·건수 동안 지표를 보고 되돌리기 기준에 닿으면 이전 버전으로 돌린다. 그 버전이 쓴 경험 항목(`harness_version`)도 걸러낸다 | 되돌림 |

- **사례를 나눈다.** 개선안을 만드는 쪽은 읽기용 사례의 기록만 읽고, 판정은 그쪽이 본 적 없는 판정용 사례로 한다. 유형별로 무작위로 뽑고 기준선 점수를 보고 고르지 않는다. 사례가 적어 나눌 수 없으면 나누지 않고 반복 실행으로 흔들림을 줄이되 결과에 "분할 없음, 방향성 판정"이라고 적는다.
- **최종 확인용 데이터는 이 루프에서 열지 않는다.** 채택분은 "릴리스 후보"다. 최종 확인용 평가와 팀 배포는 S8에서 한 번 한다.
- **후보가 여럿이면** 판정용 결과로 고르고, 비슷하면 변경이 가장 작은 것을 고른다.
- **실행 조건.** 현재 버전과 후보를 메모리·설정이 섞이지 않는 분리된 프로필에서 돌린다. 시도마다 초기 상태를 복원하고 새 세션에서 잰다. 이전 시도의 작업 폴더와 git 기록이 다음 시도에 보이지 않게 한다.
- **기록.** 라운드마다 `improve/round-<n>.json`을 새 파일로 쓴다(덮어쓰기 금지): 현재 버전, 후보, 거부 사유, 사례별 비교표, 판정과 사유, 하네스 해시, 개선안 입력 해시, 승인자.
- **되돌리기.** 채택 1건이 커밋 1개다. 되돌리는 명령을 한 번은 실제로 실행해 이전 버전이 기록에 찍히는지 본다.
- **멈춤 조건.** 최대 라운드, 비용 상한, 하네스 해시 불일치나 오염 발견(즉시), 2~3 라운드(제안값) 연속으로 효과가 흔들림 폭을 못 넘음. 정체하면 내용을 더 고치지 않고 남은 실패를 지침 부족 / 채점기 / 환경·하네스 / 구조 / 흔들림으로 나눈다.

## 9. 알려진 실패 양상과 안전장치

| 실패 양상 | 어떻게 생기나 | 안전장치 |
|---|---|---|
| 평가셋 과적합 | 개선안은 자기가 읽은 실패에 맞춰진다. 그 사례로 판정하면 점수만 오른다. 최종 확인용으로 여러 번 고르면 그 데이터에도 맞춰진다 | 읽기용·판정용 분리, 최종 확인용은 릴리스 전 한 번, 외우기 형식 검사, 흔들림 폭보다 작은 차이는 채택하지 않기, 운영 기록으로 평가셋 보충(S8) |
| 목표 해킹·테스트 변조 | 점수를 올리는 가장 쉬운 길이 채점 코드나 테스트를 고치거나, 정답을 읽거나, 실행 기록을 꾸미거나, 탐지 장치를 없애는 것일 수 있다. 스스로 코드를 고치는 에이전트와 평가 연구에서 이런 사례가 보고됐고, "하지 말라"는 지시만으로는 잘 막히지 않았다고 한다(확인 필요) | 7절 표를 코드로 강제(허용 목록, 해시, 읽을 수 없는 위치), 자기 보고가 아니라 환경에서 읽은 결과로 채점, 이상하게 높은 점수는 손으로 확인, 사람 승인 |
| 반복 재작성으로 무너짐 | 프롬프트나 메모리를 통째로 다시 쓰게 하면 회를 거듭할수록 짧고 일반적인 문장만 남고 세부 규칙이 사라진다고 보고됐다(확인 필요). 반대로 라운드마다 "조심하라"를 쌓으면 길어지기만 한다 | 항목 단위 추가·폐기 diff만 받기, 전체 교체 거부, 항목 ID와 도움·해로움 카운터, 길이 상한, 항상 읽히는 토큰 수를 가드레일로 두기 |
| 기억 오염 | 외부 입력에 섞인 지시가 경험으로 저장돼 다음 세션에서 믿을 만한 내용으로 읽힌다 | 출처 신뢰 등급, `untrusted` 미주입, 규칙 저장소 읽기 전용, 변경 이력 |
| 낡은 기억 | 코드가 바뀌어 교훈이 틀려졌는데 계속 주입된다 | 주입 전 근거 대조, 만료, `harmful` 카운터 |
| 틀린 신호로 고치기 | 원인이 채점기나 환경인데 지침만 계속 고친다 | "판정 불가" 구분, 정체 시 실패 분류, 채점기 반례 시험(S1) |

## 10. 인수 기준 3-1~3-4를 증거로 보이는 방법

| 항목 | 약한 증거 | 강한 증거 | README 확인 방법 (입력 → 기대 관찰 → 확인 명령) |
|---|---|---|---|
| 3-1 저장·유지 | 저장소 파일이 있다 (손으로 만들어도 생긴다) | 기록의 저장 이벤트(항목 ID, 실행 ID) + 프로세스를 끝낸 뒤 새 세션이 같은 경로로 그 ID를 읽는다 + 규칙과 경험이 다른 저장소에 한 건씩 + 실패한 작업에서 생긴 항목 | 일부러 실패하는 작업 실행 → 종료 → 경험 파일 마지막 줄에 실패 항목 → 파일에서 ID 검색, 기록 조회로 저장 이벤트 확인 |
| 3-2 검색·실제 활용 | 기록에 조회 이벤트가 있다 | 새 세션의 조회 이벤트에 앞 세션이 남긴 ID가 "주입됨" + 계획의 "참조한 경험"에 그 ID와 반영 내용 + 교훈을 따른 코드 변경 + 주입을 끄고 돌린 결과와 다르다 | 앞 작업과 비슷한 요청을 새 세션에 입력 → 계획에 참조한 경험 ID → 요청 ID로 조회·사후 이벤트 출력. 대조: 주입을 끄고 같은 요청 |
| 3-3 개선안 생성 | "개선이 필요하다"는 문장 | 실패 기록의 이벤트 ID를 인용한 개선안 파일(관찰, 가설, 변경 diff, 기대 효과, 예상 회귀) + 대상이 시스템 프롬프트·스킬·메모리 규칙 중 하나로 명시 + 만든 시점에 대상 파일 변경 없음 + 금지 경로를 건드린 후보가 거부된 기록 | 실패하는 평가 시나리오 실행 → 개선 명령 실행 → 개선안 파일과 diff 생성 → 작업 폴더에 대상 파일 변경이 없음을 확인 |
| 3-4 전후 검증·반영 | 전후 점수 두 개 | 결과보다 먼저 커밋된 사전 등록 파일 + 같은 조건의 사례별 전후 표 + 회귀 결과 + 판정과 사유 + 탈락한 후보가 반영되지 않았다는 확인 + 채택분의 버전 표시와 커밋 + 반영 뒤 새 세션에서 쓰인 기록 | 평가 명령을 현재 버전과 후보로 실행 → 비교표 → 라운드 기록의 판정 → 버전 표시 변경 → 새 세션 요청의 기록에 새 버전과 해당 항목 ID |

보류로 끝난 라운드도 3-4의 절차 증거는 된다. "통과한 개선안을 다음 작업에 반영"까지 보이려면 채택이 한 번은 있어야 한다. 고칠 수 있는 실패(예: 테스트 명령을 모르는 상태)를 하나 준비해 둔다.

## 참고 자료

"(확인 필요)"는 요약 도구를 거쳐 읽은 자료다. 반영한 내용은 원문과 한 번 대조한다.

메모리
- Anthropic, Memory tool: https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool
- Claude Code 문서, 메모리: https://code.claude.com/docs/en/memory
- Anthropic, Managed Agents 메모리: https://platform.claude.com/docs/en/managed-agents/memory
- GitHub Blog, Building an agentic memory system for GitHub Copilot (확인 필요): https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/
- GitHub Docs, Copilot Memory (확인 필요): https://docs.github.com/en/copilot/concepts/agents/copilot-memory
- LangGraph 문서, Memory (확인 필요): https://docs.langchain.com/oss/python/langgraph/memory
- Anthropic, Contextual Retrieval (확인 필요): https://www.anthropic.com/news/contextual-retrieval
- MINJA, 메모리 주입 공격 (Dong 외, 2025) (확인 필요): https://arxiv.org/abs/2503.03704
- OWASP LLM04:2025 Data and Model Poisoning (확인 필요): https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/

자기개선
- Anthropic, 평가 기반 개선 루프 가이드: 공개 URL 없음 (Claude Code에 번들된 `claude-api` 스킬의 `shared/evals/eval-hillclimb.md`)
- Anthropic, Demystifying evals for AI agents (확인 필요): https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Anthropic, Writing tools for agents (확인 필요): https://www.anthropic.com/engineering/writing-tools-for-agents
- ACE (Zhang 외, 2025) (확인 필요): https://arxiv.org/abs/2510.04618
- Reflexion (Shinn 외, 2023) (확인 필요): https://arxiv.org/abs/2303.11366 / ExpeL (Zhao 외, 2023) (확인 필요): https://arxiv.org/abs/2308.10144
- Darwin Gödel Machine (Zhang 외, 2025) (확인 필요): https://arxiv.org/abs/2505.22954 , https://sakana.ai/dgm/
- SICA (Robeyns 외, 2025) (확인 필요): https://arxiv.org/abs/2504.15228
- OpenAI Cookbook, Self-evolving agents (확인 필요): https://developers.openai.com/cookbook/examples/partners/self_evolving_agents/autonomous_agent_retraining
- METR, Recent frontier models are reward hacking (확인 필요): https://metr.org/blog/2025-06-05-recent-reward-hacking/
- ImpossibleBench (Zhong 외, 2025) (확인 필요): https://arxiv.org/abs/2510.20270

최적화·배포 (`design/07-optimize.md`, `design/08-release.md`의 근거)
- Anthropic, Prompt caching (확인 필요): https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Anthropic, Optimizing for cost and intelligence (확인 필요): https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence
- Anthropic, Effort: https://platform.claude.com/docs/en/build-with-claude/effort
- Anthropic, Batch processing: https://platform.claude.com/docs/en/build-with-claude/batch-processing
- Anthropic, Reducing latency: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency
- vLLM 문서, Automatic Prefix Caching (확인 필요): https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/
- Google SRE Workbook, Canarying Releases (확인 필요): https://sre.google/workbook/canarying-releases/
- Anthropic, A postmortem of three recent issues (확인 필요): https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues
- Langfuse 문서, Datasets (확인 필요): https://langfuse.com/docs/evaluation/experiments/datasets
