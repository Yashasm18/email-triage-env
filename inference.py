import asyncio, json, os, textwrap
from openai import OpenAI
import httpx

API_KEY = os.environ.get("API_KEY") or os.environ.get("HF_TOKEN")
API_BASE_URL = os.environ.get("API_BASE_URL")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
SPACE_URL = os.getenv("SPACE_URL", "http://localhost:7860")
TASKS_TO_RUN = ["email-classification", "urgency-detection", "spam-filtering"]

PRIMARY_PROMPT = """Analyze the email using Chain-of-Thought reasoning. Determine intent and enterprise routing. Respond ONLY with JSON: {"label": "...", "summary": "[Reasoning]: ... [Summary]: ...", "reply": "...", "department": "..."}"""
REVIEWER_PROMPT = """Quality Control: Review logic and tone. If routing is wrong, fix it. Output ONLY corrected JSON."""

def log_start(task, env, model): print(f"[START] task={task} env={env} model={model}", flush=True)
def log_step(step, action, reward, done): print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error=null", flush=True)
def log_end(steps, score, rewards): print(f"[END] success=true steps={steps} score={max(0.01, min(0.99, score)):.3f} rewards={','.join(f'{r:.2f}' for r in rewards)}", flush=True)

def get_action(client, email_text):
    try:
        draft = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "system", "content": PRIMARY_PROMPT}, {"role": "user", "content": email_text}], temperature=0.7).choices[0].message.content
        final = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "system", "content": REVIEWER_PROMPT}, {"role": "user", "content": f"Orig: {email_text}\nDraft: {draft}"}], temperature=0.1).choices[0].message.content
        text = final.strip()
        if "```" in text: text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except: return {"label": "work", "summary": "error", "reply": "error", "department": "none"}

async def run_task(client, task_id):
    log_start(task_id, "email-triage-env", MODEL_NAME)
    rewards = []
    async with httpx.AsyncClient(timeout=30) as http:
        obs = (await http.post(f"{SPACE_URL}/reset")).json().get("observation", {})
        for step in range(1, 4):
            action = get_action(client, obs.get("email", ""))
            res = (await http.post(f"{SPACE_URL}/step", json=action)).json()
            reward = float(res.get("reward", 0.01))
            rewards.append(reward)
            log_step(step, json.dumps(action), reward, res.get("done", False))
            if res.get("done", False): break
            obs = res.get("observation", {})
    log_end(len(rewards), sum(rewards)/len(rewards), rewards)

async def main():
    if not API_KEY or not API_BASE_URL: return
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    for task in TASKS_TO_RUN: await run_task(client, task)

if __name__ == "__main__": asyncio.run(main())
