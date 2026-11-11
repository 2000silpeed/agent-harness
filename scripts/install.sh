#!/usr/bin/env bash
# 프로젝트 폴더에 설치한다. 이미 있는 파일은 덮어쓰지 않는다.
#   bash scripts/install.sh <프로젝트 경로>                 # Claude 세팅 + 코딩 에이전트 방법론 도구
#   bash scripts/install.sh --claude-only <프로젝트 경로>   # Claude 세팅만 (지침·규칙·설정 템플릿, 훅 예시)
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE=full
if [[ "${1:-}" == "--claude-only" ]]; then MODE=claude; shift; fi
DST="${1:?설치할 프로젝트 경로를 주세요}"
mkdir -p "$DST"; DST="$(cd "$DST" && pwd)"
SETUP="$REPO/claude-setup"; KIT="$REPO/kit"

copy_tree() {  # $1=원본 폴더, $2=대상 폴더. 이미 있는 파일은 건너뜀
  (cd "$1" && find . -type f) | while IFS= read -r f; do
    if [[ ! -e "$2/$f" ]]; then mkdir -p "$(dirname "$2/$f")"; cp "$1/$f" "$2/$f"; fi
  done
}
copy_new() { [[ -e "$2" ]] || { mkdir -p "$(dirname "$2")"; cp "$1" "$2"; echo "생성: ${2#$DST/}"; }; }
ignore() { touch "$DST/.gitignore"; grep -qxF "$1" "$DST/.gitignore" || echo "$1" >> "$DST/.gitignore"; }

# 1) Claude 세팅: 지침, 경로 규칙, 설정 템플릿, 훅 예시(기본으로 켜지지 않음)
copy_new "$SETUP/templates/CLAUDE.md" "$DST/CLAUDE.md"
copy_new "$SETUP/templates/rules/testing.md" "$DST/.claude/rules/testing.md"
copy_new "$SETUP/templates/settings.local.example.json" "$DST/.claude/settings.local.example.json"
copy_new "$SETUP/templates/mcp.example.json" "$DST/.claude/mcp.example.json"
copy_tree "$SETUP/hooks" "$DST/.claude/hooks"
chmod +x "$DST/.claude/hooks/"*.py "$DST/.claude/hooks/"*.sh
ignore ".claude/settings.local.json"; ignore "CLAUDE.local.md"

SETTINGS="$DST/.claude/settings.json"
if [[ "$MODE" == claude ]]; then
  copy_new "$SETUP/templates/settings.json" "$SETTINGS"
  echo "설치 완료(Claude 세팅): $DST"
  echo "다음: claude-setup/GUIDE.md 의 A2부터 따라가며 CLAUDE.md 와 .claude/rules 를 프로젝트에 맞게 고친다."
  exit 0
fi

# 2) 코딩 에이전트 방법론 도구: harness/, 스킬, 지침 import, SessionStart 훅
copy_tree "$KIT/harness" "$DST/harness"
copy_tree "$KIT/.claude/skills" "$DST/.claude/skills"
chmod +x "$DST/harness/scripts/"*.sh
IMPORT_LINE="@harness/HARNESS.md"
grep -qxF "$IMPORT_LINE" "$DST/CLAUDE.md" || printf '\n%s\n' "$IMPORT_LINE" >> "$DST/CLAUDE.md"

if [[ ! -f "$SETTINGS" ]]; then
  cp "$KIT/.claude/settings.json" "$SETTINGS"
elif grep -q 'harness/scripts/phase.sh' "$SETTINGS"; then
  :
elif command -v jq >/dev/null; then
  tmp="$(mktemp)"
  jq -s '.[0] as $a | .[1] as $b
    | $a * {hooks: (($a.hooks // {}) + {SessionStart: (($a.hooks.SessionStart // []) + $b.hooks.SessionStart)})}' \
    "$SETTINGS" "$KIT/.claude/settings.json" > "$tmp" && mv "$tmp" "$SETTINGS"
else
  echo "주의: $SETTINGS 가 이미 있고 jq 가 없어 훅을 합치지 못했습니다. kit/.claude/settings.json 의 SessionStart 훅을 직접 추가하세요."
fi

mkdir -p "$DST/design"
echo "설치 완료(Claude 세팅 + 방법론 도구): $DST"
echo "다음: 그 폴더에서 Claude Code 를 열고 \"프로젝트 시작하자\" 라고 말하세요."
(cd "$DST" && bash harness/scripts/phase.sh)
