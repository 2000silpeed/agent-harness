# agent-harness

강의(2~4일차: RAG · 멀티 에이전트 · MCP/Skills/Eval)와 수업 저장소([HyunjunJeon/sds_ax_advanced_2026](https://github.com/HyunjunJeon/sds_ax_advanced_2026))의 평가·하네스 자료를 바탕으로, **에이전트 프로젝트를 시작해서 완성품까지 끌고 가는 하네스**다. 특정 과제에 묶이지 않는다.
Claude Code가 이 하네스를 읽고 단계별로 진행한다. 사람은 이 하네스를 설명서로 따라가면 된다.

## 구성

```
agent-harness/
├── notes/                  # 강의 정리 (일차별 종합 + 강의별 상세)
├── kit/                    # 프로젝트에 설치되는 하네스 본체
│   ├── harness/
│   │   ├── PLAYBOOK.md     # P0~P9 단계별 설명서 (입력 → 할 일 → 산출물 → 게이트)
│   │   ├── HARNESS.md      # Claude가 매 세션 따르는 작업 규칙 (CLAUDE.md에서 import)
│   │   ├── reference/
│   │   │   └── eval-rsi-rules.md   # Day05 평가·Day05_new 자기개선·Day06 6책임·Jev → 규칙 R1~R32
│   │   ├── templates/      # 단계별 산출물 템플릿 + 결정 기록 + 최적화 요청 원문
│   │   └── scripts/
│   │       ├── phase.sh        # 현재 단계와 남은 게이트를 판정 (순서는 도구가 지킨다)
│   │       └── start-phase.sh  # 단계 템플릿을 design/에 복사
│   └── .claude/
│       ├── settings.json   # SessionStart 훅: 세션마다 현재 단계 표시
│       └── skills/         # project-kickoff, workflow-to-architecture, plan-review, skill-authoring,
│                           # tool-design-review, agent-eval, self-improve-loop, optimize-agent, criteria-check
└── scripts/install.sh      # kit을 새 프로젝트에 설치
```

## 사용법

```bash
# 1) 새 프로젝트(또는 기존 저장소)에 설치
bash scripts/install.sh ~/work/my-agent

# 2) 그 폴더에서 Claude Code 실행 후
"프로젝트 시작하자"
```

설치하면 다음이 생긴다.
- `CLAUDE.md`에 `@harness/HARNESS.md`가 추가된다. 기존 내용은 유지된다.
- `.claude/settings.json`에 SessionStart 훅이 추가된다. 기존 설정이 있으면 jq로 병합한다.
- `harness/`, `.claude/skills/`, `design/`이 생긴다. 이미 있는 파일은 덮어쓰지 않는다.

이후 Claude는 매 세션 `phase.sh`로 현재 단계를 확인한다. 해당 단계의 템플릿을 `design/`에 채우고, 게이트가 모두 체크되면 다음 단계로 넘어간다.

## 단계

| 단계 | 산출물 | 핵심 원칙 | 출처 |
|---|---|---|---|
| P0 킥오프 | `00-brief.md` | 완료 정의, 인수 기준, 아주 작은 조각 하나 | 3일차 7강, 4일차 3강 |
| P1 워크플로우 | `01-workflow.md` | 5단계 이하, 판단/생성 꼬리표, HITL | 3일차 2·4·5강 |
| P2 아키텍처 | `02-architecture.md` | 싱글 우선, 컨텍스트 경계로만 분리, 하네스 6책임 | 3일차, Day06 자료 |
| P3 지식·메모리 | `03-knowledge.md` | 계층 폴더 + index.md, 규칙·경험 분리, 변하는 값은 뒤에 | 2일차 1~3강 |
| P4 도구·스킬 | `04-tools-skills.md` | 도구는 적게·명확하게, 스킬은 XML·단계 공개, Closed Question 판단 | 4일차 |
| P5 구현·기준선 | `05-build.md` | 가장 단순한 버전, 기록 남기기, 기준선 측정 | 2일차 5·6강, 3일차 5강 |
| P6 하네스·관측 | `06-harness.md` | 제안과 실행 분리, 승인 게이트(fail-closed), JSONL 로그 | 3일차 4강, 교재 |
| P7 평가 | `07-eval.md` | Code → Judge → 사람, fact/hypothesis 분리 | 4일차 교재, Day05 자료 |
| P8 자기개선·최적화 | `08-optimization.md` | 손잡이 하나, 같은 조건 비교, ADOPT/HOLD, 동작 유지 | Day05_new 자료, 3일차 6강 |
| P9 릴리스·회고 | `09-release.md` | 인수 기준 자가 점검, Eval 카드, 회고 | 4일차 교재, 3일차 7강 |

## 강의 노트

[`notes/README.md`](notes/README.md)에서 일차별 종합으로 들어갈 수 있다. 전사가 불명확했던 부분은 각 파일의 "확인 필요"에 따로 표시돼 있다.
