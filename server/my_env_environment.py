from uuid import uuid4
import random

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State
from openenv.core.rubrics import Rubric

try:
    from ..models import MyAction, MyObservation
except ImportError:
    from models import MyAction, MyObservation


def keyword_score(text, keywords):
    if not text or not keywords:
        return 0.0
    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return hits / len(keywords)


class EasyTaskRubric(Rubric):
    def __init__(self):
        super().__init__()
        self._ground_truth = {}

    def set_ground_truth(self, gt):
        self._ground_truth = gt

    def forward(self, action, observation) -> float:
        reward = 0.0
        correct_label = self._ground_truth.get("label")
        if action.label == correct_label:
            reward = 0.85
        elif action.label in ["spam", "personal", "work", "urgent"]:
            reward = 0.15
        return min(max(reward, 0.01), 0.99)


class MediumTaskRubric(Rubric):
    def __init__(self):
        super().__init__()
        self._ground_truth = {}

    def set_ground_truth(self, gt):
        self._ground_truth = gt

    def forward(self, action, observation) -> float:
        reward = 0.0
        correct_label = self._ground_truth.get("label")
        if action.label == correct_label:
            reward += 0.45
        elif action.label in ["spam", "personal", "work", "urgent"]:
            reward += 0.08
        if action.summary and len(action.summary) > 10:
            reward += 0.20
        reply_keywords = self._ground_truth.get("reply_keywords", [])
        if action.reply and reply_keywords:
            reward += 0.25 * keyword_score(action.reply, reply_keywords)
        return min(max(reward, 0.01), 0.99)


class HardTaskRubric(Rubric):
    def __init__(self):
        super().__init__()
        self._ground_truth = {}

    def set_ground_truth(self, gt):
        self._ground_truth = gt

    def forward(self, action, observation) -> float:
        reward = 0.0
        correct_label = self._ground_truth.get("label")
        if action.label == correct_label:
            reward += 0.35
        elif action.label in ["spam", "personal", "work", "urgent"]:
            reward += 0.06
        if action.summary and len(action.summary) > 10:
            reward += 0.15
        reply_keywords = self._ground_truth.get("reply_keywords", [])
        if action.reply and reply_keywords:
            reward += 0.20 * keyword_score(action.reply, reply_keywords)
        correct_dept = self._ground_truth.get("department")
        if action.department == correct_dept:
            reward += 0.20
        elif action.department and action.department != "none":
            reward += 0.04
        return min(max(reward, 0.01), 0.99)


class EmailTriageRubric(Rubric):
    def __init__(self):
        super().__init__()
        self.easy = EasyTaskRubric()
        self.medium = MediumTaskRubric()
        self.hard = HardTaskRubric()
        self._current_task_id = "easy"

    def set_task(self, task_id: str, ground_truth: dict):
        self._current_task_id = task_id
        if task_id == "easy":
            self.easy.set_ground_truth(ground_truth)
        elif task_id == "medium":
            self.medium.set_ground_truth(ground_truth)
        else:
            self.hard.set_ground_truth(ground_truth)

    def forward(self, action, observation) -> float:
        if self._current_task_id == "easy":
            return self.easy(action, observation)
        elif self._current_task_id == "medium":
            return self.medium(action, observation)
        else:
            return self.hard(action, observation)


