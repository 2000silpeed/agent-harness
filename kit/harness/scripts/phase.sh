#!/usr/bin/env bash
# 현재 단계를 design/ 산출물의 게이트 체크박스로 판정한다.
# 사용: bash harness/scripts/phase.sh [--brief]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DESIGN="$ROOT/design"
BRIEF="${1:-}"

PHASES=(
  "00-brief|P0 킥오프|project-kickoff"
  "01-workflow|P1 워크플로우|workflow-to-architecture"
  "02-architecture|P2 아키텍처|workflow-to-architecture"
  "03-knowledge|P3 지식·데이터|-"
  "04-tools-skills|P4 도구·스킬|skill-authoring, tool-design-review"
  "05-build|P5 구현·기준선|-"
  "06-harness|P6 하네스·안전·관측|tool-design-review, plan-review"
  "07-eval|P7 평가|golden-dataset, agent-eval"
  "08-optimization|P8 최적화·개선|optimize-agent"
  "09-release|P9 릴리스·회고|-"
)

# 게이트 절의 미체크 항목 출력
open_gates() {
  awk '/^## 게이트/{g=1;next} /^## /{g=0} g && /^- \[ \]/' "$1"
}

log() {
  mkdir -p "$DESIGN"
  printf '%s\t%s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "$1" >> "$DESIGN/.phase-log"
}

done_count=0
for entry in "${PHASES[@]}"; do
  IFS='|' read -r file name skills <<<"$entry"
  path="$DESIGN/$file.md"
  num="${file%%-*}"
  if [[ ! -f "$path" ]]; then
    echo "[하네스] 현재 단계: $name  (완료 ${done_count}/10)"
    echo "  - 산출물 없음 → bash harness/scripts/start-phase.sh $num"
    echo "  - 지침: harness/PLAYBOOK.md 의 '$name' 절"
    [[ "$skills" != "-" ]] && echo "  - 사용할 스킬: $skills"
    log "current=$name missing"
    exit 0
  fi
  gates="$(open_gates "$path")"
  if [[ -n "$gates" ]]; then
    echo "[하네스] 현재 단계: $name  (완료 ${done_count}/10)"
    echo "  - 산출물: design/$file.md"
    [[ "$skills" != "-" ]] && echo "  - 사용할 스킬: $skills"
    echo "  - 남은 게이트:"
    if [[ "$BRIEF" == "--brief" ]]; then
      echo "$gates" | head -5 | sed 's/^/    /'
    else
      echo "$gates" | sed 's/^/    /'
      echo "  - 지침: harness/PLAYBOOK.md 의 '$name' 절"
    fi
    log "current=$name open_gates=$(echo "$gates" | wc -l | tr -d ' ')"
    exit 0
  fi
  done_count=$((done_count+1))
done
echo "[하네스] 모든 단계(P0~P9) 게이트 통과. 완성품 릴리스 완료 상태입니다."
log "all_done"
