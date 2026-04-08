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
# 🧠 EXPERT DATASET: CORPORATE TRIAGE SCENARIOS
# ==========================================================
TASKS = {
    "email-classification": [
        {
            "email": "URGENT: Database cluster 'prod-db-01' is reporting 98% disk utilization. Performance is degrading rapidly across all services.", 
            "label": "urgent", 
            "ground_truth": {"label": "urgent"}
        },
        {
            "email": "FINAL NOTICE: Your domain registration for 'company-hq.com' expires in 24 hours. Click here to renew immediately and avoid downtime.", 
            "label": "work", 
            "ground_truth": {"label": "work"}
        },
        {
            "email": "Hey team, just a reminder about the office pizza party this Friday at 5 PM. Hope to see you all there!", 
            "label": "personal", 
            "ground_truth": {"label": "personal"}
        },
        {
            "email": "CONGRATULATIONS! You've been selected for a $1000 Amazon Gift Card. Just complete this survey to claim your reward.", 
            "label": "spam", 
            "ground_truth": {"label": "spam"}
        }
    ],

    "urgency-detection": [
        {
            "email": "Subject: Critical API Timeout in EMEA Region. Since the v2.4 deployment, 15% of checkout requests in Europe are timing out. Customer support is receiving flooded tickets. We need a rollback plan or a hotfix immediately.", 
            "label": "urgent", 
            "ground_truth": {
                "label": "urgent", 
                "reply_keywords": ["deployment", "checkout", "investigate", "rollback", "hotfix", "apologize"]
            }
        },
        {
            "email": "Hi, I'm a journalist from TechCrunch. We're doing a story on your new AI features and would love to get a quote from your CTO by tomorrow morning.", 
            "label": "work", 
            "ground_truth": {
                "label": "work", 
                "reply_keywords": ["TechCrunch", "CTO", "interview", "opportunity", "press"]
            }
        }
    ],

    "spam-filtering": [
        {
            "email": "SECURITY ALERT: We've detected a massive brute-force attack on the admin gateway from multiple restricted IP ranges. Log analysis suggests an attempted SQL injection. Please initiate incident response protocols.", 
            "label": "urgent", "department": "security", 
            "ground_truth": {
                "label": "urgent", "department": "security", 
                "reply_keywords": ["incident", "protocol", "audit", "security", "mitigate", "attack"]
            }
        },
        {
            "email": "BILLING DISPUTE: I was charged for the 'Premium Enterprise' tier ($1,200) despite canceling my trial three days ago. If this isn't refunded, I will file a dispute with my bank.", 
            "label": "urgent", "department": "billing", 
            "ground_truth": {
                "label": "urgent", "department": "billing", 
                "reply_keywords": ["refund", "cancel", "dispute", "billing", "correct", "apologize"]
            }
        },
        {
            "email": "GDPR DATA REQUEST: I am writing to formally request a copy of all personal data your company holds on me, as per my rights under Article 15. Please confirm receipt.", 
            "label": "work", "department": "legal", 
            "ground_truth": {
                "label": "work", "department": "legal", 
                "reply_keywords": ["GDPR", "privacy", "compliance", "receipt", "legal"]
            }
        }
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
        return MyObservation(
            email=self.current_email["email"],
            done=False,
            reward=0.01, # Hackathon safe-range
            metadata={"task_id": self.current_task_id, "instruction": self._get_instruction()}
        )

    def _load_next_task(self):
        task_id = TASK_ORDER[self.task_index % len(TASK_ORDER)]
        self.current_task_id = task_id
        self.current_email = random.choice(TASKS[task_id])
        self.ground_truth = self.current_email["ground_truth"]

    def _get_instruction(self):
        if self.current_task_id == "email-classification":
            return "Classify intent. Set 'label' to: spam, personal, work, or urgent."
        elif self.current_task_id == "urgency-detection":
            return "Analyze urgency. Provide 'label', a 1-sentence 'summary', and a professional 'reply'."
        else:
            return "Enterprise Triage. Provide 'label', correct 'department' routing, 'summary', and 'reply'."

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
        return MyObservation(
            email=self.current_email["email"],
            done=done,
            reward=float(reward),
            metadata={"task_id": self.current_task_id, "instruction": self._get_instruction(), "steps_taken": self._state.step_count}
        )

    @property
    def state(self):
        return self._state
