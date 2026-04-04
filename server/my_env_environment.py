from uuid import uuid4
import random

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import MyAction, MyObservation
    from ..grader import grade
except ImportError:
    from models import MyAction, MyObservation
    from grader import grade

TASKS = {
    "easy": [
        {"email": "URGENT: Production server is down, fix immediately!", "label": "urgent", "department": "engineering", "ground_truth": {"label": "urgent"}},
        {"email": "Win a free iPhone now!!! Click here to claim your prize!!!", "label": "spam", "department": "none", "ground_truth": {"label": "spam"}},
        {"email": "Hey, are we still on for dinner tonight?", "label": "personal", "department": "none", "ground_truth": {"label": "personal"}},
        {"email": "Reminder: submit your project report by tomorrow", "label": "work", "department": "management", "ground_truth": {"label": "work"}},
        {"email": "Congratulations! You have won a lottery prize of $1,000,000!", "label": "spam", "department": "none", "ground_truth": {"label": "spam"}},
        {"email": "Client feedback received, please review the attached document", "label": "work", "department": "management", "ground_truth": {"label": "work"}},
        {"email": "Security alert: suspicious login attempt detected on your account", "label": "urgent", "department": "security", "ground_truth": {"label": "urgent"}},
        {"email": "Happy birthday! Have a wonderful day!", "label": "personal", "department": "none", "ground_truth": {"label": "personal"}},
    ],
    "medium": [
        {"email": "Hi, I placed an order 2 weeks ago and still haven't received it. Order #12345. Please help ASAP.", "label": "urgent", "department": "support", "ground_truth": {"label": "urgent", "reply_keywords": ["sorry", "order", "track", "help", "resolve"]}},
        {"email": "We are interested in your enterprise plan. Can you send pricing details?", "label": "work", "department": "sales", "ground_truth": {"label": "work", "reply_keywords": ["pricing", "plan", "team", "contact", "details"]}},
        {"email": "The API is returning 500 errors since your last deployment. This is breaking our production app.", "label": "urgent", "department": "engineering", "ground_truth": {"label": "urgent", "reply_keywords": ["sorry", "issue", "fix", "team", "investigate"]}},
        {"email": "I'd like to cancel my subscription and get a refund for this month.", "label": "work", "department": "billing", "ground_truth": {"label": "work", "reply_keywords": ["cancel", "refund", "process", "account", "confirm"]}},
        {"email": "Can you share the slides from yesterday's webinar? It was very helpful.", "label": "work", "department": "marketing", "ground_truth": {"label": "work", "reply_keywords": ["slides", "share", "webinar", "send", "link"]}},
    ],
    "hard": [
        {"email": "This is absolutely unacceptable! I've been charged twice for the same order and nobody is responding. I'm going to dispute this with my bank and post about this on Twitter if I don't hear back in 1 hour.", "label": "urgent", "department": "billing", "ground_truth": {"label": "urgent", "department": "billing", "reply_keywords": ["apologize", "refund", "immediately", "priority", "resolve", "charge"]}},
        {"email": "Dear team, I wanted to flag that our competitor just launched a feature very similar to what we've been building for 6 months. We should discuss strategy. Also, the Q3 report is due Friday and I still need numbers from sales and engineering.", "label": "work", "department": "management", "ground_truth": {"label": "work", "department": "management", "reply_keywords": ["acknowledge", "meeting", "discuss", "strategy", "report", "coordinate"]}},
        {"email": "Hi, my name is Sarah and I'm a journalist writing about data privacy practices in tech companies. I'd like to request a comment from your team about the recent data breach reports circulating online. Deadline is tomorrow morning.", "label": "urgent", "department": "legal", "ground_truth": {"label": "urgent", "department": "legal", "reply_keywords": ["acknowledge", "legal", "team", "respond", "review", "deadline"]}},
        {"email": "Server memory usage has been climbing steadily for 3 days — now at 94%. We haven't deployed anything new. Logs show unusual traffic patterns from 3 IPs. Could be a memory leak or something more serious.", "label": "urgent", "department": "security", "ground_truth": {"label": "urgent", "department": "security", "reply_keywords": ["investigate", "block", "team", "monitor", "escalate", "security"]}},
    ]
}

TASK_ORDER = ["easy", "medium", "hard"]


class MyEnvironment(Environment):

    def __init__(self):
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
            reward=0.0,
            metadata={
                "task_id": self.current_task_id,
                "instruction": self._get_instruction(),
            }
        )

    def _load_next_task(self):
        task_id = TASK_ORDER[self.task_index % len(TASK_ORDER)]
        self.current_task_id = task_id
        self.current_email = random.choice(TASKS[task_id])
        self.ground_truth = self.current_email["ground_truth"]

    def _get_instruction(self):
        if self.current_task_id == "easy":
            return "Classify this email. Set 'label' to one of: spam, personal, work, urgent."
        elif self.current_task_id == "medium":
            return "Classify this email with 'label', write a short 'summary', and draft a professional 'reply'."
        else:
            return "Classify this email with 'label', identify the correct 'department' to route it to, write a 'summary', and draft a professional 'reply'."

    def step(self, action: MyAction, *args, **kwargs):
        self._state.step_count += 1

        reward = grade(
            task_id=self.current_task_id,
            state={"email": self.current_email["email"]},
            action=action,
            ground_truth=self.ground_truth,
        )

        self.task_index += 1
        done = self.task_index >= len(TASK_ORDER)

        if not done:
            self._load_next_task()
            next_email = self.current_email["email"]
            next_instruction = self._get_instruction()
            next_task_id = self.current_task_id
        else:
            next_email = self.current_email["email"]
            next_instruction = "Episode complete."
            next_task_id = self.current_task_id

        return MyObservation(
            email=next_email,
            done=done,
            reward=reward,
            metadata={
                "task_id": next_task_id,
                "instruction": next_instruction,
                "steps_taken": self._state.step_count,
            }
        )

    @property
    def state(self):
        return self._state