import asyncio
import json
import os
import textwrap
from typing import List, Optional
from openai import OpenAI
import httpx

# ── HACKATHON CONFIG (STRICT PROXY COMPLIANCE) ────────────
API_KEY = os.environ.get("API_KEY") or os.environ.get("HF_TOKEN")
API_BASE_URL = os.environ.get("API_BASE_URL")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
SPACE_URL = os.getenv("SPACE_URL", "http://localhost:7860")
BENCHMARK = "email-triage-env"
TASKS_TO_RUN = ["email-classification", "urgency-detection", "spam-filtering"]

# ── EXPERT PROMPTS (CHAIN-OF-THOUGHT & REFINEMENT) ────────
PRIMARY_PROMPT = "You are an expert Email Triage Agent. Analyze intent and enterprise routing using Chain-of-Thought. Respond ONLY with JSON: {'label': '...', 'summary': '[Reasoning]: ...', 'reply': '...', 'department': '...'}"
REVIEWER_PROMPT = "Quality Control: Review the draft JSON for accuracy and tone. Output ONLY final corrected JSON."

# ── STDOUT LOGGING (FIXED FOR DEEP VALIDATOR REGEX) ────────
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error or 'null'}", flush=True)

def log_end(task_id: str, success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    safe_score = max(0.01, min(0.99, score))
    # FIXED: Added task= to the [END] line as per Deep Validator requirements
    print(f"[END] task={task_id} success={str(success).lower()} steps={steps} score={safe_score:.3f} rewards={rewards_str}", flush=True)

# ── COLD-BOOT RESCUE (RETRIES FOR HF SLEEPING) ────────────
async def safe_post(http, url, json_data, max_retries=10):
    for i in range(max_retries):
        try:
            resp = await http.post(url, json=json_data)
            if resp.status_code == 200:
                return resp
            print(f"[DEBUG] HF Space waking up... (Status {resp.status_code}). Retry {i+1}", flush=True)
        except Exception:
            print(f"[DEBUG] Connection attempt {i+1} failed. Retrying...", flush=True)
        await asyncio.sleep(6) # Give the container time to boot
    raise Exception("HF Space failed to respond after multiple retries.")

# ── AGENT LOGIC (DUAL-STAGE REFINEMENT) ────────────────────
def get_action(client: OpenAI, email_text: str):
    try:
        # 1. Draft
        draft_res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": PRIMARY_PROMPT}, {"role": "user", "content": email_text}],
            temperature=0.7
        )
        draft = (draft_res.choices[0].message.content or "{}").strip()
        # 2. Refine
        final_res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": REVIEWER_PROMPT}, {"role": "user", "content": f"Orig: {email_text}\nDraft: {draft}"}],
            temperature=0.1
        )
        text = (final_res.choices[0].message.content or "{}").strip()
        if "```" in text: text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except:
        return {"label": "work", "summary": "Error", "reply": "Thank you.", "department": "none"}

# ── TASK EXECUTION (SYNCED WITH SERVER) ───────────────────
async def run_task(client: OpenAI, task_id: str):
    log_start(task_id, BENCHMARK, MODEL_NAME)
    rewards = []
    try:
        async with httpx.AsyncClient(timeout=60) as http:
            # 1. RESET (Now sending task_id to start specific level)
            resp = await safe_post(http, f"{SPACE_URL}/reset", {"task_id": task_id})
            obs_data = resp.json().get("observation", {})
            
            # 2. STEPS
            for step in range(1, 4):
                action = get_action(client, obs_data.get("email", ""))
                step_resp = await http.post(f"{SPACE_URL}/step", json=action)
                res = step_resp.json()
                
                reward = float(res.get("reward", 0.01))
                rewards.append(reward)
                log_step(step, json.dumps(action), reward, res.get("done", False), None)
                if res.get("done", False): break
                obs_data = res.get("observation", {})

        avg_score = sum(rewards) / len(rewards) if rewards else 0.01
        log_end(task_id, (avg_score >= 0.4), len(rewards), avg_score, rewards)
    except Exception as e:
        log_end(task_id, False, 0, 0.01, [0.01])

# ── MAIN ENTRY ────────────────────────────────────────────
async def main():
    if not API_KEY or not API_BASE_URL:
        print("[ERROR] API_KEY or API_BASE_URL missing.", flush=True)
        return
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    for task_name in TASKS_TO_RUN:
        await run_task(client, task_name)

if __name__ == "__main__":
    asyncio.run(main())
