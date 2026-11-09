#!/usr/bin/env python3
"""PreToolUse 훅: 승인된 계획 없이 코드를 바꾸지 못하게 막는다.

stdin으로 받은 훅 입력(JSON)에서 수정 대상 파일을 읽고,
design/plans/*.md 중 `status: approved`인 계획이 없으면 exit 2로 차단한다.
design/, harness/, 문서(.md) 수정은 계획 없이도 허용한다.
"""
import json
import os
import sys
from pathlib import Path

ALLOW_PREFIXES = ("design/", "harness/", ".claude/")
ALLOW_SUFFIXES = (".md",)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("plan_gate: 훅 입력을 읽지 못해 차단합니다(fail closed).", file=sys.stderr)
        return 2
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
    target = (data.get("tool_input") or {}).get("file_path") or ""
    try:
        rel = Path(target).resolve().relative_to(root).as_posix()
    except ValueError:
        rel = target
    if rel.startswith(ALLOW_PREFIXES) or rel.endswith(ALLOW_SUFFIXES):
        return 0
    plans = sorted((root / "design" / "plans").glob("*.md"))
    approved = [p for p in plans if "status: approved" in p.read_text(encoding="utf-8", errors="ignore")]
    if approved:
        return 0
    print(
        f"plan_gate: 승인된 계획이 없어 '{rel}' 수정을 막았습니다. "
        "plan-review 스킬로 design/plans/에 계획을 쓰고 리뷰·승인(status: approved)을 받은 뒤 다시 시도하세요.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
