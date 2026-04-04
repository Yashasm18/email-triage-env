import asyncio
import os
import json
from openai import AsyncOpenAI
from openenv.core.env_client.client import EnvClient

try:
    from models import MyAction
except ImportError:
    from my_env.models import MyAction

API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
DOCKER_IMAGE = os.environ.get("DOCKER_IMAGE", "my_env")
MAX_STEPS = 10
MAX_TOTAL_REWARD = 3.0
SUCCESS_SCORE_THRESHOLD = 0.5

def log_start(task_id):
    print(json.dumps({"type": "START", "task_id": task_id}), flush=True)

def log_step(step, action, reward, done, error=None):
    print(json.dumps({"type": "STEP", "step": step, "action": action, "reward": reward, "done": done, "error": str(error) if error else None}), flush=True)

def log_end(success, steps, score, rewards):
    print(json.dumps({"type": "END", "success": success, "steps": steps, "score": score, "rewards": rewards}), flush=True)

async def get_model_action(client, email, instruction, history):
    system_prompt = """You are an expert email triage assistant.
For each email, respond with a JSON object:
- label: one of spam/personal/work/urgent
- summary: 1-2 sentence summary
- reply: professional reply
- department: engineering/support/sales/billing/marketing/legal/security/management/none

Respond ONLY with valid JSON."""

    user_msg = f"Instruction: {instruction}\n\nEmail: {email}"
    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=500,
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    try:
        data = json.loads(text)
        return MyAction(
            label=data.get("label"),
            summary=data.get("summary"),
            reply=data.get("reply"),
            department=data.get("department"),
        )
    except Exception:
        return MyAction(label="work", summary=text[:100], reply="Thank you.", department="none")

async def run_task(task_id):
    log_start(task_id)
    client = AsyncOpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)
    rewards = []
    steps_taken = 0

    try:
        env = EnvClient(image=DOCKER_IMAGE)
        result = await env.reset()
        obs = result.observation

        for step in range(MAX_STEPS):
            instruction = obs.metadata.get("instruction", "Classify this email.")
            action = await get_model_action(client, obs.email, instruction, [])
            result = await env.step(action)
            obs = result.observation
            reward = result.reward or 0.0
            done = result.done
            rewards.append(reward)
            steps_taken = step + 1
            log_step(step=step, action=str(action.label), reward=reward, done=done)
            if done:
                break

        score = min(max(sum(rewards) / MAX_TOTAL_REWARD, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD
    except Exception as e:
        score = 0.0
        success = False
        print(f"[DEBUG] Error: {e}", flush=True)
    finally:
        try:
            await env.close()
        except Exception:
            pass
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

async def main():
    for task_id in ["easy", "medium", "hard"]:
        await run_task(task_id)

if __name__ == "__main__":
    asyncio.run(main())