#!/usr/bin/env python3
"""계획 승인: 사람이 자기 터미널에서 실행해 승인 기록을 남긴다.

사용법(프로젝트 루트에서):
    python3 .claude/hooks/approve_plan.py <plan_id> [--by 이름]

하는 일:
    1. design/plans/<plan_id>.md의 형식을 검사한다(필수 구역, 수정 대상 경로, 보호 경로 등).
    2. status가 in_review이고 `## 리뷰 이력`에 현재 version의 APPROVE 판정이 있는지 본다.
    3. 수정 대상·위험 표시를 화면에 보여 주고 확인(yes)을 받는다.
    4. 계획 머리말의 status를 approved로 바꾸고, 승인 기록
       design/approvals/<plan_id>.json = {plan_id, version, plan_sha256, reviewer_verdict,
       approved_by, approved_at}을 쓴다.

plan_gate.py는 이 기록의 version·해시가 지금 계획과 같을 때만 코드 수정을 통과시킨다.
계획 본문을 고치면 해시가 달라져 승인이 무효가 되므로 다시 실행해야 한다.

에이전트가 실행하면 자기 승인이 된다. 그래서 터미널(TTY)이 아니거나 에이전트 셸로 보이면
(환경 변수 CLAUDECODE) 거절한다. 이 확인은 방지턱이지 보장이 아니다. 권한 설정에서 이 스크립트
실행과 design/approvals/ 쓰기를 함께 막아 둔다(README 참고).

종료 코드: 0 = 승인 기록 작성, 1 = 거절(사유는 stderr).
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import plan_lib

AGENT_ENV_VARS = ("CLAUDECODE",)  # 에이전트가 띄운 셸에 설정되는 환경 변수(쓰는 도구에 맞게 추가)
APPROVABLE = ("in_review", "approved")  # approved는 사람이 같은 version을 다시 승인하는 경우


def refuse(message: str) -> int:
    """거절 사유를 stderr에 쓰고 종료 코드 1을 돌려준다."""
    print(f"approve_plan: {message}", file=sys.stderr)
    return 1


def approval_blockers(plan: plan_lib.Plan, root: Path) -> list[str]:
    """승인할 수 없는 이유를 모은다(형식 문제, 상태, 리뷰 판정, 이전 승인과의 version 관계, 다른 승인 계획).

    Args:
        plan: 승인하려는 계획.
        root: 프로젝트 루트.

    Returns:
        이유 목록. 비어 있으면 승인할 수 있다.
    """
    blockers = plan_lib.format_problems(plan, root)
    if plan.status not in APPROVABLE:
        blockers.append(f"status가 '{plan.status}'입니다. 리뷰를 거친 계획(in_review)만 승인합니다")
    verdict = plan_lib.review_verdict(plan)
    if verdict != "APPROVE":
        blockers.append(
            f"'## 리뷰 이력'에 v{plan.version}의 APPROVE 판정 줄이 없습니다(현재: {verdict or '없음'}). "
            "예: '- v1: APPROVE — 지적 없음'"
        )
    try:
        previous = plan_lib.read_approval(root, plan.plan_id)
    except plan_lib.PlanError:
        previous = None  # 깨진 기록은 새 기록으로 덮어쓴다
    if previous and plan.version is not None and type(previous["version"]) is int:
        if previous["version"] > plan.version:
            blockers.append(f"이미 v{previous['version']}이 승인돼 있습니다. version은 뒤로 갈 수 없습니다")
        elif previous["version"] == plan.version and previous["plan_sha256"] != plan.sha256:
            blockers.append(
                f"version {plan.version}은 다른 본문으로 이미 승인됐습니다. 본문을 고쳤다면 version을 올리고 "
                "다시 리뷰받은 뒤 승인합니다"
            )
    plans, _ = plan_lib.list_plans(root)
    others = [other.path.stem for other in plans if other.status == "approved" and other.path != plan.path]
    if others:
        blockers.append(f"이미 approved인 다른 계획이 있습니다({', '.join(others)}). done 또는 superseded로 정리한 뒤 승인합니다")
    return blockers


def show_summary(plan: plan_lib.Plan) -> None:
    """사람이 확인할 내용을 출력한다. 화면에 보이는 것은 게이트가 실제로 읽는 값이다."""
    sections = plan_lib.split_sections(plan.body)
    print(f"계획      {plan.plan_id}  v{plan.version}  risk={plan.meta.get('risk')}  ({plan.path})")
    print(f"본문 해시 {plan.sha256}")
    print("수정 대상 (게이트가 허용할 경로)")
    for entry in plan_lib.scope_entries(plan.body):
        print(f"  {entry!r}")
    print("위험 표시")
    for line in sections.get(plan_lib.section_key("위험 표시"), "").splitlines():
        print(f"  {line}")


def write_record(root: Path, plan: plan_lib.Plan, approved_by: str) -> Path:
    """승인 기록을 임시 파일에 쓴 뒤 제자리로 옮긴다(쓰다 만 파일이 남지 않게)."""
    record = {
        "plan_id": plan.plan_id,
        "version": plan.version,
        "plan_sha256": plan.sha256,
        "reviewer_verdict": "APPROVE",
        "approved_by": approved_by,
        "approved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    path = plan_lib.approval_path(root, plan.plan_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".json.tmp")
    temp.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return path


def main() -> int:
    """인자를 읽고, 검사하고, 확인받고, 승인 기록을 쓴다."""
    parser = argparse.ArgumentParser(description="계획을 승인하고 승인 기록을 남긴다(사람이 실행).")
    parser.add_argument("plan_id", help="design/plans/<plan_id>.md의 plan_id")
    parser.add_argument("--by", default="", help="승인자 이름(기본: 로그인 사용자 이름)")
    args = parser.parse_args()

    if any(os.environ.get(name) for name in AGENT_ENV_VARS) or not sys.stdin.isatty():
        return refuse(
            "사람이 자기 터미널에서 직접 실행해야 합니다(에이전트 셸이거나 입력이 터미널이 아닙니다). "
            "에이전트는 이 스크립트를 실행하지 않고 사용자에게 실행을 요청합니다."
        )
    if not plan_lib.PLAN_ID_PATTERN.match(args.plan_id):
        return refuse(f"plan_id 형식이 틀립니다: {args.plan_id!r}")

    root = plan_lib.project_root()
    path = root / plan_lib.PLANS_DIR / f"{args.plan_id}.md"
    try:
        original = path.read_text(encoding="utf-8")
        plan = plan_lib.Plan(path, *plan_lib.parse_plan_text(original))
    except (OSError, plan_lib.PlanError) as exc:
        return refuse(f"{path}를 읽지 못했습니다: {exc}")

    blockers = approval_blockers(plan, root)
    if blockers:
        return refuse("승인할 수 없습니다.\n" + "\n".join(f"  - {blocker}" for blocker in blockers))

    show_summary(plan)
    if input("이 계획을 승인합니까? 승인하려면 yes: ").strip() != "yes":
        return refuse("승인하지 않았습니다. 바뀐 것은 없습니다.")
    if path.read_text(encoding="utf-8") != original:
        return refuse("확인하는 사이 계획 파일이 바뀌었습니다. 다시 실행해 내용을 확인하세요.")

    updated = plan_lib.with_status(original, "approved")
    if plan_lib.body_sha256(plan_lib.parse_plan_text(updated)[1]) != plan.sha256:
        return refuse("status를 바꾸면 본문 해시가 달라집니다. 계획 파일의 머리말을 확인하세요.")
    path.write_text(updated, encoding="utf-8")
    record_path = write_record(root, plan, args.by or getpass.getuser())
    print(f"approve_plan: {plan.plan_id} v{plan.version} 승인 기록을 썼습니다 → {record_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
