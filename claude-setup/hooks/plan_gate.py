#!/usr/bin/env python3
"""PreToolUse 훅: 사람이 승인한 계획의 범위 안에서만 코드를 바꾸게 한다.

stdin으로 받은 훅 입력(JSON)에서 수정 대상 경로를 읽어 아래 순서로 판정한다.

    1. 세션 임시 폴더(입력의 scratchpad_dir) 아래        → 통과
    2. 프로젝트 밖                                       → 차단
    3. 보호 경로(승인 기록, 훅 코드, 설정, 추가 목록)    → 차단. 계획에 적혀 있어도 막는다
    4. design/ 아래 또는 마크다운(.md)                   → 통과. 계획·설계 문서는 계획 없이 쓴다
    5. 그 밖(코드): status가 approved인 계획이 정확히 하나이고, 그 계획의 승인 기록
       (design/approvals/<plan_id>.json)의 version·해시가 지금 계획과 같고,
       경로가 계획의 `## 수정 대상` 안이면               → 통과. 아니면 차단

계획 파일의 `status: approved` 글자만으로는 통과하지 않는다. 승인 기록은 사람이 자기 터미널에서
approve_plan.py를 실행해야 생긴다.

종료 코드: 0 = 통과, 2 = 차단(사유는 stderr). 깨진 입력이나 내부 오류처럼 판정하지 못한
경우도 2로 끝낸다(fail closed). 종료 코드 1은 차단이 아니므로 쓰지 않는다.
"""
from __future__ import annotations

import contextlib
import json
import sys
from pathlib import Path

try:
    import plan_lib
except Exception as exc:  # noqa: BLE001 - 공용 모듈이 없거나 깨져도 exit 1(통과)이 아니라 exit 2(차단)
    print(f"plan_gate[gate.failure]: plan_lib를 불러오지 못해 차단합니다(fail closed): {exc!r}", file=sys.stderr)
    sys.exit(2)

PATH_KEYS = ("file_path", "notebook_path")  # Edit·Write는 file_path, NotebookEdit는 notebook_path
FREE_PREFIXES = ("design/",)                # 계획 없이 쓸 수 있는 폴더(보호 경로 검사가 먼저다)
FREE_SUFFIXES = (".md",)                    # 계획 없이 쓸 수 있는 확장자
APPROVE_HINT = "사람이 자기 터미널에서 `python3 .claude/hooks/approve_plan.py <plan_id>`를 실행해야 승인됩니다."


class Block(Exception):
    """차단 판정.

    Attributes:
        rule: 차단 규칙 ID(기록과 시험에서 구분하는 데 쓴다).
        message: 모델에 돌려줄 사유와 다음 행동.
    """

    def __init__(self, rule: str, message: str) -> None:
        """규칙 ID와 사유를 담는다."""
        super().__init__(message)
        self.rule = rule
        self.message = message


def target_paths(data: dict) -> list[str]:
    """훅 입력에서 수정 대상 경로를 꺼낸다.

    Args:
        data: 훅 입력 객체.

    Returns:
        경로 문자열 목록(1개 이상).

    Raises:
        Block: tool_input이 객체가 아니거나, 경로가 없거나 문자열이 아니면.
    """
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        raise Block("gate.bad_input", "훅 입력에 tool_input 객체가 없습니다.")
    raws = [tool_input[key] for key in PATH_KEYS if key in tool_input]
    if not raws or not all(isinstance(raw, str) and raw.strip() for raw in raws):
        raise Block(
            "gate.bad_input",
            f"훅 입력에서 수정 대상 경로({', '.join(PATH_KEYS)})를 찾지 못했습니다. "
            "이 게이트는 Edit·Write·NotebookEdit 호출에만 연결합니다.",
        )
    return raws


def resolve_target(raw: str, data: dict) -> Path:
    """수정 대상 경로를 심볼릭 링크까지 푼 절대 경로로 바꾼다. 상대 경로는 입력의 cwd 기준이다."""
    path = Path(raw).expanduser()
    if not path.is_absolute():
        cwd = data.get("cwd")
        path = Path(cwd if isinstance(cwd, str) and cwd else ".") / path
    return path.resolve()


