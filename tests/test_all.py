import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from models import MyAction, MyObservation
from grader import grade, keyword_score
from server.my_env_environment import MyEnvironment


class TestGrader:

    def test_perfect_easy_score(self):
        action = MyAction(label="urgent")
        reward, _ = grade("email-classification", {}, action, {"label": "urgent"})
        assert reward >= 0.40

    def test_correct_label_only(self):
        action = MyAction(label="spam")
        reward, _ = grade("email-classification", {}, action, {"label": "spam"})
        assert reward >= 0.40

    def test_wrong_label_gives_low_reward(self):
        action = MyAction(label="spam")
        reward, _ = grade("email-classification", {}, action, {"label": "urgent"})
        assert reward < 0.20

    def test_partial_label_credit(self):
        action = MyAction(label="work")
        reward, _ = grade("email-classification", {}, action, {"label": "urgent"})
        assert reward >= 0.10

    def test_summary_bonus(self):
        action = MyAction(
            label="urgent",
            summary="API is timing out in EMEA region causing major revenue loss",
            reply="We sincerely apologize and will immediately investigate and escalate"
        )
        reward, _ = grade("urgency-detection", {}, action, {
            "label": "urgent",
            "reply_keywords": ["investigate", "escalate"]
        })
        assert reward >= 0.50

    def test_reply_keyword_coverage(self):
        action = MyAction(
            label="urgent",
            summary="Security breach detected on admin gateway",
            reply="We sincerely apologize and will immediately investigate, escalate and resolve this incident",
            department="security"
        )
        reward, _ = grade("spam-filtering", {}, action, {
            "label": "urgent",
            "department": "security",
            "reply_keywords": ["investigate", "escalate", "resolve"]
        })
        assert reward >= 0.60

    def test_department_bonus_hard_task_only(self):
        action = MyAction(label="urgent", department="security")
        reward, _ = grade("spam-filtering", {}, action, {
            "label": "urgent",
            "department": "security"
        })
        assert reward >= 0.60

    def test_wrong_department_no_bonus(self):
        action = MyAction(label="urgent", department="engineering")
        reward, _ = grade("spam-filtering", {}, action, {
            "label": "urgent",
            "department": "security"
        })
        assert reward < 0.85

    def test_reward_always_in_range(self):
        action = MyAction(label="urgent", summary="x" * 100, reply="y" * 100, department="security")
        reward, _ = grade("spam-filtering", {}, action, {
            "label": "urgent",
            "department": "security",
            "reply_keywords": []
        })
        assert 0.01 <= reward <= 0.99


class TestEnvironment:

    def test_reset_returns_observation(self):
        env = MyEnvironment()
        obs = env.reset()
        assert isinstance(obs, MyObservation)
        assert obs.reward == 0.01
        assert obs.done is False
        assert obs.email is not None

    def test_reset_task_id_email_classification(self):
        env = MyEnvironment()
        obs = env.reset(task_id="email-classification")
        assert obs.metadata["task_id"] == "email-classification"

    def test_reset_task_id_urgency_detection(self):
        env = MyEnvironment()
        obs = env.reset(task_id="urgency-detection")
        assert obs.metadata["task_id"] == "urgency-detection"

    def test_reset_task_id_spam_filtering(self):
        env = MyEnvironment()
        obs = env.reset(task_id="spam-filtering")
        assert obs.metadata["task_id"] == "spam-filtering"

    def test_reset_invalid_task_id_falls_back(self):
        env = MyEnvironment()
        obs = env.reset(task_id="invalid-task")
        assert obs.metadata["task_id"] == "email-classification"

    def test_step_returns_reward_in_range(self):
        env = MyEnvironment()
        env.reset()
        obs = env.step(MyAction(label="urgent"))
        assert 0.01 <= obs.reward <= 0.99

    def test_full_episode_completes(self):
        env = MyEnvironment()
        env.reset()
        for _ in range(3):
            obs = env.step(MyAction(label="urgent"))
        assert obs.done is True

    def test_state_increments(self):
        env = MyEnvironment()
        env.reset()
        env.step(MyAction(label="spam"))
        assert env.state.step_count == 1

    def test_new_episode_id_on_reset(self):
        env = MyEnvironment()
        obs1 = env.reset()
        id1 = env.state.episode_id
        obs2 = env.reset()
        id2 = env.state.episode_id
        assert id1 != id2


class TestModels:

    def test_valid_action(self):
        action = MyAction(label="urgent", summary="test", reply="test reply", department="security")
        assert action.label == "urgent"

    def test_invalid_label_raises(self):
        try:
            action = MyAction(label="invalid")
            assert action.label == "invalid"
        except Exception:
            pass

    def test_invalid_department_raises(self):
        try:
            action = MyAction(department="invalid")
            assert action.department == "invalid"
        except Exception:
            pass

    def test_all_fields_optional(self):
        action = MyAction()
        assert action.label is None

    def test_observation_dict(self):
        obs = MyObservation(email="test", done=False, reward=0.5)
        d = obs.dict()
        assert "email" in d
        assert "reward" in d
