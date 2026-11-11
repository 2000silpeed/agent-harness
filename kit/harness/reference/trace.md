# 기록: 요청별 이벤트 형식과 조회

> S2(관측)의 참고 문서다. S5(`gate_block`, `plan_status`)와 S6(`memory`, `improve`)을 만들 때마다 그 이벤트가 실제로 남는지 다시 본다. 산출물은 `design/02-baseline.md`의 "관측" 절에 채운다.
> 필드 이름과 값은 제안이다. 바꿔도 되지만 한 번 정하면 형식 검사 코드로 고정한다.

## 1. 구조

- **세 층:** 대화(`session_id`) ⊃ 요청(`request_id`) ⊃ 이벤트. 사용자 요청 한 건이 기록 한 묶음이다.
- **요청 ID 하나로 이어지는 것:** 계획 파일, 승인 기록, 이벤트, 요약 지표, 평가 결과.
- **서브에이전트**의 이벤트는 부모와 같은 `request_id`에 자기 `agent_id`를 붙인다.
- **쓰는 방식:** 한 줄에 이벤트 하나(JSONL), 뒤에 붙이기만 한다. 일이 끝날 때마다 바로 쓰고 내보낸다. 끝에 한꺼번에 쓰지 않는다.
- **두는 곳 (제안값):** 요청별 `runs/<request_id>/events.jsonl`, 요청당 한 줄 요약 `runs/summary.jsonl`. 에이전트가 고칠 수 없는 위치에 둔다(`security.md` 5절).

## 2. 공통 필드

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `ts` | 문자열 | O | 이벤트가 끝난 시각. UTC, 밀리초 |
| `seq` | 정수 | O | 요청 안에서 1부터 1씩 증가. 정렬 키는 (`request_id`, `seq`) |
| `session_id`, `request_id` | 문자열 | O | 대화, 요청 한 건 |
| `span_id`, `parent_span_id` | 문자열 |  | 중첩(요청 ⊃ 단계 ⊃ 호출)을 남길 때 |
| `agent` | 문자열 | O | 역할 이름 (예: `main`, `plan-reviewer`) |
| `agent_id`, `parent_agent_id` | 문자열 |  | 서브에이전트 구분 |
| `phase` | 열거 | O | `plan` \| `review` \| `code` \| `test` \| `result` (3절) |
| `type` | 열거 | O | 이벤트 종류 (4절) |
| `name` | 문자열 | O | 모델 이름, 도구 이름, 규칙 ID 등 |
| `status` | 열거 | O | `ok` \| `error` \| `blocked` \| `timeout` \| `cancelled` |
| `error_type` | 문자열 |  | 정해진 목록에서 고른다 (예: `exit_nonzero`, `rate_limit`, `invalid_args`, `not_found`, `_OTHER`). 자유 문장 금지 |
| `error_message` | 문자열 |  | 가린 뒤 잘라서 (제안값: 500자) |
| `duration_ms` | 정수 |  | 모르면 null |
| `attempt` | 정수 |  | 같은 작업의 몇 번째 시도인가. 1부터 |
| `content_ref`, `redacted` | 문자열, 불리언 |  | 원문을 따로 저장했을 때 그 위치, 가리기가 적용됐는가 (7절) |

필수가 아닌 필드는 빼도 되고, 뺀 것은 null로 읽는다. `status=blocked`는 게이트가 막은 것이고 오류가 아니다.

## 3. 단계 표시

| `phase` | 담는 일 | 요청 흐름과의 대응 (제안값) |
|---|---|---|
| `plan` | 요구 확인, 메모리 조회, 계획 작성·수정 | 요구 확인, 계획 |
| `review` | 독립 리뷰, 사람 승인 | 리뷰·승인 |
| `code` | 코드 변경 | 구현 |
| `test` | 테스트·린트 실행 | 검증 |
| `result` | 완료 확인, 보고, 경험 저장, 개선 | 보고·학습 |

- **흐름을 조정하는 코드가 현재 단계를 상태로 들고 이벤트마다 붙인다.** 도구 이름으로 추정하지 않는다. 테스트 파일 편집, 계획 파일 쓰기, 리뷰어의 파일 읽기에서 틀린다.
- 요청과 따로 도는 개선 작업은 자기 `request_id`를 갖는다. 평가 실행은 `test`, 채택 결정은 `result`로 붙인다 (제안값).

