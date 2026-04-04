from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

try:
    from my_env_environment import MyEnvironment
    from models import MyAction, MyObservation
except ImportError:
    from .my_env_environment import MyEnvironment
    from .models import MyAction, MyObservation

app = FastAPI(title="Email Triage OpenEnv")

# Global environment instance
env = MyEnvironment()


class ResetResponse(BaseModel):
    observation: dict
    reward: float = 0.0
    done: bool = False
    info: dict = {}


class StepRequest(BaseModel):
    label: Optional[str] = None
    summary: Optional[str] = None
    reply: Optional[str] = None
    department: Optional[str] = None


class StepResponse(BaseModel):
    observation: dict
    reward: float
    done: bool
    info: dict = {}


class StateResponse(BaseModel):
    episode_id: str
    step_count: int


@app.post("/reset")
def reset():
    obs = env.reset()
    return {
        "observation": obs.dict(),
        "reward": 0.0,
        "done": False,
        "info": obs.metadata,
    }


@app.post("/step")
def step(action: StepRequest):
    my_action = MyAction(
        label=action.label,
        summary=action.summary,
        reply=action.reply,
        department=action.department,
    )
    obs = env.step(my_action)
    return {
        "observation": obs.dict(),
        "reward": obs.reward,
        "done": obs.done,
        "info": obs.metadata,
    }


@app.get("/state")
def state():
    s = env.state
    return {
        "episode_id": s.episode_id,
        "step_count": s.step_count,
    }


@app.get("/")
def root():
    return {"status": "ok", "message": "Email Triage OpenEnv is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
