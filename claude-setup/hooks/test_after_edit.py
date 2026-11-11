#!/usr/bin/env python3
"""PostToolUse 훅: 코드 파일을 고치면 이름 규칙으로 짝지은 테스트만 돌린다.

모델 판단 없이 규칙으로 테스트를 고른다. 규칙은 TEST_RULES를 프로젝트에 맞게 고친다.
테스트가 실패하거나 짝 테스트가 없으면 exit 2로 stderr를 모델에 돌려준다.
Post 훅은 이미 실행된 수정을 되돌리지 못한다. 알려 줄 뿐이다.

고장 정책은 통과(fail open)다. 입력을 못 읽으면 조용히 건너뛴다. 최종 방어선은 CI다.
종료 코드: 0 = 통과 또는 건너뜀, 2 = 모델에 알릴 실패.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path


def paired_test(source: Path) -> Path:
    """소스 파일에 짝지은 테스트 경로를 만든다. 예: src/foo.py → tests/test_foo.py."""
    return Path("tests") / f"test_{source.stem}.py"


# (소스 확장자, 테스트 경로 만들기, 실행 명령). 실행 명령 뒤에 테스트 파일 경로가 붙는다.
TEST_RULES: list[tuple[str, Callable[[Path], Path], list[str]]] = [
    (".py", paired_test, [sys.executable, "-m", "pytest", "-q"]),
]
SKIP_DIRS = {".claude", "tests"}             # 이 폴더 아래 파일은 짝 테스트를 요구하지 않는다
SKIP_NAMES = {"__init__.py", "conftest.py"}  # 이 이름의 파일도 건너뛴다
TIMEOUT_SEC = 300                            # 설정의 훅 timeout(초)보다 작게 둔다
TAIL_CHARS = 3000                            # 모델에 돌려주는 출력 길이(훅 출력 상한은 10,000자)


def find_root(data: dict, target: Path) -> Path:
    """수정한 파일을 품은 루트를 고른다.

    워크트리 세션에서는 CLAUDE_PROJECT_DIR가 원래 체크아웃을 가리키므로, 파일을 품은 쪽
    (CLAUDE_PROJECT_DIR 또는 입력의 cwd)을 고른다.

    Args:
        data: 훅 입력 객체.
        target: 수정한 파일의 절대 경로.

    Returns:
        테스트를 찾고 실행할 루트.
    """
    candidates = [cand for cand in (os.environ.get("CLAUDE_PROJECT_DIR"), data.get("cwd")) if isinstance(cand, str) and cand]
    for cand in candidates:
        if target.is_relative_to(Path(cand).resolve()):
            return Path(cand).resolve()
    return Path(candidates[0] if candidates else ".").resolve()


def should_skip(target: Path, root: Path) -> bool:
    """짝 테스트를 요구하지 않는 파일인지 본다(테스트 파일 자신, 건너뛸 이름·폴더)."""
    if target.name in SKIP_NAMES or target.name.startswith("test_"):
        return True
    return target.is_relative_to(root) and bool(SKIP_DIRS & set(target.relative_to(root).parts[:-1]))


def main() -> int:
    """stdin의 훅 입력에서 수정한 파일을 읽어 짝 테스트를 돌린다."""
    try:
        data = json.loads(sys.stdin.buffer.read())
        raw = data["tool_input"].get("file_path") or ""
    except (ValueError, AttributeError, KeyError, TypeError):
        return 0  # 입력을 못 읽으면 건너뛴다
    if not isinstance(raw, str) or not raw:
        return 0
    target = Path(raw).resolve()
    root = find_root(data, target)
    if should_skip(target, root):
        return 0
    for suffix, to_test, command in TEST_RULES:
        if target.suffix != suffix:
            continue
        test_file = root / to_test(target)
        if not test_file.exists():
            print(f"test_after_edit: {target.name}에 짝지은 테스트({to_test(target)})가 없습니다.", file=sys.stderr)
            return 2
        try:
            result = subprocess.run(
                command + [str(test_file)], cwd=root, capture_output=True, text=True, timeout=TIMEOUT_SEC, check=False,
            )
        except subprocess.TimeoutExpired:
            print(f"test_after_edit: {test_file.name}이 {TIMEOUT_SEC}초 안에 끝나지 않았습니다.", file=sys.stderr)
            return 2
        except OSError as exc:
            print(f"test_after_edit: 테스트 명령을 실행하지 못했습니다: {exc}", file=sys.stderr)
            return 2
        if result.returncode != 0:
            tail = (result.stdout + result.stderr)[-TAIL_CHARS:]
            print(f"test_after_edit: {test_file.name} 실패\n{tail}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
