#!/usr/bin/env bash
# 단계 템플릿을 design/ 으로 복사한다. 이미 있으면 덮어쓰지 않는다.
# 사용: bash harness/scripts/start-phase.sh <00~09>
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TPL="$ROOT/harness/templates"
DESIGN="$ROOT/design"
num="${1:?단계 번호(00~09)를 주세요}"
num="$(printf '%02d' "$((10#$num))")"
src="$(ls "$TPL"/"$num"-*.md 2>/dev/null | head -1 || true)"
[[ -z "$src" ]] && { echo "템플릿 없음: $num"; exit 1; }
mkdir -p "$DESIGN"
dst="$DESIGN/$(basename "$src")"
if [[ -e "$dst" ]]; then
  echo "이미 있음: design/$(basename "$src") (덮어쓰지 않음)"
else
  cp "$src" "$dst"
  echo "생성: design/$(basename "$src")"
fi
[[ -e "$DESIGN/decisions.md" ]] || { cp "$TPL/decisions.md" "$DESIGN/decisions.md"; echo "생성: design/decisions.md"; }
printf '%s\tstart-phase %s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "$num" >> "$DESIGN/.phase-log"
echo "다음: 템플릿을 채우고 게이트를 체크한 뒤 bash harness/scripts/phase.sh"
