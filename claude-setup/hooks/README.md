# 훅 예시 (필요할 때 켠다)

아래 훅은 설치해도 기본으로 켜지지 않는다. 규칙이 생기고 필요가 확인되면 `.claude/settings.json`에 연결해서 켠다. 연결 예시는 `settings.example.json`이고, 프로젝트에 설치되면 `.claude/hooks/`에 놓인다.

| 파일 | 이벤트 | 하는 일 | 차단 여부 |
|---|---|---|---|
| `plan_gate.py` | PreToolUse (Edit·Write) | 승인된 계획(`design/plans/*.md`의 `status: approved`)이 없으면 코드 수정을 막는다. 입력을 못 읽으면 막는다(fail closed) | 막음 (exit 2) |
| `test_after_edit.py` | PostToolUse (Edit·Write) | 고친 파일과 이름 규칙으로 짝지은 테스트만 돌리고, 실패하면 결과를 모델에 돌려준다 | 이미 실행된 뒤라 막지 않음, 피드백 (exit 2) |
| `prompt_reminder.sh` + `reminders.md` | UserPromptSubmit | 자꾸 잊는 지침을 매 요청에 덧붙인다 | 막지 않음 |

## 주의
- 차단은 명시적 차단 신호(exit 2, JSON deny)로만 된다. **exit 1이나 스크립트 오류·타임아웃은 기본적으로 통과**된다. 꼭 막아야 하는 것은 권한 deny 설정으로도 이중화한다.
- 매처를 우회하는 경로가 있다. 예를 들어 셸 명령으로 파일을 쓰면 Edit·Write 매처를 거치지 않는다. `plan_gate.py`만으로 완전히 막히지 않는다.
- 훅은 권한을 조일 수는 있어도 풀 수는 없다. 클론한 저장소의 훅도 내 PC에서 실행되니 신뢰한 작업 공간에서만 켠다.
- Post·Stop 훅의 통과는 수정 완료의 증거가 아니다. 최종 방어선은 PR 리뷰와 CI다.
- 이벤트 이름, 입력 필드, 차단 방식은 도구 버전마다 다를 수 있다. 켜기 전에 쓰는 도구의 훅 공식 문서로 확인하고, 일부러 틀린 입력으로 차단되는지 시험한다.
