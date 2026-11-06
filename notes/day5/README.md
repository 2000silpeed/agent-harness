# 5일차 종합 — 에이전트 평가: Golden Set · Trace · Judge, 그리고 판단 모델을 LLM 앞으로

| 파일 | 내용 |
|---|---|
| [00-deck.md](00-deck.md) | 교재: AI Agent Evaluation — Golden Dataset · Trace · Eval · Trajectory (계정 잠금 해제 Agent 예제) |
| [01-lecture1.md](01-lecture1.md) | 1강: 시험지·정답지·과정 — 골든 데이터셋, 트레이스, 궤적 평가, 정답지 만들기의 현실 |
| [02-lecture2.md](02-lecture2.md) | 2강: Claude Code 사용 기록을 Langfuse로 남기기 (측정해야 개선할 수 있다) |
| [03-lecture3.md](03-lecture3.md) | 3강: Dataset·Evaluator 만들기와 평가 기준(rubric) 설계, 샘플링 |
| [04-lecture4.md](04-lecture4.md) | 4강: 무료 모델 엔드포인트, Jev 딥 에이전트 실습(파일 업로드·인용 과제) |
| [05-lecture5.md](05-lecture5.md) | 5강: Long Context 줄이기, 판단 모델(Jev)을 LLM 앞단에 두기 |
| [06-lecture6.md](06-lecture6.md) | 6강: 에이전트 개선 실습 안내 (`task.md`) |
| [07-lecture7.md](07-lecture7.md) | 7강: 코딩 에이전트 프로젝트 안내, 문제점 기준 평가 데이터셋, 코드 모드 |
| [08-lecture8.md](08-lecture8.md) | 8강(자습): 한 주 복습, 다음 주 예고 |

## 실습 코드 위치

수업 저장소 `github.com/HyunjunJeon/sds_ax_advanced_2026` 기준이다(2026-11-06 `72f4c18f`).

| 강의 | 저장소 위치 | 비고 |
|---|---|---|
| 교재·1강 이론 | `Day05/Day5_이론자료.pdf`, `Day05_new/use_cc/concepts/m1.md`·`m2.md` | 1강은 이론만. 실습은 `Day05_new`에서 시작한다고 안내 |
| 2강 Langfuse 연동 | `Day05_new/use_cc/missions/m0.md`, `Day05_new/.env.example` | Claude Code 플러그인 연동 자체는 저장소에 없음 |
| 3강 Dataset·Evaluator | `Day05_new/02-Offline-Golden-Dataset.ipynb`, `03a-Online-Eval-Trace-Selection.ipynb`, `use_cc/concepts/m2.md`·`m3a.md`, `eval_lab/decisions.py`(Jev 질문 유형) | 강사는 미션 카드 대신 화면에서 직접 시연 |
| 4~6강 Jev 딥 에이전트 | `used_jev_deepagents/`, `Day05_new/task.md`, 판서 `Day05_new/Day05_01.png` | 노트북 없음 |
| 스크립트판 평가 파이프라인 | `Day05/00~09_*.py`, `business_lab/` | 덱 내용을 코드로 구현한 트랙. 강의에서 직접 열지는 않음 |
| 강의 밖 (노트북만) | `Day05_new/04-Agent-Monitoring`, `05-Continuous-Operation`, `06-Lab-Self-Improving-Agent` | 강의에서 다루지 않음. 하네스에는 반영하지 않았다 |

## 하루 요약

- **평가 = 시험지(Golden Set) + 채점(Evaluator) + 풀이 과정(Trace/Trajectory).** 최종 답이 같아도 과정이 다르면 같은 성공이 아니다. 평가 축은 Outcome(목표 상태) / Trajectory(대상·권한·순서) / Final Response(전달 정확성) 세 가지다.
- **정답지는 담당자 인터뷰에서 시작한다.** LLM에만 맡기면 50~60점짜리 일반 문제가 된다. LLM 초안 → 담당자 피드백을 반복하고, 문서에 없는 예외의 정답은 담당자가 채운다. 정답지는 Q&A가 아니라 **시나리오**(거칠 단계, 금지 행동, 순서 규칙)로 쓰고, 운영 기록 중 반복·재현·정답 정의가 가능한 것을 골든으로 승격한다. 개발용과 최종 확인용(holdout)을 나눈다.
- **측정해야 개선할 수 있다.** 자기 Claude Code 사용 기록부터 관측 도구(Langfuse)에 쌓는다. 셀프호스팅으로 데이터 제어권을 가질 수 있다. 턴 단위로 읽으면 429 뒤 재시도 같은 낭비가 보인다.
- **Judge에게 "0~1점 매겨라"만 시키면 0.7로 쏠린다.** 등급마다 관찰 가능한 기준을 촘촘히 주는 것이 개발자 몫이다. LLM Judge는 일관성이 떨어지므로 여러 번 돌려 흔들림을 보고, 사람 라벨과 비교해 false pass를 잰다. 분류·예/아니오는 판단 모델(Jev)이 싸고 안정적이다. **모든 요청을 평가하면 파산한다.** 기록할 때부터 "체크 필요" 표시를 남기고 샘플링한다.
- **정책·부작용 위반은 평균으로 상쇄하지 않는 필수 관문이다.** 판정 상태는 PASS / FAIL / INSUFFICIENT_EVIDENCE / EVALUATOR_ERROR / INFRA_ERROR로 나누고, 누락을 분모에서 지우지 않는다. 비교는 조건을 잠그고 한 번에 하나만 바꾸며, pass@k·pass^k·slice별 회귀·통과 1건당 비용을 본다. 승인 기준은 결과를 보기 전에 고정한다.
- **컨텍스트는 유한한 자원이다.** 원본은 파일에 두고 컨텍스트에는 최소만 넣는다. LLM에게 압축을 시키는 게 가장 비싸다.
- **판단 모델은 LLM 앞에서 가로챈다.** LLM이 툴 콜로 판단 모델을 부르면 모순이고 느리다. 의도 분석, index.md로 파일 고르기, 청크별 yes/no, 리랭킹 대신 문장 번호 고르기를 앞단에서 처리하면 LLM은 답변만 한다. 판단 호출은 배치로 묶는다. 근거 밖 사실 경고는 사용자 대신 trace에 남긴다.
- **평가 데이터셋은 기능이 아니라 고치려는 "문제점"으로 묶는다**(예: 툴 호출 과다 → 궤적 평가). input/expected_output 키는 목적에 맞게 바꿔도 된다. 질문·데이터로 필요한 스킬이 정해지면 LLM에 고르게 하지 말고 코드로 강제 로드한다.
- **다음 주 프로젝트(7강):** 코딩 에이전트를 기반으로 기능 추가·개선. 채점 4항목은 린트, 계획 → 리뷰 → 승인 후에만 코드 변경, 메모리 기반 자가 개선 하네스, 모니터링 연동이다. 기반 에이전트는 바꿔도 된다고 했다.

## 확인 필요 (요약)

- 2강: Claude Code ↔ Langfuse 공식 플러그인 이름과 환경변수 이름(저장소에 없음).
- 4강: 강사는 "백엔드에 PDF 지원이 없다"고 했지만 `used_jev_deepagents/src/attachments.py`에 PDF 처리 코드가 있다. 시연 실패 원인은 미확인.
- 5강: 문장 번호 표기 형식(판서 그림의 `<1>문장1</1>`, `[2]문장2` 중 무엇을 썼는지).
- 5·6·8강: 실습·자습 시간이 길어 무발화 구간이 많다(각 파일 "확인 필요" 참고).
