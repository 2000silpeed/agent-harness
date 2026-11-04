# 13. 평가: 감으로 때려 맞추는 시대는 지났다

## 기준선 [강의]
- 먼저 **Single Agent 기준선**을 만듭니다. 기준선이 없으면 개선 여부도 알 수 없습니다.
- 기록할 지표: `task_success`, `total_latency`, `model / tool calls`, `input / output tokens`
- 정보 부족과 실행 오류를 구분하고, "실행 기록 + 실패 사례 1개"를 남깁니다.
- 감으로 평가하면 담당자의 말이 계속 바뀝니다. 실행 기록을 남깁니다.
- 로그 형식은 [`templates/baseline-log.md`](../templates/baseline-log.md)를 따릅니다.

## 구조 비교 실험 [강의]
- 사례 유형: 단순 / 복합 / 정보 부족 / 승인 필요
- 비교 구조: Single / Single+Skills / Supervisor / Handoff / Hybrid
- **고정할 것**: 데이터, 권한, 모델, 예산, 반복 횟수
- 기록할 것: 성공률, 지연, 토큰, 정책 위반

## 골드 데이터셋 루프 [강의, 3일차 3강]
1. 처음에는 사람이 확정한 결과를 정답지로 씁니다.
2. AI 판단을 정답지로 평가합니다.
3. 틀린 지점을 **구체적으로** 적습니다. 예: "떡볶이까지는 맞고 가맹점명이 틀렸다."
4. 스킬이나 프롬프트를 보정하고 다시 돌립니다. 맞을 때까지 반복합니다.

스킬 `gold-dataset-loop`가 이 과정을 안내합니다.

## 구조 회고 [강의]
프로젝트가 끝나면 "내가 왜 이 구조를 선택했을까?", "굳이 서브에이전트를 썼어야 했나?"를 반드시 돌아봅니다. 회고 양식은 [`templates/structure-retrospective.md`](../templates/structure-retrospective.md)입니다.
