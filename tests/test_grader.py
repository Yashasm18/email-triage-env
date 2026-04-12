import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grader import grade, keyword_score, has_negation


def make_action(label=None, summary=None, reply=None, department=None):
    class Action:
        pass
    a = Action()
    a.label = label
    a.summary = summary
    a.reply = reply
    a.department = department
    return a


def test_correct_label_gives_high_reward():
    action = make_action(label="urgent")
    reward, feedback = grade("email-classification", {}, action, {"label": "urgent"})
    assert reward >= 0.4
    assert "Correct label" in feedback


def test_wrong_label_gives_low_reward():
    action = make_action(label="spam")
    reward, feedback = grade("email-classification", {}, action, {"label": "urgent"})
    assert reward < 0.4


def test_invalid_label_gives_minimal_reward():
    action = make_action(label="garbage")
    reward, feedback = grade("email-classification", {}, action, {"label": "urgent"})
    assert reward <= 0.15
    assert "Invalid label" in feedback


def test_negation_gives_minimum_reward():
    action = make_action(label="urgent", summary="This is not urgent at all", reply="not urgent")
    reward, feedback = grade("email-classification", {}, action, {"label": "urgent"})
    assert reward == 0.01
    assert "Negation" in feedback


def test_negation_in_reply_penalized():
    action = make_action(label="urgent", reply="This is not urgent, no need to escalate")
    reward, feedback = grade("urgency-detection", {}, action, {"label": "urgent"})
    assert reward == 0.01


def test_summary_adds_reward():
    action_no = make_action(label="urgent", summary=None, reply="We sincerely apologize")
    action_yes = make_action(label="urgent", summary="API is timing out in EMEA region causing revenue loss", reply="We sincerely apologize")
    gt = {"label": "urgent", "reply_keywords": ["investigate"]}
    r1, _ = grade("urgency-detection", {}, action_no, gt)
    r2, _ = grade("urgency-detection", {}, action_yes, gt)
    assert r2 > r1


def test_professional_reply_adds_reward():
    action = make_action(
        label="urgent",
        summary="Security breach detected on admin gateway",
        reply="We sincerely apologize and will immediately investigate and escalate to resolve this.",
        department="security"
    )
    gt = {"label": "urgent", "department": "security", "reply_keywords": ["investigate", "escalate"]}
    reward, feedback = grade("spam-filtering", {}, action, gt)
    assert reward >= 0.7


def test_correct_department_adds_reward():
    action = make_action(label="urgent", summary="breach", reply="We will investigate", department="security")
    gt = {"label": "urgent", "department": "security"}
    reward, feedback = grade("spam-filtering", {}, action, gt)
    assert reward >= 0.6
    assert "Correct department" in feedback


def test_wrong_department_penalized():
    action = make_action(label="urgent", summary="breach", reply="We will investigate", department="engineering")
    gt = {"label": "urgent", "department": "security"}
    reward, _ = grade("spam-filtering", {}, action, gt)
    assert reward < 0.8


def test_reward_always_clamped():
    action = make_action(label="urgent", summary="x" * 100, reply="sincerely apologize immediately escalate resolve assist investigate regards", department="security")
    gt = {"label": "urgent", "department": "security", "reply_keywords": []}
    reward, _ = grade("spam-filtering", {}, action, gt)
    assert 0.01 <= reward <= 0.99


def test_feedback_always_has_score():
    action = make_action(label="work")
    reward, feedback = grade("email-classification", {}, action, {"label": "work"})
    assert "Score:" in feedback


def test_keyword_score_full_match():
    assert keyword_score("sorry fix resolve", ["sorry", "fix", "resolve"]) == 1.0


def test_keyword_score_partial():
    score = keyword_score("sorry for the issue", ["sorry", "fix", "resolve"])
    assert 0 < score < 1.0


def test_keyword_score_no_match():
    assert keyword_score("hello world", ["sorry", "fix"]) == 0.0


def test_has_negation_detects_pattern():
    assert has_negation("this is not urgent", "urgent") is True


def test_has_negation_false_for_clean_text():
    assert has_negation("this is urgent please help", "urgent") is False
