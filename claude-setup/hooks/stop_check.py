#!/usr/bin/env python3
"""Stop 훅(선택): 끝내기 전에 정한 검사 명령을 돌리고, 실패하면 exit 2로 계속 일하게 한다.

입력의 stop_hook_active가 true면(이미 이 훅 때문에 이어서 일하는 중) 다시 막지 않는다.
그래서 두 번째로 끝낼 때는 검사하지 않는다. 그때의 통과는 "고쳐졌다"는 증거가 아니다.
검사 명령은 CHECK_CMD를 프로젝트에 맞게 고친다. Stop은 응답이 끝날 때마다 발동하므로
명령이 느리면 응답마다 그만큼 기다린다.

고장 정책은 통과(fail open)다. 입력을 못 읽거나 검사 명령 자체가 실행되지 않으면 보내 준다.
모델이 고칠 수 없는 고장으로 끝내기를 막지 않기 위해서다. 같은 검사를 CI에도 둔다.
종료 코드: 0 = 끝내도 됨, 2 = 검사 실패(사유는 stderr).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

CHECK_CMD = [sys.executable, "-m", "pytest", "-q"]
TIMEOUT_SEC = 300   # 설정의 훅 timeout(초)보다 작게 둔다
TAIL_CHARS = 3000   # 모델에 돌려주는 출력 길이


def main() -> int:
    """stdin의 훅 입력을 읽고 검사 명령을 돌린다."""
    try:
        data = json.loads(sys.stdin.buffer.read())
    except ValueError:
        return 0
    if not isinstance(data, dict) or data.get("stop_hook_active"):
        return 0
    cwd = data.get("cwd")
    root = os.environ.get("CLAUDE_PROJECT_DIR") or (cwd if isinstance(cwd, str) and cwd else ".")
    try:
        result = subprocess.run(CHECK_CMD, cwd=root, capture_output=True, text=True, timeout=TIMEOUT_SEC, check=False)
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"stop_check: 검사를 끝내지 못했습니다: {exc}", file=sys.stderr)
        return 0
    if result.returncode != 0:
        tail = (result.stdout + result.stderr)[-TAIL_CHARS:]
        print(f"stop_check: 검사가 실패했습니다. 고친 뒤 끝내세요.\n{tail}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
