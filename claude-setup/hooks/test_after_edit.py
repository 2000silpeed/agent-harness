#!/usr/bin/env python3
"""PostToolUse 훅: 코드 파일을 고치면 이름 규칙으로 짝지은 테스트만 돌린다.

LLM 판단 없이 규칙으로 테스트를 고른다. 규칙은 TEST_RULES를 프로젝트에 맞게 고친다.
테스트가 실패하면 exit 2로 결과를 모델에 돌려준다. Post 훅은 이미 실행된 수정을 되돌리지 않는다.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# (소스 확장자, 테스트 경로 만들기, 실행 명령)
TEST_RULES = [
    (".py", lambda p: Path("tests") / f"test_{p.stem}.py", ["python", "-m", "pytest", "-q"]),
]
TIMEOUT_SEC = 300


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # 입력을 못 읽으면 검사를 건너뛴다. 최종 방어선은 CI다.
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
    target = Path((data.get("tool_input") or {}).get("file_path") or "")
    for suffix, to_test, cmd in TEST_RULES:
        if target.suffix != suffix or target.name.startswith("test_"):
            continue
        test_file = root / to_test(target)
        if not test_file.exists():
            print(f"test_after_edit: {target.name}에 짝지은 테스트({to_test(target)})가 없습니다.", file=sys.stderr)
            return 2
        try:
            result = subprocess.run(cmd + [str(test_file)], cwd=root, capture_output=True, text=True, timeout=TIMEOUT_SEC)
        except subprocess.TimeoutExpired:
            print(f"test_after_edit: {test_file.name}이 {TIMEOUT_SEC}초 안에 끝나지 않았습니다.", file=sys.stderr)
            return 2
        if result.returncode != 0:
            tail = (result.stdout + result.stderr)[-3000:]
            print(f"test_after_edit: {test_file.name} 실패\n{tail}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
