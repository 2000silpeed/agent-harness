#!/usr/bin/env bash
# UserPromptSubmit 훅: 자꾸 잊는 지침을 매 요청에 덧붙인다(6일차 6강).
# stdout으로 내보낸 내용이 모델 컨텍스트에 추가된다. 내용은 reminders.md에서 짧게 관리한다.
f="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/reminders.md"
[[ -s "$f" ]] && cat "$f"
exit 0
