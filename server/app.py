from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import uvicorn, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from my_env_environment import MyEnvironment
from models import MyAction

app = FastAPI(title="Email Triage OpenEnv")
env = MyEnvironment()

@app.get("/")
def root(): return RedirectResponse(url="/docs")

# NEW: Required by Deep Validator
@app.get("/tasks")
def get_tasks():
    return ["email-classification", "urgency-detection", "spam-filtering"]

# FIXED: Now accepts task_id from validator
@app.post("/reset")
async def reset(request: Request):
    data = await request.json()
    task_id = data.get("task_id")
    obs = env.reset(task_id=task_id)
    return {"observation": obs.dict(), "reward": 0.01, "done": False, "info": obs.metadata}

@app.post("/step")
def step(action: dict):
    my_action = MyAction(**action)
    obs = env.step(my_action)
    return {"observation": obs.dict(), "reward": float(obs.reward), "done": obs.done, "info": obs.metadata}
