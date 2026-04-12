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

TASKS = {
    "email-classification": [
        {"email": "URGENT: Database cluster prod-db-01 is at 98% disk utilization. All services degrading rapidly.", "ground_truth": {"label": "urgent"}},
        {"email": "Hey team, pizza party this Friday at 5 PM. Hope to see you all there!", "ground_truth": {"label": "personal"}},
        {"email": "Please review and sign the updated NDA before the client meeting tomorrow.", "ground_truth": {"label": "work"}},
        {"email": "Congratulations! You have been selected for a $1,000,000 prize. Click here now!", "ground_truth": {"label": "spam"}},
        {"email": "CRITICAL: Payment gateway is down. Customers cannot checkout. Immediate fix needed.", "ground_truth": {"label": "urgent"}},
        {"email": "Can you send me the Q3 budget report before end of day?", "ground_truth": {"label": "work"}},
        {"email": "Happy anniversary! Wishing you a wonderful day.", "ground_truth": {"label": "personal"}},
        {"email": "You have won a FREE vacation to Bahamas! Claim now before it expires!", "ground_truth": {"label": "spam"}},
        {"email": "Security breach detected on admin panel. Multiple failed login attempts from foreign IPs.", "ground_truth": {"label": "urgent"}},
        {"email": "Team lunch is scheduled for Wednesday at 1 PM at the usual place.", "ground_truth": {"label": "personal"}},
    ],
    "urgency-detection": [
        {"email": "Since v2.4 deployment, 15% of checkout requests in Europe are timing out. Need hotfix immediately.", "ground_truth": {"label": "urgent", "reply_keywords": ["hotfix", "investigate", "rollback", "apologize", "team"]}},
        {"email": "We are interested in your enterprise plan. Can you send pricing and onboarding details?", "ground_truth": {"label": "work", "reply_keywords": ["pricing", "plan", "team", "contact", "details"]}},
        {"email": "Hi, I placed an order 2 weeks ago and still haven't received it. Order #12345. Please help!", "ground_truth": {"label": "urgent", "reply_keywords": ["sorry", "order", "track", "resolve", "immediately"]}},
        {"email": "Can you share the slides from yesterday's all-hands meeting?", "ground_truth": {"label": "work", "reply_keywords": ["slides", "share", "send", "meeting", "link"]}},
        {"email": "Our integration with your API has been failing for 3 hours. We are losing revenue every minute.", "ground_truth": {"label": "urgent", "reply_keywords": ["sorry", "investigate", "fix", "team", "escalate"]}},
        {"email": "I would like to schedule a demo of your product for our leadership team next week.", "ground_truth": {"label": "work", "reply_keywords": ["demo", "schedule", "team", "available", "confirm"]}},
    ],
    "spam-filtering": [
        {"email": "SECURITY ALERT: Massive brute-force attack on admin gateway. SQL injection detected from multiple IPs.", "ground_truth": {"label": "urgent", "department": "security", "reply_keywords": ["incident", "protocol", "audit", "security", "block"]}},
        {"email": "GDPR DATA REQUEST: Formal request for all personal data under Article 15. Please confirm receipt.", "ground_truth": {"label": "work", "department": "legal", "reply_keywords": ["GDPR", "privacy", "compliance", "legal", "confirm"]}},
        {"email": "This is unacceptable! I have been charged twice for the same order and nobody is responding.", "ground_truth": {"label": "urgent", "department": "billing", "reply_keywords": ["apologize", "refund", "immediately", "resolve", "charge"]}},
        {"email": "Our competitor just launched a feature similar to ours. Q3 report is due Friday.", "ground_truth": {"label": "work", "department": "management", "reply_keywords": ["acknowledge", "meeting", "strategy", "discuss", "report"]}},
        {"email": "Server memory at 94% for 3 days. Logs show unusual traffic from 3 IPs. Possible attack.", "ground_truth": {"label": "urgent", "department": "security", "reply_keywords": ["investigate", "block", "monitor", "escalate", "security"]}},
        {"email": "Journalist requesting comment on recent data breach reports. Deadline is tomorrow morning.", "ground_truth": {"label": "urgent", "department": "legal", "reply_keywords": ["acknowledge", "legal", "team", "review", "respond"]}},
        {"email": "Employee complaint filed against manager for workplace harassment. Requires immediate HR review.", "ground_truth": {"label": "urgent", "department": "hr", "reply_keywords": ["acknowledge", "investigate", "confidential", "hr", "policy"]}},
        {"email": "Invoice #4521 is 60 days overdue. Please process payment immediately to avoid service suspension.", "ground_truth": {"label": "work", "department": "billing", "reply_keywords": ["invoice", "payment", "process", "confirm", "account"]}},
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

    def reset(self, task_id=None, *args, **kwargs):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        if task_id in TASKS:
            self.current_task_id = task_id
            self.task_index = TASK_ORDER.index(task_id)
        else:
            self.task_index = 0
            self.current_task_id = TASK_ORDER[0]
        self.current_email = random.choice(TASKS[self.current_task_id])
        self.ground_truth = self.current_email["ground_truth"]
        return MyObservation(
            email=self.current_email["email"],
            done=False,
            reward=0.01,
            feedback="New episode started. " + self._get_instruction(),
            metadata={"task_id": self.current_task_id, "instruction": self._get_instruction()}
        )

    def _get_instruction(self):
        if self.current_task_id == "email-classification":
            return "Classify intent. Set 'label' to: spam, personal, work, or urgent."
        elif self.current_task_id == "urgency-detection":
            return "Analyze urgency. Provide 'label', 'summary', and professional 'reply'."
        else:
            return "Enterprise Triage. Set 'label', 'department', write 'summary' and 'reply'."

    def step(self, action: MyAction, *args, **kwargs):
        self._state.step_count += 1
        reward, feedback = grade(
            task_id=self.current_task_id,
            state={"email": self.current_email["email"]},
            action=action,
            ground_truth=self.ground_truth,
        )
        self.task_index += 1
        done = self.task_index >= len(TASK_ORDER)
        if not done:
            self.current_task_id = TASK_ORDER[self.task_index]
            self.current_email = random.choice(TASKS[self.current_task_id])
            self.ground_truth = self.current_email["ground_truth"]
        return MyObservation(
            email=self.current_email["email"],
            done=done,
            reward=float(reward),
            feedback=feedback,
            metadata={"task_id": self.current_task_id, "instruction": self._get_instruction(), "steps_taken": self._state.step_count}
        )

    @property
    def state(self):
        return self._state
