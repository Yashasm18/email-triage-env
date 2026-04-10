from uuid import uuid4
import random

try:
    from openenv.core.env_server.interfaces import Environment
    from openenv.core.env_server.types import State
except ImportError:
    class Environment: pass
    class State:
        def __init__(self, episode_id, step_count):
            self.episode_id = episode_id
            self.step_count = step_count

try:
    from models import MyAction, MyObservation
    from grader import grade
except ImportError:
    from .models import MyAction, MyObservation
    from .grader import grade

# ==========================================================
# 🧠 EXPERT DATASET: HIGH-STAKES CORPORATE SCENARIOS
# ==========================================================
TASKS = {
    "email-classification": [
        {"email": "URGENT: Database cluster reporting 98% disk utilization. Performance is degrading.", "label": "urgent", "ground_truth": {"label": "urgent"}},
        {"email": "Hey team, reminder about the office pizza party this Friday at 5 PM!", "label": "personal", "ground_truth": {"label": "personal"}}
    ],
    "urgency-detection": [
        {"email": "CRITICAL: 15% of checkout requests in Europe are timing out. We need a hotfix immediately.", 
         "label": "urgent", "ground_truth": {"label": "urgent", "reply_keywords": ["hotfix", "investigate", "sorry"]}}
    ],
    "spam-filtering": [
        {"email": "SECURITY ALERT: Massive brute-force attack detected on admin gateway. Log analysis suggests SQL injection.", 
         "label": "urgent", "department": "security", "ground_truth": {"label": "urgent", "department": "security"}},
        {"email": "GDPR DATA REQUEST: Formal request for a copy of all personal data held, as per Article 15.", 
         "label": "work", "department": "legal", "ground_truth": {"label": "work", "department": "legal"}}
    ]
}

TASK_ORDER = ["email-classification", "urgency-detection", "spam-filtering"]

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
        # CRITICAL: 0.01 reward for validator range safety
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

    def _get_instruction(self):
        return f"Task: {self.current_task_id}. Provide accurate label, summary, and routing."

    def step(self, action: MyAction, *args, **kwargs):
        self._state.step_count += 1
        reward = grade(self.current_task_id, None, action, self.ground_truth)
        self.task_index += 1
        done = self.task_index >= len(TASK_ORDER)
        if not done:
            self._load_next_task()
        
        return MyObservation(
            email=self.current_email["email"],
            done=done,
            reward=float(reward), # Clipped by grader logic
            metadata={"task_id": self.current_task_id, "steps_taken": self._state.step_count}
        )

    @property
    def state(self):
        return self._state
