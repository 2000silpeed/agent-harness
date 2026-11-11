# 훅 예시 (필요할 때 켠다)

이 폴더의 파일은 프로젝트에 설치하면 `.claude/hooks/`에 놓인다. 설치만으로는 아무것도 켜지지 않는다. 규칙이 생기고 필요가 확인되면 `settings.example.json`의 해당 부분을 `.claude/settings.json`에 옮겨서 켠다.

표준 라이브러리만 쓴다. Python 3.9 이상이 필요하다. 3.13에서 전체 시험을 돌렸고 3.11·3.12에서 컴파일과 게이트 실행을 확인했다. 3.9·3.10은 실행해 보지 않았다(확인 필요).

## 파일

| 파일 | 연결하는 곳 (매처) | 하는 일 | 차단 | 고장 나면 |
|---|---|---|---|---|
| `plan_gate.py` | PreToolUse (`Edit\|Write\|NotebookEdit`) | 사람이 승인한 계획의 수정 대상 안에서만 코드 수정을 통과시킨다. 보호 경로는 항상 막는다 | 막음 (exit 2) | 막는다 (스크립트의 예외 처리 + 설정의 `onFailure: "block"`) |
| `approve_plan.py` | 훅 아님. **사람이 자기 터미널에서** 실행 | 계획 형식을 검사하고, 수정 대상·위험 표시를 보여 준 뒤 승인 기록 `design/approvals/<plan_id>.json`을 쓴다 | — | 기록을 쓰지 않는다 (exit 1) |
| `check_plan.py` | 훅 아님. 누구나 실행 | 계획 형식 검사(리뷰에 올리기 전). 인자 없이 실행하면 계획 목록과 승인 상태를 보여 준다 | — | exit 1 |
| `plan_lib.py` | 위 세 스크립트가 불러 쓰는 공용 모듈 | 계획 읽기, 본문 해시, 경로 판정, 형식 검사, 승인 기록 대조 | — | 없으면 게이트는 막는다 |
| `protected_paths.txt` | `plan_gate.py`가 읽는다 | 보호 경로 추가 목록(예: 인수 테스트, 채점용 평가셋, CI 설정) | — | — |
| `test_after_edit.py` | PostToolUse (`Edit\|Write`) | 고친 `.py`와 이름 규칙으로 짝지은 테스트만 돌리고, 실패하면 결과를 모델에 돌려준다 | 이미 실행된 뒤라 못 막음. 알림 (exit 2) | 건너뛴다 |
| `prompt_reminder.sh` + `reminders.md` | UserPromptSubmit (매처 없음) | 짧은 사실 진술을 요청마다 덧붙인다 | 막지 않음 | 건너뛴다 |
| `stop_check.py` (선택) | Stop (매처 없음) | 끝내기 전에 검사 명령을 돌리고 실패하면 계속 일하게 한다 | 끝내기를 막음 (exit 2) | 보내 준다 |
| `statusline.py` (선택) | 훅 아님. 설정의 `statusLine` | 모델 · 컨텍스트 사용률 · 프롬프트 캐시 상태 · 세션 비용(추정)을 한 줄로 보여 준다 | — | 안내 문구 한 줄을 낸다 |
| `settings.example.json` | 연결 예시 | 위 세 훅의 연결 + 보호 경로와 승인 스크립트에 대한 권한 차단 규칙 | — | — |

## 계획 게이트가 판정하는 순서

`plan_gate.py`는 수정하려는 경로를 심볼릭 링크까지 풀어 아래 순서로 본다.

1. 세션 임시 폴더(훅 입력의 `scratchpad_dir`, v2.1.257 이상) 아래면 통과.
2. 프로젝트 밖이면 차단.
3. 보호 경로면 차단. 계획에 적혀 있어도 막는다. 내장: `design/approvals/**`, `.claude/hooks/**`, `.claude/settings*.json`. 추가분은 `protected_paths.txt`.
4. `design/` 아래이거나 마크다운(`.md`)이면 통과. 계획과 설계 문서는 계획 없이 쓴다.
5. 그 밖(코드)은 아래를 모두 만족해야 통과.
   - `design/plans/*.md` 중 `status: approved`인 계획이 정확히 하나다.
   - 그 계획의 승인 기록 `design/approvals/<plan_id>.json`이 있고, 기록의 `plan_id`·`version`·`plan_sha256`이 지금 계획과 같다.
   - 경로가 그 계획의 `## 수정 대상` 표 첫 칸에 든다(정확한 경로, `dir/*`는 바로 아래 파일, `dir/**`는 아래 전부).

계획 파일에 `status: approved`라고 적는 것만으로는 통과하지 않는다. 승인 기록이 없기 때문이다. 승인 뒤 계획 본문을 고치면 해시가 달라져 승인이 무효가 된다. 줄 끝 공백과 앞뒤 빈 줄만 다른 것은 같은 본문으로 본다. 머리말은 해시에 넣지 않는다(`status`를 바꿀 수 있어야 한다). 대신 `plan_id`와 `version`을 기록과 대조한다.

차단 메시지는 `plan_gate[규칙 ID]: 사유와 다음 행동` 형식이다.

