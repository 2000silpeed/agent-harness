from stepguard import SessionState, answer_faq, classify_intent, select_candidates, decline


def test_rejects_out_of_order():
    s = SessionState()
    r = answer_faq(s, "환불")
    assert r["ok"] is False and r["error"] == "out_of_order"
    assert r["next_tool"] == ["classify_intent"]
    assert s.current_step == "start"


def test_happy_path_returns_next_tool():
    s = SessionState()
    assert classify_intent(s, "환불 되나요?")["next_tool"] == "select_candidates"
    assert select_candidates(s, "환불 되나요?")["next_tool"] == "answer_faq"
    r = answer_faq(s, "환불")
    assert r["ok"] and r["next_tool"] is None
    assert s.history == ["classify_intent", "select_candidates", "answer_faq"]


def test_non_faq_goes_to_decline():
    s = SessionState()
    assert classify_intent(s, "날씨 어때")["next_tool"] == "decline"
    assert decline(s)["ok"]
    # 새 턴은 다시 classify_intent부터
    assert classify_intent(s, "배송 언제")["ok"]
