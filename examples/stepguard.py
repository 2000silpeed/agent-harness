"""도구가 순서를 강제하는 패턴 (docs/11-tool-enforced-ordering.md).

시스템 프롬프트에 "1→2→3→4 순서를 지켜라"라고 쓰는 대신, 각 도구가
현재 단계를 읽고 어긋나면 거절하며, 다음에 부를 도구를 반환한다.
프레임워크에 묶이지 않도록 순수 Python으로 작성했다. LangChain @tool 등으로 감싸 쓰면 된다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

# 단계 정의: 도구 이름 → 이 도구를 부를 수 있는 이전 단계 집합
FLOW: dict[str, set[str]] = {
    "classify_intent": {"start", "answer_faq", "ask_clarification", "decline", "handoff"},
    "select_candidates": {"classify_intent"},
    "ask_clarification": {"select_candidates"},
    "answer_faq": {"select_candidates"},
    "decline": {"classify_intent"},
    "handoff": {"classify_intent", "select_candidates", "ask_clarification"},
}
TERMINAL = {"answer_faq", "ask_clarification", "decline", "handoff"}


@dataclass
class SessionState:
    current_step: str = "start"
    history: list[str] = field(default_factory=list)  # 영속 저장 대상(파일/DB)


def guarded(name: str, next_tool: Callable[[Any], str | None]):
    """도구 함수를 순서 검사로 감싼다. next_tool(result)는 다음 도구 이름(또는 None=종료)을 고른다."""

    def wrap(fn: Callable[..., Any]):
        def tool(state: SessionState, *args: Any, **kwargs: Any) -> dict[str, Any]:
            allowed_prev = FLOW[name]
            if state.current_step not in allowed_prev:
                return {
                    "ok": False,
                    "error": "out_of_order",
                    "message": f"'{name}'은 지금 호출할 수 없습니다. 현재 단계: {state.current_step}",
                    "next_tool": expected_next(state),
                }
            result = fn(*args, **kwargs)
            state.current_step = name
            state.history.append(name)
            nxt = None if name in TERMINAL else next_tool(result)
            return {"ok": True, "result": result, "next_tool": nxt,
                    "message": "끝났어, 이번 턴을 종료해" if nxt is None else f"다음은 {nxt}"}

        tool.__name__ = name
        return tool

    return wrap


def expected_next(state: SessionState) -> list[str]:
    return sorted(t for t, prev in FLOW.items() if state.current_step in prev)


# ---- 예시 도구 (실제 구현은 모델·데이터 호출로 대체) ----
FAQ = {"환불": "결제 후 7일 이내 환불 가능합니다.", "배송": "평균 2일 소요됩니다."}


@guarded("classify_intent", lambda r: "select_candidates" if r == "faq" else "decline")
def classify_intent(utterance: str) -> str:
    return "faq" if any(k in utterance for k in FAQ) else "other"


@guarded("select_candidates", lambda r: "answer_faq" if len(r) == 1 else "ask_clarification")
def select_candidates(utterance: str) -> list[str]:
    return [k for k in FAQ if k in utterance]


@guarded("answer_faq", lambda r: None)
def answer_faq(key: str) -> str:
    return FAQ[key]


@guarded("ask_clarification", lambda r: None)
def ask_clarification(candidates: list[str]) -> str:
    return f"어떤 것을 물어보셨나요? ({', '.join(candidates) or '없음'})"


@guarded("decline", lambda r: None)
def decline() -> str:
    return "FAQ 범위 밖의 문의입니다. 상담원을 연결해 드릴까요?"


@guarded("handoff", lambda r: None)
def handoff() -> str:
    return "상담원에게 연결합니다."


if __name__ == "__main__":
    s = SessionState()
    print(answer_faq(s, "환불"))            # 거절: classify_intent부터
    print(classify_intent(s, "환불 되나요?"))
    print(select_candidates(s, "환불 되나요?"))
    print(answer_faq(s, "환불"))