| 규칙 ID | 뜻 |
|---|---|
| `plan.approved_required` | `status: approved`인 계획이 없다 |
| `plan.multiple_approved` | `status: approved`인 계획이 둘 이상이다 |
| `plan.approval_record_missing` | 승인 기록 파일이 없다 |
| `plan.approval_record_invalid` | 승인 기록이 JSON 객체가 아니거나 키가 빠졌다 |
| `plan.approval_stale` | 승인 기록의 version이나 해시가 지금 계획과 다르다 |
| `scope.outside_plan` | 경로가 수정 대상에 없다. 계획을 갱신하고 재리뷰·재승인을 받으라고 안내한다 |
| `protected_path` | 보호 경로다 |
| `path.outside_project` | 프로젝트 밖이다 |
| `gate.bad_input` / `gate.failure` | 입력 형태가 틀렸다 / 판정 중 오류가 났다 |

계획 파일 양식(머리말 키, 본문 구역, 구역별 형식 검사)과 상태 전이는 방법론 도구를 함께 설치했을 때 `harness/reference/plan-gate.md`에 있다. 줄여 쓰면 이렇다.

```
---
plan_id: 20261111-add-greeting     # 파일 이름과 같다
request_id:                        # 선택
version: 1                         # 본문이 바뀔 때마다 +1
status: draft                      # draft | in_review | approved | superseded | done | rejected
base_commit:                       # 선택
risk: low                          # low | medium | high
---
## 요구사항 / ## 범위 / ## 완료 조건 / ## 수정 대상 / ## 작업 순서 / ## 테스트 방법
## 위험 표시 / ## 가정·미결 질문 / ## 참조 메모리·근거 / ## 리뷰 이력 / ## 실행 결과
```

`## 실행 결과`는 코드 수정이 모두 끝난 뒤에 적는다. 본문이 바뀌는 순간 해시가 달라져 그 뒤의 코드 수정은 막힌다.

## 승인하는 법 (사람)

```bash
python3 .claude/hooks/check_plan.py                 # 계획 목록과 승인 상태
python3 .claude/hooks/check_plan.py <plan_id>       # 형식 검사 (에이전트가 돌려도 된다)
python3 .claude/hooks/approve_plan.py <plan_id> --by "이름"   # 사람만. 프로젝트 루트에서
```

`approve_plan.py`는 형식 문제가 있거나, `status`가 `in_review`가 아니거나, `## 리뷰 이력`에 현재 version의 `APPROVE` 줄(예: `- v1: APPROVE — 지적 없음`)이 없거나, 다른 `approved` 계획이 남아 있으면 거절한다. 통과하면 게이트가 실제로 읽을 수정 대상과 위험 표시를 화면에 보여 주고 `yes`를 입력받는다. 그 뒤 계획 머리말의 `status`를 `approved`로 바꾸고 기록을 쓴다.

```json
{"plan_id": "20261111-add-greeting", "version": 1, "plan_sha256": "…", "reviewer_verdict": "APPROVE",
 "approved_by": "이름", "approved_at": "2026-11-11T05:12:03Z"}
```

범위가 바뀌면 계획의 `version`을 올리고 `status`를 `in_review`로 되돌려 다시 리뷰받은 뒤 이 명령을 다시 실행한다. 같은 version에서 본문만 바꾼 재승인은 거절한다.

## 켜는 법

1. `claude --version`이 2.1.295 이상인지 본다. 그보다 낮으면 `onFailure`를 쓸 수 없으므로 그 줄을 뺀다. 이때 게이트가 시작조차 못 하는 고장(파이썬 없음, 시간 초과)은 통과가 된다.
2. `settings.example.json`에서 필요한 부분을 `.claude/settings.json`에 옮긴다. 형식은 exec 형식(`command` + `args`)이고 경로는 `${CLAUDE_PROJECT_DIR}` 기준이다.
3. `claude doctor`를 돌려 `Invalid settings`가 없는지 본다(이 예시는 v2.1.322에서 경고 없이 통과했다). 세션 안에서는 `/hooks`에 등록이 보이는지 본다.
4. 아래 "세 가지 입력 시험"을 프로젝트에서 직접 돌린다.
5. 세션에서 위반을 한 번 시도해 본다. 차단 사유가 대화 기록에 보여야 한다. `onFailure`는 스크립트 경로를 일부러 틀리게 적어 막히는지 본다.

매처 메모
- 파일을 고치는 도구는 `Edit`, `Write`, `NotebookEdit`다. `NotebookEdit`는 경로를 `notebook_path`에 담는다(`plan_gate.py`가 둘 다 읽는다).
- `MultiEdit`는 현재 도구 목록에 없는 옛 이름이다. 옛 버전을 쓴다면 매처에 `|MultiEdit`를 더한다(그 버전에서 실제로 호출되는지는 확인 필요).
- `test_after_edit.py`는 `.py`만 다루므로 매처에 `NotebookEdit`를 넣지 않았다.
- `UserPromptSubmit`과 `Stop`은 매처가 없는 이벤트다.

