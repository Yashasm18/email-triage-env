from uuid import uuid4
import random

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from models import MyAction, MyObservation
from grader import grade


# ── Task pool ────────────────────────────────────────────────────────────────
# Task IDs match openenv.yaml, inference.py, and app.py exactly.

TASKS = {
    "email-classification": [
        {
            "email": "URGENT: Production server is down, fix immediately!",
            "ground_truth": {"label": "urgent"},
        },
        {
            "email": "Win a free iPhone now!!! Click here to claim your prize!!!",
            "ground_truth": {"label": "spam"},
        },
        {
            "email": "Hey, are we still on for dinner tonight?",
            "ground_truth": {"label": "personal"},
        },
        {
            "email": "Reminder: submit your project report by tomorrow end of day.",
            "ground_truth": {"label": "work"},
        },
        {
            "email": "Congratulations! You've been selected for a $500 gift card. Claim now!",
            "ground_truth": {"label": "spam"},
        },
        {
            "email": "Can you review the pull request I opened this morning?",
            "ground_truth": {"label": "work"},
        },
        {
            "email": "Happy birthday! Hope you have a wonderful day.",
            "ground_truth": {"label": "personal"},
        },
        {
            "email": "CRITICAL: Database connection pool exhausted — all services degraded.",
            "ground_truth": {"label": "urgent"},
        },
    ],

    "urgency-detection": [
        {
            "email": (
                "Hi, I placed an order 2 weeks ago and still haven't received it. "
                "Order #12345. Please help ASAP."
            ),
            "ground_truth": {
                "label": "urgent",
                "reply_keywords": ["sorry", "order", "track", "help", "resolve"],
            },
        },
        {
            "email": (
                "We are interested in your enterprise plan. "
                "Can you send pricing details and a demo?"
            ),
            "ground_truth": {
                "label": "work",
                "reply_keywords": ["pricing", "plan", "team", "contact", "details"],
            },
        },
        {
            "email": (
                "The API is returning 500 errors since your last deployment. "
                "This is breaking our production app."
            ),
            "ground_truth": {
                "label": "urgent",
                "reply_keywords": ["sorry", "issue", "fix", "team", "investigate"],
            },
        },
        {
            "email": (
                "Our integration stopped working after the 2.4 update. "
                "We need this fixed before our client presentation tomorrow."
            ),
            "ground_truth": {
                "label": "urgent",
                "reply_keywords": ["apologize", "fix", "team", "update", "priority"],
            },
        },
        {
            "email": (
                "Can you walk me through the onboarding steps for new team members? "
                "We have 5 people joining next Monday."
            ),
            "ground_truth": {
                "label": "work",
                "reply_keywords": ["guide", "steps", "team", "onboard", "help"],
            },
        },
        {
            "email": (
                "My account was locked out after too many failed login attempts. "
                "I need access urgently for a client call in 30 minutes."
            ),
            "ground_truth": {
                "label": "urgent",
                "reply_keywords": ["reset", "access", "account", "immediately", "help"],
            },
        },
    ],

    "spam-filtering": [
        {
            "email": (
                "This is absolutely unacceptable! I've been charged twice for the same "
                "order and nobody is responding to my emails."
            ),
            "ground_truth": {
                "label": "urgent",
                "department": "billing",
                "reply_keywords": ["apologize", "refund", "immediately", "priority", "resolve", "charge"],
            },
        },
        {
            "email": (
                "Server memory usage has been climbing steadily for 3 days — now at 94%. "
                "Logs show unusual traffic patterns from 3 external IPs."
            ),
            "ground_truth": {
                "label": "urgent",
                "department": "security",
                "reply_keywords": ["investigate", "block", "team", "monitor", "escalate", "security"],
            },
        },
        {
            "email": (
                "We would like to negotiate a volume discount for 200 licences. "
                "Who should I speak to about custom pricing?"
            ),
            "ground_truth": {
                "label": "work",
                "department": "sales",
                "reply_keywords": ["discount", "pricing", "contact", "team", "negotiate"],
            },
        },
        {
            "email": (
                "Our legal team has flagged a potential GDPR compliance issue with "
                "how user data is stored. We need a formal response within 48 hours."
            ),
            "ground_truth": {
                "label": "urgent",
                "department": "legal",
                "reply_keywords": ["compliance", "gdpr", "team", "review", "respond", "data"],
            },
        },
        {
            "email": (
                "The CI pipeline for our main branch has been failing for 6 hours. "
                "All deployments are blocked. Engineers are standing by."
            ),
            "ground_truth": {
                "label": "urgent",
                "department": "engineering",
                "reply_keywords": ["investigate", "pipeline", "fix", "team", "deploy", "escalate"],
            },
        },
        {
            "email": (
                "We were overcharged on our last three invoices. "
                "The amounts don't match our contract. Please review and issue corrections."
            ),
            "ground_truth": {
                "label": "urgent",
                "department": "billing",
                "reply_keywords": ["invoice", "review", "correct", "apologize", "contract", "resolve"],
            },
        },
    ],
}

TASK_ORDER = ["email-classification", "urgency-detection", "spam-filtering"]


def _get_instruction(task_id: str) -> str:
    if task_id == "email-classification":
        return "Classify this email. Set 'label' to one of: spam, personal, work, urgent."
    elif task_id == "urgency-detection":
        return (
            "Classify this email with 'label', write a short 'summary', "
            "and draft a professional 'reply'."
        )
    else:  # spam-filtering
        return (
            "Classify this email with 'label', identify the correct 'department', "
            "write a 'summary', and draft a professional 'reply'."
        )


class MyEnvironment(Environment):

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.task_index = 0
        self.current_task_id = TASK_ORDER[0]
        self.current_data = random.choice(TASKS[self.current_task_id])

    def _load_task(self, task_id=None):
        self.current_task_id = task_id or TASK_ORDER[self.task_index % len(TASK_ORDER)]
        self.current_data = random.choice(TASKS[self.current_task_id])

    def reset(self, task_id=None, *args, **kwargs):
        self._state = State(episode_id=str(uuid4()), step_count=0)

        if task_id and task_id in TASKS:
            self.task_index = TASK_ORDER.index(task_id)
        else:
            self.task_index = 0

        self._load_task(task_id if task_id in TASKS else None)

        return MyObservation(
            email=self.current_data["email"],
            done=False,
            reward=0.01,
            metadata={
                "task_id": self.current_task_id,
                "instruction": _get_instruction(self.current_task_id),
            },
        )

    def step(self, action: MyAction, *args, **kwargs):
        self._state.step_count += 1

        reward = grade(
            self.current_task_id,
            {"email": self.current_data["email"]},
            action,
            self.current_data["ground_truth"],
        )

        self.task_index += 1
        done = self.task_index >= len(TASK_ORDER)

        if not done:
            self._load_task()

        # Return the NEXT email (or empty string if episode is done)
        next_email = self.current_data["email"] if not done else ""
        next_task_id = self.current_task_id if not done else TASK_ORDER[-1]

        return MyObservation(
            email=next_email,
            done=done,
            reward=float(reward),
            metadata={
                "task_id": next_task_id,
                "instruction": _get_instruction(next_task_id) if not done else "",
                "steps_taken": self._state.step_count,
            },
        )

    @property
    def state(self):
        return self._state
