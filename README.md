# agent-harness

8일 과정 강의와 수업 저장소([HyunjunJeon/sds_ax_advanced_2026](https://github.com/HyunjunJeon/sds_ax_advanced_2026))에서 **두 가지 목적에 필요한 것만** 골라 정리한 저장소다. 강의가 올라올 때마다 [`UPDATING.md`](UPDATING.md) 절차로 갱신한다. 현재 2~7일차까지 반영했다.

| 축 | 질문 | 읽을 문서 |
|---|---|---|
| ① 내 Claude 세팅 | 내 Claude Code를 어떻게 세팅해서 쓰면 좋은가 | [`claude-setup/GUIDE.md`](claude-setup/GUIDE.md) |
| ② 회사 코딩 에이전트 구축 | 어떤 순서로 만들고, 단계마다 무엇을 고민하고, 어떻게 검증하고, 언제 끝났다고 보고, 무엇을 병렬로 할 수 있는가 | [`kit/harness/METHOD.md`](kit/harness/METHOD.md), 통과해야 할 기준은 [`kit/harness/CRITERIA.md`](kit/harness/CRITERIA.md) |

두 문서 모두 단계마다 **왜 / 고민할 것 / 진행 / 검증 / 끝났다는 기준 / 순서와 병렬**을 적었다. 특정 프레임워크를 전제하지 않는다.

## 구성

```
agent-harness/
├── claude-setup/           # 축 ①
│   ├── GUIDE.md            # A0~A10: 전역 정리 → 지침 → 설정 → 기록 → 스킬 → 훅 → 검증, 승격 규칙
│   ├── templates/          # CLAUDE.md, 경로 규칙, 설정 파일 템플릿
│   └── hooks/              # 필요할 때 켜는 훅 예시 (계획 승인 게이트, 수정 후 테스트, 지침 리마인더)
├── kit/                    # 축 ②: 코딩 에이전트 프로젝트에 설치하는 것
│   ├── harness/
│   │   ├── METHOD.md       # S0~S8 방법론 본문
│   │   ├── CRITERIA.md     # 인수 기준 16개 항목(40점) → 단계 → 만들 것 → 증명
│   │   ├── HARNESS.md      # Claude가 매 세션 따르는 작업 규칙
│   │   ├── templates/      # 단계별 산출물 양식 (결정 사항, 검증 기록, 완료 기준)
│   │   └── scripts/        # phase.sh(단계 상태·병렬 가능 여부), start-phase.sh(선행 단계 확인)
│   └── .claude/            # 단계별 스킬, SessionStart 훅
├── notes/                  # 강의 원자료 정리 (일차별). 두 문서의 근거
├── scripts/install.sh
└── UPDATING.md             # 강의 반영 절차와 기록
```

## 사용법

```bash
# Claude 세팅만 (지침·규칙·설정 템플릿, 훅 예시)
bash scripts/install.sh --claude-only ~/work/my-project

# 코딩 에이전트 구축 프로젝트 (Claude 세팅 + 방법론 도구)
bash scripts/install.sh ~/work/coding-agent
```

이미 있는 파일은 덮어쓰지 않는다. 훅 예시는 설치만 되고 켜지지 않는다.

코딩 에이전트 프로젝트에서는 Claude Code를 열면 단계 상태가 보인다. `bash harness/scripts/phase.sh`로도 볼 수 있다.

## 코딩 에이전트 구축 단계 (축 ②)

```
S0 범위·기반 ─┬─► S1 시험지·채점기 ───────────┐
              └─► S2 뼈대·관측 ─────────► [기준선] ─┬─► S3 컨텍스트·메모리 ─┐
                                                   ├─► S4 도구·스킬 ───────┼─► S6 자기개선 ─┐
                                                   └─► S5 실행 제어 ───────┤                ├─► S8 배포·운영
                                                                           └─► S7 최적화 ───┘
```

- 같은 열에 있는 단계는 동시에 진행할 수 있다(S1과 S2, S3·S4·S5, S6과 S7).
- 만드는 것은 병렬, 반영하는 것은 하나씩이다. 반영할 때마다 평가를 돌린다.
- 평가(S1)와 기록(S2)이 먼저다. 재지 못하면 좋아졌는지 알 수 없다.

## 강의 노트

[`notes/README.md`](notes/README.md)에서 일차별 정리로 들어간다. 강의에는 두 축과 직접 관련 없는 내용(모델 업계 동향, 추론 엔진 내부 구조 등)도 많다. 그런 내용은 노트에만 두고 두 문서에는 넣지 않았다.