권한 차단 규칙(`settings.example.json`의 `permissions.deny`)
- `Edit(/design/approvals/**)`, `Edit(/.claude/hooks/**)`, `Edit(/.claude/settings*.json)`: 파일 도구(Edit·Write·NotebookEdit)와 하네스가 알아보는 셸 파일 명령·리다이렉션의 쓰기를 막는다. 게이트와 같은 경로를 한 번 더 막는 것이다.
- `Bash(*approve_plan*)`: 에이전트가 승인 스크립트를 실행하는 흔한 형태를 막는다.
- 이 규칙을 넣으면 Claude에게 설정 파일 수정을 시킬 수 없다. 설정과 훅은 사람이 고친다.

선택 항목 연결

```json
{ "hooks": { "Stop": [ { "hooks": [ { "type": "command", "command": "python3",
    "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/stop_check.py"], "timeout": 330 } ] } ] } }
```

Stop 훅에는 `onFailure`가 듣지 않는다. 검사 명령이 느리면 응답마다 그만큼 기다린다.

```json
{ "statusLine": { "type": "command", "command": "python3 ~/.claude/statusline.py" } }
```

`statusline.py`는 `~/.claude/`에 복사해 사용자 설정(`~/.claude/settings.json`)에 연결한다. 캐시 필드(`prompt_cache`)는 v2.1.251 이상에서 온다. 60%·80% 표시는 (제안값)이다.

## 세 가지 입력 시험

훅마다 정상·위반·깨진 입력을 넣어 종료 코드를 본다. 프로젝트 루트에서 실행한다. 막는 훅은 깨진 입력에 2, 알리는 훅은 0이 나와야 한다.

```bash
export CLAUDE_PROJECT_DIR="$PWD"

# plan_gate.py (막는 훅: 깨진 입력도 2여야 한다)
echo '{"tool_name":"Write","tool_input":{"file_path":"'"$PWD"'/README.md"}}' | python3 .claude/hooks/plan_gate.py; echo "정상(문서 수정) exit=$?"
echo '{"tool_name":"Edit","tool_input":{"file_path":"'"$PWD"'/src/app.py"}}' | python3 .claude/hooks/plan_gate.py; echo "위반(승인 없이 코드 수정) exit=$?"
echo '[]' | python3 .claude/hooks/plan_gate.py; echo "깨진 입력 exit=$?"

# test_after_edit.py (알리는 훅: 깨진 입력은 0으로 건너뛴다)
echo '{"tool_input":{"file_path":"'"$PWD"'/src/app.py"}}' | python3 .claude/hooks/test_after_edit.py; echo "정상(짝 테스트 통과) exit=$?"
echo '{"tool_input":{"file_path":"'"$PWD"'/src/lonely.py"}}' | python3 .claude/hooks/test_after_edit.py; echo "위반(짝 테스트 없음) exit=$?"
echo '[]' | python3 .claude/hooks/test_after_edit.py; echo "깨진 입력 exit=$?"

# prompt_reminder.sh (붙이는 훅: 막지 않는다. 입력을 읽지 않으므로 '위반' 입력이 없다)
echo '{"prompt":"hi"}' | bash .claude/hooks/prompt_reminder.sh; echo "정상 exit=$?"
echo '{broken' | bash .claude/hooks/prompt_reminder.sh >/dev/null; echo "깨진 입력 exit=$?"

# stop_check.py (선택. 끝내기를 막는 훅: 깨진 입력은 0으로 보내 준다)
echo '{"stop_hook_active":false}' | python3 .claude/hooks/stop_check.py; echo "검사 결과대로(통과 0, 실패 2) exit=$?"
echo '{"stop_hook_active":true}' | python3 .claude/hooks/stop_check.py; echo "이미 이어서 일하는 중 exit=$?"
echo '{broken' | python3 .claude/hooks/stop_check.py; echo "깨진 입력 exit=$?"
```

`src/app.py`에 짝 테스트 `tests/test_app.py`가 있고 `src/lonely.py`에는 없는 프로젝트에서 위 명령은 차례로 0, 2, 2 / 0, 2, 0 / 0, 0 / 0, 0, 0을 냈다.

## 시험 결과

2026-11-11, Python 3.13.18. 설치 스크립트로 임시 프로젝트를 만들고 훅마다 stdin에 JSON을 넣어 실행한 실제 종료 코드다. 실제 세션에서 훅이 발동하는지는 이 표에 없다("한계" 참고).

읽는 법
- 입력 칸의 `Edit src/app.py`는 `{"tool_name":"Edit","tool_input":{"file_path":"<프로젝트>/src/app.py"}}`를 넣었다는 뜻이다. `NotebookEdit`는 `notebook_path`에 넣었다. `+키`는 입력에 그 키를 더했다는 뜻이다.
- 시험 계획의 수정 대상은 `src/app.py`, `src/util/**`, `src/api/*`, `nb/analysis.ipynb`다.
- `approve_plan.py`의 "터미널"은 가짜 터미널(pty)에서 실행해 사람의 입력을 흉내 낸 것이다.
- 종료 코드: 게이트 0 통과 / 2 차단, `approve_plan.py`·`check_plan.py` 0 성공 / 1 거절.

