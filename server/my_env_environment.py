from uuid import uuid4
import random

try:
    from openenv.core.env_server.interfaces import Environment
    from openenv.core.env_server.types import State
except ImportError:
    # Fallback for local development or environment variations
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
        {
            "email": "URGENT: Database cluster 'prod-db-01' is reporting 98% disk utilization. Performance is degrading rapidly across all services.", 
            "label": "urgent", 
            "ground_truth": {"label": "urgent"}
        },
        {
            "email": "Hey team, just a reminder about the office pizza party this Friday at 5 PM. Hope to see you all there!", 
            "label": "personal", 
            "ground_truth": {"label": "personal"}
        }
    ],

    "urgency-detection": [
        {
            "email": "Subject: Critical API Timeout in EMEA Region. Since the v2.4 deployment, 15% of checkout requests in Europe are timing out. We need a hotfix immediately.", 
            "label": "urgent", 
            "ground_truth": {
                "label": "urgent", 
                "reply_keywords": ["hotfix", "investigate", "rollback", "apologize"]
            }
        }
    ],

    "spam-filtering": [
        {
            "email": "SECURITY ALERT: Massive brute-force attack detected on admin gateway from multiple restricted IP ranges. Log analysis suggests SQL injection.", 
            "label": "urgent", "department": "security", 
            "ground_truth": {
                "label": "urgent", "department": "security", 
                "reply_keywords": ["incident", "protocol", "audit", "security", "attack"]
            }
        },
        {
            "email": "GDPR DATA REQUEST: I am writing to formally request a copy of all personal data your company holds on me, as per my rights under Article 15. Please confirm receipt.", 
            "label": "work", "department": "legal", 
            "ground_truth": {
                "label": "work", "department": "legal", 
                "reply_keywords": ["GDPR", "privacy", "compliance", "legal"]
            }
        }
    ]
}

TASK_ORDER = ["email-classification", "urgency-detection", "spam-filtering"]

# ==========================================================
# 🏗 ENVIRONMENT LOGIC (REFINED FOR DEEP VALIDATION)
# ==========================================================
class MyEnvironment(Environment):

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_email = None
        self.current_task_id = None
        self.ground_truth = None
        self.task_index = 0

    def reset(self, task_id=None, *args, **kwargs):
        """
        REFINED RESET: Now accepts task_id to allow the validator 
        to start specific evaluation levels.
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        
        # If the validator passes a specific task_id, we switch to it
        if task_id in TASKS:
            self.current_task_id = task_id
            self.task_index = TASK_ORDER.index(task_id)
        else:
            # Otherwise, start from the beginning
            self.task_index = 0
            self.current_task_id = TASK_ORDER[0]
            
        self.current_email = random.choice(TASKS[self.current_task_id])
        self.ground_truth = self.current_email["ground_truth"]
        
        # CRITICAL: 0.01 reward for range-safety during reset
        return MyObservation(
            email=self.current_email["email"],
            done=False,
            reward=0.01, 
            metadata={
                "task_id": self.current_task_id, 
                "instruction": self._get_instruction()
            }
        )

    def _get_instruction(self):
        if self.current_task_id == "email-classification":
            return "Classify intent. Set 'label' to: spam, personal, work, or urgent."
        elif self.current_task_id == "urgency-detection":
            return "Analyze urgency. Provide 'label', summary, and professional 'reply'."
        else:
            return "Enterprise Triage. Route to 'department' and draft a response."

    def step(self, action: MyAction, *args, **kwargs):
        """Executes one step and advances the internal task index."""
        self._state.step_count += 1
        
        # Grading logic
        reward = grade(
            task_id=self.current_task_id,
            state={"email": self.current_email["email"]},
            action=action,
            ground_truth=self.ground_truth,
        )
        
        # Move to next task in sequence
        self.task_index += 1
        done = self.task_index >= len(TASK_ORDER)
        
        # If not done, load the next item for the observation
        if not done:
            self.current_task_id = TASK_ORDER[self.task_index]
            self.current_email = random.choice(TASKS[self.current_task_id])
            self.ground_truth = self.current_email["ground_truth"]
        
        return MyObservation(
            email=self.current_email["email"],
            done=done,
            reward=float(reward),
            metadata={
                "task_id": self.current_task_id, 
                "instruction": self._get_instruction(), 
                "steps_taken": self._state.step_count
            }
        )

    @property
    def state(self):
        return self._state
