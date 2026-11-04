#!/usr/bin/env bash
# PostToolUse 감시 훅: 어떤 도구를 언제 불렀는지만 기록한다(입력·출력 내용은 기록하지 않음).
# 출력: $CLAUDE_PROJECT_DIR/.harness/logs/tool-use.jsonl  (gitignore 대상)
# 실패해도 작업을 막지 않도록 항상 exit 0.
set -u
dir="${CLAUDE_PROJECT_DIR:-.}/.harness/logs"
mkdir -p "$dir" 2>/dev/null || exit 0
input="$(cat)"
if command -v jq >/dev/null 2>&1; then
  printf '%s' "$input" | jq -c --arg ts "$(date -u +%FT%TZ)" \
    '{ts: $ts, session: .session_id, tool: .tool_name}' >> "$dir/tool-use.jsonl" 2>/dev/null
else
  tool="$(printf '%s' "$input" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
  printf '{"ts":"%s","tool":"%s"}\n' "$(date -u +%FT%TZ)" "$tool" >> "$dir/tool-use.jsonl"
fi
exit 0
