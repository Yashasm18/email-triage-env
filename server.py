from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from my_env_environment import MyEnvironment
from models import MyAction

app = FastAPI(title="Email Triage OpenEnv")
env = MyEnvironment()

@app.get("/")
def root(): return RedirectResponse(url="/docs")

@app.post("/reset")
def reset():
    obs = env.reset()
    return {"observation": obs.dict(), "reward": 0.01, "done": False, "info": obs.metadata}

@app.post("/step")
def step(action: dict):
    my_action = MyAction(**action)
    obs = env.step(my_action)
    return {"observation": obs.dict(), "reward": float(obs.reward), "done": obs.done, "info": obs.metadata}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
