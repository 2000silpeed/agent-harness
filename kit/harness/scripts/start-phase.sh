#!/usr/bin/env bash
# 단계 산출물 템플릿을 design/ 으로 복사한다. 선행 단계가 안 끝났으면 거절한다.
# 사용: bash harness/scripts/start-phase.sh <0~8> [--force "이유"]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
TPL="$ROOT/harness/templates"
DESIGN="$ROOT/design"
source "$HERE/stages.sh"
num="${1:?단계 번호(0~8)를 주세요}"; num="$((10#$num))"
force="${2:-}"; reason="${3:-}"

found=""
for e in "${STAGES[@]}"; do
  IFS='|' read -r n file name deps skills <<<"$e"
  [[ "$n" == "$num" ]] && { found="$e"; break; }
done
[[ -z "$found" ]] && { echo "없는 단계: $num (0~8)"; exit 1; }
IFS='|' read -r n file name deps skills <<<"$found"

wait_for=""
for d in $deps; do
  for e in "${STAGES[@]}"; do
    IFS='|' read -r dn dfile dname _ _ <<<"$e"
    [[ "$dn" == "$d" ]] && [[ "$(stage_state "$DESIGN" "$dfile")" != done ]] && wait_for+="$dname, "
  done
done
mkdir -p "$DESIGN"
[[ -e "$DESIGN/decisions.md" ]] || { cp "$TPL/decisions.md" "$DESIGN/decisions.md"; echo "생성: design/decisions.md"; }
if [[ -n "$wait_for" ]]; then
  if [[ "$force" == "--force" && -n "$reason" ]]; then
    printf '| %s | %s | 선행 단계(%s) 미완료 상태로 시작 | 건너뜀 | %s | 선행 단계 완료 후 재검토 |\n' "$(date '+%Y-%m-%d')" "$name" "${wait_for%, }" "$reason" >> "$DESIGN/decisions.md"
    echo "선행 단계 미완료(${wait_for%, })를 건너뜁니다. 이유를 design/decisions.md에 기록했습니다."
  else
    echo "거절: '$name'을 시작하려면 먼저 끝내야 합니다 → ${wait_for%, }"
    echo "꼭 건너뛰어야 하면: bash harness/scripts/start-phase.sh $num --force \"이유\""
    exit 2
  fi
fi
dst="$DESIGN/$file.md"
if [[ -e "$dst" ]]; then echo "이미 있음: design/$file.md (덮어쓰지 않음)"; else cp "$TPL/$file.md" "$dst"; echo "생성: design/$file.md"; fi
printf '%s\tstart %s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "$name" >> "$DESIGN/.phase-log"
echo "다음: harness/METHOD.md 의 '$name' 절을 읽고 산출물을 채운다. 완료 기준을 실제로 확인한 뒤 체크한다."
