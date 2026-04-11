import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grader import grade, keyword_score


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
    ground_truth = {"label": "urgent"}
    reward, feedback = grade("email-classification", {}, action, ground_truth)
    assert reward >= 0.4, f"Expected >= 0.4, got {reward}"
    assert "Correct label" in feedback


def test_wrong_label_gives_low_reward():
    action = make_action(label="work")
    ground_truth = {"label": "urgent"}
    reward, feedback = grade("email-classification", {}, action, ground_truth)
    assert 0.01 <= reward < 0.5, f"Expected partial reward, got {reward}"


def test_invalid_label_gives_minimal_reward():
    action = make_action(label="garbage_value")
    ground_truth = {"label": "urgent"}
    reward, feedback = grade("email-classification", {}, action, ground_truth)
    assert reward <= 0.2, f"Expected low reward, got {reward}"
    assert "Invalid label" in feedback


def test_urgency_detection_with_reply():
    action = make_action(
        label="urgent",
        summary="API is timing out in EMEA region",
        reply="We sincerely apologize, our team will investigate and rollback immediately"
    )
    ground_truth = {
        "label": "urgent",
        "reply_keywords": ["hotfix", "investigate", "rollback", "apologize"]
    }
    reward, feedback = grade("urgency-detection", {}, action, ground_truth)
    assert reward >= 0.4, f"Expected reward >= 0.4, got {reward}"


def test_urgency_detection_no_reply_penalized():
    action = make_action(label="urgent", summary=None, reply=None)
    ground_truth = {"label": "urgent", "reply_keywords": ["hotfix", "investigate"]}
    reward, feedback = grade("urgency-detection", {}, action, ground_truth)
    assert "No reply" in feedback or "missing" in feedback


def test_spam_filtering_correct_department():
    action = make_action(
        label="urgent",
        summary="Security breach detected",
        reply="We will sincerely investigate and apologize for this immediately",
        department="security"
    )
    ground_truth = {
        "label": "urgent",
        "department": "security",
        "reply_keywords": ["incident", "protocol", "audit", "security"]
    }
    reward, feedback = grade("spam-filtering", {}, action, ground_truth)
    assert reward >= 0.7, f"Expected high reward, got {reward}"
    assert "Correct department" in feedback


def test_spam_filtering_wrong_department():
    action = make_action(
        label="urgent",
        summary="Security breach detected",
        reply="We will sincerely investigate immediately",
        department="engineering"
    )
    ground_truth = {
        "label": "urgent",
        "department": "security",
        "reply_keywords": ["incident", "security"]
    }
    reward, feedback = grade("spam-filtering", {}, action, ground_truth)
    assert reward < 0.9, "Wrong department should not give max reward"


def test_reward_always_clipped():
    action = make_action(label="urgent", summary="x" * 100, reply="y" * 100, department="security")
    ground_truth = {"label": "urgent", "department": "security", "reply_keywords": []}
    reward, feedback = grade("spam-filtering", {}, action, ground_truth)
    assert 0.01 <= reward <= 0.99


def test_feedback_always_present():
    action = make_action(label="spam")
    ground_truth = {"label": "spam"}
    reward, feedback = grade("email-classification", {}, action, ground_truth)
    assert isinstance(feedback, str)
    assert "Score:" in feedback


def test_keyword_score_full_match():
    score = keyword_score("sorry we will fix and resolve", ["sorry", "fix", "resolve"])
    assert score == 1.0


def test_keyword_score_partial_match():
    score = keyword_score("sorry for the issue", ["sorry", "fix", "resolve"])
    assert 0 < score < 1.0


def test_keyword_score_no_match():
    score = keyword_score("completely unrelated text", ["sorry", "fix", "resolve"])
    assert score == 0.0
