# agent-harness

SDS AX Advanced 과정(2~3일차: RAG·컨텍스트·스킬·멀티턴 → 멀티 에이전트 아키텍처·하네스·최적화·Claude Code 활용) 강의 자료를 바탕으로 만든 **Claude Code용 에이전트 하네스**입니다. 그대로 쓰기보다 각자의 업무에 맞게 고쳐 쓰는 출발점으로 만들었습니다.

## 구성
```
CLAUDE.md                 # 짧고 고정된 작업 규칙 (캐시 보호를 위해 변동 값 없음)
docs/                     # 단계별 가이드 00~15 + 사례 + decisions/
templates/                # 설계서, 계약, 로그, 노트, 핸드오프, 스킬 뼈대 등
.claude/skills/           # 프로젝트 스킬 9종
.claude/settings.json     # .env 접근 차단 + 도구 사용 기록 훅
.claude/hooks/            # log-tool-use.sh (PostToolUse 감시)
examples/stepguard.py     # 도구가 순서를 강제하는 패턴 + 테스트
memory/                   # session-memory 표지판
.env.example              # 키는 사람이 직접 입력
```

## 스킬
| 스킬 | 언제 |
|---|---|
| design-agent-architecture | 새 에이전트·자동화 설계 (워크플로우 → CODE/MODEL/HUMAN) |
| split-decision | 서브에이전트로 나눌지 판단 |
| workflow-to-agent | LangGraph MVP → 에이전트 → 도구 강제 순서 |
| optimize-agent | 동작 불변·토글·근거로 최적화 |
| gold-dataset-loop | 정답지 기반 평가·보정 반복 |
| interview-me | 모호한 요구사항을 인터뷰로 파내기 |
| retro | 대화 기록으로 주간 회고 |
| session-memory | 주제 종료 시 표지판 남기기, 재등장 시 상세 요약 |
| folder-summarizer | 낯선 자료 폴더 요약 + index.md 초안 |

## 다른 프로젝트에 적용하기
1. `CLAUDE.md`, `.claude/`, `templates/`를 대상 저장소에 복사합니다. `docs/`는 참고용으로 링크만 걸어도 됩니다.
2. `CLAUDE.md`의 규칙 중 맞지 않는 것은 지우고, 프로젝트 고유 규칙은 짧게 덧붙입니다. 날짜나 버전처럼 바뀌는 값은 넣지 않습니다.
3. 첫 작업은 `design-agent-architecture`로 업무 하나를 5단계 이하로 설계하는 것부터 시작합니다.

## 출처와 표기
- 강의에서 직접 나온 내용은 **[강의]**, 하네스용으로 덧붙인 제안은 **[제안]**, 전사가 불확실한 내용은 **[불확실]**로 표시했습니다.
- 강의에서 실제 settings.json, 훅, 서브에이전트 정의 원문은 공개되지 않았습니다. 이 저장소의 설정, 훅, 스킬은 강의 원칙을 바탕으로 새로 작성한 것입니다.
- 3일차 6강의 최적화 지시문 원문(txt)은 이번 정리에 포함되지 않았습니다.

## 주의
무거운 멀티 에이전트, 장시간 목표 루프, 바이너리 분석은 토큰 소모가 큽니다. 회사 계정 한도에 영향이 없도록 개인 계정이나 작은 범위에서 먼저 검증하세요.
