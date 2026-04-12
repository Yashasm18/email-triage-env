try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError("openenv is required") from e

try:
    from ..models import MyAction, MyObservation
    from .my_env_environment import MyEnvironment
except Exception:
    from models import MyAction, MyObservation
    from server.my_env_environment import MyEnvironment

from grader import grade
from fastapi import Request

app = create_app(
    MyEnvironment,
    MyAction,
    MyObservation,
    env_name="my_env",
    max_concurrent_envs=1,
)

@app.get("/health", tags=["meta"])
def health():
    """Liveness probe — returns 200 when server is ready."""
    return {"status": "ok"}

@app.get("/tasks", tags=["meta"])
def get_tasks():
    """List all available tasks with difficulty levels."""
    return {
        "tasks": [
            {"id": "email-classification", "description": "Classify email intent only", "difficulty": "easy", "reward_range": [0.01, 0.99]},
            {"id": "urgency-detection", "description": "Classify + summarize + reply", "difficulty": "medium", "reward_range": [0.01, 0.99]},
            {"id": "spam-filtering", "description": "Classify + department + summarize + reply", "difficulty": "hard", "reward_range": [0.01, 0.99]}
        ]
    }

@app.post("/grader", tags=["meta"])
async def run_grader(request: Request):
    """Grade a specific action against ground truth."""
    data = await request.json()
    task_id = data.get("task_id", "email-classification")
    action_data = data.get("action", {})
    ground_truth = data.get("ground_truth", {"label": "work"})
    action = MyAction(**action_data)
    reward, feedback = grade(task_id, {}, action, ground_truth)
    return {"task_id": task_id, "reward": reward, "feedback": feedback}

def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
