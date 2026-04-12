import sys, os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from openenv import create_app

# Add directory to path for local imports
sys.path.insert(0, os.path.dirname(__file__))

from my_env_environment import MyEnvironment
from models import MyAction, MyObservation

# 1. Initialize Expert Environment
env = MyEnvironment()

# 2. Create the App with Playground UI
app = create_app(env, action_cls=MyAction, observation_cls=MyObservation)

# 3. Additional Endpoints from README
@app.get("/health")
def health():
    return {"status": "healthy", "version": "0.1.0"}

@app.get("/tasks")
def get_tasks():
    return ["email-classification", "urgency-detection", "spam-filtering"]

@app.post("/grader")
async def manual_grader(request: Request):
    # Allows manual grading of an action against ground truth via API
    data = await request.json()
    from grader import grade
    reward = grade(data.get("task_id"), None, MyAction(**data.get("action")), data.get("ground_truth"))
    return {"reward": reward}
