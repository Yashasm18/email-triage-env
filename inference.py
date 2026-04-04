"""
Inference Script — Email Triage OpenEnv
========================================
MANDATORY env vars before running:
  API_BASE_URL   The API endpoint for the LLM
  MODEL_NAME     The model identifier to use for inference
  HF_TOKEN       Your Hugging Face / API key
  LOCAL_IMAGE_NAME  (optional) if using from_docker_image()

Defaults set only for API_BASE_URL and MODEL_NAME.
HF_TOKEN has no default — must be set externally.
"""

import asyncio
import json
import os
import textwrap
from typing import List, Optional

from openai import OpenAI
import httpx

# ── Config ────────────────────────────────────────────────
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
SPACE_URL = os.getenv("SPACE_URL", "https://souller-email-triage-env.hf.space")
TASK_NAME = os.getenv("TASK_NAME", "email-triage")
BENCHMARK = os.getenv("BENCHMARK", "email-triage-env")

MAX_STEPS = 3
TEMPERATURE = 0.3
MAX_TOKENS = 300
SUCCESS_SCORE_THRESHOLD = 0.4

# ── Logging helpers ───────────────────────────────────────
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ── System prompt ─────────────────────────────────────────
SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an expert email triage assistant.
    You will receive an email and must respond with a JSON object containing:
    - "label": one of spam, personal, work, urgent
    - "summary": a brief 1-2 sentence summary of the email
    - "reply": a short professional reply draft
    - "department": the department to route to (engineering, support, sales, billing, marketing, legal, security, management, none)

    Respond ONLY with a valid JSON object. No extra text, no markdown, no explanation.
    Example:
    {"label": "urgent", "summary": "Server is down.", "reply": "We are investigating immediately.", "department": "engineering"}
    """
).strip()


def get_action(client: OpenAI, email_text: str, step: int) -> dict:
    user_prompt = f"Step: {step}\nEmail:\n{email_text}\n\nRespond with JSON only."
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "{}").strip()
        # Strip markdown if model wraps in ```json
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return {"label": "work", "summary": "Unable to process.", "reply": "Thank you for your email.", "department": "none"}


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        # ── Reset environment ──────────────────────────────
        async with httpx.AsyncClient(timeout=30) as http:
            reset_resp = await http.post(f"{SPACE_URL}/reset", json={})
            reset_resp.raise_for_status()
            reset_data = reset_resp.json()

        obs = reset_data.get("observation", {})
        done = reset_data.get("done", False)

        for step in range(1, MAX_STEPS + 1):
            if done:
                break

            email_text = obs.get("email", "")
            action_dict = get_action(client, email_text, step)
            action_str = json.dumps(action_dict, separators=(",", ":"))

            # ── Step environment ───────────────────────────
            async with httpx.AsyncClient(timeout=30) as http:
                step_resp = await http.post(f"{SPACE_URL}/step", json=action_dict)
                step_resp.raise_for_status()
                step_data = step_resp.json()

            obs = step_data.get("observation", {})
            reward = float(step_data.get("reward", 0.0))
            done = step_data.get("done", False)
            error = None

            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action=action_str, reward=reward, done=done, error=error)

            if done:
                break

        score = sum(rewards) / len(rewards) if rewards else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Episode error: {exc}", flush=True)
        if not rewards:
            rewards = [0.0]

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
