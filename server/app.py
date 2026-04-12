from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from my_env_environment import MyEnvironment
from models import MyAction

app = FastAPI(
    title="Email Triage OpenEnv",
    description=(
        "Agentic RL benchmark for enterprise email triage. "
        "Agents classify, summarise, route, and reply to emails "
        "across three difficulty levels."
    ),
    version="1.0.0",
)
env = MyEnvironment()


# ── Root → Swagger UI (keeps the default OpenEnv playground intact) ──────────
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


# ── Health check (required by Dockerfile HEALTHCHECK) ───────────────────────
@app.get("/health", tags=["meta"])
def health():
    """Liveness probe — returns 200 when the server is ready."""
    return {"status": "ok"}


# ── Environment endpoints ────────────────────────────────────────────────────

@app.get("/tasks", tags=["meta"])
def get_tasks():
    """List all available task IDs."""
    return ["email-classification", "urgency-detection", "spam-filtering"]


@app.post("/reset", tags=["environment"])
async def reset(request: Request):
    """
    Start a new episode.

    Optionally pass ``{"task_id": "email-classification"}`` (or
    ``"urgency-detection"`` / ``"spam-filtering"``) to jump directly
    to a specific task. If omitted the environment starts from the
    beginning of the difficulty progression.
    """
    try:
        data = await request.json()
    except Exception:
        data = {}

    task_id = data.get("task_id") if data else None
    obs = env.reset(task_id=task_id)
    return {
        "observation": obs.dict(),
        "reward": obs.reward,
        "done": obs.done,
        "info": obs.metadata,
    }


@app.post("/step", tags=["environment"])
def step(action: dict):
    """
    Submit a ``MyAction`` and receive a reward + next observation.

    Required fields (depending on task difficulty):
    - ``label``      — always required
    - ``summary``    — required for urgency-detection and spam-filtering
    - ``reply``      — required for urgency-detection and spam-filtering
    - ``department`` — required for spam-filtering
    """
    obs = env.step(MyAction(**action))
    return {
        "observation": obs.dict(),
        "reward": float(obs.reward),
        "done": obs.done,
        "info": obs.metadata,
    }


@app.get("/state", tags=["environment"])
def state():
    """Return the current episode ID and step count."""
    s = env.state
    return {"episode_id": s.episode_id, "step_count": s.step_count}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
