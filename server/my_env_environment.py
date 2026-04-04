from uuid import uuid4
import random

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import MyAction, MyObservation
except ImportError:
    from models import MyAction, MyObservation


class MyEnvironment(Environment):

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current = None

        # 🔥 FULL DATASET (30 emails)
        self.emails = [
            # 🔴 SPAM
            {"email": "Win a free iPhone now!!! Click here"},
            {"email": "Congratulations! You have won a lottery prize"},
            {"email": "Limited time offer! Buy now and save big"},
            {"email": "Your bank account needs verification, click here"},
            {"email": "Get rich quick scheme, earn $5000 per day"},
            {"email": "Claim your free vacation tickets now"},
            {"email": "Exclusive reward waiting for you, click now"},
            {"email": "Act fast! Offer expires in 2 hours"},
            {"email": "Earn money online with zero investment"},
            {"email": "You have been selected for a special bonus"},

            # 🟢 WORK / IMPORTANT
            {"email": "Reminder: submit your project report by tomorrow"},
            {"email": "Meeting rescheduled to 3 PM tomorrow"},
            {"email": "Client feedback received, please review the document"},
            {"email": "URGENT: Production server is down, fix immediately"},
            {"email": "Your Amazon order has been shipped"},
            {"email": "Please review the attached contract and provide feedback"},
            {"email": "Team meeting agenda for Monday attached"},
            {"email": "Deadline extended for submission by two days"},
            {"email": "Project update required by end of day"},
            {"email": "Your interview is scheduled for tomorrow at 10 AM"},

            # 🟡 PERSONAL
            {"email": "Hey, are we still on for dinner tonight?"},
            {"email": "Happy birthday! Have a great day!"},
            {"email": "Let’s catch up this weekend"},
            {"email": "Can you call me when you’re free?"},
            {"email": "Don’t forget the party this Saturday"},

            # ⚠️ EDGE CASES
            {"email": "Security alert: suspicious login attempt detected"},
            {"email": "Final notice: your subscription is expiring"},
            {"email": "Invoice attached for your recent purchase"},
            {"email": "Your account will be locked unless you verify now"},
            {"email": "Important update regarding your account security"}
        ]

    # ✅ RESET
    def reset(self, *args, **kwargs):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current = random.choice(self.emails)

        return MyObservation(
            email=self.current["email"],
            done=False,
            reward=0.0
        )

    # ✅ STEP
    def step(self, action, *args, **kwargs):
        if self.current is None:
            self.current = random.choice(self.emails)

        self._state.step_count += 1

        return MyObservation(
            email=self.current["email"],
            done=True,
            reward=0.0,
            metadata={
                "message": "Processed successfully"
            }
        )

    # ✅ STATE (required)
    @property
    def state(self):
        return self._state
