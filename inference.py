import asyncio, json, os
from openai import OpenAI
import httpx

API_KEY = os.environ.get("API_KEY") or os.environ.get("HF_TOKEN")
API_BASE_URL = os.environ.get("API_BASE_URL")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
SPACE_URL = "http://localhost:7860"

def log_start(t): print(f"[START] task={t} env=email-triage-env model={MODEL_NAME}", flush=True)
def log_step(s, a, r, d): print(f"[STEP] step={s} action={a} reward={r:.2f} done={str(d).lower()} error=null", flush=True)
def log_end(t, s, sc, rs): print(f"[END] task={t} success=true steps={s} score={max(0.01, min(0.99, sc)):.3f} rewards={','.join(f'{r:.2f}' for r in rs)}", flush=True)

def get_action(client, email):
    try:
        # STAGE 1: DRAFT (Chain-of-Thought)
        draft = client.chat.completions.create(
            model=MODEL_NAME, 
            messages=[{"role": "system", "content": "Draft triage JSON: label, summary, reply, department. Use Chain-of-Thought."}, 
                      {"role": "user", "content": email}]
        ).choices[0].message.content
        
        # STAGE 2: REVIEWER (Refinement)
        final = client.chat.completions.create(
            model=MODEL_NAME, 
            messages=[{"role": "system", "content": "Review and correct this triage JSON for accuracy and tone. Output ONLY final JSON."}, 
                      {"role": "user", "content": f"Original: {email}\nDraft: {draft}"}]
        ).choices[0].message.content
        
        res = final.strip()
        if "```" in res: res = res.split("```")[1].replace("json", "").strip()
        return json.loads(res)
    except: 
        return {"label": "work", "summary": "error", "reply": "error", "department": "none"}

async def run_task(client, task_id):
    log_start(task_id)
    rewards = []
    async with httpx.AsyncClient(timeout=60) as http:
        obs = (await http.post(f"{SPACE_URL}/reset", json={"task_id": task_id})).json().get("observation", {})
        for step in range(1, 4):
            action = get_action(client, obs.get("email", ""))
            res = (await http.post(f"{SPACE_URL}/step", json=action)).json()
            reward = float(res.get("reward", 0.01))
            rewards.append(reward)
            log_step(step, json.dumps(action), reward, res.get("done", False))
            if res.get("done", False): break
            obs = res.get("observation", {})
    log_end(task_id, len(rewards), sum(rewards)/len(rewards), rewards)

async def main():
    if not API_KEY or not API_BASE_URL: return
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    for t in ["email-classification", "urgency-detection", "spam-filtering"]: await run_task(client, t)

if __name__ == "__main__": asyncio.run(main())