TASKS = {
    "easy": [
        {"email": "URGENT: Production server is down, fix immediately!", "ground_truth": {"label": "urgent"}},
        {"email": "Win a free iPhone now!!! Click here to claim your prize!!!", "ground_truth": {"label": "spam"}},
        {"email": "Hey, are we still on for dinner tonight?", "ground_truth": {"label": "personal"}},
        {"email": "Reminder: submit your project report by tomorrow", "ground_truth": {"label": "work"}},
        {"email": "Congratulations! You have won a lottery prize of $1,000,000!", "ground_truth": {"label": "spam"}},
        {"email": "Client feedback received, please review the attached document", "ground_truth": {"label": "work"}},
        {"email": "Security alert: suspicious login attempt detected on your account", "ground_truth": {"label": "urgent"}},
        {"email": "Happy birthday! Have a wonderful day!", "ground_truth": {"label": "personal"}},
    ],
    "medium": [
        {"email": "Hi, I placed an order 2 weeks ago and still haven't received it. Order #12345. Please help ASAP.", "ground_truth": {"label": "urgent", "reply_keywords": ["sorry", "order", "track", "help", "resolve"]}},
        {"email": "We are interested in your enterprise plan. Can you send pricing details?", "ground_truth": {"label": "work", "reply_keywords": ["pricing", "plan", "team", "contact", "details"]}},
        {"email": "The API is returning 500 errors since your last deployment. This is breaking our production app.", "ground_truth": {"label": "urgent", "reply_keywords": ["sorry", "issue", "fix", "team", "investigate"]}},
        {"email": "I'd like to cancel my subscription and get a refund for this month.", "ground_truth": {"label": "work", "reply_keywords": ["cancel", "refund", "process", "account", "confirm"]}},
        {"email": "Can you share the slides from yesterday's webinar? It was very helpful.", "ground_truth": {"label": "work", "reply_keywords": ["slides", "share", "webinar", "send", "link"]}},
    ],
    "hard": [
        {"email": "This is absolutely unacceptable! I've been charged twice for the same order and nobody is responding.", "ground_truth": {"label": "urgent", "department": "billing", "reply_keywords": ["apologize", "refund", "immediately", "priority", "resolve", "charge"]}},
        {"email": "Dear team, our competitor just launched a feature similar to ours. Q3 report is due Friday.", "ground_truth": {"label": "work", "department": "management", "reply_keywords": ["acknowledge", "meeting", "discuss", "strategy", "report", "coordinate"]}},
        {"email": "Hi, I'm a journalist writing about data privacy. I'd like a comment about recent data breach reports. Deadline is tomorrow.", "ground_truth": {"label": "urgent", "department": "legal", "reply_keywords": ["acknowledge", "legal", "team", "respond", "review", "deadline"]}},
        {"email": "Server memory usage has been climbing for 3 days, now at 94%. Logs show unusual traffic from 3 IPs.", "ground_truth": {"label": "urgent", "department": "security", "reply_keywords": ["investigate", "block", "team", "monitor", "escalate", "security"]}},
    ]
}

TASK_ORDER = ["easy", "medium", "hard"]


class MyEnvironment(Environment):

    def __init__(self):
        email_rubric = EmailTriageRubric()
        super().__init__(rubric=email_rubric)
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_email = None
        self.current_task_id = None
        self.ground_truth = None
        self.task_index = 0

    def reset(self, *args, **kwargs):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.task_index = 0
        self._load_next_task()
        return MyObservation(
            email=self.current_email["email"],
            done=False,
            reward=0.01,
            metadata={"task_id": self.current_task_id, "instruction": self._get_instruction()}
        )

    def _load_next_task(self):
        task_id = TASK_ORDER[self.task_index % len(TASK_ORDER)]
        self.current_task_id = task_id
        self.current_email = random.choice(TASKS[task_id])
        self.ground_truth = self.current_email["ground_truth"]
        self.rubric.set_task(task_id, self.ground_truth)

    def _get_instruction(self):
        if self.current_task_id == "easy":
            return "Classify this email. Set 'label' to one of: spam, personal, work, urgent."
        elif self.current_task_id == "medium":
            return "Classify this email with 'label', write a short 'summary', and draft a professional 'reply'."
        else:
            return "Classify this email with 'label', identify the correct 'department', write a 'summary', and draft a professional 'reply'."

    def step(self, action: MyAction, *args, **kwargs):
        self._state.step_count += 1
        reward = self.rubric(action, None)
        self.task_index += 1
        done = self.task_index >= len(TASK_ORDER)
        if not done:
            self._load_next_task()
        return MyObservation(
            email=self.current_email["email"],
            done=done,
            reward=reward,
            metadata={"task_id": self.current_task_id, "instruction": self._get_instruction(), "steps_taken": self._state.step_count}
        )

    @property
    def state(self):
        return self._state
# force rebuild Wed Apr  8 17:17:03 IST 2026
