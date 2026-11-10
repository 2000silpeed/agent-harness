#!/usr/bin/env bash
# 단계별 상태를 보여준다: 완료 / 진행 중 / 지금 시작할 수 있음(병렬 가능) / 선행 단계 대기.
# 사용: bash harness/scripts/phase.sh [--brief]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
DESIGN="$ROOT/design"
BRIEF="${1:-}"
source "$HERE/stages.sh"

declare -A STATE NAME
for e in "${STAGES[@]}"; do
  IFS='|' read -r n file name deps skills <<<"$e"
  STATE[$n]="$(stage_state "$DESIGN" "$file")"; NAME[$n]="$name"
done

done_n=0; doing=(); ready=(); blocked=()
for e in "${STAGES[@]}"; do
  IFS='|' read -r n file name deps skills <<<"$e"
  case "${STATE[$n]}" in
    done) done_n=$((done_n+1)) ;;
    doing) doing+=("$e") ;;
    none)
      wait_for=""
      for d in $deps; do [[ "${STATE[$d]}" == done ]] || wait_for+="S$d "; done
      if [[ -z "$wait_for" ]]; then ready+=("$e"); else blocked+=("$name ← ${wait_for% } 완료 필요"); fi ;;
  esac
done

total=${#STAGES[@]}
if (( done_n == total )); then
  echo "[하네스] 모든 단계(S0~S8) 완료 기준 통과. 운영 루프(기록 → 평가셋 승격 → 개선)를 이어 간다."
  exit 0
fi
echo "[하네스] 완료 ${done_n}/${total}"
if (( ${#doing[@]} )); then
  echo "진행 중:"
  for e in "${doing[@]}"; do
    IFS='|' read -r n file name deps skills <<<"$e"
    gates="$(open_gates "$DESIGN/$file.md")"
    echo "  - $name (design/$file.md, 남은 완료 기준 $(echo "$gates" | wc -l | tr -d ' ')개)"
    if [[ "$BRIEF" == "--brief" ]]; then echo "$gates" | head -3 | sed 's/^/      /'; else echo "$gates" | sed 's/^/      /'; fi
    [[ "$skills" != "-" ]] && echo "      스킬: $skills"
  done
fi
if (( ${#ready[@]} )); then
  (( ${#ready[@]} > 1 )) && echo "지금 시작할 수 있음 (서로 병렬 가능):" || echo "지금 시작할 수 있음:"
  for e in "${ready[@]}"; do
    IFS='|' read -r n file name deps skills <<<"$e"
    line="  - $name → bash harness/scripts/start-phase.sh $n"
    [[ "$skills" != "-" ]] && line+="  (스킬: $skills)"
    echo "$line"
  done
fi
if (( ${#blocked[@]} )) && [[ "$BRIEF" != "--brief" ]]; then
  echo "선행 단계 대기:"
  for b in "${blocked[@]}"; do echo "  - $b"; done
fi
[[ "$BRIEF" == "--brief" ]] || echo "지침: harness/METHOD.md 의 해당 단계 절. 병렬로 만들되 반영은 하나씩, 반영할 때마다 평가를 돌린다."
mkdir -p "$DESIGN"; printf '%s\tdone=%s doing=%s ready=%s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "$done_n" "${#doing[@]}" "${#ready[@]}" >> "$DESIGN/.phase-log"
