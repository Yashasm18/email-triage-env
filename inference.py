import asyncio
import json
import os
import re

from openai import OpenAI
import httpx

# ── Config ───────────────────────────────────────────────────────────────────
API_KEY      = os.environ.get("API_KEY") or os.environ.get("HF_TOKEN")
API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
SPACE_URL    = os.environ.get("SPACE_URL", "http://localhost:7860")

# ── Logging helpers (format expected by OpenEnv leaderboard) ─────────────────
def log_start(task_id):
    print(
        f"[START] task={task_id} env=email-triage-env model={MODEL_NAME}",
        flush=True,
    )

def log_step(step, action, reward, done):
    print(
        f"[STEP] step={step} action={json.dumps(action)} "
        f"reward={reward:.2f} done={str(done).lower()} error=null",
        flush=True,
    )

def log_end(task_id, steps, avg_score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] task={task_id} success=true steps={steps} "
        f"score={max(0.01, min(0.99, avg_score)):.3f} rewards={rewards_str}",
        flush=True,
    )


# ── Dual-stage inference ─────────────────────────────────────────────────────
def _extract_json(text: str) -> dict:
    """Strip markdown fences and parse the first JSON object found."""
    # Remove ```json ... ``` or ``` ... ``` fences
    text = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fallback: find first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    # Safe default
    return {"label": "work", "summary": "Unable to parse response.", "reply": "error", "department": "none"}


def get_dual_action(client: OpenAI, email: str, instruction: str) -> dict:
    """
    Two-pass LLM inference:
      Pass 1 — Draft: generate an initial triage action via Chain-of-Thought.
      Pass 2 — Review: critique and refine the draft for accuracy and tone.
    Returns a dict with keys: label, summary, reply, department.
    """
    SYSTEM_DRAFT = (
        "You are an expert email triage assistant. "
        "Given an email and an instruction, produce a JSON object with these fields:\n"
        "  label      (one of: spam, personal, work, urgent)\n"
        "  summary    (one sentence describing the email's core issue)\n"
        "  reply      (a professional, empathetic reply draft)\n"
        "  department (one of: engineering, support, sales, billing, marketing, "
        "legal, security, management, none)\n\n"
        "Think step-by-step before producing JSON."
    )

    SYSTEM_REVIEW = (
        "You are a senior email triage reviewer. "
        "You are given an email, an instruction, and a draft triage JSON. "
        "Your job: fix any errors in label, improve the reply to be professional "
        "and include relevant keywords (e.g. apologize, resolve, escalate, investigate), "
        "and confirm the correct department. "
        "Output ONLY a valid JSON object — no markdown, no explanation."
    )

    try:
        # ── Pass 1: Draft ────────────────────────────────────────────────────
        draft_resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_DRAFT},
                {"role": "user", "content": f"Instruction: {instruction}\n\nEmail:\n{email}"},
            ],
            max_tokens=512,
            temperature=0.3,
        )
        draft_text = draft_resp.choices[0].message.content.strip()

        # ── Pass 2: Review ───────────────────────────────────────────────────
        review_resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_REVIEW},
                {
                    "role": "user",
                    "content": (
                        f"Instruction: {instruction}\n\n"
                        f"Email:\n{email}\n\n"
                        f"Draft:\n{draft_text}"
                    ),
                },
            ],
            max_tokens=512,
            temperature=0.1,
        )
        final_text = review_resp.choices[0].message.content.strip()
        return _extract_json(final_text)

    except Exception as exc:
        print(f"[WARN] LLM call failed: {exc}", flush=True)
        return {
            "label": "work",
            "summary": "Error during inference.",
            "reply": "Thank you for your email. We will get back to you shortly.",
            "department": "none",
        }


# ── Task runner ──────────────────────────────────────────────────────────────
async def run_task(client: OpenAI, task_id: str):
    log_start(task_id)
    rewards = []

    async with httpx.AsyncClient(timeout=60) as http:
        # Reset — pass task_id so the env starts at the right difficulty
        resp = await http.post(f"{SPACE_URL}/reset", json={"task_id": task_id})
        resp.raise_for_status()
        data = resp.json()
        obs  = data.get("observation", {})
        instruction = obs.get("metadata", {}).get("instruction", "Triage this email.")

        for step_num in range(1, 4):
            email = obs.get("email", "")
            if not email:
                break

            action = get_dual_action(client, email, instruction)

            step_resp = await http.post(f"{SPACE_URL}/step", json=action)
            step_resp.raise_for_status()
            result = step_resp.json()

            reward = float(result.get("reward", 0.01))
            done   = result.get("done", False)
            rewards.append(reward)
            log_step(step_num, action, reward, done)

            if done:
                break

            obs = result.get("observation", {})
            instruction = obs.get("metadata", {}).get("instruction", "Triage this email.")

    avg_score = sum(rewards) / len(rewards) if rewards else 0.01
    log_end(task_id, len(rewards), avg_score, rewards)


# ── Entry point ──────────────────────────────────────────────────────────────
async def main():
    if not API_KEY:
        print("[ERROR] No API_KEY or HF_TOKEN set — skipping inference.", flush=True)
        return
    if not API_BASE_URL:
        print("[ERROR] No API_BASE_URL set — skipping inference.", flush=True)
        return

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    # Task IDs match openenv.yaml and my_env_environment.py exactly
    for task_id in ["email-classification", "urgency-detection", "spam-filtering"]:
        await run_task(client, task_id)


if __name__ == "__main__":
    asyncio.run(main())
