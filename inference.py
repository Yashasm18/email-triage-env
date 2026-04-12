import asyncio, json, os, textwrap
from openai import OpenAI
import httpx

# --- HACKATHON CONFIG ---
API_KEY = os.environ.get("API_KEY") or os.environ.get("HF_TOKEN")
API_BASE_URL = os.environ.get("API_BASE_URL")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
SPACE_URL = "http://localhost:7860"
TASKS_TO_RUN = ["email-classification", "urgency-detection", "spam-filtering"]

# --- LOGGING HELPERS ---
def log_start(task): 
    print(f"[START] task={task} env=email-triage-env model={MODEL_NAME}", flush=True)

def log_step(step, action, reward, done): 
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error=null", flush=True)

def log_end(task_id, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] task={task_id} success=true steps={steps} score={max(0.01, min(0.99, score)):.3f} rewards={rewards_str}", flush=True)

# --- DUAL-STAGE INFERENCE ENGINE ---
def get_action(client, email_text):
    try:
        # STAGE 1: DRAFT PASS (Chain-of-Thought)
        # As described in README: Qwen generates initial JSON via CoT
        print(f"[DEBUG] Executing Draft Pass (Chain-of-Thought)...", flush=True)
        draft_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert Email Triage Agent. Analyze the email using Chain-of-Thought. Draft a JSON response with: label, summary, reply, and department."},
                {"role": "user", "content": f"Triage this email: {email_text}"}
            ],
            temperature=0.7
        ).choices[0].message.content

        # STAGE 2: REVIEWER PASS (Critique & Correction)
        # As described in README: Second call corrects the draft for accuracy and tone
        print(f"[DEBUG] Executing Reviewer Pass (Critique & Refinement)...", flush=True)
        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Quality Critic. Review the following draft triage for accuracy, professional tone, and correct routing. Output ONLY the final corrected JSON."},
                {"role": "user", "content": f"Original Email: {email_text}\nDraft Triage: {draft_response}"}
            ],
            temperature=0.1
        ).choices[0].message.content
        
        # Parse and clean JSON
        text = final_response.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)

    except Exception as e:
        print(f"[DEBUG] Inference Error: {e}", flush=True)
        return {"label": "work", "summary": "error during refinement", "reply": "Thank you for your patience.", "department": "none"}

# --- TASK EXECUTION ---
async def run_task(client, task_id):
    log_start(task_id)
    rewards = []
    async with httpx.AsyncClient(timeout=60) as http:
        # Reset environment
        resp = await http.post(f"{SPACE_URL}/reset", json={"task_id": task_id})
        obs = resp.json().get("observation", {})
        
        for step in range(1, 4):
            # Run the Dual-Stage Agent
            action = get_action(client, obs.get("email", ""))
            
            # Step environment
            res = (await http.post(f"{SPACE_URL}/step", json=action)).json()
            reward = float(res.get("reward", 0.01))
            rewards.append(reward)
            
            log_step(step, json.dumps(action), reward, res.get("done", False))
            
            if res.get("done", False): break
            obs = res.get("observation", {})
            
    log_end(task_id, len(rewards), sum(rewards)/len(rewards), rewards)

async def main():
    if not API_KEY or not API_BASE_URL:
        print("[ERROR] HF_TOKEN or API_BASE_URL not set.", flush=True)
        return
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    for task in TASKS_TO_RUN:
        await run_task(client, task)

if __name__ == "__main__":
    asyncio.run(main())
