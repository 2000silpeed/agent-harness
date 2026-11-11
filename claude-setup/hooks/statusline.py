#!/usr/bin/env python3
"""상태줄(선택): 모델 · 컨텍스트 사용률 · 프롬프트 캐시 상태 · 세션 비용(추정)을 한 줄로 보여 준다.

Claude Code가 stdin으로 주는 JSON을 읽어 한 줄을 출력한다. 훅이 아니라 설정의 statusLine에 연결한다.
모델 호출이 없어 토큰을 쓰지 않는다. 없는 필드와 null은 건너뛴다(prompt_cache는 첫 응답 뒤에 생긴다).
어떤 입력에도 죽지 않고 한 줄을 낸다.

출력 예: Opus | ctx 8% | cache warm 91% miss x2(tools_changed) | $0.01
"""
from __future__ import annotations

import json
import sys

WARN_PCT, HIGH_PCT = 60, 80  # (제안값) 이 선을 넘으면 !, !!를 붙인다. 도구가 권장하는 값이 아니다


def as_dict(value: object) -> dict:
    """dict가 아니면 빈 dict로 바꾼다."""
    return value if isinstance(value, dict) else {}


def is_number(value: object) -> bool:
    """숫자인지 본다(bool은 뺀다)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def render(data: dict) -> str:
    """상태줄 입력 객체에서 한 줄을 만든다.

    Args:
        data: 상태줄 입력 JSON 객체.

    Returns:
        ` | `로 이은 한 줄.
    """
    parts = [str(as_dict(data.get("model")).get("display_name") or "?")]

    used = as_dict(data.get("context_window")).get("used_percentage")
    if is_number(used):
        mark = "!!" if used >= HIGH_PCT else "!" if used >= WARN_PCT else ""
        parts.append(f"ctx {used:.0f}%{mark}")

    cache = as_dict(data.get("prompt_cache"))
    if cache:
        text = "cache warm" if cache.get("warm") else "cache cold"
        if is_number(cache.get("hit_ratio")):
            text += f" {cache['hit_ratio'] * 100:.0f}%"
        if is_number(cache.get("misses")) and cache["misses"] > 0:
            causes = as_dict(cache.get("last_miss_cause")).get("causes")
            cause = f"({causes[0]})" if isinstance(causes, list) and causes else ""
            text += f" miss x{cache['misses']}{cause}"
        parts.append(text)

    cost = as_dict(data.get("cost")).get("total_cost_usd")
    if is_number(cost):
        parts.append(f"${cost:.2f}")
    return " | ".join(parts)


def main() -> None:
    """stdin을 읽어 상태줄 한 줄을 출력한다. 입력이 깨져도 종료 코드는 0이다."""
    try:
        data = json.loads(sys.stdin.buffer.read())
        line = render(data) if isinstance(data, dict) else "statusline: unexpected input"
    except ValueError:
        line = "statusline: unreadable input"
    print(line)


if __name__ == "__main__":
    main()
