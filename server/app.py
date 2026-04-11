from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import uvicorn, sys, os

# Ensures the server can find my_env_environment.py in the same folder
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from my_env_environment import MyEnvironment
from models import MyAction
from grader import grade

app = FastAPI(title="Email Triage OpenEnv")
env = MyEnvironment()

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {"id": "easy", "description": "Classify email label only", "difficulty": "easy", "reward_range": [0.01, 0.99]},
            {"id": "medium", "description": "Classify + summarize + reply", "difficulty": "medium", "reward_range": [0.01, 0.99]},
            {"id": "hard", "description": "Classify + department + summarize + reply", "difficulty": "hard", "reward_range": [0.01, 0.99]}
        ]
    }

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

@app.post("/grader")
async def run_grader(request: Request):
    data = await request.json()
    task_id = data.get("task_id", "easy")
    action_data = data.get("action", {})
    ground_truth = data.get("ground_truth", {"label": "work"})

    action = MyAction(**action_data)
    reward, feedback = grade(task_id, {}, action, ground_truth)

    return {"task_id": task_id, "reward": reward, "feedback": feedback}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
