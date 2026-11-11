#!/usr/bin/env bash
# UserPromptSubmit 훅: reminders.md의 짧은 사실 진술을 요청마다 덧붙인다.
#
# - exit 0일 때 stdout의 일반 텍스트가 모델 컨텍스트에 추가된다.
#   출력이 '{'로 시작하면 JSON으로 해석되므로 reminders.md는 '{'로 시작하지 않게 쓴다.
# - 붙인 글은 대화 기록에 남아 요청마다 쌓인다. 몇 줄로 유지하고, 변하지 않는 규칙은 지침 파일에 둔다.
# - 고장 정책은 통과(fail open)다. 파일이 없거나 비어 있으면 아무것도 붙이지 않는다. 막는 훅이 아니다.
f="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/reminders.md"
[[ -s "$f" ]] && cat "$f"
exit 0
