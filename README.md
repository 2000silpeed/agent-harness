# agent-harness

8일 과정 강의와 수업 저장소([HyunjunJeon/sds_ax_advanced_2026](https://github.com/HyunjunJeon/sds_ax_advanced_2026))를 바탕으로, **새 에이전트 프로젝트를 시작해서 완성품까지 끌고 가는 하네스**다. 강의가 하루 끝날 때마다 [`UPDATING.md`](UPDATING.md) 절차로 갱신한다. 현재 2~7일차까지 반영했다.
특정 프레임워크를 전제하지 않는다. 강의 실습 도구(LangGraph, Deep Agents)는 예시로만 쓴다.
Claude Code가 이 하네스를 읽고 단계별로 진행한다. 사람은 이 하네스를 설명서로 따라가면 된다.

## 구성

```
agent-harness/
├── UPDATING.md             # 하루 강의 반영 절차와 반영 기록
├── notes/                  # 강의 정리 (일차별 종합 + 강의별 상세)
│   └── _pending/           # 아직 강의 전인 날의 저장소 조사 자료 (하네스 미반영)
├── kit/                    # 프로젝트에 설치되는 하네스 본체
│   ├── harness/
│   │   ├── PLAYBOOK.md     # P0~P9 단계별 설명서 (입력 → 할 일 → 산출물 → 게이트)
│   │   ├── HARNESS.md      # Claude가 매 세션 따르는 작업 규칙 (CLAUDE.md에서 import)
│   │   ├── hooks/          # 필요할 때 켜는 훅 예시 (계획 승인 게이트, 수정 후 테스트, 지침 리마인더)
│   │   ├── templates/      # 단계별 산출물 템플릿 + 결정 기록 + 최적화 요청 원문
│   │   └── scripts/
│   │       ├── phase.sh        # 현재 단계와 남은 게이트를 판정 (순서는 도구가 지킨다)
│   │       └── start-phase.sh  # 단계 템플릿을 design/에 복사
│   └── .claude/
│       ├── settings.json   # SessionStart 훅: 세션마다 현재 단계 표시
│       └── skills/         # project-kickoff, workflow-to-architecture, skill-authoring,
│                           # tool-design-review, hook-design, plan-review, serving-plan, golden-dataset, agent-eval, optimize-agent
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
| P0 킥오프 | `00-brief.md` | 완료 정의와 성공 지표, 아주 작은 조각 하나 | 3일차 7강, 4일차 3강 |
| P1 워크플로우 | `01-workflow.md` | 5단계 이하, 판단/생성 꼬리표, HITL | 3일차 2·4·5강 |
| P2 아키텍처 | `02-architecture.md` | 싱글 우선, 컨텍스트 경계로만 분리 | 3일차 1~3강, 교재 |
| P3 지식·데이터 | `03-knowledge.md` | 계층 폴더 + index.md, 고정은 앞·변하는 값은 뒤 | 2일차 1~3강 |
| P4 도구·스킬 | `04-tools-skills.md` | 도구는 적게·명확하게, 스킬은 XML·단계 공개 | 4일차 1·2·5·6강 |
| P5 구현·기준선 | `05-build.md` | 가장 단순한 버전, 기록 남기기, 기준선 측정, 모델·서빙 결정(용량 = 가중치 + KV) | 2일차 5·6강, 3일차 5강, 7일차 |
| P6 하네스·안전·관측 | `06-harness.md` | 제안과 실행 분리, 부탁·위임·강제 배치와 훅 설계, 계획 승인 후 코드 변경, 관측 | 3일차 4강, 5일차 2·7강, 6일차 |
| P7 평가 | `07-eval.md` | 시나리오형 Golden Set, Outcome/Trajectory/Response, 평가기 반례 검증, 조건 잠금 비교 | 4일차, 5일차 |
| P8 최적화·개선 | `08-optimization.md` | 동작 유지·토글·근거, 서빙 최적화, 기록 기반 개선은 검증 통과분만 반영 | 3일차 6강, 5일차 7강, 7일차 |
| P9 릴리스·회고 | `09-release.md` | 검증된 것만 배포, Eval 카드, 회고 | 4일차 3강, 교재 Ch.7 |

## 강의 노트

[`notes/README.md`](notes/README.md)에서 일차별 종합으로 들어갈 수 있다. 전사가 불명확했던 부분은 각 파일의 "확인 필요"에 따로 표시돼 있다.
