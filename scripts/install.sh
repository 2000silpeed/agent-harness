#!/usr/bin/env bash
# 하네스(kit/)를 새 프로젝트 폴더에 설치한다.
# 사용: bash scripts/install.sh <프로젝트 경로>
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/../kit" && pwd)"
DST="${1:?설치할 프로젝트 경로를 주세요}"
mkdir -p "$DST"
DST="$(cd "$DST" && pwd)"

# 1) harness/ 와 스킬 복사 (기존 파일은 덮어쓰지 않음)
copy_tree() {  # $1=원본 폴더, $2=대상 폴더. 이미 있는 파일은 건너뜀
  (cd "$1" && find . -type f) | while IFS= read -r f; do
    if [[ ! -e "$2/$f" ]]; then mkdir -p "$(dirname "$2/$f")"; cp "$1/$f" "$2/$f"; fi
  done
}
copy_tree "$SRC/harness" "$DST/harness"
copy_tree "$SRC/.claude/skills" "$DST/.claude/skills"
chmod +x "$DST/harness/scripts/"*.sh

# 2) CLAUDE.md 에 하네스 규칙 import
IMPORT_LINE="@harness/HARNESS.md"
if [[ -f "$DST/CLAUDE.md" ]]; then
  grep -qxF "$IMPORT_LINE" "$DST/CLAUDE.md" || printf '\n%s\n' "$IMPORT_LINE" >> "$DST/CLAUDE.md"
else
  printf '# 프로젝트 규칙\n\n%s\n' "$IMPORT_LINE" > "$DST/CLAUDE.md"
fi

# 3) SessionStart 훅 설정 (기존 settings.json 이 있으면 jq 로 병합)
SETTINGS="$DST/.claude/settings.json"
if [[ ! -f "$SETTINGS" ]]; then
  cp "$SRC/.claude/settings.json" "$SETTINGS"
elif grep -q 'harness/scripts/phase.sh' "$SETTINGS"; then
  :
elif command -v jq >/dev/null; then
  tmp="$(mktemp)"
  jq -s '.[0] as $a | .[1] as $b
    | $a * {hooks: (($a.hooks // {}) + {SessionStart: (($a.hooks.SessionStart // []) + $b.hooks.SessionStart)})}' \
    "$SETTINGS" "$SRC/.claude/settings.json" > "$tmp" && mv "$tmp" "$SETTINGS"
else
  echo "주의: $SETTINGS 가 이미 있고 jq 가 없어 훅을 병합하지 못했습니다. kit/.claude/settings.json 의 SessionStart 훅을 직접 추가하세요."
fi

mkdir -p "$DST/design"
echo "설치 완료: $DST"
echo "다음: 그 폴더에서 Claude Code 를 열고 \"프로젝트 시작하자\" 라고 말하세요."
(cd "$DST" && bash harness/scripts/phase.sh)