def approved_plan(root: Path, rel: str) -> plan_lib.Plan:
    """유효한 승인 기록이 있는 계획 하나를 찾는다.

    Args:
        root: 프로젝트 루트.
        rel: 지금 고치려는 경로(메시지용).

    Returns:
        status가 approved이고 승인 기록의 version·해시가 맞는 유일한 계획.

    Raises:
        Block: 승인된 계획이 없거나, 둘 이상이거나, 승인 기록이 없거나 낡았으면.
    """
    plans, unreadable = plan_lib.list_plans(root)
    approved = [plan for plan in plans if plan.status == "approved"]
    if not approved:
        seen = ", ".join(f"{plan.path.stem}({plan.status or '상태 없음'})" for plan in plans) or "없음"
        broken = f" 읽지 못한 계획 파일: {', '.join(unreadable)}." if unreadable else ""
        raise Block(
            "plan.approved_required",
            f"승인된 계획이 없어 '{rel}' 수정을 막았습니다. 현재 계획: {seen}.{broken} "
            f"{plan_lib.PLANS_DIR}/<plan_id>.md에 계획을 쓰고 리뷰를 받은 뒤 사람에게 승인을 요청하세요. {APPROVE_HINT}",
        )
    if len(approved) > 1:
        names = ", ".join(plan.path.stem for plan in approved)
        raise Block(
            "plan.multiple_approved",
            f"status가 approved인 계획이 여러 개라 '{rel}' 수정을 막았습니다({names}). "
            "끝난 계획은 done, 바뀐 계획은 superseded로 정리해 하나만 남기세요.",
        )
    plan = approved[0]
    problem = plan_lib.approval_problem(root, plan)
    if problem:
        rule, reason = problem
        raise Block(
            rule,
            f"계획 '{plan.path.stem}'의 승인이 유효하지 않아 '{rel}' 수정을 막았습니다: {reason}. "
            "계획을 고쳤다면 version을 올리고 status를 in_review로 되돌려 다시 리뷰받은 뒤 사람에게 재승인을 요청하세요. "
            f"{APPROVE_HINT} 승인 기록은 직접 만들거나 고칠 수 없습니다.",
        )
    return plan


def check(data: object) -> None:
    """훅 입력 하나를 판정한다. 통과면 그냥 돌아오고, 차단이면 Block을 낸다.

    Args:
        data: stdin에서 읽은 JSON 값.

    Raises:
        Block: 차단 사유가 있을 때.
    """
    if not isinstance(data, dict):
        raise Block("gate.bad_input", "훅 입력이 JSON 객체가 아닙니다.")
    raws = target_paths(data)
    root = plan_lib.project_root()
    scratch = data.get("scratchpad_dir")
    scratch_dir = Path(scratch).resolve() if isinstance(scratch, str) and scratch else None
    protected = plan_lib.protected_patterns(root)
    plan: plan_lib.Plan | None = None

    for raw in raws:
        target = resolve_target(raw, data)
        if scratch_dir and target.is_relative_to(scratch_dir):
            continue
        if not target.is_relative_to(root):
            raise Block(
                "path.outside_project",
                f"'{target}'은 프로젝트({root}) 밖이라 막았습니다. 이 게이트는 프로젝트 밖 쓰기를 허용하지 않습니다.",
            )
        rel = target.relative_to(root).as_posix()
        if plan_lib.is_protected(rel, protected):
            raise Block(
                "protected_path",
                f"'{rel}'은 보호 경로(게이트 코드·설정·승인 기록·보호 목록)라 막았습니다. "
                "계획에 적혀 있어도 에이전트는 고칠 수 없습니다. 필요한 변경은 사람에게 요청하세요.",
            )
        if rel.startswith(FREE_PREFIXES) or rel.lower().endswith(FREE_SUFFIXES):
            continue
        plan = plan or approved_plan(root, rel)
        entries = plan_lib.scope_entries(plan.body)
        bad = [entry for entry in entries if plan_lib.scope_entry_problem(entry)]
        if bad:
            raise Block("plan.scope_invalid", f"계획 '{plan.plan_id}'의 수정 대상에 형식이 틀린 경로가 있습니다: {', '.join(bad)}.")
        if not plan_lib.in_scope(rel, entries):
            raise Block(
                "scope.outside_plan",
                f"'{rel}'은 승인된 계획 '{plan.plan_id}' v{plan.version}의 수정 대상에 없어 막았습니다. "
                "이 파일이 꼭 필요하면 여기서 멈추고, 계획의 version을 올려 수정 대상에 추가한 뒤 "
                f"다시 리뷰받고 사람에게 재승인을 요청하세요. {APPROVE_HINT}",
            )


def block(rule: str, message: str) -> int:
    """차단 사유를 stderr에 쓰고 종료 코드 2를 돌려준다. 출력이 실패해도 2다."""
    with contextlib.suppress(Exception):  # 사유를 못 써도 차단은 유지한다
        print(f"plan_gate[{rule}]: {message}", file=sys.stderr)
    return 2


def main() -> int:
    """stdin의 훅 입력을 판정해 종료 코드를 돌려준다(0 통과, 2 차단)."""
    try:
        check(json.loads(sys.stdin.buffer.read()))
    except Block as blocked:
        return block(blocked.rule, blocked.message)
    except Exception as exc:  # noqa: BLE001 - 깨진 입력·예상 못 한 오류도 통과시키지 않는다
        return block("gate.failure", f"판정하지 못해 차단합니다(fail closed): {exc!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
