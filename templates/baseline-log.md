# 기준선 / 구조 비교 로그

JSONL 한 줄에 실행 하나를 기록합니다. 저장 위치 예: `eval/runs.jsonl`

```json
{"case_id": "c-012", "case_type": "단순|복합|정보부족|승인필요", "structure": "single|single+skills|supervisor|handoff|hybrid", "model": "…", "task_success": true, "latency_ms": 1420, "model_calls": 3, "tool_calls": 4, "input_tokens": 2100, "output_tokens": 180, "cache_read_tokens": 1800, "policy_violation": false, "failure_kind": null}
```

- `failure_kind`: `info_missing` | `exec_error` | `policy` | `system` | null
- 비교할 때 고정할 것: 데이터, 권한, 모델, 예산, 반복 횟수
- 실패 사례는 최소 1개를 원문과 함께 남깁니다.