| # | 훅 | 상황 | 입력 | 기대 | 실제 | 차단 규칙·출력 |
|---|---|---|---|---|---|---|
| 1 | plan_gate | 계획 없음 → 코드 수정 | `Edit src/app.py` | 2 | 2 | plan.approved_required |
| 2 | plan_gate | 계획 없음 → 마크다운 | `Write README.md` | 0 | 0 |  |
| 3 | plan_gate | 계획 없음 → 계획 파일 쓰기 | `Write design/plans/20261111-add-greeting.md` | 0 | 0 |  |
| 4 | plan_gate | 계획 없음 → 설계 문서 | `Write design/02-baseline.md` | 0 | 0 |  |
| 5 | plan_gate | 계획 없음 → 스킬 문서(.claude 안의 .md) | `Write .claude/skills/x/SKILL.md` | 0 | 0 |  |
| 6 | plan_gate | draft 계획 → 코드 수정 | `Edit src/app.py` | 2 | 2 | plan.approved_required |
| 7 | approve_plan | draft 계획 승인 시도 | `approve_plan.py 20261111-add-greeting (터미널, 입력 'yes')` | 1 | 1 | approve_plan: 승인할 수 없습니다. / status가 'draft'입니다. 리뷰를 거친 계획(in_review)만 승인합니다 |
| 8 | plan_gate | in_review 계획(승인 전) → 코드 수정 | `Edit src/app.py` | 2 | 2 | plan.approved_required |
| 9 | plan_gate | 에이전트가 status: approved만 써넣음(승인 기록 없음) | `Edit src/app.py` | 2 | 2 | plan.approval_record_missing |
| 10 | plan_gate | 해시가 틀린 승인 기록 | `Edit src/app.py` | 2 | 2 | plan.approval_stale |
| 11 | plan_gate | JSON이 아닌 승인 기록 | `Edit src/app.py` | 2 | 2 | plan.approval_record_invalid |
| 12 | check_plan | 형식이 맞는 계획 | `check_plan.py 20261111-add-greeting` | 0 | 0 | check_plan: 20261111-add-greeting v1 형식 검사 통과 (본문 sha256 5c1941daeca5… |
| 13 | check_plan | 구역(위험 표시)이 빠진 계획 | `check_plan.py 20261111-add-greeting` | 1 | 1 | check_plan: 20261111-add-greeting v1 형식 문제 1건 |
| 14 | approve_plan | 구역이 빠진 계획 승인 시도 | `approve_plan.py 20261111-add-greeting (터미널, 입력 'yes')` | 1 | 1 | approve_plan: 승인할 수 없습니다. / '## 위험 표시' 구역이 없습니다 |
| 15 | approve_plan | 리뷰 판정이 REVISE인 계획 | `approve_plan.py 20261111-add-greeting (터미널, 입력 'yes')` | 1 | 1 | approve_plan: 승인할 수 없습니다. / '## 리뷰 이력'에 v1의 APPROVE 판정 줄이 없습니다(현재: REVISE). 예: '- v1: APPROVE — 지적 없음' |
| 16 | approve_plan | 수정 대상에 보호 경로가 든 계획 | `approve_plan.py 20261111-add-greeting (터미널, 입력 'yes')` | 1 | 1 | approve_plan: 승인할 수 없습니다. / 수정 대상 '.claude/hooks/plan_gate.py': 보호 경로는 계획에 넣을 수 없습니다(사람이 직접 고친다) |
| 17 | approve_plan | 터미널이 아닌 곳에서 실행(에이전트 셸 흉내) | `approve_plan.py 20261111-add-greeting (터미널 아님, 입력을 파이프로)` | 1 | 1 | approve_plan: 사람이 자기 터미널에서 직접 실행해야 합니다(에이전트 셸이거나 입력이 터미널이 아닙니다). 에이전트는 이 스크립트를 실행하지 않고 사용자에게 실행을 요청합니다. |
| 18 | approve_plan | 터미널이지만 CLAUDECODE=1(에이전트 셸 표시) | `approve_plan.py 20261111-add-greeting (터미널, 입력 'yes')` | 1 | 1 | approve_plan: 사람이 자기 터미널에서 직접 실행해야 합니다(에이전트 셸이거나 입력이 터미널이 아닙니다). 에이전트는 이 스크립트를 실행하지 않고 사용자에게 실행을 요청합니다. |
| 19 | approve_plan | 확인 질문에 no | `approve_plan.py 20261111-add-greeting (터미널, 입력 'no')` | 1 | 1 | approve_plan: 승인하지 않았습니다. 바뀐 것은 없습니다. |
| 20 | approve_plan | └ 그 뒤 승인 기록 없음 확인 | `test -e design/approvals/<plan_id>.json` | 1 | 1 |  |
| 21 | approve_plan | 정상 승인(사람, 터미널, yes) | `approve_plan.py 20261111-add-greeting (터미널, 입력 'yes')` | 0 | 0 | approve_plan: 20261111-add-greeting v1 승인 기록을 썼습니다 → design/approvals/20261111-add-greeting.json |
| 22 | check_plan | 목록(승인 기록 유효 표시) | `check_plan.py` | 0 | 0 | 20261111-add-greeting  v1  approved  [승인 기록 유효] |
| 23 | plan_gate | 승인 뒤 → 수정 대상 안(정확한 경로) | `Edit src/app.py` | 0 | 0 |  |
| 24 | plan_gate | 승인 뒤 → 수정 대상 안(dir/** 아래 깊은 파일) | `Write src/util/text/fmt.py` | 0 | 0 |  |
| 25 | plan_gate | 승인 뒤 → 수정 대상 안(dir/* 바로 아래) | `Edit src/api/v1.py` | 0 | 0 |  |
| 26 | plan_gate | 승인 뒤 → dir/*의 하위 폴더(범위 밖) | `Edit src/api/deep/v2.py` | 2 | 2 | scope.outside_plan |
| 27 | plan_gate | 승인 뒤 → 수정 대상 밖 | `Edit src/other.py` | 2 | 2 | scope.outside_plan |
| 28 | plan_gate | 승인 뒤 → 서브에이전트의 범위 밖 수정 | `Edit src/other.py +agent_id +agent_type` | 2 | 2 | scope.outside_plan |
| 29 | plan_gate | 승인 뒤 → NotebookEdit 수정 대상 안 | `NotebookEdit nb/analysis.ipynb` | 0 | 0 |  |
| 30 | plan_gate | 승인 뒤 → NotebookEdit 수정 대상 밖 | `NotebookEdit nb/other.ipynb` | 2 | 2 | scope.outside_plan |
| 31 | plan_gate | 승인 뒤 → 보호 경로: 게이트 코드 | `Edit .claude/hooks/plan_gate.py` | 2 | 2 | protected_path |
| 32 | plan_gate | 승인 뒤 → 보호 경로: 훅 폴더의 .md | `Edit .claude/hooks/reminders.md` | 2 | 2 | protected_path |
| 33 | plan_gate | 승인 뒤 → 보호 경로: 설정 | `Write .claude/settings.json` | 2 | 2 | protected_path |
| 34 | plan_gate | 승인 뒤 → 보호 경로: 로컬 설정 | `Write .claude/settings.local.json` | 2 | 2 | protected_path |
| 35 | plan_gate | 승인 뒤 → 보호 경로: 승인 기록 | `Write design/approvals/20261111-add-greeting.json` | 2 | 2 | protected_path |
| 36 | plan_gate | 승인 뒤 → 보호 경로(대소문자만 다름) | `Edit .Claude/Hooks/plan_gate.py` | 2 | 2 | protected_path |
| 37 | plan_gate | 승인 뒤 → 프로젝트 밖 | `Edit /etc/hosts` | 2 | 2 | path.outside_project |
| 38 | plan_gate | 승인 뒤 → '..'으로 돌아가는 경로 | `Edit design/../src/other.py` | 2 | 2 | scope.outside_plan |
| 39 | plan_gate | 승인 뒤 → design/ 안의 심볼릭 링크(실제는 src/other.py) | `Edit design/link.py` | 2 | 2 | scope.outside_plan |
| 40 | plan_gate | 세션 임시 폴더(scratchpad_dir) 안 | `Write /tmp/scratch-x/notes.py +scratchpad_dir` | 0 | 0 |  |
| 41 | plan_gate | 경로 키가 없는 도구 입력(Bash 등) | `Bash ls` | 2 | 2 | gate.bad_input |
| 42 | plan_gate | 깨진 입력: JSON 배열 | `[]` | 2 | 2 | gate.bad_input |
| 43 | plan_gate | 깨진 입력: JSON 문자열 | `"x"` | 2 | 2 | gate.bad_input |
| 44 | plan_gate | 깨진 입력: null | `null` | 2 | 2 | gate.bad_input |
| 45 | plan_gate | 깨진 입력: tool_input이 문자열 | `{"tool_input":"x"}` | 2 | 2 | gate.bad_input |
| 46 | plan_gate | 깨진 입력: file_path가 숫자 | `{"tool_input":{"file_path":123}}` | 2 | 2 | gate.bad_input |
| 47 | plan_gate | 깨진 입력: tool_input이 빈 객체 | `{"tool_input":{}}` | 2 | 2 | gate.bad_input |
| 48 | plan_gate | 깨진 입력: 빈 입력 | `(빈 입력)` | 2 | 2 | gate.failure |
| 49 | plan_gate | 깨진 입력: JSON 아님 | `{broken` | 2 | 2 | gate.failure |
| 50 | plan_gate | 깨진 입력: UTF-8이 아닌 바이트 | `{"tool_input":{"file_path":"<0xFF 0xFE>"}}` | 2 | 2 | gate.failure |
| 51 | plan_gate | 승인 뒤 계획 본문 수정(수정 대상 추가) → 추가한 파일 | `Edit src/other.py` | 2 | 2 | plan.approval_stale |
| 52 | plan_gate | 승인 뒤 계획 본문 수정 → 원래 범위 안 파일도 | `Edit src/app.py` | 2 | 2 | plan.approval_stale |
| 53 | plan_gate | 머리말 version만 올림(기록은 v1) | `Edit src/app.py` | 2 | 2 | plan.approval_stale |
| 54 | plan_gate | 줄 끝 공백만 달라짐(같은 본문으로 본다) | `Edit src/app.py` | 0 | 0 |  |
| 55 | plan_gate | v2로 갱신(in_review, 재승인 전) → 코드 수정 | `Edit src/app.py` | 2 | 2 | plan.approved_required |
| 56 | approve_plan | v2 재승인 | `approve_plan.py 20261111-add-greeting (터미널, 입력 'yes')` | 0 | 0 | approve_plan: 20261111-add-greeting v2 승인 기록을 썼습니다 → design/approvals/20261111-add-greeting.json |
| 57 | plan_gate | v2 재승인 뒤 → 새로 추가한 파일 | `Edit src/other.py` | 0 | 0 |  |
| 58 | approve_plan | 승인 뒤 본문을 고치고 version은 그대로 둔 채 재승인 시도 | `approve_plan.py 20261111-add-greeting (터미널, 입력 'yes')` | 1 | 1 | approve_plan: 승인할 수 없습니다. / version 2은 다른 본문으로 이미 승인됐습니다. 본문을 고쳤다면 version을 올리고 다시 리뷰받은 뒤 승인합니다 |
| 59 | plan_gate | approved 계획이 둘 | `Edit src/app.py` | 2 | 2 | plan.multiple_approved |
| 60 | approve_plan | 다른 approved 계획이 있을 때 승인 시도 | `approve_plan.py 20261111-add-greeting (터미널, 입력 'yes')` | 1 | 1 | approve_plan: 승인할 수 없습니다. / 이미 approved인 다른 계획이 있습니다(20261110-old). done 또는 superseded로 정리한 뒤 승인합니다 |
| 61 | plan_gate | status: done(승인 기록은 남아 있음) → 코드 수정 | `Edit src/app.py` | 2 | 2 | plan.approved_required |
| 62 | plan_gate | 보호 목록의 테스트가 승인된 계획에 들어 있음 | `Edit tests/acceptance/test_contract.py` | 2 | 2 | protected_path |
| 63 | plan_gate | 설정 파일이 승인된 계획에 들어 있음 | `Edit .claude/settings.json` | 2 | 2 | protected_path |
| 64 | check_plan | 수정 대상에 '..' 경로 | `check_plan.py 20261111-add-greeting` | 1 | 1 | 수정 대상 '../secrets.py': '.', '..', 빈 구간, 끝 슬래시는 쓸 수 없습니다(폴더 전체는 'dir/**') |
| 65 | check_plan | 수정 대상에 중간 와일드카드 | `check_plan.py 20261111-add-greeting` | 1 | 1 | 수정 대상 'src/*/x.py': 와일드카드는 끝의 '/*' 또는 '/**' 하나만 쓸 수 있습니다 |
| 66 | check_plan | 수정 대상에 보호 경로를 품는 폴더 | `check_plan.py 20261111-add-greeting` | 1 | 1 | 수정 대상 '.claude/**': 보호 경로는 계획에 넣을 수 없습니다(사람이 직접 고친다) |
| 67 | check_plan | 수정 대상에 보이지 않는 문자 | `check_plan.py 20261111-add-greeting` | 1 | 1 | 수정 대상 'src/a\u200b.py': 공백이나 보이지 않는 문자가 들어 있습니다 |
| 68 | check_plan | 수정 대상 구역이 두 번 | `check_plan.py 20261111-add-greeting` | 1 | 1 | 구역이 두 번 나옵니다: '## 수정 대상' |
| 69 | check_plan | 완료 조건에 대응 없는 요구(R2) | `check_plan.py 20261111-add-greeting` | 1 | 1 | 완료 조건: 대응하는 조건이 없는 요구가 있습니다(R2) |
| 70 | check_plan | 확인 명령이 빈 완료 조건 | `check_plan.py 20261111-add-greeting` | 1 | 1 | 완료 조건 C1: 확인 명령이나 기대 관찰 칸이 비어 있습니다 |
| 71 | check_plan | 테스트 파일을 고치는데 위험 표시 '없음' | `check_plan.py 20261111-add-greeting` | 1 | 1 | 수정 대상에 테스트·잠금 파일이 있는데 위험 표시가 '없음'입니다(tests/test_app.py) |
| 72 | check_plan | 위험 표시가 있는데 risk: low | `check_plan.py 20261111-add-greeting` | 1 | 1 | 위험 표시에 항목이 있으면 머리말 risk는 medium 이상이어야 합니다 |
| 73 | check_plan | 머리말 plan_id가 파일 이름과 다름 | `check_plan.py 20261111-add-greeting` | 1 | 1 | 머리말 plan_id('something-else')가 파일 이름('20261111-add-greeting')과 다릅니다 |
| 74 | plan_gate | 승인 기록은 맞지만 수정 대상 구역이 두 번인 계획 | `Edit src/other.py` | 2 | 2 | gate.failure |
| 75 | plan_gate | 한계: 셸로 해시까지 맞춘 승인 기록을 위조하면 통과 | `Edit src/app.py` | 0 | 0 |  |
| 76 | plan_gate | plan_lib.py가 없음(공용 모듈 누락) | `(정상 입력)` | 2 | 2 | gate.failure |
| 77 | plan_gate | 스크립트 경로 오타(python3가 파일을 못 엶) | `(정상 입력)` | 2 | 2 | python3: can't open file … (python3 자신의 종료 코드) |
| 78 | test_after_edit | 짝 테스트 통과 | `Edit src/app.py` | 0 | 0 |  |
| 79 | test_after_edit | 짝 테스트 실패 | `Edit src/bad.py` | 2 | 2 | test_after_edit: test_bad.py 실패 |
| 80 | test_after_edit | 짝 테스트 없음 | `Edit src/lonely.py` | 2 | 2 | test_after_edit: lonely.py에 짝지은 테스트(tests/test_lonely.py)가 없습니다. |
| 81 | test_after_edit | 코드가 아닌 파일 | `Edit README.md` | 0 | 0 |  |
| 82 | test_after_edit | 테스트 파일 자신 | `Edit tests/test_app.py` | 0 | 0 |  |
| 83 | test_after_edit | 훅 폴더의 .py | `Edit .claude/hooks/plan_gate.py` | 0 | 0 |  |
| 84 | test_after_edit | 깨진 입력: JSON 배열 | `[]` | 0 | 0 |  |
| 85 | test_after_edit | 깨진 입력: JSON 아님 | `{x` | 0 | 0 |  |
| 86 | test_after_edit | 깨진 입력: tool_input이 문자열 | `{"tool_input":"x"}` | 0 | 0 |  |
| 87 | test_after_edit | 깨진 입력: 빈 입력 | `(빈 입력)` | 0 | 0 |  |
| 88 | prompt_reminder | reminders.md 있음 → stdout에 내용 | `{"prompt":"hi"}` | 0 | 0 | stdout 5줄, 첫 줄 '<reminders>' |
| 89 | prompt_reminder | 깨진 입력(입력을 읽지 않는다) | `{broken` | 0 | 0 | stdout 5줄 |
| 90 | prompt_reminder | reminders.md 없음 → 출력 없음 | `{"prompt":"hi"}` | 0 | 0 | stdout 0바이트 |
| 91 | stop_check | 검사 실패(tests/test_bad.py) | `{"stop_hook_active":false}` | 2 | 2 | stop_check: 검사가 실패했습니다. 고친 뒤 끝내세요. |
| 92 | stop_check | 이미 이어서 일하는 중(stop_hook_active) | `{"stop_hook_active":true}` | 0 | 0 |  |
| 93 | stop_check | 검사 통과 | `{"stop_hook_active":false}` | 0 | 0 |  |
| 94 | stop_check | 깨진 입력: JSON 아님 | `{broken` | 0 | 0 |  |
| 95 | stop_check | 깨진 입력: JSON 배열 | `[]` | 0 | 0 |  |
| 96 | statusline | 정상 입력 | `{"model": {"display_name": "Opus"}, "context_window": {"used…` | 0 | 0 | 출력: Opus \| ctx 8% \| cache warm 91% miss x2(tools_changed) \| $0.01 |
| 97 | statusline | 필드가 null·없음 | `{"model":null,"context_window":{"used_percentage":null}}` | 0 | 0 | 출력: ? |
| 98 | statusline | 깨진 입력: JSON 배열 | `[]` | 0 | 0 | 출력: statusline: unexpected input |
| 99 | statusline | 깨진 입력: 빈 입력 | `(빈 입력)` | 0 | 0 | 출력: statusline: unreadable input |

합계 99건, 기대와 다른 것 0건.

- 75번은 통과가 기대값이다. 게이트만으로는 못 막는 경로를 확인한 것이다(아래 "한계").
- 77번의 2는 `python3`가 스크립트 파일을 못 열 때 스스로 내는 종료 코드다. `python3` 자체가 없거나 시간 초과면 훅이 종료 코드를 내지 못하므로 `onFailure: "block"`이 있어야 막힌다.

## 한계: 이 훅이 막지 못하는 것

| 막지 못하는 것 | 이유 | 보완 |
|---|---|---|
| 에이전트가 셸로 승인 기록을 직접 쓴다 (`echo … > design/approvals/x.json`, `python3 -c …`) | 게이트는 파일 도구(Edit·Write·NotebookEdit)만 본다. 위 표 75번이 이 경우다 | 권한 차단 규칙(`Edit(/design/approvals/**)`는 리다이렉션과 알려진 파일 명령까지 덮는다), 셸의 파일 쓰기 격리(샌드박스. 설정 이름은 쓰는 버전 문서로 확인 필요), 승인 기록을 커밋하고 그 폴더 변경을 사람이 리뷰(예: 코드 소유자 지정) |
| 에이전트가 `approve_plan.py`를 실행한다 | 스크립트는 터미널이 아니거나 `CLAUDECODE` 환경 변수가 있으면 거절하지만, 가짜 터미널을 만들고 변수를 지우면 통과한다(위 표의 시험이 바로 그렇게 실행했다). `CLAUDECODE`는 v2.1.322의 셸에서 값이 있는 것을 봤을 뿐 문서로는 확인 필요 | 권한 차단 규칙 `Bash(*approve_plan*)`. Bash 규칙은 흔한 형태만 막으므로(이름을 조립해 부르면 통과) CI와 사람 리뷰가 마지막 선이다 |
| 셸 명령으로 코드 파일을 쓴다 (`sed -i`, `cat >`, 스크립트) | 매처에 걸리지 않는다 | 끝내기 전·CI에서 `git diff --name-only <base_commit>`의 파일이 수정 대상 안인지 검사 |
| 계획 내용이 옳은지, 리뷰가 실제로 있었는지 | 형식만 본다. `## 리뷰 이력`의 `APPROVE` 줄은 에이전트도 쓸 수 있다 | 승인하는 사람이 화면의 수정 대상·위험 표시와 계획을 읽는다. 리뷰어 출력을 따로 보관한다 |
| 수정 대상 안에서의 나쁜 변경 | 경로만 본다. 내용은 보지 않는다 | 테스트, CI, PR 리뷰 |
| 파일 삭제·이름 바꾸기 | 파일 도구에는 삭제가 없다. 셸로 한다 | CI의 범위 검사, 테스트 삭제 탐지 |
| 마크다운과 `design/` 아래 파일의 수정 | 계획 없이 쓰도록 열어 뒀다. 지침 파일(`CLAUDE.md`, 스킬)도 마크다운이다 | 지침 파일을 `protected_paths.txt`에 넣거나 PR 리뷰에서 본다 |
| 하드 링크로 보호 경로를 가리키는 파일 | 심볼릭 링크는 풀지만 하드 링크는 구분하지 못한다 | CI |
| 머리말의 `risk`·`base_commit`을 승인 뒤에 바꾼다 | 머리말은 해시에 없다 | 승인 기록과 PR에서 본다 |

그 밖의 한계
- 한 번에 `approved` 계획은 하나다. 두 작업을 같은 체크아웃에서 동시에 승인해 둘 수 없다.
- 워크트리 세션에서는 `CLAUDE_PROJECT_DIR`가 원래 체크아웃을 가리킨다. 워크트리 안의 파일은 "프로젝트 밖"으로 판정돼 문서까지 전부 막힌다(막는 쪽으로 틀린다).
- 수정·삭제 대상이 `base_commit`에 실제로 있는지는 검사하지 않는다. 리뷰어가 직접 열어 본다.
- `test_after_edit.py`: 병렬 편집이면 훅도 동시에 돌아 테스트가 겹칠 수 있다. 무거워지면 묶음당 한 번 도는 이벤트(PostToolBatch)나 Stop으로 옮긴다. 성공한 호출 뒤에만 돈다.
- `stop_check.py`: `stop_hook_active`를 보고 물러나므로 두 번째로 끝낼 때는 검사하지 않는다. 그때의 통과는 고쳐졌다는 증거가 아니다. 8번 연속 막으면 하네스가 턴을 끝낸다.
- `prompt_reminder.sh`: 붙인 글은 대화 기록에 요청마다 쌓인다. 예약 작업이나 백그라운드 서브에이전트 보고에도 돈다. 변하지 않는 규칙은 지침 파일에 둔다.
- 실제 세션에서의 발동(차단 메시지가 모델에 전달되는지, `onFailure: "block"`이 시작 실패를 막는지)은 이 저장소에서 돌려 보지 않았다. 켠 뒤 "켜는 법" 5번으로 직접 확인한다.
- Windows에서는 실행해 보지 않았다(확인 필요).

## 훅 동작 요약 (v2.1.322 문서 기준)

- 차단은 exit 2(사유는 stderr)나 JSON 결정으로만 된다. PreToolUse의 JSON 결정은 `hookSpecificOutput.permissionDecision`(`allow`·`deny`·`ask`)에 둔다. 최상위에 두면 오류 없이 무시된다.
- **exit 1, 스크립트 오류, 시간 초과, 경로 오타는 `hook error` 알림만 남기고 통과한다.** `"onFailure": "block"`(v2.1.295 이상, `command`·`http` 훅)을 주면 이런 실패도 막는다. Stop 계열 이벤트와 `async` 훅에는 효과가 없다.
- 훅의 거부는 모든 권한 모드에서 통한다. 훅의 허용(`allow`)은 확인 창을 건너뛰게 할 뿐 권한 설정의 deny·ask 규칙을 넘지 못한다.
- exit 2의 효과는 이벤트마다 다르다. PreToolUse는 도구 호출을 막고, PostToolUse는 이미 실행된 뒤라 stderr를 모델에 보여 주기만 하고, Stop은 끝내기를 막는다.
- 훅은 서브에이전트의 도구 호출에도 돈다(입력에 `agent_id`·`agent_type`). 같은 이벤트의 훅은 병렬로 돌고, 하나가 막아도 나머지는 끝까지 돈다.
- 명령 훅은 내 사용자 권한으로, 샌드박스 밖에서 실행된다. 클론한 저장소의 훅도 내 PC에서 돈다. 비대화형 실행(`claude -p`)은 신뢰 확인 없이 저장소의 훅을 돌린다.
- 이벤트 이름, 입력 필드, 차단 방식은 버전마다 다를 수 있다. 켜기 전에 쓰는 버전의 훅 문서로 확인한다.
