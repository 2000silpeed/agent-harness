# agent-harness

강의(2~4일차: RAG · 멀티 에이전트 · MCP/Skills/Eval)와 수업 저장소([HyunjunJeon/sds_ax_advanced_2026](https://github.com/HyunjunJeon/sds_ax_advanced_2026))의 5~8일차 자료를 바탕으로, **에이전트 프로젝트를 시작해서 완성품까지 끌고 가는 하네스**다.
기본 대상은 최종 프로젝트 **dcode(deepagents-code) 소스로 Coding Assistant 만들기**(`Day08/project_guide.md`, 평가 40점)다.
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
│   │   │   ├── dcode.md            # dcode 빌드·확장 지점·평가 기준 매핑 (path:line 근거)
│   │   │   └── eval-rsi-rules.md   # Day05 평가·Day05_new 자기개선·Day06 6책임·Jev → 규칙 R1~R32
│   │   ├── templates/      # 단계별 산출물 템플릿 + 결정 기록 + 최적화 요청 원문
│   │   └── scripts/
│   │       ├── phase.sh        # 현재 단계와 남은 게이트를 판정 (순서는 도구가 지킨다)
│   │       └── start-phase.sh  # 단계 템플릿을 design/에 복사
│   └── .claude/
│       ├── settings.json   # SessionStart 훅: 세션마다 현재 단계 표시
│       └── skills/         # project-kickoff, workflow-to-architecture, plan-review, skill-authoring,
│                           # tool-design-review, agent-eval, self-improve-loop, optimize-agent, rubric-check
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

| 단계 | 산출물 | 핵심 원칙 | 평가 항목 | 출처 |
|---|---|---|---|---|
| P0 킥오프 | `00-brief.md` | 완료 정의, 평가 기준 체크리스트, 개발 환경(WSL·별도 venv) | 전체 | 4일차 3강, Day06·07 |
| P1 워크플로우 | `01-workflow.md` | 요구사항 → 계획·리뷰 → 구현 → 검증 → 학습, HITL | 2 | 3일차 2·4·5강 |
| P2 아키텍처 | `02-architecture.md` | 싱글 우선, dcode 확장 지점 선택, 하네스 6책임 | 2·3·4 | 3일차, Day06, dcode 분석 |
| P3 지식·메모리 | `03-knowledge.md` | 규칙과 경험 분리, 검색 후 메시지로 주입, 스레드 1회 로드 한계 | 3-1·3-2 | 2일차, dcode 분석 |
| P4 도구·스킬 | `04-tools-skills.md` | 계획 스킬·리뷰어 서브에이전트, Closed Question 판단 | 2 | 4일차 |
| P5 구현·기준선 | `05-build.md` | `make lint/test`, 헤드리스 실행, 기준선 측정 | 1 | 2·3일차, dcode 분석 |
| P6 하네스·관측 | `06-harness.md` | 계획 승인 게이트(fail-closed), JSONL 이벤트 로그, summary, 조회 | 2-4·4 | 3일차 4강, Day08 |
| P7 평가 | `07-eval.md` | Code → Judge → 사람, fact/hypothesis 분리 | 3-4·4 | 4일차 교재, Day05 |
| P8 자기개선·최적화 | `08-optimization.md` | 손잡이 하나, 같은 조건 비교, ADOPT/HOLD 판정 | 3-3·3-4 | Day05_new, 3일차 6강 |
| P9 제출·회고 | `09-release.md` | README 테스트 케이스, 루브릭 자가 점검, 회고 | 전체 | Day08, 3일차 7강 |

## 강의 노트

[`notes/README.md`](notes/README.md)에서 일차별 종합으로 들어갈 수 있다. 전사가 불명확했던 부분은 각 파일의 "확인 필요"에 따로 표시돼 있다.
