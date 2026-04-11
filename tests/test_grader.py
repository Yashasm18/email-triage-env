import sys
import os

# Add repo root to path so 'grader' can be imported
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


def test_correct_label_gives_max_base_reward():
    action = make_action(label="urgent", summary="Server is down", reply="We are on it")
    ground_truth = {"label": "urgent"}
    reward = grade("easy", {}, action, ground_truth)
    assert reward >= 0.5, f"Expected >= 0.5, got {reward}"


def test_wrong_label_gives_partial_reward():
    action = make_action(label="work", summary=None, reply=None)
    ground_truth = {"label": "urgent"}
    reward = grade("easy", {}, action, ground_truth)
    assert 0.01 <= reward < 0.5, f"Expected partial reward, got {reward}"


def test_invalid_label_gives_minimal_reward():
    action = make_action(label="garbage_value", summary=None, reply=None)
    ground_truth = {"label": "urgent"}
    reward = grade("easy", {}, action, ground_truth)
    assert reward <= 0.2, f"Expected low reward, got {reward}"


def test_summary_adds_reward():
    action_no_summary = make_action(label="urgent", summary=None, reply=None)
    action_with_summary = make_action(
        label="urgent",
        summary="Production server is down and needs fix",
        reply=None
    )
    ground_truth = {"label": "urgent"}
    r1 = grade("medium", {}, action_no_summary, ground_truth)
    r2 = grade("medium", {}, action_with_summary, ground_truth)
    assert r2 > r1, "Summary should increase reward"


def test_reply_keywords_add_reward():
    action = make_action(
        label="urgent",
        summary="API is broken",
        reply="We are sorry for the issue, our team will investigate and fix it immediately"
    )
    ground_truth = {
        "label": "urgent",
        "reply_keywords": ["sorry", "investigate", "fix", "team"]
    }
    reward = grade("medium", {}, action, ground_truth)
    assert reward >= 0.4, f"Expected reward >= 0.4 with keywords, got {reward}"


def test_hard_task_correct_department_adds_reward():
    action = make_action(
        label="urgent",
        summary="Security breach detected",
        reply="We will escalate to security team to investigate and block the IPs",
        department="security"
    )
    ground_truth = {
        "label": "urgent",
        "department": "security",
        "reply_keywords": ["escalate", "security", "investigate", "block"]
    }
    reward = grade("hard", {}, action, ground_truth)
    assert reward >= 0.7, f"Expected high reward for hard task, got {reward}"


def test_hard_task_wrong_department_penalized():
    action = make_action(
        label="urgent",
        summary="Security breach detected",
        reply="We will escalate to security team to investigate and block the IPs",
        department="engineering"
    )
    ground_truth = {
        "label": "urgent",
        "department": "security",
        "reply_keywords": ["escalate", "security", "investigate", "block"]
    }
    reward = grade("hard", {}, action, ground_truth)
    assert reward < 0.9, "Wrong department should not give max reward"


def test_reward_is_always_clipped():
    action = make_action(
        label="urgent",
        summary="x" * 100,
        reply="y" * 100,
        department="security"
    )
    ground_truth = {"label": "urgent", "department": "security", "reply_keywords": []}
    reward = grade("hard", {}, action, ground_truth)
    assert 0.01 <= reward <= 0.99, f"Reward must be clipped to [0.01, 0.99], got {reward}"


def test_keyword_score_full_match():
    score = keyword_score("sorry for the issue we will fix and resolve", ["sorry", "fix", "resolve"])
    assert score == 1.0


def test_keyword_score_partial_match():
    score = keyword_score("sorry for the issue", ["sorry", "fix", "resolve"])
    assert 0 < score < 1.0


def test_keyword_score_no_match():
    score = keyword_score("completely unrelated text here", ["sorry", "fix", "resolve"])
    assert score == 0.0
