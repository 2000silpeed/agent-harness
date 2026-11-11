# 보류 자료 (아직 강의 전)

수업 저장소에서 미리 조사했지만 아직 강의하지 않은 날의 자료다. 결과물(`claude-setup/`, `kit/`)에는 들어가 있지 않다. 해당 날 강의가 올라오면 강의 내용과 대조해 확인된 부분만 옮기고 여기서 지운다(`UPDATING.md` 4단계).

| 파일 | 해당 일차 | 내용 |
|---|---|---|
| `day5-8-repo-rules.md` | 5~6일차 (일부 4일차 Jev) | Day05 평가 파이프라인, Day05_new 자기개선 루프, Day06 하네스 6책임·근거 수준, Jev 게이트 → 규칙 R1~R32. **5일차 반영 후 남은 것:** §2 자기개선 루프 세부(Day05_new 06, 강의에서 다루지 않음), §3 하네스 6책임·근거 수준(6일차 강의에서 다루지 않음 — 저장소 `Day06/AGENTS.md` 분석 트랙에만 있음), §4.3 Jev fail-closed 게이트 세부, R5·R6·R15·R18~R27 |

## 옮긴 기록

| 일차 | 옮긴 것 | 위치 |
|---|---|---|
| 5일차 | `skills/plan-review/` (7강에서 "계획 → 리뷰 → 승인 후에만 코드 변경" 확인) | `kit/.claude/skills/plan-review/` |
| 5일차 | §1 평가 파이프라인 중 강의·교재로 확인된 원칙(시나리오 계약, 필수 관문, 반례 검증, Judge vs 사람 라벨, 조건 잠금·한 조건 변경, pass@k, holdout 분리, 승인 기준 사전 고정) | `kit/harness/METHOD.md` S1, `golden-dataset`·`agent-eval` 스킬 |
| 6일차 | 옮긴 것 없음. 6일차 강의는 Claude Code 하네스 구성(메모리·스킬·훅)을 다뤘고, 보류 자료의 여섯 책임·근거 수준·자기개선 루프는 강의에서 다루지 않았다 | — |
| 7일차 | 옮긴 것 없음. 7일차는 모델 서빙(vLLM)을 다뤘고 보류 자료와 겹치는 주제가 없다 | — |
| 미니 PJT 공지 | `skills/criteria-check/` (평가 기준 슬라이드를 받아 `harness/CRITERIA.md` 기준으로 고쳐 씀) | `kit/.claude/skills/criteria-check/` |
| 미니 PJT 공지 | `day8-dcode-map.md` (과제를 dcode로 하기로 해서 단계 중심으로 다시 씀) | `kit/harness/bases/dcode.md` |
| 조사 반영 (2026-11-11) | `skills/self-improve-loop/` (강의에서 세부를 다루지 않았으나 인수 기준 3-3·3-4에 필요해 공개 자료 조사로 고쳐 씀: 읽기용·판정용 과제 분리, 사전 고정, 사람 승인, 되돌리기) | `kit/.claude/skills/self-improve-loop/` |
| 조사 반영 (2026-11-11) | `day5-8-repo-rules.md` §4.3 게이트의 실패 시 차단 원칙(공식 문서로 확인된 범위만) | `kit/harness/reference/security.md`, `claude-setup/hooks/` |
| 8일차 | `day5-8-repo-rules.md` §4.3 Jev 게이트의 실패 시 차단 원칙(강의와 `Day08_new/guard_lab/gate.py`·`contracts.py`로 확인: 판정 실패는 REVIEW, 두 문턱값, 코드가 결정) | `kit/harness/reference/security.md` 8절 |
| 8일차 | 남은 것: §2 자기개선 루프 세부, §3 하네스 6책임·근거 수준, R5·R6·R15·R18~R27. 8일차까지 강의에서 다루지 않았다. 자기개선 루프는 공개 자료 조사로 따로 반영했다(위 조사 반영 행) | — |
