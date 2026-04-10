from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import uvicorn, sys, os

# Ensures the server can find my_env_environment.py in the same folder
sys.path.insert(0, os.path.dirname(__file__))

from my_env_environment import MyEnvironment
from models import MyAction

app = FastAPI(title="Email Triage OpenEnv")
env = MyEnvironment()

@app.get("/")
def root(): 
    return RedirectResponse(url="/docs")

# FIX 1: Mandatory endpoint for the Judge's automated script
@app.get("/tasks")
def get_tasks():
    return ["email-classification", "urgency-detection", "spam-filtering"]

# FIX 2: Reset now accepts task_id to allow the judge to test specific levels
@app.post("/reset")
async def reset(request: Request):
    try:
        data = await request.json()
        task_id = data.get("task_id")
    except:
        task_id = None
    
    obs = env.reset(task_id=task_id)
    return {
        "observation": obs.dict(), 
        "reward": 0.01, 
        "done": False, 
        "info": obs.metadata
    }

@app.post("/step")
def step(action: dict):
    my_action = MyAction(**action)
    obs = env.step(my_action)
    return {
        "observation": obs.dict(), 
        "reward": float(obs.reward), 
        "done": obs.done, 
        "info": obs.metadata
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