## 4. 이벤트 종류

| `type` | 언제 | 추가 필드 |
|---|---|---|
| `request_start` | 요청을 받은 직후 | `request_digest`, `base_commit`, `harness_version`, `config_digest`, `budget` |
| `llm_call` | 모델 호출이 끝날 때마다 (실패 포함) | `provider`, `purpose`(plan·review·code·judge 등), `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, `finish_reason`, `ttft_ms` |
| `tool_call` | 도구 실행이 끝날 때마다 (실패 포함) | `tool_call_id`, `tool_type`(builtin·external·skill), `args_digest`, `args_bytes`, `result_bytes`, `exit_code`, `paths`(건드린 파일) |
| `memory` | 메모리 조회·주입·저장·저장 거부·폐기 | `op`(search·inject·write·reject·delete), `query_digest`, `hit_ids`, `injected_ids`, `count`, `source_session` |
| `improve` | 개선안 제안·검증·채택·기각 | `stage`(propose·validate·adopt·reject), `proposal_id`, `target`(prompt·skill·memory), `baseline_score`, `candidate_score`, `regression` |
| `gate_block` | 게이트가 막았거나 검사기가 실패했을 때 | `gate`(format·approval·pre_edit·completion·permission·sandbox), `decision`(deny·ask), `reason`, `plan_id`, `plan_version`, `target`, `fail_closed` |
| `plan_status` | 계획 상태가 바뀔 때 | `plan_id`, `plan_version`, `from`, `to`, `actor`(agent·reviewer·human·gate), `verdict`, `finding_ids`, `plan_sha256` |
| `request_end` | 요청이 끝날 때 | `final_status`(done·hold·handoff·failed = 완료·보류·사람에게 넘김·실패), `summary`(5절) |

- `gate_block`의 `name`은 규칙 ID다. 차단과 검사기 실패(`fail_closed=true`)는 전부 남긴다. 허용 결정도 일부 남기면(`decision: allow`) 게이트가 살아 있는지 볼 수 있다.
- `plan_status`의 상태 값과 `actor` 규칙은 `plan-gate.md`를 따른다.
- 긴 작업(모델 호출, 테스트 실행)은 시작 이벤트도 남기거나 시작 시각을 끝 이벤트에 넣는다. 그래야 도중에 죽었을 때 무엇을 하던 중인지 남는다.

### 예시: 짧은 요청 한 건

줄을 줄이려고 모델 호출 대부분과 null 필드를 뺐다. 범위 밖 수정이 한 번 막히고(7번), 테스트가 한 번 실패했다가(9번) 통과한(11번) 요청이다.

```jsonl
{"ts":"2026-11-11T05:10:00.120Z","seq":1,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"plan","type":"request_start","name":"request","status":"ok","request_digest":"h:1b2c","base_commit":"3f2a9c1","harness_version":"0.3.0","config_digest":"h:aa01","budget":{"max_turns":40,"max_seconds":900}}
{"ts":"2026-11-11T05:10:00.480Z","seq":2,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"plan","type":"memory","name":"experience_store","status":"ok","op":"search","count":2,"hit_ids":["exp-012","exp-031"],"injected_ids":["exp-012"],"duration_ms":40}
{"ts":"2026-11-11T05:10:09.700Z","seq":3,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"plan","type":"llm_call","name":"model-a","status":"ok","purpose":"plan","input_tokens":5210,"output_tokens":830,"finish_reason":"stop","duration_ms":9100,"attempt":1}
{"ts":"2026-11-11T05:10:09.900Z","seq":4,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"plan","type":"plan_status","name":"plan","status":"ok","plan_id":"20261111-fix-login-timeout","plan_version":1,"from":"draft","to":"in_review","actor":"gate"}
{"ts":"2026-11-11T05:10:21.300Z","seq":5,"session_id":"s_7f","request_id":"req_0042","agent":"plan-reviewer","agent_id":"a_02","parent_agent_id":"a_01","phase":"review","type":"llm_call","name":"model-b","status":"ok","purpose":"review","input_tokens":3110,"output_tokens":420,"finish_reason":"stop","duration_ms":11000,"attempt":1}
{"ts":"2026-11-11T05:12:03.000Z","seq":6,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"review","type":"plan_status","name":"plan","status":"ok","plan_id":"20261111-fix-login-timeout","plan_version":1,"from":"in_review","to":"approved","actor":"human","verdict":"APPROVE","plan_sha256":"9d4e"}
{"ts":"2026-11-11T05:12:40.100Z","seq":7,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"code","type":"gate_block","name":"scope.outside_plan","status":"blocked","gate":"pre_edit","decision":"deny","reason":"수정 대상에 없는 파일","plan_id":"20261111-fix-login-timeout","plan_version":1,"target":"src/config.py","fail_closed":false}
{"ts":"2026-11-11T05:13:02.500Z","seq":8,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"code","type":"tool_call","name":"edit_file","status":"ok","tool_type":"builtin","args_digest":"h:9c1e","args_bytes":412,"paths":["src/auth/session.py"],"duration_ms":35,"attempt":1}
{"ts":"2026-11-11T05:13:25.900Z","seq":9,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"test","type":"tool_call","name":"run_tests","status":"error","error_type":"exit_nonzero","error_message":"2 failed, 14 passed","tool_type":"builtin","args_digest":"h:77aa","exit_code":1,"duration_ms":18200,"attempt":1}
{"ts":"2026-11-11T05:14:10.200Z","seq":10,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"code","type":"tool_call","name":"edit_file","status":"ok","tool_type":"builtin","args_digest":"h:d20f","args_bytes":230,"paths":["src/auth/session.py"],"duration_ms":31,"attempt":1}
{"ts":"2026-11-11T05:14:31.400Z","seq":11,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"test","type":"tool_call","name":"run_tests","status":"ok","tool_type":"builtin","args_digest":"h:77aa","exit_code":0,"duration_ms":17900,"attempt":2}
{"ts":"2026-11-11T05:16:52.720Z","seq":12,"session_id":"s_7f","request_id":"req_0042","agent":"main","phase":"result","type":"request_end","name":"request","status":"ok","final_status":"done","summary":{"duration_s":412.6,"time_to_first_response_s":null,"llm_calls":2,"tool_calls":4,"retries":{"llm":0,"tool":0,"review_rounds":0,"test_runs":1},"gate_blocks":1,"gate_failures":0,"tokens":{"input":8320,"output":1250,"cache_read":null,"cache_write":null},"cost":null,"human_approvals":1,"phases_seen":["plan","review","code","test","code","test","result"],"first_error":{"seq":9,"phase":"test","type":"tool_call","name":"run_tests","error_type":"exit_nonzero"},"first_unrecovered_error":null,"log_write_errors":0}}
```

## 5. 요약 지표

`request_end`의 `summary`에 넣고 요약 파일에도 한 줄 쓴다. **모르는 값은 null이다. 0은 세어 보니 0일 때만 쓴다.** 필드는 빼지 않고 null로 적는다.

| 지표 | 정의 |
|---|---|
| `duration_s` | `request_end.ts` − `request_start.ts` |
| `time_to_first_response_s` | 사용자에게 보이는 첫 출력까지 |
| `llm_calls`, `tool_calls` | 해당 이벤트 수. 재시도 포함 |
| `retries.llm` / `.tool` / `.review_rounds` / `.test_runs` | 종류별로 따로 센다. 한 숫자로 합치면 무엇이 늘었는지 모른다. 모델 호출 중 `attempt > 1`인 수 / 같은 도구·같은 인자를 다시 부른 수(테스트 실행 제외) / 첫 리뷰 뒤에 더 돈 리뷰 수 / 첫 실행 뒤에 다시 돌린 테스트 실행 수 |
| `gate_blocks`, `gate_failures` | `gate_block` 수, 그중 `fail_closed=true` 수 |
| `tokens.input` / `.output` / `.cache_read` / `.cache_write` | 합계. 입력 토큰에 캐시분을 넣을지 정해 한 가지로 맞춘다 |
| `cost` | 단가를 모르면 null |
| `human_approvals` | 사람이 승인한 횟수 |
| `phases_seen` | 지나간 단계. 순서대로, 이어진 중복은 하나로. 되돌아가면 다시 적는다 (code, test, code, test) |
| `first_error`, `first_unrecovered_error` | `{seq, phase, type, name, error_type}` 또는 null (6절) |
| `log_write_errors` | 기록 쓰기에 실패한 수. 삼키지 않고 센다 |

## 6. "첫 실패"의 정의와 찾는 절차

| 이름 | 정의 | 쓰임 |
|---|---|---|
| 첫 오류 | `seq` 순으로 `status`가 `error`나 `timeout`인 첫 이벤트 | 무슨 일이 처음 어긋났나 |
| 복구 안 된 첫 오류 | 오류 중, 뒤에 같은 작업의 성공이 없는 첫 이벤트 | **원인 후보** |
| 첫 게이트 차단 | `type=gate_block`인 첫 이벤트 | 정상 동작이다. 오류로 세지 않고 따로 보여준다 |

"같은 작업"은 도구면 같은 `name` + `args_digest`, 모델 호출이면 같은 `purpose`다. 절차를 코드로 고정한다.

1. 요청의 이벤트를 `seq` 순으로 읽는다. 빈 번호나 중복이 있으면 "기록 손상"으로 알린다.
2. `request_end`가 없으면 "미완: 마지막 이벤트 seq=N"을 먼저 보여준다(8절).
3. 첫 오류를 찾는다.
4. 오류마다 뒤에 같은 작업의 `ok`가 있는지 본다. 없는 첫 오류가 복구 안 된 첫 오류다.
5. 그 이벤트의 직전 N개(제안값: 5)와, 직전 모델 호출, 직전 `code` 단계 변경("의심 변경")을 함께 보여준다. `gate_block` 목록은 따로 보여준다.

조회 명령은 최소 세 개다 (이름은 제안값): `trace show <request_id>`(단계별 시간순 목록), `trace first-failure <request_id>`(위 절차의 결과), `trace summary [--since …]`(요청별 요약 표).

## 7. 가리기와 원문

- **기본은 메타데이터만 남긴다:** 이름, 크기, 해시, 소요 시간, 상태. 프롬프트, 도구 인자, 도구 출력의 원문은 남기지 않는다.
- **가리기는 쓰기 전에, 애플리케이션 안에서 한다.** 수집 쪽에서 가리면 이미 나간 뒤다.
- **가릴 것:** 환경변수 값, 알려진 키·토큰 형식, 자격증명·설정 파일 내용, 인증 헤더, 이메일·전화번호 같은 개인정보, 사내 식별자(팀이 정한다).
- **적용 대상:** `error_message`, `reason`, `paths`, 원문 저장소로 가는 내용 전부. 가렸으면 `redacted=true`.
- **해시는 가리기가 아니다.** 짧거나 뻔한 값은 해시로 되짚을 수 있다. 시크릿이 들 수 있는 인자는 비밀 키를 섞은 해시를 쓰거나 해시도 남기지 않는다.
- **원문이 필요하면** 이벤트와 다른 저장소에 두고 `content_ref`로 가리킨다. 위치, 접근 권한, 보존 기간(제안값: 30일)을 정해 적는다. 오래 둘 것은 평가셋으로 승격한다. 외부 관측 도구로 보낼 때는 그곳이 이 내용을 보관해도 되는 곳인지 먼저 확인한다.

## 8. 미완 요청과 표본

- 프로세스가 죽으면 `request_end`가 없다. **끝 이벤트가 없는 요청은 "미완"으로 판정한다.** 성공으로도 실패로도 세지 않고 따로 센다. 마지막 줄이 잘려 있으면 그 줄만 버리고 버린 사실을 알린다.
- 요청이 예외로 끝나도 `request_end`(`final_status=failed`)를 쓰도록 종료 처리에 넣는다. 성공 경로에서만 쓰면 실패가 기록 없이 사라진다.
- 표본: 평가셋과 시범 운영 규모에서는 **전부 남긴다.** 줄여야 하면 요청이 끝난 뒤에 정하고, 오류·게이트 차단·정책 위반·미완 요청은 항상 남긴다. 시작할 때 미리 뽑으면 실패한 그 요청이 빠진다.

## 9. OpenTelemetry GenAI 규약과의 대응

조사일(2026-11-11) 기준 이 규약은 **전체가 확정 전(Development) 상태**이고 문서 저장소가 옮겨졌다. 이름이 바뀔 수 있고, 아래 이름의 일부는 요약을 거쳐 확인했다(**확인 필요**). 그래서 내부 기록을 주 증거로 쓰고, 외부 관측 도구로 보낼 때만 변환기 하나로 바꾼다. 규약 이름은 그 변환기에만 두고 코드 곳곳에 박지 않는다.

| 내부 | 규약 | 비고 |
|---|---|---|
| 요청 (`request_start` ~ `request_end`) | `invoke_workflow` 스팬 (모델이 흐름을 정하면 `invoke_agent`). trace ID | 흐름을 코드가 정하면 workflow |
| `session_id` / `agent` | `gen_ai.conversation.id` / `gen_ai.agent.name` |  |
| `llm_call` | 추론 스팬. `gen_ai.operation.name`(예: `chat`), `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`·`output_tokens`, `gen_ai.response.finish_reasons` | 캐시 토큰 속성도 있다. 재시도 번호 속성은 없다 |
| `tool_call` | `execute_tool` 스팬. `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.type` | 인자·결과 원문은 규약에서도 선택 사항 |
| `memory` | 작업 이름 `search_memory`, `create_memory`, `update_memory` 등. `gen_ai.memory.record.count` |  |
| `phase=plan` | `plan` 스팬 | 나머지 단계는 대응 없음 |
| `error_type` | `error.type` | 모르면 `_OTHER` |
| `duration_s`, `llm_calls`, `tool_calls` | `gen_ai.invoke_agent.duration`, `.inference_calls`, `.tool_calls` |  |
| `tokens.*` | `gen_ai.client.inference.usage.*` |  |

**규약에 없어서 직접 정의한 것:** `phase`, `seq`, `attempt`와 종류별 재시도, `gate_block`, `plan_status`, `improve`, `human_approvals`, `first_error`, `first_unrecovered_error`, `redacted`, `log_write_errors`. 내보낼 때는 자체 이름 공간(예: `harness.gate.decision`)을 쓰고 `gen_ai.*` 아래에 새 이름을 만들지 않는다. 규약도 내용 원문은 기본으로 남기지 않게 하므로 7절과 방향이 같다.

## 10. 검증 시험

| 시험 | 방법 | 기대 |
|---|---|---|
| 다섯 단계 | 정상 요청 1건 | `phases_seen`에 plan, review, code, test, result가 순서대로 |
| 도구 오류 | 일부러 실패하는 도구 호출 | `status=error`, `error_type` 있음. 조회 도구가 그 줄을 가리킴 |
| 복구된 오류 | 한 번 실패한 뒤 성공하는 호출 | `first_error` 있음, `first_unrecovered_error`는 null, 재시도 1 |
| 모델 호출 오류 | 모델 연결을 잠깐 끊음 | `llm_call` 오류, `attempt` 증가, `retries.llm` 반영 |
| 게이트 차단 | 승인 없이 수정 시도 (`security.md` RT-01) | `gate_block`이 남고 `first_error`에 섞이지 않음 |
| 미완 요청 | 실행 중 프로세스 강제 종료 | 그때까지의 이벤트가 있고 "미완"으로 표시 |
| 가리기 | 가짜 시크릿을 요청문·도구 출력에 넣음 | 기록 전체 검색에서 원문 0건 |
| 형식·순서 | 모든 이벤트를 형식 검사에 통과시킴 | 필수 필드 누락 0건, 열거값 밖 0건, `seq`에 빈 번호·중복 없음 |
| 서브에이전트 | 리뷰어 호출이 있는 요청 | 같은 `request_id`, 다른 `agent_id` |
| 지표 대조 | `llm_calls`·`tool_calls`를 이벤트 수로 직접 셈 | 일치 |
| 모르는 값 | 토큰을 알려주지 않는 모델로 실행 | 토큰이 0이 아니라 null |
| 사람이 찾기 | 팀원이 기록만 보고 첫 실패와 원인을 말함 | 조회 도구 출력과 일치. 걸린 시간 기록 |

## 참고 자료

조사일 2026-11-11. 대부분 요약을 거쳐 읽었다. 이름을 코드에 쓰기 전에 원문에서 다시 확인한다.

- OpenTelemetry GenAI 시맨틱 컨벤션 저장소: https://github.com/open-telemetry/semantic-conventions-genai (Development 상태)
- OpenTelemetry, Sampling: https://opentelemetry.io/docs/concepts/sampling/
- Langfuse, 데이터 모델: https://langfuse.com/docs/observability/data-model / 마스킹: https://langfuse.com/docs/observability/features/masking
- LangSmith, 관측 개념: https://docs.langchain.com/langsmith/observability-concepts
- Claude Code 문서, 모니터링: https://code.claude.com/docs/en/monitoring-usage (한 기반의 이벤트 구성 예)
