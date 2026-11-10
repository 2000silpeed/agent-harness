# 템플릿

| 파일 | 놓는 곳 | 커밋 | 용도 |
|---|---|---|---|
| `CLAUDE.md` | 프로젝트 루트 | 한다 | 프로젝트 지침. XML 구역, 200줄 이하 |
| `rules/testing.md` | `.claude/rules/` | 한다 | 경로 범위 규칙 예시. `paths`에 맞는 파일을 다룰 때만 로드 |
| `settings.json` | `.claude/settings.json` | 한다 | 팀 공유 설정. 권한 금지 목록부터 |
| `settings.local.example.json` | `.claude/settings.local.json`으로 복사 | 안 한다 | 개인 설정. 이 프로젝트에서만 다른 모델·엔드포인트를 쓸 때. 인증 값은 파일에 적지 말고 직접 관리한다 |

설정 키와 환경 변수 이름은 버전에 따라 바뀔 수 있다. 적용 전에 공식 문서의 설정·환경 변수 페이지로 확인한다.
