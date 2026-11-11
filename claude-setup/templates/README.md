# 템플릿

| 파일 | 놓는 곳 | 커밋 | 용도 |
|---|---|---|---|
| `CLAUDE.md` | 프로젝트 루트(또는 `.claude/CLAUDE.md`) | 한다 | 프로젝트 지침. 200줄 이하. 구역은 마크다운 헤더와 불릿으로 나눈다(공식 문서가 권하는 구조) |
| `rules/testing.md` | `.claude/rules/` | 한다 | 경로 범위 규칙 예시. `paths`에 맞는 파일을 읽거나 고칠 때만 로드된다. `paths`가 없으면 매 세션 로드된다 |
| `settings.json` | `.claude/settings.json` | 한다 | 팀 공유 설정. 금지(`deny`)와 확인(`ask`) 규칙부터. MCP 서버는 여기에 두지 않는다 |
| `mcp.example.json` | 저장소 루트에 `.mcp.json`으로 복사 | 한다 | 팀 공유 MCP 서버 예시. 인증 값은 `${변수}`로 참조하고 파일에 적지 않는다. 팀원은 각자 서버를 승인해야 한다 |
| `settings.local.example.json` | `.claude/settings.local.json`으로 복사 | 안 한다 | 개인 설정. 이 프로젝트에서만 다른 모델·엔드포인트를 쓸 때 |

## 쓰기 전에
- 설정 파일은 엄격한 JSON이다. 주석과 끝 쉼표는 오류다. `<...>` 자리표시는 실제 값으로 바꾸고, 쓰지 않는 키는 지운다.
- `settings.local.json`을 손으로 만들었으면 `.gitignore`에 직접 넣는다. Claude Code가 처음 쓸 때만 자동으로 git 제외 목록에 들어간다.
- 인증 값은 커밋되는 파일에 두지 않는다. 셸 환경 변수, 로컬 설정 파일, `apiKeyHelper` 중 하나를 쓴다.
- `settings.local.example.json`의 `ANTHROPIC_BASE_URL`은 요청을 보낼 곳만 바꾼다. 모델은 `model` 키가 정한다. 게이트웨이가 다른 모델 ID를 요구할 때만 `env`에 `ANTHROPIC_DEFAULT_SONNET_MODEL`(별칭 `sonnet`이 가리킬 ID)을 더한다.
- `CLAUDE.md`의 안내 주석(`<!-- -->`)은 컨텍스트에 넣기 전에 제거되므로 토큰을 쓰지 않는다. 규칙 파일의 주석도 제거되는지는 확인 필요다. 규칙 파일은 채운 뒤 주석을 지운다.

## 금지 규칙의 범위
- `Read(./.env)`는 Claude를 시작한 디렉터리의 `.env`만 막는다. 하위 폴더의 `.env`까지 막으려면 `Read(**/.env)`를 쓴다.
- `Read(./.env.*)`는 `.env.example`도 막는다. 같은 `deny` 목록에서 뒤에 `!`로 시작하는 부정 패턴을 두면 예외를 뺄 수 있다. 예: `Read(!.env.example)`. 이 문자열 자체는 공식 예시에 없으므로 확인 필요다. 적용 뒤 실제로 읽히는지 시험한다.
- `Read(./secrets/**)`가 하위 폴더의 `secrets/`에도 걸리는지는 확인 필요다. 모든 깊이를 막으려면 `Read(secrets/**)`로 쓴다.
- `Read` 금지는 파일 도구와 `cat` 같은 읽기 명령을 막는다. `grep -r`이나 스크립트가 직접 여는 것까지 막으려면 샌드박스를 켠다.
- `ask`의 `Bash(git push *)`는 푸시 전에 항상 묻게 한다. 필요 없으면 지운다.

## 적용 뒤 확인
```bash
python3 -m json.tool .claude/settings.json > /dev/null && echo OK
git check-ignore -v .claude/settings.local.json
claude doctor          # 설정 오류
claude mcp list        # .mcp.json 서버 상태(승인 대기 포함)
```
세션 안에서는 `/status`(읽은 설정 파일), `/permissions`(규칙과 출처 파일), `/mcp`를 본다.

설정 키와 환경 변수 이름은 버전에 따라 바뀔 수 있다. 적용 전에 공식 문서의 [설정](https://code.claude.com/docs/en/settings-reference)·[환경 변수](https://code.claude.com/docs/en/env-vars)·[MCP](https://code.claude.com/docs/en/mcp) 페이지로 확인한다.
