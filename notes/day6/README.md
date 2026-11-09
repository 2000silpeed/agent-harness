# 6일차 종합 — Claude Code로 구성하는 하네스: 메모리(부탁) · 스킬(위임) · 훅(강제)

| 파일 | 내용 |
|---|---|
| [00-deck.md](00-deck.md) | 교재: Claude Code로 구성하는 Harness — Memory, Skills, Hooks (원본 PDF 95쪽까지 보충) |
| [01-lecture1.md](01-lecture1.md) | 1강: 하네스 수업 도입, 웹·앱·CLI 비교, `.claude` 폴더와 `settings.json` |
| [02-lecture2.md](02-lecture2.md) | 2강: 메모리 계층 — CLAUDE.md, rules, CLAUDE.local.md, AGENTS.md |
| [03-lecture3.md](03-lecture3.md) | 3강: 훅 생애 주기별 활용법 |
| [04-lecture4.md](04-lecture4.md) | 4강: Anthropic 에이전트 메모리 글과 드리밍, pstack·Ouroboros 분석 실습 |
| [05-lecture5.md](05-lecture5.md) | 5강: 국산 모델 동향, Ouroboros 인터뷰로 나만의 플러그인 만들기 |
| [06-lecture6.md](06-lecture6.md) | 6강: 프로젝트 단위 훅 설계와 나만의 하네스 만들기·검증 |
| [99-extras.md](99-extras.md) | 배포 자료 `harness_final.pdf`(하네스 6계층·Ratchet), `Context as an Environment.pdf`(Scroll), 판서 이미지 4장 |

## 실습 코드 위치

수업 저장소 `github.com/HyunjunJeon/sds_ax_advanced_2026` 기준이다(2026-11-09 `de9b90a1`).

| 강의 | 저장소 위치 | 비고 |
|---|---|---|
| 1·2강 설정·메모리 | `Day06_new/docs/sources/claude_code/01_instructions.md`, `04_state.md`, `Day06_new/CLAUDE.md`(`@AGENTS.md` 한 줄) | 공식 문서 대장(I·T·C·S…) 형태로 정리돼 있음 |
| 3·6강 훅 | `Day06_new/docs/sources/claude_code/03_control.md`, `Day06_new/use_cc/lab/hook_templates/`, `use_cc/part2/concept.md` | 훅 이벤트와 템플릿 |
| 4·5강 플러그인 분석 | `Day06_new/info.md`(pstack·Ouroboros·superpowers·claude-mem 링크), `Day06/ouroboros/`, `Day06/task.md` | pstack은 저장소에 없음(공식: `cursor/plugins`의 `pstack`) |
| 하네스 소스 분석 트랙 | `Day06/HARNESSES.md`, `Day06/AGENTS.md`(여섯 책임·근거 수준), `Day06/pi`, `deepseek-harness`, `ouroboros` | 강의에서 직접 다루지 않음. `Day06/gajae-code/`는 문서에서 인용되지만 저장소에 없음 |
| 이론 PDF | `Day06/Day6_Agent_Harness_이론자료.pdf`(50쪽) | 강의 교재 `CC_Harness_Day6.pdf`와 다른 자료 |

## 하루 요약

- **오늘은 개발 하네스를 세팅하는 날.** 공개 하네스를 설치·분석하고 포크해서 "나만의 하네스"를 만든 뒤, 빈 폴더에서 작은 개발 작업(백엔드 API 하나)으로 검증한다. 기능이 궁금하면 공식 문서의 핵심 개념(작동 방식, 확장, 설정 디렉터리, 컨텍스트 윈도우)부터 읽는다.
- **부탁 → 위임 → 강제.** 메모리(CLAUDE.md 등)는 부탁, 스킬은 위임, 훅은 강제다. 메모리는 지시일 뿐 강제가 아니다. 같은 컨벤션을 두 번 틀리면 상시 지침에, 같은 절차를 세 번째 붙여넣으면 스킬에, 매번 일어나야 하면 훅에, 다른 저장소에도 필요하면 플러그인으로 묶는다.
- **메모리는 계층으로.** 조직 / 개인 전역 / 프로젝트 / 경로 범위 rules / 개인 로컬 / 자동 메모리. 전역은 비우거나 공통만 두고, 팀 지침은 커밋한다. 자동 메모리는 개인 PC에만 있어 "같은 도구인데 체감이 다른" 원인이 된다. CLAUDE.md는 시스템 프롬프트가 아니라 유저 메시지로 들어가고, 덮어쓰지 않고 이어붙는다. CLAUDE로 시작하는 파일이 있으면 AGENTS.md는 읽지 않는다. 문서 양식은 XML로 통일하라고 권했다.
- **훅이 안정성을 좌우한다.** 도구 전·후가 가장 중요하다. Pre는 막고, Post는 고치게 하고, Stop은 끝내기 전에 확인한다. 검사는 훅, 해결은 스킬이다. 대표 예: 코드 파일을 고치면 이름 규칙으로 짝지은 테스트만 LLM 판단 없이 돌린다.
- **훅의 함정(교재 3부).** exit 2나 JSON deny만 막고 exit 1·오류·타임아웃은 조용히 통과한다(fail open). 셸로 파일 쓰기는 Edit·Write 매처를 우회한다. 훅은 권한을 조일 수는 있어도 풀 수는 없고, 클론한 저장소의 훅도 내 PC에서 돈다. 어느 한 층도 완전하지 않으니 최종 방어선은 PR 리뷰와 CI다.
- **설정 범위.** 프로젝트 `settings.json`(팀 공유)과 `settings.local.json`(개인)을 나누고, 비싼 모델·엔드포인트는 그 프로젝트의 `env`에서만 바꾼다.
- **에이전트 메모리(Anthropic 글).** 트랜스크립트 → 노트 → 표현 → 주입 컨텍스트로 압축되고, "드리밍"이 불필요한 것을 걷어낸다. 작은 내용을 남겨도 의미 있게 동작한다. 무엇을 남길지는 작업 종류에 따라 정한다.
- **공개 하네스 분석.** pstack은 대부분의 스킬을 모델이 스스로 못 부르게 막고, 진입점이 23개 플레이북 중 하나를 골라 단계 그대로 따르게 한다. Ouroboros는 소크라테스식 인터뷰로 계획을 만든다. 인터뷰가 끝나지 않으면 20턴쯤에서 멈추고 만들게 한다. 개인화 버전을 설치하면 원본은 지운다.

## 확인 필요 (요약)

- 1강: advisor 비용(강의는 "토큰을 안 쓴다", 공식 문서는 사용량 한도·크레딧에 포함), `history.jsonl` 범위(강의는 전체 대화, 공식은 입력한 프롬프트만). 둘 다 공식 문서와 달라 미확인으로 남김.
- 2강: 세션 시작 적재 순서 6단계 중 일부(공식 문서는 나열만 함).
- 4강: Claude Code의 드리밍 켜고 끄기(공식 문서에 없음, 제3자 글만 있음), Ouroboros setup이 전역 CLAUDE.md를 고치는지 프로젝트별인지(강의와 저장소 스킬이 다름).
- 6강: "Claude는 `.env`를 직접 못 본다"(공식 문서 미확인), pstack 테스트 매핑 예시(README에 없음).
- 교재 `harness_final.pdf`는 저자 미상의 독립 정리 자료이고 일부 수치에 출처가 없다(99-extras 참고).
