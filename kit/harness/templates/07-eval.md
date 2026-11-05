# P7. 평가

## 평가셋
| 유형 | 건수 | 예시 |
|---|---|---|
| Implicit (암시적 요청) |  |  |
| Explicit (명시적 요청) |  |  |
| Negative (트리거되면 안 됨) |  |  |
| 근거 없음 |  |  |
| 권한 없음 |  |  |
| 도구 실패 |  |  |

- 골드셋 출처(사람 확정 여부):
- 위치: `eval/`

## 실패 분석 (근거 없는 가설로 실험하지 않는다)
| artifact_id | evidence_ids (run·event) | fact (관찰) | hypothesis (원인 가설) | alternative (대안 가설) | change (바꿀 한 조건) | success_criteria | owner |
|---|---|---|---|---|---|---|---|

- 근거 수준 라벨: 실행 경로에서 확인 / 코드 정의만 / 문서만 / 추정

## 채점
| 축 | 지표 | 검사 방식(코드/루브릭/Judge) |
|---|---|---|
| Activation | Precision / Recall |  |
| Execution | 필수 행동, 유효 인자 |  |
| Outcome | 업무 완료, 근거 품질 |  |

- 순서: Code(lint·test·형식) → 의미 판정(Judge·디시전 모델) → 사람(불일치)
- 정책·안전 실패는 평균으로 상쇄하지 않는다
- Judge를 쓰면 사람 라벨로 false pass / false reject를 먼저 잰다
- mock·scripted 결과는 "계약 검증"으로만 표기한다

## 결과
| 버전 | 날짜 | 건수 | Activation | Execution | Outcome | 지연 | 토큰 | 실패 종류 |
|---|---|---|---|---|---|---|---|---|
| baseline |  |  |  |  |  |  |  |  |

## 게이트 (모두 체크해야 다음 단계)
- [ ] 평가셋에 6가지 유형이 모두 있다
- [ ] 평가가 명령 한 줄로 재실행된다
- [ ] 기준선 결과표가 채워졌다
