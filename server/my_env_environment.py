from uuid import uuid4
import random
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State
from models import MyAction, MyObservation
from grader import grade

TASKS = {
    "email-classification": [ # EASY: Label only
        {"email": "Hey, are we still on for dinner?", "ground_truth": {"label": "personal"}}
    ],
    "urgency-detection": [ # MEDIUM: Label + Summary + Reply
        {"email": "API Timeout in EMEA region. 15% failures.", "ground_truth": {"label": "urgent", "reply_keywords": ["investigate", "sorry"]}}
    ],
    "spam-filtering": [ # HARD: Label + Routing + Reply
        {"email": "SECURITY ALERT: SQL Injection attempt on admin portal.", "ground_truth": {"label": "urgent", "department": "security", "reply_keywords": ["incident", "audit"]}}
    ]
}
TASK_ORDER = ["email-classification", "urgency-detection", "spam-filtering"]

class MyEnvironment(Environment):
    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.task_index = 0
        self._load_task()

    def _load_task(self, task_id=None):
        self.current_task_id = task_id or TASK_ORDER[self.task_index % len(TASK_ORDER)]
        self.current_data = random.choice(TASKS[self.current_task_id])

    def reset(self, task_id=None, *args, **kwargs):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        if task_id in TASKS:
            self.task_index = TASK_ORDER.index(task_id)
        else:
            self.task_index = 0
        self._load_task(task_id)
        return MyObservation(email=self.current_data["email"], done=False, reward=0.01, metadata={"task_id": self.current_task_id})

    def step(self, action: MyAction, *args, **kwargs):
        self._state.step_count += 1
        reward = grade(self.current_task_id, None, action, self.current_data["ground_truth"])
        self.task_index += 1
        done = self.task_index >= len(TASK_ORDER)
        if not done: self._load_task()
        return MyObservation(email=self.current_data["email"], done=done, reward=float(reward), metadata={"task_id": self.current_task_id})

    @property
    def state(self): return self._state
