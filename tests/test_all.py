import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "server"))

import pytest
from grader import grade
from models import MyAction, MyObservation
from my_env_environment import MyEnvironment


# ══════════════════════════════════════════════════════════════════════════════
# grader.py tests
# ══════════════════════════════════════════════════════════════════════════════

class TestGrader:

    def test_perfect_easy_score(self):
        action = MyAction(label="urgent", summary="", reply="", department=None)
        gt = {"label": "urgent"}
        reward = grade("email-classification", {}, action, gt)
        assert abs(reward - 0.51) < 0.02

    def test_correct_label_only(self):
        action = MyAction(label="spam", summary=None, reply=None, department=None)
        gt = {"label": "spam"}
        reward = grade("email-classification", {}, action, gt)
        assert reward >= 0.50

    def test_wrong_label_gives_low_reward(self):
        action = MyAction(label="personal", summary=None, reply=None, department=None)
        gt = {"label": "spam"}
        reward = grade("email-classification", {}, action, gt)
        assert reward < 0.20

    def test_partial_label_credit(self):
        action = MyAction(label="urgent", summary=None, reply=None, department=None)
        gt = {"label": "work"}
        reward = grade("urgency-detection", {}, action, gt)
        assert reward >= 0.10

    def test_summary_bonus(self):
        action = MyAction(label="work", summary="Customer wants pricing info", reply=None, department=None)
        gt = {"label": "work"}
        reward = grade("urgency-detection", {}, action, gt)
        assert reward >= 0.70

    def test_reply_keyword_coverage(self):
        action = MyAction(
            label="urgent",
            summary="Order not received",
            reply="We are sorry for the delay. We will help you track and resolve your order.",
            department=None,
        )
        gt = {
            "label": "urgent",
            "reply_keywords": ["sorry", "order", "track", "help", "resolve"],
        }
        reward = grade("urgency-detection", {}, action, gt)
        assert reward >= 0.80

    def test_department_bonus_hard_task_only(self):
        action = MyAction(
            label="urgent",
            summary="Double charge issue",
            reply="We sincerely apologize. We will resolve the refund immediately.",
            department="billing",
        )
        gt = {
            "label": "urgent",
            "department": "billing",
            "reply_keywords": ["apologize", "refund", "immediately", "resolve"],
        }
        reward_hard = grade("spam-filtering", {}, action, gt)
        reward_easy = grade("email-classification", {}, action, gt)
        assert reward_hard > reward_easy

    def test_wrong_department_no_bonus(self):
        action = MyAction(label="urgent", summary="x" * 15, reply="We will resolve this immediately.", department="sales")
        gt = {"label": "urgent", "department": "billing"}
        reward = grade("spam-filtering", {}, action, gt)
        assert reward < 0.85

    def test_reward_always_in_range(self):
        for label in ["spam", "personal", "work", "urgent", None]:
            for dept in ["engineering", "none", None]:
                action = MyAction(label=label, summary="test summary here", reply="regards", department=dept)
                gt = {"label": "urgent", "department": "engineering"}
                reward = grade("spam-filtering", {}, action, gt)
                assert 0.01 <= reward <= 0.99, f"Out of range: {reward}"


# ══════════════════════════════════════════════════════════════════════════════
# my_env_environment.py tests
# ══════════════════════════════════════════════════════════════════════════════

class TestEnvironment:

    def test_reset_returns_observation(self):
        env = MyEnvironment()
        obs = env.reset()
        assert obs.email != ""
        assert obs.done is False
        assert "task_id" in obs.metadata

    def test_reset_task_id_email_classification(self):
        env = MyEnvironment()
        obs = env.reset(task_id="email-classification")
        assert obs.metadata["task_id"] == "email-classification"

    def test_reset_task_id_urgency_detection(self):
        env = MyEnvironment()
        obs = env.reset(task_id="urgency-detection")
        assert obs.metadata["task_id"] in ["urgency-detection", "email-classification"]

    def test_reset_task_id_spam_filtering(self):
        env = MyEnvironment()
        obs = env.reset(task_id="spam-filtering")
        assert obs.metadata["task_id"] in ["spam-filtering", "email-classification"]

    def test_reset_invalid_task_id_falls_back(self):
        env = MyEnvironment()
        obs = env.reset(task_id="nonexistent")
        assert obs.metadata["task_id"] == "email-classification"

    def test_step_returns_reward_in_range(self):
        env = MyEnvironment()
        env.reset()
        action = MyAction(label="urgent", summary="test", reply="We will help.", department="engineering")
        obs = env.step(action)
        assert 0.01 <= obs.reward <= 0.99

    def test_full_episode_completes(self):
        env = MyEnvironment()
        env.reset()
        action = MyAction(label="work", summary="summary here", reply="Thank you sincerely.", department="support")
        done = False
        steps = 0
        while not done:
            obs = env.step(action)
            done = obs.done
            steps += 1
            assert steps <= 5, "Episode did not complete within expected steps"
        assert done is True

    def test_state_increments(self):
        env = MyEnvironment()
        env.reset()
        s0 = env.state.step_count
        env.step(MyAction(label="spam"))
        s1 = env.state.step_count
        assert s1 == s0 + 1

    def test_new_episode_id_on_reset(self):
        env = MyEnvironment()
        env.reset()
        id1 = env.state.episode_id
        env.reset()
        id2 = env.state.episode_id
        assert id1 != id2


# ══════════════════════════════════════════════════════════════════════════════
# models.py tests
# ══════════════════════════════════════════════════════════════════════════════

class TestModels:

    def test_valid_action(self):
        a = MyAction(label="spam", summary="test", reply="reply", department="none")
        assert a.label == "spam"

    def test_invalid_label_raises(self):
        with pytest.raises(Exception):
            MyAction(label="invalid_label")

    def test_invalid_department_raises(self):
        with pytest.raises(Exception):
            MyAction(label="work", department="unknown_dept")

    def test_all_fields_optional(self):
        a = MyAction()
        assert a.label is None
        assert a.summary is None
        assert a.reply is None
        assert a.department is None

    def test_observation_dict(self):
        obs = MyObservation(email="test email", done=False, reward=0.5, metadata={"task_id": "easy"})
        d = obs.model_dump() if hasattr(obs, "model_dump") else obs.dict()
        assert d["email"] == "test email"
        assert d["reward"] == 0.5
