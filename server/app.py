try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError("openenv is required") from e

try:
    from ..models import MyAction, MyObservation
    from .my_env_environment import MyEnvironment
except Exception:
    from models import MyAction, MyObservation
    from server.my_env_environment import MyEnvironment, keyword_score

app = create_app(
    MyEnvironment,
    MyAction,
    MyObservation,
    env_name="my_env",
    max_concurrent_envs=1,
)

@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {"id": "easy", "description": "Classify email label", "difficulty": "easy", "grader": "EasyTaskRubric", "reward_range": [0.01, 0.99]},
            {"id": "medium", "description": "Classify + summary + reply", "difficulty": "medium", "grader": "MediumTaskRubric", "reward_range": [0.01, 0.99]},
            {"id": "hard", "description": "Classify + department + summary + reply", "difficulty": "hard", "grader": "HardTaskRubric", "reward_range": [0.01, 0.99]}
        ]
    }

@app.post("/grader")
async def run_grader(request: dict):
    task_id = request.get("task_id", "easy")
    action_data = request.get("action", {})
    ground_truth = request.get("ground_truth", {"label": "work"})
    action = MyAction(**action_data)
    reward = 0.0
    if task_id == "easy":
        if action.label == ground_truth.get("label"):
            reward = 0.85
        elif action.label in ["spam", "personal", "work", "urgent"]:
            reward = 0.15
    elif task_id == "medium":
        if action.label == ground_truth.get("label"):
            reward += 0.45
        elif action.label in ["spam", "personal", "work", "urgent"]:
            reward += 0.08
        if action.summary and len(action.summary) > 10:
            reward += 0.20
        kws = ground_truth.get("reply_keywords", [])
        if action.reply and kws:
            reward += 0.25 * keyword_score(action.reply, kws)
    elif task_id == "hard":
        if action.label == ground_truth.get("label"):
            reward += 0.35
        elif action.label in ["spam", "personal", "work", "urgent"]:
            reward += 0.06
        if action.summary and len(action.summary) > 10:
            reward += 0.15
        kws = ground_truth.get("reply_keywords", [])
        if action.reply and kws:
            reward += 0.20 * keyword_score(action.reply, kws)
        if action.department == ground_truth.get("department"):
            reward += 0.20
        elif action.department and action.department != "none":
            reward += 0.04
    reward = min(max(reward, 0.01), 0.99)
    return {"task_id": task_id, "reward": reward}

def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
