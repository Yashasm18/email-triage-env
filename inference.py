import asyncio
import json
import os
import textwrap
from typing import List, Optional
from openai import OpenAI
import httpx

# ── REQUIRED CONFIG ───────────────────────────────────────
API_KEY = os.getenv("HF_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
SPACE_URL = os.getenv("SPACE_URL", "http://localhost:7860")
BENCHMARK = "email-triage-env"
TASKS_TO_RUN = ["email-classification", "urgency-detection", "spam-filtering"]

# ── EXPERT SYSTEM PROMPT ──────────────────────────────────
SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an expert Enterprise Email Triage Agent. 
    Respond with a JSON object containing:
    - "label": (spam, personal, work, urgent)
    - "summary": A professional 1-sentence summary.
    - "reply": A professional, empathetic response.
    - "department": Route to (engineering, support, sales, billing, legal, security, management, or none).

    ROUTING RULES:
    - Technical issues -> 'engineering'
    - Security threats -> 'security'
    - Refunds/Charges -> 'billing'
    - GDPR/Legal -> 'legal'
    
    Respond ONLY with valid JSON.
    """
).strip()

# ── LOGGING ───────────────────────────────────────────────
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    err = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={err}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    safe_score = max(0.01, min(0.99, score))
    print(f"[END] success={str(success).lower()} steps={steps} score={safe_score:.3f} rewards={rewards_str}", flush=True)

# ── LLM LOGIC ─────────────────────────────────────────────
def get_action(client: OpenAI, email_text: str):
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Triage email: {email_text}"}
            ],
            temperature=0.3,
            max_tokens=300
        )
        text = (completion.choices[0].message.content or "{}").strip()
        if "```json" in text: text = text.split("```json")[1].split("```")[0]
        elif "```" in text: text = text.split("```")[1].split("```")[0]
        return json.loads(text)
    except Exception:
        return {"label": "work", "summary": "Error", "reply": "Error", "department": "none"}

# ── RUN ───────────────────────────────────────────────────
async def run_task(client: OpenAI, task_id: str):
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    rewards = []
    try:
        async with httpx.AsyncClient(timeout=30) as http:
            resp = await http.post(f"{SPACE_URL}/reset")
            obs = resp.json().get("observation", {})
            for step in range(1, 4):
                action = get_action(client, obs.get("email", ""))
                step_resp = await http.post(f"{SPACE_URL}/step", json=action)
                res = step_resp.json()
                reward = float(res.get("reward", 0.01))
                rewards.append(reward)
                log_step(step, json.dumps(action), reward, res.get("done", False), None)
                if res.get("done", False): break
                obs = res.get("observation", {})
        score = sum(rewards) / len(rewards) if rewards else 0.01
        log_end(success=(score >= 0.4), steps=len(rewards), score=score, rewards=rewards)
    except Exception:
        log_end(success=False, steps=0, score=0.01, rewards=[0.01])

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY or "placeholder")
    for task in TASKS_TO_RUN:
        await run_task(client, task)

if __name__ == "__main__":
    asyncio.run(main())
