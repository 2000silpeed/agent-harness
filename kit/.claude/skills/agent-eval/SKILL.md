---
name: agent-eval
description: 에이전트·스킬의 평가셋을 만들고 Activation/Execution/Outcome 세 축으로 채점해 design/07-eval.md 결과표를 채운다. P7 단계, 스킬이나 프롬프트를 고친 뒤 "나아졌나" 확인, 회귀 테스트, 모델 교체 비교에 사용.
---

<principles>
- 개선은 평가로 증명한다. 같은 모델·요청·예산 조건에서 **변수 하나만** 바꾼다.
- 품질, 비용(토큰·호출 수), 지연을 함께 기록한다.
- 결정적 규칙 검사(코드)와 의미 평가(루브릭 + 사람/Judge)를 함께 쓴다. 각 검사가 증명한 것만 보고한다.
- Runtime 자기 검증과 Offline 평가를 분리한다. 평가 코드와 정답은 에이전트가 고칠 수 없는 곳에 둔다.
- 완료는 에이전트의 "완료했다"가 아니라 실제 상태(테스트 결과, 파일, 로그)로 판정한다.
- 채점 순서는 Code → 의미 판정(Judge·디시전 모델) → 사람(불일치)이다. 정책·안전 실패를 평균으로 상쇄하지 않는다.
- Judge를 쓰면 사람 라벨로 false pass·false reject를 먼저 잰다. PASS·FAIL 표본이 모두 없으면 `insufficient_coverage`다.
- mock·scripted 결과는 "계약 검증"이지 개선율이 아니다.
- 모르는 값(비용 등)은 0이 아니라 null이다. 누락된 실행도 분모에 남긴다.
- 실패 행을 지우지 않고, 테스트를 skip하지 않고, 예산을 올려 실패를 감추지 않는다.
- 상세 규칙: `harness/reference/eval-rsi-rules.md` §1, §6-B·C.
</principles>

<procedure>
1. `start-phase.sh 07`. `eval/cases.jsonl`을 만든다. 한 줄에 `{"id","type","input","expected","must_do","must_not"}` 형식으로 쓴다.
2. 유형별로 최소 3건씩 만든다: implicit, explicit, negative, no_evidence, unauthorized, tool_failure. 사람이 확정한 골드 데이터가 있으면 우선 쓴다.
3. 실행 스크립트 `eval/run.py`(또는 `.sh`)를 만든다. 케이스마다 트레이스(호출한 도구·인자·토큰·지연)를 `eval/results/<버전>-<날짜>.jsonl`에 저장한다.
4. 채점:
   - Activation: 불려야 할 때 불렸나(Recall), 불리면 안 될 때 안 불렸나(Precision)
   - Execution: must_do를 했나, must_not을 안 했나, 인자가 유효한가
   - Outcome: 업무가 끝났나. 주장마다 근거가 실제로 그 주장을 지지하나(ID가 있다고 지지하는 건 아니다)
5. 결과표에 버전, 날짜, 건수, 세 축 점수, 지연, 토큰, 실패 종류를 적는다.
6. 실패마다 fact / hypothesis / alternative / evidence_ids를 쓴다. 근거 ID가 없는 가설로는 개선 실험을 시작하지 않는다.
7. 실패를 증상별로 분류하고 고칠 계층을 제안한다: 발견(description) → 선택 → 수행(본문) → 코드 → 공통 정책.
8. 평가셋(시나리오)은 실행 전에 정하고, 바꾸면 새 데이터 버전으로 보고 두 버전을 모두 다시 돌린다.
</procedure>

<when_to_rerun>
모델 변경, 스킬·프롬프트·도구 계약 변경, 실제 운영에서 실패 트레이스가 생겼을 때 다시 돌린다.
</when_to_rerun>
