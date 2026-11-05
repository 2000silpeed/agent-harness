# P6. 하네스·관측

## 승인 게이트
- 구현 위치 (PreToolUse 훅 / wrap_tool_call 미들웨어):
- 차단 대상 도구:
- 승인 판정 기준 (예: 계획 파일 `status: approved` + 변경 대상이 계획 범위 안):
- 차단 시 모델에 돌려주는 메시지:
- 판정기 오류 시: 차단 (fail-closed)
- 서브에이전트 경로에서도 걸리는지 검증 방법:

## 권한·예산·종료
| 대상 | 읽기 | 쓰기 | 승인 필요 | 막는 위치 |
|---|---|---|---|---|

- 최대 턴 / 시간 / 재시도:
- 종료 상태: 완료 / 보류 / 사람 전환 / 실패

## 이벤트 로그
- 경로: `logs/<run_id>.jsonl` (append-only, 같은 이름이면 거부)
- 공통 필드: run_id, thread_id, turn_index, phase, event, call_id, parent_id, ts, duration_ms, status, error, version
- phase: plan / review / code / test / result / memory / improve
- event: llm_call, tool_call, memory_retrieve, memory_write, improve_proposal, improve_eval, improve_adopt, gate_block
- 비밀 마스킹 규칙:

## 지표
`logs/<run_id>.summary.json`
| 지표 | 원천 | 모를 때 |
|---|---|---|
| 총 소요 |  | null |
| LLM 호출 수 |  | null |
| 도구 호출 수 |  | null |
| 재시도 수 |  | null |
| 토큰 / 비용 |  | null |

## 조회
- 명령: `trace_query --run <id> [--errors] [--phase test]`
- 출력: 첫 실패 이벤트 + 직전 맥락 + 원인 후보

## 게이트 (모두 체크해야 다음 단계)
- [ ] 승인 없는 쓰기와 범위 밖 변경이 실제로 차단된다 (차단 로그로 확인)
- [ ] 한 요청의 전체 흐름이 로그에 시간순으로 남는다
- [ ] summary.json이 생성되고 모르는 값은 null이다
- [ ] 조회 도구가 실패 run의 첫 실패 지점을 찾는다
- [ ] 로그에 키·비밀이 없다
