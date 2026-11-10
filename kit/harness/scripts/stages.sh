#!/usr/bin/env bash
# 단계 정의: 번호|산출물|이름|시작에 필요한 단계|쓸 스킬
# phase.sh 와 start-phase.sh 가 함께 읽는다. 순서와 병렬 관계의 근거는 harness/METHOD.md 1절.
STAGES=(
  "0|00-brief|S0 범위·기반 결정||project-kickoff, serving-plan"
  "1|01-eval|S1 시험지·채점기|0|golden-dataset, agent-eval"
  "2|02-baseline|S2 뼈대·관측·기준선|0|workflow-to-architecture"
  "3|03-context|S3 컨텍스트·메모리|2|-"
  "4|04-tools-skills|S4 도구·스킬|2|skill-authoring, tool-design-review"
  "5|05-control|S5 실행 제어|2|hook-design, plan-review"
  "6|06-improve|S6 자기개선|1 2 3 5|agent-eval"
  "7|07-optimize|S7 최적화|3 4 5|optimize-agent, serving-plan"
  "8|08-release|S8 배포·운영|6 7|agent-eval"
)

# 완료 기준 절의 미체크 항목 출력
open_gates() { awk '/^## 완료 기준/{g=1;next} /^## /{g=0} g && /^- \[ \]/' "$1"; }

# 단계 상태: done / doing / none
stage_state() {  # $1=design 폴더, $2=산출물 이름
  local f="$1/$2.md"
  [[ -f "$f" ]] || { echo none; return; }
  [[ -z "$(open_gates "$f")" ]] && echo done || echo doing
}
