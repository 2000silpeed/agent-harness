#!/usr/bin/env python3
"""계획 형식 검사: 계획을 리뷰에 올리기 전(draft → in_review)에 돌린다.

사용법:
    python3 .claude/hooks/check_plan.py              # 계획 목록과 승인 상태
    python3 .claude/hooks/check_plan.py <plan_id>    # design/plans/<plan_id>.md 형식 검사

읽기만 한다. 에이전트가 실행해도 된다. 형식만 보고 내용이 옳은지는 보지 않는다.
종료 코드: 0 = 통과, 1 = 문제 있음 또는 계획을 읽지 못함.
"""
from __future__ import annotations

import sys

import plan_lib


def show_list() -> int:
    """계획마다 version, status, 승인 기록 대조 결과를 한 줄씩 출력한다."""
    root = plan_lib.project_root()
    plans, unreadable = plan_lib.list_plans(root)
    for plan in plans:
        problem = plan_lib.approval_problem(root, plan)
        approval = "승인 기록 유효" if problem is None else f"승인 없음: {problem[1]}"
        print(f"{plan.path.stem}  v{plan.meta.get('version', '?')}  {plan.status or '?'}  [{approval}]")
    for note in unreadable:
        print(f"읽지 못함: {note}")
    if not plans and not unreadable:
        print(f"{plan_lib.PLANS_DIR}/에 계획이 없습니다.")
    return 0


def check_one(plan_id: str) -> int:
    """계획 하나의 형식 문제를 출력한다."""
    root = plan_lib.project_root()
    if not plan_lib.PLAN_ID_PATTERN.match(plan_id):
        print(f"check_plan: plan_id 형식이 틀립니다: {plan_id!r}", file=sys.stderr)
        return 1
    path = root / plan_lib.PLANS_DIR / f"{plan_id}.md"
    try:
        plan = plan_lib.read_plan(path)
    except (OSError, plan_lib.PlanError) as exc:
        print(f"check_plan: {path}를 읽지 못했습니다: {exc}", file=sys.stderr)
        return 1
    problems = plan_lib.format_problems(plan, root)
    if problems:
        print(f"check_plan: {plan_id} v{plan.meta.get('version', '?')} 형식 문제 {len(problems)}건", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"check_plan: {plan_id} v{plan.version} 형식 검사 통과 (본문 sha256 {plan.sha256[:12]}…)")
    return 0


def main(argv: list[str]) -> int:
    """인자에 따라 목록 출력 또는 형식 검사를 한다."""
    if len(argv) > 2:
        print(__doc__, file=sys.stderr)
        return 1
    return check_one(argv[1]) if len(argv) == 2 else show_list()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
