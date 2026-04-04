# Email Triage OpenEnv

A real-world OpenEnv environment where an AI agent triages emails by classifying, summarizing, routing, and replying to them — with increasing difficulty across 3 task levels.

---

## Environment Description

Email triage is a task every professional does daily. This environment simulates an inbox where an agent must:
- Classify emails (spam, personal, work, urgent)
- Summarize email content
- Draft professional replies
- Route emails to the correct department

---

## Action Space

| Field | Type | Values | Required |
|-------|------|--------|----------|
| `label` | string | spam, personal, work, urgent | All tasks |
| `summary` | string | Free text | Medium + Hard |
| `reply` | string | Free text | Medium + Hard |
| `department` | string | engineering, support, sales, billing, marketing, legal, security, management, none | Hard only |

## Observation Space

| Field | Type | Description |
|-------|------|-------------|
| `email` | string | The email text to process |
| `done` | boolean | Whether the episode is complete |
| `reward` | float | Reward from the last action (0.0–1.0) |
| `metadata` | object | Contains task_id, instruction, steps_taken |

---

## Tasks

### Easy
Classify the email label only.
- Reward: 0.5 for correct label, 0.1 for valid but wrong label
- Example: `{"label": "spam"}`

### Medium
Classify label + write a summary + draft a reply.
- Reward: label (0.5) + summary relevance (0.2) + reply keyword match (0.3)
- Example: `{"label": "urgent", "summary": "...", "reply": "..."}`

### Hard
All of the above + route to the correct department.
- Reward: label (0.5) + department (0.2) + summary (0.1) + reply keywords (0.2)
- Example: `{"label": "urgent", "summary": "...", "reply": "...", "department": "billing"}`

---

## Reward Function

Rewards are deterministic and keyword-based (no ML models needed):
- Label match: exact match = 0.5, valid but wrong = 0.1
- Summary: keyword overlap with email content
- Reply: keyword match against ground truth reply keywords
- Department: exact match = 0.2, valid but wrong = 0.05
- All rewards clamped to [0.0, 1.0]

---

## Baseline Scores

| Task | Baseline Score |
|------|---------------|
| Easy | ~0.50 |
| Medium | ~0.55 |
| Hard | ~0.60 |

---

## Setup & Usage

### Local

```bash
git clone https://huggingface.co/spaces/souller/email-triage-env
cd email-triage-env
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 7860
```

### Docker

```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

### API Endpoints

- `POST /reset` — Start a new episode
- `POST /step` — Submit an action
- `GET /state` — Get current episode state

### Run Inference

```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="your_hf_token_here"
export SPACE_URL="https://souller-email-triage-env.hf.space"
python inference.py
```

---

## Project Structure

```
.
├── server.py              # FastAPI server (OpenEnv endpoints)
├── my_env_environment.py  # Core environment logic
├── models.py              # Pydantic action/observation models
├── grader.py              # Reward/grading logic
├── inference.py           # Baseline inference script
├── openenv.yaml           # OpenEnv metadata
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
└── README.md
```
